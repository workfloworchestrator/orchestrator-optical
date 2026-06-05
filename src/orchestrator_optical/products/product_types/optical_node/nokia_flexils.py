"""Models for the subscriptions of Nokia FlexILS Optical Nodes."""

from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator_optical.products.product_types.optical_node.abstracts import (
    AbstractOpticalNode,
    AbstractOpticalNodeInactive,
    AbstractOpticalNodeProvisioning,
)


class OpticalNodeNokiaFlexIlsInactive(AbstractOpticalNodeInactive, is_base=True):
    """A Nokia FlexILS Optical Node that is inactive."""

    optical_node: NokiaFlexIlsBlockInactive


class OpticalNodeNokiaFlexIlsProvisioning(
    AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia FlexILS Optical Node that is provisioning."""

    optical_node: NokiaFlexIlsBlockProvisioning


class OpticalNodeNokiaFlexIls(AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """A Nokia FlexILS Optical Node that is active."""

    optical_node: NokiaFlexIlsBlock
