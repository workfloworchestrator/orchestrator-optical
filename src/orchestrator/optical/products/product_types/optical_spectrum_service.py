"""Models for the optical spectrum service subscriptions."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumServiceBlock,
    OpticalSpectrumServiceBlockInactive,
    OpticalSpectrumServiceBlockProvisioning,
)


class OpticalSpectrumServiceSubscriptionInactive(SubscriptionModel, is_base=True):
    """An optical spectrum service subscription in the INACTIVE state."""

    optical_spectrum_service: OpticalSpectrumServiceBlockInactive


class OpticalSpectrumServiceSubscriptionProvisioning(
    OpticalSpectrumServiceSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """An optical spectrum service subscription in the PROVISIONING state."""

    optical_spectrum_service: OpticalSpectrumServiceBlockProvisioning


class OpticalSpectrumServiceSubscription(
    OpticalSpectrumServiceSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """An optical spectrum service subscription in the ACTIVE state."""

    optical_spectrum_service: OpticalSpectrumServiceBlock
