"""Abstract implementations of Optical Pipe Product Blocks."""

from typing import Annotated

from annotated_types import Len

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalPortBlock,
    AbstractOpticalPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
)

FiberSides = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


class AbstractOpticalPipeBlockInactive(ProductBlockModel, product_block_name="AbstractOpticalPipeBlock"):
    """Abstract base class for all optical pipe blocks in the INACTIVE state."""

    optical_pipe_identifier: str | None = None
    optical_pipe_terminations: FiberSides[AbstractOpticalPortBlockInactive]


class AbstractOpticalPipeBlockProvisioning(
    AbstractOpticalPipeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract base class for all optical pipe blocks in the PROVISIONING state."""

    optical_pipe_identifier: str | None
    optical_pipe_terminations: FiberSides[AbstractOpticalPortBlockProvisioning]


class AbstractOpticalPipeBlock(AbstractOpticalPipeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base class for all optical pipe blocks in the ACTIVE state."""

    optical_pipe_identifier: str
    optical_pipe_terminations: FiberSides[AbstractOpticalPortBlock]
