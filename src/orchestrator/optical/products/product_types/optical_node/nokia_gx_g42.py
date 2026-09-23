"""Models for the subscriptions of Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import (
    NokiaGxG42Block,
    NokiaGxG42BlockInactive,
    NokiaGxG42BlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node.abstracts import (
    AbstractOpticalNodeSubscription,
    AbstractOpticalNodeSubscriptionInactive,
    AbstractOpticalNodeSubscriptionProvisioning,
)


class OpticalNodeNokiaGxG42SubscriptionInactive(AbstractOpticalNodeSubscriptionInactive, is_base=True):
    """A Nokia GX G42 Optical Node that is inactive."""

    optical_node: NokiaGxG42BlockInactive


class OpticalNodeNokiaGxG42SubscriptionProvisioning(
    OpticalNodeNokiaGxG42SubscriptionInactive,
    AbstractOpticalNodeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """A Nokia GX G42 Optical Node that is provisioning."""

    optical_node: NokiaGxG42BlockProvisioning


class OpticalNodeNokiaGxG42Subscription(
    OpticalNodeNokiaGxG42SubscriptionProvisioning,
    AbstractOpticalNodeSubscription,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """A Nokia GX G42 Optical Node that is active."""

    optical_node: NokiaGxG42Block
