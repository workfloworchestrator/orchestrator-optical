"""Product Blocks of OLS Line Optical Ports."""

from typing import Literal

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlock,
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalOlsPortBlockProvisioning,
    OpticalPortRole,
)


class OlsLinePortBlockInactive(AbstractOpticalOlsPortBlockInactive, product_block_name="OlsLinePortBlock"):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE
    optical_port_host_node: AbstractOpticalNodeBlockInactive


class OlsLinePortBlockProvisioning(
    OlsLinePortBlockInactive, AbstractOpticalOlsPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_host_node: AbstractOpticalNodeBlockProvisioning


class OlsLinePortBlock(
    OlsLinePortBlockProvisioning, AbstractOpticalOlsPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_host_node: AbstractOpticalNodeBlock
