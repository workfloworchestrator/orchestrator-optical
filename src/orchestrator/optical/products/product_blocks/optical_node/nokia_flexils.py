"""Product Blocks of Nokia FlexILS Optical Nodes."""

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
from orchestrator.optical.utils.custom_types.ip_address import IPAddress


class NokiaFlexIlsBlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaFlexIlsBlock"):
    """Product Block of a Nokia FlexILS Optical Node that is inactive."""

    optical_node_role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER] | None = None
    optical_flexils_gmpls_id: IPAddress | None = None
    optical_flexils_target_id: str | None = None

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive


class NokiaFlexIlsBlockProvisioning(
    NokiaFlexIlsBlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia FlexILS Optical Node that is provisioning."""

    optical_node_role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER]
    optical_flexils_gmpls_id: IPAddress
    optical_flexils_target_id: str

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning

    @model_validator(mode="after")
    def enforce_flexils(self):
        """Ensure that the Optical Node is a Nokia FlexILS."""
        if self.management.optical_module_node_vendor != Vendor.NOKIA:
            msg = f"Nokia FlexILS can only have vendor 'Nokia', got {self.management.optical_module_node_vendor}."
            raise ValueError(msg)
        if self.management.optical_module_node_platform != Platform.FLEXILS:
            msg = (
                f"Nokia FlexILS can only have platform 'FLEXILS', "
                f"got {self.management.optical_module_node_platform}."
            )
            raise ValueError(msg)
        return self


class NokiaFlexIlsBlock(
    NokiaFlexIlsBlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia FlexILS Optical Node that is active."""

    optical_node_role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER]
    optical_flexils_gmpls_id: IPAddress
    optical_flexils_target_id: str

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
