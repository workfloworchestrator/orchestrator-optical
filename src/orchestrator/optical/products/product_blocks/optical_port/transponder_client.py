"""Product Blocks of Transponder Client Optical Ports."""

from typing import Literal

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.unions import (
    TransponderBlockInactiveUnion,
    TransponderBlockProvisioningUnion,
    TransponderBlockUnion,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalPortBlock,
    AbstractOpticalPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    OpticalPortRole,
)


class OpticalTransponderClientPortBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="OpticalTransponderClientPortBlock"
):
    """Optical Transponder Client Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_CLIENT] = OpticalPortRole.TRANSPONDER_CLIENT
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_port_host_node: TransponderBlockInactiveUnion


class OpticalTransponderClientPortBlockProvisioning(
    OpticalTransponderClientPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Optical Transponder Client Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_CLIENT] = OpticalPortRole.TRANSPONDER_CLIENT
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: TransponderBlockProvisioningUnion


class OpticalTransponderClientPortBlock(
    OpticalTransponderClientPortBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Optical Transponder Client Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_CLIENT] = OpticalPortRole.TRANSPONDER_CLIENT
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: TransponderBlockUnion
