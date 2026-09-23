"""Product Blocks of Nokia Groove G30 Optical Nodes."""

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


class NokiaGrooveG30BlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaGrooveG30Block"):
    """Product Block of a Nokia Groove G30 Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive

    @model_validator(mode="after")
    def enforce_g30(self):
        """Ensure that the Optical Node is a Nokia Groove G30."""
        if (vendor := self.management.optical_module_node_vendor) is not None and vendor != Vendor.NOKIA:
            msg = f"Nokia Groove G30 can only have vendor 'Nokia', got {vendor}."
            raise ValueError(msg)
        if (platform := self.management.optical_module_node_platform) is not None and platform != Platform.GROOVE_G30:
            msg = f"Nokia Groove G30 can only have platform 'GROOVE G30', got {platform}."
            raise ValueError(msg)
        return self


class NokiaGrooveG30BlockProvisioning(
    NokiaGrooveG30BlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia Groove G30 Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole | None = None

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class NokiaGrooveG30Block(
    NokiaGrooveG30BlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia Groove G30 Optical Node that is active."""

    optical_node_role: OpticalNodeRole

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
