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
# **G30 Upgrade Workflow: FP4.5.2 → FP4.8.0**.

This workflow orchestrates the firmware upgrade of a G30 device. Due to version dependencies,
this is a **multi-stage process**.

!!! info "Upgrade Path"
    The upgrade is performed in three sequential stages:

    1.  **U-boot patching** (Preliminary): Includes U-boot patching.
    2.  **FP4.5.2 → FP4.7.2** (Intermediate): Necessary as dictated by release notes of FP4.8.0.
    3.  **FP4.7.2 → FP4.8.0** (Final): The target deployment version.

!!! danger "Service Impact Analysis"
    While node restarts are generally safe, specific hardware upgrades in this workflow **will** impact traffic.

    | Equipment | Restart type | Service Impact | How | When |
    | :--- | :--- | :--- | :--- | :--- |
    | Node | Restart | ✅ **Non-Service Affecting** | all NE at once | After each release activation |
    | OCC2 and CHM2T | Warm Restart | ✅ **Non-Service Affecting** | all NE at once | After FP4.7.2 activation |
    | CHM1 | Cold Restart | ⚠️ **SERVICE AFFECTING** | one card at a time | After FP4.7.2 upgrade |

!!! tip "User Action Needed"
    This workflow requires manual approval but only if unexpected alarms are detected after each upgrade.

## Workflow Phases

### 1. Phase 1: Initialization
*   **Target Selection:** User selects the specific G30 device.
*   **Inventory Audit:** System checks current software version and hardware inventory (CHM1, OCC2, CHM2T).


### 2. Phase 2: Intermediate Upgrade (to FP4.7.2)
*   **Preparation:** Verifies active SW, clears old sessions, and performs DB/Log backups.
*   **Execution:** Downloads and activates the FP4.7.2 image.
*   **Verification:** Validates node reachability, optical circuit health, and alarm status.
*   **Restarts:** Performs specific card restarts (see Service Impact below).

### 3. Phase 3: Final Upgrade (to FP4.8.0)
*   **Update Target:** Sets upgrade target to FP4.8.0.
*   **Execution:** Repeats the standard Pre-check, Download, Activation, and Verification cycle.

"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
from datetime import UTC, datetime
from string import Template
from typing import Annotated, Any, TypeAlias

from orchestrator import workflow
from orchestrator.config.assignee import Assignee
from orchestrator.forms import FormPage, SubmitFormPage
from orchestrator.forms.validators import Choice, Label, choice_list
from orchestrator.targets import Target
from orchestrator.workflow import StepList, begin, conditional, done, init, inputstep, retrystep, step
from orchestrator.workflows.steps import store_process_subscription
from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from requests.exceptions import HTTPError
from structlog import get_logger

from products.product_blocks.optical_device import Platform
from products.product_types.optical_device import OpticalDevice
from services.asyncsshcli import async_ssh_cli
from services.infinera import G30Client
from workflows.shared import active_subscription_with_instance_value_selector
from workflows.tasks.shared import (
    raise_if_no_traffic_btw_routers,
    retrieve_all_router_from_netbox_selector,
    retrieve_up_up_backbone_interfaces_of_routers,
)

logger = get_logger(__name__)

SFTP_PASS = None # omitted to share on public repo
BACKUP_PATH = None # omitted to share on public repo
UPLOAD_PATH = f"omitted"
SW_IMAGES_PATH = Template(
    f"omitted"
)
PATCH_PATH = f"omitted"


def initial_input_form_generator() -> FormGenerator:
    """Generates the initial input form for the G30 upgrade workflow.

    Displays a warning banner about the upgrade process (restarts, service impact)
    and prompts the user to select the G30 device to be upgraded.
    """
    achtung = (
        "This task will upgrade the selected G30 from FP4.5.2 to FP4.7.2"
        " and then from 4.7.2 to 4.8.0.\nThese upgrades will restart the entire node"
        " and CHM1 cards.\nNode restarts are not service affecting, but card restarts are.\n"
        "Depending on the hardware installed, the upgrade process may take up to 2 hours.\n"
        "Please confirm you read this banner by replacing it with 'UPGRADE'."
    )
    Achtung = Annotated[  # noqa: N806
        str,
        Field(
            achtung,
            title="⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️",
            json_schema_extra={
                "format": "long",
            },
        ),
    ]

    G30Choice: TypeAlias = Choice  # noqa: UP040
    g30_choice: G30Choice = active_subscription_with_instance_value_selector(
        product_type="OpticalDevice",
        resource_type="platform",
        value=Platform.Groove_G30,
        prompt="Select the G30 to be upgraded",
    )
    RouterChoice: TypeAlias = choice_list  # noqa: UP040
    routers_choice: RouterChoice = retrieve_all_router_from_netbox_selector()

    class InputForm(FormPage):
        achtung: Achtung
        subscription_id: g30_choice
        routers_list: routers_choice

        @model_validator(mode="after")
        def validate(self) -> InputForm:
            if self.achtung.strip().upper() != "UPGRADE":
                msg = "Please read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ text box!"
                raise ValueError(msg)
            return self

    user_input = yield InputForm
    return user_input.dict()


@step("Setting up things to upgrade from FP4.5.2 to FP4.7.2")
def initialize_variables_452_472(subscription_id: UUIDstr, routers_list: list) -> State:
    """Initialize variables for G30 upgrade from FP4.5.2 to FP4.7.2.

    Fetches device details from subscription, sets versions, creates G30 client,
    and detects presence of CHM1, OCC2, CHM2T modules to determine restart needs.
    """
    device = OpticalDevice.from_subscription(subscription_id).optical_device
    current_version = "FP4.5.2"
    new_version = "FP4.7.2"
    g30 = G30Client(lo_ip=device.lo_ip, mngmt_ip=device.mngmt_ip)
    are_chm1s_in_node_and_is_cold_restart_needed = (
        g30.operations.cli_command(commands="show inventory module-type=CHM1 module-type", echo="off") != {}
    )
    is_occ2_in_node_and_is_fpga_restart_needed = (
        g30.operations.cli_command(commands="show inventory module-type=OCC2 module-type", echo="off") != {}
    )
    is_chm2t_in_node_and_is_dsp_restart_needed = (
        g30.operations.cli_command(commands="show inventory module-type=CHM2T module-type", echo="off") != {}
    )
    interfaces_to_check = retrieve_up_up_backbone_interfaces_of_routers(routers_list)

    return {
        "fqdn": device.fqdn,
        "lo_ip": device.lo_ip,
        "mngmt_ip": device.mngmt_ip,
        "new_version": new_version,
        "current_version": current_version,
        "is_occ2_in_node_and_is_fpga_restart_needed": is_occ2_in_node_and_is_fpga_restart_needed,
        "are_chm1s_in_node_and_is_cold_restart_needed": are_chm1s_in_node_and_is_cold_restart_needed,
        "is_chm2t_in_node_and_is_dsp_restart_needed": is_chm2t_in_node_and_is_dsp_restart_needed,
        "interfaces_to_check": interfaces_to_check,
    }


async def _async_wrapper_for_step_patch_uboot_of_g30_chassis(
    g30_ip: str, g30_user: str, g30_pass: str, shelves: int
) -> dict[str, str]:
    """Async wrapper to patch u-boot on G30 chassis and shelves.

    Establishes an SSH connection to the G30, uploads the patch file, and iterates
    through shelves to check for flawed u-boot versions. Applies the patch if needed
    and verifies the fix.
    """
    raise NotImplementedError("Connection logic is not implemented in this snippet for security reasons.")  # FIXME


@step("Patching the uboot of G30 chasses (Infinera's FSB_240110)")
def patch_uboot_of_g30_chassis(lo_ip: str, mngmt_ip: str) -> State:
    """Patches u-boot scripts on G30 chassis shelves to fix Infinera FSB_240110 issue.

    Uses async SSH to chassis and shelves: downloads patch, checks for flawed u-boot
    on each shelf, applies fix if svn5399 detected, reports status per shelf.
    """
    raise NotImplementedError("Connection logic is not implemented in this snippet for security reasons.")  # FIXME


@step("Check swload version G30")
def check_active_sw_version(current_version: str, lo_ip: str, mngmt_ip: str) -> State:
    """Verifies active softwareload version matches expected current_version.

    Queries G30 CLI for active swload; raises ValueError if mismatch.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands="show sw-management softwareload-* swload-state=Active", echo="off"
    )
    swload_object = request_g30.get("ne:softwareload")[0]

    if swload_object.get("swload-version") == current_version:
        return {"status": f"👍 G30 softwareload version matches {current_version}."}

    msg = (
        f"G30 softwareload version is not {current_version}, upgrade not possible.\n"
        f"Current software state: {json.dumps(request_g30, indent=4)}"
    )
    raise ValueError(msg)


@step("Delete sessions")
def delete_all_sessions(lo_ip: str, mngmt_ip: str) -> State:
    """Deletes all active sessions on G30 via CLI command.

    Prepares clean session state before software upgrade.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    g30.operations.cli_command(commands="delete session*", echo="off")
    return {"Sessions Deleted": True}


@retrystep("Backup G30 database")
def backup_database(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Backs up G30 database to timestamped SFTP location.

    Uses G30 upload operation with file_description 'Backup G30 database'.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    string_dt = dt.strftime("%Y_%m_%d_%H_%M")

    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_DB_{string_dt}.zip"),
        password=SFTP_PASS,
        file_description="Backup G30 database",
        filetype="database",
    )
    return {"status": request_g30}


@retrystep("Upload security log G30")
def upload_security_log(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Uploads G30 security log to timestamped SFTP location.

    Uses G30 upload operation with filetype 'securitylog'.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    string_dt = dt.strftime("%Y_%m_%d_%H_%M")
    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_security_log_{string_dt}.zip"),
        password=SFTP_PASS,
        file_description="Upload G30 security log",
        filetype="securitylog",
    )
    return {"status": request_g30}


@retrystep("Upload summary log G30")
def upload_summary_log(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Uploads G30 summary log to timestamped SFTP location.

    Uses G30 upload operation with filetype 'summarylog'.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    string_dt = dt.strftime("%Y_%m_%d_%H_%M")
    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_summary_log_{string_dt}.zip"),
        password=SFTP_PASS,
        file_description="Upload G30 summary log",
        filetype="summarylog",
    )
    return {"status": request_g30}


@retrystep("Upload diagnostics log G30")
def upload_diagnostics_log(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Uploads G30 diagnostics log to timestamped SFTP location.

    Uses G30 upload operation with filetype 'diagnosticslog'.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    date_string = dt.strftime("%Y-%m-%d")

    try:
        g30.operations.cli_command(
            commands=f"show log configuration | include diagnosticslog | include {date_string}", echo="off"
        )
    except json.JSONDecodeError as e:  # this is expected because the response is not a valid JSON
        if "success" in e.doc:
            return {"status": "Diagnosticslog uploaded"}

    string_dt = dt.strftime("%Y_%m_%d_%H_%M")
    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_diagnostics_log_{string_dt}.zip"),
        password=SFTP_PASS,
        file_description="Upload G30 diagnostics log",
        filetype="diagnosticslog",
    )
    return {"status": request_g30}


@step("Download new software image on G30")
def download_sw_image(lo_ip: str, mngmt_ip: str, new_version: str) -> State:
    """Downloads G30 SW image for new_version."""
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands="show sw-management softwareload-* swload-state=Inactive", echo="off"
    )
    if request_g30 != {}:
        swload_object = request_g30.get("ne:softwareload")[0]
        if swload_object.get("swload-version") == new_version:
            return {
                "status": f"G30 softwareload version {new_version} already downloaded. We can proceed to activation."
            }

    resp = g30.operations.download(
        source=SW_IMAGES_PATH.substitute(version=new_version[2:]),
        password=SFTP_PASS,
        file_description="Download G30 SW image",
        filetype="swimage",
    )

    return {"status": resp, "new_version": new_version}


@retrystep("Check downloaded software image on G30")
def check_downloaded_sw_image(lo_ip: str, mngmt_ip: str, new_version: str) -> State:
    """Verifies inactive softwareload matches new_version after download.

    Queries G30 CLI; raises ValueError if not ready.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands="show sw-management softwareload-* swload-state=Inactive", echo="off"
    )
    if request_g30 == {}:
        raise ValueError("Inactive slot empty, is this a fresh G30 without any SW image downloaded?")
    swload_object = request_g30.get("ne:softwareload")[0]
    if swload_object.get("swload-version") == new_version:
        return {
            "status": f"G30 softwareload version {new_version} downloaded successfully. We can proceed to activation."
        }
    msg = f"G30 softwareload version {new_version} not downloaded correctly or still downloading."
    raise ValueError(msg)


@step("Activate G30 software image")
def activate_sw_image_and_update_current_sw_version(lo_ip: str, mngmt_ip: str, new_version: str) -> State:
    """Activates inactive SW image and updates current_version in state.

    Executes 'activate swimage' CLI, waits 15s.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(commands="activate swimage upgrade-db", echo="off")
    time.sleep(15)
    return {"status": request_g30, "current_version": new_version}


@step("Warm restart ne with FPGA upgrade for OCC2 card")
def warm_restart_ne_with_fpga_upgrade(lo_ip: str, mngmt_ip: str) -> State:
    """Performs warm restart of NE with optional FPGA/DSP upgrades.

    Initiates restart via G30 operations; raises if not 'In-progress'.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    status = g30.operations.restart(entity_id="ne:ne", restart_type="warm", fpga_upgrade=None)

    if status["coriant-rpc:output"]["status"] != "In-progress":
        msg = "Failed to restart NE"
        raise ValueError(msg)

    time.sleep(15)
    msg = "Restarting NE"
    return {"status": msg}


@step("Check if OCC2 are updated")
def check_occ2_updated(lo_ip: str, mngmt_ip: str) -> State:
    """Checks if all OCC2 cards have current firmware (no not-current state).

    Queries CLI; raises UserWarning if any need restart.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands=("show sw-management current-fw-version-* fw-equipment-type=OCC2 fw-state=not-current"),
        echo="off",
    )
    if request_g30 == {}:
        return {"status": "All OCC2 cards are updated."}

    formatted_state = json.dumps(request_g30, indent=4)
    msg = f"OCC2 cards need to be restarted to complete the upgrade.\nCurrent software state: {formatted_state}"
    raise UserWarning(msg)


@step("Warm restart ne with DSP upgrade for CHM2T card")
def warm_restart_ne_with_dsp_upgrade(lo_ip: str, mngmt_ip: str) -> State:
    """Performs warm restart of NE with optional FPGA/DSP upgrades.

    Initiates restart via G30 operations; raises if not 'In-progress'.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    status = g30.operations.restart(entity_id="ne:ne", restart_type="warm", dsp_upgrade=None)

    if status["coriant-rpc:output"]["status"] != "In-progress":
        msg = "Failed to restart NE"
        raise ValueError(msg)

    time.sleep(15)
    msg = "Restarting NE"
    return {"status": msg}


@step("Check if CHM2T are updated")
def check_chm2t_updated(lo_ip: str, mngmt_ip: str) -> State:
    """Checks if all CHM2T cards have current firmware (no not-current state).

    Queries CLI; raises UserWarning if any need restart.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands=("show sw-management current-fw-version-* fw-equipment-type=CHM2T fw-state=not-current"),
        echo="off",
    )
    if request_g30 == {}:
        return {"status": "All CHM2T cards are updated."}

    msg = (
        "CHM2T cards need to be restarted to complete the upgrade.\n"
        f"Current software state: {json.dumps(request_g30, indent=4)}"
    )
    raise UserWarning(msg)


def _get_och_os_list(lo_ip: str, mngmt_ip: str) -> list[dict[str, Any]]:
    """Retrieves a list of OCH OS instances from the G30.

    Fetches optical channel details including alias, Q-factor, availability status,
    actual TX optical power, and actual frequency for all 'up' admin-status channels.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    g30_request = g30.operations.cli_command(
        commands=(
            "show och-os admin-status=up alias-name Q-factor avail-status actual-tx-optical-power actual-frequency"
        ),
        echo="off",
    )
    list_och_os = g30_request.get("ne:och-os", [])

    if isinstance(list_och_os, dict):
        list_och_os = [list_och_os]

    return list_och_os


@step("Save the status of all optical circuits before the upgrade")
def save_optical_circuits_status_before_upgrade(lo_ip: str, mngmt_ip: str) -> State:
    """Saves the status of all optical circuits before the upgrade.

    Retrieves the current state of OCH OS instances and stores them in a dictionary
    keyed by alias name for later comparison.
    """
    ochs_before_upgrade = {}
    ochs = _get_och_os_list(lo_ip, mngmt_ip)

    for och in ochs:
        ochs_before_upgrade[och["alias-name"]] = och

    return {"ochs_before_upgrade": ochs_before_upgrade}


def check_optical_circuits(lo_ip: str, mngmt_ip: str, ochs_before_upgrade: dict[str, Any]) -> State:
    """Checks the status of optical circuits against their pre-upgrade state.

    Compares current Q-factor, TX optical power, frequency, and availability status
    with the saved pre-upgrade values. Raises ValueError if significant degradation
    is detected.
    """
    current_och_os_list = _get_och_os_list(lo_ip, mngmt_ip)

    for och in current_och_os_list:
        och_dict_before_upgrade = ochs_before_upgrade.get(och["alias-name"])

        if och_dict_before_upgrade is None:
            continue

        if float(och["Q-factor"]) < float(och_dict_before_upgrade["Q-factor"]) - 0.5:
            msg = (
                f"Optical circuit {och['alias-name']} has Q factor {och['Q-factor']}, "
                f"before it had {och_dict_before_upgrade['Q-factor']}, wait till Q factor stabilizes.\n"
            )
            raise ValueError(msg)

        if float(och["actual-tx-optical-power"]) < float(och_dict_before_upgrade["actual-tx-optical-power"]) - 0.5:
            msg = (
                f"Optical circuit {och['alias-name']} has actual-tx-optical-power {och['actual-tx-optical-power']}, "
                f"before it had {och_dict_before_upgrade['actual-tx-optical-power']},"
                " wait till actual-tx-optical-power stabilizes.\n"
            )
            raise ValueError(msg)

        if (
            int(och["actual-frequency"]) < int(och_dict_before_upgrade["actual-frequency"]) - 50
            or int(och["actual-frequency"]) > int(och_dict_before_upgrade["actual-frequency"]) + 50
        ):
            msg = (
                f"Optical circuit {och['alias-name']} has actual-frequency {och['actual-frequency']}, "
                f"before it had {och_dict_before_upgrade['actual-frequency']}, wait till actual-frequency stabilizes.\n"
            )
            raise ValueError(msg)

        if och["avail-status"] != och_dict_before_upgrade["avail-status"]:
            if och["avail-status"] == "":
                continue
            msg = (
                f"Optical circuit {och['alias-name']} has avail-status {och['avail-status']}, "
                f"before it had {och_dict_before_upgrade['avail-status']}, wait till och-os stabilizes.\n"
            )
            raise ValueError(msg)

    return {"status": "Optical circuits that were in service before the upgrade are up."}


@retrystep(
    "Cold restart CHM1 cards one-by-one. This step will fail and resume several times until all cards are restarted."
)
def cold_restart_chm1s_1by1_while_checking_services(
    lo_ip: str, mngmt_ip: str, ochs_before_upgrade: dict[str, Any], interfaces_to_check: dict
) -> State:
    """Cold restarts CHM1 cards one by one while checking services.

    Identifies CHM1 cards with outdated firmware, restarts the first one found,
    and raises UserWarning to trigger a retry (which allows the workflow to pause
    and resume). Verifies optical circuits before proceeding.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    check_optical_circuits(lo_ip, mngmt_ip, ochs_before_upgrade)
    raise_if_no_traffic_btw_routers(interfaces_to_check)

    request_g30 = g30.operations.cli_command(
        commands=("show current-fw-version-card-*/*/CHM-DSP fw-equipment-type=CHM1 fw-state=not-current"),
        echo="off",
    )
    cards_to_restart = request_g30.get("ne:current-fw-version")

    if cards_to_restart is not None:
        card = cards_to_restart[0]
        status = g30.operations.restart(entity_id=card["equipment-entity"], restart_type="cold")

        if status["coriant-rpc:output"]["status"] != "In-progress":
            msg = f"Failed to restart CHM1 card {card['equipment-entity']}\n"
            raise ValueError(msg)

        msg = f"Cold restarting CHM1 card {card['equipment-entity']}. Will automatically retry after some time."
        raise UserWarning(msg)

    return {"status": "All CHM1 cards restarted successfully."}


@retrystep("Check if G30 is back online")
def check_until_g30_becomes_responsive(lo_ip: str, mngmt_ip: str) -> State:
    """Checks if the G30 node is back online and responsive.

    Attempts to retrieve NE data. If successful, the node is considered online.
    This step is designed to be retried until success.
    """
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
    result = g30.data.ne.retrieve(content="nonconfig", depth=2, with_defaults="trim")
    return {"response_status": result}


@step("Setting up things to upgrade from FP4.7.2 to FP4.8.0")
def update_variables_472_480() -> State:
    """Updates workflow variables for the second phase of the upgrade (FP4.7.2 to FP4.8.0).

    Sets the new target version to FP4.8.0 and resets restart flags as they are
    not expected to be needed for this specific version jump.
    """
    return {
        "new_version": "FP4.8.0",
        "current_version": "FP4.7.2",
        "is_occ2_in_node_and_is_fpga_restart_needed": False,
        "are_chm1s_in_node_and_is_cold_restart_needed": False,
        "is_chm2t_in_node_and_is_dsp_restart_needed": False,
    }


def retrieve_active_alarms(lo_ip: str, mngmt_ip: str) -> set[str]:
    g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)

    try:
        alarms = g30.data.ne.fault.standing_condition.retrieve(depth=2, with_defaults="trim", content="nonconfig")
    except HTTPError as e:
        if e.response.status_code == 404:
            return set()
        raise

    alarm_set = set()
    for alarm in alarms:
        if alarm["severity-level"] in ["critical", "major"]:
            alarm_string = ";".join(
                (
                    alarm["fm-entity"],
                    alarm["location"],
                    alarm["direction"],
                    alarm["condition-type"],
                    alarm["condition-description"],
                )
            )
            alarm_set.add(alarm_string)

    return alarm_set


@step("Saving critical and major alarms before upgrading")
def save_alarms_before_upgrade(lo_ip: str, mngmt_ip: str) -> State:
    """Saves critical and major alarms present before the upgrade.

    Retrieves current standing conditions, filters for critical and major severity,
    and stores them as a set of unique alarm strings for later comparison.
    """
    alarm_set = retrieve_active_alarms(lo_ip, mngmt_ip)

    return {"alarms_before_upgrade": alarm_set}


@step("Checking that no new alarm has appeared after the upgrade")
def compare_alarms_to_those_before_upgrading(lo_ip: str, mngmt_ip: str, alarms_before_upgrade: Any) -> State:
    """Compares current alarms to those saved before the upgrade.

    Identifies any *new* critical or major alarms that have appeared since the
    upgrade started. Returns a list of these unexpected alarms.
    """
    alarms_before_upgrade = set(alarms_before_upgrade)
    current_alarms = retrieve_active_alarms(lo_ip, mngmt_ip)

    unexpected_alarms = current_alarms - alarms_before_upgrade

    return {"unexpected_alarms": unexpected_alarms}


@inputstep("New critical or major alarms found after upgrade. Should we proceed?", assignee=Assignee.SYSTEM)
def approve_unexpected_alarms() -> FormGenerator:
    """Asks the user to approve unexpected alarms found after upgrade.

    Displays a form if new critical or major alarms are detected, requiring user
    confirmation to proceed with the workflow.
    """

    class Form(SubmitFormPage):
        model_config = ConfigDict(title="Please confirm before continuing")
        msg_label: Label = "See the unexpected alarms in the output of the previous step. Do you want to proceed?"

    yield Form
    return {}


@workflow(
    "Task to upgrade G30 devices from FP4.5.2 to FP4.8.0",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def upgrade_g30_from_452_to_480() -> StepList:
    """Workflow to upgrade G30 from FP4.5.2 to FP4.8.0.

    Orchestrates the two-stage upgrade process:
    1. Upgrade from FP4.5.2 to FP4.7.2 (including u-boot patching and potential restarts).
    2. Upgrade from FP4.7.2 to FP4.8.0.
    Includes pre-checks, backups, safe activation, verification of services/alarms,
    and handling of card restarts.
    """
    pre_upgrade_operations = (
        begin
        >> check_active_sw_version
        >> delete_all_sessions
        >> backup_database
        >> upload_security_log
        >> upload_summary_log
        >> upload_diagnostics_log
        >> download_sw_image
        >> check_downloaded_sw_image
    )

    activate_and_check = (
        begin
        >> activate_sw_image_and_update_current_sw_version
        >> check_until_g30_becomes_responsive
        >> check_active_sw_version
        >> compare_alarms_to_those_before_upgrading
        >> conditional(lambda state: state["unexpected_alarms"] != [])(approve_unexpected_alarms)
        >> step("Checking that no optical circuit has gone down")(check_optical_circuits)
    )

    warm_restart_and_check = (
        begin
        >> warm_restart_ne_with_fpga_upgrade
        >> check_until_g30_becomes_responsive
        >> conditional(lambda state: state["is_occ2_in_node_and_is_fpga_restart_needed"])(check_occ2_updated)
        >> conditional(lambda state: state["is_chm2t_in_node_and_is_dsp_restart_needed"])(
            warm_restart_ne_with_dsp_upgrade
        )
        >> conditional(lambda state: state["is_chm2t_in_node_and_is_dsp_restart_needed"])(
            check_until_g30_becomes_responsive
        )
        >> conditional(lambda state: state["is_chm2t_in_node_and_is_dsp_restart_needed"])(check_chm2t_updated)
        >> compare_alarms_to_those_before_upgrading
        >> conditional(lambda state: state["unexpected_alarms"] != [])(approve_unexpected_alarms)
        >> step("Checking that no optical circuit has gone down")(check_optical_circuits)
    )

    return (
        init
        >> store_process_subscription()
        >> initialize_variables_452_472
        >> patch_uboot_of_g30_chassis
        >> pre_upgrade_operations
        >> save_alarms_before_upgrade
        >> save_optical_circuits_status_before_upgrade
        >> activate_and_check
        >> conditional(
            lambda state: (
                state["is_occ2_in_node_and_is_fpga_restart_needed"]
                or state["is_chm2t_in_node_and_is_dsp_restart_needed"]
            )
        )(warm_restart_and_check)
        >> conditional(lambda state: state["are_chm1s_in_node_and_is_cold_restart_needed"])(
            cold_restart_chm1s_1by1_while_checking_services
        )
        >> update_variables_472_480
        >> pre_upgrade_operations
        >> activate_and_check
        >> done
    )


""" In future, rather than retrysteps use callback steps to handle retries and notifications.
Below is an idea of how to do it but it would be even better if gnmi subscriptions with few
seconds heartbeat were implemented.


def ping_until_success(lo_ip: str, mngmt_ip: str, callback_url: str, max_attempts: int = 100):
    for attempt in range(max_attempts):
        try:
            g30 = G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)
            result = g30.data.ne.retrieve(content="nonconfig", depth=2, with_defaults="trim")
            if result:
                logger.info("Result", extra={"result": result})
                requests.post("http://193.206.159.136:14000/ping", json={"url": callback_url}, timeout=10)
                return
        except Exception as e:
            logger.error("Error", extra={"error": str(e)})
            # logger.info("Result", extra={"result": result})
            # if result.returncode == 0:
            # requests.post(
            #     f"http://localhost:8080{callback_url}",
            #     json={"success": 0},timeout=10
            # )
            # return
            # Ping succeeded - notify callback

            requests.post(
                "http://193.206.159.136:14000/progress",
                json={"url": callback_url + "/progress", "attempt": attempt},
                timeout=10,
            )

        time.sleep(5)  # Wait before retry

    # Max attempts reached - report failure
    requests.post("http://193.206.159.136:14000/fail", json={"url": callback_url}, timeout=10)


@step("Initiate ping monitoring")
def start_ping_monitor(callback_route: str, mngmt_ip: str) -> State:
    # Start background thread that pings target_host
    # When ping succeeds, POST to callback_route
    while True:
        result = subprocess.run(["ping", "-c", "1", mngmt_ip], capture_output=True)
        if result.returncode != 0:
            logger.info("Result", extra={"result": result})
            break
        time.sleep(2)  # Wait before retry

    threading.Thread(target=ping_until_success, args=(mngmt_ip, callback_route, 250), daemon=True).start()
    return {"ping_started": True}


@step("Validate ping result")
def validate_ping(callback_result: dict) -> State:
    if callback_result.get("success") != 0:
        raise ValueError("Ping validation failed")
    return {"ping_validated": True, "current_version": new_version}


ping_callback = callback_step(name="Wait for ping success", action_step=start_ping_monitor, validate_step=validate_ping)
"""
