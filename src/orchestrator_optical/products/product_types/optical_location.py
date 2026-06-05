"""Abstract Product Types of an Optical Location."""

from orchestrator.domain import SubscriptionModel

from orchestrator_optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)


class AbstractOpticalLocationInactive(SubscriptionModel):
    """Abstract model of an Optical Location that is inactive."""

    optical_location: AbstractOpticalLocationBlockInactive


class AbstractOpticalLocationProvisioning(AbstractOpticalLocationInactive):
    """Abstract model of an Optical Location that is provisioning."""

    optical_location: AbstractOpticalLocationBlockProvisioning


class AbstractOpticalLocation(AbstractOpticalLocationProvisioning):
    """Abstract model of an Optical Location that is active."""

    optical_location: AbstractOpticalLocationBlock
