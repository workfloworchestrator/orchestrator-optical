from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import Node

if TYPE_CHECKING:
    from ..data_models import ioa_protection


class ProtectionSwitchNode(Node):
    """Navigator for RPC protection-switch"""

    def __call__(
        self, input_data: ioa_protection.ProtectionSwitchInput | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_protection import ProtectionSwitch, ProtectionSwitchInput

        if input_data is None:
            input_data = ProtectionSwitchInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ProtectionSwitchInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ProtectionSwitchInput.model_validate_json(input_data)

        rpc_data = ProtectionSwitch(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)
