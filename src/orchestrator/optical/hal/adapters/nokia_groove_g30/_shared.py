"""Device-level, cross-area shared helpers for the Nokia Groove G30 adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockInactive
from orchestrator.optical.services.nokia import G30Client

if TYPE_CHECKING:
    from orchestrator.optical.services.nokia.g30.data_navigators.ne import PortItemNode, SubportItemNode


def get_g30_client(optical_node_block: AbstractOpticalNodeBlockInactive) -> G30Client:
    """Return a RESTCONF client to reach the given Nokia Groove G30 node.

    Args:
        optical_node_block: The Nokia Groove G30 node block (any lifecycle variant).

    Returns:
        A Groove G30 RESTCONF client.
    """
    return G30Client(
        loopback_ip=str(optical_node_block.management.optical_module_node_dcn_loopback_ip or "") or None,
        management_ip=str(optical_node_block.management.optical_module_node_dcn_interface_ip or "") or None,
    )


def g30_ids_from_port_name(port_name: str) -> tuple[int, int, int | None, int, int | None]:
    """Return the shelf, slot, subslot, port and subport ids of a Groove G30 port name.

    Args:
        port_name: The name of the port to obtain the ids from, e.g. ``"port-1/2/3"``
            or ``"port-1/3.1/1.4"``.

    Returns:
        A tuple with the shelf id, slot id, subslot id (or None), port id and
        subport id (or None).

    Raises:
        ValueError: If a subport id is given without a subslot id.
    """
    ids = port_name.rsplit("-", maxsplit=1)[-1]  # port-1/2/3 -> 1/2/3 or port-1/3.1/1.4 -> 1/3.1/1.4
    shelf_id, slot_id, port_id = ids.split("/")  # 1/2/3 -> 1, 2, 3 or 1/3.1/1.4 -> 1, 3.1, 1.4

    subslot_id = None
    if "." in slot_id:
        slot_id, subslot_id = slot_id.split(".")

    subport_id = None
    if "." in port_id:
        port_id, subport_id = port_id.split(".")

    if subport_id and not subslot_id:
        msg = "Subport ID is not supported without subslot ID in Groove G30 configuration."
        raise ValueError(msg)

    return (
        int(shelf_id),
        int(slot_id),
        int(subslot_id) if subslot_id is not None else None,
        int(port_id),
        int(subport_id) if subport_id is not None else None,
    )


def g30_port_navigator_node_from_port_name(
    g30_device_block: AbstractOpticalNodeBlockInactive,
    port_name: str,
) -> tuple[PortItemNode | SubportItemNode, int, int, int | None, int, int | None]:
    """Return the RESTCONF endpoint of a Groove G30 port, with its shelf, slot, subslot, port and subport ids.

    Args:
        g30_device_block: Optical Node block of the Groove G30 device.
        port_name: The name of the port to obtain the endpoint from.

    Returns:
        A tuple with the RESTCONF endpoint, shelf id, slot id, subslot id (or None),
        port id and subport id (or None).

    Raises:
        ValueError: If a subport id is given without a subslot id.
    """
    g30 = get_g30_client(g30_device_block)
    shelf_id, slot_id, subslot_id, port_id, subport_id = g30_ids_from_port_name(port_name)

    if subslot_id is not None and subport_id is not None:
        endpoint = (
            g30.data.ne_ne.shelf(shelf_id)
            .slot(slot_id)
            .card.subslot(subslot_id)
            .subcard.port(port_id)
            .subport(subport_id)
        )
    elif subslot_id is not None:
        endpoint = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.port(port_id)
    else:
        endpoint = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    return endpoint, shelf_id, slot_id, subslot_id, port_id, subport_id
