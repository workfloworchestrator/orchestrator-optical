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

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field, computed_field

from orchestrator_extra_optical.products.product_blocks.optical_dark_spectrum import (
    DarkSpectrumBlock,
    DarkSpectrumBlockInactive,
    DarkSpectrumBlockProvisioning,
)
from orchestrator_extra_optical.products.product_blocks.optical_port import (
    OpticalDevicePortBlock,
    OpticalDevicePortBlockInactive,
    OpticalDevicePortBlockProvisioning,
)

LinePortList = Annotated[list[SI], Len(min_length=2, max_length=2)]


class OpticalTransportChannelBlockInactive(ProductBlockModel, product_block_name="OpticalTransportChannel"):
    transport_channel_id: int | None = None
    central_frequency: int | None = None
    mode: str | None = None
    line_ports: LinePortList[OpticalDevicePortBlockInactive] = Field(default_factory=list)
    optical_spectrum: DarkSpectrumBlockInactive


class OpticalTransportChannelBlockProvisioning(
    OpticalTransportChannelBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    transport_channel_id: int
    central_frequency: int
    mode: str
    line_ports: LinePortList[OpticalDevicePortBlockProvisioning]
    optical_spectrum: DarkSpectrumBlockProvisioning

    @computed_field
    @property
    def title(self) -> str:
        first_code = self.line_ports[0].optical_device.location.code.lower()
        second_code = self.line_ports[1].optical_device.location.code.lower()
        return f"och{self.transport_channel_id}_{first_code}-{second_code}"


class OpticalTransportChannelBlock(OpticalTransportChannelBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    transport_channel_id: int
    central_frequency: int
    mode: str
    line_ports: LinePortList[OpticalDevicePortBlock]
    optical_spectrum: DarkSpectrumBlock
