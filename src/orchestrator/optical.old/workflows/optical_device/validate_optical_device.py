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

from products.product_types.optical_device import OpticalDevice
from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from workflows.optical_device.create_optical_device import subscription_description

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_optical_device(subscription: OpticalDevice) -> State:
    return {
        "subscription": subscription,
    }


@step("Update subscription description")
def update_subscription_description(subscription: OpticalDevice) -> State:
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
    }


@validate_workflow()
def validate_optical_device() -> StepList:
    return begin >> load_initial_state_optical_device >> update_subscription_description
