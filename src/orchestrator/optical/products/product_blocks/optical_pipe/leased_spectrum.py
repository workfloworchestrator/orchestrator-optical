"""Product Blocks of Leased Spectrum Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe._abstracts import (
    _AbstractOpticalPipeBlock,
    _AbstractOpticalPipeBlockInactive,
    _AbstractOpticalPipeBlockProvisioning,
    FiberSides,
)
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    LeasedSpectrumPortBlock,
    LeasedSpectrumPortBlockInactive,
    LeasedSpectrumPortBlockProvisioning,
)


class OpticalLeasedSpectrumBlockInactive(_AbstractOpticalPipeBlockInactive, product_block_name="LeasedSpectrumBlock"):
    """Inactive state of a Leased Spectrum product block."""

    optical_pipe_name: str | None = None
    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlockInactive]


class OpticalLeasedSpectrumBlockProvisioning(
    OpticalLeasedSpectrumBlockInactive,
    _AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Leased Spectrum product block."""

    optical_pipe_name: str | None
    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlockProvisioning]


class OpticalLeasedSpectrumBlock(
    OpticalLeasedSpectrumBlockProvisioning,
    _AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Leased Spectrum product block."""

    optical_pipe_name: str
    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlock]
