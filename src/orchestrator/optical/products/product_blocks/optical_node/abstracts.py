"""Abstract implementation of Optical Node Product Blocks."""

from pydantic_forms.types import strEnum

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


class OpticalNodeRole(strEnum):
    """Roles of Optical Nodes."""

    ROADM = "ROADM"
    AMPLIFIER = "Amplifier"
    TRANSPONDER = "Transponder"
    TRANSPONDER_XOADM = "Transponder and xOADM"
    IPODWDM = "IPoDWDM"


class AbstractOpticalNodeBlockInactive(ProductBlockModel):
    """Abstract implementation of an Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive


class AbstractOpticalNodeBlockProvisioning(
    AbstractOpticalNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementaiton of an Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole | None = None

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class AbstractOpticalNodeBlock(AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Node."""

    optical_node_role: OpticalNodeRole

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
