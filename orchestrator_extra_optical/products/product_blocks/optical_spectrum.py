# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle

from products.product_blocks.optical_spectrum_path_constraints import (
    OpticalSpectrumPathConstraintsBlock,
    OpticalSpectrumPathConstraintsBlockInactive,
    OpticalSpectrumPathConstraintsBlockProvisioning,
)
from products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlock,
    OpticalSpectrumSectionBlockInactive,
    OpticalSpectrumSectionBlockProvisioning,
)
from utils.custom_types.frequencies import Passband

OpticalSpectrumSectionsList = Annotated[list[SI], Len(min_length=0, max_length=9)]


class OpticalSpectrumBlockInactive(
    ProductBlockModel, product_block_name="OpticalSpectrum"
):
    spectrum_name: str | None = None
    passband: Passband | None = None
    optical_spectrum_sections: OpticalSpectrumSectionsList[
        OpticalSpectrumSectionBlockInactive
    ]
    optical_spectrum_path_constraints: OpticalSpectrumPathConstraintsBlockInactive


class OpticalSpectrumBlockProvisioning(
    OpticalSpectrumBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    spectrum_name: str | None = None
    passband: Passband
    optical_spectrum_sections: OpticalSpectrumSectionsList[
        OpticalSpectrumSectionBlockProvisioning
    ]
    optical_spectrum_path_constraints: OpticalSpectrumPathConstraintsBlockProvisioning


class OpticalSpectrumBlock(
    OpticalSpectrumBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    spectrum_name: str
    passband: Passband
    optical_spectrum_sections: OpticalSpectrumSectionsList[OpticalSpectrumSectionBlock]
    optical_spectrum_path_constraints: OpticalSpectrumPathConstraintsBlock
