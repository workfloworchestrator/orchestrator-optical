"""Models for the subscriptions of Nokia Groove G30 Optical Nodes."""

from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30Block,
    NokiaGrooveG30BlockInactive,
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator_optical.products.product_types.optical_node.abstracts import (
    AbstractOpticalNode,
    AbstractOpticalNodeInactive,
    AbstractOpticalNodeProvisioning,
)


class OpticalNodeNokiaGrooveG30Inactive(AbstractOpticalNodeInactive, is_base=True):
    """A Nokia Groove G30 Optical Node that is inactive."""

    optical_node: NokiaGrooveG30BlockInactive


class OpticalNodeNokiaGrooveG30Provisioning(
    OpticalNodeNokiaGrooveG30Inactive, AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia Groove G30 Optical Node that is provisioning."""

    optical_node: NokiaGrooveG30BlockProvisioning


class OpticalNodeNokiaGrooveG30(
    OpticalNodeNokiaGrooveG30Provisioning, AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A Nokia Groove G30 Optical Node that is active."""

    optical_node: NokiaGrooveG30Block
