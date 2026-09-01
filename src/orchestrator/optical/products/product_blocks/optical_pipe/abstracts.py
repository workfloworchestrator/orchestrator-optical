"""Abstract implementations of Optical Pipe Product Blocks."""

from typing import Annotated

from annotated_types import Len
from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    AnyOpticalPortBlock,
    AnyOpticalPortBlockInactive,
    AnyOpticalPortBlockProvisioning,
)

FiberSides = Annotated[list[SI], Len(min_length=2, max_length=2), "List of the 2 ports connected by the fiber."]


class OpticalPipeType(strEnum):
    """The Type of the Optical Pipe."""

    PATCH = "Patch"
    SPAN = "Span"
    LEASED_SPECTRUM = "Leased Spectrum"

class AbstractOpticalPipeBlockInactive(ProductBlockModel):
    """Abstract base class for all optical pipe blocks in the INACTIVE state."""
    # this is needed because the orchestrator-core source code does not fully support Pydantic Discriminated Unions
    # that is Annotated[X | Y, discriminator=] is serialized to str repr because of the Annotated type. Thus, we have to
    # use strEnum to ensure the correct Block is loaded from the DB
    optical_pipe_type: OpticalPipeType 
    optical_pipe_name: str | None = None
    optical_pipe_terminations: FiberSides[AnyOpticalPortBlockInactive] | None = None


class AbstractOpticalPipeBlockProvisioning(
    AbstractOpticalPipeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract base class for all optical pipe blocks in the PROVISIONING state."""

    optical_pipe_type: OpticalPipeType
    optical_pipe_name: str | None
    optical_pipe_terminations: FiberSides[AnyOpticalPortBlockProvisioning]


class AbstractOpticalPipeBlock(AbstractOpticalPipeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract base class for all optical pipe blocks in the ACTIVE state."""

    optical_pipe_type: OpticalPipeType
    optical_pipe_name: str
    optical_pipe_terminations: FiberSides[AnyOpticalPortBlock]
