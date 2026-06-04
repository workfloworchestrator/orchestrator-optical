"""Optical Coherent Pluggables."""

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic_forms.types import strEnum

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    CoherentPluggableBlock,
    CoherentPluggableBlockInactive,
    CoherentPluggableBlockProvisioning,
)


class OpticalCoherentPluggablePartNumber(strEnum):
    """Enumerate supported optical device vendor and part numbers."""

    CISCO_QDD_400G_ZRP_S = "CISCO QDD-400G-ZRP-S"
    CISCO_DP04QSDD_HK9 = "CISCO DP04QSDD-HK9"


class OpticalCoherentPluggableInactive(SubscriptionModel, is_base=True):
    """TODO: Document."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlockInactive


class OpticalCoherentPluggableProvisioning(
    OpticalCoherentPluggableInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """TODO: Document."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlockProvisioning


class OpticalCoherentPluggable(
    OpticalCoherentPluggableProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """TODO: Document."""

    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber
    optical_coherent_pluggable: OpticalCoherentPluggableBlock
