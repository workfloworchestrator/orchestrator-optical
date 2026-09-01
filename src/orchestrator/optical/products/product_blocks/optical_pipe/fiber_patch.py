"""Product Blocks of Fiber Patch Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    FiberSides,
)
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    PatchPortBlock,
    PatchPortBlockInactive,
    PatchPortBlockProvisioning,
)


class OpticalFiberPatchBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="FiberPatchBlock"):
    """Inactive state of a Fiber Patch product block."""

    optical_pipe_name: str | None = None
    optical_pipe_terminations: FiberSides[PatchPortBlockInactive]


class OpticalFiberPatchBlockProvisioning(
    OpticalFiberPatchBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Fiber Patch product block."""

    optical_pipe_name: str | None
    optical_pipe_terminations: FiberSides[PatchPortBlockProvisioning]


class OpticalFiberPatchBlock(
    OpticalFiberPatchBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Fiber Patch product block."""

    optical_pipe_name: str
    optical_pipe_terminations: FiberSides[PatchPortBlock]
