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

"""
TNMS (Transport Network Management System) API Client Package.

This package provides a client interface for interacting with the TNMS API.
It handles authentication and provides methods for device management operations.

Example:
    >>> from services.infinera import tnms_client
    >>> devices = tnms_client.data.equipment.devices.retrieve(fields=["name", "type"])

Note:
    The package is configured using environment variables:
    TNMS_ENDPOINT
    TNMS_SECONDARY_ENDPOINT
    TNMS_USER
    TNMS_PASSWORD
    TOPOLOGY_UUID
    G30_USER
    G30_PASSWORD
    G42_USER
    G42_PASSWORD
    FLEXILS_USER
    FLEXILS_PASSWORD

    The client instance is created as a singleton from the environment variables.
"""

import logging
import socket
from typing import Final

from urllib3.util import connection

from services.infinera.flexils.client import FlexilsClient
from services.infinera.flexils.exceptions import FlexILSClientError, TL1CommandDeniedError
from services.infinera.g30.client import G30Client
from services.infinera.g42.client import G42Client
from services.infinera.tnms.client import TnmsClient
from services.infinera.tnms.exceptions import ApiError, AuthenticationError, TnmsClientError, ValidationError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def _enable_tcp_keepalive_once():
    if getattr(connection, "tcp_keepalive_patched", False):
        return  # already patched (by us or someone else)

    orig = connection.create_connection

    def patched(*args, **kwargs):
        sock = orig(*args, **kwargs)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 60)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6)
        except (AttributeError, OSError):
            pass  # some platforms don't support all options
        return sock

    connection.create_connection = patched
    connection.tcp_keepalive_patched = True  # mark as patched


_enable_tcp_keepalive_once()


__version__: Final[str] = "1.0.0"

# Singleton instance configured from environment variables
# with automatic re-authentication
tnms_client: Final[TnmsClient] = TnmsClient.from_env()
__all__ = [
    "ApiError",
    "AuthenticationError",
    "FlexILSClientError",
    "FlexilsClient",
    "G30Client",
    "G42Client",
    "TL1CommandDeniedError",
    "TnmsClientError",
    "ValidationError",
    "__version__",
    "tnms_client",
]
