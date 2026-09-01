"""Transponder-area HAL dispatchers.

Signal bandwidth retrieval, line/client transceiver configuration, transponder
cross-connects, factory resets, validation and transmit/receive power
alignment for Optical Digital Service subscriptions. Each operation is routed
with ``match/case`` on the vendor and platform of the Optical Node to the
matching per-device adapter (see :mod:`orchestrator.optical.hal.adapters`).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from orchestrator.optical.hal._common import (
    OpticalNodeBlock,
    UnsupportedPlatformError,
    _as_flexils_block,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_flexils import transponder as flexils
from orchestrator.optical.hal.adapters.nokia_groove_g30 import transponder as groove_g30
from orchestrator.optical.hal.adapters.nokia_gx_g42 import transponder as gx_g42
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.utils.custom_types.frequencies import Frequency

__all__ = [
    "align_tx_power_to_target",
    "configure_line_transceivers",
    "configure_transceiver_client",
    "configure_transponder_crossconnect",
    "delete_transponder_crossconnect",
    "delta_rx_power_vs_target",
    "factory_reset_transponder_client",
    "factory_reset_transponder_lines",
    "get_signal_bandwidth",
    "validate_trx_client",
    "validate_trx_crossconnect",
    "validate_trx_line",
]


def get_signal_bandwidth(optical_node_block: OpticalNodeBlock, port_name: str) -> int:
    """Return the signal bandwidth, in MHz, of the transport channel carried by the given line port.

    Args:
        optical_node_block: The Optical Node hosting the line port.
        port_name: The line port name.

    Returns:
        The signal bandwidth in MHz.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the channel of the given port cannot be found.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_signal_bandwidth(optical_node_block, port_name)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_signal_bandwidth(optical_node_block, port_name)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "get_signal_bandwidth is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"get_signal_bandwidth: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def configure_line_transceivers(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> dict[str, Any]:
    """Configure the line transceivers on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Returns:
        A dictionary of configuration diffs, keyed by port/facility name.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the configuration is invalid.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.configure_line_transceivers(
                optical_node_block,
                port_names,
                central_frequencies,
                modes,
                descriptions,
            )
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.configure_line_transceivers(
                optical_node_block,
                port_names,
                central_frequencies,
                modes,
                descriptions,
            )
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "configure_line_transceivers is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"configure_line_transceivers: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def configure_transceiver_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> dict[str, Any]:
    """Configure the client port of a transceiver on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Returns:
        A dictionary of configuration diffs, keyed by facility name.

    Raises:
        NotImplementedError: If the node vendor or the requested speed is not supported.
        ValueError: If the configuration is invalid.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.configure_transceiver_client(optical_node_block, port_name, description, speed)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.configure_transceiver_client(optical_node_block, port_name, description, speed)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "configure_transceiver_client is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"configure_transceiver_client: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def configure_transponder_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    """Configure a cross-connect between client and line ports on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        client_port_name: The client port name.
        line_port_names: List of line port names.
        xconn_description: Optional description for the cross-connect.

    Returns:
        The created cross-connect configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross-connect cannot be created.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.configure_transponder_crossconnect(
                optical_node_block,
                client_port_name,
                line_port_names,
                xconn_description,
            )
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.configure_transponder_crossconnect(
                optical_node_block,
                client_port_name,
                line_port_names,
                xconn_description,
            )
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "configure_transponder_crossconnect is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"configure_transponder_crossconnect: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def delete_transponder_crossconnect(optical_node_block: OpticalNodeBlock, client_port_name: str) -> dict[str, Any]:
    """Delete a cross-connect between client and line ports on the given Optical Node.

    Args:
        optical_node_block: The Optical Node (transponder) to configure.
        client_port_name: The client port name.

    Returns:
        A dictionary with a ``"message"`` and the list of deleted cross-connects.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the client port has no ethernet service.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.delete_transponder_crossconnect(optical_node_block, client_port_name)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.delete_transponder_crossconnect(optical_node_block, client_port_name)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "delete_transponder_crossconnect is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"delete_transponder_crossconnect: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def factory_reset_transponder_client(optical_node_block: OpticalNodeBlock, port_name: str) -> dict[str, Any]:
    """Factory reset the client port configuration of the given Optical Node.

    Args:
        optical_node_block: The Optical Node to reset.
        port_name: The client port name.

    Returns:
        The reset configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.factory_reset_transponder_client(optical_node_block, port_name)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.factory_reset_transponder_client(optical_node_block, port_name)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "factory_reset_transponder_client is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"factory_reset_transponder_client: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def factory_reset_transponder_lines(
    optical_node_block: OpticalNodeBlock,
    line_port_names: list[str],
) -> dict[str, Any] | list[Any]:
    """Factory reset the transponder line configuration of the given Optical Node.

    Args:
        optical_node_block: The Optical Node to reset.
        line_port_names: The line port names.

    Returns:
        The reset configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.factory_reset_transponder_lines(optical_node_block, line_port_names)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.factory_reset_transponder_lines(optical_node_block, line_port_names)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "factory_reset_transponder_lines is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"factory_reset_transponder_lines: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def validate_trx_line(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    """Validate the transceiver line configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the configuration is invalid.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.validate_trx_line(
                optical_node_block,
                port_names,
                central_frequencies,
                modes,
                descriptions,
            )
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.validate_trx_line(
                optical_node_block,
                port_names,
                central_frequencies,
                modes,
                descriptions,
            )
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "validate_trx_line is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"validate_trx_line: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def validate_trx_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> None:
    """Validate the transceiver client configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Raises:
        NotImplementedError: If the node vendor or the requested speed is not supported.
        ValueError: If the configuration is invalid.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.validate_trx_client(optical_node_block, port_name, description, speed)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.validate_trx_client(optical_node_block, port_name, description, speed)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "validate_trx_client is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"validate_trx_client: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def validate_trx_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    """Validate the transponder cross-connect configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        client_port_name: The client port name.
        line_port_names: The line port names.
        xconn_description: The description of the cross-connect.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross-connect is missing or its description does not match.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.validate_trx_crossconnect(
                optical_node_block,
                client_port_name,
                line_port_names,
                xconn_description,
            )
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.validate_trx_crossconnect(
                optical_node_block,
                client_port_name,
                line_port_names,
                xconn_description,
            )
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "validate_trx_crossconnect is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"validate_trx_crossconnect: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def delta_rx_power_vs_target(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_name: str,
    circuit_identifier: str = "",
) -> float:
    r"""Return the difference :math:`P_{current\_rx} - P_{target\_rx}` in dB for the given optical channel.

    Args:
        optical_node_block: The Optical Node to compute for.
        optical_spectrum_name: The optical spectrum name; used as the CKTIDSUFFIX fallback.
        circuit_identifier: The subscription instance id of the circuit; used as the CKTIDSUFFIX.

    Returns:
        The delta target received power in dB.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the optical channel cannot be found on the device.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.delta_rx_power_vs_target(
                _as_flexils_block(optical_node_block),
                optical_spectrum_name,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            msg = "delta_rx_power_vs_target is not implemented for Groove G30 and GX G42 nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"delta_rx_power_vs_target: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def align_tx_power_to_target(
    optical_node_block: OpticalNodeBlock,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, Any]:
    r"""Subtract db_from_target decibels (dB) to the transmitted optical power.

    I.e. :math:`P^{new}_{tx} = P^{old}_{tx} - \Delta P`, where :math:`P^{old}_{tx}`
    is the currently configured required transmit power (``required-tx-optical-power``
    on G30, ``tx-power`` on G42), used as the baseline for the adjustment.

    Args:
        optical_node_block: The Optical Node to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.

    Returns:
        A dictionary indicating the old and new required transmit power.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If no transmit power is configured on the line port.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.align_tx_power_to_target(optical_node_block, line_port_name, db_from_target)
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.align_tx_power_to_target(optical_node_block, line_port_name, db_from_target)
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "align_tx_power_to_target is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"align_tx_power_to_target: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)
