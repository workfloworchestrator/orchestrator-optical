"""Contract tests for the Nokia TNMS TAPI client.

The TNMS client speaks TAPI RESTCONF over ``requests``. These tests pin the
request URLs, the response parsing and the exception mapping without a live
TNMS, by intercepting HTTP with ``responses``.
"""

import json

import pytest
import requests
import responses

from orchestrator.optical.services.nokia import get_tnms_client
from orchestrator.optical.services.nokia.tnms import endpoints as tnms_endpoints
from orchestrator.optical.services.nokia.tnms.client import TnmsClient
from orchestrator.optical.services.nokia.tnms.endpoints import Data, Operations
from orchestrator.optical.services.nokia.tnms.exceptions import (
    ApiError,
    AuthenticationError,
    TnmsClientError,
    ValidationError,
)
from orchestrator.optical.settings import get_settings

BASE_URL = "https://tnms.example.com"
AUTH_URL = f"{BASE_URL}/auth"
DATA_CONTEXT_URL = f"{BASE_URL}/data/tapi-common:context"
CLI_RESULT_URL = f"{BASE_URL}/operations/tapi-equipment-extensions-cli:get-cli-script-result/"
RUN_CLI_URL = f"{BASE_URL}/operations/tapi-equipment-extensions-cli:run-cli-script/"

TNMS_ENV = {
    "OPTICAL_TNMS_USER": "env-user",
    "OPTICAL_TNMS_PASSWORD": "env-password",
    "OPTICAL_TNMS_ENDPOINT": "https://tnms.env.example.com/",
}


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    """Keep the settings and lazy-client caches from leaking across tests."""
    get_settings.cache_clear()
    get_tnms_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_tnms_client.cache_clear()


@pytest.fixture
def client() -> TnmsClient:
    return TnmsClient("user", "password", BASE_URL + "/")


def test_init_normalizes_urls_and_builds_facades(client: TnmsClient) -> None:
    assert client.url == BASE_URL
    assert client._fallback_url is None  # noqa: SLF001
    assert isinstance(client.data, Data)
    assert isinstance(client.operations, Operations)


def test_init_stores_normalized_fallback_url() -> None:
    client = TnmsClient("user", "password", BASE_URL, fallback_url="https://fallback.example.com/")
    assert client._fallback_url == "https://fallback.example.com"  # noqa: SLF001


@pytest.mark.parametrize(
    ("resource", "expected_path"),
    [
        ("equipment", "/data/tapi-common:context/tapi-equipment:physical-context"),
        ("topology", "/data/tapi-common:context/tapi-topology:topology-context"),
        ("connectivity", "/data/tapi-common:context/tapi-connectivity:connectivity-context"),
        ("notification", "/data/tapi-common:context/tapi-notification:notification-context"),
        ("job", "/data/tapi-common:context/infn-job:job-context"),
    ],
)
def test_data_resource_paths(client: TnmsClient, resource: str, expected_path: str) -> None:
    endpoint = getattr(client.data, resource)
    assert endpoint._full_path == expected_path  # noqa: SLF001


def test_endpoint_traversal_pluralizes_and_builds_instance_path(client: TnmsClient) -> None:
    instance = client.data.equipment.devices("uuid-1")
    assert instance._full_path == (  # noqa: SLF001
        "/data/tapi-common:context/tapi-equipment:physical-context/device=uuid-1"
    )


@responses.activate
def test_retrieve_parses_json_and_sends_fields(client: TnmsClient) -> None:
    responses.add(responses.GET, DATA_CONTEXT_URL, json={"foo": {"a": 1, "b": 2}}, status=200)

    result = client.data.equipment.retrieve(fields=["name", "uuid"])

    assert result == {"a": 1, "b": 2}
    request = responses.calls[0].request
    assert request.url.startswith(DATA_CONTEXT_URL)
    assert "tapi-equipment%3Aphysical-context%28name%3Buuid%29" in request.url


@responses.activate
def test_request_returns_parsed_json(client: TnmsClient) -> None:
    responses.add(responses.GET, f"{BASE_URL}/data/x", json={"ok": True}, status=200)
    assert client._request("GET", "/data/x") == {"ok": True}  # noqa: SLF001


@responses.activate
def test_request_delete_returns_empty_dict(client: TnmsClient) -> None:
    responses.add(responses.DELETE, f"{BASE_URL}/data/x", status=204)
    assert client._request("DELETE", "/data/x") == {}  # noqa: SLF001


@responses.activate
def test_request_non_2xx_maps_to_api_error(client: TnmsClient) -> None:
    responses.add(responses.GET, f"{BASE_URL}/data/x", json={"detail": "boom"}, status=500)

    with pytest.raises(ApiError, match="API error 500") as exc_info:
        client._request("GET", "/data/x")  # noqa: SLF001

    assert exc_info.value.status_code == 500


@responses.activate
def test_request_401_reauthenticates_and_retries(client: TnmsClient) -> None:
    responses.add(responses.GET, f"{BASE_URL}/data/x", json={"detail": "expired"}, status=401)
    responses.add(responses.POST, AUTH_URL, json={"token_type": "Bearer", "access_token": "new-token"}, status=200)
    responses.add(responses.GET, f"{BASE_URL}/data/x", json={"ok": True}, status=200)

    assert client._request("GET", "/data/x") == {"ok": True}  # noqa: SLF001
    assert client._session.headers["Authorization"] == "Bearer new-token"  # noqa: SLF001


@responses.activate
def test_authenticate_posts_credentials_and_stores_token(client: TnmsClient) -> None:
    responses.add(responses.POST, AUTH_URL, json={"token_type": "Bearer", "access_token": "abc"}, status=200)

    client._authenticate()  # noqa: SLF001

    assert responses.calls[0].request.body == "user=user&password=password"
    assert client._session.headers["Authorization"] == "Bearer abc"  # noqa: SLF001
    assert client._session.headers["Content-Type"] == "application/yang-data+json"  # noqa: SLF001


@responses.activate
def test_authenticate_http_error_is_not_wrapped_as_authentication_error(client: TnmsClient) -> None:
    """An HTTP auth failure surfaces as ``requests.HTTPError``, not ``AuthenticationError``.

    ``_authenticate`` only reaches ``AuthenticationError`` when the endpoint loop
    completes without returning; HTTP errors are re-raised as ``requests.HTTPError``.
    """
    responses.add(responses.POST, AUTH_URL, json={"detail": "bad creds"}, status=401)

    with pytest.raises(requests.HTTPError, match="401 Client Error"):
        client._authenticate()  # noqa: SLF001


def test_authentication_error_is_a_tnms_client_error() -> None:
    assert issubclass(AuthenticationError, TnmsClientError)


def test_from_settings_builds_client(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in TNMS_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("OPTICAL_TNMS_SECONDARY_ENDPOINT", "https://tnms2.env.example.com")
    get_settings.cache_clear()

    client = TnmsClient.from_settings()

    assert client.user == "env-user"
    assert client.url == "https://tnms.env.example.com"
    assert client._fallback_url == "https://tnms2.env.example.com"  # noqa: SLF001


@pytest.mark.parametrize(
    "missing",
    ["OPTICAL_TNMS_USER", "OPTICAL_TNMS_PASSWORD", "OPTICAL_TNMS_ENDPOINT"],
)
def test_from_settings_missing_required_raises_validation_error(monkeypatch: pytest.MonkeyPatch, missing: str) -> None:
    for key, value in TNMS_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv(missing)
    get_settings.cache_clear()

    with pytest.raises(ValidationError, match=missing):
        TnmsClient.from_settings()


def test_from_env_delegates_to_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in TNMS_ENV.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()

    assert TnmsClient.from_env().url == "https://tnms.env.example.com"


def test_get_tnms_client_is_lazy_and_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    assert get_tnms_client.cache_info().currsize == 0

    for key, value in TNMS_ENV.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()

    first = get_tnms_client()
    second = get_tnms_client()

    assert first is second
    assert get_tnms_client.cache_info().currsize == 1


@responses.activate
def test_get_cli_script_result_returns_finished_output(client: TnmsClient) -> None:
    output = {"status": "FINISHED", "id": 7, "device-results": [{"device-ref": "d", "responses": []}]}
    responses.add(
        responses.POST,
        CLI_RESULT_URL,
        json={"tapi-equipment-extensions-cli:output": output},
        status=200,
    )

    assert client.operations.get_cli_script_result(7) == output
    assert json.loads(responses.calls[0].request.body) == {"tapi-equipment-extensions-cli:input": {"id": 7}}


@responses.activate
def test_get_cli_script_result_unexpected_status_raises_api_error(client: TnmsClient) -> None:
    responses.add(
        responses.POST,
        CLI_RESULT_URL,
        json={"tapi-equipment-extensions-cli:output": {"status": "BROKEN"}},
        status=200,
    )

    with pytest.raises(ApiError, match="API error 400"):
        client.operations.get_cli_script_result(7)


@responses.activate
def test_get_cli_script_result_retries_until_finished(client: TnmsClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tnms_endpoints, "sleep", lambda *_: None)
    responses.add(
        responses.POST,
        CLI_RESULT_URL,
        json={"tapi-equipment-extensions-cli:output": {"status": "RUNNING"}},
        status=200,
    )
    responses.add(
        responses.POST,
        CLI_RESULT_URL,
        json={"tapi-equipment-extensions-cli:output": {"status": "FINISHED", "id": 7}},
        status=200,
    )

    result = client.operations.get_cli_script_result(7, base_delay=0)

    assert result["status"] == "FINISHED"
    assert len(responses.calls) == 2


@responses.activate
def test_get_cli_script_result_exhausts_retries(client: TnmsClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tnms_endpoints, "sleep", lambda *_: None)
    for _ in range(2):
        responses.add(
            responses.POST,
            CLI_RESULT_URL,
            json={"tapi-equipment-extensions-cli:output": {"status": "RUNNING"}},
            status=200,
        )

    with pytest.raises(ApiError, match="Job retrieval failed after 2 retries"):
        client.operations.get_cli_script_result(7, max_retries=2, base_delay=0)


@responses.activate
def test_run_cli_script_posts_commands_and_polls_result(client: TnmsClient) -> None:
    responses.add(
        responses.POST,
        RUN_CLI_URL,
        json={"tapi-equipment-extensions-cli:output": {"id": 42}},
        status=200,
    )
    output = {"status": "FINISHED", "id": 42, "device-results": []}
    responses.add(
        responses.POST,
        CLI_RESULT_URL,
        json={"tapi-equipment-extensions-cli:output": output},
        status=200,
    )

    result = client.operations.run_cli_script(["dev-1"], ["SHOW-FOO;"], channel="TL1")

    assert result == output
    assert json.loads(responses.calls[0].request.body) == {
        "tapi-equipment-extensions-cli:input": {
            "device-list": ["dev-1"],
            "commands": ["SHOW-FOO;"],
            "channel": "TL1",
            "error-policy": "ABORT",
        }
    }
