"""Module for Optical Pipe product blocks (Fiber Patch, Fiber Span, and Leased Spectrum)."""

from typing import Annotated

from annotated_types import Len
from pydantic import Discriminator, Field

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port import (
    AbstractOpticalPortBlock,
    AbstractOpticalPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
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

FiberSides = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]

PatchPortBlockInactive = Annotated[
    OpticalTransponderClientPortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]
PatchPortBlockProvisioning = Annotated[
    OpticalTransponderClientPortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]
PatchPortBlock = Annotated[
    OpticalTransponderClientPortBlock
    | OpticalTransponderLinePortBlock
    | OlsAddDropPortBlock
    | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

SpanPortBlockInactive = OlsLinePortBlockInactive
SpanPortBlockProvisioning = OlsLinePortBlockProvisioning
SpanPortBlock = OlsLinePortBlock

LeasedSpectrumPortBlockInactive = Annotated[
    OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]

LeasedSpectrumPortBlockProvisioning = Annotated[
    OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]

LeasedSpectrumPortBlock = Annotated[
    OpticalTransponderLinePortBlock | OlsAddDropPortBlock | OlsLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

OpticalTransportLineChannelBlockInactive = Annotated[
    OpticalTransponderLinePortBlockInactive | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]

OpticalTransportLineChannelBlockProvisioning = Annotated[
    OpticalTransponderLinePortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]

OpticalTransportLineChannelBlock = Annotated[
    OpticalTransponderLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

OpticalDigitalServiceClientPortBlockInactive = Annotated[
    OpticalTransponderClientPortBlockInactive | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]

OpticalDigitalServiceClientPortBlockProvisioning = Annotated[
    OpticalTransponderClientPortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]

OpticalDigitalServiceClientPortBlock = Annotated[
    OpticalTransponderClientPortBlock | OpticalCoherentPluggableBlock, Field(discriminator="optical_port_role")
]


class AbstractOpticalPipeBlockInactive(ProductBlockModel, product_block_name="AbstractOpticalPipeBlock"):
    """Abstract base class for all optical pipe blocks in the INACTIVE state."""

    optical_pipe_identifier: str | None = None
    optical_pipe_terminations: FiberSides[AbstractOpticalPortBlockInactive]


class AbstractOpticalPipeBlockProvisioning(
    AbstractOpticalPipeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract base class for all optical pipe blocks in the PROVISIONING state."""

    optical_pipe_identifier: str | None
    optical_pipe_terminations: FiberSides[AbstractOpticalPortBlockProvisioning]


class AbstractOpticalPipeBlock(AbstractOpticalPipeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base class for all optical pipe blocks in the ACTIVE state."""

    optical_pipe_identifier: str
    optical_pipe_terminations: FiberSides[AbstractOpticalPortBlock]


class OpticalFiberPatchBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberPatchBlock"):
    """Inactive state of a Fiber Patch product block."""

    optical_pipe_terminations: FiberSides[PatchPortBlockInactive]


class OpticalFiberPatchBlockProvisioning(
    OpticalFiberPatchBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Fiber Patch product block."""

    optical_pipe_terminations: FiberSides[PatchPortBlockProvisioning]


class OpticalFiberPatchBlock(
    OpticalFiberPatchBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Fiber Patch product block."""

    optical_pipe_terminations: FiberSides[PatchPortBlock]


class OpticalFiberSpanBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberSpanBlock"):
    """Inactive state of a Fiber Span product block."""

    optical_pipe_terminations: FiberSides[SpanPortBlockInactive]


class OpticalFiberSpanBlockProvisioning(
    OpticalFiberSpanBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Fiber Span product block."""

    optical_pipe_terminations: FiberSides[SpanPortBlockProvisioning]


class OpticalFiberSpanBlock(
    OpticalFiberSpanBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Fiber Span product block."""

    optical_pipe_terminations: FiberSides[SpanPortBlock]


class OpticalLeasedSpectrumBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="LeasedSpectrumBlock"):
    """Inactive state of a Leased Spectrum product block."""

    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlockInactive]


class OpticalLeasedSpectrumBlockProvisioning(
    OpticalLeasedSpectrumBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Leased Spectrum product block."""

    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlockProvisioning]


class OpticalLeasedSpectrumBlock(
    OpticalLeasedSpectrumBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Leased Spectrum product block."""

    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlock]


OpticalPipeBlockUnion = Annotated[
    OpticalFiberPatchBlock | OpticalFiberSpanBlock | OpticalLeasedSpectrumBlock,
    Discriminator(lambda x: x.product.name),
]
OpticalPipeBlockUnionProvisioning = Annotated[
    OpticalFiberPatchBlockProvisioning | OpticalFiberSpanBlockProvisioning | OpticalLeasedSpectrumBlockProvisioning,
    Discriminator(lambda x: x.product.name),
]
OpticalPipeBlockUnionInactive = Annotated[
    OpticalFiberPatchBlockInactive | OpticalFiberSpanBlockInactive | OpticalLeasedSpectrumBlockInactive,
    Discriminator(lambda x: x.product.name),
]
