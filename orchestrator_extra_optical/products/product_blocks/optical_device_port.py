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
from orchestrator.types import SubscriptionLifecycle
from pydantic import computed_field

from products.product_blocks.optical_device import (
    OpticalDeviceBlock,
    OpticalDeviceBlockInactive,
    OpticalDeviceBlockProvisioning,
)
from utils.custom_types.frequencies import Passband

ListOfPassbands = Annotated[list[Passband], Len(min_length=0, max_length=128)]


class OpticalDevicePortBlockInactive(
    ProductBlockModel, product_block_name="OpticalDevicePort"
):
    port_name: str | None = None
    port_description: str | None = None
    optical_device: OpticalDeviceBlockInactive | None = None
    netbox_id: int | None = None
    used_passbands: ListOfPassbands | None = None


class OpticalDevicePortBlockProvisioning(
    OpticalDevicePortBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    port_name: str
    port_description: str | None = None
    optical_device: OpticalDeviceBlockProvisioning
    netbox_id: int | None = None
    used_passbands: ListOfPassbands | None = None

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.optical_device.fqdn} {self.port_name}"


class OpticalDevicePortBlock(
    OpticalDevicePortBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    port_name: str
    port_description: str
    optical_device: OpticalDeviceBlock
    netbox_id: int | None = None
    used_passbands: ListOfPassbands | None = None
