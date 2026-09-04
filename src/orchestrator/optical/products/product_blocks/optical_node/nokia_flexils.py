"""Product Blocks of Nokia FlexILS Optical Nodes."""

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
from orchestrator.optical.utils.custom_types.ip_address import IPAddress


class NokiaFlexIlsBlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaFlexIlsBlock"):
    """Product Block of a Nokia FlexILS Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None
    optical_flexils_gmpls_id: IPAddress | None = None
    optical_flexils_target_id: str | None = None

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive

    @model_validator(mode="after")
    def enforce_flexils(self):
        """Ensure that the Optical Node is a Nokia FlexILS."""
        if (vendor := self.management.optical_module_node_vendor) is not None and vendor != Vendor.NOKIA:
            msg = f"Nokia FlexILS can only have vendor 'Nokia', got {vendor}."
            raise ValueError(msg)
        if (platform := self.management.optical_module_node_platform) is not None and platform != Platform.FLEXILS:
            msg = f"Nokia FlexILS can only have platform 'FLEXILS', got {platform}."
            raise ValueError(msg)
        return self


class NokiaFlexIlsBlockProvisioning(
    NokiaFlexIlsBlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia FlexILS Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole | None = None
    optical_flexils_gmpls_id: IPAddress
    optical_flexils_target_id: str

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class NokiaFlexIlsBlock(
    NokiaFlexIlsBlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia FlexILS Optical Node that is active."""

    optical_node_role: OpticalNodeRole
    optical_flexils_gmpls_id: IPAddress
    optical_flexils_target_id: str

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
