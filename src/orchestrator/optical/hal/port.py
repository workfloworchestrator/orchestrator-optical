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
    OpticalNodeBlock,
    UnsupportedPlatformError,
    _as_flexils_block,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_flexils import port as flexils
from orchestrator.optical.hal.adapters.nokia_groove_g30 import port as groove_g30
from orchestrator.optical.hal.adapters.nokia_gx_g42 import port as gx_g42
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import AbstractOpticalPortBlockInactive

__all__ = [
    "check_fiber_terminating_port",
    "configure_termination_when_attaching_new_fiber",
    "factory_reset_port_configuration",
    "get_device_client_ports_names",
    "get_device_line_ports_names",
    "get_device_ports_names",
    "retrieve_transceiver_modes",
    "set_channel_description",
    "set_port_admin_state",
    "set_port_description",
]


def get_device_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Retrieve the list of optical port names of an Optical Node.

    Args:
        optical_node_block: Optical Node of which the optical ports are to be retrieved.

    Returns:
        A list of optical port names of the optical node.

    Raises:
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.get_device_ports_names(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_device_ports_names(optical_node_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_device_ports_names(optical_node_block)
        case _:
            msg = f"get_device_ports_names: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def get_device_client_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Retrieve the list of client optical port names of an Optical Node.

    Args:
        optical_node_block: Optical Node of which the client optical ports are to be retrieved.

    Returns:
        A list of client optical port names of the optical node.

    Raises:
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.get_device_client_ports_names(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_device_client_ports_names(optical_node_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_device_client_ports_names(optical_node_block)
        case _:
            msg = f"get_device_client_ports_names: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def get_device_line_ports_names(optical_node_block: OpticalNodeBlock) -> list[str]:
    """Retrieve the list of line optical port names of an Optical Node.

    Args:
        optical_node_block: Optical Node of which the line optical ports are to be retrieved.

    Returns:
        A list of line optical port names of the optical node.

    Raises:
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.get_device_line_ports_names(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_device_line_ports_names(optical_node_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_device_line_ports_names(optical_node_block)
        case _:
            msg = f"get_device_line_ports_names: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def retrieve_transceiver_modes(optical_node_block: OpticalNodeBlock, port_name: str) -> list[str]:
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
            return groove_g30.retrieve_transceiver_modes(optical_node_block, port_name)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.retrieve_transceiver_modes(optical_node_block, port_name)
        case (Vendor.NOKIA, Platform.FLEXILS):
            return []
        case _:
            msg = f"retrieve_transceiver_modes: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def set_port_description(optical_port_block: AbstractOpticalPortBlockInactive, port_description: str) -> dict[str, Any]:
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
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.set_channel_description(optical_node_block, facility_id, description)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.set_channel_description(optical_node_block, facility_id, description)
        case (Vendor.NOKIA, Platform.FLEXILS):
            return {"not-applicable": "Nokia FlexILS devices do not support channel descriptions"}
        case _:
            msg = f"set_channel_description: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def set_port_admin_state(
    optical_port_block: AbstractOpticalPortBlockInactive,
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
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.configure_termination(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.configure_termination(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.configure_termination(optical_port_block, remote_port_block)
        case _:
            msg = f"configure_termination_when_attaching_new_fiber: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


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
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.factory_reset(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.factory_reset(optical_port_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.factory_reset(optical_port_block)
        case _:
            msg = f"factory_reset_port_configuration: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)


def check_fiber_terminating_port(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> None:
    """Check if an optical port attached to a fiber is correctly configured.

    Args:
        optical_port_block: Optical Port to check.
        remote_port_block: The remote Optical Port to verify the connection against.

    Raises:
        ValueError: If the port configuration does not match the expected one.
        UnsupportedPlatformError: If the host node is not supported by this operation.
    """
    host_node = optical_port_block.optical_port_host_node
    match _vendor_platform(host_node):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.check_fiber(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.check_fiber(optical_port_block, remote_port_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.check_fiber(optical_port_block, remote_port_block)
        case _:
            msg = f"check_fiber_terminating_port: {type(host_node).__name__}"
            raise UnsupportedPlatformError(msg)
