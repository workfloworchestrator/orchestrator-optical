"""Union types for Optical Pipe Product Blocks."""

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

OpticalPipeBlockUnion = OpticalFiberPatchBlock | OpticalFiberSpanBlock | OpticalLeasedSpectrumBlock
OpticalPipeBlockUnionProvisioning = (
    OpticalFiberPatchBlockProvisioning | OpticalFiberSpanBlockProvisioning | OpticalLeasedSpectrumBlockProvisioning
)
OpticalPipeBlockUnionInactive = (
    OpticalFiberPatchBlockInactive | OpticalFiberSpanBlockInactive | OpticalLeasedSpectrumBlockInactive
)
