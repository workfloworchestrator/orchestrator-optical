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

from typing import TypeAlias, cast

from orchestrator.domain import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.targets import Target
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription
from orchestrator.workflows.utils import create_workflow
from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType, Platform, Vendor
from products.product_types.optical_device import (
    OpticalDeviceInactive,
    OpticalDeviceProvisioning,
)
from products.product_types.pop import PoP
from products.services.optical_device import get_nms_uuid
from utils.custom_types.fqdn import FQDN, FQDNPrefix
from utils.custom_types.ip_address import IPAddress
from workflows.shared import (
    active_subscription_selector,
    create_summary_form,
    subscriptions_by_product_type_and_instance_value,
)

logger = get_logger(__name__)


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return (
        f"{subscription.optical_device.fqdn} "
        f"({subscription.optical_device.vendor} "
        f"{subscription.optical_device.platform})"
    )


def initial_input_form_generator(product_name: str) -> FormGenerator:
    PartnerChoice = NotImplementedError("Not implemented")  # FIXME
    PoPChoice = NotImplementedError("Not implemented")  # FIXME

    class CreateOpticalDeviceForm(FormPage):
        model_config = ConfigDict(title=product_name)
        partner_id: PartnerChoice
        pop_id: PoPChoice
        vendor: Vendor
        platform: Platform
        device_type: DeviceType
        fqdn_prefix_before_pop: FQDNPrefix = "flex"
        lo_ip: IPAddress | None = None
        mngmt_ip: IPAddress | None = None

        @model_validator(mode="after")
        def validate_data(self) -> "CreateOpticalDeviceForm":
            pop_subscription = PoP.from_subscription(self.pop_id)
            pop_code = pop_subscription.pop.code.lower()
            fqdn = f"{self.fqdn_prefix_before_pop}.{pop_code}.garr.net"

            for resource, value in [
                ("fqdn", fqdn),
                ("lo_ip", self.lo_ip),
                ("mngmt_ip", self.mngmt_ip),
                ("lo_ip", self.mngmt_ip),
                ("mngmt_ip", self.lo_ip),
            ]:
                subs = subscriptions_by_product_type_and_instance_value(
                    product_type="OpticalDevice",
                    resource_type=resource,
                    value=str(value),
                    status=[
                        SubscriptionLifecycle.INITIAL,
                        SubscriptionLifecycle.PROVISIONING,
                        SubscriptionLifecycle.ACTIVE,
                    ],
                )
                if subs:
                    msg = f"{resource} {value} already in use by subscription {subs[0].subscription_id}"
                    raise ValueError(msg)

            return self

    user_input = yield CreateOpticalDeviceForm
    user_input_dict = user_input.model_dump()
    summary_fields = [
        "partner_id",
        "pop_id",
        "vendor",
        "platform",
        "device_type",
        "fqdn_prefix_before_pop",
        "lo_ip",
        "mngmt_ip",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Construct Subscription model")
def construct_optical_device_model(
    product: UUIDstr,
    partner_id: UUIDstr,
    pop_id: UUIDstr,
    vendor: Vendor,
    platform: Platform,
    device_type: DeviceType,
    fqdn_prefix_before_pop: FQDN,
    lo_ip: IPAddress | None,
    mngmt_ip: IPAddress | None,
    nms_uuid: UUIDstr | None = None,
    netbox_id: int | None = None,
) -> State:
    subscription = OpticalDeviceInactive.from_product_id(
        product_id=product,
        customer_id=partner_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    pop_subscription = PoP.from_subscription(pop_id)
    subscription.optical_device.pop = pop_subscription.pop

    pop_code = pop_subscription.pop.code.lower()
    subscription.optical_device.fqdn = f"{fqdn_prefix_before_pop}.{pop_code}.garr.net"

    subscription.optical_device.vendor = vendor
    subscription.optical_device.platform = platform
    subscription.optical_device.device_type = device_type
    subscription.optical_device.lo_ip = lo_ip
    subscription.optical_device.mngmt_ip = mngmt_ip
    subscription.optical_device.nms_uuid = nms_uuid
    subscription.optical_device.netbox_id = netbox_id  # TODO: add actual call to NetBox

    subscription = OpticalDeviceProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)
    subscription.description = subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


@step("Retrieving the UUID of this device in its Network Management System")
def find_nms_uuid(subscription: OpticalDeviceProvisioning) -> UUIDstr:
    nms_uuid = get_nms_uuid(subscription.optical_device)
    subscription.optical_device.nms_uuid = nms_uuid
    return {"subscription": subscription}


additional_steps = begin


@create_workflow(
    "create optical device",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_optical_device() -> StepList:
    return (
        begin
        >> construct_optical_device_model
        >> store_process_subscription()
        >> find_nms_uuid
    )
