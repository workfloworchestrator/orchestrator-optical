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

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any, Literal

from products.product_blocks.optical_device import OpticalDeviceBlock, OpticalDeviceBlockProvisioning, Platform
from products.product_blocks.optical_device_port import OpticalDevicePortBlock, OpticalDevicePortBlockProvisioning
from products.services.optical_device import get_flex_client, get_g30_client, get_g42_client
from services.nokia import TL1CommandDeniedError
from utils.attributedispatch import attribute_dispatch_base, attributedispatch

if TYPE_CHECKING:
    from services.nokia.g30.data_navigators.ne import PortItemNode, SubportItemNode


def g30_ids_from_port_name(port_name: str) -> tuple[int, int, int | None, int, int | None]:
    """
    Returns the shelf_id, slot_id, subslot_id, port_id, subport_id.

    Args:
        port_name: The name of the port to obtain the endpoint from

    Returns:
        Tuple containing the shelf_id, slot_id, subslot_id, port_id, subport_id
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

    return (int(x) if x else x for x in (shelf_id, slot_id, subslot_id, port_id, subport_id))


def g30_port_navigator_node_from_port_name(
    g30_device_block: OpticalDeviceBlock, port_name: str
) -> tuple[PortItemNode | SubportItemNode, int, int, int | None, int, int | None]:
    """
    Returns the RESTCONF endpoint, shelf_id, slot_id, subslot_id, port_id, subport_id.

    Args:
        g30_device_block: OpticalDeviceBlock of the Groove G30 device
        port_name: The name of the port to obtain the endpoint from

    Returns:
        Tuple containing the endpoint, shelf_id, slot_id, subslot_id, port_id, subport_id

    Example:
        >>> g30_obtain_port_endpoint_from_port_name(g30_device_block, "port-1/2/3")
        (endpoint, "1", "2", None, "3", None)
        >>> t = g30_obtain_port_endpoint_from_port_name(g30_device_block, "port-1/3.1/1.4")
        >>> t
        (endpoint, "1", "3", "1", "1", "4")
        >>> t[0].retrieve(depth=2)
    """
    g30 = get_g30_client(g30_device_block)
    shelf_id, slot_id, subslot_id, port_id, subport_id = g30_ids_from_port_name(port_name)

    if subslot_id and subport_id:
        endpoint = (
            g30.data.ne_ne.shelf(shelf_id)
            .slot(slot_id)
            .card.subslot(subslot_id)
            .subcard.port(port_id)
            .subport(subport_id)
        )
    elif subslot_id and not subport_id:
        endpoint = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.port(port_id)
    else:
        endpoint = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    return endpoint, shelf_id, slot_id, subslot_id, port_id, subport_id


@attributedispatch("platform")
def retrieve_transceiver_modes(optical_device: OpticalDeviceBlock, port_name: str) -> list[str]:  # noqa: ARG001
    """
    Retrieve the list of supported modulations for a specific port on an optical device.

    This function uses an attribute-based dispatch mechanism to determine the
    appropriate implementation based on the platform of the optical device.

    Args:
        optical_device (OpticalDeviceBlock): The optical device containing the port.
        port_name (str): The name of the port for which to retrieve modulations.

    Returns:
        List[str]: A list of supported modes for the specified port.
    """
    return attribute_dispatch_base(retrieve_transceiver_modes, "platform", optical_device.platform)


@retrieve_transceiver_modes.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock, port_name: str) -> list[str]:
    # prevent ruff from formatting the next mapping
    # fmt: off
    mapping = {
        "CHM1": [
            "not-applicable",      "QPSK_100G",          "16QAM_200G",          "8QAM_300G",
        ],
        "CHM2T": [
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

    g30 = get_g30_client(optical_device)

    card = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.retrieve(depth=2)

    card_type = card.required_type

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


@retrieve_transceiver_modes.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock, port_name: str) -> list[str]:
    # prevent ruff from formatting the next mapping
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

    g42 = get_g42_client(optical_device)

    card = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").retrieve(depth=2, content="config")
    card_type = card.required_subtype

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


def _flex_get_device_ports_names(optical_device: OpticalDeviceBlock) -> list[str]:
    flex = get_flex_client(optical_device)
    try:
        scg_aids = [str(x["AID"]) for x in flex.rtrv_scg().parsed_data]
    except TL1CommandDeniedError as e:
        if "INPUT, SPECIFIED OBJECT ENTITY DOES NOT EXIST" not in e.response:
            raise
        scg_aids = []
    ots_aids = [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]
    return scg_aids + ots_aids


def _g30_get_device_ports_names(optical_device: OpticalDeviceBlock) -> list[str]:
    g30 = get_g30_client(optical_device)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    ports_name = []
    max_slot_id_with_useful_ports = 4
    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            ports_name.extend(p.alias_name for p in (slot.card.port or []))

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                for port in subslot.subcard.port or []:
                    ports_name.append(port.alias_name)

                    if port.subport:
                        ports_name.extend(sp.alias_name for sp in port.subport)

    return ports_name


def _g42_get_device_ports_names(optical_device: OpticalDeviceBlock) -> list[str]:
    g42 = get_g42_client(optical_device)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in card.port if (p.port_type == "line" or p.installed_type))

    return ports


def get_device_ports_names(optical_device: OpticalDeviceBlock) -> list[str]:
    """
    Retrieve a list of optical ports of an OpticalDevice (generic function).
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical ports are to be retrieved
    Returns:
        A list of optical ports' names of the optical device
    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
    """
    match optical_device.platform:
        case Platform.FlexILS:
            return _flex_get_device_ports_names(optical_device)
        case Platform.Groove_G30:
            return _g30_get_device_ports_names(optical_device)
        case Platform.GX_G42:
            return _g42_get_device_ports_names(optical_device)
        case _:
            raise TypeError(
                f"No implementation of get_device_ports_names found for platform {optical_device.platform!r}"
            )


@attributedispatch("platform")
def get_device_client_ports_names(optical_device: OpticalDeviceBlock) -> list[str]:
    """
    Retrieve a list of optical ports of an OpticalDevice (generic function).
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical ports are to be retrieved

    Returns:
        A list of optical ports' names of the optical device

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
    """
    return attribute_dispatch_base(get_device_client_ports_names, "platform", optical_device.platform)


@get_device_client_ports_names.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    flex = get_flex_client(optical_device)
    return [x["AID"] for x in flex.rtrv_scg().parsed_data]


@get_device_client_ports_names.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g30 = get_g30_client(optical_device)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    ports_name = []
    max_slot_id_with_useful_ports = 4

    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            for port in slot.card.port or []:
                is_sub_interface = "." in (port.alias_name or "")
                is_in_client_range = 3 <= port.port_id <= 12  # noqa: PLR2004

                if is_sub_interface or is_in_client_range:
                    ports_name.append(port.alias_name)

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                for port in subslot.subcard.port or []:
                    ports_name.append(port.alias_name)

                    if port.subport:
                        ports_name.extend(sp.alias_name for sp in port.subport)

    return ports_name


@get_device_client_ports_names.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g42 = get_g42_client(optical_device)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in card.port if p.installed_type)

    return ports


@attributedispatch("platform")
def get_device_line_ports_names(optical_device: OpticalDeviceBlock) -> list[str]:
    """
    Retrieve a list of optical ports of an OpticalDevice (generic function).
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical ports are to be retrieved

    Returns:
        A list of optical ports' names of the optical device

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
    """
    return attribute_dispatch_base(get_device_line_ports_names, "platform", optical_device.platform)


@get_device_line_ports_names.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    flex = get_flex_client(optical_device)
    return [x["AID"] for x in flex.rtrv_ots().parsed_data]


@get_device_line_ports_names.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g30 = get_g30_client(optical_device)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=5, content="config")

    ports_name = []
    max_slot_id_with_useful_ports = 4

    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            for port in slot.card.port or []:
                is_in_line_range = 1 <= (port.port_id or 999) <= 2  # noqa: PLR2004

                if is_in_line_range:
                    ports_name.append(port.alias_name)

    return ports_name


@get_device_line_ports_names.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g42 = get_g42_client(optical_device)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in card.port if p.port_type == "line")

    return ports


@attributedispatch("platform")
def set_port_description(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:  # noqa: ARG001
    """
    Set the description of an optical port on an OpticalDevice (generic function).
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical port is to be modified
        port_name: The name of the optical port to set the description on
        port_description: The description to set on the port

    Returns:
        Dict[str, Any]

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
        ValueError: in case the configuration failed
    """
    return attribute_dispatch_base(set_port_description, "platform", optical_device.platform)


@set_port_description.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:
    flex = get_flex_client(optical_device)
    if "L" in port_name:
        flex.ed_ots(aid=port_name, label=rf'"{port_description}"')
        return flex.rtrv_ots(aid=port_name)
    flex.ed_scg(aid=port_name, label=rf'"{port_description}"')
    return flex.rtrv_scg(aid=port_name)


@set_port_description.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:
    endpoint, _, _, _, _, _ = g30_port_navigator_node_from_port_name(optical_device, port_name)
    port = endpoint.retrieve(content="config", depth=2)
    port.service_label = port_description
    endpoint.update(port)
    return endpoint.retrieve(content="config", depth=2).model_dump()


@set_port_description.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
    g42 = get_g42_client(optical_device)
    port_uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)

    port_config = port_uri.retrieve(content="config", depth=2)
    port_config.label = port_description

    port_uri.update(port_config)

    return port_uri.retrieve(content="config", depth=2).model_dump()


@attributedispatch("platform")
def set_channel_description(optical_device: OpticalDeviceBlock, facility_id: str, description: str) -> dict[str, Any]:  # noqa: ARG001
    """
    Set the description of an optical channel on an OpticalDevice (generic function).
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical port is to be modified
        facility_id: The id of the optical channel to set the description on (e.g. 1/1/1)
        description: The description to set on the port

    Returns:
        Dict[str, Any]

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
        ValueError: in case the configuration failed
    """
    return attribute_dispatch_base(set_channel_description, "platform", optical_device.platform)


@set_channel_description.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock, facility_id: str, description: str) -> dict[str, Any]:
    g30 = get_g30_client(optical_device)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(facility_id)
    uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os

    och_os = uri.retrieve(content="config", depth=2)
    och_os.service_label = description
    uri.update(och_os)

    return uri.retrieve(content="config", depth=2).model_dump()


@set_channel_description.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock, facility_id: str, description: str) -> dict[str, Any]:
    g42 = get_g42_client(optical_device)
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


@attributedispatch("platform")
def set_port_admin_state(
    optical_device: OpticalDeviceBlock,
    port_name: str,  # noqa: ARG001
    admin_state: Literal["up", "down", "maintenance"],  # noqa: ARG001
) -> dict[str, Any]:
    """
    Set the administrative state of an optical port on an OpticalDevice (generic function).
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical port is to be modified
        port_name: The name of the optical port to set the admin state on
        admin_state: The administrative state to set on the port: ["up", "down", "maintenance"]

    Returns:
        Dict[str, Any]

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
        ValueError: in case the configuration failed
    """
    return attribute_dispatch_base(set_port_admin_state, "platform", optical_device.platform)


@set_port_admin_state.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    port_name: str,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """
    FlexILS has 3 admin states for the tributary ports: IS (in service), OOS (out of service), and MT (maintenance).
    Line ports (OTS) can only be in IS or MT state.
    It works as a finite state machine with the following transitions:
    OOS <-edit---edit-> IS <-rst---put-> MT.
    """
    flex = get_flex_client(optical_device)

    # Line ports (OTS)
    if "L" in port_name:
        if admin_state == "down":
            msg = "Line ports (OTS) can only be in service (IS) or maintenance (MT) state"
            raise ValueError(msg)
        if admin_state == "maintenance":
            flex.put_maintenance(aidtype="OTS", aid=port_name)
        elif admin_state == "up":
            flex.rst_maintenance(aidtype="OTS", aid=port_name)
        return flex.rtrv_ots(aid=port_name)

    # Tributary ports (SCG)
    ## from any state to in-service state (we must know the current state of the
    # finite state machine to move between states)
    try:
        flex.ed_scg(aid=port_name, is_oos="IS")
    except TL1CommandDeniedError as e:
        if "use RST command" not in e.response:
            raise
        flex.rst_maintenance(aidtype="SCG", aid=port_name)
    ## from in-service state to desired state
    if admin_state == "up":
        pass
    elif admin_state == "down":
        flex.ed_scg(aid=port_name, is_oos="OOS")
    elif admin_state == "maintenance":
        flex.put_maintenance(aidtype="SCG", aid=port_name)

    return flex.rtrv_scg(aid=port_name)


@set_port_admin_state.register(Platform.Groove_G30)
def _(
    optical_device: OpticalDeviceBlock,
    port_name: str,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    mapping = {
        "up": "up",
        "down": "down",
        "maintenance": "up-no-alm",
    }
    status = mapping[admin_state]

    port_uri = g30_port_navigator_node_from_port_name(optical_device, port_name)[0]

    port = port_uri.retrieve(content="config", depth=2)
    port.admin_status = status

    port_uri.update(port)
    return port_uri.retrieve(depth=2, content="config").model_dump()


@set_port_admin_state.register(Platform.GX_G42)
def _(
    optical_device: OpticalDeviceBlock,
    port_name: str,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    mapping = {
        "up": "unlock",
        "down": "lock",
        "maintenance": "maintenance",
    }
    status = mapping[admin_state]

    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    g42 = get_g42_client(optical_device)
    uri: PortItemNode = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)

    conf = uri.retrieve(content="config", depth=2)
    conf.admin_state = status
    uri.update(conf)

    return uri.retrieve(depth=2)


@attributedispatch("platform")
def configure_termination_when_attaching_new_fiber(
    optical_device: OpticalDeviceBlockProvisioning,
    port: OpticalDevicePortBlockProvisioning,  # noqa: ARG001
    remote_port: OpticalDevicePortBlockProvisioning,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Configure an optical port on an OpticalDevice when attaching a fiber to it.
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical port is to be configured
        port: The name of the optical port to configure
        remote_port: The remote port to connect to

    Returns:
        Dict[str, Any]

    Raises:
        ValueError: in case the configuration failed
    """
    return attribute_dispatch_base(
        configure_termination_when_attaching_new_fiber,
        "platform",
        optical_device.platform,
    )


def flexils_check_port_is_in_manualmode2_else_set_it(
    optical_device: OpticalDeviceBlock,
    port_name: str,
):
    flex = get_flex_client(optical_device)
    scg = flex.rtrv_scg(aid=port_name).parsed_data[0]

    if scg["INTFTYP"] != "MANUALMODE-2":
        card_aid = port_name.split("-")[:-1]
        card_aid = "-".join(card_aid)
        card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]

        if card["TYPE"] in ["FSM", "FRM"]:
            # tributary ports of FSM and system ports of FRM cards can only be unlocked or locked
            set_port_admin_state(optical_device, port_name, "down")
        else:
            set_port_admin_state(optical_device, port_name, "maintenance")

        flex.ed_scg(aid=port_name, intftyp="MANUALMODE-2")

    set_port_admin_state(optical_device, port_name, "up")


@configure_termination_when_attaching_new_fiber.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    flex = get_flex_client(optical_device)
    port_name = port.port_name
    description = port.port_description

    # Handle FlexILS-to-FlexILS connection separately (simpler case)
    if remote_port.optical_device.platform == Platform.FlexILS:
        flex.ed_ots(aid=port_name, label=rf'"{description}"')
        flex.rst_maintenance(aidtype="OTS", aid=port_name)
        return flex.rtrv_ots(aid=port_name)

    # Handle FlexILS connections to other platform types
    flexils_check_port_is_in_manualmode2_else_set_it(optical_device, port_name)

    remote_node_id = _get_remote_node_id(remote_port)
    remote_port_id = _extract_remote_port_id(remote_port)
    provowremptp = f"{remote_node_id}/{remote_port_id}"
    flex.ed_scg(
        aid=port_name,
        provowremptp=provowremptp,
        label=rf'"{description}"',
    )

    return flex.rtrv_scg(aid=port_name)


def _get_remote_node_id(remote_port: OpticalDevicePortBlock) -> str:
    """Extract node ID from remote port's device based on platform type."""
    platform = remote_port.optical_device.platform

    if platform == Platform.Groove_G30:
        g30 = get_g30_client(remote_port.optical_device)
        inventory = g30.data.ne_ne.inventory_data.inventory.retrieve(depth=2)

        for item in inventory:
            if item.equipment_type == "shelf" and item.shelf_id == 1:
                return item.serial_number

        msg = f"Could not find shelf serial number for G30 device {remote_port.optical_device.fqdn}"
        raise ValueError(msg)

    if platform == Platform.GX_G42:
        return remote_port.optical_device.fqdn.removesuffix(".garr.net")

    msg = f"Unsupported remote platform for FlexILS connection: {platform}"
    raise ValueError(msg)


def _extract_remote_port_id(remote_port: OpticalDevicePortBlock) -> str:
    """Extract and format the port ID from the remote port name."""
    match = re.search(r"\d", remote_port.port_name)
    if not match:
        msg = f"Could not extract port identifier from remote port name: {remote_port.port_name}"
        raise ValueError(msg)
    port_id = remote_port.port_name[match.start() :]
    return re.sub(r"[^a-zA-Z0-9]", "-", port_id)


@configure_termination_when_attaching_new_fiber.register(Platform.Groove_G30)
def _(  # noqa: PLR0915
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    port_name = port.port_name
    endpoint, shelf_id, slot_id, subslot_id, port_id, _ = g30_port_navigator_node_from_port_name(
        optical_device, port_name
    )
    port_config = endpoint.retrieve(depth=2, content="config")

    if remote_port.optical_device.platform == Platform.FlexILS:
        port_config.external_connectivity = "yes"
        port_config.connected_to = f"{remote_port.optical_device.fqdn} {remote_port.port_name}"
        port_config.admin_status = "up"

        endpoint.update(port_config)
        return endpoint.retrieve(depth=2, content="config").model_dump()

    if remote_port.optical_device.platform == Platform.Groove_G30:
        is_same_device = remote_port.optical_device.subscription_instance_id == optical_device.subscription_instance_id
        is_amplifier_port = slot_id == 3 and subslot_id == 3 and port_id == 1  # noqa: PLR2004

        if is_same_device:
            port_config.external_connectivity = "no"
            port_config.connected_to = f"patched to {remote_port.port_name}"
            port_config.admin_status = "up"
            endpoint.update(port_config)
            return endpoint.retrieve(depth=2, content="config").model_dump()

        if not is_same_device and not is_amplifier_port:
            port_config.external_connectivity = "yes"
            port_config.connected_to = f"{remote_port.optical_device.fqdn} {remote_port.port_name}"
            port_config.admin_status = "up"
            endpoint.update(port_config)
            return endpoint.retrieve(depth=2, content="config").model_dump()

        if is_amplifier_port and not is_same_device:  # link H4
            g30 = get_g30_client(optical_device)

            booster_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(2).subcard.amplifier("ba")
            booster = booster_uri.retrieve(content="config", depth=2)
            booster.admin_status = "up"
            booster.amplifier_enable = "enabled"
            booster.input_los_shutdown = "disabled"
            booster.control_mode = "manual"
            booster.gain_range_control = "manual"
            booster.target_gain_range = "standard"
            booster.target_gain = 22.0
            booster.output_voa = 10.0
            booster.tilt_control_mode = "manual"
            booster.gain_tilt = 0.0
            booster_uri.update(booster)

            preamp_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.amplifier("pa")
            preamp = preamp_uri.retrieve(content="config", depth=2)
            preamp.admin_status = "up"
            preamp.amplifier_enable = "enabled"
            preamp.input_los_shutdown = "disabled"
            preamp.control_mode = "auto"
            preamp.gain_range_control = "auto"
            preamp.target_gain_range = "standard"
            preamp.tilt_control_mode = "auto"
            preamp_uri.update(preamp)

            port_config.external_connectivity = "yes"
            port_config.connected_to = f"{remote_port.optical_device.fqdn} {remote_port.port_name}"
            port_config.admin_status = "up"
            endpoint.update(port_config)

            return {
                "port": endpoint.retrieve(depth=2, content="config").model_dump(),
                "booster": booster_uri.retrieve(depth=2, content="config").model_dump(),
                "preamp": preamp_uri.retrieve(depth=2, content="config").model_dump(),
            }

        msg = "Unsupported fiber connection between provided ports of different Groove G30 devices."
        raise ValueError(msg)

    msg = (
        "Unsupported remote optical device platform when configuring Groove G30 remote port: "
        f"{remote_port.optical_device.platform}"
    )
    raise ValueError(msg)


@configure_termination_when_attaching_new_fiber.register(Platform.GX_G42)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    shelf_id, slot_id, port_id = port.port_name.split("-")
    g42 = get_g42_client(optical_device)
    uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    uri.update(
        name=port_id,
        external_connectivity="yes",
        connected_to=f"{remote_port.optical_device.fqdn} {remote_port.port_name}",
        admin_state="unlock",
    )
    return uri.retrieve(content="config", depth=2).model_dump()


@attributedispatch("platform")
def factory_reset_port_configuration(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,  # noqa: ARG001
    remote_port: OpticalDevicePortBlock,  # noqa: ARG001
) -> dict[str, Any]:
    """Prune the configuration of an optical port on an OpticalDevice."""
    return attribute_dispatch_base(factory_reset_port_configuration, "platform", optical_device.platform)


@factory_reset_port_configuration.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    flex = get_flex_client(optical_device)
    port_name = port.port_name

    if remote_port.optical_device.platform == Platform.FlexILS:
        flex.ed_ots(aid=port_name, label=r'""')
        return flex.rtrv_ots(aid=port_name)

    set_port_admin_state(optical_device, port_name, "maintenance")
    flex.ed_scg(
        aid=port_name,
        intftyp="MANUALMODE-2",
        provowremptp=r'""',
        label=r'""',
    )
    set_port_admin_state(optical_device, port_name, "down")
    return flex.rtrv_scg(aid=port_name)


@factory_reset_port_configuration.register(Platform.Groove_G30)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,  # noqa: ARG001
) -> dict[str, Any]:
    port_name = port.port_name
    port_uri = g30_port_navigator_node_from_port_name(optical_device, port_name)[0]
    config = port_uri.retrieve(content="config", depth=2)

    if "." in port_name:  # inside OCC2 card
        config.connected_to = ""
        port_uri.update(config)
    else:
        config.external_connectivity = "no"
        config.connected_to = ""
        config.admin_status = "down"
        config.port_mode = "not-applicable"
        config.service_label = ""
        port_uri.update(config)

    return port_uri.retrieve(content="config", depth=2).model_dump()


@factory_reset_port_configuration.register(Platform.GX_G42)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,  # noqa: ARG001
) -> dict[str, Any]:
    g42 = get_g42_client(optical_device)
    shelf_id, slot_id, port_id = port.port_name.split("-")
    uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = uri.retrieve(content="config", depth=2)
    conf.external_connectivity = "no"
    conf.connected_to = ""
    conf.admin_state = "lock"
    conf.label = ""
    uri.update(conf)
    return uri.retrieve(content="config", depth=2).model_dump()


@attributedispatch("platform")
def check_fiber_terminating_port(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,  # noqa: ARG001
    remote_port: OpticalDevicePortBlock,  # noqa: ARG001
) -> None:
    """
    Check if an optical port on an OpticalDevice attached to a fiber is correctly configured.
    Specific implementations of this generic function MUST specify the *platform* they work on.

    Args:
        optical_device: OpticalDevice of which the optical port is to be checked
        port: The optical port to check
        remote_port: The remote port to verify the connection against

    Returns:
        None

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.
    """
    return attribute_dispatch_base(check_fiber_terminating_port, "platform", optical_device.platform)


@check_fiber_terminating_port.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> None:
    flex = get_flex_client(optical_device)
    port_name = port.port_name
    description = port.port_description

    # Handle FlexILS-to-FlexILS connection separately (simpler case)
    if remote_port.optical_device.platform == Platform.FlexILS:
        ots = flex.rtrv_ots(aid=port_name)
        ots = ots.parsed_data[0]
        checks = (
            description in ots["LABEL"]
            and "IS" in ots["OPERSTATE"]
            and remote_port.port_name in ots["PROVNBROTS"]
            and ots["PROVNBROTS"] == ots["DISCNBROTS"]
            and ots["HISTSTATS"] == "ENABLED"
        )
        if not checks:
            raise ValueError(
                json.dumps(
                    {
                        "optical_device": optical_device.fqdn,
                        "port_name": port_name,
                        "expected": {
                            "label": description,
                            "operstate": "IS",
                            "provnbrots": remote_port.port_name,
                            "discnbrots": remote_port.port_name,
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
    else:
        # Handle FlexILS connections to other platform types
        remote_node_id = _get_remote_node_id(remote_port)
        remote_port_id = _extract_remote_port_id(remote_port)
        provowremptp = f"{remote_node_id}/{remote_port_id}"

        scg = flex.rtrv_scg(aid=port_name)
        scg = scg.parsed_data[0]

        checks = (
            scg["INTFTYP"] == "MANUALMODE-2"
            and scg["PROVOWREMPTP"] == provowremptp
            and description in scg["LABEL"]
            and "IS" in scg["OPERSTATE"]
            and ots["HISTSTATS"] == "ENABLED"
        )
        if not checks:
            raise ValueError(
                json.dumps(
                    {
                        "optical_device": optical_device.fqdn,
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


@check_fiber_terminating_port.register(Platform.Groove_G30)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> None:
    port_name = port.port_name
    endpoint = g30_port_navigator_node_from_port_name(optical_device, port_name)[0]
    port_data = endpoint.retrieve(depth=2)
    """ e.g. port_data looks like this:
    {
        "alias-name": "port-3/1/1",
        "och-os": {},
        "port-id": 1,
        "port-mode": "SP16QAM_300G",
        "port-name": "01:Line:TxRx",
        "port-type": "line",
        "oper-status": "up",
        "admin-status": "up",
        "avail-status": "",
        "connected-to": "flex.pa01.garr.net 1-E1-1-T3A",
        "service-label": "och-175_sr01-pa01_f151",
        "rx-optical-power": "-6.3",
        "tx-optical-power": "2.8",
        "actual-pluggable-type": "empty",
        "external-connectivity": "yes",
        "possible-pluggable-types": [
            "non-pluggable"
        ],
        "rx-optical-power-selected-channel": "-7.2"
    }

    or

    {
        "alias-name": "subport-1/3.1/1.2",
        "port-name": "ad2",
        "port-type": "optical-nomon",
        "subport-id": 2,
        "oper-status": "up",
        "admin-status": "up",
        "avail-status": "",
        "connected-to": "patched to port-2/1/1",
        "service-label": "",
        "direction-type": "rxtx",
        "external-connectivity": "no"
    }

    or

    {
        "alias-name": "port-1/3.3/1",
        "port-id": 1,
        "port-name": "dwdm-line",
        "port-type": "optical",
        "oper-status": "up",
        "admin-status": "up",
        "avail-status": "",
        "connected-to": "g30.sr01.garr.net port-1/3.3/1",
        "service-label": "",
        "direction-type": "rxtx",
        "rx-optical-power": "-19.3",
        "tx-optical-power": "4.0",
        "external-connectivity": "yes"
    }
    """

    if (
        remote_port.optical_device.platform == Platform.Groove_G30
        and remote_port.optical_device.subscription_instance_id == optical_device.subscription_instance_id
    ):
        con_to_string = f"patched to {remote_port.port_name}"
        ext_connectivity = "no"
    else:
        con_to_string = f"{remote_port.optical_device.fqdn} {remote_port.port_name}"
        ext_connectivity = "yes"

    checks = (
        port_data.admin_status == "up"
        and port_data.external_connectivity == ext_connectivity
        and port_data.connected_to == con_to_string
    )

    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": optical_device.fqdn,
                    "port_name": port_name,
                    "expected": {
                        "admin-status": "up",
                        "external-connectivity": ext_connectivity,
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


@check_fiber_terminating_port.register(Platform.GX_G42)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> None:
    g42 = get_g42_client(optical_device)
    shelf_id, slot_id, port_id = port.port_name.split("-")
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = endpoint.retrieve(depth=2, content="config")
    """ e.g. conf looks like this, but it is a Pydantic model, not dict:
    {
        "AID": "1-4-L1",
        "name": "L1",
        "label": "",
        "port-type": "line",
        "alias-name": "",
        "oper-state": "enabled",
        "admin-state": "unlock",
        "avail-state": "normal in-service",
        "connected-to": "flex.na01.garr.net 1-E2-1-T3A",
        "hosted-interface": "/ioa-ne:ne/facilities/super-channel-group[name='1-4-L1']",
        "alarm-report-control": "allowed",
        "external-connectivity": "yes"
    }
    """

    checks = (
        conf.admin_state == "unlock"
        and conf.external_connectivity == "yes"
        and conf.connected_to == f"{remote_port.optical_device.fqdn} {remote_port.port_name}"
    )
    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": optical_device.fqdn,
                    "port_name": port.port_name,
                    "expected": {
                        "admin-status": "unlock",
                        "external-connectivity": "yes",
                        "connected-to": f"{remote_port.optical_device.fqdn} {remote_port.port_name}",
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
