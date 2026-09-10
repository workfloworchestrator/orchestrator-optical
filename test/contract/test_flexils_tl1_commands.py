"""Contract tests for the Nokia FlexILS TL1 parser, serializer and command registry.

These tests pin the device-facing contract of the TL1 layer: how raw device
responses are parsed (``TL1BaseResponse.from_raw_text``), how command objects are
rendered into TL1 strings (``TL1BaseCommand.to_string``), how command classes are
registered and looked up (``TL1CommandRegistry``) and how a representative subset
of concrete commands (OEL/OSNC/OCRS/EQPT) parses canned device output.

No SSH, network or database is involved: every input is a canned string.
"""

import pytest

from orchestrator.optical.services.nokia.flexils.commands.base import (
    TL1BaseCommand,
    TL1BaseResponse,
    TL1CommandRegistry,
)
from orchestrator.optical.services.nokia.flexils.commands.eqpt import RetrieveEqpt
from orchestrator.optical.services.nokia.flexils.commands.ocrs import (
    DeleteOcrs,
    EditOcrs,
    EnterOcrs,
    OcrsResponse,
    RetrieveOcrs,
)
from orchestrator.optical.services.nokia.flexils.commands.oel import (
    EditOel,
    EnterOel,
    OelResponse,
    OperateValrouteOel,
    RetrieveOel,
)
from orchestrator.optical.services.nokia.flexils.commands.osnc import (
    DeleteOsnc,
    EditOsnc,
    EnterOsnc,
    OsncResponse,
    RetrieveOsnc,
)
from orchestrator.optical.services.nokia.flexils.exceptions import TL1CommandDeniedError
from orchestrator.optical.services.nokia.flexils.utils import TL1CompletionStatus

TAG = "WFOTAG"

# The commands exercised in this module, keyed by the registry name (i.e. the
# method the client binds dynamically from ``verb`` + ``modifier``).
REGISTERED_COMMANDS: dict[str, type[TL1BaseCommand]] = {
    "opr_valroute_oel": OperateValrouteOel,
    "rtrv_oel": RetrieveOel,
    "ent_oel": EnterOel,
    "ed_oel": EditOel,
    "rtrv_osnc": RetrieveOsnc,
    "ent_osnc": EnterOsnc,
    "ed_osnc": EditOsnc,
    "dlt_osnc": DeleteOsnc,
    "rtrv_ocrs": RetrieveOcrs,
    "ent_ocrs": EnterOcrs,
    "ed_ocrs": EditOcrs,
    "dlt_ocrs": DeleteOcrs,
    "rtrv_eqpt": RetrieveEqpt,
}


def _tl1_response(records: list[str], *, status: str = "COMPLD", tag: str = TAG, sid: str = "flex.bo01") -> str:
    """Build a raw TL1 response from record lines (mirrors what the device emits)."""
    payload = "\n".join(f'"{record}"' for record in records)
    return f"{sid} 25-10-27 16:45:12\nM  {tag} {status}\n{payload}\n;\n"


OEL_RESPONSE = _tl1_response(["1-A-1-L1:OEL:1-A-1-L1:IS-NR:LABEL=foo"])
OSNC_RESPONSE = _tl1_response(
    ["1-A-1-L1-1:OSNC:LABEL=some,OELAID=bo01-ba01,REMENDPOINT=1-Z-1-L1-1,REMNODETID=flex.ba01,CKTIDSUFFIX=abc:IS-NR"]
)
OCRS_RESPONSE = _tl1_response(
    [
        "1-E1-1-T2A-1,1-A-1-L1-1:2WAY:LABEL=f099c99,SIGTYPE=SIGNALED,CKTIDSUFFIX=OCh099_bo01-ba01,"
        "PASSBANDLIST=193450000&193550000,CARRIERLIST=193500000&37500:IS-NR"
    ]
)


class _FakeTransportClient:
    """Duck-typed ``FlexilsClient`` that records commands and replays a canned response."""

    tid = "flex.bo01"

    def __init__(self, raw_response: str) -> None:
        self.raw_response = raw_response
        self.commands: list[tuple[str, str]] = []

    def execute_raw_command(self, command: str, correlation_tag: str) -> str:
        self.commands.append((command, correlation_tag))
        return self.raw_response


# ---------------------------------------------------------------------------
# TL1BaseResponse.from_raw_text — pure parser
# ---------------------------------------------------------------------------


def test_from_raw_text_parses_success_single_record() -> None:
    response = TL1BaseResponse.from_raw_text(OEL_RESPONSE, TAG)
    assert response.status == TL1CompletionStatus.COMPLD
    assert response.ctag == TAG
    assert response.parsed_data == [
        {
            "positional_param_0_0": "1-A-1-L1",
            "positional_param_1_0": "OEL",
            "positional_param_2_0": "1-A-1-L1",
            "positional_param_3_0": "IS-NR",
            "LABEL": "foo",
        }
    ]


def test_from_raw_text_parses_multiline_payload() -> None:
    raw = _tl1_response(
        [
            "1-A-1-L1:OEL:1-A-1-L1:IS-NR:LABEL=foo",
            "1-A-2-L1:OEL:1-A-2-L1:OOS:LABEL=bar",
        ]
    )
    response = TL1BaseResponse.from_raw_text(raw, TAG)
    assert len(response.parsed_data) == 2
    assert [record["LABEL"] for record in response.parsed_data] == ["foo", "bar"]
    assert response.parsed_data[1]["positional_param_3_0"] == "OOS"


def test_from_raw_text_parses_deny_without_records() -> None:
    raw = f"flex.bo01 25-10-27 16:45:12\nM  {TAG} DENY\n   /*   Input, Invalid Value, aid */\n;\n"
    response = TL1BaseResponse.from_raw_text(raw, TAG)
    assert response.status == TL1CompletionStatus.DENY
    assert response.parsed_data == []
    assert "DENY" in response.raw_data


def test_from_raw_text_raises_without_tag() -> None:
    with pytest.raises(ValueError, match=f"Could not find tag {TAG}"):
        TL1BaseResponse.from_raw_text("flex.bo01 25-10-27 16:45:12\nM  OTHER COMPLD\n;\n", TAG)


def test_from_raw_text_parses_ampersand_lists() -> None:
    raw = _tl1_response(["X:LABEL=a&b,CARRIERLIST=1&2&-3&4"])
    response = TL1BaseResponse.from_raw_text(raw, TAG)
    assert response.parsed_data[0]["LABEL"] == ["a", "b"]
    assert response.parsed_data[0]["CARRIERLIST"] == [["1", "2"], ["3", "4"]]


# ---------------------------------------------------------------------------
# TL1BaseCommand.to_string — pure serializer
# ---------------------------------------------------------------------------


def test_to_string_omits_absent_optional_positional() -> None:
    assert RetrieveOel(tid="flex.bo01", ctag=TAG).to_string() == f"RTRV-OEL:flex.bo01::{TAG}::::;"


def test_to_string_includes_present_positional() -> None:
    command = RetrieveOel(tid="flex.bo01", aid="1-A-1-L1", ctag=TAG)
    assert command.to_string() == f"RTRV-OEL:flex.bo01:1-A-1-L1:{TAG}::::;"


def test_to_string_renders_action_command() -> None:
    command = OperateValrouteOel(tid="flex.bo01", aid="1-A-1-L1", ctag=TAG)
    assert command.to_string() == f"OPR-VALROUTE-OEL:flex.bo01:1-A-1-L1:{TAG}::::;"


def test_to_string_renders_osnc_delete() -> None:
    command = DeleteOsnc(tid="flex.bo01", aid="1-A-1-L1-1", ctag=TAG)
    assert command.to_string() == f"DLT-OSNC:flex.bo01:1-A-1-L1-1:{TAG}::::;"


def test_to_string_renders_ocrs_comma_separated_positional() -> None:
    command = RetrieveOcrs(tid="flex.bo01", fromaid="1-E1-1-T2A-1", toaid="1-A-1-L1-1", ctag=TAG)
    assert command.to_string() == f"RTRV-OCRS:flex.bo01:1-E1-1-T2A-1,1-A-1-L1-1:{TAG}::::;"


def test_to_string_renders_eqpt_retrieve() -> None:
    command = RetrieveEqpt(tid="flex.bo01", aid="1-A-1", ctag=TAG)
    assert command.to_string() == f"RTRV-EQPT:flex.bo01:1-A-1:{TAG}::::;"


def test_to_string_renders_edit_oel_named_params() -> None:
    command = EditOel(tid="flex.bo01", aid="1-A-1-L1", label="my label", ctag=TAG)
    assert command.to_string() == f"ED-OEL:flex.bo01:1-A-1-L1:{TAG}:::LABEL=my label:;"


def test_to_string_joins_flat_lists_with_ampersand() -> None:
    command = EnterOel(
        tid="flex.bo01",
        aid="1-A-1-L1",
        ctag=TAG,
        explicitroute=[("flex.bo01", "1-A-2-L1", "flex.ba01", "1-A-1-L1")],
        label="OCh001",
        srcnodename="flex.bo01",
        dstnodename="flex.ba01",
        validfrangelist=[193450000, 193550000],
    )
    assert "VALIDFRANGELIST=193450000&193550000" in command.to_string()
    assert "EXPLICITROUTE=flex.bo01&1-A-2-L1&flex.ba01&1-A-1-L1" in command.to_string()


def test_to_string_renders_full_enter_oel() -> None:
    command = EnterOel(
        tid="flex.bo01",
        aid="1-A-1-L1",
        ctag=TAG,
        explicitroute=[("flex.bo01", "1-A-2-L1", "flex.ba01", "1-A-1-L1")],
        label="OCh001",
        srcnodename="flex.bo01",
        dstnodename="flex.ba01",
        validfrangelist=[193450000, 193550000],
    )
    assert command.to_string() == (
        f"ENT-OEL:flex.bo01:1-A-1-L1:{TAG}:::LABEL=OCh001,SRCNODENAME=flex.bo01,DSTNODENAME=flex.ba01,"
        "MODULATION=PM-NONE,ENCODMOD=None,RATE=NA,SPECTYPE=NA,CARDTYPE=UNKNOWN,"
        "FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE,COMPCARDTYPELIST=UNKNOWN,"
        "VALIDFRANGELIST=193450000&193550000,SRCPOWEROFFSET=0,DSTPOWEROFFSET=0,"
        "EXPLICITROUTE=flex.bo01&1-A-2-L1&flex.ba01&1-A-1-L1,OELSOURCE=MANUAL,GAURDBAND=0,"
        "NUMFECITRNS=4:IS;"
    )


def test_to_string_renders_full_enter_ocrs() -> None:
    command = EnterOcrs(
        tid="flex.bo01",
        fromaid="1-E1-1-T2A-1",
        toaid="1-A-1-L1-1",
        ctag=TAG,
        freqslotplantype="FREQ-SLOT-PLAN-NONE",
    )
    assert command.to_string() == (
        f"ENT-OCRS:flex.bo01:1-E1-1-T2A-1,1-A-1-L1-1:{TAG}:::FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE;"
    )


def test_to_string_renders_enter_osnc_flat_lists() -> None:
    command = EnterOsnc(
        tid="flex.bo01",
        aid="1-A-1-L1-1",
        ctag=TAG,
        cktidsuffix="abc",
        label="lab",
        remendpoint="1-Z-1-L1-1",
        remnodetid="flex.ba01",
        oelaid="bo01-ba01",
        passbandlist=[193450000, 193550000],
        carrierlist=[193500000, 37500],
    )
    text = command.to_string()
    assert text.startswith(f"ENT-OSNC:flex.bo01:1-A-1-L1-1:{TAG}:::")
    assert "CKTIDSUFFIX=abc" in text
    assert "PASSBANDLIST=193450000&193550000" in text
    assert "CARRIERLIST=193500000&37500" in text


# ---------------------------------------------------------------------------
# TL1CommandRegistry / TL1CommandMeta — registration and lookup
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("method_name", "command_class"), sorted(REGISTERED_COMMANDS.items()))
def test_concrete_commands_register_under_verb_modifier(method_name: str, command_class: type[TL1BaseCommand]) -> None:
    assert TL1CommandRegistry.commands[method_name] is command_class


def test_every_registry_key_is_derived_from_verb_and_modifier() -> None:
    for method_name, command_class in TL1CommandRegistry.commands.items():
        expected = f"{command_class.verb.lower()}_{command_class.modifier.lower().replace('-', '_')}"
        assert method_name == expected


def test_representative_command_families_are_discoverable() -> None:
    assert {
        "opr_valroute_oel",
        "rtrv_oel",
        "ent_oel",
        "rtrv_osnc",
        "ent_osnc",
        "rtrv_ocrs",
        "ent_ocrs",
        "rtrv_eqpt",
    } <= set(TL1CommandRegistry.commands)


def test_base_command_is_not_registered() -> None:
    assert TL1BaseCommand not in TL1CommandRegistry.commands.values()


# ---------------------------------------------------------------------------
# Concrete commands: response model wiring and parsing
# ---------------------------------------------------------------------------


def test_retrieve_oel_wires_oel_response_class() -> None:
    assert RetrieveOel.response_class is OelResponse


def test_oel_response_renames_positional_params() -> None:
    response = OelResponse.from_raw_text(OEL_RESPONSE, TAG)
    record = response.parsed_data[0]
    assert record["AID"] == "1-A-1-L1"
    assert record["RESOURCETYPE"] == "OEL"
    assert record["OPERSTATE"] == "IS-NR"
    assert record["LABEL"] == "foo"


def test_retrieve_osnc_wires_osnc_response_class() -> None:
    assert RetrieveOsnc.response_class is OsncResponse


def test_osnc_response_renames_positional_params() -> None:
    response = OsncResponse.from_raw_text(OSNC_RESPONSE, TAG)
    record = response.parsed_data[0]
    assert record["LOCENDPOINT"] == "1-A-1-L1-1"
    assert record["OPERSTATE"] == "IS-NR"
    assert record["REMENDPOINT"] == "1-Z-1-L1-1"
    assert record["CKTIDSUFFIX"] == "abc"


def test_retrieve_ocrs_wires_ocrs_response_class() -> None:
    assert RetrieveOcrs.response_class is OcrsResponse


def test_ocrs_response_renames_positional_params() -> None:
    response = OcrsResponse.from_raw_text(OCRS_RESPONSE, TAG)
    record = response.parsed_data[0]
    assert record["FROMAID"] == "1-E1-1-T2A-1"
    assert record["TOAID"] == "1-A-1-L1-1"
    assert record["CrossConnectType"] == "2WAY"
    assert record["OPERSTATE"] == "IS-NR"
    assert record["CKTIDSUFFIX"] == "OCh099_bo01-ba01"
    assert record["PASSBANDLIST"] == ["193450000", "193550000"]


# ---------------------------------------------------------------------------
# TL1BaseCommand.execute — device call and response handling
# ---------------------------------------------------------------------------


def test_command_execute_sends_rendered_string_and_parses_response() -> None:
    client = _FakeTransportClient(OEL_RESPONSE)
    command = RetrieveOel(tid="flex.bo01", aid="1-A-1-L1", ctag=TAG)
    response = command.execute(client)
    assert client.commands == [(f"RTRV-OEL:flex.bo01:1-A-1-L1:{TAG}::::;", TAG)]
    assert response.status == TL1CompletionStatus.COMPLD
    assert response.parsed_data[0]["AID"] == "1-A-1-L1"


def test_command_execute_raises_on_deny() -> None:
    client = _FakeTransportClient(_tl1_response([], status="DENY"))
    with pytest.raises(TL1CommandDeniedError):
        RetrieveOel(tid="flex.bo01", ctag=TAG).execute(client)


def test_command_execute_tolerates_already_present() -> None:
    raw = f"flex.bo01 25-10-27 16:45:12\nM  {TAG} COMPLD\n/* ALREADY EXISTS */\n;\n"
    client = _FakeTransportClient(raw)
    response = RetrieveOel(tid="flex.bo01", ctag=TAG).execute(client)
    assert response.status == TL1CompletionStatus.COMPLD


def test_command_response_class_is_base_response_by_default() -> None:
    assert DeleteOcrs.response_class is TL1BaseResponse
