"""Module for Optical Transport Channel product blocks."""

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
    TransponderLinePortBlock,
    TransponderLinePortBlockInactive,
    TransponderLinePortBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlock,
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)

LinePortList = Annotated[list[SI], Len(min_length=2, max_length=2)]

# --- Discriminated Line Port Unions ---

TrxInactive = Annotated[
    CoherentPluggableBlockInactive | TransponderLinePortBlockInactive,
    Field(discriminator="role"),
]

TrxProvisioning = Annotated[
    CoherentPluggableBlockProvisioning | TransponderLinePortBlockProvisioning,
    Field(discriminator="role"),
]

Trx = Annotated[
    CoherentPluggableBlock | TransponderLinePortBlock,
    Field(discriminator="role"),
]


class OpticalTransportChannelBlockInactive(ProductBlockModel, product_block_name="OpticalTransportChannel"):
    """Inactive state of an Optical Transport Channel product block."""

    channel_name: str | None = None
    central_frequency: int | None = None
    mode: str | None = None
    line_ports: LinePortList[TrxInactive]
    spectrum: OpticalSpectrumBlockInactive


class OpticalTransportChannelBlockProvisioning(
    OpticalTransportChannelBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an Optical Transport Channel product block."""

    channel_name: str
    central_frequency: int
    mode: str
    line_ports: LinePortList[TrxProvisioning]
    spectrum: OpticalSpectrumBlockProvisioning


class OpticalTransportChannelBlock(OpticalTransportChannelBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Transport Channel product block."""

    line_ports: LinePortList[Trx]
    spectrum: OpticalSpectrumBlock
