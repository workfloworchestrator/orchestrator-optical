"""Models for the subscriptions of Fiber Patch Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_patch import (
    OpticalFiberPatchBlock,
    OpticalFiberPatchBlockInactive,
    OpticalFiberPatchBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_pipe.abstracts import (
    AbstractOpticalPipeSubscription,
    AbstractOpticalPipeSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
)


class OpticalFiberPatchSubscriptionInactive(AbstractOpticalPipeSubscriptionInactive, is_base=True):
    """Base model for an internal fiber patch subscription in the INACTIVE state."""

    optical_pipe: OpticalFiberPatchBlockInactive


class OpticalFiberPatchSubscriptionProvisioning(
    OpticalFiberPatchSubscriptionInactive,
    AbstractOpticalPipeSubscriptionProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base model for an internal fiber patch subscription in the PROVISIONING state."""

    optical_pipe: OpticalFiberPatchBlockProvisioning


class OpticalFiberPatchSubscription(
    OpticalFiberPatchSubscriptionProvisioning, AbstractOpticalPipeSubscription, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base model for an internal fiber patch subscription in the ACTIVE state."""

    optical_pipe: OpticalFiberPatchBlock
