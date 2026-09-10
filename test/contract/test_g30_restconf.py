"""Contract tests for the Nokia Groove G30 RESTCONF adapter.

The G30 client/navigator tree is faked with ``SimpleNamespace`` objects and the
adapter's ``get_g30_client`` factory is monkeypatched, so no device is contacted.
Pure helpers are exercised directly; navigator-reading functions assert the value
they return and the RESTCONF operation they issue on the fake endpoint.
"""

from __future__ import annotations

import copy
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from orchestrator.optical.hal.adapters.nokia_groove_g30 import _shared as g30_shared
from orchestrator.optical.hal.adapters.nokia_groove_g30 import node as g30_node
from orchestrator.optical.hal.adapters.nokia_groove_g30 import port as g30_port
from orchestrator.optical.hal.adapters.nokia_groove_g30 import transponder as g30_transponder
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import g30_ids_from_port_name
from orchestrator.optical.hal.adapters.nokia_groove_g30.node import _get_eth1_details
from orchestrator.optical.hal.adapters.nokia_groove_g30.port import _g30_aid_id, _g30_port_role
from orchestrator.optical.hal.adapters.nokia_groove_g30.transponder import (
    _client_speed_config,
    _extract_shelf_slot_port_ids_from_odu_string,
    _get_modulation_and_rate_from_mode,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.services.nokia.g30.data_models.ne import (
    AdminStatusEnum,
    CardTypeEnum,
    PortModeEnum,
    SwloadStateEnum,
    YesNoEnum,
)


class _Model(SimpleNamespace):
    """Minimal stand-in for a pydantic model, exposing only what the adapters call."""

    def model_copy(self, *, deep: bool = False) -> _Model:
        clone = _Model()
        clone.__dict__.update(copy.deepcopy(self.__dict__) if deep else self.__dict__)
        return clone

    def model_dump(self, **_: Any) -> dict[str, Any]:
        return dict(self.__dict__)


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


def _patch_g30_client(monkeypatch: pytest.MonkeyPatch, client: Any) -> None:
    """Patch ``get_g30_client`` everywhere the adapter modules bound it by name."""
    for module in (g30_shared, g30_node, g30_port, g30_transponder):
        monkeypatch.setattr(module, "get_g30_client", lambda *_: client)


def _node_block(fqdn: str | None = None, vendor: Vendor | None = None, platform: Platform | None = None) -> Any:
    return SimpleNamespace(
        management=SimpleNamespace(
            optical_module_node_fqdn=fqdn,
            optical_module_node_vendor=vendor,
            optical_module_node_platform=platform,
        )
    )


def _port_block(port_name: str, host_node: Any | None = None) -> Any:
    return SimpleNamespace(optical_port_name=port_name, optical_port_host_node=host_node or _node_block())


def _port_endpoint_client(endpoint: Any) -> Any:
    """Fake client whose ``shelf(s).slot(sl).card.port(p)`` chain yields ``endpoint``."""
    return SimpleNamespace(
        url="https://g30.example.net",
        data=SimpleNamespace(
            ne_ne=SimpleNamespace(
                shelf=lambda *_: SimpleNamespace(
                    slot=lambda *_: SimpleNamespace(card=SimpleNamespace(port=lambda *_: endpoint))
                )
            )
        ),
    )


# --------------------------------------------------------------------------- pure helpers


@pytest.mark.parametrize(
    ("port_name", "expected"),
    [
        ("port-1/2/3", (1, 2, None, 3, None)),
        ("port-1/3.1/1.4", (1, 3, 1, 1, 4)),
        ("subport-1/3.1/3", (1, 3, 1, 3, None)),
    ],
)
def test_g30_ids_from_port_name(port_name: str, expected: tuple[int, int, int | None, int, int | None]) -> None:
    assert g30_ids_from_port_name(port_name) == expected


def test_g30_ids_from_port_name_rejects_subport_without_subslot() -> None:
    with pytest.raises(ValueError, match="Subport ID is not supported without subslot ID"):
        g30_ids_from_port_name("port-1/2/3.4")


def test_g30_aid_id_strips_the_port_prefix() -> None:
    assert _g30_aid_id("port-1/3.3/1") == "1/3.3/1"


def test_g30_port_role_occ2_with_matching_ots_is_ols_line() -> None:
    role = _g30_port_role(is_occ2=True, is_card_port=True, port_id=1, port_name="port-1/3.3/1", ots_ids={"1/3.3/1"})
    assert role is OpticalPortRole.OLS_LINE


def test_g30_port_role_occ2_without_matching_ots_is_ols_add_drop() -> None:
    role = _g30_port_role(is_occ2=True, is_card_port=False, port_id=3, port_name="subport-1/3.1/3", ots_ids={"1/3.3/1"})
    assert role is OpticalPortRole.OLS_ADD_DROP


@pytest.mark.parametrize("port_id", [1, 2])
def test_g30_port_role_non_occ2_card_ports_1_and_2_are_transponder_line(port_id: int) -> None:
    role = _g30_port_role(
        is_occ2=False, is_card_port=True, port_id=port_id, port_name=f"port-1/2/{port_id}", ots_ids=set()
    )
    assert role is OpticalPortRole.TRANSPONDER_LINE


def test_g30_port_role_non_occ2_other_ports_are_transponder_client() -> None:
    role = _g30_port_role(is_occ2=False, is_card_port=True, port_id=3, port_name="port-1/2/3", ots_ids=set())
    assert role is OpticalPortRole.TRANSPONDER_CLIENT


def test_get_eth1_details_without_ip() -> None:
    assert _get_eth1_details(None) == (None, None, False, 0)


@pytest.mark.parametrize(
    ("eth1_ip", "expected"),
    [
        ("10.127.5.10", ("eth1", "10.127.5.1", True, 24)),
        ("172.16.5.10", ("eth1", "172.16.5.1", True, 24)),
        ("10.10.5.10", ("eth1", "10.10.5.9", False, 30)),
    ],
)
def test_get_eth1_details_derives_gateway_and_prefix(eth1_ip: str, expected: tuple[str, str, bool, int]) -> None:
    assert _get_eth1_details(eth1_ip) == expected


def test_get_eth1_details_rejects_out_of_range_ip() -> None:
    with pytest.raises(ValueError, match="Invalid management IP"):
        _get_eth1_details("192.168.1.1")


@pytest.mark.parametrize(
    ("speed", "expected"),
    [
        (OpticalDigitalServiceSpeed(100), ("100GBE", "eth100g", "auto")),
        (OpticalDigitalServiceSpeed(400), ("400GBE", "eth400g", "enabled")),
    ],
)
def test_client_speed_config(speed: OpticalDigitalServiceSpeed, expected: tuple[str, str, str]) -> None:
    assert _client_speed_config(speed) == expected


def test_client_speed_config_rejects_unsupported_speed() -> None:
    with pytest.raises(NotImplementedError):
        _client_speed_config(OpticalDigitalServiceSpeed(800))


@pytest.mark.parametrize(
    ("port_mode", "expected"),
    [
        ("QPSK_100G", ("DP-QPSK", "100G")),
        ("16QAM_400G", ("DP-16QAM", "400G")),
        ("SP16QAM_300G_C", ("DP-SP16QAM", "150G")),
        ("not-applicable", ("not-applicable", "not-applicable")),
        ("unknown-mode", ("not-applicable", "not-applicable")),
    ],
)
def test_get_modulation_and_rate_from_mode(port_mode: str, expected: tuple[str, str]) -> None:
    assert _get_modulation_and_rate_from_mode(port_mode) == expected


def test_extract_shelf_slot_port_ids_from_odu_string() -> None:
    odu = "/ne:ne/shelf[shelf-id='1']/slot[slot-id='4']/card/port[port-id='3']/eth100g/odu[odutype-L1='odu4']"
    assert _extract_shelf_slot_port_ids_from_odu_string(odu) == (1, 4, 3)


def test_extract_shelf_slot_port_ids_from_odu_string_rejects_garbage() -> None:
    with pytest.raises(ValueError, match="Could not extract the shelf, slot and port ids"):
        _extract_shelf_slot_port_ids_from_odu_string("not-an-odu-string")


# --------------------------------------------------------------------------- node


def _software_client(items: list[Any]) -> Any:
    return SimpleNamespace(
        url="https://g30.example.net",
        data=SimpleNamespace(
            ne_ne=SimpleNamespace(
                system=SimpleNamespace(
                    sw_management=SimpleNamespace(softwareload=SimpleNamespace(retrieve=lambda **_: items))
                )
            )
        ),
    )


def test_g30_software_version_returns_the_active_load(monkeypatch: pytest.MonkeyPatch) -> None:
    items = [
        SimpleNamespace(swload_state=SwloadStateEnum.INACTIVE, swload_version="21.0"),
        SimpleNamespace(swload_state=SwloadStateEnum.ACTIVE, swload_version="22.1"),
    ]
    _patch_g30_client(monkeypatch, _software_client(items))
    assert g30_node.software_version(SimpleNamespace()) == "22.1"


def test_g30_software_version_raises_without_an_active_load(monkeypatch: pytest.MonkeyPatch) -> None:
    items = [SimpleNamespace(swload_state=SwloadStateEnum.INACTIVE, swload_version="21.0")]
    _patch_g30_client(monkeypatch, _software_client(items))
    with pytest.raises(ValueError, match="No current firmware version found"):
        g30_node.software_version(SimpleNamespace())


def _inventory_client(module_types: list[str]) -> Any:
    inventory = [SimpleNamespace(module_type=module_type) for module_type in module_types]
    return SimpleNamespace(
        url="https://g30.example.net",
        data=SimpleNamespace(
            ne_ne=SimpleNamespace(
                inventory_data=SimpleNamespace(inventory=SimpleNamespace(retrieve=lambda **_: inventory))
            )
        ),
    )


def test_g30_role_with_occ2_inventory_is_transponder_xoadm(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g30_client(monkeypatch, _inventory_client(["CHM2", "OCC2"]))
    assert g30_node.role(SimpleNamespace()) is OpticalNodeRole.TRANSPONDER_XOADM


def test_g30_role_without_occ2_is_transponder(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g30_client(monkeypatch, _inventory_client(["CHM2", "CHM1"]))
    assert g30_node.role(SimpleNamespace()) is OpticalNodeRole.TRANSPONDER


# --------------------------------------------------------------------------- port


def _card_client(card_type: CardTypeEnum) -> Any:
    card = SimpleNamespace(required_type=card_type)
    return SimpleNamespace(
        url="https://g30.example.net",
        data=SimpleNamespace(
            ne_ne=SimpleNamespace(
                shelf=lambda *_: SimpleNamespace(
                    slot=lambda *_: SimpleNamespace(card=SimpleNamespace(retrieve=lambda **_: card))
                )
            )
        ),
    )


def test_g30_retrieve_transceiver_modes_returns_the_card_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g30_client(monkeypatch, _card_client(CardTypeEnum.CHM2T))
    modes = g30_port.retrieve_transceiver_modes(SimpleNamespace(), "port-1/2/1")
    assert "16QAM_200G" in modes
    assert "not-applicable" in modes


def test_g30_retrieve_transceiver_modes_rejects_unsupported_card(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_g30_client(monkeypatch, _card_client(CardTypeEnum.OCC2))
    with pytest.raises(ValueError, match="not supported"):
        g30_port.retrieve_transceiver_modes(SimpleNamespace(), "port-1/2/1")


def test_g30_set_port_admin_state_updates_the_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(_Model(admin_status=AdminStatusEnum.DOWN, service_label="link"))
    _patch_g30_client(monkeypatch, _port_endpoint_client(endpoint))

    diffs = g30_port.set_port_admin_state(_port_block("port-1/2/3"), "up")

    assert endpoint.update_calls
    assert endpoint.model.admin_status is AdminStatusEnum.UP
    assert diffs["+++"]["root['admin_status']"] is AdminStatusEnum.UP


def test_g30_factory_reset_prunes_the_port_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(
        _Model(
            admin_status=AdminStatusEnum.UP,
            external_connectivity=YesNoEnum.YES,
            connected_to="remote 1/2/3",
            port_mode=PortModeEnum("100GBE"),
            service_label="link",
        )
    )
    _patch_g30_client(monkeypatch, _port_endpoint_client(endpoint))

    diffs = g30_port.factory_reset(_port_block("port-1/2/3"))

    assert endpoint.update_calls
    assert endpoint.model.external_connectivity is YesNoEnum.NO
    assert endpoint.model.connected_to == ""
    assert endpoint.model.admin_status is AdminStatusEnum.DOWN
    assert endpoint.model.port_mode is PortModeEnum.NOT_APPLICABLE
    assert diffs["+++"]  # the reset produced changes


def test_g30_configure_termination_to_a_flexils_node_sets_external_connectivity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    endpoint = _Endpoint(_Model(external_connectivity=YesNoEnum.NO, connected_to="", admin_status=AdminStatusEnum.DOWN))
    _patch_g30_client(monkeypatch, _port_endpoint_client(endpoint))
    host = _node_block("local.example.net", Vendor.NOKIA, Platform.GROOVE_G30)
    remote = _node_block("remote.example.net", Vendor.NOKIA, Platform.FLEXILS)

    diffs = g30_port.configure_termination(
        _port_block("port-1/2/1", host),
        _port_block("port-9/9/9", remote),
    )

    assert endpoint.model.external_connectivity is YesNoEnum.YES
    assert endpoint.model.connected_to == "remote.example.net port-9/9/9"
    assert diffs["+++"]  # the update produced changes


def test_g30_check_fiber_passes_when_the_port_is_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(
        _Model(
            admin_status=AdminStatusEnum.UP,
            external_connectivity=YesNoEnum.YES,
            connected_to="remote.example.net port-9/9/9",
        )
    )
    _patch_g30_client(monkeypatch, _port_endpoint_client(endpoint))
    host = _node_block("local.example.net", Vendor.NOKIA, Platform.GROOVE_G30)
    remote = _node_block("remote.example.net", Vendor.NOKIA, Platform.FLEXILS)

    g30_port.check_fiber(_port_block("port-1/2/1", host), _port_block("port-9/9/9", remote))


def test_g30_check_fiber_raises_when_the_port_is_misconfigured(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(
        _Model(
            admin_status=AdminStatusEnum.DOWN,
            external_connectivity=YesNoEnum.NO,
            connected_to="",
        )
    )
    _patch_g30_client(monkeypatch, _port_endpoint_client(endpoint))
    host = _node_block("local.example.net", Vendor.NOKIA, Platform.GROOVE_G30)
    remote = _node_block("remote.example.net", Vendor.NOKIA, Platform.FLEXILS)

    with pytest.raises(ValueError, match="port-1/2/1"):
        g30_port.check_fiber(_port_block("port-1/2/1", host), _port_block("port-9/9/9", remote))


# --------------------------------------------------------------------------- transponder


def _och_os_client(och_os: _Endpoint) -> Any:
    port_node = SimpleNamespace(och_os=och_os)
    return SimpleNamespace(
        url="https://g30.example.net",
        data=SimpleNamespace(
            ne_ne=SimpleNamespace(
                shelf=lambda *_: SimpleNamespace(
                    slot=lambda *_: SimpleNamespace(card=SimpleNamespace(port=lambda *_: port_node))
                )
            )
        ),
    )


@pytest.mark.parametrize(
    ("fec_type", "expected"),
    [("SDFEC27ND", 75_000), ("SDFEC15ND2", 68_750), ("other", 37_500)],
)
def test_g30_get_signal_bandwidth_maps_the_fec_type(
    monkeypatch: pytest.MonkeyPatch, fec_type: str, expected: int
) -> None:
    _patch_g30_client(monkeypatch, _och_os_client(_Endpoint(_Model(fec_type=fec_type))))
    assert g30_transponder.get_signal_bandwidth(SimpleNamespace(), "port-1/2/1") == expected


def test_g30_configure_transceiver_client_updates_port_and_ethernet(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = _Endpoint(_Model(admin_status=AdminStatusEnum.DOWN, service_label="", port_mode=None))
    eth = _Endpoint(_Model(admin_status=AdminStatusEnum.DOWN))
    endpoint.eth100g = eth
    _patch_g30_client(monkeypatch, _port_endpoint_client(endpoint))

    diffs = g30_transponder.configure_transceiver_client(
        SimpleNamespace(),
        "port-1/2/3",
        "client link",
        OpticalDigitalServiceSpeed(100),
    )

    assert endpoint.update_calls
    assert eth.update_calls
    assert endpoint.model.admin_status is AdminStatusEnum.UP
    assert endpoint.model.service_label == "client link"
    assert endpoint.model.port_mode is PortModeEnum("100GBE")
    assert diffs["+++"]  # the update produced changes


def test_g30_align_tx_power_to_target_clamps_at_the_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    och_os = _Endpoint(_Model(required_tx_optical_power=Decimal("5.00")))
    _patch_g30_client(monkeypatch, _och_os_client(och_os))

    diffs = g30_transponder.align_tx_power_to_target(SimpleNamespace(), "port-1/2/1", "20.0")

    assert och_os.update_calls
    assert och_os.model.required_tx_optical_power == Decimal("-10.00")
    assert diffs["+++"]["root['required_tx_optical_power']"] == Decimal("-10.00")


def test_g30_align_tx_power_to_target_raises_without_a_configured_power(monkeypatch: pytest.MonkeyPatch) -> None:
    och_os = _Endpoint(_Model(required_tx_optical_power=None))
    _patch_g30_client(monkeypatch, _och_os_client(och_os))

    with pytest.raises(ValueError, match="No required transmit power configured"):
        g30_transponder.align_tx_power_to_target(_node_block(), "port-1/2/1", "1.0")
