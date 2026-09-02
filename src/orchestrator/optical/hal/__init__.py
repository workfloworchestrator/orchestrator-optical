"""Hardware Abstraction Layer for the optical orchestrator.

This package provides the device-facing operations of the optical orchestrator,
organized by area and dispatched on the vendor/platform of the Optical Node
product block with ``match/case``:

- :mod:`orchestrator.optical.hal.node` — node discovery, client factories and
  the node-level retrieve/validate operations.
- :mod:`orchestrator.optical.hal.port` — port enumeration, admin state and
  fiber-termination configure/reset/check.
- :mod:`orchestrator.optical.hal.transport_channel` — transponder line/client
  configuration, cross-connects, validation and power alignment.
- :mod:`orchestrator.optical.hal.spectrum` — the FlexILS optical circuit
  (OEL/OSNC/OCRS) engine and optical cross-connections.

Each area module routes to a per-device adapter under
:mod:`orchestrator.optical.hal.adapters` (one subpackage per vendor platform).
"""

from orchestrator.optical.hal.node import (
    FlexilsGneProvider,
    discover_flexils_node,
    get_flex_client,
    get_g30_client,
    get_g42_client,
    get_optical_node_client,
    retrieve_omses_terminating_on_device,
    retrieve_optical_node_role_and_software_version,
    retrieve_ports_spectral_occupations,
    retrieve_software_version,
    validate_management_network_config,
)
from orchestrator.optical.hal.port import (
    check_fiber_terminating_port,
    configure_termination_when_attaching_new_fiber,
    factory_reset_port_configuration,
    get_device_client_ports_names,
    get_device_line_ports_names,
    get_device_ports_by_role,
    get_device_ports_names,
    retrieve_transceiver_modes,
    set_channel_description,
    set_port_admin_state,
    set_port_description,
)
from orchestrator.optical.hal.spectrum import (
    append_optical_circuit_label,
    create_optical_cross_connection,
    delete_optical_circuit,
    delete_optical_cross_connection,
    deploy_optical_circuit,
    modify_optical_circuit,
    validate_optical_circuit,
)
from orchestrator.optical.hal.transport_channel import (
    align_tx_power_to_target,
    configure_line_transceivers,
    configure_transceiver_client,
    configure_transponder_crossconnect,
    delete_transponder_crossconnect,
    delta_rx_power_vs_target,
    factory_reset_transponder_client,
    factory_reset_transponder_lines,
    get_signal_bandwidth,
    validate_trx_client,
    validate_trx_crossconnect,
    validate_trx_line,
)

__all__ = [
    "FlexilsGneProvider",
    "align_tx_power_to_target",
    "append_optical_circuit_label",
    "check_fiber_terminating_port",
    "configure_line_transceivers",
    "configure_termination_when_attaching_new_fiber",
    "configure_transceiver_client",
    "configure_transponder_crossconnect",
    "create_optical_cross_connection",
    "delete_optical_circuit",
    "delete_optical_cross_connection",
    "delete_transponder_crossconnect",
    "delta_rx_power_vs_target",
    "deploy_optical_circuit",
    "discover_flexils_node",
    "factory_reset_port_configuration",
    "factory_reset_transponder_client",
    "factory_reset_transponder_lines",
    "get_device_client_ports_names",
    "get_device_line_ports_names",
    "get_device_ports_by_role",
    "get_device_ports_names",
    "get_flex_client",
    "get_g30_client",
    "get_g42_client",
    "get_optical_node_client",
    "get_signal_bandwidth",
    "modify_optical_circuit",
    "retrieve_omses_terminating_on_device",
    "retrieve_optical_node_role_and_software_version",
    "retrieve_ports_spectral_occupations",
    "retrieve_software_version",
    "retrieve_transceiver_modes",
    "set_channel_description",
    "set_port_admin_state",
    "set_port_description",
    "validate_management_network_config",
    "validate_optical_circuit",
    "validate_trx_client",
    "validate_trx_crossconnect",
    "validate_trx_line",
]
