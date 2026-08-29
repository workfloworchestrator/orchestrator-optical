"""Unions for Optical Node Product Blocks.

These are plain (non-discriminated) unions. A field-based discriminator is impossible here
because the vendor role literals overlap (Groove G30 and GX G42 both allow ``TRANSPONDER``),
and pydantic's function discriminators require ``Tag``-wrapped members.

They must stay plain unions: orchestrator-core's field classifier (``is_union_type`` in
``orchestrator.core.types``) cannot see through ``Annotated``-wrapped members, and would
persist single-reference fields of such unions (e.g. ``optical_port_host_node``) as plain
strings instead of product block references.

Pydantic resolves these unions unambiguously via each member's ``optical_node_role`` literal
plus the ``enforce_*`` vendor/platform model validators defined on every lifecycle class.
"""

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

AnyOpticalNodeBlockInactiveUnion = NokiaFlexIlsBlockInactive | NokiaGrooveG30BlockInactive | NokiaGxG42BlockInactive
AnyOpticalNodeBlockProvisioningUnion = (
    NokiaFlexIlsBlockProvisioning | NokiaGrooveG30BlockProvisioning | NokiaGxG42BlockProvisioning
)
AnyOpticalNodeBlockUnion = NokiaFlexIlsBlock | NokiaGrooveG30Block | NokiaGxG42Block

OlsBlockInactiveUnion = NokiaFlexIlsBlockInactive | NokiaGrooveG30BlockInactive
OlsBlockProvisioningUnion = NokiaFlexIlsBlockProvisioning | NokiaGrooveG30BlockProvisioning
OlsBlockUnion = NokiaFlexIlsBlock | NokiaGrooveG30Block

TransponderBlockInactiveUnion = NokiaGrooveG30BlockInactive | NokiaGxG42BlockInactive
TransponderBlockProvisioningUnion = NokiaGrooveG30BlockProvisioning | NokiaGxG42BlockProvisioning
TransponderBlockUnion = NokiaGrooveG30Block | NokiaGxG42Block
