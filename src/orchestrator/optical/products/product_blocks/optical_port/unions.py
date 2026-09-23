"""Union types for Optical Port Product Blocks.

These are plain (non-discriminated) unions. Pydantic resolves them unambiguously because every
member pins a distinct ``optical_port_role: Literal[...]`` value.

They must stay plain unions: orchestrator-core's field classifier (``is_list_type``/
``is_union_type`` in ``orchestrator.core.types``) cannot see through ``Annotated``-wrapped
discriminated unions, and would persist list fields of such unions (e.g. optical pipe
terminations) as plain strings instead of nested product block references.
"""

from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_line import (
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlock,
    OpticalTransponderClientPortBlockInactive,
    OpticalTransponderClientPortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_line import (
    OpticalTransponderLinePortBlock,
    OpticalTransponderLinePortBlockInactive,
    OpticalTransponderLinePortBlockProvisioning,
)

AnyOpticalPortBlockInactive = (
    OpticalTransponderClientPortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive
)
AnyOpticalPortBlockProvisioning = (
    OpticalTransponderClientPortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning
)
AnyOpticalPortBlock = (
    OpticalTransponderClientPortBlock
    | OpticalTransponderLinePortBlock
    | OlsAddDropPortBlock
    | OlsLinePortBlock
    | OpticalCoherentPluggableBlock
)

PatchPortBlockInactive = (
    OpticalTransponderClientPortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OpticalCoherentPluggableBlockInactive
)
PatchPortBlockProvisioning = (
    OpticalTransponderClientPortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning
)
PatchPortBlock = (
    OpticalTransponderClientPortBlock
    | OpticalTransponderLinePortBlock
    | OlsAddDropPortBlock
    | OpticalCoherentPluggableBlock
)

SpanPortBlockInactive = (
    OlsLinePortBlockInactive | OpticalTransponderLinePortBlockInactive | OpticalCoherentPluggableBlockInactive
)
SpanPortBlockProvisioning = (
    OlsLinePortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning
)
SpanPortBlock = OlsLinePortBlock | OpticalTransponderLinePortBlock | OpticalCoherentPluggableBlock

LeasedSpectrumPortBlockInactive = (
    OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive
)

LeasedSpectrumPortBlockProvisioning = (
    OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning
)

LeasedSpectrumPortBlock = (
    OpticalTransponderLinePortBlock | OlsAddDropPortBlock | OlsLinePortBlock | OpticalCoherentPluggableBlock
)

OpticalTransportLineChannelBlockInactive = (
    OpticalTransponderLinePortBlockInactive | OpticalCoherentPluggableBlockInactive
)

OpticalTransportLineChannelBlockProvisioning = (
    OpticalTransponderLinePortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning
)

OpticalTransportLineChannelBlock = OpticalTransponderLinePortBlock | OpticalCoherentPluggableBlock

OpticalDigitalServiceClientPortBlockInactive = (
    OpticalTransponderClientPortBlockInactive | OpticalCoherentPluggableBlockInactive
)

OpticalDigitalServiceClientPortBlockProvisioning = (
    OpticalTransponderClientPortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning
)

OpticalDigitalServiceClientPortBlock = OpticalTransponderClientPortBlock | OpticalCoherentPluggableBlock
