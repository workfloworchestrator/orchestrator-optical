"""Port-area HAL dispatchers.

Each operation is routed with ``match/case`` on the vendor and platform of the
hosting Optical Node to the matching per-device adapter (see
:mod:`orchestrator.optical.hal.adapters`). Operations that act on a node
enumerate its ports; operations that act on a single port take the Optical Port
block and derive the host node from it.
"""

from __future__ import annotations

from typing import Any, Literal

from orchestrator.optical.hal._common import (
    UnsupportedPlatformError,
    _as_flexils_block,
    _as_g30_block,
    _as_g42_block,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_flexils import port as flexils
from orchestrator.optical.hal.adapters.nokia_groove_g30 import port as groove_g30
from orchestrator.optical.hal.adapters.nokia_gx_g42 import port as gx_g42
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import OpticalPipeType
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning

__all__ = [
    "check_fiber_terminating_port",
    "configure_termination_when_attaching_new_fiber",
    "factory_reset_port_configuration",
    "get_device_ports_by_role",
    "get_transceiver_capacity_from_mode",
    "is_transponder_line_port",
    "parse_port_identifiers",
    "retrieve_common_transceiver_modes",
    "retrieve_transceiver_modes",
    "set_channel_description",
    "set_port_admin_state",
    "set_port_description",
]


def get_device_ports_by_role(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    roles: list[OpticalPortRole] | None = None,
) -> list[str]:
    """Retrieve the device port names of an Optical Node for the requested Optical Port roles.

    This is the single port-enumeration operation of the HAL: a caller asks for the
    ports of the roles it can terminate on (e.g. only OLS line ports for a fiber
    span, every role when ``roles`` is ``None``). The vendor/platform of the hosting
    node selects the adapter, which enumerates the requested roles and de-duplicates
    the result.

    Args:
        optical_node_block: Optical Node of which the optical ports are to be retrieved.
        roles: The Optical Port roles to retrieve. ``None`` (the default) retrieves every role the
            node's vendor/platform supports.

    Returns:
        The de-duplicated device port names of the requested roles.

    Raises:
        UnsupportedPortRoleError: If a requested role is not supported by the node's vendor/platform.
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.get_device_ports_by_role(_as_flexils_block(optical_node_block), roles)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_device_ports_by_role(_as_g30_block(optical_node_block), roles)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_device_ports_by_role(_as_g42_block(optical_node_block), roles)
        case _:
            msg = f"get_device_ports_by_role: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def retrieve_transceiver_modes(optical_node_block: AnyOpticalNodeBlockProvisioningUnion, port_name: str) -> list[str]:
    """Retrieve the list of supported transceiver modes for a specific port on an Optical Node.

    Args:
        optical_node_block: The Optical Node containing the port.
        port_name: The name of the port for which to retrieve the modes.

    Returns:
        A list of supported modes for the specified port.

    Raises:
        ValueError: If the card of the port is not supported.
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.retrieve_transceiver_modes(_as_g30_block(optical_node_block), port_name)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.retrieve_transceiver_modes(_as_g42_block(optical_node_block), port_name)
        case (Vendor.NOKIA, Platform.FLEXILS):
            return []
        case _:
            msg = f"retrieve_transceiver_modes: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


#: Transceiver mode values reported by the adapters that are sentinels rather than
#: selectable operating modes (e.g. the Groove G30 ``"not-applicable"`` entry).
TRANSPORT_MODE_SENTINELS = frozenset({"not-applicable"})


def retrieve_common_transceiver_modes(node_ports: list[tuple[AnyOpticalNodeBlockProvisioningUnion, str]]) -> list[str]:
    """Return the operating modes supported by every given line port card.

    This is the set algebra behind the transport-mode dropdown of the Optical
    Digital Service forms: one service-wide mode must be valid on all of its
    line port cards, so only the intersection is offered.

    Args:
        node_ports: ``(host node block, device port name)`` pairs, typically the
            selected line ports of both sides of the service.

    Returns:
        The intersection of the per-card mode tables, in the order of the first
        card's table and without sentinel values. An empty list means the cards
        share no common mode (or every card reported an unknown table, e.g.
        FlexILS); it is NOT an error — callers offer a rejecting placeholder
        instead. Hard failures (unreachable devices, unsupported platforms such
        as packet nodes) propagate to the caller.
    """
    common: list[str] | None = None
    for optical_node_block, port_name in node_ports:
        modes = [
            mode
            for mode in retrieve_transceiver_modes(optical_node_block, port_name)
            if mode not in TRANSPORT_MODE_SENTINELS
        ]
        if not modes:
            # Unknown table: excluded from the intersection (fail open), mirroring
            # the construct-time mode check.
            continue
        common = modes if common is None else [mode for mode in common if mode in set(modes)]
        if not common:
            return []
    return common or []


def get_transceiver_capacity_from_mode(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion, mode: str
) -> int | None:
    """Return the carrier capacity in Gbit/s of a transceiver mode on an Optical Node.

    Each node family resolves the mode its own way (see the per-device
    adapters); modes without a resolvable bitrate yield None (unknown
    capacity), as do FlexILS nodes, whose modes are free text.

    Args:
        optical_node_block: The Optical Node hosting the line port.
        mode: The operating mode string stored on the transport channel.

    Returns:
        The capacity in Gbit/s, or None when the capacity is unknown.

    Raises:
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_transceiver_capacity_from_mode(mode)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_transceiver_capacity_from_mode(mode)
        case (Vendor.NOKIA, Platform.FLEXILS):
            return None
        case _:
            msg = f"get_transceiver_capacity_from_mode: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def set_port_description(optical_port_block: AnyOpticalPortBlockProvisioning, port_description: str) -> dict[str, Any]:
    """Set the description of an optical port.

    Args:
        optical_port_block: Optical Port of which the description is to be set.
        port_description: The description to set on the port.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.set_port_description(optical_port_block, port_description)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.set_port_description(optical_port_block, port_description)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.set_port_description(optical_port_block, port_description)
        case _:
            msg = f"set_port_description: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


def set_channel_description(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
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
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.set_channel_description(_as_g30_block(optical_node_block), facility_id, description)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.set_channel_description(_as_g42_block(optical_node_block), facility_id, description)
        case (Vendor.NOKIA, Platform.FLEXILS):
            return {"not-applicable": "Nokia FlexILS devices do not support channel descriptions"}
        case _:
            msg = f"set_channel_description: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def set_port_admin_state(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Set the administrative state of an optical port.

    Args:
        optical_port_block: Optical Port of which the admin state is to be set.
        admin_state: The administrative state to set on the port: ``["up", "down", "maintenance"]``.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.set_port_admin_state(optical_port_block, admin_state)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.set_port_admin_state(optical_port_block, admin_state)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.set_port_admin_state(optical_port_block, admin_state)
        case _:
            msg = f"set_port_admin_state: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


def configure_termination_when_attaching_new_fiber(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
    pipe_type: OpticalPipeType,
) -> dict[str, Any]:
    """Configure an optical port when attaching a fiber to it.

    The pipe type is forwarded to the adapters that key their decision on it
    (a Nokia FlexILS port picks its OTS/SCG path from the local port role and
    the pipe type).

    Args:
        optical_port_block: Optical Port to configure.
        remote_port_block: The remote Optical Port to connect to.
        pipe_type: The type of the Optical Pipe being terminated on the port.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.configure_termination(optical_port_block, remote_port_block, pipe_type)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.configure_termination(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.configure_termination(optical_port_block, remote_port_block)
        case _:
            msg = f"configure_termination_when_attaching_new_fiber: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


def factory_reset_port_configuration(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
    pipe_type: OpticalPipeType,
) -> dict[str, Any]:
    """Prune the configuration of an optical port.

    Args:
        optical_port_block: Optical Port of which the configuration is to be pruned.
        remote_port_block: The remote Optical Port connected to the port.
        pipe_type: The type of the Optical Pipe terminated on the port; forwarded to
            the adapters that key their reset path on it (Nokia FlexILS).

    Returns:
        The port configuration after the reset.

    Raises:
        ValueError: In case the configuration failed.
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.factory_reset(optical_port_block, remote_port_block, pipe_type)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.factory_reset(optical_port_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.factory_reset(optical_port_block)
        case _:
            msg = f"factory_reset_port_configuration: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


def check_fiber_terminating_port(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
    pipe_type: OpticalPipeType,
) -> None:
    """Check if an optical port attached to a fiber is correctly configured.

    Args:
        optical_port_block: Optical Port to check.
        remote_port_block: The remote Optical Port to verify the connection against.
        pipe_type: The type of the Optical Pipe terminated on the port; forwarded to
            the adapters that key their check path on it (Nokia FlexILS).

    Raises:
        ValueError: If the port configuration does not match the expected one.
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.check_fiber(optical_port_block, remote_port_block, pipe_type)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.check_fiber(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.check_fiber(optical_port_block, remote_port_block)
        case _:
            msg = f"check_fiber_terminating_port: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


def parse_port_identifiers(port_name: str, platform: Platform) -> tuple[str, str, str]:
    """Split a device port name into shelf, slot and port identifiers.

    The conventions are the device-native ones (see the HAL adapters):
    ``"port-1/2/3"`` on Groove G30, ``"1-4-L1"`` on GX G42.

    Args:
        port_name: The device-native port name.
        platform: The platform of the hosting node.

    Returns:
        The ``(shelf, slot, port)`` identifiers as strings.

    Raises:
        ValueError: If the platform is not a transponder platform or the name does not parse.
    """
    match platform:
        case Platform.GROOVE_G30:
            raw = port_name.split("-", 1)[-1]
            shelf, slot, port = raw.split("/")
        case Platform.GX_G42:
            shelf, slot, port = port_name.split("-", 2)
        case _:
            msg = f"Cannot parse port identifiers on platform {platform}"
            raise ValueError(msg)
    return shelf, slot, port


def is_transponder_line_port(port: str, platform: Platform) -> bool:
    """Return whether a port identifier is a line (coherent) port of its card."""
    match platform:
        case Platform.GROOVE_G30:
            return port.isdigit() and int(port) in (1, 2)
        case Platform.GX_G42:
            return port in ("L1", "L2")
        case _:
            return False
