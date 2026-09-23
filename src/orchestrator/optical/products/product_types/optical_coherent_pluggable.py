"""Optical Coherent Pluggables."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
    OpticalCoherentPluggablePartNumber,
)


class OpticalCoherentPluggableSubscriptionInactive(SubscriptionModel, is_base=True):
    """An Optical Coherent Pluggable that is inactive."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlockInactive


class OpticalCoherentPluggableSubscriptionProvisioning(
    OpticalCoherentPluggableSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """An Optical Coherent Pluggable that is provisioning."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlockProvisioning


class OpticalCoherentPluggableSubscription(
    OpticalCoherentPluggableSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """An Optical Coherent Pluggable that is active."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlock
