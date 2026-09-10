"""Contract tests for ``FlexilsClient`` command execution without SSH.

The SSH transport is faked at the documented seams: ``_send_and_receive_until``
for the raw command exchange and ``execute_raw_command`` for the command layer.
No socket, device or database is touched; settings are read lazily and no
credentials are required to construct a client.
"""

import pytest

from orchestrator.optical.services.nokia.flexils.client import FlexilsClient
from orchestrator.optical.services.nokia.flexils.utils import TL1CompletionStatus

TID = "flex.bo01"
GNE_IP = "10.0.0.1"


def _client() -> FlexilsClient:
    return FlexilsClient(tid=TID, gne_ip=GNE_IP)


def _response(record: str, *, tag: str = "WFOTAG", status: str = "COMPLD") -> str:
    return f'{TID} 25-10-27 16:45:12\nM  {tag} {status}\n"{record}"\n;\n'


def test_client_binds_registry_commands() -> None:
    client = _client()
    for method_name in ("rtrv_oel", "rtrv_osnc", "rtrv_ocrs", "ent_oel", "rtrv_eqpt", "put_maintenance"):
        assert callable(getattr(client, method_name))


def test_bound_command_renders_and_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client()
    seen: list[tuple[str, str]] = []

    def fake_execute(command: str, correlation_tag: str) -> str:
        seen.append((command, correlation_tag))
        return _response("1-A-1-L1:OEL:1-A-1-L1:IS-NR:LABEL=foo")

    monkeypatch.setattr(client, "execute_raw_command", fake_execute)
    response = client.rtrv_oel(aid="1-A-1-L1", ctag="WFOTAG")

    assert seen == [(f"RTRV-OEL:{TID}:1-A-1-L1:WFOTAG::::;", "WFOTAG")]
    assert response.status == TL1CompletionStatus.COMPLD
    assert response.parsed_data[0]["AID"] == "1-A-1-L1"


def test_execute_command_rejects_tid_kwarg() -> None:
    client = _client()
    with pytest.raises(ValueError, match="Passing 'tid'"):
        client.rtrv_oel(tid="other-node", ctag="WFOTAG")


def test_execute_raw_command_strips_echo_and_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client()
    captured: list[tuple[str, list[str]]] = []
    command = f"RTRV-OEL:{TID}::WFOTAG::::;"

    def fake_send(cmd: str, until: list[str]) -> str:
        captured.append((cmd, until))
        return f'{command}\r\nM  WFOTAG COMPLD\r\n"1-A-1-L1:OEL:1-A-1-L1:IS-NR"\r\nTL1>>'

    monkeypatch.setattr(client, "_send_and_receive_until", fake_send)
    stdout = client.execute_raw_command(command, "WFOTAG")

    assert stdout == 'M  WFOTAG COMPLD\r\n"1-A-1-L1:OEL:1-A-1-L1:IS-NR"\r\n'
    assert captured[0][1] == ["WFOTAG COMPLD", "WFOTAG DENY", "WFOTAG PRTL", "M  0 DENY"]


def test_execute_raw_command_reauthenticates_on_login_not_active(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client()
    sent: list[str] = []
    command = f"RTRV-OEL:{TID}::WFOTAG::::;"

    def fake_send(cmd: str, until: list[str]) -> str:
        sent.append(cmd)
        if cmd == command and sent.count(command) == 1:
            return "PRIVILEGE, LOGIN NOT ACTIVE\r\nTL1>>"
        if cmd == command:
            return f'{command}\r\nM  WFOTAG COMPLD\r\n"x"\r\nTL1>>'
        return "M  X COMPLD\r\nTL1>>"

    monkeypatch.setattr(client, "_send_and_receive_until", fake_send)
    stdout = client.execute_raw_command(command, "WFOTAG")

    assert stdout == 'M  WFOTAG COMPLD\r\n"x"\r\n'
    assert sent[0] == command
    assert sent[1].startswith("ACT-USER:")
    assert sent[2].startswith("INH-MSG-ALL:")
    assert sent[3] == command


def test_connect_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client()
    monkeypatch.setattr(client, "_username", None)
    monkeypatch.setattr(client, "_password", None)
    with pytest.raises(RuntimeError, match="OPTICAL_FLEXILS_USER"):
        client._connect()  # noqa: SLF001
