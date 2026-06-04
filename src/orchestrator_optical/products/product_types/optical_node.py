"""Models for the subscriptions of optical nodes."""

from enum import StrEnum
from typing import Annotated, Literal

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_node import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
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


# ── Abstract subscription (no is_base) — for generic workflow code ───────────
class AbstractOpticalNodeSubscriptionInactive(SubscriptionModel):
    vendor_and_platform: VendorAndPlatform
    node: AbstractOpticalNodeBlockInactive


class AbstractOpticalNodeSubscriptionProvisioning(AbstractOpticalNodeSubscriptionInactive):
    node: AbstractOpticalNodeBlockProvisioning


class AbstractOpticalNodeSubscription(AbstractOpticalNodeSubscriptionProvisioning):
    node: AbstractOpticalNodeBlock


# ── Concrete subscription for generic optical nodes ──────────────────────────────────
class OpticalNodeSubscriptionInactive(AbstractOpticalNodeSubscriptionInactive, is_base=True):
    vendor_and_platform: NotSpecializedPlatforms
    node: OpticalNodeBlockInactive


class OpticalNodeSubscriptionProvisioning(
    OpticalNodeSubscriptionInactive,
    AbstractOpticalNodeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    node: OpticalNodeBlockProvisioning


class OpticalNodeSubscription(
    OpticalNodeSubscriptionProvisioning, AbstractOpticalNodeSubscription, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    node: OpticalNodeBlock


# ── Concrete subscription for FlexILS ───────────────────────────────────────
class NokiaFlexILSNodeSubscriptionInactive(AbstractOpticalNodeSubscriptionInactive, is_base=True):
    vendor_and_platform: Literal[VendorAndPlatform.NOKIA_FLEXILS] = VendorAndPlatform.NOKIA_FLEXILS
    node: NokiaFlexILSNodeBlockInactive


class NokiaFlexILSNodeSubscriptionProvisioning(
    NokiaFlexILSNodeSubscriptionInactive,
    AbstractOpticalNodeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """base model for an optical node subscription in the PROVISIONING state."""

    node: NokiaFlexILSNodeBlockProvisioning


class NokiaFlexILSNodeSubscription(
    NokiaFlexILSNodeSubscriptionProvisioning, AbstractOpticalNodeSubscription, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """base model for an optical node subscription in the ACTIVE state."""

    node: NokiaFlexILSNodeBlock
