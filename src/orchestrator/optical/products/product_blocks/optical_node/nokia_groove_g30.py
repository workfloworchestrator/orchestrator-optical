"""Product Blocks of Nokia Groove G30 Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)


class NokiaGrooveG30BlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaGrooveG30Block"):
    """Product Block of a Nokia Groove G30 Optical Node that is inactive."""


class NokiaGrooveG30BlockProvisioning(
    NokiaGrooveG30BlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia Groove G30 Optical Node that is provisioning."""


class NokiaGrooveG30Block(
    NokiaGrooveG30BlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia Groove G30 Optical Node that is active."""
