"""Product Blocks of Fiber Span Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    FiberSides,
)
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    SpanPortBlock,
    SpanPortBlockInactive,
    SpanPortBlockProvisioning,
)


class OpticalFiberSpanBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberSpanBlock"):
    """Inactive state of a Fiber Span product block."""

    optical_pipe_name: str | None = None
    optical_pipe_terminations: FiberSides[SpanPortBlockInactive]


class OpticalFiberSpanBlockProvisioning(
    OpticalFiberSpanBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Fiber Span product block."""

    optical_pipe_name: str | None
    optical_pipe_terminations: FiberSides[SpanPortBlockProvisioning]


class OpticalFiberSpanBlock(
    OpticalFiberSpanBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Fiber Span product block."""

    optical_pipe_name: str
    optical_pipe_terminations: FiberSides[SpanPortBlock]
