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

from orchestrator.types import SubscriptionLifecycle
from pydantic import Field
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice, choice_list

from products.product_types.optical_fiber import OpticalFiber
from workflows.shared import subscriptions_by_product_type


def get_fibers_connected_to(
    device_subscription_id: UUIDstr,
    status: list[SubscriptionLifecycle] | None = None,
) -> list[OpticalFiber]:
    """
    Retrieve a list of fiber subscriptions that are connected to the given device subscription.

    Args:
        device_subscription_id (UUIDstr): The subscription ID of the device to check connectivity for.
        status (List[SubscriptionLifecycle]): The lifecycle status of the fiber subscriptions to retrieve.

    Returns:
        List[OpticalFiber]: A list of fiber subscriptions that are connected to the given device subscription.
    """
    if status is None:
        status = [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING]

    fiber_subs = subscriptions_by_product_type("OpticalFiber", status)

    connected_fibers_subs = []
    for fiber_sub in fiber_subs:
        fiber_sub = OpticalFiber.from_subscription(fiber_sub.subscription_id)
        fiber = fiber_sub.optical_fiber
        for port in fiber.terminations:
            if str(port.optical_device.owner_subscription_id) == device_subscription_id:
                connected_fibers_subs.append(fiber_sub)

    return connected_fibers_subs


def optical_fiber_selector(
    status: list[SubscriptionLifecycle] | None = None,
    prompt: str = "",
) -> Choice:
    if status is None:
        status = [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING]

    subscriptions = subscriptions_by_product_type("OpticalFiber", status)
    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }

    if not prompt:
        prompt = "Select an Optical Fiber"

    return Choice(prompt, zip(products.keys(), products.items(), strict=False))


def multiple_optical_fiber_selector(
    status: list[SubscriptionLifecycle] | None = None,
    prompt: str = "Select one or more Optical Fibers",
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
) -> type[list[Choice]]:
    if status is None:
        status = [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING]

    base_choice = optical_fiber_selector(status, prompt)
    return Annotated[
        choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items),
        Field(title=prompt),
    ]
