"""Models for the subscriptions of optical pipes."""

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_pipe import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    FiberPatchBlock,
    FiberPatchBlockInactive,
    FiberPatchBlockProvisioning,
    FiberSpanBlock,
    FiberSpanBlockInactive,
    FiberSpanBlockProvisioning,
    LeasedSpectrumBlock,
    LeasedSpectrumBlockInactive,
    LeasedSpectrumBlockProvisioning,
)


class AbstractOpticalPipeSubscriptionInactive(SubscriptionModel):
    """Abstract base model for generic optical pipe subscription handling."""

    optical_pipe: AbstractOpticalPipeBlockInactive


class AbstractOpticalPipeSubscriptionProvisioning(AbstractOpticalPipeSubscriptionInactive):
    """Abstract base model for provisioning optical pipe subscriptions."""

    optical_pipe: AbstractOpticalPipeBlockProvisioning


class AbstractOpticalPipeSubscription(AbstractOpticalPipeSubscriptionProvisioning):
    """Abstract base model for active/operational optical pipe subscriptions."""

    optical_pipe: AbstractOpticalPipeBlock


class FiberPatchSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for an internal fiber patch subscription in the INACTIVE state."""

    optical_pipe: FiberPatchBlockInactive


class FiberPatchSubscriptionProvisioning(
    FiberPatchSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for an internal fiber patch subscription in the PROVISIONING state."""

    optical_pipe: FiberPatchBlockProvisioning


class FiberPatchSubscription(
    FiberPatchSubscriptionProvisioning,
    AbstractOpticalPipeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Base model for an internal fiber patch subscription in the ACTIVE state."""

    optical_pipe: FiberPatchBlock


class FiberSpanSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for a fiber span subscription in the INACTIVE state."""

    optical_pipe: FiberSpanBlockInactive


class FiberSpanSubscriptionProvisioning(
    FiberSpanSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for a fiber span subscription in the PROVISIONING state."""

    optical_pipe: FiberSpanBlockProvisioning


class FiberSpanSubscription(
    FiberSpanSubscriptionProvisioning,
    AbstractOpticalPipeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Base model for a fiber span subscription in the ACTIVE state."""

    optical_pipe: FiberSpanBlock


class LeasedSpectrumSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for a leased spectrum subscription in the INACTIVE state."""

    optical_pipe: LeasedSpectrumBlockInactive


class LeasedSpectrumSubscriptionProvisioning(
    LeasedSpectrumSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for a leased spectrum subscription in the PROVISIONING state."""

    optical_pipe: LeasedSpectrumBlockProvisioning


class LeasedSpectrumSubscription(
    LeasedSpectrumSubscriptionProvisioning,
    AbstractOpticalPipeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Base model for a leased spectrum subscription in the ACTIVE state."""

    optical_pipe: LeasedSpectrumBlock
