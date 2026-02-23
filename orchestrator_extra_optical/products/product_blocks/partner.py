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

from enum import StrEnum

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle


class PartnerType(StrEnum):
    GARR = "GARR"


class PartnerBlockInactive(ProductBlockModel, product_block_name="Partner"):
    partner_name: str | None = None
    partner_type: PartnerType | None = None
    garrxdb_id: int | None = None
    netbox_id: int | None = None


class PartnerBlockProvisioning(
    PartnerBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    partner_name: str
    partner_type: PartnerType
    garrxdb_id: int | None = None
    netbox_id: int | None = None


class PartnerBlock(PartnerBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    partner_name: str
    partner_type: PartnerType
    garrxdb_id: int | None = None
    netbox_id: int | None = None
