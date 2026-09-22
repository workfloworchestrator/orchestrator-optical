"""Unit tests for the lazily-resolved application settings.

The module must be importable and ``get_settings()`` callable with no ``OPTICAL_*``
environment variables set; values are read at call time (and cached) rather than at
import time.
"""

import os
import subprocess
import sys
from pathlib import Path

from orchestrator.optical.settings import OpticalSettings, get_settings

_EXPECTED_FIELDS = {
    "flexils_user",
    "flexils_password",
    "g30_user",
    "g30_password",
    "g42_user",
    "g42_password",
    "tnms_endpoint",
    "tnms_secondary_endpoint",
    "tnms_user",
    "tnms_password",
    "customer_choice",
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
        assert all(getattr(settings, name) is None for name in _EXPECTED_FIELDS)
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
