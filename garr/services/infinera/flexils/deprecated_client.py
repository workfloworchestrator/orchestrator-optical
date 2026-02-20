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

import os
from typing import TYPE_CHECKING, Any, TypeVar

from services.infinera.flexils.commands.base import TL1BaseCommand, TL1BaseResponse, TL1CommandRegistry

if TYPE_CHECKING:
    from services.infinera.tnms.client import TnmsClient

T = TypeVar("T", bound=TL1BaseCommand)


# Define class attributes at module level
# removed auth info for sharing on public repo


class FlexILSClient:
    def __init__(self, tnms_client: "TnmsClient", tnms_device_uuid: str, device_tid: str):
        """Client for executing TL1 commands on FlexILS devices through TNMS.

        Note:
            Command methods are created dynamically during initialization based on
            the commands registered in TL1CommandRegistry. See their attributes in
            the respective command module under commands folder.
        """
        self.device_uuid = tnms_device_uuid
        self.device_tid = device_tid
        self.tnms_client = tnms_client
        self._init_command_methods()

    def __getattr__(self, name: str) -> Any:
        """
        Fallback dynamic method factory for TL1 commands.

        When an attribute is not found on the instance (i.e. not bound in
        __init__), this hook looks up `name` in the TL1CommandRegistry. If a
        matching command class exists, it returns a thin wrapper that will
        build and dispatch the TL1 command on demand. Otherwise it raises
        AttributeError as usual.

        Relation to _init_command_methods:
        - __getattr__ ensures that *all* registered commands can be invoked,
          even if they weren't bound up front.
        - Together with _init_command_methods, it provides both eager binding
          (for discoverability) and lazy fallback (for completeness).
        """
        cmd_cls = TL1CommandRegistry.commands.get(name)
        if cmd_cls:

            def method(**kwargs: Any) -> TL1BaseResponse:
                return self._execute_command(cmd_cls, **kwargs)

            return method
        msg = f"{self.__class__.__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    def execute_raw_commands(self, commands: list[str], error_policy: str = "ABORT") -> list[str]:
        """Execute a list of TL1 commands on a device."""
        full_commands = [
            f"ACT-USER:{self.device_tid}:{_username}:WFOTAG::{_password};",
            *commands,
            f"CANC-USER:{self.device_tid}:{_username}:WFOTAG;",
        ]
        response = self.tnms_client.operations.run_cli_script(
            [self.device_uuid], full_commands, channel="TL1", error_policy=error_policy
        )
        return [resp["output"] for resp in response["device-results"][0]["responses"][1:-1]]

    def execute_raw_command(self, command: str, correlation_tag: str) -> str:
        """Execute a TL1 command on a device."""
        commands = [
            f"ACT-USER:{self.device_tid}:{_username}:{correlation_tag}::{_password};",
            command,
            f"CANC-USER:{self.device_tid}:{_username}:{correlation_tag};",
        ]
        response = self.tnms_client.operations.run_cli_script(
            [self.device_uuid], commands, channel="TL1", error_policy="CONTINUE"
        )
        return response["device-results"][0]["responses"][1]["output"]

    def _execute_command(self, command_cls: type[T], **kwargs: Any) -> TL1BaseResponse:
        """Execute a TL1 command using its Pydantic model."""
        command = command_cls(tid=self.device_tid, **kwargs)
        return command.execute(self)

    def _init_command_methods(self) -> None:
        """
        Eagerly bind TL1 command methods on this instance.

        Iterates through all commands registered in TL1CommandRegistry and
        creates a real bound method on `self` for each. This:
          - Improves discoverability (dir(), IDE auto‐complete).
          - Avoids the tiny overhead of __getattr__ on common paths.
          - Still delegates actual execution via _execute_command.

        Relation to __getattr__:
        - Commands bound here will bypass __getattr__ entirely.
        - __getattr__ remains as a safety net for any future or dynamic
          commands added after initialization.
        """
        for method_name, command_class in TL1CommandRegistry.commands.items():
            # Create a closure to capture command_class
            def create_method(cmd_class):
                def method(**kwargs):
                    return self._execute_command(cmd_class, **kwargs)

                return method

            bound_method = create_method(command_class)
            bound_method.__name__ = method_name
            bound_method.__qualname__ = f"{self.__class__.__name__}.{method_name}"
            setattr(self, method_name, bound_method)
