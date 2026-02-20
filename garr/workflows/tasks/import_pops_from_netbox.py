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

from services import netbox
from workflows.shared import subscriptions_by_product_type_and_instance_value

achtung = (
    "Make sure there is a partner subscription for GARR! "
    "This task will launch a sub-workflow for each PoP in Netbox "
    "that is not yet present in the WFO. "
    "Check progress on the Subscriptions page."
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


def initial_input_form_generator() -> FormGenerator:
    class WarningForm(FormPage):
        achtung: Achtung

        @model_validator(mode="after")
        def validate_csv(self) -> "WarningForm":
            if self.achtung != "IMPORT":
                msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
                raise ValueError(
                    msg
                )
            return self

    user_input = yield WarningForm
    user_input_dict = user_input.dict()
    return user_input_dict


@step("Fetch input data")
def fetch_input_data() -> State:
    pop_group = netbox.api.dcim.site_groups.get(name="PoP")
    pop_group_id = pop_group.id
    pops = netbox.api.dcim.sites.filter(group_id=pop_group_id)
    input_data = []
    for pop in pops:
        if pop.custom_fields.get("garrx_db_id") is None or not match(
            r"^[A-Z0-9]{4}$", pop.slug.upper()
        ):
            continue
        input_data.append(
            {
                "netbox_id": pop.id,
                "code": pop.slug.upper(),
                "full_name": pop.name,
                "latitude": str(pop.latitude) if pop.latitude else None,
                "longitude": str(pop.longitude) if pop.longitude else None,
                "garrxdb_id": pop.custom_fields["garrx_db_id"],
            }
        )
    return {"pops": input_data}


@step("Discard already created PoPs")
def discard_already_created_pops(pops: list[dict]) -> State:
    product_name = "PoP"

    remaining_pops = []
    pops_already_in_db = []
    for pop in pops:
        code = pop["code"]
        is_pop_in_db = subscriptions_by_product_type_and_instance_value(
            product_name, "code", code, [x for x in SubscriptionLifecycle]
        )
        if is_pop_in_db:
            pops_already_in_db.append(pop)
        else:
            remaining_pops.append(pop)

    return {"remaining_pops": remaining_pops, "pops_already_in_db": pops_already_in_db}


@step("Create workflow input forms")
def create_workflow_inputs(remaining_pops: list[dict]) -> State:
    """Generate a list of input forms for sub-workflows.

    This step takes a list of POP data and formats it into a list of
    input forms that can be used to initiate "create" sub-workflows.
    An empty dictionary is appended to each input to handle any
    summary or confirmation steps in the sub-workflow.

    Args:
        remaining_pops: A list of dictionaries, where each dictionary
            contains the data for a single POP to be created.

    Returns:
        A state dictionary with the key "workflow_input_forms" containing
            the list of generated input forms.
    """
    # wf of type create expects an additional input with just the product id because of the wrapper @create_workflow.
    product_id = get_product_by_name("pop").product_id

    input_forms = []
    for pop in remaining_pops:
        user_inputs = []
        user_inputs.append({"product": product_id})
        user_inputs.append(pop)
        input_forms.append(user_inputs)
        user_inputs.append({}) # empty dict for the summary/confirmation form step

    return {"workflow_input_forms": input_forms}


@step("Start Sub-Workflows")
def start_sub_workflows(workflow_input_forms: list[State]) -> State:
    process_ids: list[UUIDstr] = []
    while workflow_input_forms:
        user_inputs = workflow_input_forms[-1]
        with db.database_scope():
            process_id = start_process(
                "create_pop", user_inputs=user_inputs, user="SYSTEM"
            )
            process_ids.append(process_id)
        workflow_input_forms.pop()
        sleep(1)

    return {"process_ids": process_ids}


@workflow(
    "Import PoPs from Netbox",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def import_pops_from_netbox() -> StepList:
    return (
        begin
        >> fetch_input_data
        >> discard_already_created_pops
        >> create_workflow_inputs
        >> start_sub_workflows
        >> done
    )
