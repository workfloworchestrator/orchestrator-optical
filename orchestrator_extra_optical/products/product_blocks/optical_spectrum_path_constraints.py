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

from products.product_blocks.optical_device import (
    OpticalDeviceBlock,
    OpticalDeviceBlockInactive,
    OpticalDeviceBlockProvisioning,
)
from products.product_blocks.optical_fiber import (
    OpticalFiberBlock,
    OpticalFiberBlockInactive,
    OpticalFiberBlockProvisioning,
)

ListOfExclude_nodes = Annotated[list[SI], Len(min_length=0, max_length=30)]

ListOfExclude_spans = Annotated[list[SI], Len(min_length=0, max_length=30)]


class OpticalSpectrumPathConstraintsBlockInactive(
    ProductBlockModel, product_block_name="OpticalSpectrumPathConstraints"
):
    exclude_nodes: ListOfExclude_nodes[OpticalDeviceBlockInactive]
    exclude_spans: ListOfExclude_spans[OpticalFiberBlockInactive]


class OpticalSpectrumPathConstraintsBlockProvisioning(
    OpticalSpectrumPathConstraintsBlockInactive,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    exclude_nodes: ListOfExclude_nodes[OpticalDeviceBlockProvisioning]
    exclude_spans: ListOfExclude_spans[OpticalFiberBlockProvisioning]


class OpticalSpectrumPathConstraintsBlock(
    OpticalSpectrumPathConstraintsBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.ACTIVE],
):
    exclude_nodes: ListOfExclude_nodes[OpticalDeviceBlock]
    exclude_spans: ListOfExclude_spans[OpticalFiberBlock]
