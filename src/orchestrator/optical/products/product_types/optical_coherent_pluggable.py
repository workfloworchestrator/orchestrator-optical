"""Optical Coherent Pluggables."""

from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)


class OpticalCoherentPluggablePartNumber(strEnum):
    """Enumerate supported optical device vendor and part numbers."""

    CISCO_QDD_400G_ZRP_S = "CISCO QDD-400G-ZRP-S"
    CISCO_DP04QSDD_HK9 = "CISCO DP04QSDD-HK9"


class OpticalCoherentPluggableInactive(SubscriptionModel, is_base=True):
    """An Optical Coherent Pluggable that is inactive."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlockInactive


class OpticalCoherentPluggableProvisioning(
    OpticalCoherentPluggableInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """An Optical Coherent Pluggable that is provisioning."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlockProvisioning


class OpticalCoherentPluggable(OpticalCoherentPluggableProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """An Optical Coherent Pluggable that is active."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlock
