"""Models for the subscriptions of optical pipes."""

from enum import StrEnum
from typing import Literal

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


# ── Fixed Inputs ───────────
class PipeType(StrEnum):
    """Types of optical pipes."""

    PATCH = "Fiber Patch"
    SPAN = "Fiber Span"
    LEASED_SPECTRUM = "Leased Spectrum"


# ── Abstract subscription (no is_base) — for generic workflow code ───────────
class AbstractOpticalPipeSubscriptionInactive(SubscriptionModel):
    """Abstract base model for generic optical pipe subscription handling."""

    pipe_type: PipeType
    block: AbstractOpticalPipeBlockInactive


class AbstractOpticalPipeSubscriptionProvisioning(AbstractOpticalPipeSubscriptionInactive):
    """Abstract base model for provisioning optical pipe subscriptions."""

    block: AbstractOpticalPipeBlockProvisioning


class AbstractOpticalPipeSubscription(AbstractOpticalPipeSubscriptionProvisioning):
    """Abstract base model for active/operational optical pipe subscriptions."""

    block: AbstractOpticalPipeBlock


# ── Concrete subscription for Fiber Patch ─────────────────────────────────────
class FiberPatchSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for an internal fiber patch subscription in the INACTIVE state."""

    pipe_type: Literal[PipeType.PATCH] = PipeType.PATCH
    block: FiberPatchBlockInactive


class FiberPatchSubscriptionProvisioning(
    FiberPatchSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for an internal fiber patch subscription in the PROVISIONING state."""

    block: FiberPatchBlockProvisioning


class FiberPatchSubscription(
    FiberPatchSubscriptionProvisioning,
    AbstractOpticalPipeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Base model for an internal fiber patch subscription in the ACTIVE state."""

    block: FiberPatchBlock


# ============================================================================
# Fiber Span Subscriptions
# ============================================================================


class FiberSpanSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for a fiber span subscription in the INACTIVE state."""

    pipe_type: Literal[PipeType.SPAN] = PipeType.SPAN
    block: FiberSpanBlockInactive


class FiberSpanSubscriptionProvisioning(
    FiberSpanSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for a fiber span subscription in the PROVISIONING state."""

    block: FiberSpanBlockProvisioning


class FiberSpanSubscription(
    FiberSpanSubscriptionProvisioning,
    AbstractOpticalPipeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Base model for a fiber span subscription in the ACTIVE state."""

    block: FiberSpanBlock


# ============================================================================
# Leased Spectrum Subscriptions
# ============================================================================


class LeasedSpectrumSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for a leased spectrum subscription in the INACTIVE state."""

    pipe_type: Literal[PipeType.LEASED_SPECTRUM] = PipeType.LEASED_SPECTRUM
    block: LeasedSpectrumBlockInactive


class LeasedSpectrumSubscriptionProvisioning(
    LeasedSpectrumSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for a leased spectrum subscription in the PROVISIONING state."""

    block: LeasedSpectrumBlockProvisioning


class LeasedSpectrumSubscription(
    LeasedSpectrumSubscriptionProvisioning,
    AbstractOpticalPipeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """Base model for a leased spectrum subscription in the ACTIVE state."""

    block: LeasedSpectrumBlock
