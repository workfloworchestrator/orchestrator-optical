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

from orchestrator.domain import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.targets import Target
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription
from orchestrator.workflows.utils import create_workflow
from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_types.pop import PopInactive, PopProvisioning
from utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from workflows.partner.shared import get_partner_subscription_by_name
from workflows.shared import create_summary_form, subscriptions_by_product_type_and_instance_value


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return f"{subscription.pop.full_name} (Point of Presence)"


logger = get_logger(__name__)


def initial_input_form_generator(product_name: str) -> FormGenerator:
    class CreatePopForm(FormPage):
        model_config = ConfigDict(title=product_name)

        code: str
        full_name: str
        garrxdb_id: int
        netbox_id: int
        latitude: LatitudeCoordinate | None = None
        longitude: LongitudeCoordinate | None = None

        @model_validator(mode="after")
        def validate_data(self) -> "CreatePopForm":
            if self.code and not match(r"^[A-Z0-9]{4}$", self.code):
                msg = "code must be 4 uppercase alphanumeric characters, e.g. 'AZ99'"
                raise ValueError(
                    msg
                )

            if not self.full_name.startswith(self.code):
                msg = "full_name must start with the code, e.g. 'AZ99-Alpha'"
                raise ValueError(
                    msg
                )

            for resource, value in [
                ("garrxdb_id", self.garrxdb_id),
                ("netbox_id", self.netbox_id),
                ("code", self.code),
            ]:
                subs = subscriptions_by_product_type_and_instance_value(
                    product_type="PoP",
                    resource_type=resource,
                    value=str(value),
                    status=[
                        SubscriptionLifecycle.INITIAL,
                        SubscriptionLifecycle.PROVISIONING,
                        SubscriptionLifecycle.ACTIVE,
                    ],
                )
                if subs:
                    raise ValueError(
                        f"{resource} {value} already in use by subscription {subs[0].subscription_id}"
                    )

            return self

    user_input = yield CreatePopForm
    user_input_dict = user_input.model_dump()

    summary_fields = [
        "garrxdb_id",
        "netbox_id",
        "code",
        "full_name",
        "latitude",
        "longitude",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Construct Subscription model")
def construct_pop_model(
    product: UUIDstr,
    garrxdb_id: int,
    netbox_id: int,
    code: str,
    full_name: str,
    latitude: str | None,
    longitude: str | None,
) -> State:
    partner = get_partner_subscription_by_name("GARR")
    partner_id = str(partner.subscription_id)
    pop = PopInactive.from_product_id(
        product_id=product,
        customer_id=partner_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    pop.pop.code = code
    pop.pop.full_name = full_name
    pop.pop.garrxdb_id = garrxdb_id
    pop.pop.netbox_id = netbox_id
    pop.pop.latitude = latitude
    pop.pop.longitude = longitude

    pop = PopProvisioning.from_other_lifecycle(pop, SubscriptionLifecycle.PROVISIONING)
    pop.description = subscription_description(pop)

    return {
        "subscription": pop,
        "subscription_id": pop.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": pop.description,
    }


additional_steps = begin


@create_workflow(
    "create Point of Presence",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_pop() -> StepList:
    return begin >> construct_pop_model >> store_process_subscription()
