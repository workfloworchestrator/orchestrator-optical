from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

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


class OpticalPacketNodeInactive(ProductBlockModel, product_block_name="OpticalPacketNode"):
    sw_version: str | None = None
    vendor_platform: str | None = None
    fqdn: Fqdn | None = None
    management_ips: IpAddressesList | None = None
    location: OpticalLocationInactive

class OpticalPacketNodeProvisioning(OpticalPacketNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    sw_version: str
    vendor_platform: str
    fqdn: Fqdn
    management_ips: IpAddressesList
    location: OpticalLocationProvisioning

class OpticalPacketNode(OpticalPacketNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    location: OpticalLocationBlock
