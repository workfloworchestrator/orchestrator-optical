"""Abstract models for the subscriptions of Optical Nodes."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)


class AbstractOpticalNodeSubscriptionInactive(SubscriptionModel):
    """Abstract base model for an optical node subscription in the inactive state."""

    optical_node: AbstractOpticalNodeBlockInactive


class AbstractOpticalNodeSubscriptionProvisioning(AbstractOpticalNodeSubscriptionInactive):
    """Abstract base model for an optical node subscription in the provisioning state."""

    optical_node: AbstractOpticalNodeBlockProvisioning


class AbstractOpticalNodeSubscription(AbstractOpticalNodeSubscriptionProvisioning):
    """Abstract base model for an optical node subscription in the active state."""

    optical_node: AbstractOpticalNodeBlock
