"""Product Blocks of Optical Packet Nodes.

An Optical Packet Node is a packet-layer node that accepts Optical Coherent Pluggables,
i.e. it terminates coherent wavelengths carrying IP over the DWDM layer. It is modelled as
a first-class Optical Node whose role is fixed to ``IPODWDM``.
"""

from typing import Literal

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node._abstracts import (
    _AbstractOpticalNodeBlock,
    _AbstractOpticalNodeBlockInactive,
    _AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlock,
    OpticalModuleNodeManagementBlockInactive,
    OpticalModuleNodeManagementBlockProvisioning,
)


class OpticalModulePacketNodeBlockInactive(
    _AbstractOpticalNodeBlockInactive, product_block_name="OpticalModulePacketNode"
):
    """A packet layer Node that accepts Optical Coherent Pluggables that is inactive."""

    optical_node_role: Literal[OpticalNodeRole.IPODWDM] = OpticalNodeRole.IPODWDM

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive


class OpticalModulePacketNodeBlockProvisioning(
    OpticalModulePacketNodeBlockInactive,
    _AbstractOpticalNodeBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """A packet layer Node that accepts Optical Coherent Pluggables that is provisioning."""

    optical_node_role: Literal[OpticalNodeRole.IPODWDM] = OpticalNodeRole.IPODWDM

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class OpticalModulePacketNodeBlock(
    OpticalModulePacketNodeBlockProvisioning, _AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A packet layer Node that accepts Optical Coherent Pluggables."""

    optical_node_role: Literal[OpticalNodeRole.IPODWDM] = OpticalNodeRole.IPODWDM

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
