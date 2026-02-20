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

from products.product_blocks.optical_device import DeviceType
from products.product_types.optical_fiber import OpticalFiber
from products.services.optical_device import retrieve_ports_spectral_occupations
from products.services.optical_device_port import check_fiber_terminating_port

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

    check_fiber_terminating_port(
        port_a.optical_device, port_a, port_b
    )
    check_fiber_terminating_port(
        port_b.optical_device, port_b, port_a
    )

    return {}

@step("Updating used passbands")
def retrieve_used_passbands(subscription: OpticalFiber) -> State:
    for port in subscription.optical_fiber.terminations:
        device = port.optical_device
        if device.device_type in [DeviceType.ROADM, DeviceType.TransponderAndOADM]:
            ports_spectral_occupation = retrieve_ports_spectral_occupations(device)
            port.used_passbands = ports_spectral_occupation.get(port.port_name, [])

    return {"subscription": subscription}


@validate_workflow("validate optical fiber")
def validate_optical_fiber() -> StepList:
    return begin >> load_initial_state_optical_fiber >> retrieve_used_passbands
