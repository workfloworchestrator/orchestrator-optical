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

from orchestrator.forms import FormPage
from orchestrator.forms.validators import Divider
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import set_status
from orchestrator.workflows.utils import modify_workflow
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType
from products.product_types.optical_device import OpticalDevice
from products.product_types.optical_fiber import OpticalFiber
from products.product_types.optical_spectrum import (
    OpticalSpectrum,
    OpticalSpectrumProvisioning,
)
from products.services.optical_spectrum import (
    modify_optical_circuit,
)
from utils.custom_types.frequencies import Frequency, Passband
from workflows.optical_device.shared import (
    multiple_optical_device_selector,
)
from workflows.optical_fiber.shared import multiple_optical_fiber_selector
from workflows.optical_spectrum.create_optical_spectrum import subscription_description, update_used_passbands_step
from workflows.optical_spectrum.shared import (
    NoOpticalPathFoundError,
    optical_spectrum_path_selector,
    store_list_of_ports_into_spectrum_sections,
)
from workflows.shared import modify_summary_form

logger = get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = OpticalSpectrum.from_subscription(subscription_id)
    optical_spectrum = subscription.optical_spectrum
    old_passband = optical_spectrum.passband
    old_spectrum_name = optical_spectrum.spectrum_name

    optical_device_a = optical_spectrum.optical_spectrum_sections[0].add_drop_ports[0].optical_device
    optical_device_b = optical_spectrum.optical_spectrum_sections[-1].add_drop_ports[-1].optical_device

    class ModifyOpticalSpectrumForm(FormPage):
        optical_spectrum_name: str = old_spectrum_name
        frequency_min: Annotated[Frequency, Field(Title="Start frequency (THz)", multiple_of=12500)] = old_passband[0]
        frequency_max: Annotated[Frequency, Field(Title="End frequency (THz)", multiple_of=12500)] = old_passband[1]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "ModifyOpticalSpectrumForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            return self

    user_input = yield ModifyOpticalSpectrumForm
    user_input_dict = user_input.dict()

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
            optical_device_a=optical_device_a.subscription_instance_id,
            optical_device_b=optical_device_b.subscription_instance_id,
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

    return user_input_dict | {"subscription": subscription}


@step("Update subscription")
def update_subscription(
    subscription: OpticalSpectrumProvisioning,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
    exclude_devices_list: list[UUIDstr],
    exclude_fibers_list: list[UUIDstr],
) -> State:
    old_passband = subscription.optical_spectrum.passband
    old_spectrum_name = subscription.optical_spectrum.spectrum_name

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
        "old_passband": old_passband,
        "old_spectrum_name": old_spectrum_name,
    }


@step("Update subscription description")
def update_subscription_description(subscription: OpticalSpectrum) -> State:
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@step("Dividing the optical path into single-device-family sections")
def divide_path_into_sections(
    subscription: OpticalSpectrumProvisioning,
    optical_path: list[UUIDstr],
) -> State:
    src_port = subscription.optical_spectrum.optical_spectrum_sections[0].add_drop_ports[0]
    dst_port = subscription.optical_spectrum.optical_spectrum_sections[-1].add_drop_ports[-1]

    optical_path.insert(0, src_port.subscription_instance_id)
    optical_path.append(dst_port.subscription_instance_id)

    store_list_of_ports_into_spectrum_sections(optical_path, subscription.optical_spectrum)

    return {
        "subscription": subscription,
    }


@step("Modifying optical spectrum sections")
def modify_optical_sections(
    subscription: OpticalSpectrumProvisioning,
    old_passband: Passband,
    old_spectrum_name: str,
) -> State:
    optical_spectrum = subscription.optical_spectrum
    passband = optical_spectrum.passband
    spectrum_name = optical_spectrum.spectrum_name
    carrier_width = passband[1] - passband[0]
    central_frequency = (passband[0] + passband[1]) / 2
    carrier = (central_frequency, carrier_width)

    results = {}
    for section in optical_spectrum.optical_spectrum_sections:
        src_device = section.add_drop_ports[0].optical_device
        key = f"{src_device.platform}"
        results[key] = modify_optical_circuit(
            src_device,
            section,
            optical_spectrum_name=spectrum_name,
            passband=passband,
            carrier=carrier,
            label="SpectrumService",
            old_passband=old_passband,
            old_spectrum_name=old_spectrum_name,
        )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


additional_steps = begin


@modify_workflow(
    "modify optical spectrum service",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_optical_spectrum() -> StepList:
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> update_subscription_description
        >> divide_path_into_sections
        >> modify_optical_sections
        >> update_used_passbands_step
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
