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
    _find_flexils_osnc,
    _omses_from_line_ports,
    _rtrv_oel_or_none,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.services.nokia.flexils.exceptions import TL1CommandDeniedError


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


def _node(role: OpticalNodeRole, name: str = "flex.a") -> Any:
    """Build a FlexILS node whose TID (``name``) differs from its fqdn.

    Device-side identifiers must use the TID, never the fqdn, so the two are kept
    distinct to catch regressions (see :func:`_node_id`).
    """
    return NokiaFlexIlsBlockProvisioning.model_construct(
        optical_node_role=role,
        management=SimpleNamespace(optical_module_node_fqdn=f"{name}.example.com"),
        optical_flexils_target_id=name,
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
        lambda **_kwargs: ({"LOCENDPOINT": "1-A-2-L1-1", "REMENDPOINT": "1-A-2-L1-1"}, True),
    )
    monkeypatch.setattr(flexils_spectrum, "_open_shutter", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flex_client",
        lambda _device: SimpleNamespace(
            rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=[]),
            rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[{"LOCENDPOINT": "1-A-2-L1-1"}]),
        ),
    )

    result = flexils_spectrum.deploy(
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
    assert result == {"---": {}, "+++": {"root['OSNC']['LOCENDPOINT']": "1-A-2-L1-1"}}


def test_rtrv_oel_or_none_returns_none_when_object_is_missing() -> None:
    """A missing OEL is reported as absent, not as an error."""
    tid = "flex.a"

    def _rtrv_oel(**_kwargs: Any) -> Any:
        raise TL1CommandDeniedError(tid, "RTRV-OEL", "SPECIFIED OBJECT ENTITY DOES NOT EXIST")

    flex = SimpleNamespace(rtrv_oel=_rtrv_oel)

    assert _rtrv_oel_or_none(flex, "cid") is None


def test_rtrv_oel_or_none_returns_record_when_present() -> None:
    record = {"AID": "cid", "OPERSTATE": "IS"}
    flex = SimpleNamespace(rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=[record]))

    assert _rtrv_oel_or_none(flex, "cid") is record


def test_rtrv_oel_or_none_reraises_unrelated_denials() -> None:
    """Only the "does not exist" denial is swallowed; other TL1 errors propagate."""
    tid = "flex.a"

    def _rtrv_oel(**_kwargs: Any) -> Any:
        raise TL1CommandDeniedError(tid, "RTRV-OEL", "INVALID INPUT")

    flex = SimpleNamespace(rtrv_oel=_rtrv_oel)

    with pytest.raises(TL1CommandDeniedError):
        _rtrv_oel_or_none(flex, "cid")


def test_delete_returns_the_removed_osnc_as_a_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deleting a circuit reports the removed OSNC (`---`), never the full record."""
    osnc = {"LOCENDPOINT": "1-A-3-T11-1", "CKTIDSUFFIX": "cid"}
    flex = SimpleNamespace(
        ed_osnc=lambda **_kwargs: None,
        dlt_osnc=lambda **_kwargs: None,
    )
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_args, **_kwargs: (flex, osnc))

    result = flexils_spectrum.delete(
        _node(OpticalNodeRole.ROADM, "flex.a"),
        OpticalSpectrumSectionBlockProvisioning.model_construct(),
        "spec",
        (191_325_000, 196_125_000),
        "cid",
    )

    assert result == {
        "---": {"root['OSNC']['LOCENDPOINT']": "1-A-3-T11-1", "root['OSNC']['CKTIDSUFFIX']": "cid"},
        "+++": {},
    }


def test_find_flexils_osnc_matches_by_identifier_despite_passband_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A retried modify finds the OSNC even when the device already has the new passband.

    ``modify`` updates the device before the database transaction commits, so on a
    retry the subscription still carries the old passband while the device carries the
    new one. The lookup must identify the OSNC by CKTIDSUFFIX and endpoints, never by
    passband, or every retry fails to find it.
    """
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    add_drop_a = _port(node_a, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP)
    add_drop_b = _port(node_b, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP)
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[add_drop_a, add_drop_b],
    )

    osnc = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "REMNODETID": "flex.b",
        "CKTIDSUFFIX": "cid",
        "PASSBANDLIST": [194_300_000, 194_450_000],
    }
    flex = _FakeFlex([osnc])

    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flexils_name_client_tributary",
        lambda device, port: (("flex.a" if device is node_a else "flex.b"), flex, port),
    )

    found_flex, found_osnc = _find_flexils_osnc(
        "spec",
        section,
        (192_300_000, 192_450_000),
        "cid",
    )

    assert found_flex is flex
    assert found_osnc is osnc


def test_validate_reports_passband_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validation surfaces a passband divergence as a mismatch, not as a missing OSNC."""
    osnc = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "PASSBANDLIST": [194_300_000, 194_450_000],
        "CARRIERLIST": [194_375_000, 150_000],
        "LABEL": "spec",
    }
    flex = SimpleNamespace(
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"SHUTTERSTATE": "OPEN"}]),
    )

    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_args, **_kwargs: (flex, osnc))
    monkeypatch.setattr(flexils_spectrum, "_remote_flex_for_section", lambda *_args, **_kwargs: flex)

    with pytest.raises(ValueError, match="Passband mismatch"):
        flexils_spectrum.validate(
            _node(OpticalNodeRole.ROADM, "flex.a"),
            OpticalSpectrumSectionBlockProvisioning.model_construct(),
            "spec",
            (192_300_000, 192_450_000),
            (194_375_000, 150_000),
            "spec",
            "cid",
        )


def test_modify_returns_a_before_after_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    """Modifying a circuit reports only the changed OSNC fields."""
    osnc_before = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "OELAID": "cid",
        "PASSBANDLIST": [191_325_000, 196_125_000],
        "CARRIERLIST": [193_725_000, 4_800_000],
        "LABEL": "old",
    }
    osnc_after = {
        **osnc_before,
        "PASSBANDLIST": [191_425_000, 196_225_000],
        "CARRIERLIST": [193_825_000, 4_800_000],
        "LABEL": "new",
    }
    flex = SimpleNamespace(
        ed_osnc=lambda **_kwargs: None,
        put_maintenance=lambda **_kwargs: None,
        ed_sch=lambda **_kwargs: None,
        rst_maintenance=lambda **_kwargs: None,
        rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=[{"AID": "cid"}]),
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[osnc_after]),
    )
    remote_flex = SimpleNamespace(
        put_maintenance=lambda **_kwargs: None,
        ed_sch=lambda **_kwargs: None,
        rst_maintenance=lambda **_kwargs: None,
    )
    node = _node(OpticalNodeRole.ROADM, "flex.a")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[_port(node, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP)],
        optical_spectrum_section_express_ports=[],
    )
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_args, **_kwargs: (flex, osnc_before))
    monkeypatch.setattr(flexils_spectrum, "_remote_flex_for_section", lambda *_args, **_kwargs: remote_flex)
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.modify(
        node,
        section,
        "spec",
        (191_425_000, 196_225_000),
        (193_825_000, 4_800_000),
        label="new",
        old_passband=(191_325_000, 196_125_000),
        circuit_identifier="cid",
    )

    assert result["---"] == {
        "root['OSNC']['PASSBANDLIST'][0]": 191_325_000,
        "root['OSNC']['PASSBANDLIST'][1]": 196_125_000,
        "root['OSNC']['CARRIERLIST'][0]": 193_725_000,
        "root['OSNC']['LABEL']": "old",
    }
    assert result["+++"] == {
        "root['OSNC']['PASSBANDLIST'][0]": 191_425_000,
        "root['OSNC']['PASSBANDLIST'][1]": 196_225_000,
        "root['OSNC']['CARRIERLIST'][0]": 193_825_000,
        "root['OSNC']['LABEL']": "new",
    }


def test_append_label_returns_a_before_after_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    """Appending a label reports only the OSNC label change."""
    osnc_before = {"LOCENDPOINT": "1-A-3-T11-1", "LABEL": "a"}
    osnc_after = {"LOCENDPOINT": "1-A-3-T11-1", "LABEL": "a+b"}
    flex = SimpleNamespace(
        ed_osnc=lambda **_kwargs: None,
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[osnc_after]),
    )
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_args, **_kwargs: (flex, osnc_before))

    result = flexils_spectrum.append_label(
        _node(OpticalNodeRole.ROADM, "flex.a"),
        OpticalSpectrumSectionBlockProvisioning.model_construct(),
        "spec",
        (191_325_000, 196_125_000),
        "b",
        "cid",
    )

    assert result == {"---": {"root['OSNC']['LABEL']": "a"}, "+++": {"root['OSNC']['LABEL']": "a+b"}}


def test_delete_oel_returns_the_removed_oel_as_a_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deleting an unreferenced OEL reports the removed OEL (`---`)."""
    records = [{"AID": "cid", "OPERSTATE": "IS"}]
    flex = SimpleNamespace(
        rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=list(records)),
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[]),
        dlt_oel=lambda **_kwargs: records.clear(),
    )
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.delete_oel(_node(OpticalNodeRole.ROADM, "flex.a"), "cid")

    assert result == {"---": {"root['OEL']['AID']": "cid", "root['OEL']['OPERSTATE']": "IS"}, "+++": {}}


def test_delete_cross_connection_returns_the_removed_ocrs_as_a_diff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deleting a cross-connection reports the removed OCRS (`---`)."""
    node = _node(OpticalNodeRole.ROADM, "flex.a")
    passband = (191_325_000, 196_125_000)
    carrier = (193_725_000, 4_800_000)
    ocr = {
        "FROMAID": "1-A-1-L1-1",
        "TOAID": "1-A-2-L1-1",
        "PASSBANDLIST": list(passband),
        "CARRIERLIST": list(carrier),
        "CKTIDSUFFIX": "cid",
        "LABEL": "lbl",
    }
    flex = SimpleNamespace(
        rtrv_ocrs=lambda **_kwargs: SimpleNamespace(parsed_data=[ocr]),
        dlt_ocrs=lambda **_kwargs: None,
    )
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.delete_cross_connection(
        node,
        _port(node, "1-A-1-L1"),
        _port(node, "1-A-2-L1"),
        passband,
        carrier=carrier,
        label="lbl",
        circuit_identifier="cid",
    )

    assert result["---"]["root['OCRS']['FROMAID']"] == "1-A-1-L1-1"
    assert result["+++"] == {}
