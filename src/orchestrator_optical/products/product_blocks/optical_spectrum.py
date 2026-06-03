"""Module for Optical Spectrum product blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSection,
    OpticalSpectrumSectionInactive,
    OpticalSpectrumSectionProvisioning,
)
from orchestrator_optical.utils.custom_types.frequencies import Passband

OpticalSpectrumSectionsList = Annotated[list[SI], Len(min_length=0, max_length=9)]


class OpticalSpectrumInactive(ProductBlockModel, product_block_name="OpticalSpectrum"):
    """Inactive state of the Optical Spectrum product block."""

    spectrum_name: str | None = None
    passband: Passband | None = None
    sections: OpticalSpectrumSectionsList[OpticalSpectrumSectionInactive]


class OpticalSpectrumProvisioning(OpticalSpectrumInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Provisioning state of the Optical Spectrum product block."""

    spectrum_name: str | None = None
    passband: Passband
    sections: OpticalSpectrumSectionsList[OpticalSpectrumSectionProvisioning]


class OpticalSpectrum(OpticalSpectrumProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of the Optical Spectrum product block."""

    spectrum_name: str
    passband: Passband
    sections: OpticalSpectrumSectionsList[OpticalSpectrumSection]
