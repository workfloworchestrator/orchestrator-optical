"""Nokia GX G42 port-level HAL operations.

The configuration is declarative (see :mod:`orchestrator.optical.hal.reconcile`): it is
rendered, then applied, verified or released. It is owned by the Optical Port block.
"""

import re
from typing import Any, Literal

from orchestrator.optical.hal._common import (
    UnsupportedPortRoleError,
    _node_id,
    _port_name,
    _ports_by_role,
    _retrieve_required,
    _same_node,
)
from orchestrator.optical.hal.adapters.nokia_gx_g42._sdk import (
    PortTypeEnum,
)
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import g42_port_node, get_g42_client
from orchestrator.optical.hal.reconcile import Fragment, apply_config, fragment, release_config, verify_config
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning

#: Port roles a GX G42 node can enumerate: transponder line and client ports (no OLS ports).
_G42_SUPPORTED_ROLES = frozenset({OpticalPortRole.TRANSPONDER_LINE, OpticalPortRole.TRANSPONDER_CLIENT})


def _g42_chm6_cards(optical_node_block: NokiaGxG42BlockProvisioning) -> list[Any]:
    """Return the CHM6 cards of a GX G42 node."""
    g42 = get_g42_client(optical_node_block)
    return [
        card
        for card in g42.data.ioa_network_element_ne.equipment.card.retrieve(depth=3, content="all")
        if card.required_type == "gx:CHM6"
    ]


def _g42_client_ports_names(optical_node_block: NokiaGxG42BlockProvisioning) -> list[str]:
    """Return the AIDs of the client ports of a GX G42 node."""
    return [
        p.AID
        for card in _g42_chm6_cards(optical_node_block)
        for p in (card.port or [])
        if p.AID is not None and p.installed_type
    ]


def _g42_line_ports_names(optical_node_block: NokiaGxG42BlockProvisioning) -> list[str]:
    """Return the AIDs of the line ports of a GX G42 node."""
    return [
        p.AID
        for card in _g42_chm6_cards(optical_node_block)
        for p in (card.port or [])
        if p.AID is not None and p.port_type == PortTypeEnum.LINE
    ]


def get_device_ports_by_role(
    optical_node_block: NokiaGxG42BlockProvisioning,
    roles: list[OpticalPortRole] | None = None,
) -> list[str]:
    """Return the device port names of a GX G42 node for the requested Optical Port roles.

    A GX G42 node exposes only transponder line and client ports; it cannot enumerate OLS or
    coherent pluggable ports.
    """
    line_ports: list[str] | None = None
    client_ports: list[str] | None = None

    def port_names_for_role(role: OpticalPortRole) -> list[str]:
        nonlocal line_ports, client_ports
        if role is OpticalPortRole.TRANSPONDER_LINE:
            if line_ports is None:
                line_ports = _g42_line_ports_names(optical_node_block)
            return line_ports
        if role is OpticalPortRole.TRANSPONDER_CLIENT:
            if client_ports is None:
                client_ports = _g42_client_ports_names(optical_node_block)
            return client_ports
        msg = f"GX G42 does not support port role {role.value}"
        raise UnsupportedPortRoleError(msg)

    return _ports_by_role(_G42_SUPPORTED_ROLES, port_names_for_role, roles)


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

    card = _retrieve_required(
        g42.data.ioa_network_element_ne.equipment.card(f"{shelf_id}-{slot_id}").retrieve, depth=2, content="config"
    )
    card_type = card.required_subtype

    supported_modes = mapping.get(card_type) if card_type is not None else None

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


#: Rendering units of the port configuration owned by an Optical Port block.
DESCRIPTION_SCOPE = "description"
ADMIN_STATE_SCOPE = "admin-state"
TERMINATION_SCOPE = "termination"
CHANNEL_DESCRIPTION_SCOPE = "channel-description:{}"

_ADMIN_STATE = {"up": "unlock", "down": "lock", "maintenance": "maintenance"}


def _port_node(port_block: AnyOpticalPortBlockProvisioning) -> Any:
    """Return the navigator node of the device port of an Optical Port block."""
    return g42_port_node(get_g42_client(port_block.optical_port_host_node).data, _port_name(port_block))


def set_port_description(port_block: AnyOpticalPortBlockProvisioning, port_description: str) -> dict[str, Any]:
    """Make a GX G42 optical port carry the given description; return the applied diff."""
    fragments = [fragment(_port_node(port_block), label=port_description)]
    return apply_config(
        port_block.optical_port_host_node, port_block.subscription_instance_id, DESCRIPTION_SCOPE, fragments
    )


def set_channel_description(
    optical_node_block: NokiaGxG42BlockProvisioning,
    facility_id: str,
    description: str,
) -> dict[str, Any]:
    """Make the GX G42 super-channel carried by a line port carry the given description; return the applied diff.

    Args:
        optical_node_block: Optical Node of which the optical channel is to be modified,
            which also owns the setting.
        facility_id: The name of the line port carrying the channel (e.g. ``"1-4-L2"``).
        description: The description to set on the channel.

    Raises:
        ValueError: If no super-channel is carried by the port.
    """
    g42 = get_g42_client(optical_node_block)
    super_channels = g42.data.ioa_network_element_ne.facilities.super_channel
    channel_name = next(
        (
            channel.name
            for channel in super_channels.retrieve(depth=2, content="config") or []
            if any(carrier.startswith(facility_id) for carrier in channel.carriers)
        ),
        None,
    )
    if channel_name is None:
        msg = f"Channel with port {facility_id} not found"
        raise ValueError(msg)
    return apply_config(
        optical_node_block,
        optical_node_block.subscription_instance_id,
        CHANNEL_DESCRIPTION_SCOPE.format(facility_id),
        [fragment(super_channels(channel_name), label=description)],
    )


def set_port_admin_state(
    port_block: AnyOpticalPortBlockProvisioning,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Make a GX G42 optical port run the given administrative state; return the applied diff."""
    fragments = [fragment(_port_node(port_block), admin_state=_ADMIN_STATE[admin_state])]
    return apply_config(
        port_block.optical_port_host_node, port_block.subscription_instance_id, ADMIN_STATE_SCOPE, fragments
    )


def render_termination(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> list[Fragment]:
    """Render a GX G42 port terminating a fiber that leads to the remote port.

    A same-node fiber patch (both ends on this device) is recorded as an internal
    patch (no external connectivity); every other connection is an external one.
    """
    host_node = optical_port_block.optical_port_host_node
    remote_host_node = remote_port_block.optical_port_host_node
    remote_port_name = _port_name(remote_port_block)
    if _same_node(host_node, remote_host_node):
        connectivity, connected_to = "no", f"patched to {remote_port_name}"
    else:
        connectivity, connected_to = "yes", f"{_node_id(remote_host_node)} {remote_port_name}"
    return [
        fragment(
            _port_node(optical_port_block),
            external_connectivity=connectivity,
            connected_to=connected_to,
            admin_state="unlock",
        )
    ]


def configure_termination(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> dict[str, Any]:
    """Make a GX G42 port run the configuration of the fiber attached to it; return the applied diff."""
    return apply_config(
        optical_port_block.optical_port_host_node,
        optical_port_block.subscription_instance_id,
        TERMINATION_SCOPE,
        render_termination(optical_port_block, remote_port_block),
    )


def factory_reset(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> dict[str, Any]:
    """Release the fiber termination of a GX G42 port; return the applied diff.

    The port leaves go back to their factory value unless another product block (e.g. a
    service using the port) still holds them.
    """
    return release_config(
        optical_port_block.optical_port_host_node,
        optical_port_block.subscription_instance_id,
        TERMINATION_SCOPE,
        render_termination(optical_port_block, remote_port_block),
    )


def check_fiber(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> None:
    """Check that a GX G42 port attached to a fiber runs its termination configuration.

    Raises:
        ValueError: If the port configuration differs.
    """
    verify_config(
        optical_port_block.optical_port_host_node,
        optical_port_block.subscription_instance_id,
        TERMINATION_SCOPE,
        render_termination(optical_port_block, remote_port_block),
    )


def get_transceiver_capacity_from_mode(mode: str) -> int | None:
    """Return the carrier capacity in Gbit/s of a GX G42 transceiver mode.

    G42 modes lead with the bitrate in Gbit/s before the ``E`` separator
    (e.g. ``400E.63P``); anything else yields None (unknown capacity).

    Args:
        mode: The operating mode string stored on the transport channel.

    Returns:
        The capacity in Gbit/s, or None when the mode carries no bitrate.
    """
    match = re.match(r"(\d+)E\.", mode.strip())
    return int(match.group(1)) if match else None
