"""Product Blocks of Nokia FlexILS Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)
from orchestrator.optical.utils.custom_types.ip_address import IPAddress


class NokiaFlexIlsBlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaFlexIlsBlock"):
    """Product Block of a Nokia FlexILS Optical Node that is inactive."""

    gmpls_id: IPAddress | None = None
    optical_flexils_target_id: str | None = None


class NokiaFlexIlsBlockProvisioning(
    NokiaFlexIlsBlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia FlexILS Optical Node that is provisioning."""

    gmpls_id: IPAddress
    optical_flexils_target_id: str


class NokiaFlexIlsBlock(
    NokiaFlexIlsBlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia FlexILS Optical Node that is active."""

    gmpls_id: IPAddress
    optical_flexils_target_id: str
