"""Product Blocks of Transponder Line Optical Ports."""

from typing import Literal

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalPortBlock,
    AbstractOpticalPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    OpticalPortRole,
)


class OpticalTransponderLinePortBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="OpticalTransponderLinePortBlock"
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE
    optical_port_host_node: AbstractOpticalNodeBlockInactive


class OpticalTransponderLinePortBlockProvisioning(
    OpticalTransponderLinePortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_host_node: AbstractOpticalNodeBlockProvisioning


class OpticalTransponderLinePortBlock(
    OpticalTransponderLinePortBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_host_node: AbstractOpticalNodeBlock
