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

from products.product_blocks.optical_device_port import (
    OpticalDevicePortBlock,
    OpticalDevicePortBlockInactive,
    OpticalDevicePortBlockProvisioning,
)

AddDropPorts = Annotated[list[SI], Len(min_length=2, max_length=2)]

RouteAsListOfPorts = Annotated[list[SI], Len(min_length=0, max_length=64)]


class OpticalSpectrumSectionBlockInactive(
    ProductBlockModel, product_block_name="OpticalSpectrumSection"
):
    add_drop_ports: AddDropPorts[OpticalDevicePortBlockInactive]
    optical_path: RouteAsListOfPorts[OpticalDevicePortBlockInactive]


class OpticalSpectrumSectionBlockProvisioning(
    OpticalSpectrumSectionBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    add_drop_ports: AddDropPorts[OpticalDevicePortBlockProvisioning]
    optical_path: RouteAsListOfPorts[OpticalDevicePortBlockProvisioning]


class OpticalSpectrumSectionBlock(
    OpticalSpectrumSectionBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    add_drop_ports: AddDropPorts[OpticalDevicePortBlock]
    optical_path: RouteAsListOfPorts[OpticalDevicePortBlock]
