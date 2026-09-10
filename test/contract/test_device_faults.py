"""Fault-injection contract tests for the device-facing layers.

These tests pin down how the RESTCONF (G30/G42), TL1 (FlexILS) and TNMS clients behave
when a device misbehaves: connection timeout, HTTP 500, malformed payloads and denied
TL1 commands. They assert the *current* contract, including the places where a raw
``requests``/``json`` exception is leaked instead of being mapped to a domain error, so
that a silent change in error handling is caught by the regression net.
"""

import re
from types import SimpleNamespace
from typing import Any

import pytest
import requests
import responses
from requests.exceptions import JSONDecodeError

from orchestrator.optical.hal.adapters.nokia_groove_g30 import node as g30_node
from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as g42_node
from orchestrator.optical.services.nokia.flexils.commands.base import TL1BaseResponse
from orchestrator.optical.services.nokia.flexils.commands.eqpt import RetrieveEqpt
from orchestrator.optical.services.nokia.flexils.exceptions import TL1CommandDeniedError
from orchestrator.optical.services.nokia.flexils.utils import TL1CompletionStatus
from orchestrator.optical.services.nokia.g30.session_manager import RestconfClient as G30RestconfClient
from orchestrator.optical.services.nokia.g42.session_manager import RestconfClient as G42RestconfClient
from orchestrator.optical.services.nokia.tnms.client import TnmsClient
from orchestrator.optical.services.nokia.tnms.exceptions import ApiError

pytestmark = pytest.mark.contract

_RESTCONF_URL = "https://10.0.0.1:8181/restconf/data/contract-test"
_RESTCONF_URL_PATTERN = re.compile(r"https://10\.0\.0\.1:8181/restconf/.*")
_TNMS_URL = "https://tnms.example/api"
_AUTH_VALUE = "not-a-real-secret"

_RESTCONF_CLIENTS = [
    pytest.param(G30RestconfClient, id="g30"),
    pytest.param(G42RestconfClient, id="g42"),
]


def _restconf_client(client_cls: type) -> Any:
    """Build a RESTCONF client against a fake address; no connection is opened."""
    return client_cls(management_ip="10.0.0.1", username="user", password=_AUTH_VALUE)


class _FakeFlexilsClient:
    """Minimal FlexILS client exposing only the raw-command seam used by TL1BaseCommand."""

    def __init__(self, raw_response: str) -> None:
        self.tid = "FLEXILS"
        self._raw_response = raw_response

    def execute_raw_command(self, _command: str, _correlation_tag: str) -> str:
        return self._raw_response


@pytest.mark.parametrize("client_cls", _RESTCONF_CLIENTS)
@responses.activate
def test_restconf_connection_timeout_becomes_exception_group(client_cls: type) -> None:
    """A timeout on every endpoint surfaces as an ExceptionGroup of the transport errors."""
    client = _restconf_client(client_cls)
    responses.add(responses.GET, _RESTCONF_URL, body=requests.Timeout("simulated timeout"))

    with pytest.raises(ExceptionGroup, match="All connection attempts") as excinfo:
        client._request("GET", "/data/contract-test")  # noqa: SLF001

    assert any(isinstance(error, requests.Timeout) for error in excinfo.value.exceptions)


@pytest.mark.parametrize("client_cls", _RESTCONF_CLIENTS)
@responses.activate
def test_restconf_http_500_becomes_requests_http_error(client_cls: type) -> None:
    """An HTTP 500 is re-raised as requests.HTTPError carrying the status and the body."""
    client = _restconf_client(client_cls)
    responses.add(responses.GET, _RESTCONF_URL, status=500, body="upstream failure")

    with pytest.raises(requests.HTTPError) as excinfo:
        client._request("GET", "/data/contract-test")  # noqa: SLF001

    assert excinfo.value.response.status_code == 500
    assert "HTTP 500 Error" in str(excinfo.value)


@pytest.mark.parametrize("client_cls", _RESTCONF_CLIENTS)
@responses.activate
def test_restconf_malformed_json_leaks_raw_decode_error(client_cls: type) -> None:
    """A 2xx body that is not JSON currently leaks the raw JSONDecodeError instead of a domain error."""
    client = _restconf_client(client_cls)
    responses.add(
        responses.GET,
        _RESTCONF_URL,
        status=200,
        body="<html>not json</html>",
        content_type="application/json",
    )

    with pytest.raises(JSONDecodeError):
        client._request("GET", "/data/contract-test")  # noqa: SLF001


@responses.activate
def test_g30_adapter_surfaces_restconf_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """The G30 adapter does not swallow a RESTCONF HTTPError raised by the client."""
    client = _restconf_client(G30RestconfClient)
    monkeypatch.setattr(g30_node, "get_g30_client", lambda *_: client)
    responses.add(responses.GET, _RESTCONF_URL_PATTERN, status=500, body="boom")

    with pytest.raises(requests.HTTPError):
        g30_node.software_version(SimpleNamespace())


@responses.activate
def test_g42_adapter_surfaces_restconf_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """The G42 adapter does not swallow a RESTCONF HTTPError raised by the client."""
    client = _restconf_client(G42RestconfClient)
    monkeypatch.setattr(g42_node, "get_g42_client", lambda *_: client)
    responses.add(responses.GET, _RESTCONF_URL_PATTERN, status=500, body="boom")

    with pytest.raises(requests.HTTPError):
        g42_node.software_version(SimpleNamespace())


def test_tl1_parse_missing_tag_raises_value_error() -> None:
    """A response without the correlation tag is rejected with a ValueError."""
    with pytest.raises(ValueError, match="Could not find tag WFOTAG"):
        TL1BaseResponse.from_raw_text("M  OTHER COMPLD\n;\n", "WFOTAG")


def test_tl1_parse_missing_status_leaks_attribute_error() -> None:
    """A response whose tag is present but has no status word leaks AttributeError."""
    with pytest.raises(AttributeError, match="NoneType"):
        TL1BaseResponse.from_raw_text("WFOTAG", "WFOTAG")


def test_tl1_parse_unknown_status_raises_value_error() -> None:
    """An unrecognised completion status is rejected by the TL1CompletionStatus enum."""
    raw = "   FLEXILS\nM  WFOTAG BOGUS\n;\nTL1>>"

    with pytest.raises(ValueError, match="BOGUS"):
        TL1BaseResponse.from_raw_text(raw, "WFOTAG")


def test_tl1_denied_command_raises_typed_error() -> None:
    """A DENY response raises TL1CommandDeniedError carrying the tid and the raw response."""
    raw = '   FLEXILS\nM  WFOTAG DENY\n   "AID:TYPE::UP"\n;\nTL1>>'

    with pytest.raises(TL1CommandDeniedError) as excinfo:
        RetrieveEqpt(ctag="WFOTAG").execute(_FakeFlexilsClient(raw))

    assert excinfo.value.tid == "FLEXILS"
    assert "WFOTAG DENY" in excinfo.value.response


def test_tl1_deny_with_already_marker_is_tolerated() -> None:
    """A DENY that also carries ALREADY is parsed, not raised, keeping provisioning idempotent."""
    raw = '   FLEXILS\nM  WFOTAG DENY\n   "AID:TYPE::UP"\n;\n/* ALREADY provisioned */\nTL1>>'

    response = RetrieveEqpt(ctag="WFOTAG").execute(_FakeFlexilsClient(raw))

    assert response.status == TL1CompletionStatus.DENY


@responses.activate
def test_tnms_http_500_is_mapped_to_api_error() -> None:
    """A TNMS 500 response is wrapped into ApiError carrying the status code."""
    client = TnmsClient(user="user", password=_AUTH_VALUE, url=_TNMS_URL)
    responses.add(responses.GET, f"{_TNMS_URL}/data/contract-test", status=500, body="upstream failure")

    with pytest.raises(ApiError) as excinfo:
        client._request("GET", "/data/contract-test")  # noqa: SLF001

    assert excinfo.value.status_code == 500


@responses.activate
def test_tnms_malformed_body_leaks_raw_decode_error() -> None:
    """A non-JSON TNMS body currently leaks the raw JSONDecodeError instead of an ApiError."""
    client = TnmsClient(user="user", password=_AUTH_VALUE, url=_TNMS_URL)
    responses.add(
        responses.GET,
        f"{_TNMS_URL}/data/contract-test",
        status=200,
        body="not json",
        content_type="application/json",
    )

    with pytest.raises(JSONDecodeError):
        client._request("GET", "/data/contract-test")  # noqa: SLF001


@responses.activate
def test_tnms_401_triggers_reauth_and_retry() -> None:
    """A 401 triggers re-authentication and exactly one retry, returning the retried payload."""
    client = TnmsClient(user="user", password=_AUTH_VALUE, url=_TNMS_URL)
    responses.add(responses.POST, f"{_TNMS_URL}/auth", json={"token_type": "Bearer", "access_token": "token"})
    responses.add(responses.GET, f"{_TNMS_URL}/data/contract-test", status=401, body="expired")
    responses.add(responses.GET, f"{_TNMS_URL}/data/contract-test", json={"value": 1})

    assert client._request("GET", "/data/contract-test") == {"value": 1}  # noqa: SLF001
