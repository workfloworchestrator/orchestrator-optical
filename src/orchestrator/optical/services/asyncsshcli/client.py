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

"""A small async SSH CLI helper used by the generic CLI service.

This module provides the AsyncSshTerminal class which wraps an asyncssh connection
and a remote shell process. It contains utilities for issuing commands,
handling interactive prompts, and reading output until expected end markers
are observed. It's intended for programmatic interaction with network devices
or remote shells in integration tests / automation tasks.

The idea behind this client is that it is possible to send multiple commands
in one line using the ; separator so that using unsupported commands, such as
uuid strings, the device will reply with an error message that includes the wrong
command. This way it is possible to undoubtly detect the successfull complition of the
commands execution. Because of this rationale, this is suitable for all devices, e.g. TL1
interfaces follow different interaction patterns (correlation tags).
"""

import asyncio
import logging
from string import Template
from uuid import uuid4

import asyncssh

logger = logging.getLogger(__name__)


class AsyncSshTerminal:
    """Manage an asynchronous SSH session and remote interactive shell.

    Use this class as an async context manager to open/close the underlying
    SSH connection and interactive shell process. The class exposes helpers
    to execute commands, handle interactive prompts and safely read output
    until one of a set of expected end markers appears.

    Attributes:
        host: remote host as string
        port: remote ssh port as integer
        username: login username
        password: login password
        end_markers: list of Template instances used to detect command completion
        connection: the active asyncssh.SSHClientConnection or None
        process: the active asyncssh.SSHClientProcess or None
        timeout: default read timeout in seconds
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        unsupported_command_template_responses: list[Template] | None = None,
        timeout: int = 30,
    ):
        """Initialize a AsyncSshTerminal.

        Parameters:
            host: Hostname or IP of the remote SSH target.
            port: SSH port on the remote host.
            username: Username to authenticate with.
            password: Password to use for authentication.
            unsupported_command_template_responses: Optional list of
                string.Template instances that will be used to form
                strings which indicate command execution has completed
                (e.g. error messages to watch for). If None, the default
                list of common messages will be used: "operation
                '$command' not supported" and "$command: command not found".
            timeout: Default timeout, in seconds, used when waiting for
                process output.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.end_markers = [
            Template("operation '$command' not supported"),
            Template("$command: command not found"),
        ]
        if unsupported_command_template_responses is not None:
            self.end_markers.extend(unsupported_command_template_responses)
        self.connection: asyncssh.SSHClientConnection | None = None
        self.process: asyncssh.SSHClientProcess | None = None
        self.timeout = timeout

    async def __aenter__(self):
        """Enter the async context and establish an SSH connection and shell.

        Returns:
            self: the AsyncSshTerminal instance with an active connection and
                  shell process available at ``self.process``.

        Raises:
            asyncssh.Error (or subclass): if the SSH connection or process
                cannot be created.
        """
        self.connection = await asyncssh.connect(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            known_hosts=None,
            connect_timeout=10,
        )
        self.process = await self.connection.create_process(term_type="xterm", term_size=(1024, 48))
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the async context and close the SSH connection.

        The connection is closed and we wait for it to be closed. Exceptions
        from the context body (if any) are not suppressed here.
        """
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()

    async def _read_until_and_log(
        self,
        until: str | list[str],
    ) -> str:
        """Read from the remote process stdout until one of the stop strings.

        This helper will attempt to read repeatedly from the remote process
        stdout stream until any of the strings passed in ``until`` is found
        in the accumulated buffer. Data received is appended to a local
        buffer which is returned once a stop string appears.

        Parameters:
            until: A single string or a list of strings to match against the
                   received output. When any entry is found in the buffer
                   the method returns.

        Returns:
            The accumulated output as a string including the matched stop
            marker.

        Raises:
            TimeoutError: if no stop string is observed within ``self.timeout``
                seconds while waiting for stdout data.
        """
        if isinstance(until, str):
            until = [until]

        buffer = ""
        while True:
            try:
                chunk = await asyncio.wait_for(self.process.stdout.read(4096), timeout=self.timeout)
            except TimeoutError as e:
                msg = f"Timeout while waiting for prompts: {until}. Current buffer:\n{buffer}"
                raise TimeoutError(msg) from e
            logger.debug("Received chunk: %s", chunk)
            buffer += chunk

            if any(end in buffer for end in until):
                return buffer

    async def change_user_or_host(
        self,
        command: str,
        user_at_host_prompt: str = "username@hostname:~$ ",
        password_prompt: str | None = None,
        password: str | None = None,
    ) -> str:
        """Execute a command that changes the user or host prompt interactively.

        This helper writes ``command`` to the remote shell and then answers a
        sequence of interactive prompts (for example when performing an SSH
        jump, su, or changing to another user). The default sequence waits
        for a user@host style prompt and responds with a newline, but an
        optional password prompt can be provided and will be answered using
        the supplied ``password``.

        Parameters:
            command: the full command string to write to the remote shell
            user_at_host_prompt: the prompt string showing a changed user@host
            password_prompt: an optional prompt string expected when a
                             password is required
            password: the password to send when ``password_prompt`` is set

        Returns:
            The raw buffer of output collected while waiting for the
            configured prompts (the return value is primarily useful for
            debugging and logging).

        Raises:
            RuntimeError: if the session hasn't been started through the
                async context manager.
            ValueError: if a password prompt is provided but no password
                value was supplied.
        """
        if not self.process:
            raise RuntimeError("Session not started. Use 'async with' context.")

        if password_prompt is not None and password is None:
            raise ValueError("If password_prompt is provided, password must also be provided.")

        logger.info("Executing command: %s", command)
        self.process.stdin.write(f"{command}\n")
        await self.process.stdin.drain()

        prompt_lifo_queue = []
        prompt_lifo_queue.append((user_at_host_prompt, "\n"))
        if password_prompt:
            prompt_lifo_queue.append((password_prompt, f"{password}\n"))

        buffer = ""
        while prompt_lifo_queue:
            prompt, response = prompt_lifo_queue.pop()
            buffer += await self._read_until_and_log(prompt)
            self.process.stdin.write(response)
            await self.process.stdin.drain()

        logger.info("Command output: %s", buffer)
        return buffer

    async def execute_command(
        self,
        command: str,
        interactive_prompt: str | None = None,
        prompt_answer: str | None = None,
    ) -> str:
        """Execute a command on the remote shell and return its output.

        The command is executed in the interactive shell; a unique marker is
        appended so we can reliably detect when the command and any error
        messages have completed. The returned output has the marker lines
        filtered out.

        Parameters:
            command: the shell command to run (a trailing newline is added by
                     this method)
            interactive_prompt: optional prompt string to wait for before
                                sending ``prompt_answer`` (useful when a
                                command asks for confirmation or input)
            prompt_answer: the string to send in response to
                           ``interactive_prompt`` (required if
                           interactive_prompt is provided)

        Returns:
            The command's output with internal markers stripped out.

        Raises:
            RuntimeError: if the session isn't open (use 'async with').
            ValueError: if ``interactive_prompt`` is given but no
                        ``prompt_answer`` is supplied.
        """
        if not self.process:
            raise RuntimeError("Session not started. Use 'async with' context.")

        if interactive_prompt is not None and prompt_answer is None:
            raise ValueError("If interactive_prompt is provided, prompt_answer must also be provided.")

        marker = str(uuid4())
        marker_end_messages = [template.substitute(command=marker) for template in self.end_markers]
        full_command = f"{command}; {marker}\n"
        logger.info("Executing command: %s", full_command)
        self.process.stdin.write(full_command)
        await self.process.stdin.drain()

        buffer = ""
        if interactive_prompt:
            buffer += await self._read_until_and_log(interactive_prompt)
            self.process.stdin.write(f"{prompt_answer}\n")

        buffer += await self._read_until_and_log(marker_end_messages)
        lines = buffer.splitlines()
        clean_ouput = "\n".join(line for line in lines if marker not in line)
        logger.info("Command output: %s", clean_ouput)
        return clean_ouput
