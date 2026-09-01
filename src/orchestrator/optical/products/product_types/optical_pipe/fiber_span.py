"""Models for the subscriptions of Fiber Span Optical Pipes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import (
    OpticalFiberSpanBlock,
    OpticalFiberSpanBlockInactive,
    OpticalFiberSpanBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_pipe._abstracts import (
    _AbstractOpticalPipe,
    _AbstractOpticalPipeInactive,
    _AbstractOpticalPipeProvisioning,
)


class OpticalFiberSpanInactive(AbstractOpticalPipeInactive, is_base=True):
    """Base model for a fiber span subscription in the INACTIVE state."""

    optical_pipe: OpticalFiberSpanBlockInactive


class OpticalFiberSpanProvisioning(
    OpticalFiberSpanInactive, _AbstractOpticalPipeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Base model for a fiber span subscription in the PROVISIONING state."""

    optical_pipe: OpticalFiberSpanBlockProvisioning


class OpticalFiberSpan(OpticalFiberSpanProvisioning, _AbstractOpticalPipe, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Base model for a fiber span subscription in the ACTIVE state."""

    optical_pipe: OpticalFiberSpanBlock
