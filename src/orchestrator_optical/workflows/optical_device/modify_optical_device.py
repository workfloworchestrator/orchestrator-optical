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

from typing import Annotated

from orchestrator.domain import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, conditional, step
from orchestrator.workflows.steps import set_status
from orchestrator.workflows.utils import modify_workflow
from pydantic import Field
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator_optical.products.product_blocks.optical_node import DeviceType, Vendor, VendorAndPlatform
from orchestrator_optical.products.product_types.optical_node import (
    OpticalDevice,
    OpticalDeviceProvisioning,
)
from orchestrator_optical.products.product_types.pop import PoP
from orchestrator_optical.products.services.optical_node import get_nms_uuid
from orchestrator_optical.utils.custom_types.dns import FQDNPrefix
from orchestrator_optical.utils.custom_types.ip_address import IPAddress


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return (
        f"{subscription.optical_node.pqdn} "
        f"({subscription.optical_node.vendor} "
        f"{subscription.optical_node.vendor_and_platform})"
    )


logger = get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    PartnerChoice = NotImplementedError("Not implemented")  # FIXME
    PoPChoice = NotImplementedError("Not implemented")  # FIXME

    Instruction = Annotated[
        str,
        Field(
            "Select or enter only the fields you want to modify. The subscription will be updated with the new values.",
            title="ℹ️ℹ️ℹ️ Instruction ℹ️ℹ️ℹ️",
            json_schema_extra={
                "disabled": True,
            },
        ),
    ]

    subscription = OpticalDevice.from_subscription(subscription_id)

    class ModifyOpticalDeviceForm(FormPage):
        instruction: Instruction
        partner_id: PartnerChoice | None = None
        pop_id: PoPChoice | None = None
        vendor: Vendor | None = None
        platform: VendorAndPlatform | None = None
        device_type: DeviceType | None = None
        fqdn_prefix_before_pop: FQDNPrefix | None = None
        lo_ip: IPAddress | None = None
        remove_lo_ip: bool = False
        mngmt_ip: IPAddress | None = None
        remove_mngmt_ip: bool = False
        update_nms_uuid: bool = False

    user_input = yield ModifyOpticalDeviceForm
    user_input_dict = user_input.dict()

    return user_input_dict | {"subscription": subscription}


@step("Updating the subscription")
def update_subscription(
    subscription: OpticalDeviceProvisioning,
    partner_id: UUIDstr | None,
    pop_id: UUIDstr | None,
    vendor: Vendor | None,
    platform: VendorAndPlatform | None,
    device_type: DeviceType | None,
    fqdn_prefix_before_pop: FQDNPrefix | None,
    lo_ip: IPAddress | None,
    mngmt_ip: IPAddress | None,
    remove_lo_ip: bool = False,
    remove_mngmt_ip: bool = False,
    update_nms_uuid: bool = False,
) -> State:
    optical_node = subscription.optical_node

    if partner_id:
        subscription.customer_id = partner_id

    if pop_id:
        old_pop_code = optical_node.pop.code.lower()
        pop_subscription = PoP.from_subscription(pop_id)
        optical_node.pop = pop_subscription.pop
        pop_code = pop_subscription.pop.code.lower()
        optical_node.pqdn = optical_node.pqdn.replace(f"{old_pop_code}.garr.net", f"{pop_code}.garr.net")

    if fqdn_prefix_before_pop:
        pop_code = optical_node.pop.code.lower()
        optical_node.pqdn = f"{fqdn_prefix_before_pop}.{pop_code}.garr.net"

    if vendor:
        optical_node.vendor = vendor

    if platform:
        optical_node.vendor_and_platform = platform

    if device_type:
        optical_node.device_type = device_type

    if lo_ip:
        optical_node.lo_ip = lo_ip

    if mngmt_ip:
        optical_node.mngmt_ip = mngmt_ip

    if remove_lo_ip:
        optical_node.lo_ip = None

    if remove_mngmt_ip:
        optical_node.mngmt_ip = None

    return {"subscription": subscription}


@step("Updating subscription description")
def update_subscription_description(subscription: OpticalDevice) -> State:
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@step("Retrieving the UUID of this device in its Network Management System")
def find_nms_uuid(subscription: OpticalDevice) -> UUIDstr:
    nms_uuid = get_nms_uuid(subscription.optical_node)
    subscription.optical_node.nms_uuid = nms_uuid
    return {"subscription": subscription}


additional_steps = begin


@modify_workflow(
    "modify optical device",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_optical_node() -> StepList:
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> update_subscription_description
        >> conditional(lambda state: state["update_nms_uuid"])(find_nms_uuid)
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
