"""."""

from enum import StrEnum

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_coherent_pluggable import (
    CoherentPluggableBlock,
    CoherentPluggableBlockInactive,
    CoherentPluggableBlockProvisioning,
)


class VendorAndPartNo(StrEnum):
    """Enumerate supported optical device vendor and part numbers."""

    CISCO_QDD_400G_ZRP_S = "CISCO QDD-400G-ZRP-S"
    CISCO_DP04QSDD_HK9 = "CISCO DP04QSDD-HK9"


class CoherentPluggableSubscriptionInactive(SubscriptionModel, is_base=True):
    vendor_and_part_no: VendorAndPartNo
    transceiver: CoherentPluggableBlockInactive


class CoherentPluggableSubscriptionProvisioning(
    CoherentPluggableSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    vendor_and_part_no: VendorAndPartNo
    transceiver: CoherentPluggableBlockProvisioning


class CoherentPluggableSubscription(
    CoherentPluggableSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    vendor_and_part_no: VendorAndPartNo
    transceiver: CoherentPluggableBlock


