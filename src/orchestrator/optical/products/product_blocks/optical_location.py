"""Abstract Product Blocks of an Optical Location."""

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator.optical.utils.custom_types.dns import SubdomainPrefix


class OpticalModuleLocationBlockInactive(ProductBlockModel, product_block_name="OpticalModuleLocationBlock"):
    """A Location that hosts optical equipment that is inactive."""

    longitude: LongitudeCoordinate | None = None
    latitude: LatitudeCoordinate | None = None
    fqdn_subdomain: SubdomainPrefix | None = None


class OpticalModuleLocationBlockProvisioning(
    OpticalModuleLocationBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Location that hosts optical equipment that is provisioning."""

    longitude: LongitudeCoordinate
    latitude: LatitudeCoordinate
    fqdn_subdomain: SubdomainPrefix


class OpticalModuleLocationBlock(OpticalModuleLocationBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """A Location that hosts optical equipment."""

    longitude: LongitudeCoordinate
    latitude: LatitudeCoordinate
    fqdn_subdomain: SubdomainPrefix
