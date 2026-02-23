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

from products.product_blocks.optical_device import Platform
from products.product_types.optical_device import OpticalDevice
from workflows.shared import (
    subscription_instance_values_by_block_type_depending_on_instance_id,
)


def _parse_port_identifiers(port_name: str, platform: Platform) -> tuple[str, str, str]:
    """
    Split a port name into shelf_id, slot_id, and port_id based on platform conventions.

    Args:
        port_name: The full port identifier string.
        platform: The device platform (Groove_G30 or GX_G42).

    Returns:
        A tuple of (shelf_id, slot_id, port_id).

    Raises:
        ValueError: If the platform is unsupported or parsing fails.
    """
    if platform is Platform.Groove_G30:
        # format "port-1/2/3" -> take "1/2/3"
        raw = port_name.split("-", 1)[-1]
        shelf, slot, port = raw.split("/")
    elif platform is Platform.GX_G42:
        # format "1-4-T12"
        shelf, slot, port = port_name.split("-", 2)
    else:
        msg = f"Unsupported platform: {platform}"
        raise ValueError(msg)
    return shelf, slot, port


def trx_line_port_patched_but_not_used_selector(
    optical_device_subscription_id: UUIDstr, client_port_name: str, prompt: str = ""
) -> Choice:
    """
    Return a Choice object for selecting an unused optical line port
    on the same shelf/slot as the client port.

    Args:
        optical_device_subscription_id: UUID of the device subscription.
        client_port_name: Name of the client-facing port.
        prompt: Optional custom prompt text.

    Returns:
        A pydantic_forms.validators.Choice instance listing valid line ports.
    """
    subscription = OpticalDevice.from_subscription(optical_device_subscription_id)
    optical_device = subscription.optical_device
    shelf_id, slot_id, _ = _parse_port_identifiers(client_port_name, optical_device.platform)

    patched_ports_subscription_instance_values = subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type="OpticalDevicePort",
        resource_type="port_name",
        depending_on_instance_id=optical_device.subscription_instance_id,
        states=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
    )

    available_ports_siv = []
    for siv in patched_ports_subscription_instance_values:
        si = siv.subscription_instance
        instances_using_this_port = si.in_use_by
        is_used = any(
            i.product_block.name == "OpticalTransportChannel"
            and i.subscription.status
            in (
                SubscriptionLifecycle.ACTIVE,
                SubscriptionLifecycle.PROVISIONING,
            )
            for i in instances_using_this_port
        )
        if not is_used:
            available_ports_siv.append(siv)

    line_ports = {}
    for siv in available_ports_siv:
        port_name = siv.value
        shelf, slot, port = _parse_port_identifiers(port_name, optical_device.platform)

        if shelf != shelf_id or slot != slot_id:
            continue
        if optical_device.platform == Platform.Groove_G30:
            if int(port) > 2:
                continue
        elif optical_device.platform == Platform.GX_G42 and port not in ("L1", "L2"):
            continue

        line_ports[str(siv.subscription_instance_id)] = port_name

    if not prompt:
        prompt = f"Select line optical port on {subscription.optical_device.fqdn}"
    return Choice(prompt, zip(line_ports.keys(), line_ports.items(), strict=False))


def trx_line_port_patched_but_not_used_multiple_selector(
    optical_device_subscription_id: UUIDstr,
    client_port_name: str,
    prompt: str = "",
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
) -> type[list[Choice]]:
    """Return a Choice object for selecting multiple optical ports of an OpticalDevice."""
    base_choice = trx_line_port_patched_but_not_used_selector(optical_device_subscription_id, client_port_name, prompt)
    return Annotated[
        choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items),
        Field(title=prompt),
    ]
