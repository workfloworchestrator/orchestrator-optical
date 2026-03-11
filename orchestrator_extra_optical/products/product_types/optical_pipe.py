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
from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic_forms.types import strEnum

from orchestrator_extra_optical.products.product_blocks.optical_pipe import (
    OpticalPipeBlock,
    OpticalPipeBlockInactive,
    OpticalPipeBlockProvisioning,
)


class OpticalPipeType(strEnum):
    DARK_FIBER = "Dark Fiber"
    LEASED_DARK_SPECTRUM = "Leased Dark Spectrum"


class OpticalPipeInactive(SubscriptionModel, is_base=True):
    optical_fiber: OpticalPipeBlockInactive
    optical_pipe_type: OpticalPipeType


class OpticalPipeProvisioning(
    OpticalPipeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    optical_fiber: OpticalPipeBlockProvisioning
    optical_pipe_type: OpticalPipeType


class OpticalPipe(OpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    optical_fiber: OpticalPipeBlock
    optical_pipe_type: OpticalPipeType
