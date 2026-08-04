"""Product Blocks of Leased Spectrum Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    FiberSides,
)
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    LeasedSpectrumPortBlock,
    LeasedSpectrumPortBlockInactive,
    LeasedSpectrumPortBlockProvisioning,
)


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
