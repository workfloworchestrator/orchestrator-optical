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

from products.product_blocks.optical_device import (
    OpticalDeviceBlock,
    OpticalDeviceBlockInactive,
    OpticalDeviceBlockProvisioning,
)


class OpticalDeviceInactive(SubscriptionModel, is_base=True):
    optical_device: OpticalDeviceBlockInactive


class OpticalDeviceProvisioning(
    OpticalDeviceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    optical_device: OpticalDeviceBlockProvisioning


class OpticalDevice(
    OpticalDeviceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    optical_device: OpticalDeviceBlock
