"""Unions for Optical Node Product Blocks."""

from typing import Annotated, Any

from pydantic import Discriminator, Tag

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30Block,
    NokiaGrooveG30BlockInactive,
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import (
    NokiaGxG42Block,
    NokiaGxG42BlockInactive,
    NokiaGxG42BlockProvisioning,
)


def _node_block_tag(block_type: type[ProductBlockModel]) -> str:
    """Return the ``product_block_name`` of a concrete node block class, to be used as a union tag."""
    assert block_type.name is not None  # noqa: S101
    return block_type.name


def _node_block_discriminator(value: Any) -> str | None:
    """Return the product block name of an optical node block.

    The discriminated input is either a serialized product block (dict, as produced by
    orchestrator-core on reload) or a product block model instance. In both cases the
    ``name`` field carries the ``product_block_name`` of the concrete block chain.

    Note that blocks must be constructed with ``new()``/``from_db()``: a plain pydantic
    constructor leaves ``name`` at the abstract base default, which matches no tag.
    """
    if isinstance(value, dict):
        return value.get("name")
    return getattr(value, "name", None)


AnyOpticalNodeBlockInactiveUnion = Annotated[
    Annotated[NokiaFlexIlsBlockInactive, Tag(_node_block_tag(NokiaFlexIlsBlockInactive))]
    | Annotated[NokiaGrooveG30BlockInactive, Tag(_node_block_tag(NokiaGrooveG30BlockInactive))]
    | Annotated[NokiaGxG42BlockInactive, Tag(_node_block_tag(NokiaGxG42BlockInactive))],
    Discriminator(_node_block_discriminator),
]
AnyOpticalNodeBlockProvisioningUnion = Annotated[
    Annotated[NokiaFlexIlsBlockProvisioning, Tag(_node_block_tag(NokiaFlexIlsBlockProvisioning))]
    | Annotated[NokiaGrooveG30BlockProvisioning, Tag(_node_block_tag(NokiaGrooveG30BlockProvisioning))]
    | Annotated[NokiaGxG42BlockProvisioning, Tag(_node_block_tag(NokiaGxG42BlockProvisioning))],
    Discriminator(_node_block_discriminator),
]
AnyOpticalNodeBlockUnion = Annotated[
    Annotated[NokiaFlexIlsBlock, Tag(_node_block_tag(NokiaFlexIlsBlock))]
    | Annotated[NokiaGrooveG30Block, Tag(_node_block_tag(NokiaGrooveG30Block))]
    | Annotated[NokiaGxG42Block, Tag(_node_block_tag(NokiaGxG42Block))],
    Discriminator(_node_block_discriminator),
]

OlsBlockInactiveUnion = Annotated[
    Annotated[NokiaFlexIlsBlockInactive, Tag(_node_block_tag(NokiaFlexIlsBlockInactive))]
    | Annotated[NokiaGrooveG30BlockInactive, Tag(_node_block_tag(NokiaGrooveG30BlockInactive))],
    Discriminator(_node_block_discriminator),
]
OlsBlockProvisioningUnion = Annotated[
    Annotated[NokiaFlexIlsBlockProvisioning, Tag(_node_block_tag(NokiaFlexIlsBlockProvisioning))]
    | Annotated[NokiaGrooveG30BlockProvisioning, Tag(_node_block_tag(NokiaGrooveG30BlockProvisioning))],
    Discriminator(_node_block_discriminator),
]
OlsBlockUnion = Annotated[
    Annotated[NokiaFlexIlsBlock, Tag(_node_block_tag(NokiaFlexIlsBlock))]
    | Annotated[NokiaGrooveG30Block, Tag(_node_block_tag(NokiaGrooveG30Block))],
    Discriminator(_node_block_discriminator),
]

TransponderBlockInactiveUnion = Annotated[
    Annotated[NokiaGrooveG30BlockInactive, Tag(_node_block_tag(NokiaGrooveG30BlockInactive))]
    | Annotated[NokiaGxG42BlockInactive, Tag(_node_block_tag(NokiaGxG42BlockInactive))],
    Discriminator(_node_block_discriminator),
]
TransponderBlockProvisioningUnion = Annotated[
    Annotated[NokiaGrooveG30BlockProvisioning, Tag(_node_block_tag(NokiaGrooveG30BlockProvisioning))]
    | Annotated[NokiaGxG42BlockProvisioning, Tag(_node_block_tag(NokiaGxG42BlockProvisioning))],
    Discriminator(_node_block_discriminator),
]
TransponderBlockUnion = Annotated[
    Annotated[NokiaGrooveG30Block, Tag(_node_block_tag(NokiaGrooveG30Block))]
    | Annotated[NokiaGxG42Block, Tag(_node_block_tag(NokiaGxG42Block))],
    Discriminator(_node_block_discriminator),
]
