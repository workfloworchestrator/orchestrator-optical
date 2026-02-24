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
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription
from orchestrator.workflows.utils import create_workflow
from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator_extra_optical.products.product_blocks.optical_device import DeviceType, Platform
from orchestrator_extra_optical.products.product_blocks.optical_fiber import (
    ListOfFiberTypes,
    ListOfLengths,
)
from orchestrator_extra_optical.products.product_types.optical_device import OpticalDevice
from orchestrator_extra_optical.products.product_types.optical_fiber import (
    OpticalFiberInactive,
    OpticalFiberProvisioning,
)
from orchestrator_extra_optical.products.services.optical_device import retrieve_ports_spectral_occupations
from orchestrator_extra_optical.products.services.optical_device_port import (
    configure_termination_when_attaching_new_fiber,
)
from orchestrator_extra_optical.workflows.optical_device.shared import unused_optical_port_selector
from orchestrator_extra_optical.workflows.shared import (
    active_subscription_selector,
    create_summary_form,
    subscription_instance_values_by_block_type_depending_on_instance_id,
)


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return f"{subscription.optical_fiber.fiber_name}"


logger = get_logger(__name__)


def initial_input_form_generator(product_name: str) -> FormGenerator:
    SrcOpticalDeviceChoice = active_subscription_selector("OpticalDevice", prompt="This fiber connects this node:")  # pyright: ignore[reportInvalidTypeForm]
    DstOpticalDeviceChoice = active_subscription_selector("OpticalDevice", prompt="to this other node:")  # pyright: ignore[reportInvalidTypeForm]

    class SelectOpticalDevicesForm(FormPage):
        model_config = ConfigDict(title=product_name)

        sub_id_device_a: SrcOpticalDeviceChoice
        sub_id_device_b: DstOpticalDeviceChoice
        garrxdb_id: Annotated[int, Field(title="ID of this span in GARR-X DB if not patch-cord")] | None = None
        total_loss: Annotated[float, Field(title="Total loss of this span (dB)")] | None = None
        fiber_types: (
            Annotated[
                ListOfFiberTypes,
                Field(title=("Enter the fiber type (or types if different fibers spliced in sequence)")),
            ]
            | None
        ) = None
        lengths: (
            Annotated[
                ListOfLengths,
                Field(title=("Enter the fiber length (or lengths if different fibers spliced in sequence)")),
            ]
            | None
        ) = None

    user_input = yield SelectOpticalDevicesForm
    user_input_dict = user_input.model_dump()

    SrcOpticalPortSelector = unused_optical_port_selector(user_input_dict["sub_id_device_a"])  # pyright: ignore[reportInvalidTypeForm]
    DstOpticalPortSelector = unused_optical_port_selector(user_input_dict["sub_id_device_b"])  # pyright: ignore[reportInvalidTypeForm]

    class SelectOpticalPortsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        name_port_a: SrcOpticalPortSelector
        name_port_b: DstOpticalPortSelector

        @model_validator(mode="after")
        def validate_data(self) -> "SelectOpticalPortsForm":
            for sub_id, port_name in (
                (user_input_dict["sub_id_device_a"], self.name_port_a),
                (user_input_dict["sub_id_device_b"], self.name_port_b),
            ):
                device = OpticalDevice.from_subscription(sub_id).optical_device
                sid = device.subscription_instance_id
                device_port_sivs = subscription_instance_values_by_block_type_depending_on_instance_id(
                    product_block_type="OpticalDevicePort",
                    resource_type="port_name",
                    depending_on_instance_id=sid,
                    states=[
                        SubscriptionLifecycle.ACTIVE,
                        SubscriptionLifecycle.PROVISIONING,
                    ],
                )
                for siv in device_port_sivs:
                    if siv.value != port_name:
                        continue
                    si = siv.subscription_instance
                    instances_using_this_port = si.in_use_by
                    for instance in instances_using_this_port:
                        if instance.product_block.name == "OpticalFiber":
                            msg = (
                                f"Port {port_name} on {device.fqdn} is already"
                                " used by subscription {instance.subscription_id}."
                            )
                            raise ValueError(msg)

            return self

    user_input = yield SelectOpticalPortsForm
    user_input_dict.update(user_input.model_dump())

    summary_fields = [
        "garrxdb_id",
        "total_loss",
        "fiber_types",
        "lengths",
        "sub_id_device_a",
        "sub_id_device_b",
        "name_port_a",
        "name_port_b",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Constructing Subscription model")
def construct_optical_fiber_model(
    product: UUIDstr,
    sub_id_device_a: UUIDstr,
    name_port_a: str,
    sub_id_device_b: UUIDstr,
    name_port_b: str,
    garrxdb_id: int | None,
    total_loss: float | None,
    fiber_types: ListOfFiberTypes | None,
    lengths: ListOfLengths | None,
) -> State:
    partner_id = NotImplementedError("Not implemented")
    subscription = OpticalFiberInactive.from_product_id(
        product_id=product,
        customer_id=partner_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    src_device_subscription = OpticalDevice.from_subscription(sub_id_device_a)
    dst_device_subscription = OpticalDevice.from_subscription(sub_id_device_b)
    src_device = src_device_subscription.optical_device
    dst_device = dst_device_subscription.optical_device

    # Source Port
    subscription.optical_fiber.terminations[0].port_name = name_port_a
    subscription.optical_fiber.terminations[0].optical_device = src_device
    subscription.optical_fiber.terminations[
        0
    ].port_description = f"Physically connected to {dst_device.fqdn} {name_port_b}. "

    # Destination Port
    subscription.optical_fiber.terminations[1].port_name = name_port_b
    subscription.optical_fiber.terminations[1].optical_device = dst_device
    subscription.optical_fiber.terminations[
        1
    ].port_description = f"Physically connected to {src_device.fqdn} {name_port_a}. "

    # Fiber
    subscription.optical_fiber.fiber_name = f"{src_device.fqdn} {name_port_a} --- {dst_device.fqdn} {name_port_b}"
    subscription.optical_fiber.garrxdb_id = garrxdb_id
    subscription.optical_fiber.total_loss = total_loss
    subscription.optical_fiber.lengths = lengths
    subscription.optical_fiber.fiber_types = fiber_types

    subscription = OpticalFiberProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)
    subscription.description = subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": subscription.description,
    }


@step("Configuring fiber terminations")
def configure_fiber_terminations(
    subscription: OpticalFiberProvisioning,
) -> State:
    port_a, port_b = subscription.optical_fiber.terminations

    if port_b.optical_device.platform == Platform.FlexILS and port_a.optical_device.platform != Platform.FlexILS:
        # Swap ports to configure FlexILS first
        port_a, port_b = port_b, port_a

    key_a = f"{port_a.optical_device.fqdn} {port_a.port_name}"
    key_b = f"{port_b.optical_device.fqdn} {port_b.port_name}"

    result = {}
    result[key_a] = configure_termination_when_attaching_new_fiber(port_a.optical_device, port_a, port_b)
    result[key_b] = configure_termination_when_attaching_new_fiber(port_b.optical_device, port_b, port_a)

    return result


@step("Retrieving used passbands")
def retrieve_used_passbands(subscription: OpticalFiberProvisioning) -> State:
    for port in subscription.optical_fiber.terminations:
        device = port.optical_device
        if device.device_type in [DeviceType.ROADM, DeviceType.TransponderAndOADM]:
            ports_spectral_occupation = retrieve_ports_spectral_occupations(device)
            port.used_passbands = ports_spectral_occupation.get(port.port_name, [])

    return {"subscription": subscription}


additional_steps = begin


@create_workflow(
    "create optical fiber",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_optical_fiber() -> StepList:
    return (
        begin
        >> construct_optical_fiber_model
        >> store_process_subscription()
        >> configure_fiber_terminations
        >> retrieve_used_passbands
    )
