"""Unit tests for the Nokia Groove G30 device port role determination.

The role of every G30 port is derived from the device (card type, OTS presence
and port id), not from heuristics on the port name. These tests fake the G30
RESTCONF navigators so the rules are exercised without a live device.
"""

from types import SimpleNamespace
from typing import Any

import pytest

from orchestrator.optical.hal.adapters.nokia_groove_g30 import port as g30_port
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.services.nokia.g30.data_models.ne import CardTypeEnum


def _port(alias_name: str, port_id: int, subports: list[Any] | None = None) -> SimpleNamespace:
    return SimpleNamespace(alias_name=alias_name, port_id=port_id, subport=subports or [])


def _subport(alias_name: str, subport_id: int) -> SimpleNamespace:
    return SimpleNamespace(alias_name=alias_name, subport_id=subport_id)


def _slot(slot_id: int, card: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(slot_id=slot_id, card=card)


def _card(
    required_type: CardTypeEnum,
    ports: list[Any] | None = None,
    subslots: list[Any] | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(required_type=required_type, port=ports or [], subslot=subslots or [])


def _subslot(subcard: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(subcard=subcard)


def _fake_g30_client(shelves: list[Any], ots_names: list[str]) -> SimpleNamespace:
    optical_interfaces = SimpleNamespace(ots=[SimpleNamespace(ots_name=name) for name in ots_names])
    return SimpleNamespace(
        data=SimpleNamespace(
            ne_ne=SimpleNamespace(
                shelf=SimpleNamespace(retrieve=lambda **_: shelves),
                services=SimpleNamespace(optical_interfaces=SimpleNamespace(retrieve=lambda **_: optical_interfaces)),
            )
        )
    )


@pytest.fixture
def g30_client(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """A G30 with an OCC2 card (with and without a matching OTS) and a non-OCC2 card."""
    occ2_subcard = SimpleNamespace(
        port=[
            _port("port-1/3.3/1", 1),
            _port("port-1/3.1/3", 3, subports=[_subport("subport-1/3.1/3", 3)]),
        ]
    )
    occ2_card = _card(CardTypeEnum.OCC2, subslots=[_subslot(occ2_subcard)])
    transponder_card = _card(CardTypeEnum.CHM2, ports=[_port("port-1/2/1", 1), _port("port-1/2/3", 3)])
    client = _fake_g30_client(
        shelves=[SimpleNamespace(slot=[_slot(3, occ2_card), _slot(2, transponder_card)])],
        ots_names=["ots-1/3.3/1"],
    )
    monkeypatch.setattr(g30_port, "get_g30_client", lambda *_: client)
    return client


def test_occ2_port_with_matching_ots_is_ols_line(g30_client: SimpleNamespace) -> None:
    assert "port-1/3.3/1" in g30_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.OLS_LINE])


def test_occ2_port_without_matching_ots_is_ols_add_drop(g30_client: SimpleNamespace) -> None:
    """A port/subport of an OCC2 card with no OTS of the same id is an OLS add/drop port."""
    add_drop = g30_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.OLS_ADD_DROP])
    assert "subport-1/3.1/3" in add_drop
    assert "port-1/3.3/1" not in add_drop


def test_non_occ2_line_ports_are_card_ports_1_and_2(g30_client: SimpleNamespace) -> None:
    line = g30_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.TRANSPONDER_LINE])
    assert line == ["port-1/2/1"]


def test_non_occ2_other_ports_are_transponder_client(g30_client: SimpleNamespace) -> None:
    client = g30_port.get_device_ports_by_role(SimpleNamespace(), [OpticalPortRole.TRANSPONDER_CLIENT])
    assert client == ["port-1/2/3"]


def test_each_port_has_exactly_one_role(g30_client: SimpleNamespace) -> None:
    """Roles are disjoint: no port is reported under two roles."""
    all_roles = [
        OpticalPortRole.OLS_LINE,
        OpticalPortRole.OLS_ADD_DROP,
        OpticalPortRole.TRANSPONDER_LINE,
        OpticalPortRole.TRANSPONDER_CLIENT,
    ]
    ports_by_role = {role: set(g30_port.get_device_ports_by_role(SimpleNamespace(), [role])) for role in all_roles}
    seen: set[str] = set()
    for ports in ports_by_role.values():
        assert not (ports & seen)
        seen |= ports
    assert seen == {"port-1/3.3/1", "port-1/3.1/3", "subport-1/3.1/3", "port-1/2/1", "port-1/2/3"}
