"""Models for the subscriptions of Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.juniper_mx204 import (
    JuniperMx204Block,
    JuniperMx204BlockInactive,
    JuniperMx204BlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node.abstracts import (
    AbstractOpticalNode,
    AbstractOpticalNodeInactive,
    AbstractOpticalNodeProvisioning,
)


class OpticalModuleJuniperMx204SubscriptionInactive(AbstractOpticalNodeInactive, is_base=True):
    """A Juniper MX204 Optical Node that is inactive."""

    optical_node: JuniperMx204BlockInactive


class OpticalModuleJuniperMx204SubscriptionProvisioning(
    OpticalModuleJuniperMx204SubscriptionInactive,
    AbstractOpticalNodeProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """A Juniper MX204 Optical Node that is provisioning."""

    optical_node: JuniperMx204BlockProvisioning


class OpticalModuleJuniperMx204Subscription(
    OpticalModuleJuniperMx204SubscriptionProvisioning, AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A Juniper MX204 Optical Node that is active."""

    optical_node: JuniperMx204Block
