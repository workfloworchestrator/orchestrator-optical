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
import os
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import requests

from services.infinera.flexils.deprecated_client import FlexILSClient
from services.infinera.tnms.endpoints import Data, Operations
from services.infinera.tnms.exceptions import ApiError, AuthenticationError, ValidationError

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
            if e.response.status_code == 401:
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
        verify_tls: bool = False,
    ):
        """TNMS API client with automatic authentication handling."""
        self.user = user
        self.password = password
        self._primary_url = url.rstrip("/")
        self._fallback_url = fallback_url.rstrip("/") if fallback_url else None
        self.url = self._primary_url  # active endpoint
        self._session = requests.Session()
        self._session.verify = verify_tls
        self.data = Data(self)
        self.operations = Operations(self)

    @classmethod
    def from_env(cls) -> "TnmsClient":
        """Create client instance from environment variables."""
        required = ["TNMS_USER", "TNMS_PASSWORD", "TNMS_ENDPOINT"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            msg = f"Missing required env vars: {', '.join(missing)}"
            raise ValidationError(msg)

        return cls(
            user=os.environ["TNMS_USER"],
            password=os.environ["TNMS_PASSWORD"],
            url=os.environ["TNMS_ENDPOINT"],
            fallback_url=os.getenv("TNMS_SECONDARY_ENDPOINT"),
        )

    def _authenticate(self) -> None:
        raise NotImplementedError("Connection logic is not implemented in this snippet for security reasons.")  # FIXME

    @requires_auth
    def _request(self, method: str, path: str, log_mask: dict | None = None, **kwargs: Any) -> dict:
        """
        Make authenticated API request.

        :param log_mask: Optional dictionary to log instead of the actual kwargs
                         (used to hide secrets/credentials).
        """
        url = self.url + path

        # LOGGING: Use the mask if provided, otherwise use the actual kwargs
        log_payload = log_mask if log_mask is not None else kwargs
        msg = f"{method} {url} {log_payload}"
        log.debug(msg)

        # EXECUTION: Always use the actual kwargs
        response = self._session.request(method, url, timeout=(10, 2400), **kwargs)
        response.raise_for_status()

        msg = f"Response: {response.text}"
        log.debug(msg)

        return response.json() if method != "DELETE" else {}

    def flexils(self, device_uuid: str, device_tid: str) -> "FlexILSClient":
        """Create a FlexILS client for a specific device."""
        return FlexILSClient(self, device_uuid, device_tid)
