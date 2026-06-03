from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Discriminator, computed_field

from orchestrator_optical.products.product_blocks.optical_location import (
    OpticalLocationBlock,
    OpticalLocationInactive,
    OpticalLocationProvisioning,
)
from orchestrator_optical.utils.custom_types.fqdn import Fqdn
from orchestrator_optical.utils.custom_types.ip_address import IPAddress

IpAddressesList = Annotated[
    list[IPAddress], Len(min_length=1, max_length=10), "List of the management IP addresses of the device."
]


class NodeRole(StrEnum):
    """Device type based on its functionalities. Since chasses are modular, the type can change during device's life."""

    ROADM = "ROADM"
    AMPLIFIER = "Amplifier"
    TRANSPONDER = "Transponder"
    TRANSPONDER_XOADM = "Transponder and xOADM"


# ============================================================================
# --- Base Optical Node Product Blocks ---
# ============================================================================


class OpticalNodeInactive(ProductBlockModel, product_block_name="OpticalNode"):
    """Base Product Block for Optical Nodes."""

    sw_version: str | None = None
    fqdn: Fqdn | None = None
    role: NodeRole | None = None
    management_ips: IpAddressesList | None = None
    location: OpticalLocationInactive | None = None

    @computed_field
    @property
    def vendor_platform(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.vendor_platform


class OpticalNodeProvisioning(OpticalNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Base Product Block for Optical Nodes in provisioning state."""

    fqdn: Fqdn
    role: NodeRole
    management_ips: IpAddressesList
    location: OpticalLocationProvisioning


class OpticalNode(OpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Base Product Block for Optical Nodes in operational state."""

    sw_version: str
    location: OpticalLocationBlock


# ============================================================================
# --- FlexILS Node Product Blocks ---
# ============================================================================


class NokiaFlexILSNodeInactive(OpticalNodeInactive, product_block_name="NokiaFlexILSNode"):
    location: OpticalLocationInactive | None = None
    role: Literal[NodeRole.ROADM, NodeRole.AMPLIFIER] | None = None
    gmpls_id: IPAddress | None = None


class NokiaFlexILSNodeProvisioning(NokiaFlexILSNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    location: OpticalLocationProvisioning
    role: Literal[NodeRole.ROADM, NodeRole.AMPLIFIER]
    gmpls_id: IPAddress


class NokiaFlexILSNode(NokiaFlexILSNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    location: OpticalLocationBlock


# ============================================================================
# --- Discriminated Unions of Product Blocks ---
# ============================================================================

Node = Annotated[OpticalNodeBlock | NokiaFlexILSNodeBlock, Discriminator(lambda x: x.vendor_platform)]
NodeProvisioning = Annotated[
    OpticalNodeProvisioning | NokiaFlexILSNodeProvisioning, Discriminator(lambda x: x.vendor_platform)
]
NodeInactive = Annotated[
    OpticalNodeInactive | NokiaFlexILSNodeInactive, Discriminator(lambda x: x.vendor_platform)
]
