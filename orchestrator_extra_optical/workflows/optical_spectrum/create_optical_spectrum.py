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
from orchestrator.forms.validators import Divider
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import (
    StepList,
    begin,
    step,
)
from orchestrator.workflows.steps import set_status, store_process_subscription
from orchestrator.workflows.utils import create_workflow
from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType
from products.product_blocks.optical_fiber import (
    OpticalDevicePortBlockInactive,
)
from products.product_types.optical_device import OpticalDevice
from products.product_types.optical_fiber import OpticalFiber
from products.product_types.optical_spectrum import (
    OpticalSpectrumInactive,
    OpticalSpectrumProvisioning,
)
from products.services.optical_device_port import (
    set_port_description,
)
from products.services.optical_spectrum import (
    deploy_optical_circuit,
)
from utils.custom_types.frequencies import Frequency, Passband
from workflows.optical_device.shared import (
    multiple_optical_device_selector,
    optical_client_port_selector,
    optical_device_selector_of_types,
)
from workflows.optical_fiber.shared import multiple_optical_fiber_selector
from workflows.optical_spectrum.shared import (
    NoOpticalPathFoundError,
    optical_spectrum_path_selector,
    store_list_of_ports_into_spectrum_sections,
    update_used_passbands,
)
from workflows.shared import (
    active_subscription_selector,
    create_summary_form,
)

logger = get_logger(__name__)


def subscription_description(
    subscription: SubscriptionModel,
) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    spectrum = subscription.optical_spectrum
    return f"{spectrum.spectrum_name}"


def initial_input_form_generator(product_name: str) -> FormGenerator:
    PartnerChoice = NotImplementedError("Not implemented")  # FIXME

    class OpticalSpectrumInputForm(FormPage):
        """Form for inputing service name and min and max frequencies."""

        model_config = ConfigDict(title=product_name)

        optical_spectrum_name: str
        partner_id: PartnerChoice
        frequency_min: Annotated[Frequency, Field(Title="Start frequency (THz)", multiple_of=12500)]
        frequency_max: Annotated[Frequency, Field(Title="End frequency (THz)", multiple_of=12500)]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "OpticalSpectrumInputForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            return self

    user_input = yield OpticalSpectrumInputForm
    user_input_dict = user_input.dict()

    transceivers_types = [
        DeviceType.ROADM,
        DeviceType.TransponderAndOADM,
    ]
    NodeAChoice = optical_device_selector_of_types(
        device_types=transceivers_types,
        prompt="This service connects this node: ",
    )

    NodeBChoice = optical_device_selector_of_types(
        device_types=transceivers_types,
        prompt="...to this other node: ",
    )

    class OpticalSpectrumSrcDstForm(FormPage):
        """Form for selecting source and destination optical devices."""

        model_config = ConfigDict(title=product_name)

        src_optical_device_id: NodeAChoice
        dst_optical_device_id: NodeBChoice

        @model_validator(mode="after")
        def validate_separate_nodes(self) -> "OpticalSpectrumSrcDstForm":
            if self.dst_optical_device_id == self.src_optical_device_id:
                msg = "Destination Optical Device cannot be the same as Source Optical Device"
                raise ValueError(msg)
            return self

    user_input = yield OpticalSpectrumSrcDstForm
    user_input_dict.update(user_input.dict())

    sub_node_a = OpticalDevice.from_subscription(user_input_dict["src_optical_device_id"])
    optical_device_a = sub_node_a.optical_device
    sub_node_b = OpticalDevice.from_subscription(user_input_dict["dst_optical_device_id"])
    optical_device_b = sub_node_b.optical_device

    SrcOpticalDevicePortSelector = optical_client_port_selector(
        user_input_dict["src_optical_device_id"],
        prompt=f"Select the Add/Drop Port on {optical_device_a.fqdn}. Please be careful to select the correct port.",
    )
    DstOpticalDevicePortSelector = optical_client_port_selector(
        user_input_dict["dst_optical_device_id"],
        prompt=f"Select the Add/Drop Port on {optical_device_b.fqdn}. Please be careful to select the correct port.",
    )

    class OpticalSpectrumAddDropForm(FormPage):
        """Form for selecting source and destination add/drop ports."""

        model_config = ConfigDict(title=product_name)

        src_optical_device_port_name: SrcOpticalDevicePortSelector
        dst_optical_device_port_name: DstOpticalDevicePortSelector

    user_input = yield OpticalSpectrumAddDropForm
    user_input_dict.update(user_input.dict())

    line_system_types = [
        DeviceType.ROADM,
        DeviceType.TransponderAndOADM,
        DeviceType.Amplifier,
    ]

    ExcludeOpticalDeviceChoiceList = multiple_optical_device_selector(
        device_types=line_system_types,
        prompt="Do *not* pass through these Optical Devices",
    )

    ExcludeSpanChoiceList = multiple_optical_fiber_selector(
        prompt="Do *not* pass through these Optical Fibers",
    )

    class OpticalSpectrumConstraintsForm(FormPage):
        """Form for specifying which optical device MUST or MUST NOT be traversed by the optical spectrum."""

        model_config = ConfigDict(title=product_name)

        exclude_devices_list: ExcludeOpticalDeviceChoiceList
        divider1: Divider
        exclude_fibers_list: ExcludeSpanChoiceList

    user_input = yield OpticalSpectrumConstraintsForm
    user_input_dict.update(user_input.dict())

    passband = (user_input_dict["frequency_min"], user_input_dict["frequency_max"])

    no_path_found_msg = (
        "No optical path found, please adjust the routing constraints"
        " in the previous step or validate fibers in the path."
    )
    try:
        PathChoice = optical_spectrum_path_selector(
            optical_device_a.subscription_instance_id,
            optical_device_b.subscription_instance_id,
            passband,
            user_input_dict["exclude_devices_list"],
            user_input_dict["exclude_fibers_list"],
            prompt=(
                "Select the optical path, if you don't see the desired path,"
                " adjust constraints in previous step or validate fibers along the path."
            ),
        )
    except NoOpticalPathFoundError:
        logger.exception(
            "No optical path found",
            line_ports_a=user_input_dict["line_ports_a"],
            line_ports_b=user_input_dict["line_ports_b"],
            passband=passband,
            exclude_devices_list=user_input_dict["exclude_devices_list"],
            exclude_fibers_list=user_input_dict["exclude_fibers_list"],
        )

        PathChoice = Choice(
            no_path_found_msg,
            [
                (no_path_found_msg, no_path_found_msg),
            ],
        )

    class OdsForm3(FormPage):
        class Config:
            title = "Optical Path"

        optical_path: PathChoice

        @model_validator(mode="after")
        def validate_data(self) -> "OdsForm3":
            if self.optical_path == no_path_found_msg:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            return self

    user_input = yield OdsForm3
    user_input_dict.update(user_input.dict())

    user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")

    summary_fields = [
        "partner_id",
        "optical_spectrum_name",
        "frequency_min",
        "frequency_max",
        "src_optical_device_id",
        "dst_optical_device_id",
        "src_optical_device_port_name",
        "dst_optical_device_port_name",
        "optical_path",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Saving input data into the optical spectrum model")
def create_optical_spectrum_model(
    product: UUIDstr,
    partner_id: UUIDstr,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
    exclude_devices_list: list[UUIDstr],
    exclude_fibers_list: list[UUIDstr],
) -> State:
    # create subscription instance
    subscription = OpticalSpectrumInactive.from_product_id(
        product_id=product,
        customer_id=partner_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    # set attributes: name
    subscription.optical_spectrum.spectrum_name = optical_spectrum_name

    # set attributes: passband
    passband: Passband = (frequency_min, frequency_max)
    subscription.optical_spectrum.passband = passband

    # set attributes: optical_spectrum_constraints
    constraints = subscription.optical_spectrum.optical_spectrum_path_constraints
    for sub_id in exclude_devices_list:
        sub = OpticalDevice.from_subscription(sub_id)
        constraints.exclude_nodes.append(sub.optical_device)
    for sub_id in exclude_fibers_list:
        sub = OpticalFiber.from_subscription(sub_id)
        constraints.exclude_spans.append(sub.optical_fiber)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
    }


@step("Dividing the optical path into single-device-family sections")
def divide_path_into_sections(
    subscription: OpticalSpectrumInactive,
    optical_path: list[UUIDstr],
    src_optical_device_port_name: str,
    dst_optical_device_port_name: str,
    src_optical_device_id: UUIDstr,
    dst_optical_device_id: UUIDstr,
) -> State:
    src_device_subscription = OpticalDevice.from_subscription(src_optical_device_id)
    dst_device_subscription = OpticalDevice.from_subscription(dst_optical_device_id)
    src_device = src_device_subscription.optical_device
    dst_device = dst_device_subscription.optical_device

    # Source Add/Drop Port
    src_port = OpticalDevicePortBlockInactive.new(
        subscription_id=subscription.subscription_id,
        port_name=src_optical_device_port_name,
        optical_device=src_device,
        port_description=(
            f"Remotely connected to {dst_device.fqdn} {dst_optical_device_port_name} "
            f"via {subscription.optical_spectrum.spectrum_name}. "
        ),
    )
    src_port.save(subscription_id=subscription.subscription_id, status=SubscriptionLifecycle.INITIAL)
    # Destination Add/Drop Port
    dst_port = OpticalDevicePortBlockInactive.new(
        subscription_id=subscription.subscription_id,
        port_name=dst_optical_device_port_name,
        optical_device=dst_device,
        port_description=(
            f"Remotely connected to {src_device.fqdn} {src_optical_device_port_name} "
            f"via {subscription.optical_spectrum.spectrum_name}. "
        ),
    )
    dst_port.save(subscription_id=subscription.subscription_id, status=SubscriptionLifecycle.INITIAL)

    optical_path.insert(0, src_port.subscription_instance_id)
    optical_path.append(dst_port.subscription_instance_id)

    store_list_of_ports_into_spectrum_sections(optical_path, subscription.optical_spectrum)

    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalSpectrumProvisioning,
) -> State:
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
        "subscription": subscription,
    }


@step("Adding a description to the add/drop ports")
def configure_add_drop_ports_description(
    subscription: OpticalSpectrumProvisioning,
) -> State:
    oss = subscription.optical_spectrum.optical_spectrum_sections
    src_port = oss[0].add_drop_ports[0]
    dst_port = oss[-1].add_drop_ports[-1]

    outputs = []
    for port in (src_port, dst_port):
        command_output = set_port_description(port.optical_device, port.port_name, port.port_description)
        outputs.append(command_output)

    return {"configuration_results": outputs, "subscription": subscription}


@step("Provisioning optical spectrum sections")
def provision_optical_sections(subscription: OpticalSpectrumProvisioning) -> State:
    passband = subscription.optical_spectrum.passband
    spectrum_name = subscription.optical_spectrum.spectrum_name
    carrier = (int(0.5 * (passband[0] + passband[1])), passband[1] - passband[0])
    results = {}
    for section in subscription.optical_spectrum.optical_spectrum_sections:
        src_device = section.add_drop_ports[0].optical_device
        results[src_device.platform] = deploy_optical_circuit(
            src_device,
            section,
            spectrum_name,
            passband,
            carrier,
            label="SpectrumService",
        )

    return {
        "configuration_results": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands_step(subscription: OpticalSpectrumProvisioning) -> State:
    spectrum = subscription.optical_spectrum
    update_used_passbands(spectrum)

    return {"subscription": subscription}


additional_steps = begin


@create_workflow(
    "create optical spectrum service",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_optical_spectrum() -> StepList:
    return (
        begin
        >> create_optical_spectrum_model
        >> store_process_subscription()
        >> divide_path_into_sections
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription_description
        >> configure_add_drop_ports_description
        >> provision_optical_sections
        >> update_used_passbands_step
    )
