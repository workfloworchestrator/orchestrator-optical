from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

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


class OpticalPacketNodeBlockInactive(ProductBlockModel, product_block_name="OpticalPacketNode"):
    """TODO: Document."""

    sw_version: str | None = None
    vendor_and_platform: str | None = None
    pqdn: Pqdn | None = None  # without SLD and TLD, e.g. router01.roomA.siteB, not router01.roomA.siteB.domain.com
    management_ips: IpAddressesList | None = None
    location: OpticalLocationBlockInactive

class OpticalPacketNodeBlockProvisioning(OpticalPacketNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    sw_version: str
    vendor_and_platform: str
    pqdn: Pqdn
    management_ips: IpAddressesList
    location: OpticalLocationBlockProvisioning

class OpticalPacketNodeBlock(OpticalPacketNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    location: OpticalLocationBlock
