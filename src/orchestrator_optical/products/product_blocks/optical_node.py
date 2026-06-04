from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Discriminator, computed_field

from orchestrator_optical.products.product_blocks.optical_location import (
    OpticalLocationBlock,
    OpticalLocationBlockInactive,
    OpticalLocationBlockProvisioning,
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


# ── Abstract block (no product_block_name) ──────────────────────────────────
class AbstractOpticalNodeBlockInactive(ProductBlockModel):
    sw_version: str | None = None
    pqdn: Pqdn | None = None  # without SLD and TLD, e.g. router01.roomA.siteB, not router01.roomA.siteB.domain.com
    role: OpticalNodeRole | None = None
    management_ips: IpAddressesList | None = None
    location: OpticalLocationBlockInactive | None = None

    @computed_field
    @property
    def vendor_and_platform(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.vendor_and_platform


class AbstractOpticalNodeBlockProvisioning(
    AbstractOpticalNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    pqdn: Pqdn # without SLD and TLD, e.g. router01.roomA.siteB, not router01.roomA.siteB.domain.com
    role: OpticalNodeRole
    management_ips: IpAddressesList
    location: OpticalLocationBlockProvisioning


class AbstractOpticalNodeBlock(AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    sw_version: str
    location: OpticalLocationBlock


# ── Concrete generic block ───────────────────────────────────────────────────
class OpticalNodeBlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="OpticalNode"):
    location: OpticalLocationBlockInactive | None = None



class OpticalNodeBlockProvisioning(
    OpticalNodeBlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    location: OpticalLocationBlockProvisioning



class OpticalNodeBlock(
    OpticalNodeBlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    location: OpticalLocationBlock


# ── Concrete FlexILS block (adds specialized fields) ────────────────────────────────────
class NokiaFlexILSNodeBlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaFlexILSNode"):
    role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER] | None = None
    gmpls_id: IPAddress | None = None
    target_id: str | None = None
    location: OpticalLocationBlockInactive | None = None



class NokiaFlexILSNodeBlockProvisioning(
    NokiaFlexILSNodeBlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    role: Literal[OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER]
    gmpls_id: IPAddress
    target_id: str
    location: OpticalLocationBlockProvisioning


class NokiaFlexILSNodeBlock(
    NokiaFlexILSNodeBlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    location: OpticalLocationBlock


# ── Discriminated Unions ────────────────────────────────────
OpticalNodeBlockUnion = Annotated[
    OpticalNodeBlock | NokiaFlexILSNodeBlock, Discriminator(lambda x: x.vendor_and_platform)
]
OpticalNodeBlockUnionProvisioning = Annotated[
    OpticalNodeBlockProvisioning | NokiaFlexILSNodeBlockProvisioning, Discriminator(lambda x: x.vendor_and_platform)
]
OpticalNodeBlockUnionInactive = Annotated[
    OpticalNodeBlockInactive | NokiaFlexILSNodeBlockInactive, Discriminator(lambda x: x.vendor_and_platform)
]
