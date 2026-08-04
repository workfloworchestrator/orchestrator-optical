"""Union types for Optical Pipe Product Blocks."""

from typing import Annotated

from pydantic import Discriminator

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

OpticalPipeBlockUnion = Annotated[
    OpticalFiberPatchBlock | OpticalFiberSpanBlock | OpticalLeasedSpectrumBlock,
    Discriminator(lambda x: x.product.name),
]
OpticalPipeBlockUnionProvisioning = Annotated[
    OpticalFiberPatchBlockProvisioning | OpticalFiberSpanBlockProvisioning | OpticalLeasedSpectrumBlockProvisioning,
    Discriminator(lambda x: x.product.name),
]
OpticalPipeBlockUnionInactive = Annotated[
    OpticalFiberPatchBlockInactive | OpticalFiberSpanBlockInactive | OpticalLeasedSpectrumBlockInactive,
    Discriminator(lambda x: x.product.name),
]
