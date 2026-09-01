"""Nokia GX G42 port-level HAL operations."""

import json
from typing import Any, Literal

from orchestrator.optical.hal._common import _node_id, _port_name
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port._abstracts import _AbstractOpticalPortBlockProvisioning
from orchestrator.optical.services.nokia.g42.data_models.ioa_network_element import (
    AdminStateEnum,
    ExternalConnectivityEnum,
    PortTypeEnum,
)


def get_device_ports_names(optical_node_block: NokiaGxG42BlockProvisioning) -> list[str]:
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


def get_device_client_ports_names(optical_node_block: NokiaGxG42BlockProvisioning) -> list[str]:
    """Return the AIDs of the client ports of a GX G42 node."""
    g42 = get_g42_client(optical_node_block)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports: list[str] = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in (card.port or []) if p.AID is not None and p.installed_type)

    return ports


def get_device_line_ports_names(optical_node_block: NokiaGxG42BlockProvisioning) -> list[str]:
    """Return the AIDs of the line ports of a GX G42 node."""
    g42 = get_g42_client(optical_node_block)

    cards = g42.data.ne.equipment.card.retrieve(depth=3, content="all")

    ports: list[str] = []
    for card in cards:
        if card.required_type == "gx:CHM6":
            ports.extend(p.AID for p in (card.port or []) if p.AID is not None and p.port_type == PortTypeEnum.LINE)

    return ports


def retrieve_transceiver_modes(optical_node_block: NokiaGxG42BlockProvisioning, port_name: str) -> list[str]:
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


def set_port_description(port_block: _AbstractOpticalPortBlockProvisioning, port_description: str) -> dict[str, Any]:
    """Set the description of a GX G42 optical port.

    Args:
        port_block: Optical Port of which the description is to be set.
        port_description: The description to set on the port.

    Returns:
        The port configuration after the update.
    """
    host_node = port_block.optical_port_host_node
    port_name = _port_name(port_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
    g42 = get_g42_client(host_node)
    port_uri = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)

    port_config = port_uri.retrieve(content="config", depth=2)
    port_config.label = port_description

    port_uri.update(port_config)

    return port_uri.retrieve(content="config", depth=2).model_dump()


def set_channel_description(
    optical_node_block: NokiaGxG42BlockProvisioning,
    facility_id: str,
    description: str,
) -> dict[str, Any]:
    """Set the description of a GX G42 optical channel.

    Args:
        optical_node_block: Optical Node of which the optical channel is to be modified.
        facility_id: The id of the optical channel to set the description on (e.g. ``"1/1/1"``).
        description: The description to set on the channel.

    Returns:
        The channel configuration after the update.
    """
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


def set_port_admin_state(
    port_block: _AbstractOpticalPortBlockProvisioning,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Set the administrative state of a GX G42 optical port.

    Args:
        port_block: Optical Port of which the admin state is to be set.
        admin_state: The administrative state to set on the port: ["up", "down", "maintenance"].

    Returns:
        The port configuration after the update.
    """
    host_node = port_block.optical_port_host_node
    port_name = _port_name(port_block)
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


def configure_termination(
    optical_port_block: _AbstractOpticalPortBlockProvisioning,
    remote_port_block: _AbstractOpticalPortBlockProvisioning,
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


def factory_reset(optical_port_block: _AbstractOpticalPortBlockProvisioning) -> dict[str, Any]:
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


def check_fiber(
    optical_port_block: _AbstractOpticalPortBlockProvisioning,
    remote_port_block: _AbstractOpticalPortBlockProvisioning,
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
