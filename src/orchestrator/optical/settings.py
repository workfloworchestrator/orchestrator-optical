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

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpticalSettings(BaseSettings):
    """Configuration for the optical orchestrator.

    All fields are optional; services that require a value raise a clear error at call time when
    it is missing.

    Attributes:
        netbox_url: Base URL of the Netbox instance (``OPTICAL_NETBOX_URL``).
        netbox_token: API token for Netbox (``OPTICAL_NETBOX_TOKEN``).
        ipv4_loopback_prefix: IPv4 prefix used for Netbox loopback address reservation
            (``OPTICAL_IPV4_LOOPBACK_PREFIX``).
        ipv6_loopback_prefix: IPv6 prefix used for Netbox loopback address reservation
            (``OPTICAL_IPV6_LOOPBACK_PREFIX``).
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
        customer_choice: Import path of the user-defined customer choice function
            (``OPTICAL_CUSTOMER_CHOICE``), as ``module.path:function_name``. The
            function must return a ``type[Choice]`` whose option values are the
            customer ids used as subscription ``customer_id``.
    """

    model_config = SettingsConfigDict(env_prefix="OPTICAL_", env_file=".env", extra="ignore")

    netbox_url: str | None = None
    netbox_token: str | None = None
    ipv4_loopback_prefix: str | None = None
    ipv6_loopback_prefix: str | None = None

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

    customer_choice: str | None = None


@lru_cache
def get_settings() -> OpticalSettings:
    """Return a cached instance of the application settings."""
    return OpticalSettings()
