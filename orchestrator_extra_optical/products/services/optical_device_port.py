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

import json
import re
from typing import Any, Literal

from products.product_blocks.optical_device import OpticalDeviceBlock, Platform
from products.product_blocks.optical_device_port import OpticalDevicePortBlock
from products.services.optical_device import get_optical_device_client
from services.infinera import TL1CommandDeniedError
from utils.attributedispatch import attribute_dispatch_base, attributedispatch


@attributedispatch("platform")
def retrieve_transceiver_modes(optical_device: OpticalDeviceBlock, port_name: str) -> list[str]:
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
            "not-applicable", "QPSK_100G",
            "16QAM_200G",     "8QAM_300G",
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

    ids = port_name.split("-")[-1]  # port-1/2/3 -> 1/2/3
    shelf_id, slot_id, _ = ids.split("/")  # 1/2/3 -> 1, 2, 3

    g30 = get_optical_device_client(optical_device)
    card = g30.data.ne.shelf(shelf_id).slot(slot_id).card.retrieve(depth=2)
    card_type = card["required-type"]

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        raise ValueError(f"Card {card_type} not supported")

    return supported_modes


@retrieve_transceiver_modes.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock, port_name: str) -> list[str]:
    # prevent ruff from formatting the next mapping
    # fmt: off
    mapping = {
        "C6": [
            "100E.31U",
            "100E.70U",
            "100M.33U",
            "100M.73U",
            "150E.31P",
            "150E.31U",
            "150E.35U",
            "150E.42P",
            "150E.44P",
            "150E.70U",
            "150E.84U",
            "150M.33P",
            "150M.33U",
            "150M.36U",
            "150M.44P",
            "150M.46P",
            "150M.73U",
            "150M.87U",
            "200E.31P",
            "200E.31U",
            "200E.35U",
            "200E.42P",
            "200E.42U",
            "200E.45P",
            "200E.50P",
            "200E.63P",
            "200E.63U",
            "200E.70U",
            "200E.80U",
            "200E.93U",
            "200M.33P",
            "200M.33U",
            "200M.36U",
            "200M.44P",
            "200M.44U",
            "200M.47P",
            "200M.52P",
            "200M.66P",
            "200M.66U",
            "200M.73U",
            "200M.83U",
            "250E.31P",
            "250E.31U",
            "250E.35U",
            "250E.42P",
            "250E.50P",
            "250E.63P",
            "250E.63U",
            "250E.72P",
            "250E.84P",
            "250E.87U",
            "250M.33P",
            "250M.33U",
            "250M.36U",
            "250M.44P",
            "250M.52P",
            "250M.66P",
            "250M.66U",
            "250M.75P",
            "250M.82U",
            "250M.87P",
            "250M.91U",
            "300E.31U",
            "300E.42P",
            "300E.44P",
            "300E.50P",
            "300E.63P",
            "300E.63U",
            "300E.64P",
            "300E.65P",
            "300E.67P",
            "300E.68P",
            "300E.70P",
            "300E.72P",
            "300E.73P",
            "300E.75P",
            "300E.84P",
            "300E.89P",
            "300E.91P",
            "300E.94P",
            "300M.33U",
            "300M.44P",
            "300M.46P",
            "300M.52P",
            "300M.66P",
            "300M.66U",
            "300M.67P",
            "300M.68P",
            "300M.70P",
            "300M.71P",
            "300M.73P",
            "300M.75P",
            "300M.77P",
            "300M.79P",
            "300M.87P",
            "300M.92P",
            "300M.95P",
            "350E.42P",
            "350E.50P",
            "350E.63P",
            "350E.63U",
            "350E.72P",
            "350E.84P",
            "350M.44P",
            "350M.52P",
            "350M.66P",
            "350M.66U",
            "350M.75P",
            "350M.87P",
            "400E.42U",
            "400E.45P",
            "400E.50P",
            "400E.63P",
            "400E.63U",
            "400E.65P",
            "400E.67P",
            "400E.69P",
            "400E.72P",
            "400E.74P",
            "400E.84P",
            "400E.84U",
            "400E.91P",
            "400E.96P",
            "400M.44U",
            "400M.47P",
            "400M.52P",
            "400M.66P",
            "400M.66U",
            "400M.68P",
            "400M.70P",
            "400M.72P",
            "400M.75P",
            "400M.78P",
            "400M.87P",
            "400M.87U",
            "400M.95P",
            "450E.63P",
            "450E.63U",
            "450E.64P",
            "450E.65P",
            "450E.66P",
            "450E.67P",
            "450E.68P",
            "450E.70P",
            "450E.71P",
            "450E.72P",
            "450E.73P",
            "450E.74P",
            "450E.75P",
            "450E.81U",
            "450E.84P",
            "450E.89P",
            "450E.94P",
            "450M.66P",
            "450M.66U",
            "450M.67P",
            "450M.68P",
            "450M.69P",
            "450M.70P",
            "450M.71P",
            "450M.73P",
            "450M.74P",
            "450M.75P",
            "450M.76P",
            "450M.77P",
            "450M.79P",
            "450M.84U",
            "450M.87P",
            "450M.92P",
            "500E.63P",
            "500E.63U",
            "500E.67P",
            "500E.72P",
            "500E.84P",
            "500E.84U",
            "500E.91P",
            "500M.66P",
            "500M.66U",
            "500M.70P",
            "500M.75P",
            "500M.87P",
            "500M.87U",
            "500M.95P",
            "550E.63P",
            "550E.63U",
            "550E.72P",
            "550E.84P",
            "550E.86U",
            "550M.66P",
            "550M.66U",
            "550M.75P",
            "550M.87P",
            "550M.90U",
            "600E.63U",
            "600E.65P",
            "600E.68P",
            "600E.72P",
            "600E.75P",
            "600E.84P",
            "600E.84U",
            "600E.89P",
            "600E.91P",
            "600E.94P",
            "600E.94U",
            "600E.96P",
            "600M.66U",
            "600M.68P",
            "600M.71P",
            "600M.75P",
            "600M.79P",
            "600M.87P",
            "600M.87U",
            "600M.92P",
            "600M.95P",
            "650E.82U",
            "650E.84P",
            "650M.85U",
            "650M.87P",
            "700E.80U",
            "700E.84P",
            "700E.91P",
            "700M.83U",
            "700M.87P",
            "700M.95P",
            "750E.82U",
            "750E.84P",
            "750E.89P",
            "750E.94P",
            "750M.85U",
            "750M.87P",
            "750M.92P",
            "800E.84U",
            "800E.91P",
            "800E.96P",
            "800M.87U",
            "800M.95P",
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

    g42 = get_optical_device_client(optical_device)
    card = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").retrieve(depth=2, content="config")
    card_type = card["required-subtype"]

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        raise ValueError(f"Card {card_type} not supported")

    return supported_modes


@attributedispatch("platform")
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
    return attribute_dispatch_base(get_device_ports_names, "platform", optical_device.platform)


@get_device_ports_names.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    flex = get_optical_device_client(optical_device)
    scg_aids = [x["AID"] for x in flex.rtrv_scg().parsed_data]
    ots_aids = [x["AID"] for x in flex.rtrv_ots().parsed_data]
    return scg_aids + ots_aids


@get_device_ports_names.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g30 = get_optical_device_client(optical_device)
    shelves = g30.data.ne.shelf.retrieve(depth=8, content="config")

    ports = []
    for shelf in shelves:
        for slot in shelf.get("slot", []):
            if int(slot.get("slot-id")) > 4:
                continue

            for port in slot.get("card", {}).get("port", []):
                ports.append(port.get("alias-name"))

            for subslot in slot.get("card", {}).get("subslot", []):
                for port in subslot.get("subcard", {}).get("port", []):
                    ports.append(port.get("alias-name"))
                    for subport in port.get("subport", []):
                        ports.append(subport.get("alias-name"))

    return ports


@get_device_ports_names.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g42 = get_optical_device_client(optical_device)
    cards = g42.data.ne.equipment.card.retrieve(depth=5)
    ports = []
    for card in cards:
        if card["required-type"] == "gx:CHM6":
            for port in card["port"]:
                if port.get("port-type") == "line" or port.get("installed-type"):
                    ports.append(port.get("AID"))

    return ports


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
    flex = get_optical_device_client(optical_device)
    return [x["AID"] for x in flex.rtrv_scg().parsed_data]


@get_device_client_ports_names.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g30 = get_optical_device_client(optical_device)
    shelves = g30.data.ne.shelf.retrieve(depth=8, content="config")

    ports = []
    for shelf in shelves:
        for slot in shelf.get("slot", []):
            if int(slot.get("slot-id")) > 4:
                continue

            for port in slot.get("card", {}).get("port", []):
                port_id = int(port["port-id"])
                if "." not in port.get("alias-name") and (port_id < 2 or port_id > 12):
                    continue
                ports.append(port.get("alias-name"))

            for subslot in slot.get("card", {}).get("subslot", []):
                for port in subslot.get("subcard", {}).get("port", []):
                    ports.append(port.get("alias-name"))
                    for subport in port.get("subport", []):
                        ports.append(subport.get("alias-name"))

    return ports


@get_device_client_ports_names.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g42 = get_optical_device_client(optical_device)
    cards = g42.data.ne.equipment.card.retrieve(depth=5)
    ports = []
    for card in cards:
        if card["required-type"] == "gx:CHM6":
            for port in card["port"]:
                if port.get("installed-type"):
                    ports.append(port.get("AID"))

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
    flex = get_optical_device_client(optical_device)
    return [x["AID"] for x in flex.rtrv_ots().parsed_data]


@get_device_line_ports_names.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g30 = get_optical_device_client(optical_device)
    shelves = g30.data.ne.shelf.retrieve(depth=5, content="config")
    ports = []
    for shelf in shelves:
        for slot in shelf.get("slot", []):
            if int(slot.get("slot-id")) > 4:
                continue
            card = slot.get("card", {})
            for port in card.get("port", []):
                if int(port.get("port-id", 99)) > 2:
                    continue
                ports.append(port.get("alias-name"))
    return ports


@get_device_line_ports_names.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> list[str]:
    g42 = get_optical_device_client(optical_device)
    cards = g42.data.ne.equipment.card.retrieve(depth=5)
    ports = []
    for card in cards:
        if card["required-type"] == "gx:CHM6":
            for port in card["port"]:
                if port.get("port-type") == "line":
                    ports.append(port.get("AID"))

    return ports


@attributedispatch("platform")
def set_port_description(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:
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
    flex = get_optical_device_client(optical_device)
    if "L" in port_name:
        flex.ed_ots(aid=port_name, label=rf'"{port_description}"')
        return flex.rtrv_ots(aid=port_name)
    flex.ed_scg(aid=port_name, label=rf'"{port_description}"')
    return flex.rtrv_scg(aid=port_name)


def g30_obtain_port_endpoint_from_port_name(
    g30_device_block: OpticalDeviceBlock, port_name: str
) -> tuple[Any, str, str, str | None, str, str | None]:
    """
    Returns the endpoint, shelf_id, slot_id, subslot_id, port_id, subport_id.

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
    g30 = get_optical_device_client(g30_device_block)

    ids = port_name.split("-")[-1]  # port-1/2/3 -> 1/2/3 or port-1/3.1/1.4 -> 1/3.1/1.4
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

    if subslot_id and subport_id:
        endpoint = (
            g30.data.ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.port(port_id).subport(subport_id)
        )
    elif subslot_id and not subport_id:
        endpoint = g30.data.ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.port(port_id)
    else:
        endpoint = g30.data.ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    return endpoint, shelf_id, slot_id, subslot_id, port_id, subport_id


@set_port_description.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:
    endpoint, _, _, _, _, _ = g30_obtain_port_endpoint_from_port_name(optical_device, port_name)
    endpoint.modify(service_label=port_description)
    return endpoint.retrieve(depth=2)


@set_port_description.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock, port_name: str, port_description: str) -> dict[str, Any]:
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
    g42 = get_optical_device_client(optical_device)
    g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).modify(label=port_description)
    port = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).retrieve(depth=2, content="config")
    return port


@attributedispatch("platform")
def set_channel_description(optical_device: OpticalDeviceBlock, facility_id: str, description: str) -> dict[str, Any]:
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
    g30 = get_optical_device_client(optical_device)
    ids = facility_id.split("-")[-1]  # och-os-1/2/3 -> 1/2/3
    shelf_id, slot_id, port_id = ids.split("/")  # 1/2/3 -> 1, 2, 3
    g30.data.ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os.modify(service_label=description)
    return g30.data.ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os.retrieve(depth=2)


@set_channel_description.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock, facility_id: str, description: str) -> dict[str, Any]:
    g42 = get_optical_device_client(optical_device)
    port_name = facility_id  # e.g. "1-4-L2"

    channel_name = None
    channels = g42.data.ne.facilities.super_channel.retrieve(depth=2, content="config")
    for ch in channels:
        if any([carrier.startswith(port_name) for carrier in ch["carriers"]]):
            channel_name = ch["name"]
            break

    if channel_name is None:
        raise ValueError(f"Channel with port {port_name} not found")

    g42.data.ne.facilities.super_channel(channel_name).modify(label=description)

    return g42.data.ne.facilities.super_channel(channel_name).retrieve(depth=2, content="config")


@attributedispatch("platform")
def set_port_admin_state(
    optical_device: OpticalDeviceBlock,
    port_name: str,
    admin_state: Literal["up", "down", "maintenance"],
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
    flex = get_optical_device_client(optical_device)

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
    ## from any state to in-service state (we must know the current state of the finite state machine to move between states)
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

    ids = port_name.split("-")[-1]  # port-1/2/3 -> 1/2/3
    shelf_id, slot_id, port_id = ids.split("/")  # 1/2/3 -> 1, 2, 3

    g30 = get_optical_device_client(optical_device)
    port = g30.data.ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    port.modify(
        admin_status=status,
    )

    return port.retrieve(depth=2)


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

    g42 = get_optical_device_client(optical_device)
    port = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)

    port.modify(admin_state=status)

    return port.retrieve(depth=2)


@attributedispatch("platform")
def configure_termination_when_attaching_new_fiber(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
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
    flex = get_optical_device_client(optical_device)
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
    flex = get_optical_device_client(optical_device)
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
        g30 = get_optical_device_client(remote_port.optical_device)
        inventory = g30.data.ne.inventory_data.inventory.retrieve(depth=2)
        for item in inventory:
            if item.get("equipment-type") == "shelf" and item.get("shelf-id") == 1:
                return item["serial-number"]
        raise ValueError(f"Could not find shelf serial number for G30 device {remote_port.optical_device.fqdn}")

    if platform == Platform.GX_G42:
        return remote_port.optical_device.fqdn.replace(".garr.net", "")

    raise ValueError(f"Unsupported remote platform for FlexILS connection: {platform}")


def _extract_remote_port_id(remote_port: OpticalDevicePortBlock) -> str:
    """Extract and format the port ID from the remote port name."""
    match = re.search(r"\d", remote_port.port_name)
    if not match:
        raise ValueError(f"Could not extract port identifier from remote port name: {remote_port.port_name}")
    port_id = remote_port.port_name[match.start() :]
    return re.sub(r"[^a-zA-Z0-9]", "-", port_id)


@configure_termination_when_attaching_new_fiber.register(Platform.Groove_G30)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    port_name = port.port_name
    endpoint, shelf_id, slot_id, subslot_id, _, _ = g30_obtain_port_endpoint_from_port_name(optical_device, port_name)

    if remote_port.optical_device.platform == Platform.FlexILS:
        endpoint.modify(
            external_connectivity="yes",
            connected_to=f"{remote_port.optical_device.fqdn} {remote_port.port_name}",
            admin_status="up",
        )
        return endpoint.retrieve(depth=2)

    if remote_port.optical_device.platform == Platform.Groove_G30:
        if remote_port.optical_device.subscription_instance_id == optical_device.subscription_instance_id:
            endpoint.modify(
                external_connectivity="no",
                connected_to=f"patched to {remote_port.port_name}",
                admin_status="up",
            )
            return endpoint.retrieve(depth=2)
        if slot_id == "3" and subslot_id == "3":  # link H4
            g30 = get_optical_device_client(optical_device)
            booster = g30.data.ne.shelf(shelf_id).slot(slot_id).card.subslot("2").subcard.amplifier("ba")
            preamp = g30.data.ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.amplifier("pa")
            booster.modify(
                amplifier_name="ba",
                admin_status="up",
                amplifier_enable="enabled",
                input_los_shutdown="disabled",
                control_mode="manual",
                gain_range_control="manual",
                target_gain_range="standard",
                target_gain=22.0,
                output_voa=10.0,
                tilt_control_mode="manual",
                gain_tilt=0.0,
            )
            preamp.modify(
                amplifier_name="pa",
                admin_status="up",
                amplifier_enable="enabled",
                input_los_shutdown="disabled",
                control_mode="auto",
                gain_range_control="auto",
                target_gain_range="standard",
                tilt_control_mode="auto",
            )
            endpoint.modify(
                external_connectivity="yes",
                connected_to=f"{remote_port.optical_device.fqdn} {remote_port.port_name}",
                admin_status="up",
            )
            return {
                "port": endpoint.retrieve(depth=2),
                "booster": booster.retrieve(depth=2),
                "preamp": preamp.retrieve(depth=2),
            }
        msg = "Unsupported fiber connection between provided ports of different Groove G30 devices."
        raise ValueError(msg)

    raise ValueError(
        "Unsupported remote optical device platform when configuring Groove G30 remote port: "
        f"{remote_port.optical_device.platform}"
    )


@configure_termination_when_attaching_new_fiber.register(Platform.GX_G42)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    shelf_id, slot_id, port_id = port.port_name.split("-")

    g42 = get_optical_device_client(optical_device)
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    endpoint.modify(
        external_connectivity="yes",
        connected_to=f"{remote_port.optical_device.fqdn} {remote_port.port_name}",
        admin_status="up",
    )
    return endpoint.retrieve(depth=2)


@attributedispatch("platform")
def factory_reset_port_configuration(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    """
    Prune the configuration of an optical port on an OpticalDevice.
    """
    return attribute_dispatch_base(factory_reset_port_configuration, "platform", optical_device.platform)


@factory_reset_port_configuration.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    flex = get_optical_device_client(optical_device)
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
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    port_name = port.port_name
    endpoint, _, _, _, _, _ = g30_obtain_port_endpoint_from_port_name(optical_device, port_name)

    if "." in port_name:  # inside OCC2 card
        endpoint.modify(
            connected_to="",
        )
    else:
        endpoint.modify(
            external_connectivity="no",
            connected_to="",
            admin_status="down",
            port_mode="not-applicable",
            service_label="",
        )
    return endpoint.retrieve(depth=2)


@factory_reset_port_configuration.register(Platform.GX_G42)
def _(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
) -> dict[str, Any]:
    g42 = get_optical_device_client(optical_device)
    shelf_id, slot_id, port_id = port.port_name.split("-")
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    endpoint.modify(external_connectivity="no", connected_to="", admin_state="down", label="")
    return endpoint.retrieve(depth=2)


@attributedispatch("platform")
def check_fiber_terminating_port(
    optical_device: OpticalDeviceBlock,
    port: OpticalDevicePortBlock,
    remote_port: OpticalDevicePortBlock,
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
    flex = get_optical_device_client(optical_device)
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
    endpoint, _, _, _, _, _ = g30_obtain_port_endpoint_from_port_name(optical_device, port_name)
    port_data = endpoint.retrieve(depth=2)
    port_data = port_data[0]
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
        port_data.get("admin-status") == "up"
        and port_data.get("external-connectivity") == ext_connectivity
        and port_data.get("connected-to") == con_to_string
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
                        "admin-status": port_data.get("admin-status"),
                        "external-connectivity": port_data.get("external-connectivity"),
                        "connected-to": port_data.get("connected-to"),
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
    g42 = get_optical_device_client(optical_device)
    shelf_id, slot_id, port_id = port.port_name.split("-")
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    port_data = endpoint.retrieve(depth=2, content="config")
    """ e.g. port_data looks like this:
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
        port_data.get("admin-status") == "unlock"
        and port_data.get("external-connectivity") == "yes"
        and port_data.get("connected-to") == f"{remote_port.optical_device.fqdn} {remote_port.port_name}"
    )
    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": optical_device.fqdn,
                    "port_name": port.port_name,
                    "expected": {
                        "admin-status": "up",
                        "external-connectivity": "yes",
                        "connected-to": f"{remote_port.optical_device.fqdn} {remote_port.port_name}",
                    },
                    "actual": {
                        "admin-status": port_data.get("admin-status"),
                        "external-connectivity": port_data.get("external-connectivity"),
                        "connected-to": port_data.get("connected-to"),
                    },
                },
                indent=4,
            )
        )
