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


class OpticalModulePacketNodeBlockInactive(ProductBlockModel, product_block_name="OpticalModulePacketNode"):
    """A packet layer Node that accepts Optical Coherent Pluggables that is inactive."""

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive


class OpticalModulePacketNodeBlockProvisioning(
    OpticalModulePacketNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A packet layer Node that accepts Optical Coherent Pluggables that is provisioning."""

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class OpticalModulePacketNodeBlock(
    OpticalModulePacketNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A packet layer Node that accepts Optical Coherent Pluggables."""

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
