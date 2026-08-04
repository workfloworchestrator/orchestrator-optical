"""Product Blocks of Nokia FlexILS Optical Nodes."""

from typing import Annotated

from annotated_types import Len
from pydantic import model_validator

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress

IpAddressList = Annotated[
    list[IPAddress], Len(min_length=0, max_length=10), "List of the management IP addresses of the device."
]

class NokiaFlexIlsBlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaFlexIlsBlock"):
    """Product Block of a Nokia FlexILS Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None
    optical_node_software_version: str | None = None
    pqdn: Pqdn | None = None
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlockInactive | None = None
    optical_flexils_gmpls_id: IPAddress | None = None
    optical_flexils_target_id: str | None = None


class NokiaFlexIlsBlockProvisioning(
    NokiaFlexIlsBlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia FlexILS Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str | None
    pqdn: Pqdn
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlockProvisioning
    optical_flexils_gmpls_id: IPAddress
    optical_flexils_target_id: str

    @model_validator(mode="after")
    def at_least_one_management_ip_or_loopback_ip(self) -> "NokiaFlexIlsBlockProvisioning":
        """Validate that at least one of the GMPLS ID or management IP is provided."""
        if not self.optical_flexils_gmpls_id and not self.optical_loopback_ip and not self.optical_management_ip:
            msg = "At least one of GMPLS ID or management IP must be provided."
            raise ValueError(msg)
        return self


class NokiaFlexIlsBlock(
    NokiaFlexIlsBlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia FlexILS Optical Node that is active."""

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str
    pqdn: Pqdn
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlock
    optical_flexils_gmpls_id: IPAddress
    optical_flexils_target_id: str

    @model_validator(mode="after")
    def at_least_one_management_ip_or_loopback_ip(self) -> "NokiaFlexIlsBlock":
        """Validate that at least one of the GMPLS ID or management IP is provided."""
        if not self.optical_flexils_gmpls_id and not self.optical_loopback_ip and not self.optical_management_ip:
            msg = "At least one of GMPLS ID or management IP must be provided."
            raise ValueError(msg)
        return self
