"""Module for Optical Transport Channel product blocks."""

from typing import Annotated

from annotated_types import Len
from pydantic import Field

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe import (
    OpticalTransportLineChannelBlock,
    OpticalTransportLineChannelBlockInactive,
    OpticalTransportLineChannelBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlock,
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)

ListOfTwo = Annotated[list[SI], Len(min_length=2, max_length=2)]


class OpticalTransportChannelBlockInactive(ProductBlockModel, product_block_name="OpticalTransportChannelBlock"):
    """Inactive state of an Optical Transport Channel product block."""

    optical_transport_channel_name: str | None = None
    optical_transport_central_frequency: int | None = None
    optical_transport_mode: str | None = None
    optical_transport_line_ports: ListOfTwo[OpticalTransportLineChannelBlockInactive] = Field(default_factory=list)
    optical_transport_spectrum: OpticalSpectrumBlockInactive


class OpticalTransportChannelBlockProvisioning(
    OpticalTransportChannelBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an Optical Transport Channel product block."""

    optical_transport_channel_name: str
    optical_transport_central_frequency: int
    optical_transport_mode: str
    optical_transport_line_ports: ListOfTwo[OpticalTransportLineChannelBlockProvisioning]
    optical_transport_spectrum: OpticalSpectrumBlockProvisioning


class OpticalTransportChannelBlock(OpticalTransportChannelBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Transport Channel product block."""

    optical_transport_channel_name: str
    optical_transport_central_frequency: int
    optical_transport_mode: str
    optical_transport_line_ports: ListOfTwo[OpticalTransportLineChannelBlock]
    optical_transport_spectrum: OpticalSpectrumBlock
