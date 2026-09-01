"""Models for the subscriptions of Leased Spectrum Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumBlock,
    OpticalLeasedSpectrumBlockInactive,
    OpticalLeasedSpectrumBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_pipe._abstracts import (
    _AbstractOpticalPipe,
    _AbstractOpticalPipeInactive,
    _AbstractOpticalPipeProvisioning,
)


class OpticalLeasedSpectrumInactive(AbstractOpticalPipeInactive, is_base=True):
    """Base model for a leased spectrum subscription in the INACTIVE state."""

    optical_pipe: OpticalLeasedSpectrumBlockInactive


class OpticalLeasedSpectrumProvisioning(
    OpticalLeasedSpectrumInactive, _AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Base model for a leased spectrum subscription in the PROVISIONING state."""

    optical_pipe: OpticalLeasedSpectrumBlockProvisioning


class OpticalLeasedSpectrum(
    OpticalLeasedSpectrumProvisioning, _AbstractOpticalPipe, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base model for a leased spectrum subscription in the ACTIVE state."""

    optical_pipe: OpticalLeasedSpectrumBlock
