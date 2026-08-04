"""Abstract implementation of Optical Node Product Blocks."""

from pydantic import model_validator
from typing import Annotated

from annotated_types import Len
from pydantic import Field
from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress

IpAddressList = Annotated[
    list[IPAddress], Len(min_length=1, max_length=10), "List of the management IP addresses of the device."
]


class OpticalNodeRole(strEnum):
    """Roles of Optical Nodes."""

    ROADM = "ROADM"
    AMPLIFIER = "Amplifier"
    TRANSPONDER = "Transponder"
    TRANSPONDER_XOADM = "Transponder and xOADM"


class AbstractOpticalNodeBlockInactive(ProductBlockModel, product_block_name="AbstractOpticalNodeBlock"):
    """Abstract implementation of an Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None
    optical_node_software_version: str | None = None
    pqdn: Pqdn | None = None
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlockInactive | None = None


class AbstractOpticalNodeBlockProvisioning(
    AbstractOpticalNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementaiton of an Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str | None
    pqdn: Pqdn
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlockProvisioning

    @model_validator(mode="after")
    def at_least_one_management_ip_or_loopback_ip(self) -> "AbstractOpticalNodeBlockProvisioning":
        """Ensure that at least one of the management IP or loopback IP is provided."""
        if not self.optical_management_ip and not self.optical_loopback_ip:
            msg = "At least one of management IP or loopback IP must be provided."
            raise ValueError(msg)
        return self


class AbstractOpticalNodeBlock(AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Node.

    Attributes:
        optical_node_software_version: The currently installed software version on the Optical Node.
        pqdn: PQDN of the Optical Node, e.g. `router01.roomA.siteB`, excluding a global `domain.com` suffix.
        optical_management_ip: The management IP address of the Optical Node.
        optical_loopback_ip: The loopback IP address of the Optical Node.
        location: Location at which the Optical Node is hosted.
    """

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str
    pqdn: Pqdn
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlock

    @model_validator(mode="after")
    def at_least_one_management_ip_or_loopback_ip(self) -> "AbstractOpticalNodeBlock":
        """Ensure that at least one of the management IP or loopback IP is provided."""
        if not self.optical_management_ip and not self.optical_loopback_ip:
            msg = "At least one of management IP or loopback IP must be provided."
            raise ValueError(msg)
        return self
