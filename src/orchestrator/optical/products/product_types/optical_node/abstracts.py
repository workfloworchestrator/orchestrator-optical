"""Abstract models for the subscriptions of Optical Nodes."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)


class AbstractOpticalNodeInactive(SubscriptionModel):
    """Abstract base model for an optical node subscription in the inactive state."""

    optical_node: AbstractOpticalNodeBlockInactive


class AbstractOpticalNodeProvisioning(AbstractOpticalNodeInactive):
    """Abstract base model for an optical node subscription in the provisioning state."""

    optical_node: AbstractOpticalNodeBlockProvisioning


class AbstractOpticalNode(AbstractOpticalNodeProvisioning):
    """Abstract base model for an optical node subscription in the active state."""

    optical_node: AbstractOpticalNodeBlock
