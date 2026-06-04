"""Module for Optical Pipe product blocks (Fiber Patch, Fiber Span, and Leased Spectrum)."""

from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Literal

from annotated_types import Len
from orchestrator.domain import SubscriptionModel
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Discriminator, Field, computed_field

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    CoherentPluggableBlock,
    CoherentPluggableBlockInactive,
    CoherentPluggableBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
    TransponderClientPortBlock,
    TransponderClientPortBlockInactive,
    TransponderClientPortBlockProvisioning,
    TransponderLinePortBlock,
    TransponderLinePortBlockInactive,
    TransponderLinePortBlockProvisioning,
)

if TYPE_CHECKING:
    from orchestrator_optical.products.product_types.optical_pipe import PipeType

ListOfPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


# --- Discriminated Union Types for Patch Fibers ---

PatchPortBlocksInactive = Annotated[
    TransponderClientPortBlockInactive
    | TransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | CoherentPluggableBlockInactive,
    Field(discriminator="role"),
]

PatchPortBlocksProvisioning = Annotated[
    TransponderClientPortBlockProvisioning
    | TransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | CoherentPluggableBlockProvisioning,
    Field(discriminator="role"),
]

PatchPortBlocks = Annotated[
    TransponderClientPortBlock | TransponderLinePortBlock | OlsAddDropPortBlock | CoherentPluggableBlock,
    Field(discriminator="role"),
]


# --- Discriminated Port Unions for Span Fibers ---

SpanPortBlocksInactive = OlsLinePortBlockInactive
SpanPortBlocksProvisioning = OlsLinePortBlockProvisioning
SpanPortBlocks = OlsLinePortBlock


# --- Discriminated Port Unions for Leased Spectra ---

LeasedSpectrumPortBlocksInactive = Annotated[
    TransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | CoherentPluggableBlockInactive,
    Field(discriminator="role"),
]

LeasedSpectrumPortBlocksProvisioning = Annotated[
    TransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | CoherentPluggableBlockProvisioning,
    Field(discriminator="role"),
]

LeasedSpectrumPortBlocks = Annotated[
    TransponderLinePortBlock | OlsAddDropPortBlock | OlsLinePortBlock | CoherentPluggableBlock,
    Field(discriminator="role"),
]


# ── Abstract block (no product_block_name) ──────────────────────────────────
class AbstractOpticalPipeBlockInactive(ProductBlockModel):
    """Abstract base class for all optical pipe blocks in the INACTIVE state."""

    identifier: str | None = None
    terminations: ListOfPorts[SI]

    @computed_field
    @property
    def pipe_type(self) -> "PipeType":
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.pipe_type


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
class FiberPatchBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberPatch"):
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
class FiberSpanBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberSpan"):
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
