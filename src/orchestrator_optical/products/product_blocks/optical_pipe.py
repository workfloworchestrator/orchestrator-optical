"""Module for Optical Pipe product blocks (Fiber Patch, Fiber Span, and Leased Spectrum)."""

from enum import StrEnum
from typing import Annotated, Literal

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
    OlsAddDropPort,
    OlsAddDropPortInactive,
    OlsAddDropPortProvisioning,
    OlsLinePort,
    OlsLinePortInactive,
    OlsLinePortProvisioning,
    TransponderClientPort,
    TransponderClientPortInactive,
    TransponderClientPortProvisioning,
    TransponderLinePort,
    TransponderLinePortInactive,
    TransponderLinePortProvisioning,
)

ListOfPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


class PipeType(StrEnum):
    """missing docstring."""

    PATCH = "Fiber Patch"
    SPAN = "Fiber Span"
    LEASED_SPECTRUM = "Leased Spectrum"


# --- Discriminated Union Types for Patch Pipes ---

PatchPortBlocksInactive = Annotated[
    TransponderClientPortInactive | TransponderLinePortInactive | OlsAddDropPortInactive | CoherentPluggableInactive,
    Field(discriminator="role"),
]

PatchPortBlocksProvisioning = Annotated[
    TransponderClientPortProvisioning
    | TransponderLinePortProvisioning
    | OlsAddDropPortProvisioning
    | CoherentPluggableProvisioning,
    Field(discriminator="role"),
]

PatchPortBlocks = Annotated[
    TransponderClientPort | TransponderLinePort | OlsAddDropPort | CoherentPluggable,
    Field(discriminator="role"),
]


# --- Discriminated Port Unions for Span Pipes ---

SpanPortBlocksInactive = OlsLinePortInactive
SpanPortBlocksProvisioning = OlsLinePortProvisioning
SpanPortBlocks = OlsLinePort


# --- Discriminated Port Unions for Leased Spectrum Pipes ---

LeasedSpectrumPortBlocksInactive = Annotated[
    TransponderLinePortInactive | OlsAddDropPortInactive | OlsLinePortInactive | CoherentPluggableInactive,
    Field(discriminator="role"),
]

LeasedSpectrumPortBlocksProvisioning = Annotated[
    TransponderLinePortProvisioning
    | OlsAddDropPortProvisioning
    | OlsLinePortProvisioning
    | CoherentPluggableProvisioning,
    Field(discriminator="role"),
]

LeasedSpectrumPortBlocks = Annotated[
    TransponderLinePort | OlsAddDropPort | OlsLinePort | CoherentPluggable,
    Field(discriminator="role"),
]


# ============================================================================
# --- Fiber Patch Product Blocks ---
# ============================================================================


class FiberPatchInactive(ProductBlockModel, product_block_name="FiberPatch"):
    """Inactive state of a Fiber Patch product block."""

    optical_pipe_type: Literal[PipeType.PATCH] = PipeType.PATCH
    fiber_name: str | None = None
    terminations: ListOfPorts[PatchPortBlocksInactive]


class FiberPatchProvisioning(FiberPatchInactive, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    """Provisioning state of a Fiber Patch product block."""

    terminations: ListOfPorts[PatchPortBlocksProvisioning]


class FiberPatch(FiberPatchProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    """Active state of a Fiber Patch product block."""

    fiber_name: str
    terminations: ListOfPorts[PatchPortBlocks]


# ============================================================================
# --- Fiber Span Product Blocks ---
# ============================================================================


class FiberSpanInactive(ProductBlockModel, product_block_name="FiberSpan"):
    """Inactive state of a Fiber Span product block."""

    optical_pipe_type: Literal[PipeType.SPAN] = PipeType.SPAN
    fiber_name: str | None = None
    terminations: ListOfPorts[SpanPortBlocksInactive]


class FiberSpanProvisioning(FiberSpanInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    """Provisioning state of a Fiber Span product block."""

    terminations: ListOfPorts[SpanPortBlocksProvisioning]


class FiberSpan(FiberSpanProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    """Active state of a Fiber Span product block."""

    fiber_name: str
    terminations: ListOfPorts[SpanPortBlocks]


# ============================================================================
# --- Leased Spectrum Product Blocks ---
# ============================================================================


class LeasedSpectrumInactive(ProductBlockModel, product_block_name="LeasedSpectrum"):
    """Inactive state of a Leased Spectrum product block."""

    optical_pipe_type: Literal[PipeType.LEASED_SPECTRUM] = PipeType.LEASED_SPECTRUM
    spectrum_name: str | None = None
    terminations: ListOfPorts[LeasedSpectrumPortBlocksInactive]


class LeasedSpectrumProvisioning(LeasedSpectrumInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    """Provisioning state of a Leased Spectrum product block."""

    terminations: ListOfPorts[LeasedSpectrumPortBlocksProvisioning]


class LeasedSpectrum(LeasedSpectrumProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    """Active state of a Leased Spectrum product block."""

    spectrum_name: str
    terminations: ListOfPorts[LeasedSpectrumPortBlocks]


OpticalPipeUnion = Annotated[FiberPatch | FiberSpan | LeasedSpectrum, Field(discriminator="optical_pipe_type")]