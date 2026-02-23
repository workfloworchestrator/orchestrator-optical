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

from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.utils import validate_workflow
from pydantic_forms.types import State
from structlog import get_logger

from products.product_types.optical_spectrum import OpticalSpectrum
from products.services.optical_spectrum import validate_optical_circuit
from workflows.optical_spectrum.create_optical_spectrum import (
    subscription_description,
)

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_optical_spectrum(subscription: OpticalSpectrum) -> State:
    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalSpectrum,
) -> State:
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
    }


@step("Verifying optical spectrum sections")
def verify_optical_transport_channels(subscription: OpticalSpectrum) -> State:
    spectrum = subscription.optical_spectrum
    spectrum_name = spectrum.spectrum_name
    passband = spectrum.passband
    central_frequency = (passband[0] + passband[1]) / 2
    bandwidth = passband[1] - passband[0]
    carrier = (
        central_frequency,
        bandwidth,
    )
    for section in spectrum.optical_spectrum_sections:
        src_device = section.add_drop_ports[0].optical_device
        validate_optical_circuit(
            src_device,
            section,
            spectrum_name,
            passband,
            carrier,
            label="SpectrumService",
        )

    return


@validate_workflow("validate optical spectrum service")
def validate_optical_spectrum() -> StepList:
    return (
        begin
        >> load_initial_state_optical_spectrum
        >> update_subscription_description
        >> verify_optical_transport_channels
    )
