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

from enum import StrEnum
from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import computed_field

from products.product_blocks.optical_device_port import (
    OpticalDevicePortBlock,
    OpticalDevicePortBlockInactive,
    OpticalDevicePortBlockProvisioning,
)


class FiberType(StrEnum):
    G651_1 = "G.651.1"
    G652_A = "G.652.A"
    G652_B = "G.652.B"
    G652_C = "G.652.C"
    G652_D = "G.652.D"
    G653_A = "G.653.A"
    G653_B = "G.653.B"
    G654_A = "G.654.A"
    G654_B = "G.654.B"
    G654_C = "G.654.C"
    G654_D = "G.654.D"
    G654_E = "G.654.E"
    G655_A = "G.655.A"
    G655_B = "G.655.B"
    G655_C = "G.655.C"
    G655_D = "G.655.D"
    G655_E = "G.655.E"
    G656   = "G.656"
    G657_A = "G.657.A"
    G657_B = "G.657.B"

ListOfPorts = Annotated[list[SI], Len(min_length=2, max_length=2)]
ListOfLengths = Annotated[list[int], Len(min_length=0, max_length=5)]
ListOfFiberTypes = Annotated[list[FiberType], Len(min_length=0, max_length=5)]

class OpticalFiberBlockInactive(ProductBlockModel, product_block_name="OpticalFiber"):
    terminations: ListOfPorts[OpticalDevicePortBlockInactive]
    fiber_name: str | None = None
    garrxdb_id: int | None = None
    total_loss: float | None = None
    lengths: ListOfLengths | None = None
    fiber_types: ListOfFiberTypes | None = None


class OpticalFiberBlockProvisioning(
    OpticalFiberBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    terminations: ListOfPorts[OpticalDevicePortBlockProvisioning]
    fiber_name: str | None = None
    garrxdb_id: int | None = None
    total_loss: float | None = None
    lengths: ListOfLengths | None = None
    fiber_types: ListOfFiberTypes | None = None


class OpticalFiberBlock(
    OpticalFiberBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    terminations: ListOfPorts[OpticalDevicePortBlock]
    fiber_name: str
    garrxdb_id: int | None = None
    total_loss: float | None = None
    lengths: ListOfLengths | None = None
    fiber_types: ListOfFiberTypes | None = None

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.fiber_name}"
