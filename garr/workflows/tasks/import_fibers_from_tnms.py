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

import json
import re
from time import sleep
from typing import Annotated

from orchestrator.db import db
from orchestrator.forms import FormPage
from orchestrator.services.processes import start_process
from orchestrator.services.products import get_product_by_name
from orchestrator.targets import Target
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, done, step, workflow
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import LongText

from services.infinera import tnms_client
from workflows.shared import subscriptions_by_product_type_and_instance_value

achtung = (
    "This task will launch a sub-workflow for each fiber between two FlexILS nodes "
    "that is present in the TNMS but not yet present in the WFO. "
    "Make sure there are all necessary devices in the WFO or the sub-workflow will fail. "
    "Check progress of each fiber being created on the Subscriptions page after clicking Run."
    "If you are sure you want to proceed, replace this warning message with 'IMPORT'."
)
Achtung = Annotated[
    str,
    Field(
        achtung,
        title="⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️",
        json_schema_extra={
            "format": "long",
        },
    ),
]


def fecth_fibers_from_tnms(
    src_node_re: str, dst_node_re: str, src_port_re: str, dst_port_re: str
) -> list[dict[str, str]]:
    src_node_re = re.compile(src_node_re)
    dst_node_re = re.compile(dst_node_re)
    src_port_re = re.compile(src_port_re)
    dst_port_re = re.compile(dst_port_re)

    fibers = tnms_client.data.equipment.physical_span.retrieve(fields=["access-port"])
    devices = tnms_client.data.equipment.devices.retrieve(
        fields=["name(value)", "uuid", "access-port(name(value);uuid)"]
    )

    port_by_uuid = {}
    device_by_uuid = {}
    for device in devices:
        device_name = device["name"][0]["value"]
        device_by_uuid[device["uuid"]] = device_name

        for port in device["access-port"]:
            port_name = port["name"][0]["value"]
            # e.g. Line PTP 1-A-1.L1 or Optical-TTP 1-1.1
            port_name = port_name.split(" ")[-1]
            # e.g. 1-A-1.L1 or 1-1.1
            port_name = port_name.replace(".", "-")
            # e.g. 1-A-1-L1 or 1-1-1

            if "flex" not in device_name:
                port_name = port_name.replace("-", "/")
                port_name = "port-" + port_name

            port_by_uuid[port["uuid"]] = port_name

    fetched_fibers = []
    for f in fibers:
        access_ports = f.get("access-port", [])

        if len(access_ports) != 2 or not isinstance(access_ports, list):
            continue

        src_device_nms_uuid = access_ports[0].get("device-uuid", None)
        dst_device_nms_uuid = access_ports[1].get("device-uuid", None)
        src_port_uuid = access_ports[0].get("access-port-uuid", None)
        dst_port_uuid = access_ports[1].get("access-port-uuid", None)
        if not src_device_nms_uuid or not dst_device_nms_uuid or not src_port_uuid or not dst_port_uuid:
            continue

        src_device_name = device_by_uuid[src_device_nms_uuid]
        src_port_name = port_by_uuid[src_port_uuid]
        dst_device_name = device_by_uuid[dst_device_nms_uuid]
        dst_port_name = port_by_uuid[dst_port_uuid]
        if (
            src_device_name == dst_device_name
            or not re.match(src_node_re, src_device_name)
            or not re.match(dst_node_re, dst_device_name)
            or not re.match(src_port_re, src_port_name)
            or not re.match(dst_port_re, dst_port_name)
        ):
            continue

        reversed_fiber = {
            "src_device_name": dst_device_name,
            "src_port_name": dst_port_name,
            "dst_device_name": src_device_name,
            "dst_port_name": src_port_name,
            "src_device_nms_uuid": dst_device_nms_uuid,
            "dst_device_nms_uuid": src_device_nms_uuid,
        }
        if reversed_fiber in fetched_fibers:
            continue

        fetched_fibers.append(
            {
                "src_device_name": src_device_name,
                "src_port_name": src_port_name,
                "dst_device_name": dst_device_name,
                "dst_port_name": dst_port_name,
                "src_device_nms_uuid": src_device_nms_uuid,
                "dst_device_nms_uuid": dst_device_nms_uuid,
            }
        )

    return fetched_fibers


def initial_input_form_generator() -> FormGenerator:
    class WarningForm(FormPage):
        achtung: Achtung
        source_device_name_regular_expression: str = r"flex\.[a-z]{2}[0-9]{2}"
        destination_device_name_regular_expression: str = r"flex\.[a-z]{2}[0-9]{2}"
        source_port_name_regular_expression: str = r"\d-A-\d-L\d"
        destination_port_name_regular_expression: str = r"\d-A-\d-L\d"

        @model_validator(mode="after")
        def validate_csv(self) -> "WarningForm":
            if self.achtung != "IMPORT":
                msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
                raise ValueError(msg)
            return self

    user_input = yield WarningForm
    user_input_dict = user_input.dict()

    fibers = fecth_fibers_from_tnms(
        user_input_dict["source_device_name_regular_expression"],
        user_input_dict["destination_device_name_regular_expression"],
        user_input_dict["source_port_name_regular_expression"],
        user_input_dict["destination_port_name_regular_expression"],
    )

    class ReviewForm(FormPage):
        fetched_fibers: LongText = json.dumps(fibers, indent=4)

    user_input = yield ReviewForm
    user_input_dict.update(user_input.dict())

    user_input_dict["fetched_fibers"] = json.loads(user_input_dict["fetched_fibers"])

    return user_input_dict


@step("Finding the subscriptions of the devices")
def find_devices_subscriptions(fetched_fibers: list[dict[str, str]]) -> State:
    """
    Find subscriptions for the devices in the TNMS data.
    """
    device_sub_id_by_nms_uuid = {}
    for fiber in fetched_fibers:
        for nms_uuid in [fiber["src_device_nms_uuid"], fiber["dst_device_nms_uuid"]]:
            if nms_uuid not in device_sub_id_by_nms_uuid:
                device_subscriptions = subscriptions_by_product_type_and_instance_value(
                    "OpticalDevice",
                    "nms_uuid",
                    nms_uuid,
                    status=[SubscriptionLifecycle.ACTIVE],
                )
                if len(device_subscriptions) != 1:
                    raise ValueError(f"Device with NMS UUID {nms_uuid} not found or not unique")
                device_sub_id_by_nms_uuid[nms_uuid] = device_subscriptions[0].subscription_id

    return {"device_sub_id_by_nms_uuid": device_sub_id_by_nms_uuid}


@step("Discarding already created fibers")
def discard_already_created_fibers(fetched_fibers: list[dict[str, str]]) -> State:
    sifted_fibers = []
    for fiber in fetched_fibers:
        src_device_fqdn = fiber["src_device_name"] + ".garr.net"
        dst_device_fqdn = fiber["dst_device_name"] + ".garr.net"
        subs = subscriptions_by_product_type_and_instance_value(
            "optical_fiber",
            "fiber_name",
            f"{src_device_fqdn} {fiber['src_port_name']} --- {dst_device_fqdn} {fiber['dst_port_name']}",
            status=[SubscriptionLifecycle.ACTIVE],
        )
        if subs:
            continue
        subs = subscriptions_by_product_type_and_instance_value(
            "optical_fiber",
            "fiber_name",
            f"{dst_device_fqdn} {fiber['dst_port_name']} --- {src_device_fqdn} {fiber['src_port_name']}",
            status=[SubscriptionLifecycle.ACTIVE],
        )
        if subs:
            continue
        sifted_fibers.append(fiber)

    return {"sifted_fibers": sifted_fibers}


@step("Create workflow input forms")
def create_workflow_inputs(sifted_fibers: list[dict[str, str]], device_sub_id_by_nms_uuid: dict[str, UUIDstr]) -> State:
    """
    Create the list of input forms for the sub-workflows as if they were filled
    by the user.
    """
    product_id = get_product_by_name("optical_fiber").product_id

    input_forms = []
    for fiber in sifted_fibers:
        user_inputs = []
        user_inputs.append({"product": product_id})
        user_inputs.append(
            {
                "garrxdb_id": None,
                "total_loss": None,
                "fiber_types": None,
                "lengths": None,
                "sub_id_device_a": device_sub_id_by_nms_uuid[fiber["src_device_nms_uuid"]],
                "sub_id_device_b": device_sub_id_by_nms_uuid[fiber["dst_device_nms_uuid"]],
            }
        )
        user_inputs.append(
            {
                "name_port_a": fiber["src_port_name"],
                "name_port_b": fiber["dst_port_name"],
            }
        )
        input_forms.append(user_inputs)
        user_inputs.append({})  # empty dict for the summary/confirmation form step

    return {"workflow_input_forms": input_forms}


@step("Start Sub-Workflows")
def start_sub_workflows(workflow_input_forms: list[State]) -> State:
    process_ids: list[UUIDstr] = []
    while workflow_input_forms:
        user_inputs = workflow_input_forms[-1]
        with db.database_scope():
            process_id = start_process("create_optical_fiber", user_inputs=user_inputs, user="SYSTEM")
            process_ids.append(process_id)
        workflow_input_forms.pop()
        sleep(1)

    return {"process_ids": process_ids}


@workflow(
    "Import fibers from TNMS",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def import_fibers_from_tnms() -> StepList:
    return (
        begin
        >> find_devices_subscriptions
        >> discard_already_created_fibers
        >> create_workflow_inputs
        >> start_sub_workflows
        >> done
    )
