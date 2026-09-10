"""Contract tests for the Nokia GX G42 RESTCONF adapter.

The G42 client/navigator tree is faked with ``SimpleNamespace``/``_Nav`` objects and
the adapter's ``get_g42_client`` factory is monkeypatched, so no device is contacted.
Pure helpers are exercised directly; navigator-reading functions assert the value
they return and the RESTCONF operation they issue on the fake endpoint.
"""

from __future__ import annotations

import copy
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from requests.exceptions import HTTPError

from orchestrator.optical.hal._common import UnsupportedPortRoleError
from orchestrator.optical.hal.adapters.nokia_gx_g42 import _shared as g42_shared
from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as g42_node
from orchestrator.optical.hal.adapters.nokia_gx_g42 import port as g42_port
from orchestrator.optical.hal.adapters.nokia_gx_g42 import transponder as g42_transponder
from orchestrator.optical.hal.adapters.nokia_gx_g42.transponder import (
    _client_speed_config,
    _derive_optical_channel_key,
    _find_xcon,
    _retrieve_payload_type,
    _retrieve_time_slots,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.services.nokia.g42.data_models.ioa_network_element import (
    AdminStateEnum,
    ExternalConnectivityEnum,
    PortTypeEnum,
    ServiceTypeEnum,
)


class _Model(SimpleNamespace):
    """Minimal stand-in for a pydantic model, exposing only what the adapters call."""

    def model_copy(self, *, deep: bool = False) -> _Model:
        clone = _Model()
        clone.__dict__.update(copy.deepcopy(self.__dict__) if deep else self.__dict__)
        return clone

    def model_dump(self, **_: Any) -> dict[str, Any]:
        return dict(self.__dict__)


class _Nav(SimpleNamespace):
    """Callable navigator node: exposes attributes and returns ``child`` when called."""

    def __init__(self, child: Any = None, **attrs: Any) -> None:
        super().__init__(child=child, **attrs)

    def __call__(self, *_: Any, **__: Any) -> Any:
        return self.child


class _Endpoint(SimpleNamespace):
    """Fake RESTCONF endpoint that records the update/delete calls issued on it."""

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, update_calls=[], delete_calls=0)

    def retrieve(self, **_: Any) -> Any:
        return self.model

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.update_calls.append((args, kwargs))
        if args:
            self.model = args[0]
        else:
            updated = self.model.model_copy()
            for key, value in kwargs.items():
                setattr(updated, key, value)
            self.model = updated

    def delete(self) -> None:
        self.delete_calls += 1


def _patch_g42_client(monkeypatch: pytest.MonkeyPatch, client: Any) -> None:
    """Patch ``get_g42_client`` everywhere the adapter modules bound it by name."""
    for module in (g42_shared, g42_node, g42_port, g42_transponder):
        monkeypatch.setattr(module, "get_g42_client", lambda *_: client)


def _node_block(fqdn: str | None = None) -> Any:
    return SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn=fqdn))


def _port_block(port_name: str, host_node: Any | None = None) -> Any:
    return SimpleNamespace(optical_port_name=port_name, optical_port_host_node=host_node or _node_block())


def _equipment_client(**equipment: Any) -> Any:
    return SimpleNamespace(
        url="https://g42.example.net",
        data=SimpleNamespace(ne=SimpleNamespace(equipment=SimpleNamespace(**equipment))),
    )


def _facilities_client(**facilities: Any) -> Any:
    return SimpleNamespace(
        url="https://g42.example.net",
        data=SimpleNamespace(ne=SimpleNamespace(facilities=SimpleNamespace(**facilities))),
    )


def _services_client(**services: Any) -> Any:
    return SimpleNamespace(
        url="https://g42.example.net",
        data=SimpleNamespace(ne=SimpleNamespace(services=SimpleNamespace(**services))),
    )


# --------------------------------------------------------------------------- pure helpers


@pytest.mark.parametrize(
    ("speed", "expected"),
    [
        (OpticalDigitalServiceSpeed(100), ("gx:QSFP28", "TOM-100G-Q", "100G", "100GBE")),
        (OpticalDigitalServiceSpeed(400), ("gx:QSFPDD", "TOM-400G-Q-DR4", "400GE", "400GBE")),
    ],
)
def test_client_speed_config(speed: OpticalDigitalServiceSpeed, expected: tuple[str, str, str, str]) -> None:
    assert _client_speed_config(speed) == expected


def test_client_speed_config_rejects_unsupported_speed() -> None:
    with pytest.raises(NotImplementedError):
        _client_speed_config(OpticalDigitalServiceSpeed(800))


def test_derive_optical_channel_key_single_line() -> None:
    assert _derive_optical_channel_key(["1-4-L1"]) == "1-4-L1-1"


def test_derive_optical_channel_key_coupled_lines_uses_the_l1_carrier() -> None:
    assert _derive_optical_channel_key(["1-4-L2", "1-4-L1"]) == "1-4-L1-1"


def test_derive_optical_channel_key_rejects_invalid_coupled_lines() -> None:
    with pytest.raises(ValueError, match="Invalid line port names"):
        _derive_optical_channel_key(["1-4-L2", "1-4-L3"])


# --------------------------------------------------------------------------- node


def _chassis_client(chassis_items: list[Any], fw_items: list[Any]) -> Any:
    current_fw = SimpleNamespace(retrieve=lambda **_: fw_items)
    chassis_child = SimpleNamespace(inventory=SimpleNamespace(current_fw=current_fw))
    chassis = _Nav(child=chassis_child, retrieve=lambda **_: chassis_items)
    return _equipment_client(chassis=chassis)


def test_g42_software_version_returns_the_controller_firmware(monkeypatch: pytest.MonkeyPatch) -> None:
    controllers = [
        SimpleNamespace(name="other", is_node_controller=False),
        SimpleNamespace(name="ctrl", is_node_controller=True),
    ]
    _patch_g42_client(monkeypatch, _chassis_client(controllers, [SimpleNamespace(fw_version="22.1")]))
    assert g42_node.software_version(SimpleNamespace()) == "22.1"


def test_g42_software_version_falls_back_to_the_first_chassis(monkeypatch: pytest.MonkeyPatch) -> None:
    chassis = [SimpleNamespace(name="ctrl", is_node_controller=False)]
    _patch_g42_client(monkeypatch, _chassis_client(chassis, [SimpleNamespace(fw_version="22.2")]))
    assert g42_node.software_version(SimpleNamespace()) == "22.2"


def test_g42_software_version_raises_without_a_chassis(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _chassis_client([], []))
    with pytest.raises(ValueError, match="No chassis found"):
        g42_node.software_version(SimpleNamespace())


def test_g42_software_version_raises_without_firmware(monkeypatch: pytest.MonkeyPatch) -> None:
    chassis = [SimpleNamespace(name="ctrl", is_node_controller=True)]
    _patch_g42_client(monkeypatch, _chassis_client(chassis, [SimpleNamespace(fw_version=None)]))
    with pytest.raises(ValueError, match="No current firmware version found"):
        g42_node.software_version(SimpleNamespace())


def test_g42_role_is_always_a_transponder() -> None:
    assert g42_node.role(SimpleNamespace()) is OpticalNodeRole.TRANSPONDER


# --------------------------------------------------------------------------- port


def _card_client(card_model: _Model) -> Any:
    card_child = SimpleNamespace(retrieve=lambda **_: card_model)
    return _equipment_client(card=_Nav(child=card_child))


def test_g42_retrieve_transceiver_modes_returns_the_card_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _card_client(_Model(required_subtype="C6")))
    modes = g42_port.retrieve_transceiver_modes(SimpleNamespace(), "1-4-L1")
    assert "100E.31U" in modes
    assert "800M.95P" in modes


def test_g42_retrieve_transceiver_modes_rejects_unsupported_card(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _card_client(_Model(required_subtype="C99")))
    with pytest.raises(ValueError, match="not supported"):
        g42_port.retrieve_transceiver_modes(SimpleNamespace(), "1-4-L1")


def _chm6_ports_client(cards: list[Any]) -> Any:
    card = _Nav(child=_Nav(), retrieve=lambda **_: cards)
    return _equipment_client(card=card)


def test_g42_get_device_ports_by_role_separates_line_and_client_ports(monkeypatch: pytest.MonkeyPatch) -> None:
    ports = [
        SimpleNamespace(AID="1-4-L1", installed_type="SFP", port_type=PortTypeEnum.LINE),
        SimpleNamespace(AID="1-4-C1", installed_type="QSFP", port_type=PortTypeEnum.TRIBUTARY),
        SimpleNamespace(AID=None, installed_type="QSFP", port_type=PortTypeEnum.TRIBUTARY),
        SimpleNamespace(AID="1-4-C2", installed_type=None, port_type=PortTypeEnum.TRIBUTARY),
    ]
    cards = [SimpleNamespace(required_type="gx:CHM6", port=ports), SimpleNamespace(required_type="gx:OTHER", port=[])]
    _patch_g42_client(monkeypatch, _chm6_ports_client(cards))

    assert g42_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.TRANSPONDER_LINE]) == ["1-4-L1"]
    client_ports = g42_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.TRANSPONDER_CLIENT])
    assert "1-4-C1" in client_ports
    assert "1-4-C2" not in client_ports  # no installed transceiver


def test_g42_get_device_ports_by_role_rejects_ols_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _chm6_ports_client([]))
    with pytest.raises(UnsupportedPortRoleError, match="not supported"):
        g42_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.OLS_LINE])


def _port_endpoint_client(endpoint: Any) -> Any:
    card_child = _Nav(port=lambda *_: endpoint)
    return _equipment_client(card=_Nav(child=card_child))


def test_g42_set_port_admin_state_updates_the_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(_Model(admin_state=AdminStateEnum.LOCK, label="link"))
    _patch_g42_client(monkeypatch, _port_endpoint_client(endpoint))

    diffs = g42_port.set_port_admin_state(_port_block("1-4-L1"), "up")

    assert endpoint.update_calls
    assert endpoint.model.admin_state is AdminStateEnum.UNLOCK
    assert diffs["+++"]["root['admin_state']"] is AdminStateEnum.UNLOCK


def test_g42_factory_reset_prunes_the_port_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(
        _Model(
            admin_state=AdminStateEnum.UNLOCK,
            external_connectivity=ExternalConnectivityEnum.YES,
            connected_to="remote 1-4-L1",
            label="link",
        )
    )
    _patch_g42_client(monkeypatch, _port_endpoint_client(endpoint))

    diffs = g42_port.factory_reset(_port_block("1-4-L1"))

    assert endpoint.update_calls
    assert endpoint.model.external_connectivity is ExternalConnectivityEnum.NO
    assert endpoint.model.connected_to == ""
    assert endpoint.model.admin_state is AdminStateEnum.LOCK
    assert endpoint.model.label == ""
    assert diffs["+++"]  # the reset produced changes


# --------------------------------------------------------------------------- transponder


def _trib_ptp_client(service_type: ServiceTypeEnum | None) -> Any:
    trib_ptp = _Nav(child=_Endpoint(_Model(service_type=service_type)))
    return _facilities_client(trib_ptp=trib_ptp)


@pytest.mark.parametrize(
    ("service_type", "expected"),
    [(ServiceTypeEnum("100GBE"), "100GBE"), (ServiceTypeEnum("400GBE"), "400GBE")],
)
def test_g42_retrieve_payload_type(
    monkeypatch: pytest.MonkeyPatch, service_type: ServiceTypeEnum, expected: str
) -> None:
    _patch_g42_client(monkeypatch, _trib_ptp_client(service_type))
    assert _retrieve_payload_type(g42_shared.get_g42_client(SimpleNamespace()), "1-4-C1") == expected


def test_g42_retrieve_payload_type_rejects_an_invalid_service(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _trib_ptp_client(ServiceTypeEnum("OTU4")))
    with pytest.raises(ValueError, match="Invalid payload type"):
        _retrieve_payload_type(g42_shared.get_g42_client(SimpleNamespace()), "1-4-C1")


def test_g42_retrieve_payload_type_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _trib_ptp_client(None))
    with pytest.raises(ValueError, match="Unable to retrieve payload type"):
        _retrieve_payload_type(g42_shared.get_g42_client(SimpleNamespace()), "1-4-C1")


def _odu_client(available_time_slots: str | None) -> Any:
    odu = _Nav(child=_Endpoint(_Model(available_time_slots=available_time_slots)))
    return _facilities_client(odu=odu)


def test_g42_retrieve_time_slots_100g_uses_the_first_block(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _odu_client("1..80,161..480"))
    assert _retrieve_time_slots(g42_shared.get_g42_client(SimpleNamespace()), "1-4-L1-ODUCni", "100GBE") == "1..80"


def test_g42_retrieve_time_slots_400g_skips_small_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _odu_client("1..80,161..480"))
    assert _retrieve_time_slots(g42_shared.get_g42_client(SimpleNamespace()), "1-4-L1-ODUCni", "400GBE") == "161..480"


def test_g42_retrieve_time_slots_raises_when_insufficient(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _odu_client("1..10"))
    with pytest.raises(ValueError, match="Not enough available time slots"):
        _retrieve_time_slots(g42_shared.get_g42_client(SimpleNamespace()), "1-4-L1-ODUCni", "100GBE")


def test_g42_retrieve_time_slots_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _odu_client(None))
    with pytest.raises(ValueError, match="missing or empty"):
        _retrieve_time_slots(g42_shared.get_g42_client(SimpleNamespace()), "1-4-L1-ODUCni", "100GBE")


def _xcon_client(xcons: list[Any]) -> Any:
    return _services_client(xcon=_Nav(retrieve=lambda **_: xcons))


def test_g42_find_xcon_returns_the_matching_cross_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    match = _Model(
        source="/client",
        destination="/line/1-4-L1",
        payload_type="100GBE",
        direction="two-way",
    )
    _patch_g42_client(monkeypatch, _xcon_client([match]))
    found = _find_xcon(g42_shared.get_g42_client(SimpleNamespace()), "/client", "1-4-L1", "two-way", "100GBE")
    assert found is match


def test_g42_find_xcon_rejects_a_tributary_that_is_already_connected(monkeypatch: pytest.MonkeyPatch) -> None:
    other = _Model(
        source="/client",
        destination="/line/1-4-L2",
        payload_type="400GBE",
        direction="two-way",
    )
    _patch_g42_client(monkeypatch, _xcon_client([other]))
    with pytest.raises(ValueError, match="already cross-connected"):
        _find_xcon(g42_shared.get_g42_client(SimpleNamespace()), "/client", "1-4-L1", "two-way", "100GBE")


def test_g42_find_xcon_returns_none_when_the_device_reports_404(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_404(**_: Any) -> None:
        raise HTTPError(response=SimpleNamespace(status_code=404))

    _patch_g42_client(monkeypatch, _services_client(xcon=_Nav(retrieve=_raise_404)))
    assert _find_xcon(g42_shared.get_g42_client(SimpleNamespace()), "/client", "1-4-L1", "two-way", "100GBE") is None


def _super_channel_client(channels: list[Any]) -> Any:
    return _facilities_client(super_channel=_Nav(retrieve=lambda **_: channels))


def test_g42_get_signal_bandwidth_single_carrier(monkeypatch: pytest.MonkeyPatch) -> None:
    channel = _Model(carriers=["1-4-L1-1"], spectral_bandwidth=75)
    _patch_g42_client(monkeypatch, _super_channel_client([channel]))
    assert g42_transponder.get_signal_bandwidth(SimpleNamespace(), "1-4-L1") == 75_000


def test_g42_get_signal_bandwidth_halves_coupled_carriers(monkeypatch: pytest.MonkeyPatch) -> None:
    channel = _Model(carriers=["1-4-L1-1", "1-4-L2-1"], spectral_bandwidth=75)
    _patch_g42_client(monkeypatch, _super_channel_client([channel]))
    assert g42_transponder.get_signal_bandwidth(SimpleNamespace(), "1-4-L1") == 37_500


def test_g42_get_signal_bandwidth_raises_when_the_channel_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g42_client(monkeypatch, _super_channel_client([]))
    with pytest.raises(ValueError, match="Channel of port"):
        g42_transponder.get_signal_bandwidth(SimpleNamespace(), "1-4-L1")


def _optical_carrier_client(endpoint: _Endpoint) -> Any:
    return _facilities_client(optical_carrier=_Nav(child=endpoint))


def test_g42_align_tx_power_to_target_clamps_at_the_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    carrier = _Endpoint(_Model(tx_power=Decimal("8.00")))
    _patch_g42_client(monkeypatch, _optical_carrier_client(carrier))

    diffs = g42_transponder.align_tx_power_to_target(_node_block(), "1-4-L1", "20.0")

    assert carrier.update_calls
    assert carrier.model.tx_power == Decimal("-6.00")
    assert diffs["+++"]["root['tx_power']"] == Decimal("-6.00")


def test_g42_align_tx_power_to_target_raises_without_a_configured_power(monkeypatch: pytest.MonkeyPatch) -> None:
    carrier = _Endpoint(_Model(tx_power=None))
    _patch_g42_client(monkeypatch, _optical_carrier_client(carrier))

    with pytest.raises(ValueError, match="No transmit power configured"):
        g42_transponder.align_tx_power_to_target(_node_block(), "1-4-L1", "1.0")
