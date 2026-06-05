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

from orchestrator_optical.products.product_blocks.optical_node import DeviceType
from orchestrator_optical.products.product_types.optical_pipe import (
    OpticalFiberPatch,
    OpticalFiberSpan,
    OpticalLeasedSpectrum,
)
from orchestrator_optical.products.services.optical_node import retrieve_ports_spectral_occupations
from orchestrator_optical.products.services.optical_port import check_fiber_terminating_port

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_optical_fiber(subscription: OpticalFiber) -> State:
    return {
        "subscription": subscription,
    }


@step("Checking fiber terminations")
def configure_fiber_terminations(
    subscription: OpticalFiber,
) -> State:
    port_a, port_b = subscription.optical_fiber.terminations

    check_fiber_terminating_port(port_a.optical_node, port_a, port_b)
    check_fiber_terminating_port(port_b.optical_node, port_b, port_a)

    return {}


@step("Updating used passbands")
def retrieve_used_passbands(
    subscription: OpticalFiberSpan | OpticalLeasedSpectrum | OpticalFiberPatch,
) -> State:
    match subscription:
        case OpticalFiberSpan():
            terminations = subscription.fiber.terminations
        case OpticalLeasedSpectrum():
            terminations = subscription.leased_spectrum.terminations
        case OpticalFiberPatch():
            return {"subscription": subscription}
        case _:
            msg = f"Unsupported subscription type: {type(subscription)}"
            raise TypeError(msg)

    for port in terminations:
        device = port.optical_node
        if device.device_type in [DeviceType.ROADM, DeviceType.TransponderAndOADM]:
            ports_spectral_occupation = retrieve_ports_spectral_occupations(device)
            port.used_passbands = ports_spectral_occupation.get(port.port_name, [])

    return {"subscription": subscription}


@validate_workflow("validate optical fiber")
def validate_optical_fiber() -> StepList:
    return begin >> load_initial_state_optical_fiber >> retrieve_used_passbands
