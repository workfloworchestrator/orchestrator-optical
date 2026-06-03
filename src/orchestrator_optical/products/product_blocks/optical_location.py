from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator_optical.utils.custom_types.dns import SubdomainPrefix
from orchestrator_optical.utils.custom_types.ip_address import IPAddress

IpAddressesList = Annotated[
    list[IPAddress], Len(min_length=1, max_length=10), "List of the management IP addresses of the device."
]


class OpticalLocationInactive(ProductBlockModel, product_block_name="OpticalLocation"):
    longitude: LongitudeCoordinate | None = None
    latitude: LatitudeCoordinate | None = None
    fqdn_subdomain: SubdomainPrefix | None = None

class OpticalLocationProvisioning(OpticalLocationInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    longitude: LongitudeCoordinate
    latitude: LatitudeCoordinate
    fqdn_subdomain: SubdomainPrefix

class OpticalLocation(OpticalLocationProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    pass


