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
from orchestrator.forms.validators import DisplaySubscription
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.utils import terminate_workflow
from pydantic import Field, model_validator
from pydantic_forms.types import InputForm, State, UUIDstr
from structlog import get_logger

from products.product_types.optical_fiber import OpticalFiber
from products.services.optical_device_port import (
    factory_reset_port_configuration,
)

logger = get_logger(__name__)

achtung = (
    "Terminating an optical fiber subscription will wipe out all configuration on the termination ports and set them in admin down state. "
    "Only line ports of Open Line Systems will remain in service to prevent unintentional catastrophic failures. "
    "Please ensure you understand the consequences of this action before proceeding. "
    "If you are sure you want to proceed, please replace this warning message with 'TERMINATE'."
)
Achtung = Annotated[
    str,
    Field(
        achtung,
        title="⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️",
        json_schema_extra={
            "format": "long",
        },
    ),
]
def terminate_initial_input_form_generator(
    subscription_id: UUIDstr, customer_id: UUIDstr
) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminateOpticalFiberForm(FormPage):
        achtung: Achtung
        subscription_id: DisplaySubscription = temp_subscription_id

        @model_validator(mode="after")
        def validate_csv(self) -> "TerminateOpticalFiberForm":
            if self.achtung != "TERMINATE":
                msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
                raise ValueError(msg)
            return self

    return TerminateOpticalFiberForm


@step("Factory resetting the configuration of the termination ports")
def factory_reset_ports(subscription: OpticalFiber) -> State:
    results = {}
    port_a, port_b = subscription.optical_fiber.terminations
    results[port_a.optical_device.fqdn] = factory_reset_port_configuration(
        port_a.optical_device, port_a, port_b
    )
    results[port_b.optical_device.fqdn] = factory_reset_port_configuration(
        port_b.optical_device, port_b, port_a
    )
    return results


additional_steps = begin


@terminate_workflow(
    "terminate optical fiber",
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_optical_fiber() -> StepList:
    return begin >> factory_reset_ports
