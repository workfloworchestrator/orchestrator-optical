"""Models for the optical spectrum service subscriptions."""

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlock,
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)


class OpticalSpectrumServiceInactive(SubscriptionModel, is_base=True):
    """An optical spectrum service subscription in the INACTIVE state."""

    optical_spectrum_service: OpticalSpectrumBlockInactive


class OpticalSpectrumServiceProvisioning(
    OpticalSpectrumServiceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """An optical spectrum service subscription in the PROVISIONING state."""

    optical_spectrum_service: OpticalSpectrumBlockProvisioning


class OpticalSpectrumService(OpticalSpectrumServiceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """An optical spectrum service subscription in the ACTIVE state."""

    optical_spectrum_service: OpticalSpectrumBlock
