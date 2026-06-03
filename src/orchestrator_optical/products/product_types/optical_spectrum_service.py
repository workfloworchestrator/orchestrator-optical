"""Models for the optical spectrum service subscriptions."""

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

# relative because every org must copy this file to its local repo
from orchestrator_optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrum,
    OpticalSpectrumInactive,
    OpticalSpectrumProvisioning,
)


class OpticalSpectrumServiceSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for an optical spectrum service subscription in the INACTIVE state."""

    spectrum: OpticalSpectrumInactive


class OpticalSpectrumServiceSubscriptionProvisioning(
    OpticalSpectrumServiceSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an optical spectrum service subscription in the PROVISIONING state."""

    spectrum: OpticalSpectrumProvisioning


class OpticalSpectrumServiceSubscription(
    OpticalSpectrumServiceSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """base model for an optical spectrum service subscription in the ACTIVE state."""

    spectrum: OpticalSpectrum


