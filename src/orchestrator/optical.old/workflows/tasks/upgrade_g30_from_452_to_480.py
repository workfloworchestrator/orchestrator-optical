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

This workflow orchestrates the firmware upgrade of an Infinera G30 device. Due to version dependencies,
this is a **multi-stage process**.

!!! info "Upgrade Path"
    The upgrade is performed in three sequential stages:

    1.  **U-boot patching** (Preliminary): Includes critical U-boot patching.
    2.  **FP4.5.2 → FP4.7.2** (Intermediate): Necessary as dictated by release notes of FP4.8.0.
    3.  **FP4.7.2 → FP4.8.0** (Final): The target deployment version.

!!! danger "Service Impact Analysis"
    While node restarts are generally safe, specific hardware upgrades in this workflow **will** impact traffic.

    | Equipment | Restart type | Service Impact | How | When |
    | :--- | :--- | :--- | :--- | :--- |
    | Node | Restart | ✅ **Non-Service Affecting** | all NE at once | After each release activation |
    | OCC2 and CHM2T | Warm Restart | ✅ **Non-Service Affecting** | all NE at once | After FP4.7.2 activation |
    | CHM1 | Cold Restart | ⚠️ **SERVICE AFFECTING** | one card at a time | After FP4.7.2 upgrade |

!!! warning "Requirements"
    Ensure the following files and directories exist on the SFTP server:

    | Item | Path / Location |
    | :--- | :--- |
    | **Software Images** | `/nokia/tnms/nedata/ne_software_images/G30_FP$version/GROOVE_G30_$version` |
    | **U-boot Patch** | `/nokia/tnms/nedata/ne_software_images/G30_uboot_patch/upubs.tar.gz` |
    | **Backup Directory**| `/nokia/tnms/nedata/ne_backup_before_upgrade` |

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
import contextlib
import json
import os
import threading
import time
from datetime import UTC, datetime
from string import Template
from typing import Annotated, Any, TypeAlias

import requests
from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from requests.exceptions import HTTPError
from structlog import get_logger

from orchestrator.core import workflow
from orchestrator.core.config.assignee import Assignee
from orchestrator.core.forms import FormPage, SubmitFormPage
from orchestrator.core.forms.validators import Choice, Label, choice_list
from orchestrator.core.targets import Target
from orchestrator.core.workflow import StepList, begin, callback_step, conditional, done, init, inputstep, step
from orchestrator.core.workflows.steps import store_process_subscription
from products.product_blocks.optical_device import Platform
from products.product_types.optical_device import OpticalDevice
from services.asyncsshcli import async_ssh_cli
from services.nokia import G30Client
from settings import garr_settings
from workflows.shared import active_subscription_with_instance_value_selector
from workflows.tasks.shared import (
    raise_if_no_traffic_btw_routers,
    retrieve_all_router_from_netbox_selector,
    retrieve_up_up_backbone_interfaces_of_routers,
)

logger = get_logger(__name__)

SFTP_USER = os.environ["TNMS_SFTP_USER"]
SFTP_PASS = os.environ["TNMS_SFTP_PSW"]
_sftp_server = os.environ["TNMS_ENDPOINT"]
_sftp_server = _sftp_server.replace("https://", "")
_sftp_server = _sftp_server[: _sftp_server.find(":")]
BACKUP_PATH = Template(f"sftp://{SFTP_USER}@{_sftp_server}//nokia/tnms/nedata/ne_backup_before_upgrade/$file_name")
SW_IMAGES_PATH = Template(
    f"sftp://{SFTP_USER}@{_sftp_server}//nokia/tnms/nedata/ne_software_images/G30_FP$version/GROOVE_G30_$version"
)
PATCH_PATH = f"{SFTP_USER}@{_sftp_server}:/nokia/tnms/nedata/ne_software_images/G30_uboot_patch/upubs.tar.gz"
_ORCHESTRATOR_URL = garr_settings.ORCHESTRATOR_URL


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
    g30 = G30Client(loopback_ip=device.lo_ip, management_ip=device.mngmt_ip)
    are_chm1s_in_node_and_is_cold_restart_needed = bool(
        g30.operations.cli_command(
            commands="show inventory module-type=CHM1 module-type | display json", echo="off"
        ).result.strip()
    )
    is_occ2_in_node_and_is_fpga_restart_needed = bool(
        g30.operations.cli_command(
            commands="show inventory module-type=OCC2 module-type | display json", echo="off"
        ).result.strip()
    )
    is_chm2t_in_node_and_is_dsp_restart_needed = bool(
        g30.operations.cli_command(
            commands="show inventory module-type=CHM2T module-type | display json", echo="off"
        ).result.strip()
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
    async with async_ssh_cli(host=g30_ip, port=22, username=g30_user, password=g30_pass, timeout=30) as session:
        await session.execute_command("")

        await session.change_user_or_host(
            "shell -f",
            user_at_host_prompt=":/home/administrator$",
        )

        response = await session.execute_command(
            f"scp -o StrictHostKeyChecking=no {PATCH_PATH} /var/volatile/tmp/",
            interactive_prompt="password:",
            prompt_answer=SFTP_PASS,
        )
        if "No such file or directory" in response:
            msg = f"Error copying patch file: {response}"
            raise ValueError(msg)

        response = await session.execute_command("ls /var/volatile/tmp/upubs.tar.gz")
        if "upubs.tar.gz" not in response:
            msg = f"Patch file not found: {response}"
            raise ValueError(msg)

        enc_shelf_password = "\x01W\x07T)\x10\x07Q\x07\x12A"  # noqa: S105
        dec_shelf_password = "".join(
            chr(ord(c) ^ ord(g30_pass[i % len(g30_pass)])) for i, c in enumerate(enc_shelf_password)
        )

        result = {}
        for shelf_id in range(1, shelves + 1):
            await session.change_user_or_host(
                f"ssh 192.168.199.{shelf_id}",
                user_at_host_prompt=f"NE_{shelf_id}:~$",
                password_prompt="'s password:",  # noqa: S106
                password=dec_shelf_password,
            )

            await session.change_user_or_host(
                "sudo -i",
                user_at_host_prompt=f"root@NE_{shelf_id}:~#",
            )

            response = await session.execute_command(
                "dd if=/dev/mtdblock16 bs=1k count=1 2>/dev/null | strings |grep '2013.01.01_-svn'|awk '{print $2}'"
            )
            if "svn5399" not in response:
                result[f"shelf-{shelf_id}"] = "Good to go, no flawed uboot script detected"
                await session.change_user_or_host("exit", user_at_host_prompt=f"NE_{shelf_id}:~$")
                await session.change_user_or_host("exit", user_at_host_prompt=":/home/administrator$")
                continue

            response = await session.execute_command(
                f"scp {g30_user}@192.168.199.254:/tmp/upubs.tar.gz /tmp/upubs.tar.gz",
                interactive_prompt="'s password:",
                prompt_answer=g30_pass,
            )
            if "No such file or directory" in response:
                msg = f"Error copying patch file: {response}"
                raise ValueError(msg)

            response = await session.execute_command("ls /tmp/upubs.tar.gz")
            if "upubs.tar.gz" not in response:
                msg = f"Patch file not found: {response}"
                raise ValueError(msg)

            cmd = (
                "sudo tar xzvf /tmp/upubs.tar.gz -C / && "
                "sudo bash /usr/local/fw/upubs.sh && "
                "sudo bash /usr/local/fw/upubs.sh"
            )
            expected_response = "*** no flawed uboot script detected, it may have been fixed already or is too old to have the bug, aborting"  # noqa: E501
            response = await session.execute_command(cmd)
            if expected_response in response:
                result[f"shelf-{shelf_id}"] = "Good to go, no flawed uboot script detected"
                await session.change_user_or_host("exit", user_at_host_prompt=f"NE_{shelf_id}:~$")
                await session.change_user_or_host("exit", user_at_host_prompt=":/home/administrator$")
            else:
                msg = f"Error patching shelf {shelf_id}: {response}"
                raise ValueError(msg)

    return result


@step("Patching the uboot of G30 chasses (Infinera's FSB_240110)")
def patch_uboot_of_g30_chassis(lo_ip: str, mngmt_ip: str) -> State:
    """Patches u-boot scripts on G30 chassis shelves to fix Infinera FSB_240110 issue.

    Uses async SSH to chassis and shelves: downloads patch, checks for flawed u-boot
    on each shelf, applies fix if svn5399 detected, reports status per shelf.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=2, with_defaults="trim", content="config")
    num_shelves = len(shelves)
    g30_user = os.environ["G30_USER"]
    g30_pass = os.environ["G30_PASSWORD"]
    try:
        result = asyncio.run(
            _async_wrapper_for_step_patch_uboot_of_g30_chassis(lo_ip, g30_user, g30_pass, shelves=num_shelves)
        )
    except TimeoutError:
        result = asyncio.run(
            _async_wrapper_for_step_patch_uboot_of_g30_chassis(mngmt_ip, g30_user, g30_pass, shelves=num_shelves)
        )
    return {"status": result}


@step("Check swload version G30")
def check_active_sw_version(current_version: str, lo_ip: str, mngmt_ip: str) -> State:
    """Verifies active softwareload version matches expected current_version.

    Queries G30 CLI for active swload; raises ValueError if mismatch.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    swloads = g30.data.ne_ne.system.sw_management.softwareload.retrieve()
    active_version = next(s.swload_version for s in swloads if s.swload_state.value == "Active")
    logger.info("Active softwareload version: %s", active_version)

    if active_version == current_version:
        return {"status": f"G30 softwareload version matches {current_version}."}

    msg = (
        f"G30 softwareload version is not {current_version}, upgrade not possible. "
        f"Active version found: {active_version}"
    )
    raise ValueError(msg)


@step("Delete sessions")
def delete_all_sessions(lo_ip: str, mngmt_ip: str) -> State:
    """Deletes all active sessions on G30 via CLI command.

    Prepares clean session state before software upgrade.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    g30.operations.cli_command(commands="delete session*", echo="off")
    return {"Sessions Deleted": True}


@step("Backup G30 database")
def backup_database(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Backs up G30 database to timestamped SFTP location.

    Uses G30 upload operation with file_description 'Backup G30 database'.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    string_dt = dt.strftime("%Y_%m_%d_%H_%M")

    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_DB_{string_dt}.zip"),
        password=SFTP_PASS,
        filetype="database",
    )
    return {"status": request_g30}


@step("Upload security log G30")
def upload_security_log(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Uploads G30 security log to timestamped SFTP location.

    Uses G30 upload operation with filetype 'securitylog'.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    string_dt = dt.strftime("%Y_%m_%d_%H_%M")
    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_security_log_{string_dt}.zip"),
        password=SFTP_PASS,
        filetype="securitylog",
    )
    return {"status": request_g30}


@step("Upload summary log G30")
def upload_summary_log(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str) -> State:
    """Uploads G30 summary log to timestamped SFTP location.

    Uses G30 upload operation with filetype 'summarylog'.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    dt = datetime.now(tz=UTC)
    string_dt = dt.strftime("%Y_%m_%d_%H_%M")
    request_g30 = g30.operations.upload(
        destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_summary_log_{string_dt}.zip"),
        password=SFTP_PASS,
        filetype="summarylog",
    )
    return {"status": request_g30}


def _upload_diagnostics_log(lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str, callback_url: str) -> None:
    """Background thread: triggers diagnostics log upload on G30 and POSTs to the callback URL when done."""
    string_dt = datetime.now(tz=UTC).strftime("%Y_%m_%d_%H_%M")
    logger.info("Diagnostics upload thread started", extra={"fqdn": fqdn})
    requests.post(f"{callback_url}/progress", json={"status": "upload in progress"}, verify=False, timeout=10)  # noqa: S501
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    try:
        g30.operations.upload(
            destination=BACKUP_PATH.substitute(file_name=f"{fqdn}_{current_version}_diagnostics_log_{string_dt}.zip"),
            password=SFTP_PASS,
            filetype="diagnosticslog",
        )
        logger.info("Diagnostics log upload completed", extra={"fqdn": fqdn})
        requests.post(callback_url, json={"status": "completed"}, verify=False, timeout=10)  # noqa: S501
    except Exception as exc:
        logger.exception("Diagnostics log upload failed", extra={"fqdn": fqdn})
        with contextlib.suppress(Exception):
            requests.post(callback_url, json={"status": "timeout", "message": str(exc)}, verify=False, timeout=10)  # noqa: S501


@step("Upload diagnostics log G30")
def start_diagnostics_log_upload(
    callback_route: str, lo_ip: str, mngmt_ip: str, fqdn: str, current_version: str
) -> State:
    """Starts a background thread that uploads the G30 diagnostics log and fires the callback when done."""
    logger.info("Diagnostics log start entered", extra={"fqdn": fqdn})

    callback_url = f"{_ORCHESTRATOR_URL}{callback_route}"
    threading.Thread(
        target=_upload_diagnostics_log,
        args=(lo_ip, mngmt_ip, fqdn, current_version, callback_url),
        daemon=True,
    ).start()


@step("Validate diagnostics log upload")
def validate_diagnostics_log_upload(callback_result: dict) -> State:
    """Validates the callback result from the diagnostics log upload thread."""
    if callback_result.get("status") != "completed":
        msg = f"Diagnostics log upload failed: {callback_result.get('message', 'unknown error')}"
        raise ValueError(msg)
    return {"status": "Diagnostics log uploaded"}


upload_diagnostics_log_callback = callback_step(
    name="Upload diagnostics log G30",
    action_step=start_diagnostics_log_upload,
    validate_step=validate_diagnostics_log_upload,
)


def _verify_sw_image_downloaded(g30: G30Client, new_version: str) -> str:
    """Queries the inactive slot and returns the version string, raising ValueError if not matching."""
    swloads = g30.data.ne_ne.system.sw_management.softwareload.retrieve()
    inactive = next((s for s in swloads if s.swload_state.value == "Inactive"), None)
    if inactive is None:
        raise ValueError("Inactive slot empty after download")
    if inactive.swload_version != new_version:
        msg = f"G30 softwareload version {new_version} not found after download"
        raise ValueError(msg)
    return inactive.swload_version


def _download_sw_image(lo_ip: str, mngmt_ip: str, new_version: str, callback_url: str) -> None:
    """Background thread: downloads G30 SW image, verifies the version, and fires callback when done."""
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    swloads = g30.data.ne_ne.system.sw_management.softwareload.retrieve()
    inactive = next((s for s in swloads if s.swload_state.value == "Inactive"), None)
    if inactive is not None and inactive.swload_version == new_version:
        requests.post(callback_url, json={"status": "completed", "already_downloaded": True}, verify=False, timeout=10)  # noqa: S501
        return
    with contextlib.suppress(Exception):
        requests.post(f"{callback_url}/progress", json={"status": "download in progress"}, verify=False, timeout=5)  # noqa: S501
    try:
        g30.operations.download(
            source=SW_IMAGES_PATH.substitute(version=new_version[2:]),
            password=SFTP_PASS,
            filetype="swimage",
        )
        with contextlib.suppress(Exception):
            requests.post(
                f"{callback_url}/progress", json={"status": "verifying downloaded version"}, verify=False, timeout=5
            )  # noqa: E501, S501
        version = _verify_sw_image_downloaded(g30, new_version)
        requests.post(callback_url, json={"status": "completed", "version": version}, verify=False, timeout=10)  # noqa: S501
    except Exception as exc:  # noqa: BLE001
        with contextlib.suppress(Exception):
            requests.post(callback_url, json={"status": "failed", "message": str(exc)}, verify=False, timeout=10)  # noqa: S501


@step("Download new software image on G30")
def start_sw_image_download(callback_route: str, lo_ip: str, mngmt_ip: str, new_version: str) -> State:
    """Starts a background thread that downloads the G30 SW image and fires the callback when done."""
    callback_url = f"{_ORCHESTRATOR_URL}{callback_route}"
    threading.Thread(
        target=_download_sw_image,
        args=(lo_ip, mngmt_ip, new_version, callback_url),
        daemon=True,
    ).start()
    return {"sw_image_download_started": True}


@step("Validate SW image download")
def validate_sw_image_download(callback_result: dict) -> State:
    """Validates the callback result from the SW image download thread."""
    if callback_result.get("status") != "completed":
        msg = f"SW image download failed: {callback_result.get('message', 'unknown error')}"
        raise ValueError(msg)
    return {"status": f"SW image downloaded. {callback_result.get('response', '')}".strip()}


download_sw_image_callback = callback_step(
    name="Download new software image on G30",
    action_step=start_sw_image_download,
    validate_step=validate_sw_image_download,
)


@step("Activate G30 software image")
def activate_sw_image_and_update_current_sw_version(lo_ip: str, mngmt_ip: str, new_version: str) -> State:
    """Activates inactive SW image and updates current_version in state.

    Executes 'activate swimage' CLI, waits 15s.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(commands="activate swimage upgrade-db", echo="off")
    time.sleep(15)
    return {"status": request_g30, "current_version": new_version}


@step("Warm restart ne with FPGA upgrade for OCC2 card")
def warm_restart_ne_with_fpga_upgrade(lo_ip: str, mngmt_ip: str) -> State:
    """Performs warm restart of NE with optional FPGA/DSP upgrades.

    Initiates restart via G30 operations; raises if not 'In-progress'.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    status = g30.operations.restart(entity_id="ne:ne", restart_type="warm", fpga_upgrade=None)

    if status.status != "In-progress":
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
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands=("show sw-management current-fw-version-* fw-equipment-type=OCC2 fw-state=not-current"),
        echo="off",
    )
    logger.info(f"{request_g30}")  # noqa: G004
    if not request_g30.result.strip():
        return {"status": "All OCC2 cards are updated."}

    msg = f"OCC2 cards need to be restarted to complete the upgrade.\nCurrent software state: {request_g30.result}"
    raise UserWarning(msg)


@step("Warm restart ne with DSP upgrade for CHM2T card")
def warm_restart_ne_with_dsp_upgrade(lo_ip: str, mngmt_ip: str) -> State:
    """Performs warm restart of NE with optional FPGA/DSP upgrades.

    Initiates restart via G30 operations; raises if not 'In-progress'.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    status = g30.operations.restart(entity_id="ne:ne", restart_type="warm", dsp_upgrade=None)

    if status.status != "In-progress":
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
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    request_g30 = g30.operations.cli_command(
        commands=("show sw-management current-fw-version-* fw-equipment-type=CHM2T fw-state=not-current"),
        echo="off",
    )
    if not request_g30.result.strip():
        return {"status": "All CHM2T cards are updated."}

    msg = f"CHM2T cards need to be restarted to complete the upgrade.\nCurrent software state: {request_g30.result}"
    raise UserWarning(msg)


def _get_och_os_list(lo_ip: str, mngmt_ip: str) -> list[dict[str, Any]]:
    """Retrieves a list of OCH OS instances from the G30.

    Fetches optical channel details including alias, Q-factor, availability status,
    actual TX optical power, and actual frequency for all 'up' admin-status channels.
    """
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
    g30_request = g30.operations.cli_command(
        commands=(
            "show och-os admin-status=up alias-name Q-factor avail-status actual-tx-optical-power actual-frequency | display json"  # noqa: E501
        ),
        echo="off",
    )
    text = g30_request.result.strip()
    inner = text[1:-1].replace('"ne:och-os":', "")
    return json.loads(f"[{inner}]")


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


def _cold_restart_chm1s(
    lo_ip: str, mngmt_ip: str, ochs_before_upgrade: dict[str, Any], interfaces_to_check: dict, callback_url: str
) -> None:
    """Background thread: loops every 15s restarting CHM1 cards until all are done, then fires callback."""
    while True:
        try:
            g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
            check_optical_circuits(lo_ip, mngmt_ip, ochs_before_upgrade)
            raise_if_no_traffic_btw_routers(interfaces_to_check)
            result = g30.operations.cli_command(
                commands=(
                    "show current-fw-version-card-*/*/CHM-DSP"
                    " fw-equipment-type=CHM1 fw-state=not-current | display json"
                ),
                echo="off",
            )
            text = result.result.strip()
            if not text:
                requests.post(callback_url, json={"status": "completed"}, verify=False, timeout=10)  # noqa: S501
                return
            data = json.loads(text)
            cards_to_restart = data.get("ne:current-fw-version", [])
            if isinstance(cards_to_restart, dict):
                cards_to_restart = [cards_to_restart]
            if not cards_to_restart:
                requests.post(callback_url, json={"status": "completed"}, verify=False, timeout=10)  # noqa: S501
                return
            card = cards_to_restart[0]
            status = g30.operations.restart(entity_id=card["equipment-entity"], restart_type="cold")
            if status.status != "In-progress":
                msg = f"Failed to restart CHM1 card {card['equipment-entity']}"
                requests.post(callback_url, json={"status": "failed", "message": msg}, verify=False, timeout=10)  # noqa: S501
                return
            with contextlib.suppress(Exception):
                requests.post(
                    f"{callback_url}/progress",
                    json={"status": f"cold restarting {card['equipment-entity']}"},
                    verify=False,  # noqa: S501
                    timeout=5,
                )
        except Exception as exc:  # noqa: BLE001
            with contextlib.suppress(Exception):
                requests.post(
                    f"{callback_url}/progress", json={"status": "waiting", "error": str(exc)}, verify=False, timeout=5
                )  # noqa: E501, S501
        time.sleep(15)


@step("Start cold restart CHM1 cards one-by-one")
def start_cold_restart_chm1s(
    callback_route: str, lo_ip: str, mngmt_ip: str, ochs_before_upgrade: dict[str, Any], interfaces_to_check: dict
) -> State:
    """Starts a background thread that cold restarts CHM1 cards one by one and fires the callback when done."""
    callback_url = f"{_ORCHESTRATOR_URL}{callback_route}"
    threading.Thread(
        target=_cold_restart_chm1s,
        args=(lo_ip, mngmt_ip, ochs_before_upgrade, interfaces_to_check, callback_url),
        daemon=True,
    ).start()
    return {"chm1_cold_restart_started": True}


@step("Validate CHM1 cold restart")
def validate_cold_restart_chm1s(callback_result: dict) -> State:
    """Validates the callback result from the CHM1 cold restart thread."""
    if callback_result.get("status") != "completed":
        msg = f"CHM1 cold restart failed: {callback_result.get('message', 'unknown error')}"
        raise ValueError(msg)
    return {"status": "All CHM1 cards restarted successfully."}


cold_restart_chm1s_callback = callback_step(
    name="Cold restart CHM1 cards one-by-one",
    action_step=start_cold_restart_chm1s,
    validate_step=validate_cold_restart_chm1s,
)


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
    g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)

    try:
        alarms = g30.data.ne_ne.fault.standing_condition.retrieve(depth=2, with_defaults="trim", content="nonconfig")
    except HTTPError as e:
        if e.response.status_code == 404:  # noqa: PLR2004
            return set()
        raise

    alarm_set = set()
    for alarm in alarms:
        if alarm.severity_level in ["critical", "major"]:
            alarm_string = (
                f"{alarm.fm_entity};{alarm.location};{alarm.direction}"
                f";{alarm.condition_type};{alarm.condition_description}"
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


def _wait_for_g30_responsive(
    lo_ip: str, mngmt_ip: str, callback_url: str, max_attempts: int = 1800, poll_interval: int = 10
) -> None:
    """Background thread: polls G30 until responsive, then POSTs to the callback URL."""
    for attempt in range(1, max_attempts + 1):
        try:
            g30 = G30Client(loopback_ip=lo_ip, management_ip=mngmt_ip)
            result = g30.data.ne_ne.retrieve(content="nonconfig", depth=2, with_defaults="trim")
            if result:
                logger.info("G30 is back online", extra={"attempt": attempt, "mngmt_ip": mngmt_ip})
                requests.post(callback_url, json={"status": "up", "attempts": attempt}, verify=False, timeout=10)  # noqa: S501
                return
        except Exception as exc:  # noqa: BLE001
            logger.info("G30 not yet responsive", extra={"attempt": attempt, "error": str(exc)})
            with contextlib.suppress(Exception):
                requests.post(
                    f"{callback_url}/progress",
                    json={"attempt": attempt, "max_attempts": max_attempts, "error": str(exc)},
                    verify=False,  # noqa: S501
                    timeout=5,
                )
        time.sleep(poll_interval)

    logger.error("G30 did not come back online within max attempts", extra={"mngmt_ip": mngmt_ip})
    with contextlib.suppress(Exception):
        requests.post(
            callback_url,
            json={"status": "timeout", "message": f"G30 {mngmt_ip} did not respond after {max_attempts} attempts"},
            verify=False,  # noqa: S501
            timeout=10,
        )


@step("Start G30 responsiveness monitor")
def start_g30_monitor(callback_route: str, lo_ip: str, mngmt_ip: str) -> State:
    """Starts a background thread that monitors G30 responsiveness and fires the callback when the device is up."""
    callback_url = f"{_ORCHESTRATOR_URL}{callback_route}"
    threading.Thread(
        target=_wait_for_g30_responsive,
        args=(lo_ip, mngmt_ip, callback_url),
        daemon=True,
    ).start()
    return {"g30_monitor_started": True}


@step("Validate G30 is responsive")
def validate_g30_up(callback_result: dict) -> State:
    """Validates the callback result from the G30 responsiveness monitor."""
    if callback_result.get("status") != "up":
        msg = f"G30 did not come back online: {callback_result.get('message', 'unknown error')}"
        raise ValueError(msg)
    return {"g30_responsive": True, "monitor_attempts": callback_result.get("attempts")}


wait_for_g30_up_callback = callback_step(
    name="Wait for G30 to become responsive",
    action_step=start_g30_monitor,
    validate_step=validate_g30_up,
)


@workflow(
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
        >> upload_diagnostics_log_callback
        >> download_sw_image_callback
    )

    activate_and_check = (
        begin
        >> activate_sw_image_and_update_current_sw_version
        >> wait_for_g30_up_callback
        >> check_active_sw_version
        >> compare_alarms_to_those_before_upgrading
        >> conditional(lambda state: state["unexpected_alarms"] != [])(approve_unexpected_alarms)
        >> step("Checking that no optical circuit has gone down")(check_optical_circuits)
    )

    warm_restart_and_check = (
        begin
        >> warm_restart_ne_with_fpga_upgrade
        >> wait_for_g30_up_callback
        >> conditional(lambda state: state["is_occ2_in_node_and_is_fpga_restart_needed"])(check_occ2_updated)
        >> conditional(lambda state: state["is_chm2t_in_node_and_is_dsp_restart_needed"])(
            warm_restart_ne_with_dsp_upgrade
        )
        >> conditional(lambda state: state["is_chm2t_in_node_and_is_dsp_restart_needed"])(wait_for_g30_up_callback)
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
        >> conditional(lambda state: state["are_chm1s_in_node_and_is_cold_restart_needed"])(cold_restart_chm1s_callback)
        >> update_variables_472_480
        >> pre_upgrade_operations
        >> activate_and_check
        >> done
    )
