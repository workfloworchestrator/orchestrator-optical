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

from orchestrator.forms import FormPage
from orchestrator.forms.validators import DisplaySubscription
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.utils import terminate_workflow
from pydantic_forms.types import InputForm, State, UUIDstr
from structlog import get_logger

from products.product_types.partner import Partner

logger = get_logger(__name__)


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr, customer_id: UUIDstr
) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminatePartnerForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore

    return TerminatePartnerForm


@step(

        "Kind reminder! "
        "This workflow just puts this subscription's status in 'terminated' in the WFO database. "
        "It doesn't do anything else."

)
def just_a_reminder(subscription: Partner) -> State:
    return {}


additional_steps = begin


@terminate_workflow(
    "terminate Partner",
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_partner() -> StepList:
    return begin >> just_a_reminder
