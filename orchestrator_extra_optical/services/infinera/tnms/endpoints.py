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

from copy import deepcopy
from time import sleep
from typing import TYPE_CHECKING, Any, Literal

from services.infinera.tnms.exceptions import ApiError

if TYPE_CHECKING:
    from services.infinera.tnms.client import TnmsClient

UUIDstr = str


class Endpoint:
    def __init__(
        self,
        client: "TnmsClient",
        current_path: str = "",
        parent_path: str = "",
    ):
        self._client = client
        self._current_path = current_path.strip("/")
        self._parent_path = parent_path.rstrip("/")
        self._full_path = self._resolve_path()

    def _resolve_path(self) -> str:
        """Resolve the actual RESTCONF path"""
        return "/".join([self._parent_path, self._current_path])

    def __call__(self, uuid: str | None = None) -> "Endpoint":
        """Allow for resource instance access like .devices(uuid)"""
        if uuid is None:
            return self
        new_path = f"{self._current_path}={uuid}"
        return Endpoint(self._client, new_path, self._parent_path)

    def __getattr__(self, name: str) -> "Endpoint":
        """Enable dynamic endpoint traversal"""
        if name.endswith("s") and not self._current_path.endswith("s"):
            # Handle collection plurals (e.g., devices → device)
            name = name[:-1]
        name = name.replace("_", "-")
        return Endpoint(self._client, name, self._full_path)

    def retrieve(self, fields: list[str] | None = None, depth: int | None = None):
        """Get resources with optional field filtering and depth"""
        params = {}
        field_str = None
        if "=" not in self._current_path:
            base_resource = self._current_path
            self._full_path = self._parent_path
            field_str = base_resource
            if fields:
                field_str += f"({';'.join(fields)})"
        elif fields:
            field_str = f"({';'.join(fields)})"

        if field_str:
            params["fields"] = field_str

        if depth is not None:
            params["depth"] = str(depth)

        response = self._client._request("GET", self._full_path, params=params)
        while len(response) == 1:  # Unwrap single value responses
            if isinstance(response, dict):
                response = next(iter(response.values()))
            elif isinstance(response, list):
                response = response[0]
        return response


class Data(Endpoint):
    RESOURCES = {
        "equipment": "tapi-equipment:physical-context",
        "topology": "tapi-topology:topology-context",
        "connectivity": "tapi-connectivity:connectivity-context",
        "notification": "tapi-notification:notification-context",
        "job": "infn-job:job-context",
    }

    def __init__(self, client: "TnmsClient"):
        super().__init__(client, "data/tapi-common:context", "")

        # Initialize main API sections
        for section, path in self.RESOURCES.items():
            setattr(
                self,
                section,
                Endpoint(client=client, current_path=path, parent_path=self._full_path),
            )


class Operations:
    def __init__(self, client: "TnmsClient"):
        self.client = client
        self.base_path = "/operations"

    def get_cli_script_result(
        self,
        job_id: int,
        max_retries: int = 10,
        base_delay: float = 0.1,
    ) -> dict[str, Any]:
        """Retrieves CLI job results with exponential backoff retry mechanism.

        Args:
            job_id (int): The ID of the job to retrieve results for
            max_retries (int): Maximum number of retry attempts
            base_delay (float): Base delay between retries in seconds

        Returns:
            CliScriptResponse: The job output containing status and results

        Raises:
            Exception: If job retrieval fails after max retries

        ---

        Example raw response:
            {
            "tapi-equipment-extensions-cli:output":
                {
                    "device-results": [
                        {
                            "device-ref": "ebde41fe-b851-389a-a557-b48c400c2db4",
                            "responses": [
                                {
                                    "output": "command execution here",
                                    "status": "FINISHED" (or "FAILED")
                                }
                            ]
                        }
                    ],
                    "id": job_id,
                    "status": "FINISHED" (or "FAILED" or "RUNNING")
                }
            }
        """
        endpoint = self.base_path + "/tapi-equipment-extensions-cli:get-cli-script-result/"
        data = {"tapi-equipment-extensions-cli:input": {"id": job_id}}

        retries = 0
        while retries < max_retries:
            response = self.client._request("POST", endpoint, json=data)
            output = response["tapi-equipment-extensions-cli:output"]
            status = output["status"]

            if status == "FINISHED":
                return output
            if status in ["RUNNING", "PENDING"]:
                retries += 1
                sleep(base_delay * (2**retries))
            else:
                raise ApiError(400, output)

        error_message = f"Job retrieval failed after {max_retries} retries"
        raise ApiError(400, error_message)

    def run_cli_script(
        self,
        device_list: list[UUIDstr],
        command_list: list[str],
        channel: str = "TL1",
        error_policy: Literal["ABORT", "CONTINUE"] = "ABORT",
    ) -> dict[str, Any]:
        """Execute a list of commands on a list of devices."""
        masked_command_list = deepcopy(command_list)
        if command_list[0].startswith("ACT-USER"):
            masked_command_list = command_list[1:]
        if command_list[-1].startswith("CANC-USER"):
            masked_command_list = masked_command_list[:-1]

        body = {
            "tapi-equipment-extensions-cli:input": {
                "device-list": device_list,
                "commands": command_list,
                "channel": channel,
                "error-policy": error_policy,
            }
        }

        masked_body = deepcopy(body)
        masked_body["tapi-equipment-extensions-cli:input"]["commands"] = masked_command_list

        response = self.client._request(
            "POST",
            self.base_path + "/tapi-equipment-extensions-cli:run-cli-script/",
            log_mask=masked_body,
            json=body,
        )

        job_id = response["tapi-equipment-extensions-cli:output"]["id"]
        return self.get_cli_script_result(job_id)
