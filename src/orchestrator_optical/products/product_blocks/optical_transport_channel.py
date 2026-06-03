"""Module for Optical Transport Channel product blocks."""

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
    TransponderLinePort,
    TransponderLinePortInactive,
    TransponderLinePortProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrum,
    OpticalSpectrumInactive,
    OpticalSpectrumProvisioning,
)

LinePortList = Annotated[list[SI], Len(min_length=2, max_length=2)]

# --- Discriminated Line Port Unions ---

TrxInactive = Annotated[
    CoherentPluggableInactive | TransponderLinePortInactive,
    Field(discriminator="role"),
]

TrxProvisioning = Annotated[
    CoherentPluggableProvisioning | TransponderLinePortProvisioning,
    Field(discriminator="role"),
]

Trx = Annotated[
    CoherentPluggable | TransponderLinePort,
    Field(discriminator="role"),
]


class OpticalTransportChannelInactive(ProductBlockModel, product_block_name="OpticalTransportChannel"):
    """Inactive state of an Optical Transport Channel product block."""

    channel_name: str | None = None
    central_frequency: int | None = None
    mode: str | None = None
    line_ports: LinePortList[TrxInactive]
    spectrum: OpticalSpectrumInactive


class OpticalTransportChannelProvisioning(
    OpticalTransportChannelInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an Optical Transport Channel product block."""

    channel_name: str
    central_frequency: int
    mode: str
    line_ports: LinePortList[TrxProvisioning]
    spectrum: OpticalSpectrumProvisioning


class OpticalTransportChannel(OpticalTransportChannelProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Transport Channel product block."""

    line_ports: LinePortList[Trx]
    spectrum: OpticalSpectrum
