"""Models for optical digital service subscriptions."""

from enum import StrEnum

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlock,
    OpticalDigitalServiceBlockInactive,
    OpticalDigitalServiceBlockProvisioning,
)


class ServiceSpeed(StrEnum):
    """Enumerate supported digital service line rates."""

    SPEED_100G = "100Gbps"
    SPEED_400G = "400Gbps"
    SPEED_800G = "800Gbps"


class ServiceType(StrEnum):
    """Enumerate supported digital service framing protocol types."""

    ETHERNET = "Ethernet"


# --- Subscription Lifecycles ---


class OpticalDigitalServiceSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for an optical digital service subscription in the INACTIVE state."""

    service_speed: ServiceSpeed
    service_type: ServiceType
    service: OpticalDigitalServiceBlockInactive


class OpticalDigitalServiceSubscriptionProvisioning(
    OpticalDigitalServiceSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an optical digital service subscription in the PROVISIONING state."""

    service: OpticalDigitalServiceBlockProvisioning


class OpticalDigitalServiceSubscription(
    OpticalDigitalServiceSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    """base model for an optical digital service subscription in the ACTIVE state."""

    service: OpticalDigitalServiceBlock


