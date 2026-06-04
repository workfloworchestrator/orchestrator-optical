"""Models for the subscriptions of optical nodes."""

from enum import StrEnum
from typing import Literal

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

# relative because every org must copy this file to its local repo
from orchestrator_optical.products.product_blocks.optical_node import (
    NokiaFlexILSNodeBlock,
    NokiaFlexILSNodeBlockInactive,
    NokiaFlexILSNodeBlockProvisioning,
    OpticalNodeBlock,
    OpticalNodeBlockInactive,
    OpticalNodeBlockProvisioning,
)


class VendorAndPlatform(StrEnum):
    """Enumerate supported optical device vendor and models."""

    NOKIA_GROOVE_G30 = "Nokia Groove G30"
    NOKIA_GX_G42 = "Nokia GX G42"
    NOKIA_FLEXILS = "Nokia FlexILS"

NotSpecializedPlatforms = Literal[VendorAndPlatform.NOKIA_GROOVE_G30, VendorAndPlatform.NOKIA_GX_G42]

# --- Generic Optical Node Subscriptions ---


class OpticalNodeSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for an optical node subscription in the INACTIVE state."""

    vendor_and_platform: NotSpecializedPlatforms
    node: OpticalNodeBlockInactive


class OpticalNodeSubscriptionProvisioning(
    OpticalNodeSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an optical node subscription in the PROVISIONING state."""

    vendor_and_platform: NotSpecializedPlatforms
    node: OpticalNodeBlockProvisioning


class OpticalNodeSubscription(
    OpticalNodeSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for an optical node subscription in the ACTIVE state."""

    vendor_and_platform: NotSpecializedPlatforms
    node: OpticalNodeBlock


# --- Nokia FlexILS Specialized Subscriptions ---


class NokiaFlexILSNodeSubscriptionInactive(SubscriptionModel, is_base=True):
    """base model for an optical node subscription in the INACTIVE state."""

    vendor_and_platform: Literal[VendorAndPlatform.NOKIA_FLEXILS] = VendorAndPlatform.NOKIA_FLEXILS
    node: NokiaFlexILSNodeBlockInactive


class NokiaFlexILSNodeSubscriptionProvisioning(
    NokiaFlexILSNodeSubscriptionInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an optical node subscription in the PROVISIONING state."""

    node: NokiaFlexILSNodeBlockProvisioning


class NokiaFlexILSNodeSubscription(
    NokiaFlexILSNodeSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for an optical node subscription in the ACTIVE state."""

    node: NokiaFlexILSNodeBlock


