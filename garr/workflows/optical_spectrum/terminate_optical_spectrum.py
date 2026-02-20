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

from products.product_types.optical_spectrum import OpticalSpectrum
from products.services.optical_spectrum import delete_optical_circuit
from workflows.optical_spectrum.shared import (
    update_used_passbands,
)

logger = get_logger(__name__)


def terminate_initial_input_form_generator(subscription_id: UUIDstr, customer_id: UUIDstr) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminateOpticalSpectrumForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore

    return TerminateOpticalSpectrumForm


@step("Deleting optical sections")
def delete_optical_sections(subscription: OpticalSpectrum) -> State:
    results = {}
    passband = subscription.optical_spectrum.passband
    spectrum_name = subscription.optical_spectrum.spectrum_name
    for section in subscription.optical_spectrum.optical_spectrum_sections:
        src_device = section.add_drop_ports[0].optical_device
        key = f"{src_device.platform}"
        results[key] = delete_optical_circuit(
            src_device,
            section,
            spectrum_name,
            passband,
        )

    return {
        "configuration_results": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands_step(subscription: OpticalSpectrum) -> State:
    spectrum = subscription.optical_spectrum
    update_used_passbands(spectrum)

    return {"subscription": subscription}


additional_steps = begin


@terminate_workflow(
    "terminate optical spectrum service",
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_optical_spectrum() -> StepList:
    return (
        begin >> delete_optical_sections >> update_used_passbands_step
        # TODO: fill in additional steps if needed
    )
