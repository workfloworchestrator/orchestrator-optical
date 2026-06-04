"""Models for the subscriptions of optical pipes."""


from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_pipe import (
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

# ============================================================================
# Fiber Patch Subscriptions
# ============================================================================


class FiberPatchSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for an internal fiber patch subscription in the INACTIVE state."""

    fiber: FiberPatchBlockInactive


class FiberPatchSubscriptionProvisioning(
    FiberPatchSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an internal fiber patch subscription in the PROVISIONING state."""

    fiber: FiberPatchBlockProvisioning


class FiberPatchSubscription(
    FiberPatchSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for an internal fiber patch subscription in the ACTIVE state."""

    fiber: FiberPatchBlock


# ============================================================================
# Fiber Span Subscriptions
# ============================================================================


class FiberSpanSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for a fiber span subscription in the INACTIVE state."""

    fiber: FiberSpanBlockInactive


class FiberSpanSubscriptionProvisioning(
    FiberSpanSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for a fiber span subscription in the PROVISIONING state."""

    fiber: FiberSpanBlockProvisioning


class FiberSpanSubscription(
    FiberSpanSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for a fiber span subscription in the ACTIVE state."""

    fiber: FiberSpanBlock


# ============================================================================
# Leased Spectrum Subscriptions
# ============================================================================


class LeasedSpectrumSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for a leased spectrum subscription in the INACTIVE state."""

    leased_spectrum: LeasedSpectrumBlockInactive


class LeasedSpectrumSubscriptionProvisioning(
    LeasedSpectrumSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for a leased spectrum subscription in the PROVISIONING state."""

    leased_spectrum: LeasedSpectrumBlockProvisioning


class LeasedSpectrumSubscription(
    LeasedSpectrumSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """base model for a leased spectrum subscription in the ACTIVE state."""

    leased_spectrum: LeasedSpectrumBlock

