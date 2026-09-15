"""Models for optical digital service subscriptions."""

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlock,
    OpticalDigitalServiceBlockInactive,
    OpticalDigitalServiceBlockProvisioning,
    OpticalDigitalServiceSpeed,
    OpticalDigitalServiceType,
)


class OpticalDigitalServiceSubscriptionInactive(SubscriptionModel, is_base=True):
    """An Optical Digital service that is inactive."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlockInactive


class OpticalDigitalServiceSubscriptionProvisioning(
    OpticalDigitalServiceSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """An Optical Digital service that is provisioning."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlockProvisioning


class OpticalDigitalServiceSubscription(
    OpticalDigitalServiceSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """An Optical Digital service that is active."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlock
