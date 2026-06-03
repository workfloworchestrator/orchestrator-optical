"""Models for the subscriptions of optical pipes."""

from enum import StrEnum
from typing import Annotated

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_pipe import (
    FiberPatch,
    FiberPatchInactive,
    FiberPatchProvisioning,
    FiberSpan,
    FiberSpanInactive,
    FiberSpanProvisioning,
    LeasedSpectrum,
    LeasedSpectrumInactive,
    LeasedSpectrumProvisioning,
)

# ============================================================================
# Fiber Patch Subscriptions
# ============================================================================


class FiberPatchSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for an internal fiber patch subscription in the INACTIVE state."""

    fiber: FiberPatchInactive


class FiberPatchSubscriptionProvisioning(
    FiberPatchSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an internal fiber patch subscription in the PROVISIONING state."""

    fiber: FiberPatchProvisioning


class FiberPatchSubscription(
    FiberPatchSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for an internal fiber patch subscription in the ACTIVE state."""

    fiber: FiberPatch


# ============================================================================
# Fiber Span Subscriptions
# ============================================================================


class FiberSpanSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for a fiber span subscription in the INACTIVE state."""

    fiber: FiberSpanInactive


class FiberSpanSubscriptionProvisioning(
    FiberSpanSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for a fiber span subscription in the PROVISIONING state."""

    fiber: FiberSpanProvisioning


class FiberSpanSubscription(
    FiberSpanSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for a fiber span subscription in the ACTIVE state."""

    fiber: FiberSpan


# ============================================================================
# Leased Spectrum Subscriptions
# ============================================================================


class LeasedSpectrumSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for a leased spectrum subscription in the INACTIVE state."""

    leased_spectrum: LeasedSpectrumInactive


class LeasedSpectrumSubscriptionProvisioning(
    LeasedSpectrumSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for a leased spectrum subscription in the PROVISIONING state."""

    leased_spectrum: LeasedSpectrumProvisioning


class LeasedSpectrumSubscription(
    LeasedSpectrumSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """base model for a leased spectrum subscription in the ACTIVE state."""

    leased_spectrum: LeasedSpectrum
