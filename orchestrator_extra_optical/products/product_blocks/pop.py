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

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import computed_field

from utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate


class PoPBlockInactive(ProductBlockModel, product_block_name="PoP"):
    garrxdb_id: int | None = None
    netbox_id: int | None = None
    code: str | None = None
    full_name: str | None = None
    latitude: LatitudeCoordinate | None = None
    longitude: LongitudeCoordinate | None = None


class PoPBlockProvisioning(
    PoPBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    garrxdb_id: int
    netbox_id: int
    code: str | None = None
    full_name: str | None = None
    latitude: LatitudeCoordinate | None = None
    longitude: LongitudeCoordinate | None = None


class PoPBlock(PoPBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    garrxdb_id: int
    netbox_id: int
    code: str
    full_name: str
    latitude: LatitudeCoordinate | None = None
    longitude: LongitudeCoordinate | None = None

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.full_name}"
