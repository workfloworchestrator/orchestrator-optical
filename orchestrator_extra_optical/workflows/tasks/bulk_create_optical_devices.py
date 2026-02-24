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

import csv
from io import StringIO
from re import match
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

from orchestrator_extra_optical.products.product_blocks.optical_device import DeviceType, Platform, Vendor
from orchestrator_extra_optical.utils.custom_types.ip_address import IPAddress
from orchestrator_extra_optical.workflows.shared import subscriptions_by_product_type_and_instance_value

achtung = (
    "This task will launch a sub-workflow for each device. "
    "Make sure there are all necessary PoPs in the WFO or the sub-workflows will fail!"
    "Check each sub-workflow progress in the Subscriptions page."
    "If you are sure you want to proceed, replace this warning message with 'CREATE'."
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

CsvData = Annotated[
    str,
    Field(
        "pop_code,vendor,platform,device_type,fqdn_prefix_before_pop,lo_ip,mngmt_ip\n",
        title="CSV Data",
        json_schema_extra={
            "format": "long",
        },
    ),
]
Delimiter = Annotated[
    str,
    Field(
        ",",
        description="CSV delimiter character",
        title="Delimiter",
    ),
]


def initial_input_form_generator() -> FormGenerator:
    class CSVDataForm(FormPage):
        achtung: Achtung
        csv_data: CsvData
        delimiter: Delimiter

        @model_validator(mode="after")
        def validate_csv(self) -> "CSVDataForm":
            if self.achtung != "CREATE":
                msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
                raise ValueError(
                    msg
                )

            if not self.csv_data.strip():
                msg = "CSV content is empty"
                raise ValueError(msg)

            required_headers = set(
                h.strip() for h in CsvData.__metadata__[0].default.split(",")
            )
            csv_io = StringIO(self.csv_data)
            dict_reader = csv.DictReader(csv_io)
            devices = list(dict_reader)

            for k in devices[0].keys():
                if k not in required_headers:
                    raise ValueError(f"Header {k} is not valid")
                required_headers.remove(k)

            if required_headers:
                raise ValueError(f"Missing headers: {required_headers}")

            for idx, device in enumerate(devices):
                device["pop_code"] = device["pop_code"].upper()
                match_pop_code = match(r"^[A-Z]{2}[0-9]{2}$", device["pop_code"])
                if not match_pop_code:
                    raise ValueError(
                        f"Invalid PoP code '{device['pop_code']} at row {idx + 1}"
                    )

                vendor_str = device["vendor"]
                try:
                    device["vendor"] = Vendor(vendor_str)
                except ValueError:
                    raise ValueError(
                        f"Invalid vendor '{vendor_str}' at row {idx + 1}. Valid values are: {', '.join([v.value for v in Vendor])}"
                    )

                platform_str = device["platform"]
                try:
                    device["platform"] = Platform(platform_str)
                except ValueError:
                    raise ValueError(
                        f"Invalid platform '{platform_str}' at row {idx + 1}. Valid values are: {', '.join([p.value for p in Platform])}"
                    )

                device_type_str = device["device_type"]
                try:
                    device["device_type"] = DeviceType(device_type_str)
                except ValueError:
                    raise ValueError(
                        f"Invalid platform '{device_type_str}' at row {idx + 1}. Valid values are: {', '.join([d.value for d in DeviceType])}"
                    )

                if device["lo_ip"]:
                    device["lo_ip"] = IPAddress(device["lo_ip"])
                else:
                    device["lo_ip"] = None

                if device["mngmt_ip"]:
                    device["mngmt_ip"] = IPAddress(device["mngmt_ip"])
                else:
                    device["mngmt_ip"] = None

            self.csv_data = devices
            return self

    user_input = yield CSVDataForm
    user_input_dict = user_input.dict()
    return user_input_dict


@step("Looking for PoPs and duplicate addresses in the subscriptions")
def find_pops_and_duplicate_addresses(
    csv_data: list[dict[str, str]],
) -> State:
    partner_id = NotImplementedError("Not implemented")  # FIXME

    input_data = []
    pops_ids = {}
    for device in csv_data:
        for address in ["lo_ip", "mngmt_ip"]:
            duplicates = subscriptions_by_product_type_and_instance_value(
                "optical_device",
                address,
                device[address],
                status=[SubscriptionLifecycle.ACTIVE],
            )
            if duplicates:
                raise ValueError(
                    f"IP {device[address]} is already in use by another device"
                )

        if device["pop_code"] not in pops_ids:
            subscriptions_matching_pop_code = (
                subscriptions_by_product_type_and_instance_value(
                    "PoP",
                    "code",
                    device["pop_code"],
                    status=[SubscriptionLifecycle.ACTIVE],
                )
            )
            if len(subscriptions_matching_pop_code) != 1:
                raise ValueError(
                    f"PoP code {device['pop_code']} not found or not unique"
                )
            pops_ids[device["pop_code"]] = subscriptions_matching_pop_code[
                0
            ].subscription_id

        pop_id = pops_ids[device["pop_code"]]

        input_data.append(
            {
                "partner_id": partner_id,
                "pop_id": pop_id,
                "vendor": device["vendor"],
                "platform": device["platform"],
                "device_type": device["device_type"],
                "fqdn_prefix_before_pop": device["fqdn_prefix_before_pop"],
                "lo_ip": device["lo_ip"],
                "mngmt_ip": device["mngmt_ip"],
            }
        )

    return {"devices": input_data}


@step("Create workflow input forms")
def create_workflow_inputs(devices: list[dict]) -> State:
    """
    Constructs the input list required to initiate sub-workflows for creating devices.

    This function simulates user-filled forms by building the necessary input dictionaries
    based on the device data provided. For workflows decorated with `@create_workflow`, an
    initial input containing only the product ID is required, followed by one or more input
    dictionaries with actual device field values (e.g., 'code', 'full_name').

    For example, if the workflow is `create_pop.py` and expects device fields such as
    'code' and 'full_name', the function will return a list like:

        [
            {'product': product_id},
            {'code': 'code_value', 'full_name': 'full_name_value', ...}
        ]

    Args:
        devices (list[dict]): A list of dictionaries where each dictionary contains the
            field values for a single device to be created.

    Returns:
        State: A State object containing the assembled list of input dictionaries required
            by the workflow.

    Raises:
        ValueError: If the product cannot be retrieved by name.
    """
    product_id = get_product_by_name("optical_device").product_id

    input_forms = []
    for device in devices:
        user_inputs = []
        user_inputs.append({"product": product_id})
        user_inputs.append(device)
        user_inputs.append({}) # empty dict for the summary/confirmation form step
        input_forms.append(user_inputs)

    return {"workflow_input_forms": input_forms}


@step("Start Sub-Workflows")
def start_sub_workflows(workflow_input_forms: list[State]) -> State:
    process_ids: list[UUIDstr] = []
    while workflow_input_forms:
        user_inputs = workflow_input_forms[-1]
        with db.database_scope():
            process_id = start_process(
                "create_optical_device", user_inputs=user_inputs, user="SYSTEM"
            )
            process_ids.append(process_id)
        workflow_input_forms.pop()
        sleep(1)

    return {"process_ids": process_ids}


@workflow(
    "Create optical devices in bulk from CSV data",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def bulk_create_optical_devices() -> StepList:
    return (
        begin
        >> find_pops_and_duplicate_addresses
        >> create_workflow_inputs
        >> start_sub_workflows
        >> done
    )
