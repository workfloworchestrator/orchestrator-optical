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
- :mod:`orchestrator.optical.hal.connectivity` — the internal routes of a node
  from an add/drop port to its reachable degrees, with their occupancy.
- :mod:`orchestrator.optical.hal.spectrum` — the FlexILS optical circuit
  (OEL/OSNC/OCRS) engine and optical cross-connections.
- :mod:`orchestrator.optical.hal.reconcile` — the declarative configuration of the
  NETCONF devices (Groove G30, GX G42): render, diff, apply, release, and the golden
  configuration recorded per node.
- :mod:`orchestrator.optical.hal.sessions` — one session per device, shared within a scope
  (``@device_sessions()`` under ``@step``; form submits get one from ``retryable_form``) and kept open, idle,
  for the next scope.
- :mod:`orchestrator.optical.hal.read_cache` — the device reads of the input forms, remembered for a short
  time across the submits of a form (``retryable_form``); workflow steps always read the device.

Each area module routes to a per-device adapter under
:mod:`orchestrator.optical.hal.adapters` (one subpackage per vendor platform).
"""

from orchestrator.optical.hal.connectivity import IntraNodeEdge, retrieve_add_drop_connectivity
from orchestrator.optical.hal.node import (
    FlexilsGneProvider,
    OpticalNodeDiscovery,
    discover_flexils_node,
    discover_optical_node,
    get_flex_client,
    get_g30_client,
    get_g42_client,
    get_optical_node_client,
    retrieve_omses_terminating_on_device,
    retrieve_optical_node_role_and_software_version,
    retrieve_ports_spectral_occupations,
    retrieve_software_version,
)
from orchestrator.optical.hal.port import (
    check_fiber_terminating_port,
    configure_termination_when_attaching_new_fiber,
    factory_reset_port_configuration,
    get_device_ports_by_role,
    get_device_ports_grouped_by_role,
    get_transceiver_capacity_from_mode,
    is_transponder_line_port,
    parse_port_identifiers,
    retrieve_transceiver_modes,
    set_channel_description,
    set_port_admin_state,
    set_port_description,
)
from orchestrator.optical.hal.read_cache import DeviceReads, cached_device_read
from orchestrator.optical.hal.reconcile import (
    ConfigApplyError,
    ConfigConflictError,
    ConfigDriftError,
    config_overrides,
    golden_config,
)
from orchestrator.optical.hal.sessions import DeviceSessions, device_sessions
from orchestrator.optical.hal.spectrum import (
    create_optical_cross_connection,
    delete_optical_circuit,
    delete_optical_circuit_oel,
    delete_optical_cross_connection,
    ensure_optical_circuit,
    set_optical_circuit_label,
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
    forget_transponder_lines,
    get_signal_bandwidth,
    validate_trx_client,
    validate_trx_crossconnect,
    validate_trx_line,
)

__all__ = [
    "ConfigApplyError",
    "ConfigConflictError",
    "ConfigDriftError",
    "DeviceReads",
    "DeviceSessions",
    "FlexilsGneProvider",
    "IntraNodeEdge",
    "OpticalNodeDiscovery",
    "align_tx_power_to_target",
    "cached_device_read",
    "check_fiber_terminating_port",
    "config_overrides",
    "configure_line_transceivers",
    "configure_termination_when_attaching_new_fiber",
    "configure_transceiver_client",
    "configure_transponder_crossconnect",
    "create_optical_cross_connection",
    "delete_optical_circuit",
    "delete_optical_circuit_oel",
    "delete_optical_cross_connection",
    "delete_transponder_crossconnect",
    "delta_rx_power_vs_target",
    "device_sessions",
    "discover_flexils_node",
    "discover_optical_node",
    "ensure_optical_circuit",
    "factory_reset_port_configuration",
    "factory_reset_transponder_client",
    "factory_reset_transponder_lines",
    "forget_transponder_lines",
    "get_device_ports_by_role",
    "get_device_ports_grouped_by_role",
    "get_flex_client",
    "get_g30_client",
    "get_g42_client",
    "get_optical_node_client",
    "get_signal_bandwidth",
    "get_transceiver_capacity_from_mode",
    "golden_config",
    "is_transponder_line_port",
    "parse_port_identifiers",
    "retrieve_add_drop_connectivity",
    "retrieve_omses_terminating_on_device",
    "retrieve_optical_node_role_and_software_version",
    "retrieve_ports_spectral_occupations",
    "retrieve_software_version",
    "retrieve_transceiver_modes",
    "set_channel_description",
    "set_optical_circuit_label",
    "set_port_admin_state",
    "set_port_description",
    "validate_optical_circuit",
    "validate_trx_client",
    "validate_trx_crossconnect",
    "validate_trx_line",
]
