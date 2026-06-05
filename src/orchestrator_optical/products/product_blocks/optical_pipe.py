"""Module for Optical Pipe product blocks (Fiber Patch, Fiber Span, and Leased Spectrum)."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Discriminator, Field

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
    OpticalTransponderClientPortBlock,
    OpticalTransponderClientPortBlockInactive,
    OpticalTransponderClientPortBlockProvisioning,
    OpticalTransponderLinePortBlock,
    OpticalTransponderLinePortBlockInactive,
    OpticalTransponderLinePortBlockProvisioning,
)

ListOfPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


# --- Discriminated Union Types for Patch Fibers ---

PatchPortBlocksInactive = Annotated[
    OpticalTransponderClientPortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="role"),
]

PatchPortBlocksProvisioning = Annotated[
    OpticalTransponderClientPortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="role"),
]

PatchPortBlocks = Annotated[
    OpticalTransponderClientPortBlock
    | OpticalTransponderLinePortBlock
    | OlsAddDropPortBlock
    | OpticalCoherentPluggableBlock,
    Field(discriminator="role"),
]


# --- Discriminated Port Unions for Span Fibers ---

SpanPortBlocksInactive = OlsLinePortBlockInactive
SpanPortBlocksProvisioning = OlsLinePortBlockProvisioning
SpanPortBlocks = OlsLinePortBlock


# --- Discriminated Port Unions for Leased Spectra ---

LeasedSpectrumPortBlocksInactive = Annotated[
    OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="role"),
]

LeasedSpectrumPortBlocksProvisioning = Annotated[
    OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="role"),
]

LeasedSpectrumPortBlocks = Annotated[
    OpticalTransponderLinePortBlock | OlsAddDropPortBlock | OlsLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="role"),
]

# ----------

OpticalTransportLineChannelBlockInactive = Annotated[
    OpticalTransponderLinePortBlockInactive | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="role"),
]

OpticalTransportLineChannelBlockProvisioning = Annotated[
    OpticalTransponderLinePortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="role"),
]

OpticalTransportLineChannelBlock = Annotated[
    OpticalTransponderLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="role"),
]


class AbstractOpticalPipeBlockInactive(ProductBlockModel):
    """Abstract base class for all optical pipe blocks in the INACTIVE state."""

    identifier: str | None = None
    terminations: ListOfPorts[SI]


class AbstractOpticalPipeBlockProvisioning(
    AbstractOpticalPipeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract base class for all optical pipe blocks in the PROVISIONING state."""

    terminations: ListOfPorts[SI]


class AbstractOpticalPipeBlock(AbstractOpticalPipeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base class for all optical pipe blocks in the ACTIVE state."""

    identifier: str
    terminations: ListOfPorts[SI]


# ── Fiber Patch Product Blocks ──────────────────────────────────
class FiberPatchBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberPatchBlock"):
    """Inactive state of a Fiber Patch product block."""

    terminations: ListOfPorts[PatchPortBlocksInactive]


class FiberPatchBlockProvisioning(
    FiberPatchBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Fiber Patch product block."""

    terminations: ListOfPorts[PatchPortBlocksProvisioning]


class FiberPatchBlock(
    FiberPatchBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Fiber Patch product block."""

    terminations: ListOfPorts[PatchPortBlocks]


# ── Fiber Span Product Blocks ──────────────────────────────────
class FiberSpanBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberSpanBlock"):
    """Inactive state of a Fiber Span product block."""

    terminations: ListOfPorts[SpanPortBlocksInactive]


class FiberSpanBlockProvisioning(
    FiberSpanBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Fiber Span product block."""

    terminations: ListOfPorts[SpanPortBlocksProvisioning]


class FiberSpanBlock(
    FiberSpanBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Fiber Span product block."""

    terminations: ListOfPorts[SpanPortBlocks]


# ── Leased Spectrum Product Blocks ──────────────────────────────────
class LeasedSpectrumBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="LeasedSpectrum"):
    """Inactive state of a Leased Spectrum product block."""

    terminations: ListOfPorts[LeasedSpectrumPortBlocksInactive]


class LeasedSpectrumBlockProvisioning(
    LeasedSpectrumBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Leased Spectrum product block."""

    terminations: ListOfPorts[LeasedSpectrumPortBlocksProvisioning]


class LeasedSpectrumBlock(
    LeasedSpectrumBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Leased Spectrum product block."""

    terminations: ListOfPorts[LeasedSpectrumPortBlocks]


# ── Discriminated Unions ────────────────────────────────────────────────────
OpticalPipeBlockUnion = Annotated[
    FiberPatchBlock | FiberSpanBlock | LeasedSpectrumBlock,
    Discriminator(lambda x: x.pipe_type),
]
OpticalPipeBlockUnionProvisioning = Annotated[
    FiberPatchBlockProvisioning | FiberSpanBlockProvisioning | LeasedSpectrumBlockProvisioning,
    Discriminator(lambda x: x.pipe_type),
]
OpticalPipeBlockUnionInactive = Annotated[
    FiberPatchBlockInactive | FiberSpanBlockInactive | LeasedSpectrumBlockInactive,
    Discriminator(lambda x: x.pipe_type),
]
