# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TNMS API client implementation."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import requests

from orchestrator.optical.services.nokia.tnms.endpoints import Data, Operations
from orchestrator.optical.services.nokia.tnms.exceptions import ApiError, AuthenticationError, ValidationError
from orchestrator.optical.settings import get_settings

T = TypeVar("T")

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def requires_auth(func: Callable) -> Callable:
    """Decorator to ensure valid authentication before making requests."""

    @wraps(func)
    def wrapper(self: "TnmsClient", *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except requests.HTTPError as e:
            if e.response.status_code == 401:  # noqa: PLR2004
                # Token expired or invalid - get a new one
                self._authenticate()
                # Retry the request once
                return func(self, *args, **kwargs)
            raise ApiError(e.response.status_code, str(e)) from e

    return wrapper


class TnmsClient:
    def __init__(
        self,
        user: str,
        password: str,
        url: str,
        fallback_url: str | None = None,
        verify_tls: bool = False,  # noqa: FBT001, FBT002
    ):
        """TNMS API client with automatic authentication handling."""
        self.user = user
        self.password = password
        self._primary_url = url.rstrip("/")
        self._fallback_url = fallback_url.rstrip("/") if fallback_url else None
        self.url = self._primary_url  # active endpoint
        self._session = requests.Session()
        self._session.verify = verify_tls
        self._session.trust_env = verify_tls  # Disable env vars if TLS verification is off
        self.data = Data(self)
        self.operations = Operations(self)

    @classmethod
    def from_settings(cls) -> "TnmsClient":
        """Create client instance from the application settings.

        Reads the ``OPTICAL_TNMS_USER``, ``OPTICAL_TNMS_PASSWORD`` and ``OPTICAL_TNMS_ENDPOINT``
        variables (plus the optional ``OPTICAL_TNMS_SECONDARY_ENDPOINT``) through
        :func:`get_settings`.

        Returns:
            A TNMS client configured from the settings.

        Raises:
            ValidationError: if any of the required settings is missing.
        """
        settings = get_settings()
        user = settings.tnms_user
        password = settings.tnms_password
        endpoint = settings.tnms_endpoint
        if not (user and password and endpoint):
            missing = [
                env_var
                for value, env_var in (
                    (user, "OPTICAL_TNMS_USER"),
                    (password, "OPTICAL_TNMS_PASSWORD"),
                    (endpoint, "OPTICAL_TNMS_ENDPOINT"),
                )
                if not value
            ]
            msg = f"Missing required settings: {', '.join(missing)}"
            raise ValidationError(msg)

        return cls(
            user=user,
            password=password,
            url=endpoint,
            fallback_url=settings.tnms_secondary_endpoint,
        )

    @classmethod
    def from_env(cls) -> "TnmsClient":
        """Create client instance from the environment.

        Backward-compatible alias of :meth:`from_settings`: the ``OPTICAL_TNMS_*`` variables are
        resolved through the application settings.
        """
        return cls.from_settings()

    def _authenticate(self) -> None:
        """Obtain and store authentication token, with optional fallback."""
        auth_endpoints = [self._primary_url]
        if self._fallback_url:
            auth_endpoints.append(self._fallback_url)

        self._session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

        last_error: Exception | None = None
        for endpoint in auth_endpoints:
            self.url = endpoint

            try:
                response = self._session.post(
                    f"{self.url}/auth",
                    data={"user": self.user, "password": self.password},
                )
                response.raise_for_status()

            except (requests.HTTPError, requests.RequestException) as e:
                msg = f"{e.response.status_code} Client Error: {e.response.text}"
                error = requests.HTTPError(msg) if isinstance(e, requests.HTTPError) else requests.RequestException(msg)
                raise error from e

            except (requests.ConnectionError, requests.Timeout) as e:
                last_error = e
                continue

            else:
                token_data = response.json()
                log.info("Authenticated successfully to TNMS API @ %s", self.url)
                self._session.headers.update(
                    {
                        "Authorization": f"{token_data['token_type']} {token_data['access_token']}",
                        "Content-Type": "application/yang-data+json",
                    }
                )
                return

        msg = f"Authentication failed after trying endpoints: {auth_endpoints}"
        raise AuthenticationError(msg) from last_error

    @requires_auth
    def _request(self, method: str, path: str, log_mask: dict | None = None, **kwargs: Any) -> dict:
        """Make authenticated API request.

        :param log_mask: Optional dictionary to log instead of the actual kwargs
                         (used to hide secrets/credentials).
        """
        url = self.url + path

        # LOGGING: Use the mask if provided, otherwise use the actual kwargs
        log_payload = log_mask if log_mask is not None else kwargs
        msg = f"{method} {url} {log_payload}"
        log.info(msg)

        # EXECUTION: Always use the actual kwargs
        response = self._session.request(method, url, timeout=(10, 2400), **kwargs)
        response.raise_for_status()

        msg = f"Response: {response.text}"
        log.info(msg)

        return response.json() if method != "DELETE" else {}
