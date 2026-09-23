"""Unit tests for the lazily-resolved application settings.

The module must be importable and ``get_settings()`` callable with no ``OPTICAL_*``
environment variables set; values are read at call time (and cached) rather than at
import time.
"""

import os
import subprocess
import sys
from pathlib import Path

from orchestrator.optical.settings import OpticalSettings, get_settings, parse_verify

_EXPECTED_FIELDS = {
    "flexils_user",
    "flexils_password",
    "flexils_verify_host_key",
    "g30_user",
    "g30_password",
    "g30_verify",
    "g42_user",
    "g42_password",
    "g42_verify",
    "tnms_endpoint",
    "tnms_secondary_endpoint",
    "tnms_user",
    "tnms_password",
    "tnms_verify",
    "customer_choice",
}
# Verify settings are secure by default (True), everything else defaults to None.
_VERIFY_FIELDS = {
    "flexils_verify_host_key",
    "g30_verify",
    "g42_verify",
    "tnms_verify",
}
_OPTICAL_ENV_VARS = [f"OPTICAL_{name.upper()}" for name in _EXPECTED_FIELDS]


def test_settings_exposes_expected_optional_fields() -> None:
    assert set(OpticalSettings.model_fields) == _EXPECTED_FIELDS


def test_get_settings_returns_defaults_without_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for name in _OPTICAL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    try:
        settings = get_settings()
        for name in _EXPECTED_FIELDS:
            expected = True if name in _VERIFY_FIELDS else None
            assert getattr(settings, name) is expected, name
    finally:
        get_settings.cache_clear()


def test_get_settings_picks_up_env_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPTICAL_TNMS_USER", "alice")
    get_settings.cache_clear()
    try:
        assert get_settings().tnms_user == "alice"
    finally:
        get_settings.cache_clear()


def test_get_settings_is_cached(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    try:
        assert get_settings() is get_settings()
    finally:
        get_settings.cache_clear()


def test_import_and_get_settings_require_no_env_vars(tmp_path: Path) -> None:
    """Importing the module and building settings must not need any OPTICAL_* env var."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("OPTICAL_")}
    code = (
        "import orchestrator.optical.settings as s; assert s.get_settings.cache_info().currsize == 0; s.get_settings()"
    )

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_parse_verify_passes_through_bools_and_none() -> None:
    assert parse_verify(value=True) is True
    assert parse_verify(value=False) is False
    assert parse_verify(value=None) is None


def test_parse_verify_maps_boolean_strings() -> None:
    for token in ("true", "True", "TRUE", "1", "yes", "Y", "on", "  ON  "):
        assert parse_verify(token) is True, token
    for token in ("false", "False", "FALSE", "0", "no", "N", "off", "  Off "):
        assert parse_verify(token) is False, token


def test_parse_verify_keeps_paths_and_maps_blank_to_none() -> None:
    assert parse_verify("/etc/ssl/certs/ca-bundle.crt") == "/etc/ssl/certs/ca-bundle.crt"
    assert parse_verify("  /etc/ssl/custom-ca.pem  ") == "/etc/ssl/custom-ca.pem"
    assert parse_verify("") is None
    assert parse_verify("   ") is None


def test_verify_settings_default_to_secure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for name in _OPTICAL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.g30_verify is True
        assert settings.g42_verify is True
        assert settings.tnms_verify is True
        assert settings.flexils_verify_host_key is True
    finally:
        get_settings.cache_clear()


def test_verify_settings_accept_false_and_ca_bundle_path(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPTICAL_G30_VERIFY", "false")
    monkeypatch.setenv("OPTICAL_G42_VERIFY", "0")
    monkeypatch.setenv("OPTICAL_TNMS_VERIFY", "/etc/ssl/tnms-ca.pem")
    monkeypatch.setenv("OPTICAL_FLEXILS_VERIFY_HOST_KEY", "off")
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.g30_verify is False
        assert settings.g42_verify is False
        assert settings.tnms_verify == "/etc/ssl/tnms-ca.pem"
        assert settings.flexils_verify_host_key is False
    finally:
        get_settings.cache_clear()
