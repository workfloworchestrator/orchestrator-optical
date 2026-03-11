# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from orchestrator.domain import SUBSCRIPTION_MODEL_REGISTRY
from pydantic_forms.types import strEnum

from orchestrator_extra_optical.products.product_types.optical_device import OpticalDevice
from orchestrator_extra_optical.products.product_types.optical_digital_service import OpticalDigitalService
from orchestrator_extra_optical.products.product_types.optical_pipe import OpticalPipe, OpticalPipeType
from orchestrator_extra_optical.products.product_types.optical_dark_spectrum import OpticalDarkSpectrum


class ProductName(strEnum):
    """An enumerator of all product names defined in ``orchestrator-extra-optical``."""

    DARK_FIBER = OpticalPipeType.DARK_FIBER
    LEASED_DARK_SPECTRUM = OpticalPipeType.LEASED_DARK_SPECTRUM
    OPTICAL_DARK_SPECTRUM = "Optical Dark Spectrum"
    OPTICAL_DEVICE = "Optical Device"
    OPTICAL_DIGITAL_SERVICE = "Optical Digital Service"


class ProductType(strEnum):
    """An enumerator of all available products in ``orchestrator-extra-optical``."""

    DARK_FIBER = OpticalPipe.__name__
    LEASED_DARK_SPECTRUM = OpticalPipe.__name__
    OPTICAL_DARK_SPECTRUM = OpticalDarkSpectrum.__name__
    OPTICAL_DEVICE = OpticalDevice.__name__
    OPTICAL_DIGITAL_SERVICE = OpticalDigitalService.__name__


SUBSCRIPTION_MODEL_REGISTRY.update(
    {
        ProductName.DARK_FIBER.value: OpticalPipe,
        ProductName.LEASED_DARK_SPECTRUM.name: OpticalPipe,
        ProductName.OPTICAL_DARK_SPECTRUM.name: OpticalDarkSpectrum,
        ProductName.OPTICAL_DEVICE.name: OpticalDevice,
        ProductName.OPTICAL_DIGITAL_SERVICE.name: OpticalDigitalService,
    }
)


__all__ = ["ProductName", "ProductType"]
