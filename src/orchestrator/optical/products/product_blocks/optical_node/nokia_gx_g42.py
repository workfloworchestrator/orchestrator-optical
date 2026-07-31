"""Product Blocks of Nokia GX G42 Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)


class NokiaGxG42BlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaGxG42Block"):
    """Product Block of a Nokia GX G42 Optical Node that is inactive."""


class NokiaGxG42BlockProvisioning(
    NokiaGxG42BlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia GX G42 Optical Node that is provisioning."""


class NokiaGxG42Block(NokiaGxG42BlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Product Block of a Nokia GX G42 Optical Node that is active."""
