# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
# **G42 Upgrade Workflow: R6.0.0 → R8.0.2**.

This workflow orchestrates the firmware upgrade of an Infinera G42 device (Platform GX). Due to version dependencies
and internal upgrade paths, this is a **multi-stage process**.

!!! info "Upgrade Path"
    The workflow automatically determines the starting point based on the current version and proceeds sequentially.
    The full path is:

    1.  **R6.0.0 → R6.0.1** (Intermediate)
    2.  **R6.0.1 → R7.1.1** (Intermediate)
    3.  **R7.1.1 → R8.0.2** (Target)

    *If the node is already on an intermediate version (e.g., R7.1.1), earlier steps are automatically skipped.*

!!! danger "Service Impact Analysis"
    **This workflow is traffic affecting.** Ensure a maintenance window is open before proceeding.

    | Operation | Type | Service Impact | Scope |
    | :--- | :--- | :--- | :--- |
    | **XMM Update** | Cold Restart | ✅ not-service affecting | One card at a time (automatic switchover) |
    | **CHM6 Update** | Cold Restart | ⚠️ **service affecting** | One card at a time |

!!! tip "User Action Needed"
    The workflow is designed to run autonomously. Manual user intervention is **only** required if
    unexpected alarms (Critical/Major/Minor) appear after an upgrade stage.

## Workflow Phases

### 1. Phase 1: Initialization & Assessment
*   **Target Selection:** User selects the specific G42 device.
*   **State Capture:** The system captures:
    *   Current Software Version.
    *   Active Alarms (ignoring 'not-reported' severity).
    *   Current Q-factors of all optical carriers are recorded to ensure signal stability comparison later.

### 2. Phase 2: Sequential Upgrades
For each required version step (e.g., R6.0.1, R7.1.1, R8.0.2), the workflow performs the following loop:

*   **Backup:** Uploads the active node database to the TNMS SFTP server.
*   **Execution:** Initiates an asynchronous download and activation of the image (including DB upgrade).
*   **Verification (Retry Loop):**
    *   Checks that **no cards are restarting**.
    *   Verifies **Q-factors are stable** (alerts if drop > 1.0 dB).
    *   Confirms the active software version matches the target.
*   **Alarm Check:** Compares post-upgrade alarms with pre-upgrade alarms. If new relevant alarms exist,
    the workflow pauses for user approval.

### 3. Phase 3: Finalization (CHM6 Updates)
After reaching R8.0.2:
*   **Firmware Audit:** Checks CHM6 cards for outdated DCO firmware (`DCO-MCU-DSP-P`).
*   **Sequential Restart:** Performs a **Cold Restart** on CHM6 cards one-by-one if they are not current.
    This step includes safety checks for Q-factor stability between restarts.
"""

import os
import re
from string import Template
from typing import Annotated, TypeAlias

from orchestrator import workflow
from orchestrator.config.assignee import Assignee
from orchestrator.forms import FormPage, SubmitFormPage
from orchestrator.forms.validators import Choice, Label
from orchestrator.targets import Target
from orchestrator.workflow import StepList, begin, conditional, done, init, inputstep, retrystep, step
from orchestrator.workflows.steps import store_process_subscription
from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_blocks.optical_device import Platform
from products.product_types.optical_device import OpticalDevice
from services.infinera import G42Client
from workflows.shared import (
    active_subscription_with_instance_value_selector,
)
from workflows.tasks.shared import (
    retrieve_all_router_from_netbox_selector,
    retrieve_up_up_backbone_interfaces_of_routers,
    raise_if_no_traffic_btw_routers,
)
from utils.custom_types.ip_address import IPAddress

from orchestrator.forms.validators import Choice, Label, choice_list

logger = get_logger(__name__)


SFTP_PASS = None # omitted to share on public repo
UPLOAD_PATH = f"omitted"
DOWNLOAD_TEMPLATE = Template(
    f"omitted"
)
MAPPING = {
    "R6.0.1": "G40_ADV-R6.0.1-F-2022.11.28_11_41-45.manifest",
    "R7.1.1": "G40_ADV-R7.1.1-F-2024.11.29_11_11-52.manifest",
    "R8.0.2": "G40_ADV-R8.0.2-F-2025.11.13_10_43-140.manifest",
}


def retrieve_relevant_alarms(client: G42Client) -> set[str]:
    """Retrieves relevant alarms from the G42 device.

    Fetches current alarms and filters out those with 'not-reported' severity.
    Constructs a unique signature for each alarm based on severity, resource,
    description, direction, and location.
    """
    active_alarms = client.data.alarms.current_alarms.alarm.retrieve(depth=3)
    relevant_alarms = set()
    for alarm in active_alarms:
        if alarm.get("perceived-severity") == "not-reported":
            continue

        relevant_fields = [
            "perceived-severity",
            "resource",
            "alarm-type",
            "alarm-type-description",
            "direction",
            "location",
        ]
        alarm_signature = ";".join(alarm.get(x) for x in relevant_fields)
        relevant_alarms.add(alarm_signature)

    return relevant_alarms


def retrieve_q_factors(client: G42Client) -> dict[str, float]:
    """Retrieves Q-factors for optical channels.

    Fetches real-time PM data for 'gx:pre-fec-q' parameter.
    Returns a dictionary mapping resource names to their Q-factor values.
    """
    response = client.operations.get_pm(data_type="real-time", filter=[{"filter-id": 1, "parameter": "gx:pre-fec-q"}])

    if response["ioa-pm:output"]["number-of-result-records"] == 0:
        return {}

    pm_records = response["ioa-pm:output"]["pm-record"]
    q_factors = {}
    for record in pm_records:
        q_factors[record["resource"]] = float(record["pm-value"])

    return q_factors


def check_active_software(client: G42Client, acceptable_versions: str | list[str]) -> str:
    """
    Check if the active software on the ne and on each card (location) is within the
    list of acceptable versions.

    Raises:
        UserWarning: if the active version is not acceptable

    Returns:
        str: the active version
    """
    if isinstance(acceptable_versions, str):
        acceptable_versions = [acceptable_versions]

    def _check_sw_load(software_load: dict, acceptable_versions: list[str]) -> str:
        try:
            active_software = next(sw for sw in software_load if sw.get("swload-state") == "active")
        except StopIteration:
            active_software = next(sw for sw in software_load if sw.get("swload-status") == "activate-complete")

        active_version = active_software.get("swload-version")

        if active_version not in acceptable_versions:
            msg = f"Acceptable active versions are: {acceptable_versions}. Current active version is {active_version}."
            raise UserWarning(msg)

        return active_version

    software_load = client.data.ne.system.sw_management.software_load.retrieve(depth=2)
    active_version = _check_sw_load(software_load, acceptable_versions)

    software_locations = client.data.ne.system.sw_management.software_location.retrieve(depth=3)
    for location in software_locations:
        software_load = location["software-load"]
        _check_sw_load(software_load, [active_version])

    return active_version


def raise_if_card_is_restarting(client: G42Client) -> None:
    """Raises UserWarning if there is a card restarting.

    Checks for specific alarm types indicating a card restart or initialization.
    """
    cli_response = client.operations.cli_command(
        commands="show alarm alarm-type=EQPTCPRESET alarm-type=SW-INIT alarm-type=INIT alarm-type=NO-CTRLR-MODULE-REDUNDANCY",  # noqa: E501
        echo="off",
    )
    """
        example responses:
            {
                "ioa-rpc:output": {
                    "result": " alarm \n-------\nalarm-id              resource  resource-type  alarm-type   alarm-type-description                  direction  location  perceived-severity  reported-time         service-affecting  alarm-category  label  last-changed-time     operator-state  \n--------------------  --------  -------------  -----------  --------------------------------------  ---------  --------  ------------------  --------------------  -----------------  --------------  -----  --------------------  --------------  \n16800581061604203220  card-1-4  CHM6           EQPTCPRESET  Equipment's control plane is resetting  na         na        minor               2025-12-02T17:54:21Z  nsa                equipment              2025-12-02T17:54:24Z  none            \n\n\n"
                }
            }
        or if no alarm:
            {
                "ioa-rpc:output": {
                    "result": "\n"
                }
            }
    """  # noqa: E501
    cli_response = cli_response["ioa-rpc:output"]["result"]
    cli_response = cli_response.strip()
    if cli_response:
        match = re.search(r"card-(\d+-\d+)", cli_response)
        card_id = match.group(1)
        msg = f"card-{card_id} is restarting"
        raise UserWarning(msg)


def raise_if_q_factor_below_threshold(
    loopback_ip: str, management_ip: str, q_factors_before_upgrade: dict[str, float]
) -> None:
    """Raises UserWarning if there is a Q-factor decrease of more than 1.0 dB.

    Compares current Q-factors with those saved before the upgrade.
    """
    g42 = G42Client(loopback_ip, management_ip)
    current_q_factors = retrieve_q_factors(g42)
    for carrier, q in q_factors_before_upgrade.items():
        if current_q_factors.get(carrier) is None:
            msg = f"Unable to find Q-factor of {carrier}. Most probably the card is restarting."
            raise UserWarning(msg)

        threshold = 1.0
        if current_q_factors[carrier] < q - threshold:
            msg = (
                f"Q-factor of {carrier} is {current_q_factors[carrier]} dB, before the upgrade it was {q} dB."
                "Most probably it is stabilizing after card restart."
            )
            raise UserWarning(msg)


def initial_input_form_generator() -> FormGenerator:
    """Generates the initial input form for the G42 upgrade workflow.

    Displays a warning banner about the upgrade process and service impact.
    Prompts the user to confirm by typing 'UPGRADE' and to select the G42 device.
    """
    achtung = (
        "This workflow will perform the following upgrades (>>) to a G42:\n"
        "R6.0 >> R6.0.1 >> R7.1.1 >> R8.0.2\n"
        "If the node is running R6.0.1 or R7.1.1, respective upgrades are skipped.\n"
        "After the last upgrade, CHM6 cards will be cold restarted one-by-one.\n"
        "This is traffic affecting: ensure a maintenance window is open.\n"
        "Write UPGRADE in this text box to proceed.\n"
    )
    Achtung = Annotated[
        str,
        Field(
            achtung,
            title="⚠️⚠️⚠️ README ⚠️⚠️⚠️",
            json_schema_extra={
                "format": "long",
            },
        ),
    ]

    G42Choice: TypeAlias = Choice  # noqa: UP040
    g42_choice: G42Choice = active_subscription_with_instance_value_selector(
        product_type="OpticalDevice",
        resource_type="platform",
        value=Platform.GX_G42,
        prompt="Select the G42 to be upgraded",
    )

    RouterChoice: TypeAlias = choice_list  # noqa: UP040
    routers_choice: RouterChoice = retrieve_all_router_from_netbox_selector()

    class Form0(FormPage):
        achtung: Achtung
        subscription_id: g42_choice
        routers_ip_addresses: routers_choice

        @model_validator(mode="after")
        def validate(self) -> "Form0":
            if self.achtung.strip().upper() != "UPGRADE":
                msg = "Please read the ⚠️⚠️⚠️ README ⚠️⚠️⚠️ text box!"
                raise ValueError(msg)
            return self

    user_input = yield Form0
    return user_input.dict()


@step("Saving initial information")
def retrieve_and_save_info(subscription_id: UUIDstr, routers_ip_addresses: list[IPAddress]) -> State:
    """Retrieves and saves initial information about the G42 device.

    Fetches connection details, checks active software version, determines the
    next version to install, and saves current alarms and Q-factors.
    """
    sub = OpticalDevice.from_subscription(subscription_id)

    loopback_ip = sub.optical_device.lo_ip
    management_ip = sub.optical_device.mngmt_ip

    g42 = G42Client(loopback_ip, management_ip)

    acceptable_starting_points = ["R6.0.1", "R6.0.0", "R7.1.1", "R8.0.2"]
    active_version = check_active_software(g42, acceptable_starting_points)
    next_version_mapping = {
        "R6.0.0": "R6.0.1",
        "R6.0.1": "R7.1.1",
        "R7.1.1": "R8.0.2",
        "R8.0.2": None,
    }
    next_version = next_version_mapping[active_version]

    raise_if_card_is_restarting(g42)

    active_alarms = retrieve_relevant_alarms(g42)
    q_factors = retrieve_q_factors(g42)
    routers_interfaces_to_check = retrieve_up_up_backbone_interfaces_of_routers(routers_ip_addresses)

    return {
        "loopback_ip": sub.optical_device.lo_ip,
        "management_ip": sub.optical_device.mngmt_ip,
        "current_active_sw_version": active_version,
        "sw_version_to_be_installed": next_version,
        "alarms_before_upgrade": active_alarms,
        "q_factors_before_upgrade": q_factors,
        "routers_interfaces_to_check": routers_interfaces_to_check,
    }


@step("Uploading the active database of the node to the TNMS server")
def upload_active_database(loopback_ip: str, management_ip: str) -> State:
    """Uploads the active database of the node to the TNMS server.

    Performs a database upload operation to the configured SFTP path.
    """
    g42 = G42Client(loopback_ip, management_ip)
    result = g42.operations.upload(filetype="database", destination=UPLOAD_PATH, password=SFTP_PASS)
    if result["ioa-rpc:output"]["upload-result"] != "Success":
        msg = f"Error: {result}"
        raise UserWarning(msg)
    return {"status": f"uploaded node DB to {UPLOAD_PATH.split('@')[-1]}"}


@step("Downloading and activating new software image")
def download_and_activate_new_sw(loopback_ip: str, management_ip: str, sw_version_to_be_installed: str) -> State:
    """Downloads and activates the new software image.

    Initiates an unattended, asynchronous download and activation of the
    specified software version. Includes database upgrade.
    """
    g42 = G42Client(loopback_ip, management_ip)
    source = DOWNLOAD_TEMPLATE.substitute(
        version=sw_version_to_be_installed, manifest_filename=MAPPING[sw_version_to_be_installed]
    )
    result = g42.operations.download(
        unattended=True,
        filetype="swimage",
        source=source,
        password=SFTP_PASS,
        is_async=True,
        skip_secure_verification=True,
        db_action="upgrade-db",
    )
    expected_reply = "Download will happen in the background"
    actual_reply = result["ioa-rpc:output"]["download-result"]
    actual_reply = actual_reply.strip()
    if not actual_reply.startswith(expected_reply):
        msg = f"Error: {result}"
        raise UserWarning(msg)

    return {"status": f"Activation in progress. Downloaded image {source.split('@')[-1]}"}


@retrystep(
    "Checking that: no card is restarting, carriers' Q-factors are stable, "
    "and the active software version matches the target version"
)
def check_if_upgrade_is_done(
    loopback_ip: str, management_ip: str, sw_version_to_be_installed: str, q_factors_before_upgrade: dict[str, float]
) -> State:
    """Checks if the upgrade is completed successfully.

    Verifies that no cards are restarting and that the active software version
    matches the target version. Updates the state for the next upgrade step.
    """
    g42 = G42Client(loopback_ip, management_ip)

    raise_if_card_is_restarting(g42)
    raise_if_q_factor_below_threshold(loopback_ip, management_ip, q_factors_before_upgrade)
    active_version = check_active_software(g42, [sw_version_to_be_installed])

    next_version_mapping = {
        "R6.0.1": "R7.1.1",
        "R7.1.1": "R8.0.2",
        "R8.0.2": None,
    }
    next_version = next_version_mapping[active_version]

    return {"current_active_sw_version": active_version, "sw_version_to_be_installed": next_version}


@step("Checking if new alarm appeared")
def search_for_new_alarms(loopback_ip: str, management_ip: str, alarms_before_upgrade: list[str]) -> State:
    """Checks for new alarms that appeared after the upgrade.

    Compares the current alarms with the alarms saved before the upgrade.
    Returns a set of new, relevant alarms.
    """
    original_alarm_set = set(alarms_before_upgrade)
    g42 = G42Client(loopback_ip, management_ip)
    current_alarm_set = retrieve_relevant_alarms(g42)
    difference_set = current_alarm_set.difference(original_alarm_set)
    return {"new_alarms_after_upgrade": difference_set}


@inputstep("New relevant alarms found after upgrade. Should we proceed?", assignee=Assignee.SYSTEM)
def approve_unexpected_alarms() -> FormGenerator:
    """Asks the user to approve unexpected alarms found after upgrade.

    Displays a form if new relevant alarms are detected, requiring user
    confirmation to proceed with the workflow.
    """

    class Form(SubmitFormPage):
        model_config = ConfigDict(title="Please confirm before continuing")
        msg_label: Label = "See the unexpected alarms in the output of the previous step. Do you want to proceed?"

    yield Form
    return {}


@retrystep("Cold restart CHM6 cards one-by-one")
def cold_restart_chm6_cards(
    loopback_ip: str,
    management_ip: str,
    q_factors_before_upgrade: dict[str, float],
    routers_interfaces_to_check: dict[IPAddress, list[str]],
) -> State:
    """Statelessly restart CHM6 cards one-by-one.

    Checks if any CHM6 card is currently restarting. If not, checks for cards
    with outdated DCO firmware. Restarts the first outdated card found and
    raises an error to trigger a retry (allowing the workflow to pause).
    """
    g42 = G42Client(loopback_ip, management_ip)

    raise_if_card_is_restarting(g42)
    raise_if_q_factor_below_threshold(loopback_ip, management_ip, q_factors_before_upgrade)
    raise_if_no_traffic_btw_routers(routers_interfaces_to_check)

    cli_response = g42.operations.cli_command(
        commands="show current-fw fw-status=not-current | inc DCO-MCU-DSP-P", echo="off"
    )
    """
        example responses:
            {
                "ioa-rpc:output": {
                    "result": "current-fw-1-4/DCO-MCU-DSP-P   -  A001_0C-C00D-D005_0D-D00F  not-current  \ncurrent-fw-2-4/DCO-MCU-DSP-P   -  A001_0C-C00D-D005_0D-D00F  not-current  \n"
                }
            }
        or if no card in not-current:
            {
                "ioa-rpc:output": {
                    "result": "\n"
                }
            }
    """  # noqa: E501
    cli_response = cli_response["ioa-rpc:output"]["result"]
    cli_response = cli_response.strip()
    if cli_response:
        match = re.search(r"current-fw-(\d+-\d+)/DCO-MCU-DSP-P", cli_response)
        chm6_id = match.group(1)
        g42.operations.restart(resource=f"/ioa-ne:ne/equipment/card[name='{chm6_id}']", restart_type="cold")
        msg = f"Issued cold restart of card-{chm6_id}"
        raise UserWarning(msg)

    return {"status": "All CHM6 cards have updated firmware"}


@workflow(
    "Task to upgrade G42 devices from FP6.0.0 to FP8.0.2",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def upgrade_g42_from_600_to_802() -> StepList:
    """Workflow to upgrade G42 from R6.0.0 to R8.0.2.

    Orchestrates the multi-stage upgrade process:
    1.  R6.0.0 -> R6.0.1
    2.  R6.0.1 -> R7.1.1
    3.  R7.1.1 -> R8.0.2
    Includes pre-checks, backups, activation, verification, and final
    cold restart of CHM6 cards.
    """
    upgrade_steps = (
        begin
        >> upload_active_database
        >> download_and_activate_new_sw
        >> check_if_upgrade_is_done
        >> search_for_new_alarms
        >> conditional(lambda state: state["new_alarms_after_upgrade"])(approve_unexpected_alarms)
    )

    return (
        init
        >> store_process_subscription()
        >> retrieve_and_save_info
        >> conditional(lambda state: state["sw_version_to_be_installed"] == "R6.0.1")(upgrade_steps)
        >> conditional(lambda state: state["sw_version_to_be_installed"] == "R7.1.1")(upgrade_steps)
        >> conditional(lambda state: state["sw_version_to_be_installed"] == "R8.0.2")(upgrade_steps)
        >> cold_restart_chm6_cards
        >> done
    )
