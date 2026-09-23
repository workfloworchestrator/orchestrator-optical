"""Abstract Product Types of an Optical Location."""

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)


class OpticalModuleLocationSubscriptionInactive(SubscriptionModel, is_base=True):
    """Abstract model of an Optical Location that is inactive."""

    optical_location: OpticalModuleLocationBlockInactive


class OpticalModuleLocationSubscriptionProvisioning(
    OpticalModuleLocationSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract model of an Optical Location that is provisioning."""

    optical_location: OpticalModuleLocationBlockProvisioning


class OpticalModuleLocationSubscription(
    OpticalModuleLocationSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Abstract model of an Optical Location that is active."""

    optical_location: OpticalModuleLocationBlock
