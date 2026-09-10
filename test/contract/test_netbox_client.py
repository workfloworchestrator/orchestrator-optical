"""Contract tests for the lazy Netbox API client.

Importing the Netbox module must not touch the environment or the network: the
API object is built only when the cached accessor is first called, and it fails
with a clear error when the connection settings are missing. These tests pin
that contract without contacting a real Netbox.
"""

import os
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from orchestrator.optical.services import netbox

NETBOX_URL = "https://netbox.example.com"
NETBOX_TOKEN = "test-token"  # noqa: S105


@pytest.fixture(autouse=True)
def _clear_api_cache() -> None:
    netbox.get_netbox_api.cache_clear()
    yield
    netbox.get_netbox_api.cache_clear()


def _settings(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {"netbox_url": None, "netbox_token": None}
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("url", "token"),
    [
        (None, "token"),
        ("https://netbox.example.com", None),
        (None, None),
    ],
)
def test_get_netbox_api_raises_when_unconfigured(
    monkeypatch: pytest.MonkeyPatch, url: str | None, token: str | None
) -> None:
    monkeypatch.setattr(netbox, "get_settings", lambda: _settings(netbox_url=url, netbox_token=token))

    with pytest.raises(RuntimeError, match="Netbox is not configured"):
        netbox.get_netbox_api()


def test_get_netbox_api_builds_client_once_and_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_api = MagicMock(name="pynetbox_api")
    monkeypatch.setattr(
        netbox,
        "get_settings",
        lambda: _settings(netbox_url=NETBOX_URL, netbox_token=NETBOX_TOKEN),
    )
    monkeypatch.setattr(netbox, "pynetbox_api", fake_api)

    first = netbox.get_netbox_api()
    second = netbox.get_netbox_api()

    assert first is second
    assert first is fake_api.return_value
    fake_api.assert_called_once_with(url=NETBOX_URL, token=NETBOX_TOKEN)
    assert netbox.get_netbox_api.cache_info().currsize == 1


def test_failed_accessor_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(netbox, "get_settings", lambda: _settings())

    with pytest.raises(RuntimeError, match="Netbox is not configured"):
        netbox.get_netbox_api()

    assert netbox.get_netbox_api.cache_info().currsize == 0


def test_import_has_no_environment_side_effects() -> None:
    env = {key: value for key, value in os.environ.items() if not key.startswith("OPTICAL_")}
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", "import orchestrator.optical.services.netbox"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
