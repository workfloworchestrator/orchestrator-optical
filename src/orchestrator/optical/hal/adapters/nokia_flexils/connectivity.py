r"""Intra-node connectivity of a Nokia FlexILS node: add/drop port -> degree, with occupancy.

The internal topology of a FlexILS node is rebuilt from four TL1 reads:

- ``RTRV-EQPT``: the card type of every card (FRM, FBM, FSM, FMM*), which decides the
  internal behaviour of the card (see the card rules below), and the equipment ``SERNO``;
- ``RTRV-SCG``: the SCG ports of every card and their ``PROVNBRTP`` / ``PROVOWREMPTP``,
  i.e. the patch from that port to the port of another card (e.g. ``2-A-3-L1 -> 1-A-1-S9``,
  ``1-E1-1-T1A -> MA4621080160/1-A-3-L1``). A neighbor prefixed ``<serial>/`` is internal
  when the serial is a local ``SERNO`` (the chassis), a patch to another device otherwise
  (a transponder, another node: ignored);
- ``RTRV-OTS``: the OTS line ports, i.e. the degrees of the node;
- ``RTRV-OCRS``: the provisioned optical cross-connections with their ``PASSBANDLIST``,
  traced through the same internal topology to know which frequencies are already used
  on each internal resource.

Card rules (the single home for the card quirks):

- **FRM** (twin WSS, the degree): every ``S`` port reaches the OTS line port of the card.
  Only the spectrum available on the OTS line port matters, which the path engine
  already takes from the line port block, so the FRM adds no internal resource.
- **FBM**: every ``T`` port reaches the ``L`` ports of the card. The ``T<n>A``/``T<n>B``
  ports are coupled: a frequency used on B cannot be reused on A (one shared resource).
- **FSM** (multicast switch): any ``T`` port reaches any ``L`` port, but a ``T`` port can
  be bound to a single ``L`` for the entire spectrum: once a cross-connection binds it,
  only that ``L`` is reachable. Every ``L`` is a shared resource.
- **FMM\\*** (12:1 splitter/combiner): every ``T`` port reaches the ``L`` port, which is a
  shared resource and is patched to an FBM ``T`` port (recorded on the FBM ``T`` as
  ``PROVOWREMPTP=<chassis SERNO>/<FMM>-L1``).

Intra-card moves are upward only (``T -> L``, ``S -> OTS``); inter-card moves follow the
``PROVNBRTP`` patches in both directions. An OTS line port is terminal, so a route never
crosses a degree into an express patch towards another degree.
"""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from structlog import get_logger

from orchestrator.optical.hal._common import IntraNodeEdge
from orchestrator.optical.hal.adapters.nokia_flexils._shared import (
    _all_records,
    _record_value,
    _records,
    get_flex_client,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.utils.custom_types.frequencies import merge_intervals

logger = get_logger(__name__)

_FBM_TRIBUTARY = re.compile(r"^T(\d{1,2})[AB]$")
_TRIBUTARY = re.compile(r"^T\d+[AB]?$")
_LINE = re.compile(r"^L\d+$")
_SYSTEM = re.compile(r"^S\d+$")

#: ``RTRV-SCG`` keys holding the far end of a patch: ``PROVNBRTP`` (e.g. FBM L -> FRM S) and
#: ``PROVOWREMPTP`` (e.g. FBM T -> ``<chassis SERNO>/<FMM>-L1``, the FMM L has no PROVNBRTP).
_NEIGHBOR_KEYS: tuple[str, ...] = ("PROVNBRTP", "PROVOWREMPTP")

#: Card families with internal rules, keyed by the prefix of the ``RTRV-EQPT`` TYPE.
_CARD_FAMILIES: tuple[str, ...] = ("FRM", "FBM", "FSM", "FMM")


def _card_family(card_type: str | None) -> str | None:
    """Return the card family of a ``RTRV-EQPT`` TYPE, or None for cards without rules."""
    if not card_type:
        return None
    return next((family for family in _CARD_FAMILIES if card_type.upper().startswith(family)), None)


def _port_kind(aid: str) -> str:
    """Return the last dash-separated component of an AID (``T2A``, ``L1``, ``S9``...)."""
    return aid.rsplit("-", 1)[-1]


def _strip_channel(aid: str) -> str:
    """Strip the ``-<channel>`` suffix of an OCRS endpoint AID (``1-A-1-S4-3`` -> ``1-A-1-S4``)."""
    head, _, tail = aid.rpartition("-")
    return head if head and tail.isdigit() else aid


def _internal_neighbor_aid(value: str | None, local_serials: frozenset[str]) -> str | None:
    """Return the local port AID of a ``PROVNBRTP`` value, or None when the neighbor is external.

    The neighbor is a bare AID (internal), ``<serial>/<aid>`` with the serial of an
    equipment of this node (internal, e.g. ``MA4621081160/1-A-3-L1``), or
    ``<serial>/<aid>`` with the serial of another node (external, not an internal patch).
    """
    if not value:
        return None
    serial, separator, aid = value.rpartition("/")
    if separator and serial not in local_serials:
        return None
    return aid or None


def _passbands_of(value: Any) -> list[tuple[int, int]]:
    """Parse a ``PASSBANDLIST`` value (``[a, b]``, ``[[a, b], [c, d]]`` or ``"a&b"``)."""
    if value is None or value in ("", []):
        return []
    if isinstance(value, str):
        value = value.split("&")
    if isinstance(value, list) and value and not isinstance(value[0], list):
        value = [value]
    passbands: list[tuple[int, int]] = []
    for pair in cast(list[list[Any]], value):
        try:
            start, end = int(pair[0]), int(pair[-1])
        except (TypeError, ValueError, IndexError):
            continue
        if start < end:
            passbands.append((start, end))
    return passbands


@dataclass
class FlexilsInternalTopology:
    """The internal port graph of a FlexILS node, built from the TL1 records.

    Attributes:
        edges: Directed adjacency between port AIDs (SCG and OTS).
        ots_ports: The OTS line port AIDs (terminal nodes, the degrees).
        resources: Shared spectrum resource of a port AID, when it has one.
        fsm_tributaries: The tributary AIDs of FSM cards (bound to a single ``L``).
        card_families: Card family of every port AID with a known card.
    """

    edges: dict[str, list[str]] = field(default_factory=dict)
    ots_ports: frozenset[str] = frozenset()
    resources: dict[str, str] = field(default_factory=dict)
    fsm_tributaries: frozenset[str] = frozenset()
    card_families: dict[str, str] = field(default_factory=dict)

    def add_edge(self, src: str, dst: str) -> None:
        """Add the directed edge ``src -> dst`` (idempotent)."""
        targets = self.edges.setdefault(src, [])
        if dst not in targets:
            targets.append(dst)

    def route(self, src: str, dst: str) -> list[str] | None:
        """Return the shortest route from ``src`` to ``dst``, or None when unreachable."""
        return next((route for target, route in self.routes_from(src, {dst}) if target == dst), None)

    def routes_from(self, src: str, targets: Iterable[str] | None = None) -> list[tuple[str, list[str]]]:
        """Return the shortest route from ``src`` to every reachable target (OTS by default).

        Targets are terminal: the search never expands past a target node.
        """
        wanted = set(targets) if targets is not None else set(self.ots_ports)
        previous: dict[str, str | None] = {src: None}
        queue = deque([src])
        found: list[tuple[str, list[str]]] = []
        while queue:
            current = queue.popleft()
            if current in wanted and current != src:
                route = [current]
                while (hop := previous[route[-1]]) is not None:
                    route.append(hop)
                found.append((current, route[::-1]))
                continue
            if current in self.ots_ports and current != src:
                continue
            for neighbor in self.edges.get(current, []):
                if neighbor not in previous:
                    previous[neighbor] = current
                    queue.append(neighbor)
        return found


def _card_of(aid: str, card_types: dict[str, str]) -> str | None:
    """Return the longest card AID prefix of a port AID present in the equipment inventory."""
    parts = aid.split("-")[:-1]
    for length in range(len(parts), 0, -1):
        candidate = "-".join(parts[:length])
        if candidate in card_types:
            return candidate
    return None


def _connect_all(topology: FlexilsInternalTopology, sources: Iterable[str], targets: Sequence[str]) -> None:
    for source in sources:
        for target in targets:
            topology.add_edge(source, target)


def _apply_card_rules(topology: FlexilsInternalTopology, card: str, family: str, ports: list[str]) -> list[str]:
    """Add the intra-card edges and shared resources of a card; return its FSM tributaries."""
    for port in ports:
        topology.card_families[port] = family
    tributaries = [port for port in ports if _TRIBUTARY.match(_port_kind(port))]
    lines = [port for port in ports if _LINE.match(_port_kind(port)) and port not in topology.ots_ports]
    match family:
        case "FRM":
            systems = [port for port in ports if _SYSTEM.match(_port_kind(port))]
            _connect_all(topology, systems, [port for port in ports if port in topology.ots_ports])
        case "FBM":
            for tributary in tributaries:
                if pair := _FBM_TRIBUTARY.match(_port_kind(tributary)):
                    topology.resources[tributary] = f"{card}-T{pair.group(1)}"
            _connect_all(topology, tributaries, lines)
        case "FSM" | "FMM":
            topology.resources.update({line: line for line in lines})
            _connect_all(topology, tributaries, lines)
    return tributaries if family == "FSM" else []


def build_internal_topology(
    scg_records: Sequence[dict[str, Any]],
    eqpt_records: Sequence[dict[str, Any]],
    ots_aids: Iterable[str],
) -> FlexilsInternalTopology:
    """Build the internal port graph of a FlexILS node from its TL1 records.

    Args:
        scg_records: The parsed ``RTRV-SCG`` records (``AID``, ``PROVNBRTP``).
        eqpt_records: The parsed ``RTRV-EQPT`` records (``AID``, ``TYPE``).
        ots_aids: The AIDs of the OTS line ports (``RTRV-OTS``).

    Returns:
        The internal topology of the node.
    """
    card_types = {
        aid: card_type
        for record in eqpt_records
        if (aid := _record_value(record, "AID")) and (card_type := _record_value(record, "TYPE"))
    }
    ots = frozenset(ots_aids)
    topology = FlexilsInternalTopology(ots_ports=ots)

    scg_aids = [aid for record in scg_records if (aid := _record_value(record, "AID"))]
    ports_by_card: dict[str, list[str]] = {}
    for aid in [*scg_aids, *sorted(ots)]:
        if (card := _card_of(aid, card_types)) is not None:
            ports_by_card.setdefault(card, []).append(aid)

    fsm_tributaries: set[str] = set()
    for card, ports in ports_by_card.items():
        family = _card_family(card_types.get(card))
        if family is not None:
            fsm_tributaries.update(_apply_card_rules(topology, card, family, ports))
    topology.fsm_tributaries = frozenset(fsm_tributaries)

    local_serials = frozenset(serial for record in eqpt_records if (serial := _record_value(record, "SERNO")))
    for record in scg_records:
        if not (aid := _record_value(record, "AID")):
            continue
        for key in _NEIGHBOR_KEYS:
            neighbor = _internal_neighbor_aid(_record_value(record, key), local_serials)
            if neighbor and neighbor != aid:
                topology.add_edge(aid, neighbor)
                topology.add_edge(neighbor, aid)

    logger.debug(
        "Built FlexILS internal topology",
        num_scgs=len(scg_aids),
        num_cards=len(ports_by_card),
        num_ots=len(ots),
        num_resources=len(topology.resources),
    )
    return topology


def add_drop_connectivity_from_records(
    add_drop_port: str,
    scg_records: Sequence[dict[str, Any]],
    eqpt_records: Sequence[dict[str, Any]],
    ots_aids: Iterable[str],
    ocrs_records: Sequence[dict[str, Any]],
) -> list[IntraNodeEdge]:
    """Return the degrees reachable from an add/drop port, with the internal occupancy.

    Args:
        add_drop_port: AID of the add/drop SCG port.
        scg_records: The parsed ``RTRV-SCG`` records.
        eqpt_records: The parsed ``RTRV-EQPT`` records.
        ots_aids: The AIDs of the OTS line ports.
        ocrs_records: The parsed ``RTRV-OCRS`` records (``FROMAID``, ``TOAID``, ``PASSBANDLIST``).

    Returns:
        One edge per reachable OTS line port, sorted by line port name.

    Raises:
        ValueError: If the add/drop port is not on a card with known internal rules.
    """
    topology = build_internal_topology(scg_records, eqpt_records, ots_aids)
    if add_drop_port not in topology.card_families:
        msg = f"Add/drop port {add_drop_port} is not on a FlexILS card with known internal connectivity"
        raise ValueError(msg)

    used_by_resource: dict[str, list[tuple[int, int]]] = {}
    fsm_binding: dict[str, str] = {}
    for record in ocrs_records:
        from_aid, to_aid = _record_value(record, "FROMAID"), _record_value(record, "TOAID")
        if not from_aid or not to_aid:
            continue
        src, dst = _strip_channel(from_aid), _strip_channel(to_aid)
        route = topology.route(src, dst) or topology.route(dst, src)
        if route is None:
            continue
        passbands = _passbands_of(record.get("PASSBANDLIST"))
        for hop, next_hop in zip(route, [*route[1:], None], strict=True):
            if (resource := topology.resources.get(hop)) is not None:
                used_by_resource.setdefault(resource, []).extend(passbands)
            if hop in topology.fsm_tributaries and next_hop is not None:
                fsm_binding.setdefault(hop, next_hop)

    edges: list[IntraNodeEdge] = []
    bound_line = fsm_binding.get(add_drop_port)
    for line_port, route in topology.routes_from(add_drop_port):
        if bound_line is not None and (len(route) < 2 or route[1] != bound_line):  # noqa: PLR2004
            continue
        used = [
            passband
            for hop in route
            if (resource := topology.resources.get(hop)) is not None
            for passband in used_by_resource.get(resource, [])
        ]
        edges.append(IntraNodeEdge(add_drop_port, line_port, tuple(merge_intervals(used))))
    return sorted(edges, key=lambda edge: edge.line_port)


def retrieve_add_drop_connectivity(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    add_drop_port: str,
) -> list[IntraNodeEdge]:
    """Retrieve the degrees an add/drop port of a FlexILS node can reach, with the occupancy.

    Args:
        optical_node_block: The Nokia FlexILS node block.
        add_drop_port: AID of the add/drop SCG port.

    Returns:
        One edge per reachable OTS line port.
    """
    flex = get_flex_client(optical_node_block)
    scg_records = _records(flex.rtrv_scg())
    eqpt_records = _records(flex.rtrv_eqpt())
    ots_aids = [aid for record in _records(flex.rtrv_ots()) if (aid := _record_value(record, "AID"))]
    ocrs_records = _all_records(flex.rtrv_ocrs)
    return add_drop_connectivity_from_records(add_drop_port, scg_records, eqpt_records, ots_aids, ocrs_records)
