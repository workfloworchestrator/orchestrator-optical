import contextlib
import logging
import socket
import time
from typing import Any, ClassVar, TypeVar

import paramiko

from orchestrator.optical.services.nokia.flexils.commands.base import (
    TL1BaseCommand,
    TL1BaseResponse,
    TL1CommandRegistry,
)
from orchestrator.optical.services.nokia.flexils.utils import generate_ctag
from orchestrator.optical.settings import get_settings, parse_verify

T = TypeVar("T", bound=TL1BaseCommand)
logger = logging.getLogger(__name__)


class FlexilsClient:
    _cache: ClassVar[dict[tuple[str, str, str | None, str | None, bool | str], "FlexilsClient"]] = {}

    @classmethod
    def get_instance(
        cls,
        tid: str,
        gne_ip: str,
        timeout: int = 30,
        username: str | None = None,
        password: str | None = None,
        verify_host_key: bool | str | None = None,  # noqa: FBT001
    ) -> "FlexilsClient":
        resolved_verify = parse_verify(verify_host_key)
        if resolved_verify is None:
            resolved_verify = get_settings().flexils_verify_host_key
        key = (tid.lower(), gne_ip, username, password, resolved_verify)
        if key not in cls._cache:
            client = cls(tid, gne_ip, timeout, username, password, verify_host_key=resolved_verify)
            cls._cache[key] = client
        return cls._cache[key]

    @classmethod
    def close_all(cls):
        for client in list(cls._cache.values()):
            client.close()
        cls._cache.clear()

    def __init__(
        self,
        tid: str,
        gne_ip: str,
        timeout: int = 30,
        username: str | None = None,
        password: str | None = None,
        verify_host_key: bool | str | None = None,  # noqa: FBT001
    ):
        """Synchronous TL1 Client for Nokia FlexILS.
        Maintains a persistent SSH subsystem connection.
        """
        self.tid = tid
        self.gne_ip = gne_ip
        self.timeout = timeout

        settings = get_settings()
        self._username = username if username is not None else settings.flexils_user
        self._password = password if password is not None else settings.flexils_password
        resolved_verify = parse_verify(verify_host_key)
        self._verify_host_key: bool | str = (
            resolved_verify if resolved_verify is not None else settings.flexils_verify_host_key
        )

        self._client: paramiko.SSHClient | None = None
        self._channel: paramiko.Channel | None = None

        # Eagerly bind commands
        self._init_command_methods()

    def _authenticate(self):
        # Send login command
        ctag = generate_ctag()
        command = f"ACT-USER:{self.tid}:{self._username}:{ctag}::{self._password};"
        self.execute_raw_command(command, ctag)

        # Inhibit autonomous messages
        ctag = generate_ctag()
        command = f"INH-MSG-ALL:{self.tid}::{ctag}::;"
        self.execute_raw_command(command, ctag)

    def _connect(self):
        """Establishes the SSH connection, opens the tl1telnet subsystem and sends the login command."""
        if not self._username or not self._password:
            msg = (
                "FlexILS credentials are not configured: set OPTICAL_FLEXILS_USER and OPTICAL_FLEXILS_PASSWORD"
                " or pass username and password to the client"
            )
            raise RuntimeError(msg)

        msg = f"Connecting to {self.gne_ip} ({self.tid})..."
        logger.info(msg)
        self._close()  # Ensure clean slate

        try:
            self._client = paramiko.SSHClient()
            if self._verify_host_key is False:
                msg = (
                    "SSH host key verification is disabled for the FlexILS client "
                    "(OPTICAL_FLEXILS_VERIFY_HOST_KEY=false). Do not use in production."
                )
                logger.warning(msg)
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                self._client.load_system_host_keys()
                if isinstance(self._verify_host_key, str):
                    self._client.load_host_keys(self._verify_host_key)
                self._client.set_missing_host_key_policy(paramiko.RejectPolicy())

            self._client.connect(
                hostname=self.gne_ip,
                port=22,
                username=self._username,
                password=self._password,
                timeout=self.timeout,
                allow_agent=False,  # Disable agent forwarding
                look_for_keys=False,  # Disable looking for keys
            )

            # Open a session channel
            transport = self._client.get_transport()
            if not transport:
                msg = "Failed to get SSH transport"
                raise ConnectionError(msg)  # noqa: TRY301

            # --- KEEPALIVE INJECTION ---
            # 1. SSH-Level Keepalive: Sends an SSH keepalive packet every 30 seconds
            transport.set_keepalive(30)

            # 2. TCP-Level Keepalive: Applies your intended socket options to Paramiko's underlying socket
            sock = transport.sock
            if sock is not None:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                if hasattr(socket, "TCP_KEEPIDLE"):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                if hasattr(socket, "TCP_KEEPINTVL"):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 60)
                if hasattr(socket, "TCP_KEEPCNT"):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6)
            # ---------------------------

            self._channel = transport.open_session()
            self._channel.settimeout(self.timeout)

            # Request the specific subsystem TL1
            self._channel.invoke_subsystem("tl1telnet")
            self._send_and_receive_until("", ["License"])
            msg = f"Connected to {self.gne_ip} ({self.tid})"
            logger.info(msg)

            self._authenticate()

        except Exception as e:
            msg = f"Failed to connect to {self.gne_ip}: {e}"
            logger.exception(msg)
            self._close()
            raise

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
                msg = "Socket closed during read"
                raise EOFError(msg)

            buffer += chunk

            # Check for termination logic
            # 1. Must contain one of the markers (COMPLD, DENY, etc)
            # 2. Must end with 'TL1>>' (TL1 prompt)
            if any(marker in buffer for marker in encoded_until_strings):
                has_last_msg_started = True

            if has_last_msg_started and buffer.endswith(encoded_tl1_prompt):
                buffer = buffer.decode("utf-8")
                if buffer.startswith("ACT-USER") and self._username:
                    buffer = buffer.replace(self._username, "")
                msg = f"Command output: {buffer}"
                logger.info(msg)
                return buffer

    def execute_raw_command(self, command: str, correlation_tag: str) -> str:
        """Sends a raw TL1 command and waits for the specific termination sequence.
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
        """Execute a TL1 command using its Pydantic model.

        The command always targets the client's own tid. Callers must not pass a
        ``tid`` kwarg: to run the command against a different node, use a client
        bound to that node's tid instead.

        Raises:
            ValueError: If the caller passes a ``tid`` kwarg.
        """
        if "tid" in kwargs:
            msg = (
                f"Passing 'tid' to a TL1 command is not allowed: the client already "
                f"targets '{self.tid}'. To run the command against a different node, use a "
                f"client bound to that node's tid instead of passing 'tid' here."
            )
            raise ValueError(msg)
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

    def __del__(self):
        self.close()
