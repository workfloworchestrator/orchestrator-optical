from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import Node

if TYPE_CHECKING:
    from ..data_models import ioa_services

class CreateXconNode(Node):
    """Navigator for RPC create-xcon"""

    def __call__(self, input_data: ioa_services.CreateXconInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_services import CreateXcon, CreateXconInput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = CreateXconInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CreateXconInput.model_validate_json(input_data)

        rpc_data = CreateXcon(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)
