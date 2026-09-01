"""Abstract Product Blocks of an Optical Location."""

import re
from typing import Annotated

from pydantic import AfterValidator

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate

_CODE_PATTERN = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")


def _validate_location_code(v: str) -> str:
    if not isinstance(v, str):
        msg = "Location code must be a string"
        raise TypeError(msg)
    if not 1 <= len(v) <= 63:
        msg = "Location code must be between 1 and 63 characters"
        raise ValueError(msg)
    if not _CODE_PATTERN.fullmatch(v):
        msg = "must be a valid location code: lowercase alphanumeric + hyphens, must start and end with alphanumeric"
        raise ValueError(msg)
    return v


LocationCode = Annotated[str, AfterValidator(_validate_location_code)]


class OpticalModuleLocationBlockInactive(ProductBlockModel, product_block_name="OpticalModuleLocationBlock"):
    """A Location that hosts optical equipment that is inactive."""

    longitude: LongitudeCoordinate | None = None
    latitude: LatitudeCoordinate | None = None
    location_code: LocationCode | None = None
    location_name: str | None = None


class OpticalModuleLocationBlockProvisioning(
    OpticalModuleLocationBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Location that hosts optical equipment that is provisioning."""

    longitude: LongitudeCoordinate
    latitude: LatitudeCoordinate
    location_code: LocationCode
    location_name: str | None = None


class OpticalModuleLocationBlock(OpticalModuleLocationBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """A Location that hosts optical equipment."""

    longitude: LongitudeCoordinate
    latitude: LatitudeCoordinate
    location_code: LocationCode
    location_name: str | None = None
