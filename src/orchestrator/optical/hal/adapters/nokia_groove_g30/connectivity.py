"""Intra-node connectivity of a Nokia Groove G30 node: add/drop port -> OLS line port.

The internal topology is the user-provisioned ``services/fiber-connection`` table (the
physical fibers patched between the ports of the cards), together with the installed
cards (:func:`g30_modules`) and the OTS ids, which tell the OLS line ports apart.

Starting from the module (card or subcard) hosting the add/drop port, the search
follows the fiber connections towards other OLS modules (wavelength selector, add/drop
or amplifier modules) and stops at the first module owning OTS line ports: those line
ports are the reachable degrees. A module that owns OTS line ports itself (e.g. a fixed
mux/demux or a WSS) reaches its own line ports directly. A port on shelf X only ever
connects to ports on shelf X, so the search never leaves the shelf of the add/drop port.

The Groove G30 reports no spectral occupation, so every internal route is entirely free.
"""

from __future__ import annotations

import re
from collections import deque

from structlog import get_logger

from orchestrator.optical.hal._common import IntraNodeEdge
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (
    G30Function,
    G30Module,
    g30_ids_from_port_name,
    g30_modules,
    get_g30_client,
)
from orchestrator.optical.hal.adapters.nokia_groove_g30.naming import g30_shelf_of_port
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30BlockProvisioning,
)

logger = get_logger(__name__)

#: Key of a module: ``(shelf, slot, subslot)``.
ModuleKey = tuple[int, int, int | None]

_OLS_FUNCTIONS = frozenset({G30Function.WAVELENGTH_SELECTOR, G30Function.ADD_DROP, G30Function.AMPLIFIER})
#: A list key of an endpoint. The device prefixes every name (``ne:shelf[ne:shelf-id='2']``);
#: the SDK models hold the RFC 7951 form, prefixed on the first node only (``shelf[shelf-id='2']``).
_XPATH_KEY = re.compile(r"\[(?:ne:)?(shelf|slot|subslot|port|subport)-id='(\d+)'\]")


def g30_port_name_from_xpath(xpath: str) -> str:
    """Return the G30 port name of a fiber-connection endpoint XPath.

    Args:
        xpath: The endpoint, as the SDK models hold it (``/ne:ne/shelf[shelf-id='2']/slot[slot-id='3']/card/
            subslot[subslot-id='3']/subcard/port[port-id='3']``) or as the device writes it (every name
            prefixed with ``ne:``).

    Returns:
        The port name, e.g. ``port-2/3.3/3`` (``port-1/2/3`` without a subslot and
        ``port-1/3.1/1.4`` with a subport).

    Raises:
        ValueError: If the XPath has no shelf, slot or port id.
    """
    ids = dict(_XPATH_KEY.findall(xpath))
    if not {"shelf", "slot", "port"} <= ids.keys():
        msg = f"Unparsable Groove G30 fiber-connection endpoint: {xpath!r}"
        raise ValueError(msg)
    slot = f"{ids['slot']}.{ids['subslot']}" if "subslot" in ids else ids["slot"]
    port = f"{ids['port']}.{ids['subport']}" if "subport" in ids else ids["port"]
    return f"port-{ids['shelf']}/{slot}/{port}"


def _module_key(port_name: str) -> ModuleKey:
    shelf, slot, subslot, _, _ = g30_ids_from_port_name(port_name)
    return shelf, slot, subslot


def add_drop_connectivity_from_records(
    add_drop_port: str,
    modules: list[G30Module],
    fiber_connections: list[tuple[str, str]],
) -> list[IntraNodeEdge]:
    """Return the OLS line ports reachable from an add/drop port of a Groove G30 node.

    Args:
        add_drop_port: Name of the add/drop port, e.g. ``port-1/3.1/1``.
        modules: The installed modules of the node (see :func:`g30_modules`).
        fiber_connections: The fiber connections as ``(src port name, dst port name)``.

    Returns:
        One edge per reachable line port, sorted by line port name, with no occupancy.
    """
    by_key = {(module.shelf_id, module.slot_id, module.subslot_id): module for module in modules}
    ots_ids = next((module.ots_ids for module in modules), frozenset())
    line_ports_by_module: dict[ModuleKey, list[str]] = {}
    for ots_id in ots_ids:
        line_port = f"port-{ots_id}"
        try:
            line_ports_by_module.setdefault(_module_key(line_port), []).append(line_port)
        except ValueError:
            continue

    shelf = g30_shelf_of_port(add_drop_port)
    links: dict[ModuleKey, set[ModuleKey]] = {}
    for src, dst in fiber_connections:
        if add_drop_port in (src, dst):
            continue  # the fiber of the add/drop port itself leads to the client side
        try:
            src_key, dst_key = _module_key(src), _module_key(dst)
        except ValueError:
            continue
        if src_key[0] != shelf or dst_key[0] != shelf or src_key == dst_key:
            continue  # a port on shelf X only connects to ports on shelf X
        links.setdefault(src_key, set()).add(dst_key)
        links.setdefault(dst_key, set()).add(src_key)

    start = _module_key(add_drop_port)
    reached: list[str] = []
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current_lines := line_ports_by_module.get(current):
            reached.extend(port for port in current_lines if port != add_drop_port)
            continue  # a module owning line ports is a degree: never expand past it
        for neighbor in sorted(links.get(current, ()), key=str):
            module = by_key.get(neighbor)
            if neighbor in seen or module is None or not (module.functions & _OLS_FUNCTIONS):
                continue
            seen.add(neighbor)
            queue.append(neighbor)

    return [IntraNodeEdge(add_drop_port, line_port) for line_port in sorted(set(reached))]


def retrieve_add_drop_connectivity(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    add_drop_port: str,
) -> list[IntraNodeEdge]:
    """Retrieve the OLS line ports an add/drop port of a Groove G30 node can reach.

    Args:
        optical_node_block: The Nokia Groove G30 node block.
        add_drop_port: Name of the add/drop port.

    Returns:
        One edge per reachable line port, with no occupancy.
    """
    g30 = get_g30_client(optical_node_block)
    fiber_connections: list[tuple[str, str]] = []
    for item in g30.data.ne_ne.services.fiber_connection.retrieve(content="config") or []:
        try:
            fiber_connections.append((g30_port_name_from_xpath(item.src_port), g30_port_name_from_xpath(item.dst_port)))
        except ValueError:
            logger.warning("Skipping unparsable G30 fiber connection", src=item.src_port, dst=item.dst_port)
    return add_drop_connectivity_from_records(add_drop_port, g30_modules(optical_node_block), fiber_connections)
