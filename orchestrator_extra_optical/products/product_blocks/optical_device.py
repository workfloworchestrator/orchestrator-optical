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

from enum import StrEnum, property
from abc import ABC, abstractmethod
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import computed_field
from pydantic_forms.types import UUIDstr

from orchestrator_extra_optical.utils.custom_types.fqdn import FQDN
from orchestrator_extra_optical.utils.custom_types.ip_address import IPAddress


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


class OpticalDeviceBlockInactive(ProductBlockModel, ABC, product_block_name="OpticalDevice"):
    fqdn: FQDN | None = None
    vendor: Vendor | None = None
    platform: Platform | None = None
    device_type: DeviceType | None = None
    lo_ip: IPAddress | None = None
    mngmt_ip: IPAddress | None = None
    nms_uuid: UUIDstr | None = None
    netbox_id: int | None = None

    @property
    @abstractmethod
    def location(self):
        msg = "Class BaseOpticalDeviceBlockInactive must be subclassed to set custom properties."
        raise NotImplementedError(msg)  # FIXME


class OpticalDeviceBlockProvisioning(
    OpticalDeviceBlockInactive, ABC, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    fqdn: FQDN
    vendor: Vendor
    platform: Platform
    device_type: DeviceType
    lo_ip: IPAddress | None = None
    mngmt_ip: IPAddress | None = None
    nms_uuid: UUIDstr | None = None
    netbox_id: int | None = None

    @property
    @abstractmethod
    def location(self):
        msg = "Class BaseOpticalDeviceBlockProvisioning must be subclassed to set custom properties."
        raise NotImplementedError(msg)  # FIXME

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.vendor} {self.platform} {self.fqdn}"


class OpticalDeviceBlock(
    OpticalDeviceBlockProvisioning, ABC, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    fqdn: FQDN
    vendor: Vendor
    platform: Platform
    device_type: DeviceType
    lo_ip: IPAddress | None = None
    mngmt_ip: IPAddress | None = None
    nms_uuid: UUIDstr | None = None
    netbox_id: int | None = None

    @property
    @abstractmethod
    def location(self):
        msg = "Class BaseOpticalDeviceBlock must be subclassed to set custom properties."
        raise NotImplementedError(msg)  # FIXME
