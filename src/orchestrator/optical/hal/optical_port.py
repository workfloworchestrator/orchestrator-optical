"""Services for the Optical Port product blocks of all supported vendors.

This module provides the device-level operations used by Optical Port
subscriptions: port discovery, description and administrative state
configuration, fiber termination configuration (when attaching or removing a
fiber) and fiber termination validation.

Operations are dispatched on the vendor of the Optical Node product block
hosting the port with match/case statements, replacing the legacy
attribute-based dispatch on the ``platform`` attribute of the old
``OpticalDeviceBlock``.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal, cast

from orchestrator.optical.hal.optical_node import (
    Vendor,
    get_flex_client,
    get_g30_client,
    get_g42_client,
    vendor_of,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.abstracts import AbstractOpticalPortBlockInactive
from orchestrator.optical.services.nokia import TL1CommandDeniedError
from orchestrator.optical.services.nokia.g30.data_models.ne import (
    AdminStatusEnum,
    CardTypeEnum,
    ControlModeEnum,
    EnableSwitchEnum,
    EquipmentTypeEnum_1,
    GainRangeControlEnum,
    GainRangeTypeEnum,
    PortModeEnum,
    TiltControlModeEnum,
    YesNoEnum,
)
from orchestrator.optical.services.nokia.g42.data_models.ioa_network_element import (
    AdminStateEnum,
    ExternalConnectivityEnum,
    PortTypeEnum,
)

if TYPE_CHECKING:
    from orchestrator.optical.services.nokia.g30.data_navigators.ne import PortItemNode, SubportItemNode

OpticalNodeBlock = AbstractOpticalNodeBlock | AbstractOpticalNodeBlockProvisioning | AbstractOpticalNodeBlockInactive


def _as_flexils_block(optical_node_block: AbstractOpticalNodeBlockInactive) -> NokiaFlexIlsBlockInactive:
    """Narrow an Optical Node block to the Nokia FlexILS block type."""
    if not isinstance(optical_node_block, NokiaFlexIlsBlockInactive):
        msg = f"Expected a NokiaFlexIlsBlock, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _port_name(optical_port_block: AbstractOpticalPortBlockInactive) -> str:
    """Return the device-side name of the given Optical Port product block."""
    port_name = optical_port_block.optical_port_name
    if port_name is None:
        msg = f"Optical Port block {type(optical_port_block).__name__} has no port name"
        raise ValueError(msg)
    return port_name


def _node_id(optical_node_block: AbstractOpticalNodeBlockInactive) -> str:
    """Return the node id (fqdn) of the given Optical Node block."""
    fqdn = optical_node_block.management.optical_module_node_fqdn
    if fqdn is None:
        msg = f"Optical Node block {type(optical_node_block).__name__} has no fqdn"
        raise ValueError(msg)
    return fqdn


def _same_node(
    node_a: AbstractOpticalNodeBlockInactive,
    node_b: AbstractOpticalNodeBlockInactive,
) -> bool:
    """Return whether two Optical Node blocks refer to the same device."""
    if node_a is node_b:
        return True
    fqdn_a = node_a.management.optical_module_node_fqdn
    fqdn_b = node_b.management.optical_module_node_fqdn
    return fqdn_a is not None and fqdn_a == fqdn_b


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


def _retrieve_transceiver_modes_g30(optical_node_block: OpticalNodeBlock, port_name: str) -> list[str]:
    """Return the supported transceiver modes of a Groove G30 line port."""
    # fmt: off
    mapping = {
        CardTypeEnum.CHM1: [
            "not-applicable",      "QPSK_100G",          "16QAM_200G",          "8QAM_300G",
        ],
        CardTypeEnum.CHM2T: [
            "16QAM_200G",          "16QAM_300G",         "16QAM_32QAM_400G",    "16QAM_32QAM_500G",
            "16QAM_400G",          "32QAM_200G",          "32QAM_300G",          "32QAM_400G",
            "32QAM_500G",          "32QAM_64QAM_500G",    "32QAM_64QAM_600G",    "64QAM_300G",
            "64QAM_400G",          "64QAM_500G",          "64QAM_600G",          "QPSK_100G",
            "QPSK_200G",           "QPSK_SP16QAM_200G",   "QPSK_SP16QAM_300G",   "SP16QAM_16QAM_200G",
            "SP16QAM_16QAM_300G",  "SP16QAM_16QAM_400G",  "SP16QAM_200G",        "SP16QAM_300G",
            "SPQPSK_100G",         "SPQPSK_QPSK_100G",    "SPQPSK_QPSK_200G",    "not-applicable",
        ],
    }
    # fmt: on

    shelf_id, slot_id, _, _, _ = g30_ids_from_port_name(port_name)

    g30 = get_g30_client(optical_node_block)

    card = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.retrieve(depth=2)

    card_type = card.required_type

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


def _retrieve_transceiver_modes_g42(optical_node_block: OpticalNodeBlock, port_name: str) -> list[str]:
    """Return the supported transceiver modes of a GX G42 line port."""
    # fmt: off
    mapping = {
        "C6": [
            "100E.31U", "100E.70U", "100M.33U", "100M.73U", "150E.31P", "150E.31U", "150E.35U",
            "150E.42P", "150E.44P", "150E.70U", "150E.84U", "150M.33P", "150M.33U", "150M.36U",
            "150M.44P", "150M.46P", "150M.73U", "150M.87U", "200E.31P", "200E.31U", "200E.35U",
            "200E.42P", "200E.42U", "200E.45P", "200E.50P", "200E.63P", "200E.63U", "200E.70U",
            "200E.80U", "200E.93U", "200M.33P", "200M.33U", "200M.36U", "200M.44P", "200M.44U",
            "200M.47P", "200M.52P", "200M.66P", "200M.66U", "200M.73U", "200M.83U", "250E.31P",
            "250E.31U", "250E.35U", "250E.42P", "250E.50P", "250E.63P", "250E.63U", "250E.72P",
            "250E.84P", "250E.87U", "250M.33P", "250M.33U", "250M.36U", "250M.44P", "250M.52P",
            "250M.66P", "250M.66U", "250M.75P", "250M.82U", "250M.87P", "250M.91U", "300E.31U",
            "300E.42P", "300E.44P", "300E.50P", "300E.63P", "300E.63U", "300E.64P", "300E.65P",
            "300E.67P", "300E.68P", "300E.70P", "300E.72P", "300E.73P", "300E.75P", "300E.84P",
            "300E.89P", "300E.91P", "300E.94P", "300M.33U", "300M.44P", "300M.46P", "300M.52P",
            "300M.66P", "300M.66U", "300M.67P", "300M.68P", "300M.70P", "300M.71P", "300M.73P",
            "300M.75P", "300M.77P", "300M.79P", "300M.87P", "300M.92P", "300M.95P", "350E.42P",
            "350E.50P", "350E.63P", "350E.63U", "350E.72P", "350E.84P", "350M.44P", "350M.52P",
            "350M.66P", "350M.66U", "350M.75P", "350M.87P", "400E.42U", "400E.45P", "400E.50P",
            "400E.63P", "400E.63U", "400E.65P", "400E.67P", "400E.69P", "400E.72P", "400E.74P",
            "400E.84P", "400E.84U", "400E.91P", "400E.96P", "400M.44U", "400M.47P", "400M.52P",
            "400M.66P", "400M.66U", "400M.68P", "400M.70P", "400M.72P", "400M.75P", "400M.78P",
            "400M.87P", "400M.87U", "400M.95P", "450E.63P", "450E.63U", "450E.64P", "450E.65P",
            "450E.66P", "450E.67P", "450E.68P", "450E.70P", "450E.71P", "450E.72P", "450E.73P",
            "450E.74P", "450E.75P", "450E.81U", "450E.84P", "450E.89P", "450E.94P", "450M.66P",
            "450M.66U", "450M.67P", "450M.68P", "450M.69P", "450M.70P", "450M.71P", "450M.73P",
            "450M.74P", "450M.75P", "450M.76P", "450M.77P", "450M.79P", "450M.84U", "450M.87P",
            "450M.92P", "500E.63P", "500E.63U", "500E.67P", "500E.72P", "500E.84P", "500E.84U",
            "500E.91P", "500M.66P", "500M.66U", "500M.70P", "500M.75P", "500M.87P", "500M.87U",
            "500M.95P", "550E.63P", "550E.63U", "550E.72P", "550E.84P", "550E.86U", "550M.66P",
            "550M.66U", "550M.75P", "550M.87P", "550M.90U", "600E.63U", "600E.65P", "600E.68P",
            "600E.72P", "600E.75P", "600E.84P", "600E.84U", "600E.89P", "600E.91P", "600E.94P",
            "600E.94U", "600E.96P", "600M.66U", "600M.68P", "600M.71P", "600M.75P", "600M.79P",
            "600M.87P", "600M.87U", "600M.92P", "600M.95P", "650E.82U", "650E.84P", "650M.85U",
            "650M.87P", "700E.80U", "700E.84P", "700E.91P", "700M.83U", "700M.87P", "700M.95P",
            "750E.82U", "750E.84P", "750E.89P", "750E.94P", "750M.85U", "750M.87P", "750M.92P",
            "800E.84U", "800E.91P", "800E.96P", "800M.87U", "800M.95P"
        ],
        "C14": [
            "100E.31H", "100E.31U", "150E.31H", "150E.31P", "150E.31S", "150E.31U", "150E.42P",
            "150E.42S", "150E.44P", "150E.44S", "150E.84H", "150E.84U", "200E.31H", "200E.31P",
            "200E.31S", "200E.31U", "200E.42H", "200E.42P", "200E.42S", "200E.42U", "200E.63H",
            "200E.63P", "200E.63S", "200E.63U", "250E.31P", "250E.31S", "250E.31U", "250E.42P",
            "250E.42S", "250E.63H", "250E.63P", "250E.63S", "250E.63U", "250E.72P", "250E.72S",
            "250E.84P", "250E.84S", "300E.31U", "300E.42P", "300E.42S", "300E.44P", "300E.44S",
            "300E.63H", "300E.63P", "300E.63S", "300E.63U", "300E.72P", "300E.72S", "300E.84P",
            "300E.84S", "300E.89P", "300E.89S", "300E.94P", "300E.94S", "350E.42P", "350E.42S",
            "350E.63H", "350E.63P", "350E.63S", "350E.63U", "350E.72P", "350E.72S", "350E.84P",
            "350E.84S", "400E.42U", "400E.63H", "400E.63P", "400E.63S", "400E.63U", "400E.72P",
            "400E.72S", "400E.84H", "400E.84P", "400E.84S", "400E.84U", "450E.63P", "450E.63S",
            "450E.63U", "450E.66P", "450E.66S", "450E.72P", "450E.72S", "450E.84P", "450E.84S",
            "450E.89P", "450E.89S", "450E.94P", "450E.94S", "500E.63P", "500E.63S", "500E.63U",
            "500E.72P", "500E.72S", "500E.84H", "500E.84P", "500E.84S", "500E.84U", "550E.63P",
            "550E.63S", "550E.63U", "550E.72P", "550E.72S", "550E.84P", "550E.84S", "600E.63U",
            "600E.72P", "600E.72S", "600E.84P", "600E.84S", "600E.84U", "600E.89P", "600E.89S",
            "600E.94H", "600E.94P", "600E.94S", "600E.94U", "650E.84P", "650E.84S", "700E.84P",
            "700E.84S", "750E.84P", "750E.84S", "750E.89P", "750E.89S", "750E.94P", "750E.94S",
            "800E.84U"
        ]
    }
    # fmt: on

    shelf_id, slot_id, _ = port_name.split("-")  # 1-4-L1 --> 1, 4, L1

    g42 = get_g42_client(optical_node_block)

    card = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").retrieve(depth=2, content="config")
    card_type = card.required_subtype

    supported_modes = mapping.get(card_type) if card_type is not None else None

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


def retrieve_transceiver_modes(optical_node_block: OpticalNodeBlock, port_name: str) -> list[str]:
    """Retrieve the list of supported transceiver modes for a specific port on an Optical Node.

    Args:
        optical_node_block: The Optical Node containing the port.
        port_name: The name of the port for which to retrieve the modes.

    Returns:
        A list of supported modes for the specified port.

    Raises:
        ValueError: If the card of the port is not supported.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _retrieve_transceiver_modes_g30(optical_node_block, port_name)
        case Vendor.GX_G42:
            return _retrieve_transceiver_modes_g42(optical_node_block, port_name)
        case Vendor.FLEXILS:
            return []
        case _:
            msg = f"No implementation of retrieve_transceiver_modes found for {type(optical_node_block).__name__}"
            raise TypeError(msg)


def _flex_scg_aids(flex: Any) -> list[str]:
    """Return the SCG AIDs of a FlexILS node, tolerating nodes without SCGs."""
    try:
        return [str(x["AID"]) for x in flex.rtrv_scg().parsed_data]
    except TL1CommandDeniedError as e:
        if "INPUT, SPECIFIED OBJECT ENTITY DOES NOT EXIST" not in e.response:
            raise
        return []


def _flex_get_device_ports_names(optical_node_block: NokiaFlexIlsBlockInactive) -> list[str]:
    """Return the SCG and OTS AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    scg_aids = _flex_scg_aids(flex)
    ots_aids = [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]
    return scg_aids + ots_aids


def _g30_get_device_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Return the aliases of all the ports of a Groove G30 node."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    ports_name: list[str] = []
    max_slot_id_with_useful_ports = 4
    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            ports_name.extend(p.alias_name for p in (slot.card.port or []) if p.alias_name is not None)

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                for port in subslot.subcard.port or []:
                    if port.alias_name is not None:
                        ports_name.append(port.alias_name)
                    if port.subport:
                        ports_name.extend(sp.alias_name for sp in port.subport if sp.alias_name is not None)

    return ports_name


def _g42_get_device_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Return the AIDs of all the ports of a GX G42 node."""
    g42 = get_g42_client(optical_node_block)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports: list[str] = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(
                p.AID
                for p in (card.port or [])
                if p.AID is not None and (p.port_type == PortTypeEnum.LINE or p.installed_type)
            )

    return ports


def get_device_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Retrieve the list of optical port names of an Optical Node.

    Args:
        optical_node_block: Optical Node of which the optical ports are to be retrieved.

    Returns:
        A list of optical port names of the optical node.

    Raises:
        TypeError: In case the Optical Node is not supported by this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _flex_get_device_ports_names(_as_flexils_block(optical_node_block))
        case Vendor.GROOVE_G30:
            return _g30_get_device_ports_names(optical_node_block)
        case Vendor.GX_G42:
            return _g42_get_device_ports_names(optical_node_block)
        case _:
            msg = f"No implementation of get_device_ports_names found for {type(optical_node_block).__name__}"
            raise TypeError(msg)


def _flex_get_device_client_ports_names(optical_node_block: NokiaFlexIlsBlockInactive) -> list[str]:
    """Return the SCG AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    return _flex_scg_aids(flex)


def _g30_get_device_client_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Return the aliases of the client ports of a Groove G30 node."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    ports_name: list[str] = []
    max_slot_id_with_useful_ports = 4

    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            for port in slot.card.port or []:
                is_sub_interface = "." in (port.alias_name or "")
                is_in_client_range = 3 <= port.port_id <= 12  # noqa: PLR2004

                if (is_sub_interface or is_in_client_range) and port.alias_name is not None:
                    ports_name.append(port.alias_name)

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                for port in subslot.subcard.port or []:
                    if port.alias_name is not None:
                        ports_name.append(port.alias_name)
                    if port.subport:
                        ports_name.extend(sp.alias_name for sp in port.subport if sp.alias_name is not None)

    return ports_name


def _g42_get_device_client_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Return the AIDs of the client ports of a GX G42 node."""
    g42 = get_g42_client(optical_node_block)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports: list[str] = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in (card.port or []) if p.AID is not None and p.installed_type)

    return ports


def get_device_client_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Retrieve the list of client optical port names of an Optical Node.

    Args:
        optical_node_block: Optical Node of which the client optical ports are to be retrieved.

    Returns:
        A list of client optical port names of the optical node.

    Raises:
        TypeError: In case the Optical Node is not supported by this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _flex_get_device_client_ports_names(_as_flexils_block(optical_node_block))
        case Vendor.GROOVE_G30:
            return _g30_get_device_client_ports_names(optical_node_block)
        case Vendor.GX_G42:
            return _g42_get_device_client_ports_names(optical_node_block)
        case _:
            msg = f"No implementation of get_device_client_ports_names found for {type(optical_node_block).__name__}"
            raise TypeError(msg)


def _flex_get_device_line_ports_names(optical_node_block: NokiaFlexIlsBlockInactive) -> list[str]:
    """Return the OTS AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    return [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]


def _g30_get_device_line_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Return the aliases of the line ports of a Groove G30 node."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=5, content="config")

    ports_name: list[str] = []
    max_slot_id_with_useful_ports = 4

    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            for port in slot.card.port or []:
                is_in_line_range = 1 <= (port.port_id or 999) <= 2  # noqa: PLR2004

                if is_in_line_range and port.alias_name is not None:
                    ports_name.append(port.alias_name)

    return ports_name


def _g42_get_device_line_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Return the AIDs of the line ports of a GX G42 node."""
    g42 = get_g42_client(optical_node_block)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports: list[str] = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in (card.port or []) if p.AID is not None and p.port_type == PortTypeEnum.LINE)

    return ports


def get_device_line_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Retrieve the list of line optical port names of an Optical Node.

    Args:
        optical_node_block: Optical Node of which the line optical ports are to be retrieved.

    Returns:
        A list of line optical port names of the optical node.

    Raises:
        TypeError: In case the Optical Node is not supported by this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _flex_get_device_line_ports_names(_as_flexils_block(optical_node_block))
        case Vendor.GROOVE_G30:
            return _g30_get_device_line_ports_names(optical_node_block)
        case Vendor.GX_G42:
            return _g42_get_device_line_ports_names(optical_node_block)
        case _:
            msg = f"No implementation of get_device_line_ports_names found for {type(optical_node_block).__name__}"
            raise TypeError(msg)


def set_port_description(
    optical_port_block: AbstractOpticalPortBlockInactive,
    port_description: str,
) -> dict[str, Any]:
    """Set the description of an optical port.

    Args:
        optical_port_block: Optical Port of which the description is to be set.
        port_description: The description to set on the port.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = optical_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    match vendor_of(host_node):
        case Vendor.FLEXILS:
            flex = cast(Any, get_flex_client(_as_flexils_block(host_node)))  # TL1 methods are bound dynamically
            if "L" in port_name:
                flex.ed_ots(aid=port_name, label=rf'"{port_description}"')
                return flex.rtrv_ots(aid=port_name).model_dump()
            flex.ed_scg(aid=port_name, label=rf'"{port_description}"')
            return flex.rtrv_scg(aid=port_name).model_dump()
        case Vendor.GROOVE_G30:
            endpoint, _, _, _, _, _ = g30_port_navigator_node_from_port_name(host_node, port_name)
            endpoint.update(service_label=port_description)
            return endpoint.retrieve(content="config", depth=2).model_dump()
        case Vendor.GX_G42:
            shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
            g42 = get_g42_client(host_node)
            port_uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)

            port_config = port_uri.retrieve(content="config", depth=2)
            port_config.label = port_description

            port_uri.update(port_config)

            return port_uri.retrieve(content="config", depth=2).model_dump()
        case _:
            msg = f"No implementation of set_port_description found for {type(host_node).__name__}"
            raise TypeError(msg)


def set_channel_description(
    optical_node_block: OpticalNodeBlock,
    facility_id: str,
    description: str,
) -> dict[str, Any]:
    """Set the description of an optical channel.

    Args:
        optical_node_block: Optical Node of which the optical channel is to be modified.
        facility_id: The id of the optical channel to set the description on (e.g. ``"1/1/1"``).
        description: The description to set on the channel.

    Returns:
        The channel configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            g30 = get_g30_client(optical_node_block)
            shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(facility_id)
            uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os

            och_os = uri.retrieve(content="config", depth=2)
            och_os.service_label = description
            uri.update(och_os)

            return uri.retrieve(content="config", depth=2).model_dump()
        case Vendor.GX_G42:
            g42 = get_g42_client(optical_node_block)
            port_name = facility_id  # e.g. "1-4-L2"

            channel_name = None
            channels = g42.data.ne.facilities.super_channel.retrieve(depth=2, content="config")
            for ch in channels:
                if any(carrier.startswith(port_name) for carrier in ch.carriers):
                    channel_name = ch.name
                    break

            if channel_name is None:
                msg = f"Channel with port {port_name} not found"
                raise ValueError(msg)

            uri = g42.data.ne.facilities.super_channel(channel_name)
            conf = uri.retrieve(depth=2, content="config")
            conf.label = description
            uri.update(conf)
            return uri.retrieve(depth=2, content="config").model_dump()
        case Vendor.FLEXILS:
            return {"not-applicable": "Nokia FlexILS devices do not support channel descriptions"}
        case _:
            msg = f"No implementation of set_channel_description found for {type(optical_node_block).__name__}"
            raise TypeError(msg)


def _set_port_admin_state_flexils(
    optical_port_block: AbstractOpticalPortBlockInactive,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Set the administrative state of a Nokia FlexILS port.

    FlexILS has 3 admin states for the tributary ports: IS (in service), OOS (out of
    service), and MT (maintenance). Line ports (OTS) can only be in IS or MT state.
    It works as a finite state machine with the following transitions:
    OOS <-edit---edit-> IS <-rst---put-> MT.
    """
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)

    # Line ports (OTS)
    if "L" in port_name:
        if admin_state == "down":
            msg = "Line ports (OTS) can only be in service (IS) or maintenance (MT) state"
            raise ValueError(msg)
        if admin_state == "maintenance":
            flex.put_maintenance(aidtype="OTS", aid=port_name)
        elif admin_state == "up":
            flex.rst_maintenance(aidtype="OTS", aid=port_name)
        return flex.rtrv_ots(aid=port_name).model_dump()

    # Tributary ports (SCG)
    # from any state to in-service state (we must know the current state of the
    # finite state machine to move between states)
    try:
        flex.ed_scg(aid=port_name, is_oos="IS")
    except TL1CommandDeniedError as e:
        if "use RST command" not in e.response:
            raise
        flex.rst_maintenance(aidtype="SCG", aid=port_name)
    # from in-service state to desired state
    if admin_state == "up":
        pass
    elif admin_state == "down":
        flex.ed_scg(aid=port_name, is_oos="OOS")
    elif admin_state == "maintenance":
        flex.put_maintenance(aidtype="SCG", aid=port_name)

    return flex.rtrv_scg(aid=port_name).model_dump()


def set_port_admin_state(
    optical_port_block: AbstractOpticalPortBlockInactive,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Set the administrative state of an optical port.

    Args:
        optical_port_block: Optical Port of which the admin state is to be set.
        admin_state: The administrative state to set on the port: ["up", "down", "maintenance"].

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = optical_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    match vendor_of(host_node):
        case Vendor.FLEXILS:
            return _set_port_admin_state_flexils(optical_port_block, admin_state)
        case Vendor.GROOVE_G30:
            mapping = {
                "up": AdminStatusEnum.UP,
                "down": AdminStatusEnum.DOWN,
                "maintenance": AdminStatusEnum.UP_NO_ALM,
            }
            status = mapping[admin_state]

            port_uri = g30_port_navigator_node_from_port_name(host_node, port_name)[0]

            port_uri.update(admin_status=status)
            return port_uri.retrieve(depth=2, content="config").model_dump()
        case Vendor.GX_G42:
            mapping = {
                "up": AdminStateEnum.UNLOCK,
                "down": AdminStateEnum.LOCK,
                "maintenance": AdminStateEnum.MAINTENANCE,
            }
            status = mapping[admin_state]

            shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

            g42 = get_g42_client(host_node)
            uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)

            conf = uri.retrieve(content="config", depth=2)
            conf.admin_state = status
            uri.update(conf)

            return uri.retrieve(depth=2).model_dump()
        case _:
            msg = f"No implementation of set_port_admin_state found for {type(host_node).__name__}"
            raise TypeError(msg)


def flexils_check_port_is_in_manualmode2_else_set_it(optical_port_block: AbstractOpticalPortBlockInactive) -> None:
    """Ensure the given FlexILS SCG port is in MANUALMODE-2, setting it there if needed.

    Args:
        optical_port_block: Optical Port of the FlexILS SCG port to check and configure.

    Raises:
        ValueError: In case the configuration failed.
    """
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    scg = flex.rtrv_scg(aid=port_name).parsed_data[0]

    if scg["INTFTYP"] != "MANUALMODE-2":
        card_aid = port_name.split("-")[:-1]
        card_aid = "-".join(card_aid)
        card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]

        if card["TYPE"] in ["FSM", "FRM"]:
            # tributary ports of FSM and system ports of FRM cards can only be unlocked or locked
            set_port_admin_state(optical_port_block, "down")
        else:
            set_port_admin_state(optical_port_block, "maintenance")

        flex.ed_scg(aid=port_name, intftyp="MANUALMODE-2")

    set_port_admin_state(optical_port_block, "up")


def _get_remote_node_id(remote_port_block: AbstractOpticalPortBlockInactive) -> str:
    """Extract the node id of the device hosting the remote port, based on its vendor.

    Args:
        remote_port_block: Optical Port product block of the remote port.

    Returns:
        The Groove G30 shelf serial number, or the fqdn for the other vendors.

    Raises:
        ValueError: If the node id cannot be determined.
    """
    host_node = remote_port_block.optical_port_host_node
    match vendor_of(host_node):
        case Vendor.GROOVE_G30:
            g30 = get_g30_client(host_node)
            inventory = g30.data.ne_ne.inventory_data.inventory.retrieve(depth=2)

            for item in inventory:
                if item.equipment_type == EquipmentTypeEnum_1.SHELF and item.shelf_id == 1:
                    serial_number = item.serial_number
                    if serial_number is None:
                        msg = (
                            f"Shelf 1 of G30 device "
                            f"{host_node.management.optical_module_node_fqdn} has no serial number"
                        )
                        raise ValueError(msg)
                    return serial_number

            msg = f"Could not find shelf serial number for G30 device {host_node.management.optical_module_node_fqdn}"
            raise ValueError(msg)
        case Vendor.GX_G42 | Vendor.FLEXILS:
            return _node_id(host_node)
        case _:
            msg = f"Unsupported remote platform for FlexILS connection: {type(host_node).__name__}"
            raise ValueError(msg)


def _extract_remote_port_id(port_name: str) -> str:
    """Extract and format the port id from a port name.

    Args:
        port_name: The name of the remote port.

    Returns:
        The port id, starting from the first digit of the name, with every
        non-alphanumeric character replaced by a dash.

    Raises:
        ValueError: If no digit can be found in the port name.
    """
    match = re.search(r"\d", port_name)
    if not match:
        msg = f"Could not extract port identifier from remote port name: {port_name}"
        raise ValueError(msg)
    port_id = port_name[match.start() :]
    return re.sub(r"[^a-zA-Z0-9]", "-", port_id)


def _configure_termination_flexils(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Configure a Nokia FlexILS port when attaching a fiber to it."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    description = optical_port_block.optical_port_description or ""

    # Handle FlexILS-to-FlexILS connection separately (simpler case)
    if vendor_of(remote_port_block.optical_port_host_node) == Vendor.FLEXILS:
        flex.ed_ots(aid=port_name, label=rf'"{description}"')
        flex.rst_maintenance(aidtype="OTS", aid=port_name)
        return flex.rtrv_ots(aid=port_name).model_dump()

    # Handle FlexILS connections to other platform types
    flexils_check_port_is_in_manualmode2_else_set_it(optical_port_block)

    remote_node_id = _get_remote_node_id(remote_port_block)
    remote_port_id = _extract_remote_port_id(_port_name(remote_port_block))
    provowremptp = f"{remote_node_id}/{remote_port_id}"
    flex.ed_scg(
        aid=port_name,
        provowremptp=provowremptp,
        label=rf'"{description}"',
    )

    return flex.rtrv_scg(aid=port_name).model_dump()


def _configure_termination_g30(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Configure a Groove G30 port when attaching a fiber to it."""
    host_node = optical_port_block.optical_port_host_node
    remote_host_node = remote_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    remote_port_name = _port_name(remote_port_block)

    endpoint, shelf_id, slot_id, subslot_id, port_id, _ = g30_port_navigator_node_from_port_name(host_node, port_name)

    match vendor_of(remote_host_node):
        case Vendor.FLEXILS:
            endpoint.update(
                external_connectivity=YesNoEnum.YES,
                connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
                admin_status=AdminStatusEnum.UP,
            )
            return endpoint.retrieve(depth=2, content="config").model_dump()
        case Vendor.GROOVE_G30:
            is_same_device = _same_node(host_node, remote_host_node)
            is_amplifier_port = slot_id == 3 and subslot_id == 3 and port_id == 1  # noqa: PLR2004

            if is_same_device:
                endpoint.update(
                    external_connectivity=YesNoEnum.NO,
                    connected_to=f"patched to {remote_port_name}",
                    admin_status=AdminStatusEnum.UP,
                )
                return endpoint.retrieve(depth=2, content="config").model_dump()

            if not is_amplifier_port:
                endpoint.update(
                    external_connectivity=YesNoEnum.YES,
                    connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
                    admin_status=AdminStatusEnum.UP,
                )
                return endpoint.retrieve(depth=2, content="config").model_dump()

            # link H4: the port is an amplifier port of a different Groove G30 device
            if subslot_id is None:
                msg = "Amplifier port configuration requires a subslot id"
                raise ValueError(msg)

            g30 = get_g30_client(host_node)

            booster_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(2).subcard.amplifier("ba")
            booster = booster_uri.retrieve(content="config", depth=2)
            booster.admin_status = AdminStatusEnum.UP
            booster.amplifier_enable = EnableSwitchEnum.ENABLED
            booster.input_los_shutdown = EnableSwitchEnum.DISABLED
            booster.control_mode = ControlModeEnum.MANUAL
            booster.gain_range_control = GainRangeControlEnum.MANUAL
            booster.target_gain_range = GainRangeTypeEnum.STANDARD
            booster.target_gain = Decimal("22.0")
            booster.output_voa = Decimal("10.0")
            booster.tilt_control_mode = TiltControlModeEnum.MANUAL
            booster.gain_tilt = Decimal("0.0")
            booster_uri.update(booster)

            preamp_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.amplifier("pa")
            preamp = preamp_uri.retrieve(content="config", depth=2)
            preamp.admin_status = AdminStatusEnum.UP
            preamp.amplifier_enable = EnableSwitchEnum.ENABLED
            preamp.input_los_shutdown = EnableSwitchEnum.DISABLED
            preamp.control_mode = ControlModeEnum.AUTO
            preamp.gain_range_control = GainRangeControlEnum.AUTO
            preamp.target_gain_range = GainRangeTypeEnum.STANDARD
            preamp.tilt_control_mode = TiltControlModeEnum.AUTO
            preamp_uri.update(preamp)

            endpoint.update(
                external_connectivity=YesNoEnum.YES,
                connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
                admin_status=AdminStatusEnum.UP,
            )

            return {
                "port": endpoint.retrieve(depth=2, content="config").model_dump(),
                "booster": booster_uri.retrieve(depth=2, content="config").model_dump(),
                "preamp": preamp_uri.retrieve(depth=2, content="config").model_dump(),
            }
        case _:
            msg = (
                "Unsupported remote optical device platform when configuring Groove G30 remote port: "
                f"{type(remote_host_node).__name__}"
            )
            raise ValueError(msg)


def _configure_termination_g42(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Configure a GX G42 port when attaching a fiber to it."""
    host_node = optical_port_block.optical_port_host_node
    shelf_id, slot_id, port_id = _port_name(optical_port_block).split("-")
    g42 = get_g42_client(host_node)
    uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    uri.update(
        name=port_id,
        external_connectivity=ExternalConnectivityEnum.YES,
        connected_to=f"{_node_id(remote_port_block.optical_port_host_node)} {_port_name(remote_port_block)}",
        admin_state=AdminStateEnum.UNLOCK,
    )
    return uri.retrieve(content="config", depth=2).model_dump()


def configure_termination_when_attaching_new_fiber(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Configure an optical port when attaching a fiber to it.

    Args:
        optical_port_block: Optical Port to configure.
        remote_port_block: The remote Optical Port to connect to.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = optical_port_block.optical_port_host_node
    match vendor_of(host_node):
        case Vendor.FLEXILS:
            return _configure_termination_flexils(optical_port_block, remote_port_block)
        case Vendor.GROOVE_G30:
            return _configure_termination_g30(optical_port_block, remote_port_block)
        case Vendor.GX_G42:
            return _configure_termination_g42(optical_port_block, remote_port_block)
        case _:
            msg = (
                "No implementation of configure_termination_when_attaching_new_fiber found for "
                f"{type(host_node).__name__}"
            )
            raise TypeError(msg)


def _factory_reset_flexils(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Prune the configuration of a Nokia FlexILS port."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)

    if vendor_of(remote_port_block.optical_port_host_node) == Vendor.FLEXILS:
        flex.ed_ots(aid=port_name, label=r'""')
        return flex.rtrv_ots(aid=port_name).model_dump()

    set_port_admin_state(optical_port_block, "maintenance")
    flex.ed_scg(
        aid=port_name,
        intftyp="MANUALMODE-2",
        provowremptp=r'""',
        label=r'""',
    )
    set_port_admin_state(optical_port_block, "down")
    return flex.rtrv_scg(aid=port_name).model_dump()


def _factory_reset_g30(optical_port_block: AbstractOpticalPortBlockInactive) -> dict[str, Any]:
    """Prune the configuration of a Groove G30 port."""
    host_node = optical_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    port_uri = g30_port_navigator_node_from_port_name(host_node, port_name)[0]

    if "." in port_name:  # inside OCC2 card
        port_uri.update(connected_to="")
    else:
        port_uri.update(
            external_connectivity=YesNoEnum.NO,
            connected_to="",
            admin_status=AdminStatusEnum.DOWN,
            port_mode=PortModeEnum.NOT_APPLICABLE,
            service_label="",
        )

    return port_uri.retrieve(content="config", depth=2).model_dump()


def _factory_reset_g42(optical_port_block: AbstractOpticalPortBlockInactive) -> dict[str, Any]:
    """Prune the configuration of a GX G42 port."""
    host_node = optical_port_block.optical_port_host_node
    g42 = get_g42_client(host_node)
    shelf_id, slot_id, port_id = _port_name(optical_port_block).split("-")
    uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = uri.retrieve(content="config", depth=2)
    conf.external_connectivity = ExternalConnectivityEnum.NO
    conf.connected_to = ""
    conf.admin_state = AdminStateEnum.LOCK
    conf.label = ""
    uri.update(conf)
    return uri.retrieve(content="config", depth=2).model_dump()


def factory_reset_port_configuration(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Prune the configuration of an optical port.

    Args:
        optical_port_block: Optical Port of which the configuration is to be pruned.
        remote_port_block: The remote Optical Port connected to the port.

    Returns:
        The port configuration after the reset.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = optical_port_block.optical_port_host_node
    match vendor_of(host_node):
        case Vendor.FLEXILS:
            return _factory_reset_flexils(optical_port_block, remote_port_block)
        case Vendor.GROOVE_G30:
            return _factory_reset_g30(optical_port_block)
        case Vendor.GX_G42:
            return _factory_reset_g42(optical_port_block)
        case _:
            msg = f"No implementation of factory_reset_port_configuration found for {type(host_node).__name__}"
            raise TypeError(msg)


def _check_fiber_flexils(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> None:
    """Check if a Nokia FlexILS port attached to a fiber is correctly configured."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    remote_port_name = _port_name(remote_port_block)
    description = optical_port_block.optical_port_description or ""

    # Handle FlexILS-to-FlexILS connection separately (simpler case)
    if vendor_of(remote_port_block.optical_port_host_node) == Vendor.FLEXILS:
        ots = flex.rtrv_ots(aid=port_name).parsed_data[0]
        checks = (
            description in ots["LABEL"]
            and "IS" in ots["OPERSTATE"]
            and remote_port_name in ots["PROVNBROTS"]
            and ots["PROVNBROTS"] == ots["DISCNBROTS"]
            and ots["HISTSTATS"] == "ENABLED"
        )
        if not checks:
            raise ValueError(
                json.dumps(
                    {
                        "optical_device": _node_id(optical_port_block.optical_port_host_node),
                        "port_name": port_name,
                        "expected": {
                            "label": description,
                            "operstate": "IS",
                            "provnbrots": remote_port_name,
                            "discnbrots": remote_port_name,
                            "histstats": "ENABLED",
                        },
                        "actual": {
                            "label": ots["LABEL"],
                            "operstate": ots["OPERSTATE"],
                            "provnbrots": ots["PROVNBROTS"],
                            "discnbrots": ots["DISCNBROTS"],
                            "histstats": ots["HISTSTATS"],
                        },
                    },
                    indent=4,
                )
            )
        return

    # Handle FlexILS connections to other platform types
    remote_node_id = _get_remote_node_id(remote_port_block)
    remote_port_id = _extract_remote_port_id(remote_port_name)
    provowremptp = f"{remote_node_id}/{remote_port_id}"

    scg = flex.rtrv_scg(aid=port_name).parsed_data[0]

    checks = (
        scg["INTFTYP"] == "MANUALMODE-2"
        and scg["PROVOWREMPTP"] == provowremptp
        and description in scg["LABEL"]
        and "IS" in scg["OPERSTATE"]
        and scg["HISTSTATS"] == "ENABLED"
    )
    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": _node_id(optical_port_block.optical_port_host_node),
                    "port_name": port_name,
                    "expected": {
                        "intftyp": "MANUALMODE-2",
                        "provowremptp": provowremptp,
                        "label": description,
                        "operstate": "IS",
                        "histstats": "ENABLED",
                    },
                    "actual": {
                        "intftyp": scg["INTFTYP"],
                        "provowremptp": scg["PROVOWREMPTP"],
                        "label": scg["LABEL"],
                        "operstate": scg["OPERSTATE"],
                        "histstats": scg["HISTSTATS"],
                    },
                },
                indent=4,
            )
        )


def _check_fiber_g30(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> None:
    """Check if a Groove G30 port attached to a fiber is correctly configured."""
    host_node = optical_port_block.optical_port_host_node
    remote_host_node = remote_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    endpoint = g30_port_navigator_node_from_port_name(host_node, port_name)[0]
    port_data = endpoint.retrieve(depth=2)

    if vendor_of(remote_host_node) == Vendor.GROOVE_G30 and _same_node(host_node, remote_host_node):
        con_to_string = f"patched to {_port_name(remote_port_block)}"
        ext_connectivity = YesNoEnum.NO
    else:
        con_to_string = f"{_node_id(remote_host_node)} {_port_name(remote_port_block)}"
        ext_connectivity = YesNoEnum.YES

    checks = (
        port_data.admin_status == AdminStatusEnum.UP
        and port_data.external_connectivity == ext_connectivity
        and port_data.connected_to == con_to_string
    )

    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": _node_id(host_node),
                    "port_name": port_name,
                    "expected": {
                        "admin-status": "up",
                        "external-connectivity": ext_connectivity.value,
                        "connected-to": con_to_string,
                    },
                    "actual": {
                        "admin-status": port_data.admin_status,
                        "external-connectivity": port_data.external_connectivity,
                        "connected-to": port_data.connected_to,
                    },
                },
                indent=4,
            )
        )


def _check_fiber_g42(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> None:
    """Check if a GX G42 port attached to a fiber is correctly configured."""
    host_node = optical_port_block.optical_port_host_node
    g42 = get_g42_client(host_node)
    shelf_id, slot_id, port_id = _port_name(optical_port_block).split("-")
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = endpoint.retrieve(depth=2, content="config")

    expected_connected_to = f"{_node_id(remote_port_block.optical_port_host_node)} {_port_name(remote_port_block)}"
    checks = (
        conf.admin_state == AdminStateEnum.UNLOCK
        and conf.external_connectivity == ExternalConnectivityEnum.YES
        and conf.connected_to == expected_connected_to
    )
    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": _node_id(host_node),
                    "port_name": _port_name(optical_port_block),
                    "expected": {
                        "admin-status": "unlock",
                        "external-connectivity": "yes",
                        "connected-to": expected_connected_to,
                    },
                    "actual": {
                        "admin-status": conf.admin_state,
                        "external-connectivity": conf.external_connectivity,
                        "connected-to": conf.connected_to,
                    },
                },
                indent=4,
            )
        )


def check_fiber_terminating_port(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> None:
    """Check if an optical port attached to a fiber is correctly configured.

    Args:
        optical_port_block: Optical Port to check.
        remote_port_block: The remote Optical Port to verify the connection against.

    Returns:
        None

    Raises:
        ValueError: If the port configuration does not match the expected one.
    """
    host_node = optical_port_block.optical_port_host_node
    match vendor_of(host_node):
        case Vendor.FLEXILS:
            return _check_fiber_flexils(optical_port_block, remote_port_block)
        case Vendor.GROOVE_G30:
            return _check_fiber_g30(optical_port_block, remote_port_block)
        case Vendor.GX_G42:
            return _check_fiber_g42(optical_port_block, remote_port_block)
        case _:
            msg = f"No implementation of check_fiber_terminating_port found for {type(host_node).__name__}"
            raise TypeError(msg)
