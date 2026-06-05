"""Module for Optical Spectrum product blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlock,
    OpticalSpectrumSectionBlockInactive,
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator_optical.utils.custom_types.frequencies import Passband

OpticalSpectrumSectionList = Annotated[list[SI], Len(min_length=0, max_length=9)]


class OpticalSpectrumBlockInactive(ProductBlockModel, product_block_name="OpticalSpectrum"):
    """Inactive state of the Optical Spectrum product block."""

    optical_spectrum_name: str | None = None
    optical_spectrum_passband: Passband | None = None
    optical_spectrum_sections: OpticalSpectrumSectionList[OpticalSpectrumSectionBlockInactive] = Field(
        default_factory=list
    )


class OpticalSpectrumBlockProvisioning(OpticalSpectrumBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Provisioning state of the Optical Spectrum product block."""

    optical_spectrum_name: str | None
    optical_spectrum_passband: Passband
    optical_spectrum_sections: OpticalSpectrumSectionList[OpticalSpectrumSectionBlockProvisioning]


class OpticalSpectrumBlock(OpticalSpectrumBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of the Optical Spectrum product block."""

    optical_spectrum_name: str
    optical_spectrum_passband: Passband
    optical_spectrum_sections: OpticalSpectrumSectionList[OpticalSpectrumSectionBlock]
