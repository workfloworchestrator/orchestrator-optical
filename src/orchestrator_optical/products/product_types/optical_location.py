"""Abstract Product Types of an Optical Location."""

from orchestrator.domain import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)


class AbstractOpticalLocationInactive(SubscriptionModel, is_base=True):
    """Abstract model of an Optical Location that is inactive."""

    optical_location: AbstractOpticalLocationBlockInactive


class AbstractOpticalLocationProvisioning(
    AbstractOpticalLocationInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract model of an Optical Location that is provisioning."""

    optical_location: AbstractOpticalLocationBlockProvisioning


class AbstractOpticalLocation(AbstractOpticalLocationProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract model of an Optical Location that is active."""

    optical_location: AbstractOpticalLocationBlock
