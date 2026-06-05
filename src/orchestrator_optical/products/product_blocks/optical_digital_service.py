"""Module for Optical Digital Service product blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import (
    OpticalTransponderClientPortBlock,
    OpticalTransponderClientPortBlockInactive,
    OpticalTransponderClientPortBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlock,
    OpticalTransportChannelBlockInactive,
    OpticalTransportChannelBlockProvisioning,
)

OpticalClientPortList = Annotated[list[SI], Len(min_length=2, max_length=2)]

TransportChannelList = Annotated[
    list[SI], Len(min_length=1, max_length=2)
]  # if 2 then reverse multiplexing: 2 transport channels for one client service


# --- Discriminated Union Types for Client Ports ---

ClientsInactive = Annotated[
    OpticalTransponderClientPortBlockInactive | OpticalCoherentPluggableBlockInactive, Field(discriminator="role")
]

ClientsProvisioning = Annotated[
    OpticalTransponderClientPortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="role"),
]

Clients = Annotated[OpticalTransponderClientPortBlock | OpticalCoherentPluggableBlock, Field(discriminator="role")]


class OpticalDigitalServiceBlockInactive(ProductBlockModel, product_block_name="OpticalDigitalServiceBlock"):
    """Inactive state of an Optical Digital Service product block."""

    optical_digital_service_name: str | None = None
    client_ports: OpticalClientPortList[OpticalTransponderClientPortBlockInactive] = Field(default_factory=list)
    transport_channels: TransportChannelList[OpticalTransportChannelBlockInactive] = Field(default_factory=list)


class OpticalDigitalServiceBlockProvisioning(
    OpticalDigitalServiceBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an Optical Digital Service product block."""

    optical_digital_service_name: str
    client_ports: OpticalClientPortList[OpticalTransponderClientPortBlockProvisioning]
    transport_channels: TransportChannelList[OpticalTransportChannelBlockProvisioning]


class OpticalDigitalServiceBlock(OpticalDigitalServiceBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Digital Service product block."""

    optical_digital_service_name: str
    client_ports: OpticalClientPortList[Clients]
    transport_channels: TransportChannelList[OpticalTransportChannelBlock]
