"""Abstract implementations of Optical Pipe Product Blocks."""

from typing import Annotated

from annotated_types import Len

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    AnyOpticalPortBlock,
    AnyOpticalPortBlockInactive,
    AnyOpticalPortBlockProvisioning,
)

FiberSides = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


class _AbstractOpticalPipeBlockInactive(ProductBlockModel):
    """Abstract base class for all optical pipe blocks in the INACTIVE state."""

    optical_pipe_name: str | None = None
    optical_pipe_terminations: FiberSides[AnyOpticalPortBlockInactive] | None = None


class _AbstractOpticalPipeBlockProvisioning(
    _AbstractOpticalPipeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract base class for all optical pipe blocks in the PROVISIONING state."""

    optical_pipe_name: str | None
    optical_pipe_terminations: FiberSides[AnyOpticalPortBlockProvisioning]


class _AbstractOpticalPipeBlock(_AbstractOpticalPipeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base class for all optical pipe blocks in the ACTIVE state."""

    optical_pipe_name: str
    optical_pipe_terminations: FiberSides[AnyOpticalPortBlock]
