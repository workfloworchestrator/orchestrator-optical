"""Abstract models for the subscriptions of Optical Nodes."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node._abstracts import (
    _AbstractOpticalNodeBlock,
    _AbstractOpticalNodeBlockInactive,
    _AbstractOpticalNodeBlockProvisioning,
)


class _AbstractOpticalNodeInactive(SubscriptionModel):
    """Abstract base model for an optical node subscription in the inactive state."""

    optical_node: _AbstractOpticalNodeBlockInactive


class _AbstractOpticalNodeProvisioning(_AbstractOpticalNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Abstract base model for an optical node subscription in the provisioning state."""

    optical_node: _AbstractOpticalNodeBlockProvisioning


class _AbstractOpticalNode(_AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base model for an optical node subscription in the active state."""

    optical_node: _AbstractOpticalNodeBlock
