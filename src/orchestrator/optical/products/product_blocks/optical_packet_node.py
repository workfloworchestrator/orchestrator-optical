from typing import Annotated

from annotated_types import Len

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlock,
    OpticalModuleNodeManagementBlockInactive,
    OpticalModuleNodeManagementBlockProvisioning,
)


class OpticalModulePacketNodeInactive(ProductBlockModel, product_block_name="OpticalModulePacketNode"):
    """A packet layer Node that accepts Optical Coherent Pluggables that is inactive."""

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive


class OpticalModulePacketNodeProvisioning(
    OpticalModulePacketNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A packet layer Node that accepts Optical Coherent Pluggables that is provisioning."""

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class OpticalModulePacketNode(
    OpticalModulePacketNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A packet layer Node that accepts Optical Coherent Pluggables."""

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
