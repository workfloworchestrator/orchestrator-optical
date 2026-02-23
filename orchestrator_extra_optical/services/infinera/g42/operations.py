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

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from services.infinera.g42.client import G42Client

# Registry to store all registered operations
_operation_registry: dict[str, type["OperationEndpoint"]] = {}


def register_operation(cls: type["OperationEndpoint"]) -> type["OperationEndpoint"]:
    r"""
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
    operation_name: str  # Name of the operation (e.g., "create_xcon")
    url_path: str  # RESTCONF operation URL path (e.g., "ioa-services:create-xcon")
    input_model: type[BaseModel]  # Pydantic model for input validation

    def __init__(self, client: "G42Client"):
        r"""
        Base class for RESTCONF operations.

        Subclasses must define:
        - `operation_name`: The name of the operation (used as the method name in `Operations`).
        - `url_path`: The RESTCONF operation URL path.
        - `InputModel`: A Pydantic model for input validation.
        """
        self.client = client

    def execute(self, **kwargs: Any) -> Any:
        r"""
        Execute the operation with validated input data.

        Args:
            **kwargs: Input data for the operation.

        Returns:
            The response from the RESTCONF API.
        """
        payload = self._build_payload(kwargs)
        return self.client._request("POST", f"/operations/{self.url_path}", json=payload)  # noqa: SLF001

    def _build_payload(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        r"""
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
class CreateXconOperation(OperationEndpoint):
    r"""
    Create a cross-connect (xcon).

    Example:
        operations.create_xcon(
            source="/ioa-ne:ne/facilities/ethernet[name='1-4-T1']",
            dst_parent_odu="1-4-L1-1-ODUCni",
            direction="two-way",
            payload_type="100GBE",
            label="example",
            dst_time_slots="1..80",
            circuit_id_suffix="f001c01",
        )
    """

    operation_name = "create_xcon"
    url_path = "ioa-services:create-xcon"

    class InputModel(BaseModel):  # noqa: D106
        model_config = ConfigDict(extra="forbid")

        source: str
        dst_parent_odu: str = Field(..., alias="dst-parent-odu")
        dst_time_slots: str = Field(..., alias="dst-time-slots")
        label: str
        direction: str = Field(None)
        payload_type: str = Field(None, alias="payload-type")
        circuit_id_suffix: str = Field(None, alias="circuit-id-suffix")

    input_model = InputModel


@register_operation
class UploadOperation(OperationEndpoint):
    r"""
    Uploads files to remote server.

    Example:
        operations.upload(
            filetype="database",
            destination="sftp://{{sftp_user}}@{{sftp_server}}:/absolute_dir_path/",
            is_async=True,
            skip_secure_verification=True,
            password="{{sftp_password}}"
        )
    """

    operation_name = "upload"
    url_path = "ioa-rpc:upload"

    class InputModel(BaseModel):  # noqa: D106
        model_config = ConfigDict(extra="forbid")

        filetype: Literal["database", "config", "file", "debug-log", "fdr-log", "pm-logs", "logs"] = Field(
            ..., alias="filetype"
        )

        destination: str | None = Field(
            None,
            alias="destination",
            pattern=r"((ftp|sftp|scp|file|https|http):/)?/[^\s/$.?#].[^\s]*",
            description="Destination of the upload ([sftp|scp|ftp|https|http|file]://[user@]hostname/directorypath/filename)",
        )
        file_server: str | None = Field(None, alias="file-server", description="Pre-configured file-server name")
        path: str | None = Field(
            None,
            alias="path",
            max_length=512,
            description=(
                "Path (directory and filename) to be used in the remote file-server."
                "If not provided, the file-server initial-path is used, with system defined filename."
                "If the path targets a directory (e.g. /path/ ), the filename is dynamically generated."
                "Otherwise, the user defined filename may use some placeholders %t and %m (representing"
                " timestamp and ne-name respectively)."
            ),
        )
        source: str | None = Field(
            None, alias="source", max_length=255, description="Source file path (only for filetype='file')"
        )

        is_async: bool = Field(False, alias="async", description="Uploads asynchronously")  # noqa: FBT003
        skip_secure_verification: bool = Field(
            False,  # noqa: FBT003
            alias="skip-secure-verification",
            description="Skip TLS/SSH host verification",
        )
        debug_entity: str | None = Field(
            None, alias="debug-entity", description="Instance identifier for the entity to collect logs from"
        )
        password: str | None = Field(
            None, alias="password", min_length=1, max_length=255, description="Protocol password"
        )
        optional_content: list[str] | None = Field(
            None, alias="optional-content", description="List of files to be included for debug-log upload"
        )
        log_file_list: list[str] | None = Field(
            None, alias="log-file-list", description="Specific list of log files to upload"
        )
        start_time: str | None = Field(None, alias="start-time", description="ISO timestamp or time interval string")
        db_instance: Literal["active", "inactive"] | None = Field(
            None, alias="db-instance", description="Selected DB instance"
        )

        @model_validator(mode="after")
        def validate_target_choice(self):
            """Either 'destination' OR 'file-server' must be present."""
            if not self.destination and not self.file_server:
                raise ValueError("Mandatory choice 'target': You must provide either 'destination' or 'file-server'.")
            return self

    input_model = InputModel


@register_operation
class CliCommandOperation(OperationEndpoint):
    r"""
    Runs one or more CLI commands via YANG RPC.
    Note: Execution is synchronous, so executing long scripts may take a while.

    Example:
        operations.cli_command(
            commands="show version\\nshow interfaces",
            echo="on",
            error_option="continue-on-error",
            replace=False
        )
    """

    operation_name = "cli_command"
    url_path = "ioa-rpc:cli-command"

    class InputModel(BaseModel):  # noqa: D106
        model_config = ConfigDict(extra="forbid")

        commands: str
        echo: Literal["on", "off"] = Field("off", alias="echo")
        error_option: Literal["stop-on-error", "continue-on-error", "rollback-on-error"] = Field(
            "stop-on-error", alias="error-option"
        )
        replace: bool = Field(False, alias="replace")  # noqa: FBT003

    input_model = InputModel


@register_operation
class DownloadOperation(OperationEndpoint):
    r"""
    Transfers a file from an external location to the NE.

    Example:
        operations.download(
            filetype="file",
            source="https://example.com/myfile.txt",
            destination="/local/path/myfile.txt",
        )
        # Or
        operations.download(
            filetype="peer-certificate",
            file_server="my-server",
            path="/certs/peer.pem",
            certificate_name="peer1",
            passphrase="secret",
        )
    """

    operation_name = "download"
    url_path = "ioa-rpc:download"

    class InputModel(BaseModel):  # noqa: D106
        model_config = ConfigDict(extra="forbid")

        filetype: str

        source: str | None = Field(
            None,
            alias="source",
            pattern=r"((ftp|sftp|scp|http|https|file):/)?/[^\s/$.?#].[^\s]*",
            min_length=1,
            max_length=1024,
        )
        file_server: str | None = Field(None, alias="file-server")
        path: str | None = Field(None, alias="path", max_length=512)

        passphrase: str | None = Field(None, alias="passphrase", min_length=1, max_length=1024)
        white_listed: bool = Field(False, alias="white-listed")  # noqa: FBT003
        certificate_name: str | None = Field(None, alias="certificate-name")
        unattended: bool = Field(False, alias="unattended")  # noqa: FBT003
        is_async: bool = Field(False, validation_alias="is-async", serialization_alias="async")  # noqa: FBT003
        skip_secure_verification: bool = Field(False, alias="skip-secure-verification")  # noqa: FBT003
        sanity_check_override: bool = Field(False, alias="sanity-check-override")  # noqa: FBT003
        destination: str | None = Field(None, alias="destination")
        password: str | None = Field(None, alias="password", min_length=1, max_length=255)
        db_action: Literal["empty-db", "rollback", "upgrade-db"] | None = Field(None, alias="db-action")

        @model_validator(mode="after")
        def validate_input(self):  # noqa: D102
            # Target choice
            if self.source is None:
                if self.file_server is None or self.path is None:
                    raise ValueError("Must provide either 'source' or both 'file-server' and 'path'")
            elif self.file_server is not None or self.path is not None:
                raise ValueError("'source' cannot be combined with 'file-server' or 'path'")
            # Conditional requirements
            if self.filetype in ("local-certificate", "peer-certificate") and self.passphrase is None:
                raise ValueError("passphrase is mandatory for 'local-certificate' or 'peer-certificate'")
            if (
                self.filetype in ("local-certificate", "trusted-certificate", "peer-certificate")
                and self.certificate_name is None
            ):
                raise ValueError(
                    "certificate-name is mandatory for 'local-certificate', 'trusted-certificate' or 'peer-certificate'"
                )
            # Strict when conditions
            if self.destination is not None and self.filetype != "file":
                raise ValueError("destination only applicable for filetype='file'")
            if bool(self.sanity_check_override) and self.filetype != "database":
                raise ValueError("sanity-check-override only for filetype='database'")
            if self.white_listed and self.filetype != "peer-certificate":
                raise ValueError("white-listed only for filetype='peer-certificate'")
            return self

    input_model = InputModel


@register_operation
class RestartOperation(OperationEndpoint):
    r"""
    Restarts a specific resource of the system (card, card sub-component e.g. DCO, tom).
    If resource not provided, defaults to restarting the node controller.

    Example:
        operations.restart(type="warm")
        operations.restart(resource="/ioa-ne:ne/cards/card[name='C1']", type="cold")
        operations.restart(resource="/ioa-ne:ne/cards/card[name='C1']", sub_component="DCO", type="warm")
    """

    operation_name = "restart"
    url_path = "ioa-rpc:restart"

    class InputModel(BaseModel):  # noqa: D106
        model_config = ConfigDict(extra="forbid")

        resource: str
        restart_type: Literal["warm", "cold", "shutdown"] = Field(
            validation_alias="restart-type", serialization_alias="type"
        )
        sub_component: str | None = Field(None, alias="sub-component")

    input_model = InputModel


class PmFilter(BaseModel):
    filter_id: int = Field(..., alias="filter-id")
    resource_instance: str | None = Field(None, alias="resource-instance")
    parameter: str | None = None
    direction: str | None = None
    location: str | None = None


@register_operation
class GetPmOperation(OperationEndpoint):
    r"""
    Auxiliary RPC to retrieve PM data.
    No parameters are mandatory; each provided parameter will be handled as a filter.
    Data can be filtered by:
     - resource instance
     - resource type
     - PM time period (15min, 24h, etc)
     - PM data type (current, history, real-time)
     - PM parameter name
    Multiple filters can be provided (e.g. provide PM data for entity x and entity y).

    Example:
    >>> operations.get_pm(filter=[{"filter_id": 1, "parameter": "gx:pre-fec-q"}])
        {
            "ioa-pm:output": {
                "number-of-result-records": 1,
                "additional-records-available": false,
                "retrieval-date-time": "2025-12-02T19:01:17Z",
                "pm-record": [
                    {
                        "period": "ioa-pm:pm-real-time",
                        "monitoring-date-time": "2025-12-02T18:18:39Z",
                        "resource": "/ioa-ne:ne/facilities/optical-carrier[name='1-4-L1-1']",
                        "resource-type": "ioa-common:optical-carrier",
                        "AID": "1-4-L1-1",
                        "parameter": "gx:pre-fec-q",
                        "direction": "ingress",
                        "location": "near-end",
                        "pm-value": "0.5000000",
                        "pm-value-min": "0.0000000",
                        "pm-value-max": "0.5000000",
                        "pm-value-avg": "0.4857876",
                        "pm-unit": "dB",
                        "validity": "suspect",
                        "bin": 0
                    }
                ]
            }
        }
    """

    operation_name = "get_pm"
    url_path = "ioa-pm:get-pm"

    class InputModel(BaseModel):  # noqa: D106
        model_config = ConfigDict(extra="forbid")

        data_type: Literal["current", "history", "real-time"] = Field("real-time", alias="data-type")
        filter: list[PmFilter] = Field(default_factory=list)
        period: dict | None = None
        number_of_records: int | None = Field(None, alias="number-of-records")
        skip_records: int | None = Field(None, alias="skip-records")
        pm_history_filter: dict | None = Field(None, alias="pm-history-filter")

        @model_validator(mode="after")
        def validate_when_conditions(self):  # noqa: D102
            if self.data_type != "real-time" and self.period is None:
                raise ValueError("'period' is required when data-type != 'real-time'")
            if self.data_type == "history" and self.pm_history_filter is None:
                raise ValueError("'pm-history-filter' is required when data-type = 'history'")
            return self

    input_model = InputModel


class Operations:
    def __init__(self, client: "G42Client"):
        r"""
        A dynamic interface for invoking RESTCONF operations.

        This class dynamically adds methods for each registered operation, allowing you to call them directly.

        Example:
            import G42Client
            g42 = G42Client("192.168.42.42")
            g42.operations.create_xcon(...)

        Args:
            client (G42Client): The RESTCONF client instance used to execute operations.
        """
        self.client = client
        self._register_operations()

    def __getattr__(self, name: str) -> Callable[..., Any]:
        r"""
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
        msg = f"{self.__class__.__name__!r} has no operation '{name}' registered."
        raise AttributeError(msg)

    def _register_operations(self):
        r"""
        Dynamically add methods for registered operations.

        Each registered operation is added as a method to this class, allowing it to be called directly.
        """
        for operation_name, operation_cls in _operation_registry.items():
            setattr(self, operation_name, self._create_operation_method(operation_cls))

    def _create_operation_method(self, operation_cls: type[OperationEndpoint]) -> Callable[..., Any]:
        r"""
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
