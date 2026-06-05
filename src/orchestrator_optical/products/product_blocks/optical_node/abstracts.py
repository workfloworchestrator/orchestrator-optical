"""Abstract implementation of Optical Node Product Blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field
from pydantic_forms.types import strEnum

from orchestrator_optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)
from orchestrator_optical.utils.custom_types.dns import Pqdn
from orchestrator_optical.utils.custom_types.ip_address import IPAddress

IpAddressList = Annotated[
    list[IPAddress], Len(min_length=1, max_length=10), "List of the management IP addresses of the device."
]


class OpticalNodeRole(strEnum):
    """Roles of Optical Nodes."""

    ROADM = "ROADM"
    AMPLIFIER = "Amplifier"
    TRANSPONDER = "Transponder"
    TRANSPONDER_XOADM = "Transponder and xOADM"


class AbstractOpticalNodeBlockInactive(ProductBlockModel):
    """Abstract implementation of an Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None
    optical_node_software_version: str | None = None
    pqdn: Pqdn | None = None
    optical_management_ip_list: IpAddressList = Field(default_factory=list)
    location: AbstractOpticalLocationBlockInactive | None = None


class AbstractOpticalNodeBlockProvisioning(
    AbstractOpticalNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementaiton of an Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str | None
    pqdn: Pqdn
    optical_management_ip_list: IpAddressList
    location: AbstractOpticalLocationBlockProvisioning


class AbstractOpticalNodeBlock(AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Node.

    Attributes:
        optical_node_software_version: The currently installed software version on the Optical Node.
        pqdn: PQDN of the Optical Node, e.g. `router01.roomA.siteB`, excluding a global `domain.com` suffix.
        optical_management_ip_list: List of IP addresses for management of the Optical Node.
        location: Location at which the Optical Node is hosted.
    """

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str
    pqdn: Pqdn
    optical_management_ip_list: IpAddressList
    location: AbstractOpticalLocationBlock
