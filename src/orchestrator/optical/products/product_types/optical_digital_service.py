"""Models for optical digital service subscriptions."""

from enum import IntEnum

from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_digital_service import (
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


class OpticalDigitalServiceInactive(SubscriptionModel, is_base=True):
    """An Optical Digital service that is inactive."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlockInactive


class OpticalDigitalServiceProvisioning(OpticalDigitalServiceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """An Optical Digital service that is provisioning."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlockProvisioning


class OpticalDigitalService(OpticalDigitalServiceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """An Optical Digital service that is active."""

    optical_digital_service_speed: OpticalDigitalServiceSpeed
    optical_digital_service_type: OpticalDigitalServiceType
    optical_digital_service: OpticalDigitalServiceBlock
