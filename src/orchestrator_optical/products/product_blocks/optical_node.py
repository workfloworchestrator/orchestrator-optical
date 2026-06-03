from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Discriminator, computed_field

from orchestrator_optical.products.product_blocks.optical_location import (
    OpticalLocation,
    OpticalLocationInactive,
    OpticalLocationProvisioning,
)
from orchestrator_optical.utils.custom_types.dns import Pqdn
from orchestrator_optical.utils.custom_types.ip_address import IPAddress

IpAddressesList = Annotated[
    list[IPAddress], Len(min_length=1, max_length=10), "List of the management IP addresses of the device."
]


class OpticalNodeRole(StrEnum):
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
    pqdn: Pqdn | None = None # without SLD and TLD, e.g. router01.roomA.siteB, not router01.roomA.siteB.domain.com
    role: OpticalNodeRole | None = None
    management_ips: IpAddressesList | None = None
    location: OpticalLocationInactive | None = None

    @computed_field
    @property
    def vendor_and_platform(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.vendor_and_platform


class OpticalNodeProvisioning(OpticalNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Base Product Block for Optical Nodes in provisioning state."""

    pqdn: Pqdn
    role: OpticalNodeRole
    management_ips: IpAddressesList
    location: OpticalLocationProvisioning


class OpticalNode(OpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Base Product Block for Optical Nodes in operational state."""

    sw_version: str
    location: OpticalLocation


# ============================================================================
# --- FlexILS Node Product Blocks ---
# ============================================================================


class NokiaFlexILSNodeInactive(OpticalNodeInactive, product_block_name="NokiaFlexILSNode"):
    location: OpticalLocationInactive | None = None
    role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER] | None = None
    gmpls_id: IPAddress | None = None
    target_id: str | None = None

class NokiaFlexILSNodeProvisioning(NokiaFlexILSNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    location: OpticalLocationProvisioning
    role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER]
    gmpls_id: IPAddress
    target_id: str

class NokiaFlexILSNode(NokiaFlexILSNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    location: OpticalLocation


# ============================================================================
# --- Discriminated Unions of Product Blocks ---
# ============================================================================

OpticalNodeUnion = Annotated[OpticalNode | NokiaFlexILSNode, Discriminator(lambda x: x.vendor_and_platform)]
OpticalNodeProvisioningUnion = Annotated[
    OpticalNodeProvisioning | NokiaFlexILSNodeProvisioning, Discriminator(lambda x: x.vendor_and_platform)
]
OpticalNodeInactiveUnion = Annotated[
    OpticalNodeInactive | NokiaFlexILSNodeInactive, Discriminator(lambda x: x.vendor_and_platform)
]
