"""Models for optical digital service subscriptions."""

from enum import IntEnum

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic_forms.types import strEnum

from orchestrator_optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlock,
    OpticalDigitalServiceBlockInactive,
    OpticalDigitalServiceBlockProvisioning,
)


class OpticalDigitalServiceSpeed(IntEnum):
    """Speed of an optical port in Gbit/s."""

    _100 = 100
    _400 = 400
    _800 = 800


class OpticalDigitalServiceType(strEnum):
    """Supported digital service framing protocol types."""

    ETHERNET = "Ethernet"


# --- Subscription Lifecycles ---


class OpticalDigitalServiceInactive(SubscriptionModel, is_base=True):
    """base model for an optical digital service subscription in the INACTIVE state."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlockInactive


class OpticalDigitalServiceProvisioning(OpticalDigitalServiceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """base model for an optical digital service subscription in the PROVISIONING state."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlockProvisioning


class OpticalDigitalService(OpticalDigitalServiceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """base model for an optical digital service subscription in the ACTIVE state."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlock
