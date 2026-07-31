from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import coriant_rpc


class NoOpNode(Node):
    """Navigator for RPC no-op"""

    def __call__(self) -> None:
        resp = self._client._request("POST", self._path)


class DefaultNode(Node):
    """Navigator for RPC default"""

    def __call__(
        self, input_data: coriant_rpc.DefaultInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.DefaultOutput:
        from ..data_models.coriant_rpc import Default, DefaultInput, DefaultOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = DefaultInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DefaultInput.model_validate_json(input_data)

        rpc_data = Default(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return DefaultOutput.model_validate(data)


class DownloadNode(Node):
    """Navigator for RPC download"""

    def __call__(
        self, input_data: coriant_rpc.DownloadInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.DownloadOutput:
        from ..data_models.coriant_rpc import Download, DownloadInput, DownloadOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = DownloadInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DownloadInput.model_validate_json(input_data)

        rpc_data = Download(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return DownloadOutput.model_validate(data)


class FileNode(Node):
    """Navigator for RPC file"""

    def __call__(
        self, input_data: coriant_rpc.FileInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.FileOutput:
        from ..data_models.coriant_rpc import File, FileInput, FileOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = FileInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = FileInput.model_validate_json(input_data)

        rpc_data = File(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return FileOutput.model_validate(data)


class CertGenNode(Node):
    """Navigator for RPC cert-gen"""

    def __call__(
        self, input_data: coriant_rpc.CertGenInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.CertGenOutput:
        from ..data_models.coriant_rpc import CertGen, CertGenInput, CertGenOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = CertGenInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CertGenInput.model_validate_json(input_data)

        rpc_data = CertGen(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return CertGenOutput.model_validate(data)


class RestartNode(Node):
    """Navigator for RPC restart"""

    def __call__(
        self, input_data: coriant_rpc.RestartInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.RestartOutput:
        from ..data_models.coriant_rpc import Restart, RestartInput, RestartOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = RestartInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RestartInput.model_validate_json(input_data)

        rpc_data = Restart(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return RestartOutput.model_validate(data)


class UploadNode(Node):
    """Navigator for RPC upload"""

    def __call__(
        self, input_data: coriant_rpc.UploadInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.UploadOutput:
        from ..data_models.coriant_rpc import Upload, UploadInput, UploadOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = UploadInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = UploadInput.model_validate_json(input_data)

        rpc_data = Upload(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return UploadOutput.model_validate(data)


class SetTimeNode(Node):
    """Navigator for RPC set-time"""

    def __call__(
        self, input_data: coriant_rpc.SetTimeInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.SetTimeOutput:
        from ..data_models.coriant_rpc import SetTime, SetTimeInput, SetTimeOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = SetTimeInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SetTimeInput.model_validate_json(input_data)

        rpc_data = SetTime(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return SetTimeOutput.model_validate(data)


class EnableLedNode(Node):
    """Navigator for RPC enable-led"""

    def __call__(
        self, input_data: coriant_rpc.EnableLedInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.EnableLedOutput:
        from ..data_models.coriant_rpc import EnableLed, EnableLedInput, EnableLedOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = EnableLedInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = EnableLedInput.model_validate_json(input_data)

        rpc_data = EnableLed(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return EnableLedOutput.model_validate(data)


class DisableLedNode(Node):
    """Navigator for RPC disable-led"""

    def __call__(
        self, input_data: coriant_rpc.DisableLedInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.DisableLedOutput:
        from ..data_models.coriant_rpc import DisableLed, DisableLedInput, DisableLedOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = DisableLedInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DisableLedInput.model_validate_json(input_data)

        rpc_data = DisableLed(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return DisableLedOutput.model_validate(data)


class StartOtdrMeasurementNode(Node):
    """Navigator for RPC start-otdr-measurement"""

    def __call__(
        self, input_data: coriant_rpc.StartOtdrMeasurementInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.StartOtdrMeasurementOutput:
        from ..data_models.coriant_rpc import (
            StartOtdrMeasurement,
            StartOtdrMeasurementInput,
            StartOtdrMeasurementOutput,
        )

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = StartOtdrMeasurementInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = StartOtdrMeasurementInput.model_validate_json(input_data)

        rpc_data = StartOtdrMeasurement(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return StartOtdrMeasurementOutput.model_validate(data)


class StopOtdrMeasurementNode(Node):
    """Navigator for RPC stop-otdr-measurement"""

    def __call__(
        self, input_data: coriant_rpc.StopOtdrMeasurementInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.StopOtdrMeasurementOutput:
        from ..data_models.coriant_rpc import StopOtdrMeasurement, StopOtdrMeasurementInput, StopOtdrMeasurementOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = StopOtdrMeasurementInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = StopOtdrMeasurementInput.model_validate_json(input_data)

        rpc_data = StopOtdrMeasurement(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return StopOtdrMeasurementOutput.model_validate(data)


class Activate3rdpartyFwNode(Node):
    """Navigator for RPC activate-3rdparty-fw"""

    def __call__(
        self, input_data: coriant_rpc.Activate3rdpartyFwInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.Activate3rdpartyFwOutput:
        from ..data_models.coriant_rpc import Activate3rdpartyFw, Activate3rdpartyFwInput, Activate3rdpartyFwOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = Activate3rdpartyFwInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = Activate3rdpartyFwInput.model_validate_json(input_data)

        rpc_data = Activate3rdpartyFw(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return Activate3rdpartyFwOutput.model_validate(data)


class ActivateFileNode(Node):
    """Navigator for RPC activate-file"""

    def __call__(
        self, input_data: coriant_rpc.ActivateFileInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ActivateFileOutput:
        from ..data_models.coriant_rpc import ActivateFile, ActivateFileInput, ActivateFileOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ActivateFileInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ActivateFileInput.model_validate_json(input_data)

        rpc_data = ActivateFile(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ActivateFileOutput.model_validate(data)


class ClearLogNode(Node):
    """Navigator for RPC clear-log"""

    def __call__(
        self, input_data: coriant_rpc.ClearLogInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ClearLogOutput:
        from ..data_models.coriant_rpc import ClearLog, ClearLogInput, ClearLogOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ClearLogInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearLogInput.model_validate_json(input_data)

        rpc_data = ClearLog(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ClearLogOutput.model_validate(data)


class ClearDatabaseNode(Node):
    """Navigator for RPC clear-database"""

    def __call__(
        self, input_data: coriant_rpc.ClearDatabaseInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ClearDatabaseOutput:
        from ..data_models.coriant_rpc import ClearDatabase, ClearDatabaseInput, ClearDatabaseOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ClearDatabaseInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearDatabaseInput.model_validate_json(input_data)

        rpc_data = ClearDatabase(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ClearDatabaseOutput.model_validate(data)


class PingNode(Node):
    """Navigator for RPC ping"""

    def __call__(
        self, input_data: coriant_rpc.PingInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.PingOutput:
        from ..data_models.coriant_rpc import Ping, PingInput, PingOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = PingInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = PingInput.model_validate_json(input_data)

        rpc_data = Ping(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return PingOutput.model_validate(data)


class TracerouteNode(Node):
    """Navigator for RPC traceroute"""

    def __call__(
        self, input_data: coriant_rpc.TracerouteInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.TracerouteOutput:
        from ..data_models.coriant_rpc import Traceroute, TracerouteInput, TracerouteOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = TracerouteInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = TracerouteInput.model_validate_json(input_data)

        rpc_data = Traceroute(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return TracerouteOutput.model_validate(data)


class UpdatePskMapNode(Node):
    """Navigator for RPC update-psk-map"""

    def __call__(
        self, input_data: coriant_rpc.UpdatePskMapInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.UpdatePskMapOutput:
        from ..data_models.coriant_rpc import UpdatePskMap, UpdatePskMapInput, UpdatePskMapOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = UpdatePskMapInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = UpdatePskMapInput.model_validate_json(input_data)

        rpc_data = UpdatePskMap(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return UpdatePskMapOutput.model_validate(data)


class FilterItemNode(ItemNode):
    """Navigator for list item filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> coriant_rpc.FilterItem:
        from ..data_models.coriant_rpc import FilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FilterItem.model_validate(resp)

    def update(self, data: coriant_rpc.FilterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import FilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FilterItem.model_validate(data)
        elif isinstance(data, str):
            data = FilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: coriant_rpc.FilterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import FilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FilterItem.model_validate(data)
        elif isinstance(data, str):
            data = FilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FilterListNode(ListNode[FilterItemNode]):
    """Navigator for list filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[coriant_rpc.FilterItem]:
        from ..data_models.coriant_rpc import FilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FilterItem.model_validate(item) for item in resp]

    def create(self, data: list[coriant_rpc.FilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[coriant_rpc.FilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class PmDataItemNode(ItemNode):
    """Navigator for list item pm-data"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> coriant_rpc.PmDataItem:
        from ..data_models.coriant_rpc import PmDataItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmDataItem.model_validate(resp)

    def update(self, data: coriant_rpc.PmDataItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import PmDataItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmDataItem.model_validate(data)
        elif isinstance(data, str):
            data = PmDataItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: coriant_rpc.PmDataItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import PmDataItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmDataItem.model_validate(data)
        elif isinstance(data, str):
            data = PmDataItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmDataListNode(ListNode[PmDataItemNode]):
    """Navigator for list pm-data"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[coriant_rpc.PmDataItem]:
        from ..data_models.coriant_rpc import PmDataItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmDataItem.model_validate(item) for item in resp]

    def create(self, data: list[coriant_rpc.PmDataItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[coriant_rpc.PmDataItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GetPmNode(Node):
    """Navigator for RPC get-pm"""

    def __call__(
        self, input_data: coriant_rpc.GetPmInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.GetPmOutput:
        from ..data_models.coriant_rpc import GetPm, GetPmInput, GetPmOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = GetPmInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetPmInput.model_validate_json(input_data)

        rpc_data = GetPm(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return GetPmOutput.model_validate(data)


class PmEntityListItemNode(ItemNode):
    """Navigator for list item pm-entity-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> coriant_rpc.PmEntityListItem:
        from ..data_models.coriant_rpc import PmEntityListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmEntityListItem.model_validate(resp)

    def update(self, data: coriant_rpc.PmEntityListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import PmEntityListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmEntityListItem.model_validate(data)
        elif isinstance(data, str):
            data = PmEntityListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: coriant_rpc.PmEntityListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import PmEntityListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmEntityListItem.model_validate(data)
        elif isinstance(data, str):
            data = PmEntityListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmEntityListListNode(ListNode[PmEntityListItemNode]):
    """Navigator for list pm-entity-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[coriant_rpc.PmEntityListItem]:
        from ..data_models.coriant_rpc import PmEntityListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmEntityListItem.model_validate(item) for item in resp]

    def create(self, data: list[coriant_rpc.PmEntityListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[coriant_rpc.PmEntityListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ClearPmDataNode(Node):
    """Navigator for RPC clear-pm-data"""

    def __call__(
        self, input_data: coriant_rpc.ClearPmDataInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ClearPmDataOutput:
        from ..data_models.coriant_rpc import ClearPmData, ClearPmDataInput, ClearPmDataOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ClearPmDataInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearPmDataInput.model_validate_json(input_data)

        rpc_data = ClearPmData(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ClearPmDataOutput.model_validate(data)


class ClearStatisticsDataNode(Node):
    """Navigator for RPC clear-statistics-data"""

    def __call__(
        self, input_data: coriant_rpc.ClearStatisticsDataInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ClearStatisticsDataOutput:
        from ..data_models.coriant_rpc import ClearStatisticsData, ClearStatisticsDataInput, ClearStatisticsDataOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ClearStatisticsDataInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearStatisticsDataInput.model_validate_json(input_data)

        rpc_data = ClearStatisticsData(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ClearStatisticsDataOutput.model_validate(data)


class ClearCertificateNode(Node):
    """Navigator for RPC clear-certificate"""

    def __call__(
        self, input_data: coriant_rpc.ClearCertificateInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ClearCertificateOutput:
        from ..data_models.coriant_rpc import ClearCertificate, ClearCertificateInput, ClearCertificateOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ClearCertificateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearCertificateInput.model_validate_json(input_data)

        rpc_data = ClearCertificate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ClearCertificateOutput.model_validate(data)


class ClearTrustedCertificateNode(Node):
    """Navigator for RPC clear-trusted-certificate"""

    def __call__(
        self, input_data: coriant_rpc.ClearTrustedCertificateInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ClearTrustedCertificateOutput:
        from ..data_models.coriant_rpc import (
            ClearTrustedCertificate,
            ClearTrustedCertificateInput,
            ClearTrustedCertificateOutput,
        )

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ClearTrustedCertificateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearTrustedCertificateInput.model_validate_json(input_data)

        rpc_data = ClearTrustedCertificate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ClearTrustedCertificateOutput.model_validate(data)


class SshKeygenNode(Node):
    """Navigator for RPC ssh-keygen"""

    def __call__(
        self, input_data: coriant_rpc.SshKeygenInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.SshKeygenOutput:
        from ..data_models.coriant_rpc import SshKeygen, SshKeygenInput, SshKeygenOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = SshKeygenInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SshKeygenInput.model_validate_json(input_data)

        rpc_data = SshKeygen(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return SshKeygenOutput.model_validate(data)


class PasswordNode(Node):
    """Navigator for RPC password"""

    def __call__(
        self, input_data: coriant_rpc.PasswordInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.PasswordOutput:
        from ..data_models.coriant_rpc import Password, PasswordInput, PasswordOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = PasswordInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = PasswordInput.model_validate_json(input_data)

        rpc_data = Password(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return PasswordOutput.model_validate(data)


class ResetTestSignalStatusNode(Node):
    """Navigator for RPC reset-test-signal-status"""

    def __call__(
        self, input_data: coriant_rpc.ResetTestSignalStatusInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ResetTestSignalStatusOutput:
        from ..data_models.coriant_rpc import (
            ResetTestSignalStatus,
            ResetTestSignalStatusInput,
            ResetTestSignalStatusOutput,
        )

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ResetTestSignalStatusInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ResetTestSignalStatusInput.model_validate_json(input_data)

        rpc_data = ResetTestSignalStatus(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ResetTestSignalStatusOutput.model_validate(data)


class CreateCardServicesNode(Node):
    """Navigator for RPC create-card-services"""

    def __call__(
        self, input_data: coriant_rpc.CreateCardServicesInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.CreateCardServicesOutput:
        from ..data_models.coriant_rpc import CreateCardServices, CreateCardServicesInput, CreateCardServicesOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = CreateCardServicesInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CreateCardServicesInput.model_validate_json(input_data)

        rpc_data = CreateCardServices(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return CreateCardServicesOutput.model_validate(data)


class DeleteCardServicesNode(Node):
    """Navigator for RPC delete-card-services"""

    def __call__(
        self, input_data: coriant_rpc.DeleteCardServicesInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.DeleteCardServicesOutput:
        from ..data_models.coriant_rpc import DeleteCardServices, DeleteCardServicesInput, DeleteCardServicesOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = DeleteCardServicesInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DeleteCardServicesInput.model_validate_json(input_data)

        rpc_data = DeleteCardServices(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return DeleteCardServicesOutput.model_validate(data)


class IfconfigNode(Node):
    """Navigator for RPC ifconfig"""

    def __call__(
        self, input_data: coriant_rpc.IfconfigInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.IfconfigOutput:
        from ..data_models.coriant_rpc import Ifconfig, IfconfigInput, IfconfigOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = IfconfigInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = IfconfigInput.model_validate_json(input_data)

        rpc_data = Ifconfig(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return IfconfigOutput.model_validate(data)


class Delete2Node(Node):
    """Navigator for RPC delete2"""

    def __call__(self, input_data: coriant_rpc.Delete2Input | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import Delete2, Delete2Input

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = Delete2Input.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = Delete2Input.model_validate_json(input_data)

        rpc_data = Delete2(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class CreateRollbackPointNode(Node):
    """Navigator for RPC create-rollback-point"""

    def __call__(
        self, input_data: coriant_rpc.CreateRollbackPointInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.CreateRollbackPointOutput:
        from ..data_models.coriant_rpc import CreateRollbackPoint, CreateRollbackPointInput, CreateRollbackPointOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = CreateRollbackPointInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CreateRollbackPointInput.model_validate_json(input_data)

        rpc_data = CreateRollbackPoint(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return CreateRollbackPointOutput.model_validate(data)


class DiffNode(Node):
    """Navigator for RPC diff"""

    def __call__(
        self, input_data: coriant_rpc.DiffInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.DiffOutput:
        from ..data_models.coriant_rpc import Diff, DiffInput, DiffOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = DiffInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DiffInput.model_validate_json(input_data)

        rpc_data = Diff(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return DiffOutput.model_validate(data)


class RollbackNode(Node):
    """Navigator for RPC rollback"""

    def __call__(
        self, input_data: coriant_rpc.RollbackInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.RollbackOutput:
        from ..data_models.coriant_rpc import Rollback, RollbackInput, RollbackOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = RollbackInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RollbackInput.model_validate_json(input_data)

        rpc_data = Rollback(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return RollbackOutput.model_validate(data)


class ProtectionSwitchNode(Node):
    """Navigator for RPC protection-switch"""

    def __call__(
        self, input_data: coriant_rpc.ProtectionSwitchInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.ProtectionSwitchOutput:
        from ..data_models.coriant_rpc import ProtectionSwitch, ProtectionSwitchInput, ProtectionSwitchOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = ProtectionSwitchInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ProtectionSwitchInput.model_validate_json(input_data)

        rpc_data = ProtectionSwitch(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return ProtectionSwitchOutput.model_validate(data)


class CliCommandNode(Node):
    """Navigator for RPC cli-command"""

    def __call__(
        self, input_data: coriant_rpc.CliCommandInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.CliCommandOutput:
        from ..data_models.coriant_rpc import CliCommand, CliCommandInput, CliCommandOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = CliCommandInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CliCommandInput.model_validate_json(input_data)

        rpc_data = CliCommand(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return CliCommandOutput.model_validate(data)


class MeasureNode(Node):
    """Navigator for RPC measure"""

    def __call__(
        self, input_data: coriant_rpc.MeasureInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.MeasureOutput:
        from ..data_models.coriant_rpc import Measure, MeasureInput, MeasureOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = MeasureInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = MeasureInput.model_validate_json(input_data)

        rpc_data = Measure(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return MeasureOutput.model_validate(data)


class DbBackupNode(Node):
    """Navigator for RPC db-backup"""

    def __call__(
        self, input_data: coriant_rpc.DbBackupInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.DbBackupOutput:
        from ..data_models.coriant_rpc import DbBackup, DbBackupInput, DbBackupOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = DbBackupInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DbBackupInput.model_validate_json(input_data)

        rpc_data = DbBackup(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return DbBackupOutput.model_validate(data)


class SimulateNode(Node):
    """Navigator for RPC simulate"""

    def __call__(self, input_data: coriant_rpc.SimulateInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.coriant_rpc import Simulate, SimulateInput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = SimulateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SimulateInput.model_validate_json(input_data)

        rpc_data = Simulate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class RepairInfoNode(Node):
    """Navigator for RPC repair-info"""

    def __call__(
        self, input_data: coriant_rpc.RepairInfoInput | dict | str | None = None, **kwargs: Any
    ) -> coriant_rpc.RepairInfoOutput:
        from ..data_models.coriant_rpc import RepairInfo, RepairInfoInput, RepairInfoOutput

        if input_data is None and kwargs:
            input_data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(input_data, dict):
            input_data = RepairInfoInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RepairInfoInput.model_validate_json(input_data)

        rpc_data = RepairInfo(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "coriant-rpc:output" in resp:
            data = resp.get("coriant-rpc:output")
        else:
            data = resp

        return RepairInfoOutput.model_validate(data)
