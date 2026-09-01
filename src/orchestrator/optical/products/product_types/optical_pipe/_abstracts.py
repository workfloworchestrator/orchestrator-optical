"""Abstract models for the subscriptions of Optical Pipes."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe._abstracts import (
    _AbstractOpticalPipeBlock,
    _AbstractOpticalPipeBlockInactive,
    _AbstractOpticalPipeBlockProvisioning,
)


class _AbstractOpticalPipeInactive(SubscriptionModel):
    """Abstract base model for generic optical pipe subscription handling."""

    optical_pipe: _AbstractOpticalPipeBlockInactive


class _AbstractOpticalPipeProvisioning(AbstractOpticalPipeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Abstract base model for provisioning optical pipe subscriptions."""

    optical_pipe: _AbstractOpticalPipeBlockProvisioning


class _AbstractOpticalPipe(AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base model for active/operational optical pipe subscriptions."""

    optical_pipe: _AbstractOpticalPipeBlock
