"""Unit tests for the HAL area dispatchers.

The dispatchers are pure ``match/case`` routers: they narrow the block and either
return a documented no-op value, raise a typed error, or delegate to a per-device
adapter. Device-bound branches are exercised by replacing the adapter seam with a
recorder, so no network or SSH connection is ever made.
"""

from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from orchestrator.optical.hal import node as hal_node
from orchestrator.optical.hal import port as hal_port
from orchestrator.optical.hal import spectrum as hal_spectrum
from orchestrator.optical.hal import transport_channel as hal_transport
from orchestrator.optical.hal._common import UnsupportedPlatformError
from orchestrator.optical.hal.adapters.nokia_flexils import node as flexils_node
from orchestrator.optical.hal.adapters.nokia_flexils import port as flexils_port
from orchestrator.optical.hal.adapters.nokia_flexils import spectrum as flexils_spectrum
from orchestrator.optical.hal.adapters.nokia_flexils import transponder as flexils_transponder
from orchestrator.optical.hal.adapters.nokia_groove_g30 import node as g30_node
from orchestrator.optical.hal.adapters.nokia_groove_g30 import port as g30_port
from orchestrator.optical.hal.adapters.nokia_groove_g30 import transponder as g30_transponder
from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as g42_node
from orchestrator.optical.hal.adapters.nokia_gx_g42 import port as g42_port
from orchestrator.optical.hal.adapters.nokia_gx_g42 import transponder as g42_transponder
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import OpticalPipeType
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed

_PASSBAND = (191_325_000, 196_125_000)
_CARRIER = (193_100_000, 6_250)
_FREQUENCIES = (193_100_000,)
_SECTION = SimpleNamespace()
_SPEED = OpticalDigitalServiceSpeed(100)


class _Recorder:
    """Callable that records every invocation and returns a canned result."""

    def __init__(self, result: Any = None) -> None:
        self.calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.result = result

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((args, kwargs))
        return self.result


def _patch(monkeypatch: pytest.MonkeyPatch, module: Any, name: str, result: Any = None) -> _Recorder:
    recorder = _Recorder(result)
    monkeypatch.setattr(module, name, recorder)
    return recorder


def _management(
    vendor: Vendor | str,
    platform: Platform | str,
    fqdn: str | None = "node.example.com",
) -> SimpleNamespace:
    return SimpleNamespace(
        optical_module_node_vendor=vendor,
        optical_module_node_platform=platform,
        optical_module_node_fqdn=fqdn,
    )


def _node_block(block_cls: type, vendor: Vendor, platform: Platform) -> Any:
    subscription_id = uuid4()
    return block_cls.model_construct(
        name=block_cls.__name__,
        subscription_instance_id=subscription_id,
        owner_subscription_id=subscription_id,
        management=_management(vendor, platform),
    )


def _flexils_node() -> Any:
    return _node_block(NokiaFlexIlsBlockProvisioning, Vendor.NOKIA, Platform.FLEXILS)


def _g30_node() -> Any:
    return _node_block(NokiaGrooveG30BlockProvisioning, Vendor.NOKIA, Platform.GROOVE_G30)


def _g42_node() -> Any:
    return _node_block(NokiaGxG42BlockProvisioning, Vendor.NOKIA, Platform.GX_G42)


def _unknown_node() -> Any:
    return SimpleNamespace(management=_management("Acme", "Unknown"))


def _port(host_node: Any, name: str = "port-1/2/3") -> Any:
    return SimpleNamespace(optical_port_host_node=host_node, optical_port_name=name)


# ---------------------------------------------------------------------------
# Unsupported platform fallbacks
# ---------------------------------------------------------------------------

_NODE_UNSUPPORTED_CALLS = [
    pytest.param(lambda block: hal_node.get_optical_node_client(block), id="get_optical_node_client"),
    pytest.param(lambda block: hal_node.retrieve_software_version(block), id="retrieve_software_version"),
    pytest.param(
        lambda block: hal_node.retrieve_optical_node_role_and_software_version(block),
        id="retrieve_optical_node_role_and_software_version",
    ),
    pytest.param(
        lambda block: hal_node.retrieve_omses_terminating_on_device(block),
        id="retrieve_omses_terminating_on_device",
    ),
    pytest.param(
        lambda block: hal_node.retrieve_ports_spectral_occupations(block),
        id="retrieve_ports_spectral_occupations",
    ),
    pytest.param(
        lambda block: hal_node.validate_management_network_config(block),
        id="validate_management_network_config",
    ),
]


@pytest.mark.parametrize("call", _NODE_UNSUPPORTED_CALLS)
def test_node_dispatchers_reject_unsupported_platform(call: Any) -> None:
    with pytest.raises(UnsupportedPlatformError):
        call(_unknown_node())


_PORT_UNSUPPORTED_CALLS = [
    pytest.param(lambda node: hal_port.get_device_ports_by_role(node), id="get_device_ports_by_role"),
    pytest.param(lambda node: hal_port.retrieve_transceiver_modes(node, "port-1/2/3"), id="retrieve_transceiver_modes"),
    pytest.param(lambda node: hal_port.set_channel_description(node, "1/1/1", "desc"), id="set_channel_description"),
    pytest.param(lambda node: hal_port.set_port_description(_port(node), "desc"), id="set_port_description"),
    pytest.param(lambda node: hal_port.set_port_admin_state(_port(node), "up"), id="set_port_admin_state"),
    pytest.param(
        lambda node: hal_port.configure_termination_when_attaching_new_fiber(
            _port(node), _port(node), OpticalPipeType.SPAN
        ),
        id="configure_termination_when_attaching_new_fiber",
    ),
    pytest.param(
        lambda node: hal_port.factory_reset_port_configuration(_port(node), _port(node), OpticalPipeType.SPAN),
        id="factory_reset_port_configuration",
    ),
    pytest.param(
        lambda node: hal_port.check_fiber_terminating_port(_port(node), _port(node), OpticalPipeType.SPAN),
        id="check_fiber_terminating_port",
    ),
]


@pytest.mark.parametrize("call", _PORT_UNSUPPORTED_CALLS)
def test_port_dispatchers_reject_unsupported_platform(call: Any) -> None:
    with pytest.raises(UnsupportedPlatformError):
        call(_unknown_node())


_SPECTRUM_UNSUPPORTED_CALLS = [
    pytest.param(
        lambda node: hal_spectrum.ensure_optical_circuit(node, _SECTION, "spec", _PASSBAND, _CARRIER),
        id="ensure_optical_circuit",
    ),
    pytest.param(
        lambda node: hal_spectrum.delete_optical_circuit(node, _SECTION, "spec", _PASSBAND),
        id="delete_optical_circuit",
    ),
    pytest.param(
        lambda node: hal_spectrum.validate_optical_circuit(node, _SECTION, "spec", _PASSBAND, _CARRIER, "label"),
        id="validate_optical_circuit",
    ),
    pytest.param(
        lambda node: hal_spectrum.set_optical_circuit_label(node, _SECTION, "spec", _PASSBAND, "label"),
        id="set_optical_circuit_label",
    ),
    pytest.param(
        lambda node: hal_spectrum.create_optical_cross_connection(node, _port(node), _port(node), _PASSBAND),
        id="create_optical_cross_connection",
    ),
    pytest.param(
        lambda node: hal_spectrum.delete_optical_cross_connection(node, _port(node), _port(node), _PASSBAND),
        id="delete_optical_cross_connection",
    ),
]


@pytest.mark.parametrize("call", _SPECTRUM_UNSUPPORTED_CALLS)
def test_spectrum_dispatchers_reject_unsupported_platform(call: Any) -> None:
    with pytest.raises(UnsupportedPlatformError):
        call(_unknown_node())


_TRANSPORT_UNSUPPORTED_CALLS = [
    pytest.param(lambda node: hal_transport.get_signal_bandwidth(node, "port-1"), id="get_signal_bandwidth"),
    pytest.param(
        lambda node: hal_transport.configure_line_transceivers(node, ("port-1",), _FREQUENCIES, ("mode",), ("desc",)),
        id="configure_line_transceivers",
    ),
    pytest.param(
        lambda node: hal_transport.configure_transceiver_client(node, "port-1", "desc", _SPEED),
        id="configure_transceiver_client",
    ),
    pytest.param(
        lambda node: hal_transport.configure_transponder_crossconnect(node, "port-1", ["port-2"]),
        id="configure_transponder_crossconnect",
    ),
    pytest.param(
        lambda node: hal_transport.delete_transponder_crossconnect(node, "port-1"),
        id="delete_transponder_crossconnect",
    ),
    pytest.param(
        lambda node: hal_transport.factory_reset_transponder_client(node, "port-1"),
        id="factory_reset_transponder_client",
    ),
    pytest.param(
        lambda node: hal_transport.factory_reset_transponder_lines(node, ["port-1"]),
        id="factory_reset_transponder_lines",
    ),
    pytest.param(
        lambda node: hal_transport.validate_trx_line(node, ("port-1",), _FREQUENCIES, ("mode",), ("desc",)),
        id="validate_trx_line",
    ),
    pytest.param(
        lambda node: hal_transport.validate_trx_client(node, "port-1", "desc", _SPEED),
        id="validate_trx_client",
    ),
    pytest.param(
        lambda node: hal_transport.validate_trx_crossconnect(node, "port-1", ["port-2"]),
        id="validate_trx_crossconnect",
    ),
    pytest.param(
        lambda node: hal_transport.delta_rx_power_vs_target(node, "spec"),
        id="delta_rx_power_vs_target",
    ),
    pytest.param(
        lambda node: hal_transport.align_tx_power_to_target(node, "port-1", Decimal("0.5")),
        id="align_tx_power_to_target",
    ),
]


@pytest.mark.parametrize("call", _TRANSPORT_UNSUPPORTED_CALLS)
def test_transport_dispatchers_reject_unsupported_platform(call: Any) -> None:
    with pytest.raises(UnsupportedPlatformError):
        call(_unknown_node())


# ---------------------------------------------------------------------------
# Documented no-op branches
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("node_factory", [_g30_node, _g42_node], ids=["g30", "g42"])
def test_retrieve_omses_is_empty_for_g30_and_g42(node_factory: Any) -> None:
    assert hal_node.retrieve_omses_terminating_on_device(node_factory()) == []


@pytest.mark.parametrize("node_factory", [_g30_node, _g42_node], ids=["g30", "g42"])
def test_retrieve_ports_spectral_occupations_is_empty_for_g30_and_g42(node_factory: Any) -> None:
    assert hal_node.retrieve_ports_spectral_occupations(node_factory()) == {}


def test_validate_management_network_config_is_noop_for_flexils_and_g42() -> None:
    assert hal_node.validate_management_network_config(_flexils_node()) is None
    assert hal_node.validate_management_network_config(_g42_node()) is None


def test_retrieve_transceiver_modes_is_empty_for_flexils() -> None:
    assert hal_port.retrieve_transceiver_modes(_flexils_node(), "port-1") == []


def test_set_channel_description_is_not_applicable_for_flexils() -> None:
    result = hal_port.set_channel_description(_flexils_node(), "1/1/1", "desc")

    assert "not-applicable" in result


@pytest.mark.parametrize("node_factory", [_g30_node, _g42_node], ids=["g30", "g42"])
@pytest.mark.parametrize(
    "call",
    [
        pytest.param(
            lambda node: hal_spectrum.ensure_optical_circuit(node, _SECTION, "spec", _PASSBAND, _CARRIER),
            id="ensure_optical_circuit",
        ),
        pytest.param(
            lambda node: hal_spectrum.delete_optical_circuit(node, _SECTION, "spec", _PASSBAND),
            id="delete_optical_circuit",
        ),
        pytest.param(
            lambda node: hal_spectrum.delete_optical_circuit_oel(node, "cid"),
            id="delete_optical_circuit_oel",
        ),
        pytest.param(
            lambda node: hal_spectrum.set_optical_circuit_label(node, _SECTION, "spec", _PASSBAND, "label"),
            id="set_optical_circuit_label",
        ),
    ],
)
def test_circuit_lifecycle_is_empty_diff_for_g30_and_g42(node_factory: Any, call: Any) -> None:
    """Platforms without internal cross-connections provision nothing, so the diff is empty."""
    result = call(node_factory())

    assert result == {"---": {}, "+++": {}}


@pytest.mark.parametrize("node_factory", [_g30_node, _g42_node], ids=["g30", "g42"])
def test_validate_optical_circuit_is_noop_for_g30_and_g42(node_factory: Any) -> None:
    assert hal_spectrum.validate_optical_circuit(node_factory(), _SECTION, "spec", _PASSBAND, _CARRIER, "label") is None


@pytest.mark.parametrize("node_factory", [_g30_node, _g42_node], ids=["g30", "g42"])
@pytest.mark.parametrize(
    "call",
    [
        pytest.param(
            lambda node: hal_spectrum.create_optical_cross_connection(node, _port(node), _port(node), _PASSBAND),
            id="create_optical_cross_connection",
        ),
        pytest.param(
            lambda node: hal_spectrum.delete_optical_cross_connection(node, _port(node), _port(node), _PASSBAND),
            id="delete_optical_cross_connection",
        ),
    ],
)
def test_cross_connections_are_not_implemented_for_g30_and_g42(node_factory: Any, call: Any) -> None:
    with pytest.raises(NotImplementedError):
        call(node_factory())


@pytest.mark.parametrize("node_factory", [_g30_node, _g42_node], ids=["g30", "g42"])
def test_delta_rx_power_is_not_implemented_for_g30_and_g42(node_factory: Any) -> None:
    with pytest.raises(NotImplementedError):
        hal_transport.delta_rx_power_vs_target(node_factory(), "spec")


# ---------------------------------------------------------------------------
# Device-bound branches: assert the dispatch reaches the adapter seam
# ---------------------------------------------------------------------------


def test_get_optical_node_client_dispatches_per_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    flex_client, g30_client, g42_client = object(), object(), object()
    flex = _patch(monkeypatch, hal_node, "get_flex_client", flex_client)
    g30 = _patch(monkeypatch, hal_node, "get_g30_client", g30_client)
    g42 = _patch(monkeypatch, hal_node, "get_g42_client", g42_client)
    flexils_block, g30_block, g42_block = _flexils_node(), _g30_node(), _g42_node()

    assert hal_node.get_optical_node_client(flexils_block) is flex_client
    assert hal_node.get_optical_node_client(g30_block) is g30_client
    assert hal_node.get_optical_node_client(g42_block) is g42_client
    assert flex.calls == [((flexils_block,), {})]
    assert g30.calls == [((g30_block,), {})]
    assert g42.calls == [((g42_block,), {})]


def test_retrieve_software_version_dispatches_per_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_node, "software_version", "flex-1")
    g30 = _patch(monkeypatch, g30_node, "software_version", "g30-1")
    g42 = _patch(monkeypatch, g42_node, "software_version", "g42-1")
    flexils_block, g30_block, g42_block = _flexils_node(), _g30_node(), _g42_node()

    assert hal_node.retrieve_software_version(flexils_block) == "flex-1"
    assert hal_node.retrieve_software_version(g30_block) == "g30-1"
    assert hal_node.retrieve_software_version(g42_block) == "g42-1"
    assert flex.calls == [((flexils_block,), {})]
    assert g30.calls == [((g30_block,), {})]
    assert g42.calls == [((g42_block,), {})]


def test_retrieve_role_and_version_dispatches_per_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    role = OpticalNodeRole.ROADM
    flex = _patch(monkeypatch, flexils_node, "role_and_version", (role, "flex-1"))
    g30_role = _patch(monkeypatch, g30_node, "role", role)
    g30_version = _patch(monkeypatch, g30_node, "software_version", "g30-1")
    g42_role = _patch(monkeypatch, g42_node, "role", role)
    g42_version = _patch(monkeypatch, g42_node, "software_version", "g42-1")
    flexils_block, g30_block, g42_block = _flexils_node(), _g30_node(), _g42_node()

    assert hal_node.retrieve_optical_node_role_and_software_version(flexils_block) == (role, "flex-1")
    assert hal_node.retrieve_optical_node_role_and_software_version(g30_block) == (role, "g30-1")
    assert hal_node.retrieve_optical_node_role_and_software_version(g42_block) == (role, "g42-1")
    assert flex.calls == [((flexils_block,), {})]
    assert g30_role.calls == [((g30_block,), {})]
    assert g30_version.calls == [((g30_block,), {})]
    assert g42_role.calls == [((g42_block,), {})]
    assert g42_version.calls == [((g42_block,), {})]


def test_retrieve_omses_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_node, "retrieve_omses", [{"local_port": "1"}])
    block = _flexils_node()

    assert hal_node.retrieve_omses_terminating_on_device(block) == [{"local_port": "1"}]
    assert recorder.calls == [((block,), {})]


def test_retrieve_ports_spectral_occupations_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_node, "retrieve_ports_spectral_occupations", {"port-1": [(1, 2)]})
    block = _flexils_node()

    assert hal_node.retrieve_ports_spectral_occupations(block) == {"port-1": [(1, 2)]}
    assert recorder.calls == [((block,), {})]


def test_validate_management_network_config_dispatches_to_g30(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, g30_node, "validate_management_network_config")
    block = _g30_node()

    assert hal_node.validate_management_network_config(block) is None
    assert recorder.calls == [((block,), {})]


def test_get_device_ports_by_role_dispatches_per_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_port, "get_device_ports_by_role", ["flex-port"])
    g30 = _patch(monkeypatch, g30_port, "get_device_ports_by_role", ["g30-port"])
    g42 = _patch(monkeypatch, g42_port, "get_device_ports_by_role", ["g42-port"])
    flexils_block, g30_block, g42_block = _flexils_node(), _g30_node(), _g42_node()
    roles = [OpticalPortRole.OLS_LINE]

    assert hal_port.get_device_ports_by_role(flexils_block, roles) == ["flex-port"]
    assert hal_port.get_device_ports_by_role(g30_block, roles) == ["g30-port"]
    assert hal_port.get_device_ports_by_role(g42_block, roles) == ["g42-port"]
    assert flex.calls == [((flexils_block, roles), {})]
    assert g30.calls == [((g30_block, roles), {})]
    assert g42.calls == [((g42_block, roles), {})]


def test_retrieve_transceiver_modes_dispatches_to_g30_and_g42(monkeypatch: pytest.MonkeyPatch) -> None:
    g30 = _patch(monkeypatch, g30_port, "retrieve_transceiver_modes", ["mode-a"])
    g42 = _patch(monkeypatch, g42_port, "retrieve_transceiver_modes", ["mode-b"])
    g30_block, g42_block = _g30_node(), _g42_node()

    assert hal_port.retrieve_transceiver_modes(g30_block, "port-1") == ["mode-a"]
    assert hal_port.retrieve_transceiver_modes(g42_block, "port-1") == ["mode-b"]
    assert g30.calls == [((g30_block, "port-1"), {})]
    assert g42.calls == [((g42_block, "port-1"), {})]


def test_set_port_description_dispatches_per_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_port, "set_port_description", {"flex": True})
    g30 = _patch(monkeypatch, g30_port, "set_port_description", {"g30": True})
    g42 = _patch(monkeypatch, g42_port, "set_port_description", {"g42": True})
    flex_port, g30_port_block, g42_port_block = _port(_flexils_node()), _port(_g30_node()), _port(_g42_node())

    assert hal_port.set_port_description(flex_port, "desc") == {"flex": True}
    assert hal_port.set_port_description(g30_port_block, "desc") == {"g30": True}
    assert hal_port.set_port_description(g42_port_block, "desc") == {"g42": True}
    assert flex.calls == [((flex_port, "desc"), {})]
    assert g30.calls == [((g30_port_block, "desc"), {})]
    assert g42.calls == [((g42_port_block, "desc"), {})]


def test_set_channel_description_dispatches_to_g30_and_g42(monkeypatch: pytest.MonkeyPatch) -> None:
    g30 = _patch(monkeypatch, g30_port, "set_channel_description", {"g30": True})
    g42 = _patch(monkeypatch, g42_port, "set_channel_description", {"g42": True})
    g30_block, g42_block = _g30_node(), _g42_node()

    assert hal_port.set_channel_description(g30_block, "1/1/1", "desc") == {"g30": True}
    assert hal_port.set_channel_description(g42_block, "1/1/1", "desc") == {"g42": True}
    assert g30.calls == [((g30_block, "1/1/1", "desc"), {})]
    assert g42.calls == [((g42_block, "1/1/1", "desc"), {})]


def test_set_port_admin_state_dispatches_per_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_port, "set_port_admin_state", {"flex": True})
    g30 = _patch(monkeypatch, g30_port, "set_port_admin_state", {"g30": True})
    g42 = _patch(monkeypatch, g42_port, "set_port_admin_state", {"g42": True})
    flex_port, g30_port_block, g42_port_block = _port(_flexils_node()), _port(_g30_node()), _port(_g42_node())

    assert hal_port.set_port_admin_state(flex_port, "up") == {"flex": True}
    assert hal_port.set_port_admin_state(g30_port_block, "up") == {"g30": True}
    assert hal_port.set_port_admin_state(g42_port_block, "up") == {"g42": True}
    assert flex.calls == [((flex_port, "up"), {})]
    assert g30.calls == [((g30_port_block, "up"), {})]
    assert g42.calls == [((g42_port_block, "up"), {})]


def test_configure_termination_dispatches_per_vendor_and_forwards_pipe_type(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_port, "configure_termination", {"flex": True})
    g30 = _patch(monkeypatch, g30_port, "configure_termination", {"g30": True})
    g42 = _patch(monkeypatch, g42_port, "configure_termination", {"g42": True})
    flex_local, flex_remote = _port(_flexils_node()), _port(_flexils_node())
    g30_local, g30_remote = _port(_g30_node()), _port(_g30_node())
    g42_local, g42_remote = _port(_g42_node()), _port(_g42_node())

    assert hal_port.configure_termination_when_attaching_new_fiber(flex_local, flex_remote, OpticalPipeType.SPAN) == {
        "flex": True
    }
    assert hal_port.configure_termination_when_attaching_new_fiber(g30_local, g30_remote, OpticalPipeType.SPAN) == {
        "g30": True
    }
    assert hal_port.configure_termination_when_attaching_new_fiber(g42_local, g42_remote, OpticalPipeType.SPAN) == {
        "g42": True
    }
    assert flex.calls == [((flex_local, flex_remote, OpticalPipeType.SPAN), {})]
    assert g30.calls == [((g30_local, g30_remote), {})]
    assert g42.calls == [((g42_local, g42_remote), {})]


def test_factory_reset_dispatches_per_vendor_and_forwards_pipe_type(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_port, "factory_reset", {"flex": True})
    g30 = _patch(monkeypatch, g30_port, "factory_reset", {"g30": True})
    g42 = _patch(monkeypatch, g42_port, "factory_reset", {"g42": True})
    flex_local, flex_remote = _port(_flexils_node()), _port(_flexils_node())
    g30_local, g30_remote = _port(_g30_node()), _port(_g30_node())
    g42_local, g42_remote = _port(_g42_node()), _port(_g42_node())

    assert hal_port.factory_reset_port_configuration(flex_local, flex_remote, OpticalPipeType.SPAN) == {"flex": True}
    assert hal_port.factory_reset_port_configuration(g30_local, g30_remote, OpticalPipeType.SPAN) == {"g30": True}
    assert hal_port.factory_reset_port_configuration(g42_local, g42_remote, OpticalPipeType.SPAN) == {"g42": True}
    assert flex.calls == [((flex_local, flex_remote, OpticalPipeType.SPAN), {})]
    assert g30.calls == [((g30_local,), {})]
    assert g42.calls == [((g42_local,), {})]


def test_check_fiber_dispatches_per_vendor_and_forwards_pipe_type(monkeypatch: pytest.MonkeyPatch) -> None:
    flex = _patch(monkeypatch, flexils_port, "check_fiber")
    g30 = _patch(monkeypatch, g30_port, "check_fiber")
    g42 = _patch(monkeypatch, g42_port, "check_fiber")
    flex_local, flex_remote = _port(_flexils_node()), _port(_flexils_node())
    g30_local, g30_remote = _port(_g30_node()), _port(_g30_node())
    g42_local, g42_remote = _port(_g42_node()), _port(_g42_node())

    assert hal_port.check_fiber_terminating_port(flex_local, flex_remote, OpticalPipeType.SPAN) is None
    assert hal_port.check_fiber_terminating_port(g30_local, g30_remote, OpticalPipeType.SPAN) is None
    assert hal_port.check_fiber_terminating_port(g42_local, g42_remote, OpticalPipeType.SPAN) is None
    assert flex.calls == [((flex_local, flex_remote, OpticalPipeType.SPAN), {})]
    assert g30.calls == [((g30_local, g30_remote), {})]
    assert g42.calls == [((g42_local, g42_remote), {})]


def test_ensure_optical_circuit_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_spectrum, "ensure", {"ensured": True})
    block = _flexils_node()

    result = hal_spectrum.ensure_optical_circuit(block, _SECTION, "spec", _PASSBAND, _CARRIER, "label", "cid")

    assert result == {"ensured": True}
    assert recorder.calls == [((block, _SECTION, "spec", _PASSBAND, _CARRIER, "label", "cid"), {})]


def test_delete_optical_circuit_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_spectrum, "delete", {"deleted": True})
    block = _flexils_node()

    result = hal_spectrum.delete_optical_circuit(block, _SECTION, "spec", _PASSBAND, "cid")

    assert result == {"deleted": True}
    assert recorder.calls == [((block, _SECTION, "spec", _PASSBAND, "cid"), {})]


def test_validate_optical_circuit_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_spectrum, "validate")
    block = _flexils_node()

    assert hal_spectrum.validate_optical_circuit(block, _SECTION, "spec", _PASSBAND, _CARRIER, "label", "cid") is None
    assert recorder.calls == [((block, _SECTION, "spec", _PASSBAND, _CARRIER, "label", "cid"), {})]


def test_set_optical_circuit_label_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_spectrum, "set_label", {"labelled": True})
    block = _flexils_node()

    result = hal_spectrum.set_optical_circuit_label(block, _SECTION, "spec", _PASSBAND, "label", "cid")

    assert result == {"labelled": True}
    assert recorder.calls == [((block, _SECTION, "spec", _PASSBAND, "label", "cid"), {})]


def test_create_optical_cross_connection_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_spectrum, "create_cross_connection", {"created": True})
    block = _flexils_node()
    from_port, to_port = _port(block), _port(block)

    result = hal_spectrum.create_optical_cross_connection(block, from_port, to_port, _PASSBAND)

    assert result == {"created": True}
    assert recorder.calls == [((block, from_port, to_port, _PASSBAND, None, None, None, ""), {})]


def test_delete_optical_cross_connection_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_spectrum, "delete_cross_connection", {"deleted": True})
    block = _flexils_node()
    from_port, to_port = _port(block), _port(block)

    result = hal_spectrum.delete_optical_cross_connection(block, from_port, to_port, _PASSBAND)

    assert result == {"deleted": True}
    assert recorder.calls == [((block, from_port, to_port, _PASSBAND, None, None, None, ""), {})]


_TRANSPORT_G30_G42_DISPATCH = [
    pytest.param(hal_transport.get_signal_bandwidth, "get_signal_bandwidth", ("port-1",), id="get_signal_bandwidth"),
    pytest.param(
        hal_transport.configure_line_transceivers,
        "configure_line_transceivers",
        (("port-1",), _FREQUENCIES, ("mode",), ("desc",)),
        id="configure_line_transceivers",
    ),
    pytest.param(
        hal_transport.configure_transceiver_client,
        "configure_transceiver_client",
        ("port-1", "desc", _SPEED),
        id="configure_transceiver_client",
    ),
    pytest.param(
        hal_transport.configure_transponder_crossconnect,
        "configure_transponder_crossconnect",
        ("port-1", ["port-2"], ""),
        id="configure_transponder_crossconnect",
    ),
    pytest.param(
        hal_transport.delete_transponder_crossconnect,
        "delete_transponder_crossconnect",
        ("port-1",),
        id="delete_transponder_crossconnect",
    ),
    pytest.param(
        hal_transport.factory_reset_transponder_client,
        "factory_reset_transponder_client",
        ("port-1",),
        id="factory_reset_transponder_client",
    ),
    pytest.param(
        hal_transport.factory_reset_transponder_lines,
        "factory_reset_transponder_lines",
        (["port-1"],),
        id="factory_reset_transponder_lines",
    ),
    pytest.param(
        hal_transport.validate_trx_line,
        "validate_trx_line",
        (("port-1",), _FREQUENCIES, ("mode",), ("desc",)),
        id="validate_trx_line",
    ),
    pytest.param(
        hal_transport.validate_trx_client,
        "validate_trx_client",
        ("port-1", "desc", _SPEED),
        id="validate_trx_client",
    ),
    pytest.param(
        hal_transport.validate_trx_crossconnect,
        "validate_trx_crossconnect",
        ("port-1", ["port-2"], ""),
        id="validate_trx_crossconnect",
    ),
    pytest.param(
        hal_transport.align_tx_power_to_target,
        "align_tx_power_to_target",
        ("port-1", Decimal("0.5")),
        id="align_tx_power_to_target",
    ),
]


@pytest.mark.parametrize(("hal_func", "adapter_name", "args"), _TRANSPORT_G30_G42_DISPATCH)
def test_transport_dispatches_to_g30_and_g42(
    monkeypatch: pytest.MonkeyPatch, hal_func: Any, adapter_name: str, args: tuple[Any, ...]
) -> None:
    g30 = _patch(monkeypatch, g30_transponder, adapter_name, "g30-result")
    g42 = _patch(monkeypatch, g42_transponder, adapter_name, "g42-result")
    g30_block, g42_block = _g30_node(), _g42_node()

    assert hal_func(g30_block, *args) == "g30-result"
    assert hal_func(g42_block, *args) == "g42-result"
    assert g30.calls == [((g30_block, *args), {})]
    assert g42.calls == [((g42_block, *args), {})]


def test_delta_rx_power_dispatches_to_flexils(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _patch(monkeypatch, flexils_transponder, "delta_rx_power_vs_target", 1.5)
    block = _flexils_node()

    assert hal_transport.delta_rx_power_vs_target(block, "spec", "cid") == 1.5
    assert recorder.calls == [((block, "spec", "cid"), {})]


_TRANSPORT_FLEXILS_NOT_IMPLEMENTED = [
    pytest.param(hal_transport.get_signal_bandwidth, ("port-1",), id="get_signal_bandwidth"),
    pytest.param(
        hal_transport.configure_line_transceivers,
        (("port-1",), _FREQUENCIES, ("mode",), ("desc",)),
        id="configure_line_transceivers",
    ),
    pytest.param(
        hal_transport.configure_transceiver_client, ("port-1", "desc", _SPEED), id="configure_transceiver_client"
    ),
    pytest.param(
        hal_transport.configure_transponder_crossconnect,
        ("port-1", ["port-2"]),
        id="configure_transponder_crossconnect",
    ),
    pytest.param(hal_transport.delete_transponder_crossconnect, ("port-1",), id="delete_transponder_crossconnect"),
    pytest.param(hal_transport.factory_reset_transponder_client, ("port-1",), id="factory_reset_transponder_client"),
    pytest.param(hal_transport.factory_reset_transponder_lines, (["port-1"],), id="factory_reset_transponder_lines"),
    pytest.param(
        hal_transport.validate_trx_line, (("port-1",), _FREQUENCIES, ("mode",), ("desc",)), id="validate_trx_line"
    ),
    pytest.param(hal_transport.validate_trx_client, ("port-1", "desc", _SPEED), id="validate_trx_client"),
    pytest.param(hal_transport.validate_trx_crossconnect, ("port-1", ["port-2"]), id="validate_trx_crossconnect"),
    pytest.param(hal_transport.align_tx_power_to_target, ("port-1", Decimal("0.5")), id="align_tx_power_to_target"),
]


@pytest.mark.parametrize(("hal_func", "args"), _TRANSPORT_FLEXILS_NOT_IMPLEMENTED)
def test_transport_flexils_branches_are_not_implemented(hal_func: Any, args: tuple[Any, ...]) -> None:
    with pytest.raises(NotImplementedError):
        hal_func(_flexils_node(), *args)
