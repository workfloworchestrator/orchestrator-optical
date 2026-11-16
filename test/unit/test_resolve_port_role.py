"""Unit tests for the role lookup of a pipe termination port."""

from types import SimpleNamespace
from typing import Any

import pytest

from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.workflows.optical_pipe import shared as pipe_shared

_NODE = SimpleNamespace(management=SimpleNamespace(optical_module_node_name="node-a"))
_ROLES = [OpticalPortRole.OLS_LINE, OpticalPortRole.OLS_ADD_DROP]


def _fake_enumeration(monkeypatch: pytest.MonkeyPatch, ports_by_role: dict[OpticalPortRole, list[str]]) -> list[Any]:
    calls: list[Any] = []

    def enumerate_ports(node_block: Any, roles: list[OpticalPortRole]) -> dict[OpticalPortRole, list[str]]:
        calls.append((node_block, roles))
        return ports_by_role

    monkeypatch.setattr(pipe_shared, "get_device_ports_grouped_by_role", enumerate_ports)
    return calls


def test_resolve_port_role_enumerates_the_node_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every candidate role is asked in one enumeration (one per role repeats the device reads)."""
    calls = _fake_enumeration(
        monkeypatch, {OpticalPortRole.OLS_LINE: ["line-1"], OpticalPortRole.OLS_ADD_DROP: ["add-drop-1"]}
    )

    assert pipe_shared.resolve_port_role(_NODE, "add-drop-1", _ROLES) is OpticalPortRole.OLS_ADD_DROP
    assert calls == [(_NODE, _ROLES)]


def test_resolve_port_role_rejects_a_port_of_no_requested_role(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_enumeration(monkeypatch, {OpticalPortRole.OLS_LINE: ["line-1"], OpticalPortRole.OLS_ADD_DROP: []})

    with pytest.raises(ValueError, match="is not one of the roles"):
        pipe_shared.resolve_port_role(_NODE, "other", _ROLES)


def test_resolve_port_role_rejects_a_port_of_several_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_enumeration(monkeypatch, {OpticalPortRole.OLS_LINE: ["port-1"], OpticalPortRole.OLS_ADD_DROP: ["port-1"]})

    with pytest.raises(ValueError, match="matches multiple roles"):
        pipe_shared.resolve_port_role(_NODE, "port-1", _ROLES)
