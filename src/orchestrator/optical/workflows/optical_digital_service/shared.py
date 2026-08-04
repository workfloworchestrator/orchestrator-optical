"""Shared helpers for the Optical Digital Service workflows.

This module ports the legacy "patched but not used" line port selectors to the
generalized Optical Node/Port model: the line ports of a transponder node that
are already connected through a fiber span or patch subscription and that are
not yet used by any Active or Provisioning Optical Transport Channel. The
platform conventions of the old selectors are kept as vendor logic dispatched
with the ``Vendor`` enum of the HAL.
"""

from typing import Annotated, cast

from pydantic import Field
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice, choice_list

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.hal.optical_node import Vendor, vendor_of
from orchestrator.optical.products.product_types.optical_node.abstracts import AbstractOpticalNode
from orchestrator.optical.workflows.shared import (
    subscription_instance_values_by_block_type_depending_on_instance_id,
)

max_g30_line_port_id = 2


def _parse_port_identifiers(port_name: str, vendor: Vendor) -> tuple[str, str, str]:
    """Split a port name into shelf_id, slot_id, and port_id based on vendor conventions.

    Args:
        port_name: The full port identifier string.
        vendor: The vendor of the Optical Node (Groove G30 or GX G42).

    Returns:
        A tuple of (shelf_id, slot_id, port_id).

    Raises:
        ValueError: If the vendor is unsupported or parsing fails.
    """
    if vendor is Vendor.GROOVE_G30:
        # format "port-1/2/3" -> take "1/2/3"
        raw = port_name.split("-", 1)[-1]
        shelf, slot, port = raw.split("/")
    elif vendor is Vendor.GX_G42:
        # format "1-4-T12"
        shelf, slot, port = port_name.split("-", 2)
    else:
        msg = f"Unsupported vendor: {vendor}"
        raise ValueError(msg)
    return shelf, slot, port


def trx_line_port_patched_but_not_used_selector(
    optical_node_subscription_id: UUIDstr,
    client_port_name: str,
    prompt: str = "",
) -> type[Choice]:
    """Return a Choice type for selecting an unused optical line port on the same shelf/slot as the client port.

    The candidate line ports are the transponder line ports of the Optical Node
    that are already connected through a fiber span or patch subscription; ports
    that are already used by an Active or Provisioning Optical Transport Channel
    are excluded.

    Args:
        optical_node_subscription_id: UUID of the Optical Node subscription.
        client_port_name: Name of the client-facing port.
        prompt: Optional custom prompt text.

    Returns:
        A pydantic_forms.validators.Choice type listing valid line ports.
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    node_vendor = vendor_of(node)
    shelf_id, slot_id, _ = _parse_port_identifiers(client_port_name, node_vendor)

    patched_ports_subscription_instance_values = (
        subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type="OpticalTransponderLinePortBlock",
            resource_type="optical_port_name",
            depending_on_instance_id=str(node.subscription_instance_id),
            states=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
        )
    )

    available_ports_siv = []
    for siv in patched_ports_subscription_instance_values:
        si = siv.subscription_instance
        instances_using_this_port = si.in_use_by
        is_used = any(
            instance.product_block.name == "OpticalTransportChannelBlock"
            and instance.subscription.status
            in (
                SubscriptionLifecycle.ACTIVE,
                SubscriptionLifecycle.PROVISIONING,
            )
            for instance in instances_using_this_port
        )
        if not is_used:
            available_ports_siv.append(siv)

    line_ports = {}
    for siv in available_ports_siv:
        port_name = siv.value
        shelf, slot, port = _parse_port_identifiers(port_name, node_vendor)

        if shelf != shelf_id or slot != slot_id:
            continue
        if node_vendor is Vendor.GROOVE_G30:
            if int(port) > max_g30_line_port_id:
                continue
        elif node_vendor is Vendor.GX_G42 and port not in ("L1", "L2"):
            continue

        line_ports[str(siv.subscription_instance_id)] = port_name

    if not prompt:
        prompt = f"Select line optical port on {node.pqdn}"
    dynamic_class = Choice(prompt, zip(line_ports.keys(), line_ports.items(), strict=False))
    return cast(type[Choice], dynamic_class)


def trx_line_port_patched_but_not_used_multiple_selector(
    optical_node_subscription_id: UUIDstr,
    client_port_name: str,
    prompt: str = "",
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
) -> type[list[Choice]]:
    """Return a Choice list type for selecting multiple unused optical line ports of an Optical Node.

    Args:
        optical_node_subscription_id: UUID of the Optical Node subscription.
        client_port_name: Name of the client-facing port.
        prompt: Optional custom prompt text.
        min_items: Minimum number of selections required.
        max_items: Maximum number of selections allowed.
        unique_items: Whether duplicate selections are allowed.

    Returns:
        A Choice list type for selecting multiple line ports.
    """
    base_choice = trx_line_port_patched_but_not_used_selector(optical_node_subscription_id, client_port_name, prompt)
    return Annotated[
        choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items),
        Field(title=prompt),
    ]  # type: ignore[valid-type]
