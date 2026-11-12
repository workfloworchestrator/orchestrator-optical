"""Contract tests of the Nokia FlexILS adapter on the TL1 wire (no device).

The real generated SDK (``flexils_tl1``) runs against its scripted transport, so these
tests pin the two things the adapter depends on and a regenerated SDK could move: the
exact bytes of every command the adapter sends, and the records it reads back. The
commands marked *as the hand-written client* are byte-identical to what the previous
client sent to production nodes; the others only lost trailing empty blocks.
"""

import pytest

pytest.importorskip("flexils_tl1")

from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

from flexils_tl1 import TL1DeniedError
from flexils_tl1.generated.responses import (
    RtrvEqptResponse,
    RtrvOcrsResponse,
    RtrvOsncResponse,
    RtrvOtelinkResponse,
)

from orchestrator.optical.hal.adapters.nokia_flexils import port as flexils_port
from orchestrator.optical.hal.adapters.nokia_flexils import spectrum as flexils_spectrum
from orchestrator.optical.hal.adapters.nokia_flexils import transponder as flexils_transponder
from orchestrator.optical.hal.adapters.nokia_flexils._shared import (
    FlexilsClient,
    _is_object_missing,
    _records,
    _tl1_list,
    _tl1_quoted,
)
from orchestrator.optical.hal.adapters.nokia_flexils.spectrum import _OEL_DEFAULTS, _OSNC_DEFAULTS
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import OpticalPipeType
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from test.support.tl1 import CTAG, GNE_IP, TID, ScriptedClient, parsed_records, reply, scripted_client

pytestmark = pytest.mark.contract

LINE, TRIB, SYSTEM = "1-A-1-L1", "1-A-1-T1", "1-A-1-S1"
SCH = f"{TRIB}-1"
PASSBAND, CARRIER = (191_350_000, 191_400_000), (191_375_000, 50_000)
ROUTE = [("flex.a", "1-A-2-L1", "flex.c", "1-A-1-L1"), ("flex.c", "1-A-2-L1", "flex.b", "1-A-1-L1")]


def _wire(head: str, tail: str = "") -> str:
    """Build the expected message ``<VERB-MOD>:<tid>:<aid>:<ctag><tail>;`` from ``<VERB-MOD>:<aid>``."""
    command, _, aid = head.partition(":")
    return f"{command}:{TID}:{aid}:{CTAG}{tail};"


_OSNC_TAIL = (
    "RESTORABLE=NONE,CKTIDSUFFIX=cid,PREPROV=TRUE,PASSBANDLIST=191350000&191400000,"
    "CARRIERLIST=191375000&50000,AUTORETUNELMSCH=DISABLED,SRCRXSCHOFFSET=0,DSTRXSCHOFFSET=0,FAULTSOAKTIMER=5,"
    "BAUDRATE=NA,MODULATION=PM-NONE,FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE,SRCSCHPOWEROFFSET=0,DSTSCHPOWEROFFSET=0,"
    "ROUTETYPE=OEL,INTRACARRSPECSHAPING=ENABLED,DIGITRIGGER=FALSE,RESTORATIONTRIGGER=OPTICALSF:IS"
)
_OEL_TAIL = (
    "LABEL=flex.a-flex.b,SRCNODENAME=flex.a,DSTNODENAME=flex.b,MODULATION=PM-NONE,ENCODMOD=None,RATE=NA,"
    "SPECTYPE=NA,CARDTYPE=UNKNOWN,FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE,COMPCARDTYPELIST=UNKNOWN,"
    "VALIDFRANGELIST=191325000&196125000,SRCPOWEROFFSET=0,DSTPOWEROFFSET=0,"
    "EXPLICITROUTE=flex.a&1-A-2-L1&flex.c&1-A-1-L1&-flex.c&1-A-2-L1&flex.b&1-A-1-L1,"
    "OELSOURCE=manual,GAURDBAND=0,NUMFECITRNS=4:IS"
)
_OCRS_TAIL = (
    "CKTIDSUFFIX=cid,FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE,SCHOFFSET=0,PASSBANDLIST=191350000&191400000,"
    "CARRIERLIST=191375000&50000,AUTORETUNELMSCH=DISABLED,INTRACARRSPECSHAPING=ENABLED"
)

#: Every command shape the adapter sends: ``(call, expected wire)``.
COMMANDS: dict[str, tuple[Callable[[FlexilsClient], Any], str]] = {
    # --- retrieves: trailing empty blocks are no longer sent
    "rtrv-toponode": (lambda c: c.rtrv_toponode(), _wire("RTRV-TOPONODE:")),
    "rtrv-sys": (lambda c: c.rtrv_sys(), _wire("RTRV-SYS:")),
    "rtrv-otelink": (lambda c: c.rtrv_otelink(), _wire("RTRV-OTELINK:")),
    "rtrv-oteintf": (lambda c: c.rtrv_oteintf(), _wire("RTRV-OTEINTF:")),
    "rtrv-ots": (lambda c: c.rtrv_ots(), _wire("RTRV-OTS:")),
    "rtrv-ots-aid": (lambda c: c.rtrv_ots(aid=LINE), _wire(f"RTRV-OTS:{LINE}")),
    "rtrv-oel": (lambda c: c.rtrv_oel(aid="cid"), _wire("RTRV-OEL:cid")),
    "rtrv-osnc": (lambda c: c.rtrv_osnc(), _wire("RTRV-OSNC:", ":::")),
    "rtrv-osnc-aid": (lambda c: c.rtrv_osnc(aid=SCH), _wire(f"RTRV-OSNC:{SCH}", ":::")),
    "rtrv-sch": (lambda c: c.rtrv_sch(aid=SCH), _wire(f"RTRV-SCH:{SCH}")),
    "rtrv-ocrs": (lambda c: c.rtrv_ocrs(), _wire("RTRV-OCRS:", ":::")),
    "rtrv-ocrs-signaled": (lambda c: c.rtrv_ocrs(sigtype="SIGNALED"), _wire("RTRV-OCRS:", ":::SIGTYPE=SIGNALED")),
    "rtrv-ocrs-aids": (
        lambda c: c.rtrv_ocrs(fromaid=f"{SYSTEM}-1", toaid=SCH),
        _wire(f"RTRV-OCRS:{SYSTEM}-1,{SCH}", ":::"),
    ),
    # --- as the hand-written client
    "rtrv-eqpt": (lambda c: c.rtrv_eqpt(), _wire("RTRV-EQPT:", "::::")),
    "rtrv-eqpt-aid": (lambda c: c.rtrv_eqpt(aid="1-A-1"), _wire("RTRV-EQPT:1-A-1", "::::")),
    "rtrv-scg": (lambda c: c.rtrv_scg(), _wire("RTRV-SCG:", "::::")),
    "rtrv-scg-aid": (lambda c: c.rtrv_scg(aid=TRIB), _wire(f"RTRV-SCG:{TRIB}", "::::")),
    "rtrv-pm-sch": (lambda c: c.rtrv_pm("SCH", SCH, montype="OPR"), _wire(f"RTRV-PM-SCH:{SCH}", "::OPR::")),
    "ed-ots-label": (
        lambda c: c.ed_ots(aid=LINE, label=_tl1_quoted("my span"), histstats="ENABLE"),
        _wire(f"ED-OTS:{LINE}", ':::LABEL="my span",HISTSTATS=ENABLE'),
    ),
    "ed-ots-clear-label": (lambda c: c.ed_ots(aid=LINE, label=_tl1_quoted("")), _wire(f"ED-OTS:{LINE}", ':::LABEL=""')),
    "ed-scg-in-service": (lambda c: c.ed_scg(aid=TRIB, pst="IS"), _wire(f"ED-SCG:{TRIB}", "::::IS")),
    "ed-scg-out-of-service": (lambda c: c.ed_scg(aid=TRIB, pst="OOS"), _wire(f"ED-SCG:{TRIB}", "::::OOS")),
    "ed-scg-manualmode": (
        lambda c: c.ed_scg(aid=TRIB, intftyp="MANUALMODE-2"),
        _wire(f"ED-SCG:{TRIB}", ":::INTFTYP=MANUALMODE-2:"),
    ),
    "ed-scg-termination": (
        lambda c: c.ed_scg(aid=TRIB, provowremptp="SN1/1-2-L1", label=_tl1_quoted("patch"), histstats="ENABLE"),
        _wire(f"ED-SCG:{TRIB}", ':::LABEL="patch",HISTSTATS=ENABLE,PROVOWREMPTP=SN1/1-2-L1:'),
    ),
    "ed-scg-reset": (
        lambda c: c.ed_scg(aid=TRIB, intftyp="MANUALMODE-2", provowremptp=_tl1_quoted(""), label=_tl1_quoted("")),
        _wire(f"ED-SCG:{TRIB}", ':::LABEL="",INTFTYP=MANUALMODE-2,PROVOWREMPTP="":'),
    ),
    "rmv-ots": (lambda c: c.rmv(aidtype="OTS", aid=LINE), _wire(f"RMV-OTS:{LINE}", "::")),
    "rst-ots": (lambda c: c.rst(aidtype="OTS", aid=LINE), _wire(f"RST-OTS:{LINE}", "::::")),
    "rmv-scg": (lambda c: c.rmv(aidtype="SCG", aid=TRIB), _wire(f"RMV-SCG:{TRIB}", "::")),
    "rst-scg": (lambda c: c.rst(aidtype="SCG", aid=TRIB), _wire(f"RST-SCG:{TRIB}", "::::")),
    "rmv-sch": (lambda c: c.rmv("SCH", SCH), _wire(f"RMV-SCH:{SCH}", "::")),
    "rst-sch": (lambda c: c.rst("SCH", SCH), _wire(f"RST-SCH:{SCH}", "::::")),
    "ed-sch-shutter": (
        lambda c: c.ed_sch(aid=SCH, shutterstate="OPEN"),
        _wire(f"ED-SCH:{SCH}", ":::SHUTTERSTATE=OPEN:"),
    ),
    "ed-oel-lock": (lambda c: c.ed_oel(aid="cid", srcnodename="OOS"), _wire("ED-OEL:cid", "::::OOS")),
    "ent-osnc": (
        lambda c: c.ent_osnc(
            aid=SCH,
            label=_tl1_quoted("ch: a + b"),
            remnodetid="flex.b",
            remendpoint="1-A-3-T2-1",
            oelaid="cid",
            cktidsuffix="cid",
            passbandlist=_tl1_list(PASSBAND),
            carrierlist=_tl1_list(CARRIER),
            **_OSNC_DEFAULTS,
        ),
        _wire(
            f"ENT-OSNC:{SCH}",
            f':::LABEL="ch: a + b",REMENDPOINT=1-A-3-T2-1,REMNODETID=flex.b,OELAID=cid,{_OSNC_TAIL}',
        ),
    ),
    "ed-osnc-lock": (lambda c: c.ed_osnc(aid=SCH, pst="OOS"), _wire(f"ED-OSNC:{SCH}", "::::OOS")),
    "ed-osnc-locked-params": (
        lambda c: c.ed_osnc(
            aid=SCH, pst="OOS", oelaid="cid", passbandlist=_tl1_list(PASSBAND), carrierlist=_tl1_list(CARRIER)
        ),
        _wire(f"ED-OSNC:{SCH}", ":::OELAID=cid,PASSBANDLIST=191350000&191400000,CARRIERLIST=191375000&50000:OOS"),
    ),
    "ed-osnc-unlock": (
        lambda c: c.ed_osnc(aid=SCH, cktidsuffix="cid", pst="IS", label=_tl1_quoted("ch: a + b")),
        _wire(f"ED-OSNC:{SCH}", ':::LABEL="ch: a + b",CKTIDSUFFIX=cid:IS'),
    ),
    "ed-osnc-label": (
        lambda c: c.ed_osnc(aid=SCH, label=_tl1_quoted("ch: a + b")),
        _wire(f"ED-OSNC:{SCH}", ':::LABEL="ch: a + b":'),
    ),
    "ent-ocrs": (
        lambda c: c.ent_ocrs(
            fromaid=f"{SYSTEM}-1",
            toaid=SCH,
            label=_tl1_quoted("x y"),
            cktidsuffix="cid",
            freqslotplantype="FREQ-SLOT-PLAN-NONE",
            schoffset="0",
            passbandlist=_tl1_list(PASSBAND),
            carrierlist=_tl1_list(CARRIER),
            autoretunelmsch="DISABLED",
            intracarrspecshaping="ENABLED",
        ),
        _wire(f"ENT-OCRS:{SYSTEM}-1,{SCH}", f':::LABEL="x y",{_OCRS_TAIL}'),
    ),
    # --- as the hand-written client, less the trailing empty blocks (and ``OELSOURCE`` in the reference's case)
    "ent-oel": (
        lambda c: c.ent_oel(
            aid="cid",
            label="flex.a-flex.b",
            srcnodename="flex.a",
            dstnodename="flex.b",
            explicitroute=_tl1_list(ROUTE),
            validfrangelist=_tl1_list((191_325_000, 196_125_000)),
            **_OEL_DEFAULTS,
        ),
        _wire("ENT-OEL:cid", f":::{_OEL_TAIL}"),
    ),
    "opr-valroute-oel": (lambda c: c.opr_valroute_oel(aid="cid"), _wire("OPR-VALROUTE-OEL:cid")),
    "dlt-oel": (lambda c: c.dlt_oel(aid="cid"), _wire("DLT-OEL:cid")),
    "dlt-osnc": (lambda c: c.dlt_osnc(aid=SCH), _wire(f"DLT-OSNC:{SCH}")),
    "dlt-ocrs": (lambda c: c.dlt_ocrs(fromaid=f"{SYSTEM}-1", toaid=SCH), _wire(f"DLT-OCRS:{SYSTEM}-1,{SCH}")),
}


@pytest.mark.parametrize(("call", "expected"), COMMANDS.values(), ids=COMMANDS.keys())
def test_command_wire(call: Callable[[FlexilsClient], Any], expected: str) -> None:
    """The SDK renders each command of the adapter into exactly these bytes."""
    with scripted_client() as client:
        call(client)

        assert client.sent == [expected]


def test_session_logs_in_and_inhibits_messages_before_the_first_command() -> None:
    with scripted_client() as client:
        client.rtrv_sys()

        login, inhibit, command = client.transport.sent
    assert login.startswith(f"ACT-USER:{TID}:user:{CTAG}::")
    assert inhibit == f"INH-MSG-ALL:{TID}::{CTAG}::;"
    assert command == _wire("RTRV-SYS:")


def test_client_exposes_the_node_it_targets() -> None:
    with scripted_client(tid="flex.a") as client:
        assert (client.tid, client.gne_ip) == ("flex.a", GNE_IP)


# ---------------------------------------------------------------------------
# Records: what the adapter reads back
# ---------------------------------------------------------------------------


def test_records_are_keyed_by_wire_name_with_the_standard_slots_named() -> None:
    """The AID, the state slots and the list values of a record land under the keys the adapter reads."""
    (osnc,) = parsed_records(
        RtrvOsncResponse,
        [
            f'{SCH}:OSNC:LABEL=\\"ch: a + b\\",OELAID=cid,REMENDPOINT=1-Z-1-T1-1,REMNODETID=flex.b,CKTIDSUFFIX=cid,'
            "PASSBANDLIST=191350000&191400000,CARRIERLIST=191375000&50000,TAG=,NEWKEY=x:IS-NR,ACT"
        ],
    )

    assert osnc == {
        "AID": SCH,
        "TYPE": "OSNC",
        "PST": "IS-NR",
        "SST": "ACT",
        "LABEL": "ch: a + b",
        "OELAID": "cid",
        "REMENDPOINT": "1-Z-1-T1-1",
        "REMNODETID": "flex.b",
        "CKTIDSUFFIX": "cid",
        "PASSBANDLIST": ["191350000", "191400000"],
        "CARRIERLIST": ["191375000", "50000"],
        "TAG": "",  # sent empty: present and empty, not missing
        "NEWKEY": "x",  # a key the reference does not document is kept
    }


def test_ocrs_records_name_both_endpoints() -> None:
    (ocrs,) = parsed_records(
        RtrvOcrsResponse,
        [
            "1-E1-1-T2A-1,1-A-1-L1-1:2WAY:LABEL=f099c99,SIGTYPE=SIGNALED,CKTIDSUFFIX=cid,"
            "PASSBANDLIST=193450000&193550000,CARRIERLIST=193500000&37500:IS-NR"
        ],
    )

    assert (ocrs["FROMAID"], ocrs["TOAID"], ocrs["CCT"], ocrs["PST"]) == ("1-E1-1-T2A-1", "1-A-1-L1-1", "2WAY", "IS-NR")
    assert ocrs["PASSBANDLIST"] == ["193450000", "193550000"]
    assert ocrs["LABEL"] == "f099c99"


def test_eqpt_records_expose_the_card_type() -> None:
    cards = parsed_records(RtrvEqptResponse, ["1-A-1:FRM:SERNO=MA1234:IS-NR", "2-A-3:FSM:SERNO=MA5678:IS-NR"])

    assert [(card["AID"], card["TYPE"], card["SERNO"]) for card in cards] == [
        ("1-A-1", "FRM", "MA1234"),
        ("2-A-3", "FSM", "MA5678"),
    ]


def test_nested_list_values_are_split_in_groups() -> None:
    (link,) = parsed_records(
        RtrvOtelinkResponse,
        ["flex.a-1-A-1-L1::REACHSCOPE=Local,AVAILFREQRANGELIST=191325000&193000000&-194000000&196125000:IS-NR"],
    )

    assert link["AVAILFREQRANGELIST"] == [["191325000", "193000000"], ["194000000", "196125000"]]


def test_a_label_holding_an_ampersand_is_not_a_list() -> None:
    (osnc,) = parsed_records(RtrvOsncResponse, [f'{SCH}:OSNC:LABEL=\\"R&D link\\":IS-NR'])

    assert osnc["LABEL"] == "R&D link"


def test_no_records_reads_as_an_empty_list() -> None:
    with scripted_client() as client:
        assert _records(client.rtrv_osnc()) == []


# ---------------------------------------------------------------------------
# Denials
# ---------------------------------------------------------------------------


def test_denied_command_raises_with_the_raw_reply() -> None:
    denial = reply(status="DENY", error="Input, Invalid Value, aid")
    with scripted_client([("RTRV-OEL", denial)]) as client, pytest.raises(TL1DeniedError) as excinfo:
        client.rtrv_oel(aid="cid")

    assert "Input, Invalid Value, aid" in excinfo.value.raw
    assert not _is_object_missing(excinfo.value)


def test_missing_object_denial_is_recognised() -> None:
    denial = reply(status="DENY", error="Input, Specified Object Entity Does Not Exist")
    with scripted_client([("RTRV-SCH", denial)]) as client, pytest.raises(TL1DeniedError) as excinfo:
        client.rtrv_sch(aid=SCH)

    assert _is_object_missing(excinfo.value)


def test_denial_for_an_entity_already_in_the_requested_state_is_done() -> None:
    """Idempotent transitions: the node answering ALREADY is a success, and the command is not resent."""
    denial = reply(status="DENY", error="Status, ALREADY In Service")
    with scripted_client([("ED-SCG", denial)]) as client:
        response = client.ed_scg(aid=TRIB, pst="IS")

        assert client.sent == [_wire(f"ED-SCG:{TRIB}", "::::IS")]
    assert response.completion == "DENY"
    assert response.records == []


# ---------------------------------------------------------------------------
# Adapter flows on the wire
# ---------------------------------------------------------------------------


def _port(name: str, role: OpticalPortRole, description: str = "") -> Any:
    node = SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn="flex.bo01.example.net"))
    return SimpleNamespace(
        optical_port_host_node=node,
        optical_port_name=name,
        optical_port_role=role,
        optical_port_description=description,
    )


@pytest.fixture
def node() -> Any:
    return SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn="flex.bo01.example.net"))


def _drive(monkeypatch: pytest.MonkeyPatch, module: Any, client: ScriptedClient) -> None:
    """Make the adapter ``module`` reach its node through the scripted ``client``."""
    monkeypatch.setattr(module, "_get_flex_client", lambda _node: client)


def test_locking_a_tributary_port_in_maintenance_restores_it_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """SCG in maintenance: ED to IS is denied, so the port is restored (RST) and only then locked."""
    scg = [f"{TRIB}:SCG:LABEL=,INTFTYP=MANUALMODE-2:OOS-MA"]
    use_rst = reply(status="DENY", error="Status, use RST command to move out of maintenance")
    with scripted_client([("RTRV-SCG", reply(scg)), ("ED-SCG", use_rst), ("RTRV-SCG", reply(scg))]) as client:
        _drive(monkeypatch, flexils_port, client)

        flexils_port.set_port_admin_state(_port(TRIB, OpticalPortRole.OLS_ADD_DROP), "down")

        assert client.sent == [
            _wire(f"RTRV-SCG:{TRIB}", "::::"),
            _wire(f"ED-SCG:{TRIB}", "::::IS"),
            _wire(f"RST-SCG:{TRIB}", "::::"),
            _wire(f"ED-SCG:{TRIB}", "::::OOS"),
            _wire(f"RTRV-SCG:{TRIB}", "::::"),
        ]


def test_span_termination_and_reset_of_a_line_port(monkeypatch: pytest.MonkeyPatch) -> None:
    port = _port(LINE, OpticalPortRole.OLS_LINE, 'to "flex.ba01", span 1')
    before, after = [f"{LINE}:OTS:LABEL=,HISTSTATS=DISABLED:OOS-MA"], [f"{LINE}:OTS:LABEL=x,HISTSTATS=ENABLED:IS-NR"]
    with scripted_client([("RTRV-OTS", reply(before)), ("RTRV-OTS", reply(after))]) as client:
        _drive(monkeypatch, flexils_port, client)

        diff = flexils_port.configure_termination(port, port, OpticalPipeType.SPAN)
        flexils_port.factory_reset(port, port, OpticalPipeType.SPAN)

        assert client.sent[1:3] == [
            _wire(f"ED-OTS:{LINE}", ':::LABEL="to \\"flex.ba01\\", span 1",HISTSTATS=ENABLE'),
            _wire(f"RST-OTS:{LINE}", "::::"),
        ]
        assert client.sent[5] == _wire(f"ED-OTS:{LINE}", ':::LABEL=""')
    assert diff["---"][f"root[AID='{LINE}']['PST']"] == "OOS-MA"
    assert diff["+++"][f"root[AID='{LINE}']['PST']"] == "IS-NR"


def test_fiber_check_reads_the_line_port_state(monkeypatch: pytest.MonkeyPatch) -> None:
    port = _port(LINE, OpticalPortRole.OLS_LINE, "span 1")
    remote = _port("1-A-2-L1", OpticalPortRole.OLS_LINE)
    ots = f'{LINE}:OTS:LABEL=\\"span 1\\",PROVNBROTS=1-A-2-L1,DISCNBROTS=1-A-2-L1,HISTSTATS=ENABLED'
    with scripted_client([("RTRV-OTS", reply([f"{ots}:IS-NR"])), ("RTRV-OTS", reply([f"{ots}:OOS-MA"]))]) as client:
        _drive(monkeypatch, flexils_port, client)

        flexils_port.check_fiber(port, remote, OpticalPipeType.SPAN)
        with pytest.raises(ValueError, match="OOS-MA"):
            flexils_port.check_fiber(port, remote, OpticalPipeType.SPAN)


def test_entering_an_oel_validates_its_route(monkeypatch: pytest.MonkeyPatch, node: Any) -> None:
    missing = reply(status="DENY", error="Input, Specified Object Entity Does Not Exist")
    created = reply(["cid:OEL:LABEL=flex.a-flex.b,SRCNODENAME=flex.a:IS-NR"])
    with scripted_client([("RTRV-OEL", missing), ("RTRV-OEL", created)]) as client:
        _drive(monkeypatch, flexils_spectrum, client)
        monkeypatch.setattr(flexils_spectrum, "_node_id", lambda n: "flex.a" if n is node else "flex.b")
        monkeypatch.setattr(flexils_spectrum, "_explicit_route_from_omses", lambda _omses: ROUTE)

        oel = flexils_spectrum._find_or_create_oel("cid", node, object(), [])  # noqa: SLF001

        assert client.sent == [
            _wire("RTRV-OEL:cid"),
            _wire("ENT-OEL:cid", f":::{_OEL_TAIL}"),
            _wire("OPR-VALROUTE-OEL:cid"),
            _wire("RTRV-OEL:cid"),
        ]
    assert oel == {"AID": "cid", "TYPE": "OEL", "PST": "IS-NR", "LABEL": "flex.a-flex.b", "SRCNODENAME": "flex.a"}


def test_rx_power_delta_reads_the_superchannel_power(monkeypatch: pytest.MonkeyPatch, node: Any) -> None:
    replies = [
        ("RTRV-OCRS", reply([f"{SYSTEM}-1,{SCH}:2WAY:CKTIDSUFFIX=cid,INTERMEDIATESCHCTP={SYSTEM}-1:IS-NR"])),
        ("RTRV-EQPT", reply(["1-A-1:FRM:SERNO=MA1234:IS-NR"])),
        ("RTRV-SCH", reply([f"{SYSTEM}-1:SCH:TARGETOPR=-4.5:IS-NR"])),
        ("RTRV-PM-SCH", reply([f"{SYSTEM}-1,SCH:OPR,-3.2,CMPL,NEND,RCV,15-MIN,10-27,16-45"])),
    ]
    with scripted_client(replies) as client:
        _drive(monkeypatch, flexils_transponder, client)

        delta = flexils_transponder.delta_rx_power_vs_target(node, "spectrum", "cid")

        assert client.sent == [
            _wire("RTRV-OCRS:", ":::SIGTYPE=SIGNALED"),
            _wire("RTRV-EQPT:1-A-1", "::::"),
            _wire(f"RTRV-SCH:{SYSTEM}-1"),
            _wire(f"RTRV-PM-SCH:{SYSTEM}-1", "::OPR::"),
        ]
    assert delta == 1.3
