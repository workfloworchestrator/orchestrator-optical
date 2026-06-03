"""Module for Optical Digital Service product blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    CoherentPluggable,
    CoherentPluggableInactive,
    CoherentPluggableProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import (
    TransponderClientPort,
    TransponderClientPortInactive,
    TransponderClientPortProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannel,
    OpticalTransportChannelInactive,
    OpticalTransportChannelProvisioning,
)

ClientPortsList = Annotated[list[SI], Len(min_length=2, max_length=2)]

TransportChannelsList = Annotated[
    list[SI], Len(min_length=1, max_length=2)
]  # if 2 then reverse multiplexing: 2 transport channels for one client service


# --- Discriminated Union Types for Client Ports ---

ClientsInactive = Annotated[TransponderClientPortInactive | CoherentPluggableInactive, Field(discriminator="role")]

ClientsProvisioning = Annotated[
    TransponderClientPortProvisioning | CoherentPluggableProvisioning, Field(discriminator="role")
]

Clients = Annotated[TransponderClientPort | CoherentPluggable, Field(discriminator="role")]


# ============================================================================
# --- Optical Digital Service Product Blocks ---
# ============================================================================


class OpticalDigitalServiceInactive(ProductBlockModel, product_block_name="OpticalDigitalService"):
    """Inactive state of an Optical Digital Service product block."""

    service_name: str | None = None
    client_ports: ClientPortsList[TransponderClientPortInactive]
    transport_channels: TransportChannelsList[OpticalTransportChannelInactive]


class OpticalDigitalServiceProvisioning(OpticalDigitalServiceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Provisioning state of an Optical Digital Service product block."""

    service_name: str
    client_ports: ClientPortsList[TransponderClientPortProvisioning]
    transport_channels: TransportChannelsList[OpticalTransportChannelProvisioning]


class OpticalDigitalService(OpticalDigitalServiceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Digital Service product block."""

    client_ports: ClientPortsList[Clients]
    transport_channels: TransportChannelsList[OpticalTransportChannel]
