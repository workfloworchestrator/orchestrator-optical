"""Groove G30 port-name parsing; pure functions that do not need the vendor SDK."""


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


def g30_shelf_of_port(port_name: str) -> int:
    """Return the shelf id of a Groove G30 port name (``port-2/3.3/3`` -> 2)."""
    return g30_ids_from_port_name(port_name)[0]
