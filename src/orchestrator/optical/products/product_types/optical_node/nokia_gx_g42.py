"""Models for the subscriptions of Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import (
    NokiaGxG42Block,
    NokiaGxG42BlockInactive,
    NokiaGxG42BlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node.abstracts import (
    AbstractOpticalNode,
    AbstractOpticalNodeInactive,
    AbstractOpticalNodeProvisioning,
)


class OpticalNodeNokiaGxG42Inactive(AbstractOpticalNodeInactive, is_base=True):
    """A Nokia GX G42 Optical Node that is inactive."""

    optical_node: NokiaGxG42BlockInactive


class OpticalNodeNokiaGxG42Provisioning(
    OpticalNodeNokiaGxG42Inactive, AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia GX G42 Optical Node that is provisioning."""

    optical_node: NokiaGxG42BlockProvisioning


class OpticalNodeNokiaGxG42(
    OpticalNodeNokiaGxG42Provisioning, AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A Nokia GX G42 Optical Node that is active."""

    optical_node: NokiaGxG42Block
