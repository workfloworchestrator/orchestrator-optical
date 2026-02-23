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

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import computed_field
from pydantic_forms.types import UUIDstr

from products.product_blocks.pop import PoPBlock, PoPBlockInactive, PoPBlockProvisioning
from utils.custom_types.fqdn import FQDN
from utils.custom_types.ip_address import IPAddress


class Vendor(StrEnum):
    Infinera = "Infinera"


class Platform(StrEnum):
    FlexILS = "FlexILS"
    Groove_G30 = "Groove G30"
    GX_G42 = "GX G42"


class DeviceType(StrEnum):
    ROADM = "ROADM"
    Amplifier = "Amplifier"
    Transponder = "Transponder"
    Transceiver = "Transceiver"
    TransponderAndOADM = "Transponder+OADM"


class OpticalDeviceBlockInactive(ProductBlockModel, product_block_name="OpticalDevice"):
    fqdn: FQDN | None = None
    pop: PoPBlockInactive | None = None
    vendor: Vendor | None = None
    platform: Platform | None = None
    device_type: DeviceType | None = None
    lo_ip: IPAddress | None = None
    mngmt_ip: IPAddress | None = None
    nms_uuid: UUIDstr | None = None
    netbox_id: int | None = None


class OpticalDeviceBlockProvisioning(
    OpticalDeviceBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    fqdn: FQDN
    pop: PoPBlockProvisioning
    vendor: Vendor
    platform: Platform
    device_type: DeviceType
    lo_ip: IPAddress | None = None
    mngmt_ip: IPAddress | None = None
    nms_uuid: UUIDstr | None = None
    netbox_id: int | None = None

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.vendor} {self.platform} {self.fqdn}"


class OpticalDeviceBlock(
    OpticalDeviceBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    fqdn: FQDN
    pop: PoPBlock
    vendor: Vendor
    platform: Platform
    device_type: DeviceType
    lo_ip: IPAddress | None = None
    mngmt_ip: IPAddress | None = None
    nms_uuid: UUIDstr | None = None
    netbox_id: int | None = None
