"""Product Blocks of Nokia GX G42 Optical Nodes."""

from typing import Literal

from pydantic import model_validator

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlock,
    OpticalModuleNodeManagementBlockInactive,
    OpticalModuleNodeManagementBlockProvisioning,
    Platform,
    Vendor,
)


class NokiaGxG42BlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaGxG42Block"):
    """Product Block of a Nokia GX G42 Optical Node that is inactive."""

    optical_node_role: Literal[OpticalNodeRole.TRANSPONDER] | None = None

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive

    @model_validator(mode="after")
    def enforce_g42(self):
        """Ensure that the Optical Node is a Nokia GX G42."""
        if (vendor := self.management.optical_module_node_vendor) is not None and vendor != Vendor.NOKIA:
            msg = f"Nokia GX G42 can only have vendor 'Nokia', got {vendor}."
            raise ValueError(msg)
        if (platform := self.management.optical_module_node_platform) is not None and platform != Platform.GX_G42:
            msg = f"Nokia GX G42 can only have platform 'GX_G42', got {platform}."
            raise ValueError(msg)
        return self


class NokiaGxG42BlockProvisioning(
    NokiaGxG42BlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia GX G42 Optical Node that is provisioning."""

    optical_node_role: Literal[OpticalNodeRole.TRANSPONDER] | None = None

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class NokiaGxG42Block(NokiaGxG42BlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Product Block of a Nokia GX G42 Optical Node that is active."""

    optical_node_role: Literal[OpticalNodeRole.TRANSPONDER]

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
