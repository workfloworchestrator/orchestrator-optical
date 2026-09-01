"""Product Blocks of Transponder Line Optical Ports."""

from typing import Literal

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.unions import (
    TransponderBlockInactiveUnion,
    TransponderBlockProvisioningUnion,
    TransponderBlockUnion,
)
from orchestrator.optical.products.product_blocks.optical_port._abstracts import (
    _AbstractOpticalPortBlock,
    _AbstractOpticalPortBlockInactive,
    _AbstractOpticalPortBlockProvisioning,
    OpticalPortRole,
)


class OpticalTransponderLinePortBlockInactive(
    _AbstractOpticalPortBlockInactive, product_block_name="OpticalTransponderLinePortBlock"
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_port_host_node: TransponderBlockInactiveUnion


class OpticalTransponderLinePortBlockProvisioning(
    OpticalTransponderLinePortBlockInactive,
    _AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: TransponderBlockProvisioningUnion


class OpticalTransponderLinePortBlock(
    OpticalTransponderLinePortBlockProvisioning, _AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: TransponderBlockUnion
