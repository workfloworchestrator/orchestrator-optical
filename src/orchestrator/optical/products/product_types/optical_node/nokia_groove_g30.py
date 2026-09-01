"""Models for the subscriptions of Nokia Groove G30 Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30Block,
    NokiaGrooveG30BlockInactive,
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node._abstracts import (
    _AbstractOpticalNode,
    _AbstractOpticalNodeInactive,
    _AbstractOpticalNodeProvisioning,
)


class OpticalNodeNokiaGrooveG30Inactive(_AbstractOpticalNodeInactive, is_base=True):
    """A Nokia Groove G30 Optical Node that is inactive."""

    optical_node: NokiaGrooveG30BlockInactive


class OpticalNodeNokiaGrooveG30Provisioning(
    OpticalNodeNokiaGrooveG30Inactive, _AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia Groove G30 Optical Node that is provisioning."""

    optical_node: NokiaGrooveG30BlockProvisioning


class OpticalNodeNokiaGrooveG30(
    OpticalNodeNokiaGrooveG30Provisioning, _AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A Nokia Groove G30 Optical Node that is active."""

    optical_node: NokiaGrooveG30Block
