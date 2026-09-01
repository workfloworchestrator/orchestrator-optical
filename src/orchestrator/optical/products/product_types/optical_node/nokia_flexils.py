"""Models for the subscriptions of Nokia FlexILS Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node._abstracts import (
    _AbstractOpticalNode,
    _AbstractOpticalNodeInactive,
    _AbstractOpticalNodeProvisioning,
)


class OpticalNodeNokiaFlexIlsInactive(_AbstractOpticalNodeInactive, is_base=True):
    """A Nokia FlexILS Optical Node that is inactive."""

    optical_node: NokiaFlexIlsBlockInactive


class OpticalNodeNokiaFlexIlsProvisioning(
    OpticalNodeNokiaFlexIlsInactive, _AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia FlexILS Optical Node that is provisioning."""

    optical_node: NokiaFlexIlsBlockProvisioning


class OpticalNodeNokiaFlexIls(
    OpticalNodeNokiaFlexIlsProvisioning, _AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A Nokia FlexILS Optical Node that is active."""

    optical_node: NokiaFlexIlsBlock
