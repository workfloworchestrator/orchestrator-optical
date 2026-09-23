# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Application settings.

Settings are read from the environment (prefixed with ``OPTICAL_``) and from an optional ``.env`` file.
No settings are required: the package is importable without any environment variables set, and
credentials/endpoints are resolved lazily by the services that need them.
"""

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Env-var tokens enabling TLS/SSH verification (case-insensitive).
_VERIFY_TRUE_VALUES = frozenset({"1", "true", "yes", "y", "on"})

#: Env-var tokens disabling TLS/SSH verification (case-insensitive, lab use only).
_VERIFY_FALSE_VALUES = frozenset({"0", "false", "no", "n", "off"})


def parse_verify(value: bool | str | None) -> bool | str | None:  # noqa: FBT001
    """Normalize a TLS/SSH verification setting to ``True``, ``False`` or a file path.

    Args:
        value: A boolean, a boolean-like string (``true``/``false`` and variants),
            a path to a CA bundle (TLS) or known-hosts file (SSH), or ``None``.

    Returns:
        ``True`` when verification is enabled, ``False`` when it is explicitly
        disabled (lab use only), the stripped path string for custom trust
        stores, or ``None`` when the input is ``None`` (not provided) or blank.
    """
    if value is None or isinstance(value, bool):
        return value
    text = value.strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in _VERIFY_TRUE_VALUES:
        return True
    if lowered in _VERIFY_FALSE_VALUES:
        return False
    return text


class OpticalSettings(BaseSettings):
    """Configuration for the optical orchestrator.

    All fields are optional; services that require a value raise a clear error at call time when
    it is missing.

    Attributes:
        flexils_user: Username for the FlexILS TL1 client (``OPTICAL_FLEXILS_USER``).
        flexils_password: Password for the FlexILS TL1 client (``OPTICAL_FLEXILS_PASSWORD``).
        g30_user: Username for the Nokia G30 restconf client (``OPTICAL_G30_USER``).
        g30_password: Password for the Nokia G30 restconf client (``OPTICAL_G30_PASSWORD``).
        g42_user: Username for the Nokia G42 restconf client (``OPTICAL_G42_USER``).
        g42_password: Password for the Nokia G42 restconf client (``OPTICAL_G42_PASSWORD``).
        tnms_endpoint: Primary endpoint of the TNMS API (``OPTICAL_TNMS_ENDPOINT``).
        tnms_secondary_endpoint: Fallback endpoint of the TNMS API (``OPTICAL_TNMS_SECONDARY_ENDPOINT``).
        tnms_user: Username for the TNMS API (``OPTICAL_TNMS_USER``).
        tnms_password: Password for the TNMS API (``OPTICAL_TNMS_PASSWORD``).
        g30_verify: TLS verification for the Nokia G30 RESTCONF client
            (``OPTICAL_G30_VERIFY``): ``True`` (default, system CA store),
            ``False`` (lab use only, disables verification), or a path to a
            custom CA bundle file for private-PKI networks.
        g42_verify: TLS verification for the Nokia G42 RESTCONF client
            (``OPTICAL_G42_VERIFY``), same semantics as ``g30_verify``.
        tnms_verify: TLS verification for the TNMS API client
            (``OPTICAL_TNMS_VERIFY``), same semantics as ``g30_verify``.
        flexils_verify_host_key: SSH host-key verification for the FlexILS TL1
            client (``OPTICAL_FLEXILS_VERIFY_HOST_KEY``): ``True`` (default,
            reject unknown host keys against the system known-hosts file),
            ``False`` (lab use only, auto-accept unknown host keys), or a path
            to a known-hosts file to verify against.
        customer_choice: Import path of the user-defined customer choice function
            (``OPTICAL_CUSTOMER_CHOICE``), as ``module.path:function_name``. The
            function must return a ``type[Choice]`` whose option values are the
            customer ids used as subscription ``customer_id``.
    """

    model_config = SettingsConfigDict(env_prefix="OPTICAL_", env_file=".env", extra="ignore")

    flexils_user: str | None = None
    flexils_password: str | None = None

    g30_user: str | None = None
    g30_password: str | None = None
    g42_user: str | None = None
    g42_password: str | None = None

    tnms_endpoint: str | None = None
    tnms_secondary_endpoint: str | None = None
    tnms_user: str | None = None
    tnms_password: str | None = None

    g30_verify: bool | str = True
    g42_verify: bool | str = True
    tnms_verify: bool | str = True

    flexils_verify_host_key: bool | str = True

    customer_choice: str | None = None

    @field_validator("g30_verify", "g42_verify", "tnms_verify", "flexils_verify_host_key", mode="before")
    @classmethod
    def _parse_verify(cls, value: Any) -> bool | str:
        """Normalize verify settings; blank/unset values fall back to the secure default."""
        parsed = parse_verify(value)
        return True if parsed is None else parsed


@lru_cache
def get_settings() -> OpticalSettings:
    """Return a cached instance of the application settings."""
    return OpticalSettings()
