"""Global settings."""

import os

from orchestrator.settings import app_settings
from pydantic_settings import BaseSettings


class GarrSettings(BaseSettings):
    """App GARR base settings."""

    IPv4_LOOPBACK_PREFIX: str = "10.0.127.0/24"
    IPv6_LOOPBACK_PREFIX: str = "fc00:0:0:127::/64"
    IPv4_CORE_LINK_PREFIX: str = "10.0.10.0/24"
    IPv6_CORE_LINK_PREFIX: str = "fc00:0:0:10::/64"
    NETBOX_URL: str = os.getenv("NETBOX_URL", "localhost:8000")
    NETBOX_TOKEN: str = os.getenv("NETBOX_TOKEN", "")
    OAUTH2_ACTIVE: bool = os.getenv("OAUTH2_ACTIVE", None)


class CelerySettings(BaseSettings):
    """Parameters for Celery."""

    broker_url: str = str(app_settings.CACHE_URI)
    result_backend: str = str(app_settings.CACHE_URI)
    result_expires: int = 3600


garr_settings = GarrSettings()
celery_settings = CelerySettings()
