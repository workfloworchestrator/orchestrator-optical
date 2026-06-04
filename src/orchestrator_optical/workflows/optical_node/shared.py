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

from orchestrator.domain import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice, choice_list

from orchestrator_optical.products.product_blocks.optical_node import OpticalNodeRole
from orchestrator_optical.products.product_types.optical_node import OpticalNodeSubscription
from orchestrator_optical.products.services.optical_port import (
    get_optical_node_client_ports_names,
    get_optical_node_line_ports_names,
    get_optical_node_ports_names,
    get_optical_transceiver_modes,
)
from orchestrator_optical.workflows.shared import (
    subscription_instance_values_by_block_type_depending_on_instance_id,
    subscriptions_by_product_type_and_instance_value,
)


def optical_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> Choice:
    """Return a Choice object for selecting an optical port of an OpticalDevice."""
    subscription = SubscriptionModel.from_subscription(optical_node_subscription_id)
    ports = get_optical_node_ports_names(subscription.optical_node)
    if not prompt:
        prompt = f"Select optical port on {subscription.optical_node.pqdn}"
    return Choice(prompt, zip(ports, ports, strict=False))


def unused_optical_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> Choice:
    """Return a Choice object for selecting an unused optical port of an OpticalDevice."""
    subscription = OpticalNodeSubscription.from_subscription(optical_node_subscription_id)
    ports = get_optical_node_ports_names(subscription.optical_node)

    ports_in_db = subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type="OpticalDevicePort",
        resource_type="port_name",
        depending_on_instance_id=subscription.optical_node.subscription_instance_id,
        statuses=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
    )
    ports_in_db = [p.value for p in ports_in_db]
    ports_in_db = set(ports_in_db)

    unused_ports = [port for port in ports if port not in ports_in_db]
    if not prompt:
        prompt = f"Select optical port on {subscription.optical_node.pqdn}"
    return Choice(prompt, zip(unused_ports, unused_ports, strict=False))


def optical_client_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> Choice:
    """Return a Choice object for selecting an optical port of an OpticalDevice."""
    subscription = OpticalNodeSubscription.from_subscription(optical_node_subscription_id)
    ports = get_optical_node_client_ports_names(subscription.optical_node)
    if not prompt:
        prompt = f"Select client optical port on {subscription.optical_node.pqdn}"
    return Choice(prompt, zip(ports, ports, strict=False))


def unused_optical_client_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> Choice:
    """Return a Choice object for selecting an unused optical port of an OpticalDevice."""
    subscription = OpticalNodeSubscription.from_subscription(optical_node_subscription_id)
    ports = get_optical_node_client_ports_names(subscription.optical_node)

    ports_in_db = subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type="OpticalDevicePort",
        resource_type="port_name",
        depending_on_instance_id=subscription.optical_node.subscription_instance_id,
        statuses=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
    )
    ports_in_db = [p.value for p in ports_in_db]
    ports_in_db = set(ports_in_db)

    unused_ports = [port for port in ports if port not in ports_in_db]
    if not prompt:
        prompt = f"Select client optical port on {subscription.optical_node.pqdn}"
    return Choice(prompt, zip(unused_ports, unused_ports, strict=False))


def optical_line_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> Choice:
    """Return a Choice object for selecting an optical port of an OpticalDevice."""
    subscription = OpticalNodeSubscription.from_subscription(optical_node_subscription_id)
    ports = get_optical_node_line_ports_names(subscription.optical_node)
    if not prompt:
        prompt = f"Select line optical port on {subscription.optical_node.pqdn}"
    return Choice(prompt, zip(ports, ports, strict=False))


def unused_optical_line_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> Choice:
    """Return a Choice object for selecting an unused optical port of an OpticalDevice."""
    subscription = OpticalNodeSubscription.from_subscription(optical_node_subscription_id)
    ports = get_optical_node_line_ports_names(subscription.optical_node)

    ports_in_db = subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type="OpticalDevicePort",
        resource_type="port_name",
        depending_on_instance_id=subscription.optical_node.subscription_instance_id,
        statuses=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
    )
    ports_in_db = [p.value for p in ports_in_db]
    ports_in_db = set(ports_in_db)

    unused_ports = [port for port in ports if port not in ports_in_db]
    if not prompt:
        prompt = f"Select line optical port on {subscription.optical_node.pqdn}"
    return Choice(prompt, zip(unused_ports, unused_ports, strict=False))


def get_optical_node_subscriptions_by_types(
    device_types: list[OpticalNodeRole],
) -> list[OpticalNodeSubscription]:
    """
    Retrieves a list of active OpticalDevice subscriptions with the given optical device types.

    Args:
        device_types (List[DeviceType]): The types of optical device to retrieve subscriptions for.

    Returns:
        List[OpticalDevice]: A list of active OpticalDevice records for the given optical device types.
    """
    subscriptions = []
    for device_type in device_types:
        subscriptions.extend(
            subscriptions_by_product_type_and_instance_value(
                product_type="OpticalDevice",
                resource_type="device_type",
                value=device_type,
                status=[SubscriptionLifecycle.ACTIVE],
            )
        )

    return subscriptions


def optical_node_selector_of_types(
    device_types: list[OpticalNodeRole],
    prompt: str | None = None,
) -> Choice:
    """
    Selects an optical device from a list of devices.

    Args:
        device_types (List[DeviceType]): A list of device types to filter the optical devices.
        prompt (str | None, optional): A custom prompt message for the selection. Defaults to None.

    Returns:
        Choice: A Choice object containing the prompt and a list of tuples with subscription IDs and descriptions.
    """
    subscriptions = get_optical_node_subscriptions_by_types(device_types)
    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }

    if not prompt:
        prompt = f"Select an Optical Device of type {', '.join(device_types)}"

    return Choice(prompt, zip(products.keys(), products.items(), strict=False))


def multiple_optical_node_selector(
    device_types: list[OpticalNodeRole],
    prompt: str | None = None,
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
) -> type[list[Choice]]:
    """
    Selects multiple optical devices from a list of devices.

    Args:
        device_types: A list of device types to filter the optical devices
        prompt: A custom prompt message for the selection
        min_items: Minimum number of selections required
        max_items: Maximum number of selections allowed
        unique_items: Whether duplicate selections are allowed
    Returns:
        A Choice list type for selecting multiple devices
    """
    base_choice = optical_node_selector_of_types(device_types, prompt)
    return Annotated[
        choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items),
        Field(title=prompt),
    ]


def transceiver_mode_selector(
    optical_node_subscription_id: UUIDstr,
    port_name: str,
    prompt: str | None = None,
) -> Choice:
    """
    Creates a Choice object for selecting a transceiver mode for a given port.

    Args:
        optical_node_subscription_id (UUIDstr): The subscription ID of the optical device.
        port_name (str): The name of the port belonging to the transceiver card.
                         This can also be a client port of a CHM2T transponder.
        prompt (str | None, optional): A custom prompt message for the selection. Defaults to None.

    Returns:
        Choice: A Choice object containing the prompt and a list of available transceiver modes.
    """
    subscription = OpticalNodeSubscription.from_subscription(optical_node_subscription_id)
    modulations = get_optical_transceiver_modes(subscription.optical_node, port_name)
    if not prompt:
        prompt = "Select a modulation"
    return Choice(prompt, zip(modulations, modulations, strict=False))
