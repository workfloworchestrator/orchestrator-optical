"""Module for Optical Digital Service product blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    CoherentPluggableBlock,
    CoherentPluggableBlockInactive,
    CoherentPluggableBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import (
    TransponderClientPortBlock,
    TransponderClientPortBlockInactive,
    TransponderClientPortBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlock,
    OpticalTransportChannelBlockInactive,
    OpticalTransportChannelBlockProvisioning,
)

ClientPortsList = Annotated[list[SI], Len(min_length=2, max_length=2)]

TransportChannelsList = Annotated[
    list[SI], Len(min_length=1, max_length=2)
]  # if 2 then reverse multiplexing: 2 transport channels for one client service


# --- Discriminated Union Types for Client Ports ---

ClientsInactive = Annotated[TransponderClientPortBlockInactive | CoherentPluggableBlockInactive, Field(discriminator="role")]

ClientsProvisioning = Annotated[
    TransponderClientPortBlockProvisioning | CoherentPluggableBlockProvisioning, Field(discriminator="role")
]

Clients = Annotated[TransponderClientPortBlock | CoherentPluggableBlock, Field(discriminator="role")]


# ============================================================================
# --- Optical Digital Service Product Blocks ---
# ============================================================================


class OpticalDigitalServiceBlockInactive(ProductBlockModel, product_block_name="OpticalDigitalService"):
    """Inactive state of an Optical Digital Service product block."""

    service_name: str | None = None
    client_ports: ClientPortsList[TransponderClientPortBlockInactive]
    transport_channels: TransportChannelsList[OpticalTransportChannelBlockInactive]


class OpticalDigitalServiceBlockProvisioning(OpticalDigitalServiceBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Provisioning state of an Optical Digital Service product block."""

    service_name: str
    client_ports: ClientPortsList[TransponderClientPortBlockProvisioning]
    transport_channels: TransportChannelsList[OpticalTransportChannelBlockProvisioning]


class OpticalDigitalServiceBlock(OpticalDigitalServiceBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Digital Service product block."""

    client_ports: ClientPortsList[Clients]
    transport_channels: TransportChannelsList[OpticalTransportChannelBlock]
