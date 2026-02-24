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

import contextlib
import logging
import os
import time
from typing import Any, ClassVar, TypeVar

import paramiko

# Assuming these exist in your project structure
from services.infinera.flexils.commands.base import TL1BaseCommand, TL1BaseResponse, TL1CommandRegistry
from services.infinera.flexils.utils import generate_ctag

T = TypeVar("T", bound=TL1BaseCommand)
logger = logging.getLogger(__name__)

class FlexilsClient:
    _cache: ClassVar[dict[tuple[str, str], "FlexilsClient"]] = {}

    @classmethod
    def get_instance(cls, tid: str, gne_ip: str, timeout: int = 30) -> "FlexilsClient":
        key = (tid.lower(), gne_ip)
        if key not in cls._cache:
            client = cls(tid, gne_ip, timeout)
            cls._cache[key] = client
        return cls._cache[key]

    @classmethod
    def close_all(cls):
        for client in list(cls._cache.values()):
            client.close()
        cls._cache.clear()

    def __init__(self, tid: str, gne_ip: str, timeout: int = 30):
        """
        Synchronous TL1 Client for Infinera FlexILS.
        Maintains a persistent SSH subsystem connection.
        """
        self.tid = tid
        self.gne_ip = gne_ip
        self.timeout = timeout

        self._client: paramiko.SSHClient | None = None
        self._channel: paramiko.Channel | None = None

        # Eagerly bind commands
        self._init_command_methods()

    def _authenticate(self):
        raise NotImplementedError("Connection logic is not implemented in this snippet for security reasons.")  # FIXME

    def _connect(self):
        raise NotImplementedError("Connection logic is not implemented in this snippet for security reasons.")  # FIXME

    def _close(self):
        """Closes channel and client."""
        if self._channel:
            with contextlib.suppress(Exception):
                self._channel.close()
            self._channel = None

        if self._client:
            with contextlib.suppress(Exception):
                self._client.close()
            self._client = None

    def _send_and_receive_until(self, command: str, until_strings: list[str]) -> str:
        """Internal logic to write to socket and read buffer."""
        if not self._channel or not self._channel.active:
            self._connect()

        if isinstance(until_strings, str):
            until_strings = [until_strings]

        # Write
        if command.startswith("ACT-USER"):
            msg = f"Logging in to {self.gne_ip} ({self.tid})..."
            logger.info(msg)
        else:
            msg = f"Sending: {command.strip()}"
            logger.info(msg)
        if isinstance(command, str):
            command = command.encode("utf-8")

        try:
            self._channel.sendall(command)
        except (OSError, paramiko.SSHException):
            logger.warning(f"Connection lost during send to {self.tid}. Reconnecting...")  # noqa: G004
            self._connect()
            self._channel.sendall(command)

        # Read loop
        buffer = b""
        has_last_msg_started = False
        start_time = time.time()
        timeout_time = start_time + self.timeout

        encoded_until_strings = [s.encode("utf-8") for s in until_strings]
        encoded_tl1_prompt = b"TL1>>"

        while True:
            if time.time() > timeout_time:
                msg = f"Timeout waiting for response to {command}"
                raise TimeoutError(msg)

            # Read available data
            chunk = self._channel.recv(4096)
            if not chunk:
                # Connection closed remotely
                raise EOFError("Socket closed during read")

            buffer += chunk

            # Check for termination logic
            # 1. Must contain one of the markers (COMPLD, DENY, etc)
            # 2. Must end with 'TL1>>' (TL1 prompt)
            if any(marker in buffer for marker in encoded_until_strings):
                has_last_msg_started = True

            if has_last_msg_started and buffer.endswith(encoded_tl1_prompt):
                buffer = buffer.decode("utf-8")
                if buffer.startswith("ACT-USER"):
                    buffer = buffer.replace(_username, "")
                msg = f"Command output: {buffer}"
                logger.info(msg)
                return buffer

    def execute_raw_command(self, command: str, correlation_tag: str) -> str:
        """
        Sends a raw TL1 command and waits for the specific termination sequence.
        Handles auto-reconnection on failure.
        """
        last_msg_markers = [
            f"{correlation_tag} COMPLD",
            f"{correlation_tag} DENY",
            f"{correlation_tag} PRTL",
            "M  0 DENY",
        ]
        stdout = self._send_and_receive_until(command, last_msg_markers)

        if "PRIVILEGE, LOGIN NOT ACTIVE"[::-1] in stdout[::-1]:
            self._authenticate()
            stdout = self._send_and_receive_until(command, last_msg_markers)

        stdout = stdout.removeprefix(f"{command}\r\n")
        return stdout.removesuffix("TL1>>")

    def _execute_command(self, command_cls: type[T], **kwargs: Any) -> TL1BaseResponse:
        """Execute a TL1 command using its Pydantic model."""
        # Note: 'tid' usually needs to be passed to the command model if strictly required
        # or the command class handles it. Assuming device_tid logic maps to self.tid
        command = command_cls(tid=self.tid, **kwargs)
        return command.execute(self)

    def _init_command_methods(self) -> None:
        """Dynamically binds methods from the Registry to this instance."""
        for method_name, command_class in TL1CommandRegistry.commands.items():

            def create_method(cmd_class):
                def method(**kwargs):
                    return self._execute_command(cmd_class, **kwargs)

                return method

            bound_method = create_method(command_class)
            bound_method.__name__ = method_name
            bound_method.__qualname__ = f"{self.__class__.__name__}.{method_name}"
            setattr(self, method_name, bound_method)

    def close(self):
        """Public method to close the connection explicitly."""
        self._close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, ensures connection closure."""
        self.close()

    def __del__(self):  # noqa: D105
        self.close()
