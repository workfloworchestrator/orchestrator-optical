"""Union types for Optical Pipe Product Blocks."""

from typing import Annotated, Any

from pydantic import Discriminator, Tag

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_patch import (
    OpticalFiberPatchBlock,
    OpticalFiberPatchBlockInactive,
    OpticalFiberPatchBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import (
    OpticalFiberSpanBlock,
    OpticalFiberSpanBlockInactive,
    OpticalFiberSpanBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumBlock,
    OpticalLeasedSpectrumBlockInactive,
    OpticalLeasedSpectrumBlockProvisioning,
)


def _pipe_block_tag(block_type: type[ProductBlockModel]) -> str:
    """Return the ``product_block_name`` of a concrete pipe block class, to be used as a union tag."""
    assert block_type.name is not None  # noqa: S101
    return block_type.name


def _pipe_block_discriminator(value: Any) -> str | None:
    """Return the product block name of an optical pipe block.

    The discriminated input is either a serialized product block (dict, as produced by
    orchestrator-core on reload) or a product block model instance. In both cases the
    ``name`` field carries the ``product_block_name`` of the concrete block chain.

    Note that blocks must be constructed with ``new()``/``from_db()``: a plain pydantic
    constructor leaves ``name`` at the abstract base default, which matches no tag.
    """
    if isinstance(value, dict):
        return value.get("name")
    return getattr(value, "name", None)


OpticalPipeBlockUnion = Annotated[
    Annotated[OpticalFiberPatchBlock, Tag(_pipe_block_tag(OpticalFiberPatchBlock))]
    | Annotated[OpticalFiberSpanBlock, Tag(_pipe_block_tag(OpticalFiberSpanBlock))]
    | Annotated[OpticalLeasedSpectrumBlock, Tag(_pipe_block_tag(OpticalLeasedSpectrumBlock))],
    Discriminator(_pipe_block_discriminator),
]
OpticalPipeBlockUnionProvisioning = Annotated[
    Annotated[OpticalFiberPatchBlockProvisioning, Tag(_pipe_block_tag(OpticalFiberPatchBlockProvisioning))]
    | Annotated[OpticalFiberSpanBlockProvisioning, Tag(_pipe_block_tag(OpticalFiberSpanBlockProvisioning))]
    | Annotated[OpticalLeasedSpectrumBlockProvisioning, Tag(_pipe_block_tag(OpticalLeasedSpectrumBlockProvisioning))],
    Discriminator(_pipe_block_discriminator),
]
OpticalPipeBlockUnionInactive = Annotated[
    Annotated[OpticalFiberPatchBlockInactive, Tag(_pipe_block_tag(OpticalFiberPatchBlockInactive))]
    | Annotated[OpticalFiberSpanBlockInactive, Tag(_pipe_block_tag(OpticalFiberSpanBlockInactive))]
    | Annotated[OpticalLeasedSpectrumBlockInactive, Tag(_pipe_block_tag(OpticalLeasedSpectrumBlockInactive))],
    Discriminator(_pipe_block_discriminator),
]
