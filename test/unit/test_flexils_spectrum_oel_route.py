"""Unit tests for the FlexILS spectrum OEL helpers (database-free).

Covers two things: the OEL deletion guard (the explicit route cannot be edited with
ED-OEL, so a path change deletes the OEL after checking RTRV-OSNC), and the OMS
segmentation used to build the OEL explicit route. The latter must only ever look up
OTEINTFs for OLS *line* ports: the add/drop ports are FMMC tributary (T) ports and
have no OTEINTF, so passing them here fails on real devices.
"""

from types import SimpleNamespace
from typing import Any

import pytest

from orchestrator.optical.hal.adapters.nokia_flexils import spectrum as flexils_spectrum
from orchestrator.optical.hal.adapters.nokia_flexils.spectrum import (
    _delete_oel_if_unused,
    _explicit_route_from_omses,
    _omses_from_line_ports,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockProvisioning,
)


class _FakeFlex:
    """Fake TL1 client exposing just the commands used by the OEL deletion guard."""

    def __init__(self, osnc_records: list[dict[str, Any]]) -> None:
        self.osnc_records = osnc_records
        self.deleted_oels: list[str] = []

    def rtrv_osnc(self) -> Any:
        return type("_Response", (), {"parsed_data": self.osnc_records})()

    def dlt_oel(self, aid: str) -> Any:
        self.deleted_oels.append(aid)
        return None


def _node(role: OpticalNodeRole, fqdn: str = "flex.a") -> Any:
    return NokiaFlexIlsBlockProvisioning.model_construct(
        optical_node_role=role,
        management=SimpleNamespace(optical_module_node_fqdn=fqdn),
    )


def _port(node: Any, name: str, role: OpticalPortRole = OpticalPortRole.OLS_LINE) -> Any:
    return SimpleNamespace(
        optical_port_host_node=node,
        optical_port_name=name,
        optical_port_role=role,
    )


def test_delete_oel_if_unused_deletes_when_no_osnc_references_it() -> None:
    flex = _FakeFlex([{"OELAID": "other-oel", "LOCENDPOINT": "1-A-1-L1-1"}])

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.deleted_oels == ["my-oel"]


def test_delete_oel_if_unused_leaves_oel_when_another_osnc_references_it() -> None:
    flex = _FakeFlex([{"OELAID": "my-oel", "LOCENDPOINT": "1-A-1-L1-1"}])

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.deleted_oels == []


def test_omses_from_line_ports_pairs_two_roadm_ports() -> None:
    port_a = _port(_node(OpticalNodeRole.ROADM, "flex.a"), "1-A-1-L1")
    port_b = _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-1-L1")

    assert _omses_from_line_ports([port_a, port_b]) == [(port_a, port_b)]


def test_omses_from_line_ports_skips_amplifiers() -> None:
    port_a = _port(_node(OpticalNodeRole.ROADM, "flex.a"), "1-A-1-L1")
    amp = _port(_node(OpticalNodeRole.AMPLIFIER, "flex.amp"), "1-A-1-L1")
    port_b = _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-1-L1")

    assert _omses_from_line_ports([port_a, amp, port_b]) == [(port_a, port_b)]


def test_omses_from_line_ports_pairs_an_intermediate_roadm() -> None:
    port_a = _port(_node(OpticalNodeRole.ROADM, "flex.a"), "1-A-1-L1")
    port_b_in = _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-1-L1")
    port_b_out = _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-2-L1")
    port_c = _port(_node(OpticalNodeRole.ROADM, "flex.c"), "1-A-1-L1")

    assert _omses_from_line_ports([port_a, port_b_in, port_b_out, port_c]) == [
        (port_a, port_b_in),
        (port_b_out, port_c),
    ]


def test_omses_from_line_ports_rejects_empty_path() -> None:
    with pytest.raises(ValueError, match="empty"):
        _omses_from_line_ports([])


def test_omses_from_line_ports_rejects_path_not_starting_with_roadm() -> None:
    amp = _port(_node(OpticalNodeRole.AMPLIFIER, "flex.amp"), "1-A-1-L1")

    with pytest.raises(ValueError, match="start with a ROADM"):
        _omses_from_line_ports([amp])


def test_explicit_route_only_looks_up_line_ports(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: list[str] = []

    def _record(device: Any, port_name: str) -> str:
        recorded.append(port_name)
        return port_name

    monkeypatch.setattr(flexils_spectrum, "_oteintf_from_port_name", _record)

    port_a = _port(_node(OpticalNodeRole.ROADM, "flex.a"), "1-A-1-L1")
    port_b = _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-2-L1")

    route = _explicit_route_from_omses([(port_a, port_b)])

    assert route == [("flex.a", "1-A-1-L1", "flex.b", "1-A-2-L1")]
    assert recorded == ["1-A-1-L1", "1-A-2-L1"]


def test_deploy_builds_omses_from_express_ports_only(monkeypatch: pytest.MonkeyPatch) -> None:
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    add_drop_a = _port(node_a, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP)
    add_drop_b = _port(node_b, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP)
    line_a = _port(node_a, "1-A-2-L1")
    line_b = _port(node_b, "1-A-2-L1")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[add_drop_a, add_drop_b],
        optical_spectrum_section_express_ports=[line_a, line_b],
    )

    captured: list[list[Any]] = []
    monkeypatch.setattr(
        flexils_spectrum,
        "_omses_from_line_ports",
        lambda ports: captured.append(list(ports)) or [(line_a, line_b)],
    )
    monkeypatch.setattr(flexils_spectrum, "_find_or_create_oel", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)
    monkeypatch.setattr(
        flexils_spectrum,
        "_find_or_create_osnc",
        lambda **_kwargs: {"LOCENDPOINT": "1-A-2-L1-1", "REMENDPOINT": "1-A-2-L1-1"},
    )
    monkeypatch.setattr(flexils_spectrum, "_open_shutter", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flex_client",
        lambda _device: SimpleNamespace(
            rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[{"LOCENDPOINT": "1-A-2-L1-1"}])
        ),
    )

    flexils_spectrum.deploy(
        node_a,
        section,
        "spec",
        (191_325_000, 196_125_000),
        (193_100_000, 6_250),
        "label",
        "cid",
    )

    assert captured == [[line_a, line_b]]
    assert all(port.optical_port_role is not OpticalPortRole.OLS_ADD_DROP for port in captured[0])
