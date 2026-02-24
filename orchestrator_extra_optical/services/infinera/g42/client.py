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

import base64
import logging
import os
from typing import Any

import requests

from services.infinera.g42.data import Data
from services.infinera.g42.operations import Operations

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class G42Client:
    """G42 API client with automatic authentication handling."""

    def __init__(self, lo_ip: str | None = None, mngmt_ip: str | None = None):
        raise NotImplementedError("Connection logic is not implemented in this snippet for security reasons.")  # FIXME

    def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        """Make authenticated API request."""

        def _helper(base_url: str):
            url = base_url + path
            msg = f"{method} {url} {kwargs}"
            log.debug(msg)
            response = self._session.request(method, url, timeout=(10, 2400), **kwargs)
            msg = f"Response: {response.text}"
            log.debug(msg)
            response.raise_for_status()
            return response.json() if response.text else {}

        try:
            result = _helper(self.url)

        except (requests.ConnectionError, requests.Timeout):
            if not self.fallback_url:
                raise
            result = _helper(self.fallback_url)

        except (requests.HTTPError, requests.RequestException) as e:
            msg = f"{e.response.status_code} Client Error: {e.response.text}"
            error = requests.HTTPError(msg) if isinstance(e, requests.HTTPError) else requests.RequestException(msg)
            raise error from e

        return result
