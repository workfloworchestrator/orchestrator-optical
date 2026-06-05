"""Module for Optical Transport Channel product blocks."""
from orchestrator_optical.products.product_blocks.optical_port import OpticalTransponderLinePortBlockInactive

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlock,
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)

OpticalLinePortList = Annotated[list[SI], Len(min_length=2, max_length=2)]


class OpticalTransportChannelBlockInactive(ProductBlockModel, product_block_name="OpticalTransportChannel"):
    """Inactive state of an Optical Transport Channel product block."""

    optical_transport_channel_name: str | None = None
    optical_transport_central_frequency: int | None = None
    optical_transport_mode: str | None = None
    optical_transport_line_ports: OpticalLinePortList[CoherentPluggableBlockInactive | OpticalTransponderLinePortBlockInactive] = Field(default_factory=list)
    optical_transport_spectrum: OpticalSpectrumBlockInactive


class OpticalTransportChannelBlockProvisioning(
    OpticalTransportChannelBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an Optical Transport Channel product block."""

    optical_transport_channel_name: str
    optical_transport_central_frequency: int
    optical_transport_mode: str
    optical_transport_line_ports: OpticalLinePortList[OpticalPortBlockProvisioning]
    optical_transport_spectrum: OpticalSpectrumBlockProvisioning


class OpticalTransportChannelBlock(OpticalTransportChannelBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Transport Channel product block."""

    optical_transport_channel_name: str
    optical_transport_central_frequency: int
    optical_transport_mode: str
    optical_transport_line_ports: OpticalLinePortList[OpticalPortBlock]
    optical_transport_spectrum: OpticalSpectrumBlock
