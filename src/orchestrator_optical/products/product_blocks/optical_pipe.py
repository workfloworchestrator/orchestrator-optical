"""Module for Optical Pipe product blocks (Fiber Patch, Fiber Span, and Leased Spectrum)."""

from enum import StrEnum
from typing import Annotated, Literal

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

ListOfPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


class PipeType(StrEnum):
    """missing docstring."""

    PATCH = "Fiber Patch"
    SPAN = "Fiber Span"
    LEASED_SPECTRUM = "Leased Spectrum"


# --- Discriminated Union Types for Patch Pipes ---

PatchPortBlocksInactive = Annotated[
    TransponderClientPortBlockInactive | TransponderLinePortBlockInactive | OlsAddDropPortBlockInactive | CoherentPluggableBlockInactive,
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


# --- Discriminated Port Unions for Span Pipes ---

SpanPortBlocksInactive = OlsLinePortBlockInactive
SpanPortBlocksProvisioning = OlsLinePortBlockProvisioning
SpanPortBlocks = OlsLinePortBlock


# --- Discriminated Port Unions for Leased Spectrum Pipes ---

LeasedSpectrumPortBlocksInactive = Annotated[
    TransponderLinePortBlockInactive | OlsAddDropPortBlockInactive | OlsLinePortBlockInactive | CoherentPluggableBlockInactive,
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


# ============================================================================
# --- Fiber Patch Product Blocks ---
# ============================================================================


class FiberPatchBlockInactive(ProductBlockModel, product_block_name="FiberPatch"):
    """Inactive state of a Fiber Patch product block."""

    optical_pipe_type: Literal[PipeType.PATCH] = PipeType.PATCH
    fiber_name: str | None = None
    terminations: ListOfPorts[PatchPortBlocksInactive]


class FiberPatchBlockProvisioning(FiberPatchBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    """Provisioning state of a Fiber Patch product block."""

    terminations: ListOfPorts[PatchPortBlocksProvisioning]


class FiberPatchBlock(FiberPatchBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    """Active state of a Fiber Patch product block."""

    fiber_name: str
    terminations: ListOfPorts[PatchPortBlocks]


# ============================================================================
# --- Fiber Span Product Blocks ---
# ============================================================================


class FiberSpanBlockInactive(ProductBlockModel, product_block_name="FiberSpan"):
    """Inactive state of a Fiber Span product block."""

    optical_pipe_type: Literal[PipeType.SPAN] = PipeType.SPAN
    fiber_name: str | None = None
    terminations: ListOfPorts[SpanPortBlocksInactive]


class FiberSpanBlockProvisioning(FiberSpanBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    """Provisioning state of a Fiber Span product block."""

    terminations: ListOfPorts[SpanPortBlocksProvisioning]


class FiberSpanBlock(FiberSpanBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    """Active state of a Fiber Span product block."""

    fiber_name: str
    terminations: ListOfPorts[SpanPortBlocks]


# ============================================================================
# --- Leased Spectrum Product Blocks ---
# ============================================================================


class LeasedSpectrumBlockInactive(ProductBlockModel, product_block_name="LeasedSpectrum"):
    """Inactive state of a Leased Spectrum product block."""

    optical_pipe_type: Literal[PipeType.LEASED_SPECTRUM] = PipeType.LEASED_SPECTRUM
    spectrum_name: str | None = None
    terminations: ListOfPorts[LeasedSpectrumPortBlocksInactive]


class LeasedSpectrumBlockProvisioning(LeasedSpectrumBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    """Provisioning state of a Leased Spectrum product block."""

    terminations: ListOfPorts[LeasedSpectrumPortBlocksProvisioning]


class LeasedSpectrumBlock(LeasedSpectrumBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    """Active state of a Leased Spectrum product block."""

    spectrum_name: str
    terminations: ListOfPorts[LeasedSpectrumPortBlocks]
