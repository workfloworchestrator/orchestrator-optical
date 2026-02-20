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

from products.product_blocks.optical_fiber import FiberType
from workflows.shared import subscriptions_by_product_type_and_instance_value

achtung = (
    "This task will launch a sub-workflow for each fiber. "
    "Make sure there are all necessary optical fibers in the WFO or the sub-workflow will fail."
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
        "optical_device_a,port_a,optical_device_b,port_b,garrxdb_id,total_loss,type1-type2-...,length1-length2-...\n",
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
            self._validate_confirmation()
            self._validate_csv_content()

            csv_io = StringIO(self.csv_data)
            dict_reader = csv.DictReader(csv_io)
            fibers = list(dict_reader)

            self._validate_headers(fibers)

            for idx, fiber in enumerate(fibers):
                row_number = idx + 1
                self._validate_device_ports(fiber, row_number)
                fiber = self._validate_and_convert_device_ids(fiber, row_number)
                fiber = self._convert_numeric_values(fiber, row_number)
                fiber = self._validate_and_convert_fiber_specifications(fiber, row_number)

            self.csv_data = fibers
            return self

        def _validate_confirmation(self) -> None:
            if self.achtung != "CREATE":
                msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
                raise ValueError(
                    msg
                )

        def _validate_csv_content(self) -> None:
            if not self.csv_data.strip():
                msg = "CSV content is empty"
                raise ValueError(msg)

        def _validate_headers(self, fibers: list[dict]) -> None:
            required_headers = set(
                h.strip() for h in CsvData.__metadata__[0].default.split(",")
            )

            for k in fibers[0].keys():
                if k not in required_headers:
                    raise ValueError(f"Header {k} is not valid")
                required_headers.remove(k)

            if required_headers:
                raise ValueError(f"Missing headers: {required_headers}")

        def _validate_device_ports(self, fiber: dict, row: int) -> None:
            for device_key, port_key in [
                ("optical_device_a", "port_a"),
                ("optical_device_b", "port_b"),
            ]:
                if fiber[device_key].startswith("g30"):
                    if not match(r"port\-\d{1,2}/\d{1,2}(\.\d{1})?/\d{1,2}", fiber[port_key]):
                        raise ValueError(
                            f"Invalid port format '{fiber[port_key]}' at row {row}. Valid format is port-<shelf>/<slot>/<port> or port-<shelf>/<slot>.<subslot>/<port>"
                        )
                elif fiber[device_key].startswith("flex") or fiber[device_key].startswith("g42"):
                    if not match(r"\d{1,2}(\-[A-Z0-9]{1,3}){1,4}", fiber[port_key]):
                        raise ValueError(
                            f"Invalid port format '{fiber[port_key]}' at row {row}. Valid format is e.g. 1-A-1-L1 or 1-E1-1-T1A or 1-3-L1"
                        )
                else:
                    raise ValueError(
                        f"Invalid optical device '{fiber[device_key]}' at row {row}. Valid FQDNs start with are g30, flex or g42."
                    )

        def _validate_and_convert_device_ids(self, fiber: dict, row: int) -> dict:
            for device_key in ["optical_device_a", "optical_device_b"]:
                subscriptions = subscriptions_by_product_type_and_instance_value(
                    "OpticalDevice",
                    "fqdn",
                    fiber[device_key],
                    status=[SubscriptionLifecycle.ACTIVE],
                )

                if not subscriptions:
                    raise ValueError(
                        f"FQDN {fiber[device_key]} not found or not active at row {row}"
                    )
                if len(subscriptions) > 1:
                    raise ValueError(
                        f"FQDN {fiber[device_key]} is not unique at row {row}"
                    )

                fiber[device_key] = subscriptions[0].subscription_id

            return fiber

        def _convert_numeric_values(self, fiber: dict, row: int) -> dict:
            fiber["total_loss"] = float(fiber["total_loss"]) if fiber["total_loss"] else None
            fiber["garrxdb_id"] = int(fiber["garrxdb_id"]) if fiber["garrxdb_id"] else None
            return fiber

        def _validate_and_convert_fiber_specifications(self, fiber: dict, row: int) -> dict:
            try:
                fiber["type1-type2-..."] = list(map(FiberType, fiber["type1-type2-..."].split("-"))) if fiber["type1-type2-..."] else None
            except ValueError:
                raise ValueError(
                    f"Invalid fiber type '{fiber['type1-type2-...']}' at row {row}. Valid values are: {', '.join([f.value for f in FiberType])}"
                )

            try:
                fiber["length1-length2-..."] = list(map(int, fiber["length1-length2-..."].split("-"))) if fiber["length1-length2-..."] else None
            except ValueError:
                raise ValueError(
                    f"Invalid fiber length '{fiber['length1-length2-...']}' at row {row}. Valid values are integers"
                )

            return fiber

    user_input = yield CSVDataForm
    user_input_dict = user_input.dict()
    return user_input_dict


@step("Create workflow input forms")
def create_workflow_inputs(csv_data: list[dict[str, str]]) -> State:
    """
    Constructs a list of input forms to simulate user-filled forms for a workflow that creates
    optical fibers. This is required for workflows decorated with `@create_workflow`, which
    expects a predefined sequence of inputs.

    Each fiber record from the CSV data results in a list of input dictionaries representing
    multiple sub-form steps:

    1. A dictionary containing only the product ID (required by `@create_workflow`).
    2. A dictionary with device connection details (e.g., device A/B, fiber type, length).
    3. A dictionary with port names.
    4. An empty dictionary for the confirmation/summary step.

    Example output for a single fiber:

        [
            {"product": product_id},
            {
                "sub_id_device_a": "deviceA",
                "sub_id_device_b": "deviceB",
                "garrxdb_id": "GARR123",
                "total_loss": "0.5",
                "fiber_types": "type1-type2",
                "lengths": "100-200"
            },
            {
                "name_port_a": "portA",
                "name_port_b": "portB"
            },
            {}
        ]

    Args:
        csv_data (list[dict[str, str]]): List of dictionaries where each dictionary represents
            a fiber connection record extracted from a CSV file. Each dictionary must contain
            the keys:
            - "optical_device_a"
            - "optical_device_b"
            - "garrxdb_id"
            - "total_loss"
            - "type1-type2-..."
            - "length1-length2-..."
            - "port_a"
            - "port_b"

    Returns:
        State: A dictionary with a single key `"workflow_input_forms"` mapping to a list of
            input forms (lists of dictionaries) required by the workflow.
    """
    product_id = get_product_by_name("optical_fiber").product_id

    input_forms = []
    for fiber in csv_data:
        user_inputs = []
        user_inputs.append({"product": product_id})
        user_inputs.append(
            {
                "sub_id_device_a": fiber["optical_device_a"],
                "sub_id_device_b": fiber["optical_device_b"],
                "garrxdb_id": fiber["garrxdb_id"],
                "total_loss": fiber["total_loss"],
                "fiber_types": fiber["type1-type2-..."],
                "lengths": fiber["length1-length2-..."],
            }
        )
        user_inputs.append(
            {
                "name_port_a": fiber["port_a"],
                "name_port_b": fiber["port_b"],
            }
        )
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
                "create_optical_fiber", user_inputs=user_inputs, user="SYSTEM"
            )
            process_ids.append(process_id)
        workflow_input_forms.pop()
        sleep(1)

    return {"process_ids": process_ids}


@workflow(
    "Create optical fibers in bulk from CSV data",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def bulk_create_optical_fibers() -> StepList:
    return (
        begin
        >> create_workflow_inputs
        >> start_sub_workflows
        >> done
    )
