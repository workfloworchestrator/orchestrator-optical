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

from orchestrator.domain import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.forms.validators import CustomerId
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import set_status
from orchestrator.workflows.utils import modify_workflow
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import read_only_field
from structlog import get_logger

from products.product_types.partner import (
    Partner,
    PartnerProvisioning,
)
from workflows.shared import modify_summary_form


def subscription_description(subscription: SubscriptionModel) -> str:
    """The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return f"{subscription.partner.partner_name} (Partner Institution)"


logger = get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = Partner.from_subscription(subscription_id)
    partner = subscription.partner

    class ModifyPartnerForm(FormPage):
        customer_id: CustomerId = subscription.customer_id
        name: read_only_field(partner.partner_name)
        type: read_only_field(partner.partner_type)
        garrxdb_id: read_only_field(partner.garrxdb_id)
        netbox_id: read_only_field(partner.netbox_id)

    user_input = yield ModifyPartnerForm
    user_input_dict = user_input.dict()

    summary_fields = ["name", "type", "garrxdb_id", "netbox_id"]
    yield from modify_summary_form(user_input_dict, subscription.partner, summary_fields)

    return user_input_dict | {"subscription": subscription}


@step("Update subscription")
def update_subscription(
    subscription: PartnerProvisioning,
) -> State:
    return {"subscription": subscription}


@step("Update subscription description")
def update_subscription_description(subscription: Partner) -> State:
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


additional_steps = begin


@modify_workflow(
    "modify Partner",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_partner() -> StepList:
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> update_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
