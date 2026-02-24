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

from typing import TYPE_CHECKING, Any, Literal

from services.infinera.g30.data_models import get_data_model

if TYPE_CHECKING:
    from services.infinera.g30.client import G30Client
import urllib.parse

UUIDstr = str


class Endpoint:
    def __init__(
        self,
        client: "G30Client",
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

    def __call__(self, id: str | None = None) -> "Endpoint":
        """Allow for resource instance access like .port(port_id)"""
        if id is None:
            return self
        id = str(id)
        parts = id.split(",")
        encoded_parts = [urllib.parse.quote(part, safe="") for part in parts]
        id = ",".join(encoded_parts)
        new_path = f"{self._current_path}={id}"
        return Endpoint(self._client, new_path, self._parent_path)

    def __getattr__(self, name: str) -> "Endpoint":
        """Enable dynamic endpoint traversal"""
        name = name.replace("_", "-")
        return Endpoint(self._client, name, self._full_path)

    def retrieve(
        self,
        content: Literal["config", "nonconfig", "all"] = "all",
        with_defaults: Literal[
            "report-all", "trim", "report-all-tagged"
        ] = "report-all",
        depth: int | str = "unbounded",
    ):
        """Get resources with optional query params"""
        params = {
            "content": content,
            "depth": depth,
            "with-defaults": with_defaults,
        }
        response = self._client._request("GET", self._full_path, params=params)

        if len(response) == 1 and isinstance(response, dict):
            response = next(iter(response.values()))

        return response

    def modify(self, **kwargs: Any) -> None:
        """Modify a resource"""
        data = {k.replace("_", "-"): v for k, v in kwargs.items()}
        if "=" in self._current_path:
            resource_name, resource_id = self._current_path.split("=")
        else:
            resource_name, resource_id = self._current_path, None

        if resource_id:
            data[f"{resource_name}-id"] = resource_id
            data = {
                resource_name: [
                    data,
                ]
            }
        else:
            data = {
                resource_name: data,
            }
        model_name = resource_name.replace("-", "")
        model = get_data_model(model_name)
        validated_data = model(**data)
        data = validated_data.model_dump(by_alias=True, exclude_unset=True)
        self._client._request("PATCH", self._full_path, json=data)

    def create(self, **kwargs: Any) -> None:
        """Create a new resource"""
        data = {k.replace("_", "-"): v for k, v in kwargs.items()}
        if "=" in self._current_path:
            resource_name, resource_id = self._current_path.split("=")
            raise ValueError(f"Cannot create a resource on a specific instance. Use the parent path {self._parent_path}/{resource_name}.")
        resource_name = self._current_path

        data = {
            resource_name: [
                data,
            ]
        }

        model_name = resource_name.replace("-", "")
        model = get_data_model(model_name)
        validated_data = model(**data)
        data = validated_data.model_dump(by_alias=True, exclude_unset=True)

        self._client._request("POST", self._parent_path, json=data)

    def replace(self, **kwargs: Any) -> None:
        """Replace a resource"""
        raise NotImplementedError  # FIXME

    def delete(self) -> None:
        """Delete a resource"""
        if "=" not in self._current_path:
            msg = "Cannot delete a resource without specifying an instance."
            raise ValueError(msg)
        self._client._request("DELETE", self._full_path)


class Data(Endpoint):
    _RESOURCES = {
        "ne": "ne:ne",
    }

    def __init__(self, client: "G30Client"):
        super().__init__(client, "data/", "")

        # Initialize main API sections
        for section, path in self._RESOURCES.items():
            setattr(
                self,
                section,
                Endpoint(client=client, current_path=path, parent_path=self._full_path),
            )
