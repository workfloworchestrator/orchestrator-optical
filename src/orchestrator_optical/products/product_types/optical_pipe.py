"""Models for the subscriptions of optical pipes."""

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_pipe import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    OpticalFiberPatchBlock,
    OpticalFiberPatchBlockInactive,
    OpticalFiberPatchBlockProvisioning,
    OpticalFiberSpanBlock,
    OpticalFiberSpanBlockInactive,
    OpticalFiberSpanBlockProvisioning,
    OpticalLeasedSpectrumBlock,
    OpticalLeasedSpectrumBlockInactive,
    OpticalLeasedSpectrumBlockProvisioning,
)


class AbstractOpticalPipeInactive(SubscriptionModel, is_base=True):
    """Abstract base model for generic optical pipe subscription handling."""

    optical_pipe: AbstractOpticalPipeBlockInactive


class AbstractOpticalPipeProvisioning(AbstractOpticalPipeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Abstract base model for provisioning optical pipe subscriptions."""

    optical_pipe: AbstractOpticalPipeBlockProvisioning


class AbstractOpticalPipe(AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base model for active/operational optical pipe subscriptions."""

    optical_pipe: AbstractOpticalPipeBlock


class OpticalFiberPatchInactive(AbstractOpticalPipeInactive, is_base=True):
    """Base model for an internal fiber patch subscription in the INACTIVE state."""

    optical_pipe: OpticalFiberPatchBlockInactive


class OpticalFiberPatchProvisioning(
    OpticalFiberPatchInactive, AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Base model for an internal fiber patch subscription in the PROVISIONING state."""

    optical_pipe: OpticalFiberPatchBlockProvisioning


class OpticalFiberPatch(OpticalFiberPatchProvisioning, AbstractOpticalPipe, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Base model for an internal fiber patch subscription in the ACTIVE state."""

    optical_pipe: OpticalFiberPatchBlock


class OpticalFiberSpanInactive(AbstractOpticalPipeInactive, is_base=True):
    """Base model for a fiber span subscription in the INACTIVE state."""

    optical_pipe: OpticalFiberSpanBlockInactive


class OpticalFiberSpanProvisioning(
    OpticalFiberSpanInactive, AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Base model for a fiber span subscription in the PROVISIONING state."""

    optical_pipe: OpticalFiberSpanBlockProvisioning


class OpticalFiberSpan(OpticalFiberSpanProvisioning, AbstractOpticalPipe, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Base model for a fiber span subscription in the ACTIVE state."""

    optical_pipe: OpticalFiberSpanBlock


class OpticalLeasedSpectrumInactive(AbstractOpticalPipeInactive, is_base=True):
    """Base model for a leased spectrum subscription in the INACTIVE state."""

    optical_pipe: OpticalLeasedSpectrumBlockInactive


class OpticalLeasedSpectrumProvisioning(
    OpticalLeasedSpectrumInactive, AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Base model for a leased spectrum subscription in the PROVISIONING state."""

    optical_pipe: OpticalLeasedSpectrumBlockProvisioning


class OpticalLeasedSpectrum(
    OpticalLeasedSpectrumProvisioning, AbstractOpticalPipe, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base model for a leased spectrum subscription in the ACTIVE state."""

    optical_pipe: OpticalLeasedSpectrumBlock
