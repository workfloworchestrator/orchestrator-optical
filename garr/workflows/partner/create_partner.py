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

from uuid import uuid4

from orchestrator.domain import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.targets import Target
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription
from orchestrator.workflows.utils import create_workflow
from pydantic import ConfigDict
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_blocks.partner import PartnerType
from products.product_types.partner import PartnerInactive, PartnerProvisioning


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return f"{subscription.partner.partner_name} (Partner Institution)"


logger = get_logger(__name__)


def initial_input_form_generator(product_name: str) -> FormGenerator:
    class CreatePartnerForm(FormPage):
        model_config = ConfigDict(title=product_name)

        partner_name: str
        partner_type: PartnerType
        garrxdb_id: int | None = None
        netbox_id: int | None = None

    user_input = yield CreatePartnerForm
    user_input_dict = user_input.dict()

    return user_input_dict


@step("Construct Subscription model")
def construct_partner_model(
    product: UUIDstr,
    partner_name: str,
    partner_type: PartnerType,
    garrxdb_id: int | None,
    netbox_id: int | None,
) -> State:
    customer_id = str(uuid4())
    subscription = PartnerInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    subscription.partner.partner_name = partner_name
    subscription.partner.partner_type = partner_type
    subscription.partner.garrxdb_id = garrxdb_id
    subscription.partner.netbox_id = netbox_id

    subscription = PartnerProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": subscription.description,
    }


additional_steps = begin


@create_workflow(
    "create Partner",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_partner() -> StepList:
    return begin >> construct_partner_model >> store_process_subscription()
