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
from pydantic_forms.types import UUIDstr

from products.product_blocks.optical_device_port import (
    OpticalDevicePortBlock,
    OpticalDevicePortBlockInactive,
    OpticalDevicePortBlockProvisioning,
)
from products.product_blocks.transport_channel import (
    OpticalTransportChannelBlock,
    OpticalTransportChannelBlockInactive,
    OpticalTransportChannelBlockProvisioning,
)


class ClientSpeednType(StrEnum):
    Ethernet100Gbps = "100Gbps Ethernet"
    Ethernet400Gbps = "400Gbps Ethernet"


ListOfClient_ports = Annotated[list[SI], Len(min_length=2, max_length=2)]

ListOfTransport_channels = Annotated[list[SI], Len(min_length=1, max_length=2)]


class OpticalDigitalServiceBlockInactive(
    ProductBlockModel, product_block_name="OpticalDigitalService"
):
    service_name: str | None = None
    service_type: ClientSpeednType | None = None
    flow_id: int | None = None
    client_id: int | None = None
    client_ports: ListOfClient_ports[OpticalDevicePortBlockInactive]
    transport_channels: ListOfTransport_channels[OpticalTransportChannelBlockInactive]
    nms_uuid: UUIDstr | None = None


class OpticalDigitalServiceBlockProvisioning(
    OpticalDigitalServiceBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    service_name: str
    service_type: ClientSpeednType
    flow_id: int
    client_id: int
    client_ports: ListOfClient_ports[OpticalDevicePortBlockProvisioning]
    transport_channels: ListOfTransport_channels[
        OpticalTransportChannelBlockProvisioning
    ]
    nms_uuid: UUIDstr | None = None

    @computed_field
    @property
    def title(self) -> str:
        title = self.service_name
        return title


class OpticalDigitalServiceBlock(
    OpticalDigitalServiceBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    service_name: str
    service_type: ClientSpeednType
    flow_id: int
    client_id: int
    client_ports: ListOfClient_ports[OpticalDevicePortBlock]
    transport_channels: ListOfTransport_channels[OpticalTransportChannelBlock]
    nms_uuid: UUIDstr | None
