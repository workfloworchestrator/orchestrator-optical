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
    _OsncNotFoundError,
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
        self.locked_oels: list[str] = []
        self.deleted_oels: list[str] = []
        self.events: list[str] = []

    def rtrv_osnc(self) -> Any:
        return type("_Response", (), {"parsed_data": self.osnc_records})()

    def ed_oel(self, aid: str, **_kwargs: Any) -> Any:
        self.locked_oels.append(aid)
        self.events.append(f"lock:{aid}")
        return None

    def dlt_oel(self, aid: str) -> Any:
        self.deleted_oels.append(aid)
        self.events.append(f"delete:{aid}")
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

    assert flex.locked_oels == ["my-oel"]
    assert flex.deleted_oels == ["my-oel"]


def test_delete_oel_if_unused_locks_the_oel_before_deleting_it() -> None:
    """FlexILS refuses DLT-OEL with "OEL is not Locked": the OEL must be put OOS first."""
    flex = _FakeFlex([])

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.events == ["lock:my-oel", "delete:my-oel"]


def test_delete_oel_if_unused_leaves_oel_when_another_osnc_references_it() -> None:
    flex = _FakeFlex([{"OELAID": "my-oel", "LOCENDPOINT": "1-A-1-L1-1"}])

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.locked_oels == []
    assert flex.deleted_oels == []


def test_delete_oel_if_unused_deletes_when_the_node_has_no_osnc() -> None:
    """A node whose last OSNC was deleted denies RTRV-OSNC; that must not block the OEL deletion."""
    flex = _FakeFlex([])
    tid = "flex.a"

    def _rtrv_osnc() -> Any:
        raise TL1CommandDeniedError(tid, "RTRV-OSNC", "SPECIFIED OBJECT ENTITY DOES NOT EXIST")

    flex.rtrv_osnc = _rtrv_osnc  # type: ignore[method-assign]

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.locked_oels == ["my-oel"]
    assert flex.deleted_oels == ["my-oel"]


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


def test_ensure_builds_omses_from_express_ports_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """On the create branch, the OEL explicit route uses only interior line ports.

    The add/drop ports are FMMC tributary (T) ports with no OTEINTF, so passing
    them here fails on real devices.
    """
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
    monkeypatch.setattr(flexils_spectrum, "_rtrv_oel_or_none", lambda _flex, _aid: None)
    monkeypatch.setattr(flexils_spectrum, "_find_or_create_oel", lambda *_args, **_kwargs: {"AID": "cid"})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)

    def _missing_osnc(*_args: Any, **_kwargs: Any) -> Any:
        msg = "no OSNC on either end"
        raise _OsncNotFoundError(msg)

    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", _missing_osnc)
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
            rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[{"LOCENDPOINT": "1-A-2-L1-1"}]),
        ),
    )

    result = flexils_spectrum.ensure(
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
    assert result == {
        "---": {},
        "+++": {"root['OEL']['AID']": "cid", "root['OSNC']['LOCENDPOINT']": "1-A-2-L1-1"},
    }


def test_find_or_create_oel_returns_existing_without_entering(monkeypatch: pytest.MonkeyPatch) -> None:
    """An existing OEL is reused: reconcile must not re-enter it."""
    existing = {"AID": "cid", "OPERSTATE": "IS"}
    entered: list[str] = []
    flex = SimpleNamespace(
        rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=[existing]),
        ent_oel=lambda **kwargs: entered.append(kwargs["aid"]),
    )
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum._find_or_create_oel(  # noqa: SLF001
        "cid", _node(OpticalNodeRole.ROADM, "flex.a"), _node(OpticalNodeRole.ROADM, "flex.b"), []
    )

    assert result is existing
    assert entered == []


def test_ensure_recreates_missing_osnc_without_duplicating(monkeypatch: pytest.MonkeyPatch) -> None:
    """A borrower heals a deleted shared OSNC: ensure creates exactly one OSNC with the new label."""
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[
            _port(node_a, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
            _port(node_b, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
        ],
        optical_spectrum_section_express_ports=[],
    )
    created = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "LABEL": "ch: svc",
        "CKTIDSUFFIX": "cid",
    }
    entered: list[dict[str, Any]] = []

    def _ent_osnc(**kwargs: Any) -> Any:
        entered.append(kwargs)
        return None

    def _rtrv_osnc(aid: str | None = None, **_kwargs: Any) -> Any:
        if aid is None:
            return SimpleNamespace(parsed_data=[])
        return SimpleNamespace(parsed_data=[created])

    tid = "flex.a"

    def _rtrv_sch_missing(**_kwargs: Any) -> Any:
        raise TL1CommandDeniedError(tid, "RTRV-SCH", "INPUT, SPECIFIED OBJECT ENTITY DOES NOT EXIST")

    flex = SimpleNamespace(ent_osnc=_ent_osnc, rtrv_osnc=_rtrv_osnc, rtrv_sch=_rtrv_sch_missing)
    monkeypatch.setattr(flexils_spectrum, "_rtrv_oel_or_none", lambda _flex, _aid: {"AID": "cid"})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)
    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flexils_name_client_tributary",
        lambda device, port: (("flex.a" if device is node_a else "flex.b"), flex, port),
    )
    opened: list[str] = []
    monkeypatch.setattr(flexils_spectrum, "_open_shutter", lambda _device, aid: opened.append(aid))
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.ensure(
        node_a, section, "spec", (191_325_000, 196_125_000), (193_100_000, 6_250), "ch: svc", "cid"
    )

    assert len(entered) == 1
    assert entered[0]["cktidsuffix"] == "cid"
    assert opened == ["1-A-3-T11-1", "1-A-3-T11-1"]
    assert result["+++"]["root['OSNC']['LOCENDPOINT']"] == "1-A-3-T11-1"


def test_find_or_create_osnc_skips_endpoint_used_by_foreign_osnc(monkeypatch: pytest.MonkeyPatch) -> None:
    """A foreign OSNC on ``<port>-1`` pushes the new circuit to ``<port>-2`` instead of colliding.

    Regression test for a borrower reconcile that reused ``1-E3-1-T2A-1`` while a legacy
    OSNC held that endpoint: the allocator only probed the superchannel namespace, so
    ``ENT-OSNC`` was denied with "already exists" (which the TL1 client does not raise)
    and the foreign record was then mistaken for the created circuit.
    """
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    occupant = {
        "LOCENDPOINT": "1-E3-1-T2A-1",
        "REMENDPOINT": "1-E1-1-T1A-1",
        "REMNODETID": "flex.b",
        "CKTIDSUFFIX": "OCh333",
        "LABEL": "f001c01",
    }
    created = {
        "LOCENDPOINT": "1-E3-1-T2A-2",
        "REMENDPOINT": "1-E1-1-T1A-2",
        "LABEL": "OCh333: f001c01",
        "CKTIDSUFFIX": "cid",
    }
    entered: list[dict[str, Any]] = []

    def _rtrv_osnc(aid: str | None = None, **_kwargs: Any) -> Any:
        if aid is None:
            return SimpleNamespace(parsed_data=[occupant])
        return SimpleNamespace(parsed_data=[created])

    tid = "flex.a"

    def _rtrv_sch_missing(**_kwargs: Any) -> Any:
        raise TL1CommandDeniedError(tid, "RTRV-SCH", "INPUT, SPECIFIED OBJECT ENTITY DOES NOT EXIST")

    flex = SimpleNamespace(
        ent_osnc=lambda **kwargs: entered.append(kwargs),
        rtrv_osnc=_rtrv_osnc,
        rtrv_sch=_rtrv_sch_missing,
    )
    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flexils_name_client_tributary",
        lambda device, port: (("flex.a" if device is node_a else "flex.b"), flex, port),
    )
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)

    record, was_created = flexils_spectrum._find_or_create_osnc(  # noqa: SLF001
        src_device=node_a,
        dst_device=node_b,
        circuit_identifier="cid",
        osnc_label="OCh333: f001c01",
        oel_aid="cid",
        src_port_name="1-E3-1-T2A",
        dst_port_name="1-E1-1-T1A",
        passband=(191_325_000, 196_125_000),
        carrier=(193_100_000, 6_250),
    )

    assert was_created is True
    assert record is created
    assert len(entered) == 1
    assert entered[0]["aid"] == "1-E3-1-T2A-2"
    assert entered[0]["remendpoint"] == "1-E1-1-T1A-2"
    assert entered[0]["cktidsuffix"] == "cid"


def test_find_or_create_osnc_rejects_foreign_record_after_ent(monkeypatch: pytest.MonkeyPatch) -> None:
    """A re-read record carrying another CKTIDSUFFIX raises instead of being adopted.

    ``ENT-OSNC`` denied with "already exists" does not raise on the TL1 wire, so the
    post-enter ``RTRV-OSNC`` can return a foreign occupant. Adopting it would drive the
    shutter commands against someone else's endpoints (which then fail with "not found"
    when its superchannels are gone).
    """
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    foreign = {
        "LOCENDPOINT": "1-E3-1-T2A-2",
        "REMENDPOINT": "1-E1-1-T1A-2",
        "CKTIDSUFFIX": "OCh333",
        "LABEL": "f001c01",
    }
    flex = SimpleNamespace(
        ent_osnc=lambda **_kwargs: None,
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[foreign]),
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"AID": "x"}]),
    )
    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flexils_name_client_tributary",
        lambda device, port: (("flex.a" if device is node_a else "flex.b"), flex, port),
    )
    monkeypatch.setattr(flexils_spectrum, "_find_first_free_endpoint_id", lambda *_args, **_kwargs: 2)
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)

    with pytest.raises(ValueError, match="occupied by another circuit.*OCh333"):
        flexils_spectrum._find_or_create_osnc(  # noqa: SLF001
            src_device=node_a,
            dst_device=node_b,
            circuit_identifier="cid",
            osnc_label="OCh333: f001c01",
            oel_aid="cid",
            src_port_name="1-E3-1-T2A",
            dst_port_name="1-E1-1-T1A",
            passband=(191_325_000, 196_125_000),
            carrier=(193_100_000, 6_250),
        )


def test_ensure_converges_stale_label_without_entering(monkeypatch: pytest.MonkeyPatch) -> None:
    """An existing OSNC with a stale label is edited in place, never duplicated."""
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[
            _port(node_a, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
            _port(node_b, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
        ],
        optical_spectrum_section_express_ports=[],
    )
    osnc_before = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "OELAID": "cid",
        "PASSBANDLIST": [191_325_000, 196_125_000],
        "CARRIERLIST": [193_100_000, 6_250],
        "LABEL": "ch: old",
    }
    osnc_after = {**osnc_before, "LABEL": "ch: svcA + svcB"}
    calls: dict[str, list[Any]] = {"ent": [], "ed": []}
    flex = SimpleNamespace(
        ed_osnc=lambda **kwargs: calls["ed"].append(kwargs),
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[osnc_after]),
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"SHUTTERSTATE": "OPEN"}]),
        put_maintenance=lambda **_kwargs: None,
        rst_maintenance=lambda **_kwargs: None,
    )
    monkeypatch.setattr(flexils_spectrum, "_rtrv_oel_or_none", lambda _flex, _aid: {"AID": "cid"})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_a, **_k: (flex, dict(osnc_before)))
    monkeypatch.setattr(flexils_spectrum, "_remote_flex_for_section", lambda *_a, **_k: flex)
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)

    result = flexils_spectrum.ensure(
        node_a, section, "spec", (191_325_000, 196_125_000), (193_100_000, 6_250), "ch: svcA + svcB", "cid"
    )

    assert calls["ent"] == []
    assert any("label" in call for call in calls["ed"])
    assert result["---"]["root['OSNC']['LABEL']"] == "ch: old"
    assert result["+++"]["root['OSNC']['LABEL']"] == "ch: svcA + svcB"


def test_ensure_is_noop_when_already_converged(monkeypatch: pytest.MonkeyPatch) -> None:
    """An already converged circuit yields an empty diff and issues no edits."""
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[
            _port(node_a, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
            _port(node_b, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
        ],
        optical_spectrum_section_express_ports=[],
    )
    osnc = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "OELAID": "cid",
        "PASSBANDLIST": [191_325_000, 196_125_000],
        "CARRIERLIST": [193_100_000, 6_250],
        "LABEL": "ch: svc",
    }
    edited: list[Any] = []
    flex = SimpleNamespace(
        ed_osnc=lambda **kwargs: edited.append(kwargs),
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"SHUTTERSTATE": "OPEN"}]),
    )
    monkeypatch.setattr(flexils_spectrum, "_rtrv_oel_or_none", lambda _flex, _aid: {"AID": "cid"})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_a, **_k: (flex, dict(osnc)))
    monkeypatch.setattr(flexils_spectrum, "_remote_flex_for_section", lambda *_a, **_k: flex)
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.ensure(
        node_a, section, "spec", (191_325_000, 196_125_000), (193_100_000, 6_250), "ch: svc", "cid"
    )

    assert edited == []
    assert result == {"---": {}, "+++": {}}


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


def test_delete_is_a_noop_when_the_osnc_is_already_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    """An already-deleted circuit yields an empty diff instead of failing (idempotent teardown)."""
    node_a = _node(OpticalNodeRole.ROADM, "flex.a")
    node_b = _node(OpticalNodeRole.ROADM, "flex.b")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[
            _port(node_a, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
            _port(node_b, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
        ],
    )
    monkeypatch.setattr(
        flexils_spectrum,
        "_get_flexils_name_client_tributary",
        lambda device, port: (("flex.a" if device is node_a else "flex.b"), SimpleNamespace(), port),
    )
    monkeypatch.setattr(flexils_spectrum, "_find_matching_osnc_on_flexils", lambda **_kwargs: None)

    result = flexils_spectrum.delete(
        node_a,
        section,
        "spec",
        (191_325_000, 196_125_000),
        "cid",
    )

    assert result == {"---": {}, "+++": {}}


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


def _converge_setup(
    monkeypatch: pytest.MonkeyPatch,
    osnc_before: dict[str, Any],
    osnc_after: dict[str, Any],
    ed_osnc: Any,
) -> Any:
    """Wire the fakes for an ``ensure`` converge branch and return the resulting diff."""
    node = _node(OpticalNodeRole.ROADM, "flex.a")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[
            _port(node, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
            _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
        ],
        optical_spectrum_section_express_ports=[],
    )
    flex = SimpleNamespace(
        ed_osnc=ed_osnc,
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[osnc_after]),
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"SHUTTERSTATE": "OPEN"}]),
        put_maintenance=lambda **_kwargs: None,
        ed_sch=lambda **_kwargs: None,
        rst_maintenance=lambda **_kwargs: None,
    )
    remote_flex = SimpleNamespace(
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"SHUTTERSTATE": "OPEN"}]),
    )
    monkeypatch.setattr(flexils_spectrum, "_rtrv_oel_or_none", lambda _flex, _aid: {"AID": "cid"})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_a, **_k: (flex, dict(osnc_before)))
    monkeypatch.setattr(flexils_spectrum, "_remote_flex_for_section", lambda *_a, **_k: remote_flex)
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)
    return flexils_spectrum.ensure(
        node,
        section,
        "spec",
        (191_425_000, 196_225_000),
        (193_825_000, 4_800_000),
        "new",
        "cid",
    )


def test_ensure_converges_spectrum_drift_with_lock_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """A passband drift locks the OSNC before editing, without touching the OELAID."""
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
    calls: list[dict[str, Any]] = []
    result = _converge_setup(monkeypatch, osnc_before, osnc_after, lambda **kwargs: calls.append(kwargs) or None)

    assert calls[0] == {"aid": "1-A-3-T11-1", "is_oos": "OOS"}
    assert calls[1] == {
        "aid": "1-A-3-T11-1",
        "passbandlist": (191_425_000, 196_225_000),
        "carrierlist": (193_825_000, 4_800_000),
        "is_oos": "OOS",
    }
    assert "oelaid" not in calls[1]
    assert calls[2]["is_oos"] == "IS"
    assert result["---"]["root['OSNC']['PASSBANDLIST'][0]"] == 191_325_000
    assert result["+++"]["root['OSNC']['PASSBANDLIST'][0]"] == 191_425_000


def test_ensure_converges_oelaid_drift_with_lock_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """An OELAID drift locks the OSNC before editing, without touching the passband.

    Regression test for the reconcile DENY (``OELAid cannot be updated when
    Admin state is not locked``): the OELAID must be edited while the OSNC is
    already out of service, never combined with the lock transition.
    """
    osnc_before = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "OELAID": "stale-oel",
        "PASSBANDLIST": [191_425_000, 196_225_000],
        "CARRIERLIST": [193_825_000, 4_800_000],
        "LABEL": "new",
    }
    osnc_after = {**osnc_before, "OELAID": "cid"}
    calls: list[dict[str, Any]] = []
    result = _converge_setup(monkeypatch, osnc_before, osnc_after, lambda **kwargs: calls.append(kwargs) or None)

    assert calls[0] == {"aid": "1-A-3-T11-1", "is_oos": "OOS"}
    assert calls[1] == {"aid": "1-A-3-T11-1", "oelaid": "cid", "is_oos": "OOS"}
    assert "passbandlist" not in calls[1]
    assert calls[2]["is_oos"] == "IS"
    assert result["---"]["root['OSNC']['OELAID']"] == "stale-oel"
    assert result["+++"]["root['OSNC']['OELAID']"] == "cid"


def test_ensure_label_only_drift_never_locks(monkeypatch: pytest.MonkeyPatch) -> None:
    """A label-only drift stays a single in-service command with no traffic impact."""
    osnc_before = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "OELAID": "cid",
        "PASSBANDLIST": [191_425_000, 196_225_000],
        "CARRIERLIST": [193_825_000, 4_800_000],
        "LABEL": "old",
    }
    osnc_after = {**osnc_before, "LABEL": "new"}
    calls: list[dict[str, Any]] = []
    result = _converge_setup(monkeypatch, osnc_before, osnc_after, lambda **kwargs: calls.append(kwargs) or None)

    assert len(calls) == 1
    assert calls[0]["is_oos"] == "IS"
    assert result == {"---": {"root['OSNC']['LABEL']": "old"}, "+++": {"root['OSNC']['LABEL']": "new"}}


def test_ensure_restores_in_service_when_oos_edit_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed OOS edit restores the circuit in service before propagating the error."""
    osnc_before = {
        "LOCENDPOINT": "1-A-3-T11-1",
        "REMENDPOINT": "1-A-3-T11-1",
        "OELAID": "stale-oel",
        "PASSBANDLIST": [191_425_000, 196_225_000],
        "CARRIERLIST": [193_825_000, 4_800_000],
        "LABEL": "new",
    }
    calls: list[dict[str, Any]] = []

    def _ed_osnc(**kwargs: Any) -> None:
        calls.append(kwargs)
        if len(calls) == 2:
            msg = "DENY: OELAid cannot be updated"
            raise ValueError(msg)

    node = _node(OpticalNodeRole.ROADM, "flex.a")
    section = OpticalSpectrumSectionBlockProvisioning.model_construct(
        optical_spectrum_section_add_drop_ports=[
            _port(node, "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
            _port(_node(OpticalNodeRole.ROADM, "flex.b"), "1-A-3-T11", OpticalPortRole.OLS_ADD_DROP),
        ],
        optical_spectrum_section_express_ports=[],
    )
    flex = SimpleNamespace(
        ed_osnc=_ed_osnc,
        rtrv_sch=lambda **_kwargs: SimpleNamespace(parsed_data=[{"SHUTTERSTATE": "OPEN"}]),
    )
    monkeypatch.setattr(flexils_spectrum, "_rtrv_oel_or_none", lambda _flex, _aid: {"AID": "cid"})
    monkeypatch.setattr(flexils_spectrum, "_ensure_manualmode2", lambda _port: None)
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_a, **_k: (flex, dict(osnc_before)))
    monkeypatch.setattr(flexils_spectrum, "_remote_flex_for_section", lambda *_a, **_k: flex)
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)
    monkeypatch.setattr(flexils_spectrum, "sleep", lambda *_args, **_kwargs: None)

    with pytest.raises(ValueError, match="DENY"):
        flexils_spectrum.ensure(
            node,
            section,
            "spec",
            (191_425_000, 196_225_000),
            (193_825_000, 4_800_000),
            "new",
            "cid",
        )

    assert calls[0] == {"aid": "1-A-3-T11-1", "is_oos": "OOS"}
    assert calls[-1] == {"aid": "1-A-3-T11-1", "is_oos": "IS"}


def test_set_label_sends_quoted_label(monkeypatch: pytest.MonkeyPatch) -> None:
    """set_label double-quotes the OSNC label so ':' survives TL1 framing."""
    calls: list[dict[str, object]] = []
    osnc_before = {"LOCENDPOINT": "1-A-3-T11-1", "LABEL": "old"}
    osnc_after = {"LOCENDPOINT": "1-A-3-T11-1", "LABEL": "ch-01: svcA + svcB"}
    flex = SimpleNamespace(
        ed_osnc=lambda **kwargs: calls.append(kwargs),
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[osnc_after]),
    )
    monkeypatch.setattr(flexils_spectrum, "_find_flexils_osnc", lambda *_args, **_kwargs: (flex, osnc_before))

    result = flexils_spectrum.set_label(
        _node(OpticalNodeRole.ROADM, "flex.a"),
        OpticalSpectrumSectionBlockProvisioning.model_construct(),
        "spec",
        (191_325_000, 196_125_000),
        "ch-01: svcA + svcB",
        "cid",
    )

    assert calls == [{"aid": "1-A-3-T11-1", "label": '"ch-01: svcA + svcB"'}]
    assert result == {"---": {"root['OSNC']['LABEL']": "old"}, "+++": {"root['OSNC']['LABEL']": "ch-01: svcA + svcB"}}


def test_tl1_label_quoting_is_idempotent() -> None:
    """Pre-quoted input is not quoted twice; blank input is rejected."""
    assert flexils_spectrum._tl1_label("ch-01: svcA + svcB") == '"ch-01: svcA + svcB"'  # noqa: SLF001
    assert flexils_spectrum._tl1_label('"ch-01: svcA + svcB"') == '"ch-01: svcA + svcB"'  # noqa: SLF001
    with pytest.raises(ValueError, match="blank"):
        flexils_spectrum._tl1_label("  ")  # noqa: SLF001


def test_delete_oel_returns_the_removed_oel_as_a_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deleting an unreferenced OEL reports the removed OEL (`---`)."""
    records = [{"AID": "cid", "OPERSTATE": "IS"}]
    flex = SimpleNamespace(
        rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=list(records)),
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[]),
        ed_oel=lambda **_kwargs: None,
        dlt_oel=lambda **_kwargs: records.clear(),
    )
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.delete_oel(_node(OpticalNodeRole.ROADM, "flex.a"), "cid")

    assert result == {"---": {"root['OEL']['AID']": "cid", "root['OEL']['OPERSTATE']": "IS"}, "+++": {}}


def test_delete_oel_is_a_noop_when_the_oel_is_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing OEL yields an empty diff and is never deleted, so a retry is safe."""
    deleted: list[str] = []
    flex = SimpleNamespace(
        rtrv_oel=lambda **_kwargs: SimpleNamespace(parsed_data=[]),
        rtrv_osnc=lambda **_kwargs: SimpleNamespace(parsed_data=[]),
        dlt_oel=lambda **kwargs: deleted.append(kwargs["aid"]),
    )
    monkeypatch.setattr(flexils_spectrum, "_get_flex_client", lambda _device: flex)

    result = flexils_spectrum.delete_oel(_node(OpticalNodeRole.ROADM, "flex.a"), "cid")

    assert result == {"---": {}, "+++": {}}
    assert deleted == []


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
