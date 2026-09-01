"""Product Blocks of Leased Spectrum Optical Pipes."""

from typing import Literal

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    FiberSides,
    OpticalPipeType,
)
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    LeasedSpectrumPortBlock,
    LeasedSpectrumPortBlockInactive,
    LeasedSpectrumPortBlockProvisioning,
)


class OpticalLeasedSpectrumBlockInactive(AbstractOpticalPipeBlockInactive, product_block_name="LeasedSpectrumBlock"):
    """Inactive state of a Leased Spectrum product block."""

    optical_pipe_type: Literal[OpticalPipeType.LEASED_SPECTRUM] = OpticalPipeType.LEASED_SPECTRUM
    optical_pipe_name: str | None = None
    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlockInactive]


class OpticalLeasedSpectrumBlockProvisioning(
    OpticalLeasedSpectrumBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Provisioning state of a Leased Spectrum product block."""

    optical_pipe_type: Literal[OpticalPipeType.LEASED_SPECTRUM] = OpticalPipeType.LEASED_SPECTRUM
    optical_pipe_name: str | None
    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlockProvisioning]


class OpticalLeasedSpectrumBlock(
    OpticalLeasedSpectrumBlockProvisioning,
    AbstractOpticalPipeBlock,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Active state of a Leased Spectrum product block."""

    optical_pipe_type: Literal[OpticalPipeType.LEASED_SPECTRUM] = OpticalPipeType.LEASED_SPECTRUM
    optical_pipe_name: str
    optical_pipe_terminations: FiberSides[LeasedSpectrumPortBlock]
