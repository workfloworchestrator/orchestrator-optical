"""Product Blocks of Juniper MX204 Optical Nodes."""

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


class JuniperMx204BlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="JuniperMx204Block"):
    """Product Block of a Juniper MX204 Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole = OpticalNodeRole.IPODWDM

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive

    @model_validator(mode="after")
    def enforce_mx204(self):
        """Ensure that the Optical Node is a Juniper MX204."""
        if (vendor := self.management.optical_module_node_vendor) is not None and vendor != Vendor.JUNIPER:
            msg = f"Juniper MX204 can only have vendor 'Juniper', got {vendor}."
            raise ValueError(msg)
        if (platform := self.management.optical_module_node_platform) is not None and platform != Platform.MX204:
            msg = f"Juniper MX204 can only have platform 'MX204', got {platform}."
            raise ValueError(msg)
        return self


class JuniperMx204BlockProvisioning(
    JuniperMx204BlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Juniper MX204 Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class JuniperMx204Block(
    JuniperMx204BlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Juniper MX204 Optical Node that is active."""

    optical_node_role: OpticalNodeRole

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
