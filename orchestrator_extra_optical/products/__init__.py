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

from products.product_types.optical_device import OpticalDevice
from products.product_types.optical_digital_service import OpticalDigitalService
from products.product_types.optical_fiber import OpticalFiber
from products.product_types.optical_spectrum import OpticalSpectrum
from products.product_types.partner import Partner
from products.product_types.pop import PoP

SUBSCRIPTION_MODEL_REGISTRY.update(
    {
        "partner": Partner,
        "pop": PoP,
        "optical_device": OpticalDevice,
        "optical_fiber": OpticalFiber,
        "optical_spectrum": OpticalSpectrum,
        "optical_digital_service": OpticalDigitalService,
    }
)
