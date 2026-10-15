"""Device-level, cross-area shared helpers for the Nokia Groove G30 adapter.

Besides the client factory and the port-name parsing, this module holds the Groove G30
card model: the installed cards and subcards are read once
(:func:`g30_modules`) and mapped to the optical functions they provide
(:func:`g30_card_functions`), and that function set is what drives both the node role
(:func:`g30_role`) and the role of each port (see
:mod:`orchestrator.optical.hal.adapters.nokia_groove_g30.port`). The node area and the
port area need the same reading of the hardware, so the reading lives here rather than
in either of them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final

from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.services.nokia import G30Client
from orchestrator.optical.services.nokia.g30.data_models.ne import CardTypeEnum

if TYPE_CHECKING:
    from orchestrator.optical.services.nokia.g30.data_navigators.ne import PortItemNode, SubportItemNode


class G30Function(StrEnum):
    """The optical function a Groove G30 card provides.

    A single card may provide several functions (e.g. ``RD09SM`` is a wavelength selector
    with add/drop ports and two amplifiers, ``CAD16AOFP2`` is an add/drop *and* an
    amplifier). Functions describe what a card *can* do; which OLS role a given port
    takes is decided by the OTS it carries, not by these.
    """

    TRANSPONDER = "T"
    WAVELENGTH_SELECTOR = "W"
    ADD_DROP = "D"
    AMPLIFIER = "A"


#: Highest slot of a Groove G30 carrying optical ports. Both the card model and the port
#: enumeration skip the slots beyond it, so that a module is looked up for every port.
G30_MAX_SLOT_ID: Final = 4


#: The functions of every Groove G30 card. Cards absent from this table perform no
#: role-relevant optical function: the housekeeping cards (``FAN``, ``PSU``, ``FRCU``,
#: ``VIR-SIM``, ``PBMTPP``), the monitoring/protection/dispersion subcards (``OCM``,
#: ``DGE``, ``OPS``, ``OTDR``, ``TDCM``) and the ``OCC2`` carrier itself, which has no
#: function of its own and is expanded to the functions of its installed subcards.
_G30_CARD_FUNCTIONS: Final[dict[CardTypeEnum, frozenset[G30Function]]] = {
    # Transponders and muxponders.
    CardTypeEnum.CHM1: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.CHM1G: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.CHM1LH: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.CHM2: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.CHM2LH: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.CHM2T: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.XTM2: frozenset({G30Function.TRANSPONDER}),
    CardTypeEnum.UTM2: frozenset({G30Function.TRANSPONDER}),
    # Wavelength selectors. A WSS routes part of the line through and drops the rest, so it
    # is an add/drop too; RD09SM also carries two amplifiers.
    CardTypeEnum.WS04SOFP2: frozenset({G30Function.WAVELENGTH_SELECTOR, G30Function.ADD_DROP}),
    CardTypeEnum.RD09SM: frozenset({G30Function.WAVELENGTH_SELECTOR, G30Function.ADD_DROP, G30Function.AMPLIFIER}),
    # Colorless add/drop. CAD16AOFP2 also carries an amplifier.
    CardTypeEnum.CAD8OFP2: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.CAD8EOFP2: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.CAD16AOFP2: frozenset({G30Function.ADD_DROP, G30Function.AMPLIFIER}),
    # Amplifiers: pre-amplifiers and boosters.
    CardTypeEnum.PAOSCOFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.PABAOFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.PAIROFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.PALROFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.PAEROFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.PAULROFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.BAHOFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.BAUOFP2: frozenset({G30Function.AMPLIFIER}),
    CardTypeEnum.BAXOFP2: frozenset({G30Function.AMPLIFIER}),
    # Mux/demux: a fixed band split is a *fixed* add/drop, as opposed to the flexible
    # (colorless) add/drop of the CAD cards. Both drop a signal, so both make the node a
    # FOADM and both expose add/drop ports.
    CardTypeEnum.OMD96: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD64: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD64S: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD48E: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD48_S: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD48_O: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD8B1OFP2: frozenset({G30Function.ADD_DROP}),
    CardTypeEnum.OMD8B2OFP2: frozenset({G30Function.ADD_DROP}),
}


def g30_card_functions(card_type: CardTypeEnum) -> frozenset[G30Function]:
    """Return the role-relevant optical functions the given Groove G30 card provides.

    Empty for the cards that perform no OLS function: the housekeeping cards, the
    monitoring/protection/dispersion subcards, and the ``OCC2`` carrier, which has no
    function of its own and is expanded to the functions of its installed subcards.
    """
    return _G30_CARD_FUNCTIONS.get(card_type, frozenset())


@dataclass(frozen=True)
class G30Module:
    """An installed Groove G30 card or subcard, with the optical functions it provides.

    Attributes:
        card_type: The equipment type reported by the device.
        functions: The role-relevant optical functions of the card (empty for the
            housekeeping and monitoring cards, and for the ``OCC2`` carrier, whose
            functions are those of its installed subcards).
        is_occ2: Whether the module is the ``OCC2`` optical carrier card, i.e. the card
            whose subcards provide the OLS functions.
        slot_id: Id of the slot holding the card.
        subslot_id: Id of the subslot holding the subcard, or ``None`` for a card.
        ots_ids: The ids of the Optical Transmission Sections configured on the node,
            used to tell an OLS line port from an add/drop port. Same set on every
            module of a node; carried here so port enumeration needs a single read.
    """

    card_type: CardTypeEnum
    functions: frozenset[G30Function]
    is_occ2: bool
    slot_id: int
    subslot_id: int | None = None
    ots_ids: frozenset[str] = frozenset()

    @property
    def is_amplifier(self) -> bool:
        """Whether the module provides an amplifier function.

        An amplifier card is bidirectional: its single fiber connection is
        simultaneously the booster's line side and the preamplifier's line side. That
        fiber belongs to the Open Line System rather than to a transponder, but whether
        it is a line or an add/drop port is decided by the OTS it carries, not by the
        card: see ``_g30_port_role``. On a Groove G30 the booster lives in subslot 2 and
        the preamplifier in the port's own subslot, so the subslot identifies which
        amplifier a port belongs to.
        """
        return G30Function.AMPLIFIER in self.functions


def g30_modules(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> list[G30Module]:
    """Read the installed cards and subcards of a Groove G30 node from the device.

    This is the single shelf read of the adapter: the node role and the role of every
    port are both derived from the returned modules, so they cannot disagree about the
    installed hardware. Every ``OCC2`` subcard is returned as its own module, with the
    functions of its card type.

    Args:
        optical_node_block: The Groove G30 node block (any lifecycle variant).

    Returns:
        One module per installed card and subcard.
    """
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")
    optical_interfaces = g30.data.ne_ne.services.optical_interfaces.retrieve(content="config", depth=4)
    ots_ids = frozenset(
        g30_ots_id(ots.ots_name) for ots in (getattr(optical_interfaces, "ots", None) or []) if ots.ots_name
    )

    modules: list[G30Module] = []
    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > G30_MAX_SLOT_ID or not slot.card:
                continue
            is_occ2 = slot.card.required_type == CardTypeEnum.OCC2
            modules.append(
                G30Module(
                    card_type=slot.card.required_type,
                    functions=g30_card_functions(slot.card.required_type),
                    is_occ2=is_occ2,
                    slot_id=slot.slot_id,
                    ots_ids=ots_ids,
                )
            )
            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                modules.append(
                    G30Module(
                        card_type=subslot.subcard.required_type,
                        functions=g30_card_functions(subslot.subcard.required_type),
                        is_occ2=is_occ2,
                        slot_id=slot.slot_id,
                        subslot_id=subslot.subslot_id,
                        ots_ids=ots_ids,
                    )
                )
    return modules


def g30_ots_id(ots_name: str) -> str:
    """Return the id shared by an OTS and its ports (e.g. ``1/3.3/1`` for ``ots-1/3.3/1``)."""
    return ots_name.split("-", 1)[-1]


def g30_node_functions(modules: list[G30Module]) -> frozenset[G30Function]:
    """Return the optical functions provided by the given Groove G30 modules.

    The functions of the ``OCC2`` carrier are those of its installed subcards, so the
    carrier contributes nothing on its own.
    """
    return frozenset().union(*(module.functions for module in modules)) if modules else frozenset()


def g30_role(functions: frozenset[G30Function], fqdn: str | None = None) -> OpticalNodeRole:
    """Return the role of a Groove G30 node from the optical functions its cards provide.

    A wavelength selector dominates: a shelf with a WSS is a ROADM whatever else it
    carries. The WSS provides add/drops of its own, so the order of the checks below is
    load-bearing -- testing add/drop first would demote every ROADM to a FOADM. Without a
    WSS, an add/drop function makes the node a FOADM (a fixed mux/demux is a *fixed*
    add/drop, a colorless add/drop a flexible one). Amplifiers alone make the node an
    amplifier; alongside a transponder card they do not change its role, since the
    amplifier is then part of the transponder rather than a standalone OLS element.

    Args:
        functions: The node's optical functions, see :func:`g30_node_functions`.
        fqdn: The node FQDN, used in the error message only.

    Returns:
        The OpticalNodeRole of the node.

    Raises:
        ValueError: If the node provides no role-relevant optical function, i.e. it has
            no optical cards installed at all, or if it provides a function that this
            mapping does not translate into a role.
    """
    where = f" on {fqdn}" if fqdn else ""
    if not functions:
        msg = f"No optical function found on the Groove G30 node{where}"
        raise ValueError(msg)

    has_transponder = G30Function.TRANSPONDER in functions
    has_add_drop = G30Function.ADD_DROP in functions
    has_selector = G30Function.WAVELENGTH_SELECTOR in functions
    has_amplifier = G30Function.AMPLIFIER in functions

    if has_selector:
        return OpticalNodeRole.TRANSPONDER_ROADM if has_transponder else OpticalNodeRole.ROADM
    if has_add_drop:
        return OpticalNodeRole.TRANSPONDER_FOADM if has_transponder else OpticalNodeRole.FOADM
    if has_transponder:
        return OpticalNodeRole.TRANSPONDER
    if has_amplifier:
        return OpticalNodeRole.AMPLIFIER

    # Nothing above matched: raise rather than fall through, so a G30Function added
    # later without a role cannot be called an amplifier. Unmapped beside mapped is
    # fine -- the mapped role wins above.
    unmapped = ", ".join(sorted(functions))
    msg = f"Optical function(s) [{unmapped}] on the Groove G30 node{where} map to no node role"
    raise ValueError(msg)


def get_g30_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> G30Client:
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
    g30_device_block: AnyOpticalNodeBlockProvisioningUnion,
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
