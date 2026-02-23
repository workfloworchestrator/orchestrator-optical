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

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from products.product_blocks.pop import PoPBlock, PoPBlockInactive, PoPBlockProvisioning


class PopInactive(SubscriptionModel, is_base=True):
    pop: PoPBlockInactive


class PopProvisioning(PopInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    pop: PoPBlockProvisioning


class PoP(PopProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    pop: PoPBlock
