from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)
from orchestrator_optical.utils.custom_types.dns import Pqdn
from orchestrator_optical.utils.custom_types.ip_address import IPAddress

IpAddressesList = Annotated[
    list[IPAddress], Len(min_length=1, max_length=10), "List of the management IP addresses of the device."
]


class AbstractOpticalPacketNodeBlockInactive(ProductBlockModel):
    """A packet layer Node that accepts Optical Coherent Pluggables that is inactive."""

    optical_packet_node_software_version: str | None = None
    optical_packet_node_vendor_and_platform: str | None = None
    pqdn: Pqdn | None = None  # without SLD and TLD, e.g. router01.roomA.siteB, not router01.roomA.siteB.domain.com
    optical_packet_node_management_ips: IpAddressesList | None = None
    location: AbstractOpticalLocationBlockInactive


class AbstractOpticalPacketNodeBlockProvisioning(
    AbstractOpticalPacketNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A packet layer Node that accepts Optical Coherent Pluggables that is provisioning."""

    optical_packet_node_software_version: str
    optical_packet_node_vendor_and_platform: str
    pqdn: Pqdn
    optical_packet_node_management_ips: IpAddressesList
    location: AbstractOpticalLocationBlockProvisioning


class AbstractOpticalPacketNodeBlock(
    AbstractOpticalPacketNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """A packet layer Node that accepts Optical Coherent Pluggables."""

    optical_packet_node_software_version: str
    optical_packet_node_vendor_and_platform: str
    pqdn: Pqdn
    optical_packet_node_management_ips: IpAddressesList
    location: AbstractOpticalLocationBlock
