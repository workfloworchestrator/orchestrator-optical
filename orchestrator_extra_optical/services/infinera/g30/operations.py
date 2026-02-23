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
import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .client import G30Client

# Registry to store all registered operations
_operation_registry: dict[str, type["OperationEndpoint"]] = {}


def register_operation(cls: type["OperationEndpoint"]) -> type["OperationEndpoint"]:
    """
    Decorator to register an operation class.

    This allows the `Operations` class to dynamically add methods for each registered operation.

    Args:
        cls: The operation class to register.

    Returns:
        The registered operation class.
    """
    _operation_registry[cls.operation_name] = cls
    return cls


class OperationEndpoint:
    """
    Base class for RESTCONF operations.

    Subclasses must define:
    - `operation_name`: The name of the operation (used as the method name in `Operations`).
    - `url_path`: The RESTCONF operation URL path.
    - `InputModel`: A Pydantic model for input validation.
    """

    operation_name: str  # Name of the operation (e.g., "create_xcon")
    url_path: str  # RESTCONF operation URL path (e.g., "ioa-services:create-xcon")
    input_model: type[BaseModel]  # Pydantic model for input validation

    def __init__(self, client: "G30Client"):
        self.client = client

    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the operation with validated input data.

        Args:
            **kwargs: Input data for the operation.

        Returns:
            The response from the RESTCONF API.
        """
        payload = self._build_payload(kwargs)
        return self.client._request("POST", f"/operations/{self.url_path}", json=payload)

    def _build_payload(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and build the payload for the operation.

        Args:
            kwargs: Input data for the operation.

        Returns:
            A dictionary representing the validated payload.
        """
        # Convert snake_case to kebab-case for input keys
        data = {k.replace("_", "-"): v for k, v in kwargs.items()}
        validated_data = self.input_model(**data).model_dump(by_alias=True, exclude_unset=True)
        return {"input": validated_data}


@register_operation
class UploadOperation(OperationEndpoint):
    """
    Backup the database.

    Example:
        operations.backup_db(backup_name="daily_backup")
    """

    operation_name = "upload"
    url_path = "coriant-rpc:upload"

    class InputModel(BaseModel):
        file_description: str | None = None
        filetype: str
        destination: str
        password: str

    input_model = InputModel


@register_operation
class DownloadOperation(OperationEndpoint):
    """
    Download a file.

    Example:
        operations.backup_db(backup_name="daily_backup")
    """

    operation_name = "download"
    url_path = "coriant-rpc:download"

    class InputModel(BaseModel):
        file_description: str | None = None
        filetype: str
        source: str
        password: str

    input_model = InputModel


@register_operation
class PingOperation(OperationEndpoint):
    """
    Ping a device.

    Example:
        operations.backup_db(backup_name="daily_backup")
    """

    operation_name = "ping"
    url_path = "coriant-rpc:ping"

    class InputModel(BaseModel):
        ping_dest: str
        ping_count: int

    input_model = InputModel


@register_operation
class ActivateOperation(OperationEndpoint):
    """
    Download a file.

    Example:
        operations.backup_db(backup_name="daily_backup")
    """

    operation_name = "activate"
    url_path = "coriant-rpc:activate-file"

    class InputModel(BaseModel):
        filetype: str
        restart_type: str | None = None
        db_action: str | None = None

    input_model = InputModel


@register_operation
class RestartOperation(OperationEndpoint):
    """
    Restart a device.

    Example:
        operations.restart(entity_id="ne:ne", restart_type="warm")
    """

    operation_name = "restart"
    url_path = "coriant-rpc:restart"

    class InputModel(BaseModel):
        entity_id: str = Field(..., alias="entity-id")
        restart_type: str = Field(..., alias="restart-type")
        fpga_upgrade: None = Field(None, alias="fpga-upgrade")
        dsp_upgrade: None = Field(None, alias="dsp-upgrade")

    input_model = InputModel


@register_operation
class CliCommandOperation(OperationEndpoint):
    r"""
    Execute a CLI command.
    To the command is appended the | display json option.

    Example:
        operations.cli_command("show card")
    """

    operation_name = "cli_command"
    url_path = "coriant-rpc:cli-command"

    class InputModel(BaseModel):
        commands: str
        echo: Literal["on", "off"] = "off"
        error_option: Literal["stop-on-error", "continue-on-error", "rollback-on-error"] = Field(
            "stop-on-error", alias="error-option"
        )
        replace: bool = False

    input_model = InputModel

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        r"""
        Execute a CLI commands.
        To the command is appended the | display json option.

        Example:
            operations.cli_command("show card")
        """
        kwargs["commands"] = kwargs["commands"].strip() + " | display json"
        payload = self._build_payload(kwargs)
        response = self.client._request("POST", f"/operations/{self.url_path}", json=payload)
        if (
            response == {}
            or response["coriant-rpc:output"]["result"] == "\n"
            or "object does not exist" in response["coriant-rpc:output"]["result"]
        ):
            return {}

        if "ERROR" in response["coriant-rpc:output"]["result"]:
            msg = f"Error in CLI command \n payload: {payload} \n response: {response}"
            raise RuntimeError(msg)

        raw_string = response["coriant-rpc:output"]["result"]

        def handle_duplicates(pairs):
            d = {}
            for key, value in pairs:
                if key in d:
                    # If the key already exists, ensure the value is a list and append
                    if isinstance(d[key], list):
                        d[key].append(value)
                    else:
                        # Convert the existing single value to a list and append the new one
                        d[key] = [d[key], value]
                else:
                    d[key] = value
            return d

        return json.loads(raw_string, object_pairs_hook=handle_duplicates)


class Operations:
    """
    A dynamic interface for invoking RESTCONF operations.

    This class dynamically adds methods for each registered operation, allowing you to call them directly.

    Example:
        import G42Client
        g42 = G42Client("192.168.42.42")
        g42.operations.create_xcon(...)

    Args:
        client (G42Client): The RESTCONF client instance used to execute operations.
    """

    def __init__(self, client: "G30Client"):
        self.client = client
        self._register_operations()

    def __getattr__(self, name: str) -> Callable[..., Any]:
        """
        Provide dynamic access to registered operations.

        This method supports IDE static analysis tools and fallback access to dynamically
        registered operations. At runtime, all methods are registered in __init__ with _register_operations.
        If you are looking for the definition of a specific method, search its name in this file.

        Args:
            name (str): The name of the operation.

        Returns:
            Callable: A method to invoke the operation.

        Raises:
            AttributeError: If the operation is not registered.
        """
        if name in _operation_registry:
            return self._create_operation_method(_operation_registry[name])
        raise AttributeError(f"{self.__class__.__name__!r} has no operation '{name}' registered.")

    def _register_operations(self):
        """
        Dynamically add methods for registered operations.

        Each registered operation is added as a method to this class, allowing it to be called directly.
        """
        for operation_name, operation_cls in _operation_registry.items():
            setattr(self, operation_name, self._create_operation_method(operation_cls))

    def _create_operation_method(self, operation_cls: type[OperationEndpoint]) -> Callable[..., Any]:
        """
        Create a method for a specific operation.

        Args:
            operation_cls (type[OperationEndpoint]): The operation class to create a method for.

        Returns:
            Callable: A method that instantiates and executes the operation using the client.
        """

        def operation_method(**kwargs):
            operation_instance = operation_cls(self.client)
            return operation_instance.execute(**kwargs)

        operation_method.__doc__ = f"Invoke the `{operation_cls.operation_name}` operation."
        return operation_method
