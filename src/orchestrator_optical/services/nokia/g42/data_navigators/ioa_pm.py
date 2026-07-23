from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import ioa_pm

class RealTimePmItemNode(ItemNode):
    """Navigator for list item real-time-pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.RealTimePmItem:
        from ..data_models.ioa_pm import RealTimePmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RealTimePmItem.model_validate(resp)

    def update(self, data: ioa_pm.RealTimePmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import RealTimePmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RealTimePmItem.model_validate(data)
        elif isinstance(data, str):
            data = RealTimePmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.RealTimePmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import RealTimePmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RealTimePmItem.model_validate(data)
        elif isinstance(data, str):
            data = RealTimePmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RealTimePmListNode(ListNode[RealTimePmItemNode]):
    """Navigator for list real-time-pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.RealTimePmItem]:
        from ..data_models.ioa_pm import RealTimePmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RealTimePmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.RealTimePmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.RealTimePmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RealTimePmDataNode(Node):
    """Navigator for real-time-pm-data"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.RealTimePmData:
        from ..data_models.ioa_pm import RealTimePmData
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RealTimePmData.model_validate(resp)

    def update(self, data: ioa_pm.RealTimePmData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import RealTimePmData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RealTimePmData.model_validate(data)
        elif isinstance(data, str):
            data = RealTimePmData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.RealTimePmData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import RealTimePmData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RealTimePmData.model_validate(data)
        elif isinstance(data, str):
            data = RealTimePmData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def real_time_pm(self) -> RealTimePmListNode:
        return RealTimePmListNode(self._client, f"{self._path}/real-time-pm", "real-time-pm", RealTimePmItemNode)

class CurrentPmItemNode(ItemNode):
    """Navigator for list item current-pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.CurrentPmItem:
        from ..data_models.ioa_pm import CurrentPmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentPmItem.model_validate(resp)

    def update(self, data: ioa_pm.CurrentPmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import CurrentPmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentPmItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentPmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.CurrentPmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import CurrentPmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentPmItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentPmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CurrentPmListNode(ListNode[CurrentPmItemNode]):
    """Navigator for list current-pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.CurrentPmItem]:
        from ..data_models.ioa_pm import CurrentPmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CurrentPmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.CurrentPmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.CurrentPmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CurrentPmDataNode(Node):
    """Navigator for current-pm-data"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.CurrentPmData:
        from ..data_models.ioa_pm import CurrentPmData
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentPmData.model_validate(resp)

    def update(self, data: ioa_pm.CurrentPmData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import CurrentPmData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentPmData.model_validate(data)
        elif isinstance(data, str):
            data = CurrentPmData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.CurrentPmData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import CurrentPmData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentPmData.model_validate(data)
        elif isinstance(data, str):
            data = CurrentPmData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def current_pm(self) -> CurrentPmListNode:
        return CurrentPmListNode(self._client, f"{self._path}/current-pm", "current-pm", CurrentPmItemNode)

class HistoryPmItemNode(ItemNode):
    """Navigator for list item history-pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.HistoryPmItem:
        from ..data_models.ioa_pm import HistoryPmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return HistoryPmItem.model_validate(resp)

    def update(self, data: ioa_pm.HistoryPmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import HistoryPmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HistoryPmItem.model_validate(data)
        elif isinstance(data, str):
            data = HistoryPmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.HistoryPmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import HistoryPmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HistoryPmItem.model_validate(data)
        elif isinstance(data, str):
            data = HistoryPmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class HistoryPmListNode(ListNode[HistoryPmItemNode]):
    """Navigator for list history-pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.HistoryPmItem]:
        from ..data_models.ioa_pm import HistoryPmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [HistoryPmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.HistoryPmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.HistoryPmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class HistoryPmDataNode(Node):
    """Navigator for history-pm-data"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.HistoryPmData:
        from ..data_models.ioa_pm import HistoryPmData
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return HistoryPmData.model_validate(resp)

    def update(self, data: ioa_pm.HistoryPmData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import HistoryPmData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HistoryPmData.model_validate(data)
        elif isinstance(data, str):
            data = HistoryPmData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.HistoryPmData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import HistoryPmData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HistoryPmData.model_validate(data)
        elif isinstance(data, str):
            data = HistoryPmData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def history_pm(self) -> HistoryPmListNode:
        return HistoryPmListNode(self._client, f"{self._path}/history-pm", "history-pm", HistoryPmItemNode)

class PmThresholdItemNode(ItemNode):
    """Navigator for list item pm-threshold"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmThresholdItem:
        from ..data_models.ioa_pm import PmThresholdItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmThresholdItem.model_validate(resp)

    def update(self, data: ioa_pm.PmThresholdItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmThresholdItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholdItem.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholdItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmThresholdItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmThresholdItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholdItem.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholdItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmThresholdListNode(ListNode[PmThresholdItemNode]):
    """Navigator for list pm-threshold"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmThresholdItem]:
        from ..data_models.ioa_pm import PmThresholdItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmThresholdItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmThresholdItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmThresholdItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmControlEntryItemNode(ItemNode):
    """Navigator for list item pm-control-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmControlEntryItem:
        from ..data_models.ioa_pm import PmControlEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmControlEntryItem.model_validate(resp)

    def update(self, data: ioa_pm.PmControlEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmControlEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmControlEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = PmControlEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmControlEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmControlEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmControlEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = PmControlEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def pm_threshold(self) -> PmThresholdListNode:
        return PmThresholdListNode(self._client, f"{self._path}/pm-threshold", "pm-threshold", PmThresholdItemNode)

class PmControlEntryListNode(ListNode[PmControlEntryItemNode]):
    """Navigator for list pm-control-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmControlEntryItem]:
        from ..data_models.ioa_pm import PmControlEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmControlEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmControlEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmControlEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmResourceItemNode(ItemNode):
    """Navigator for list item pm-resource"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmResourceItem:
        from ..data_models.ioa_pm import PmResourceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmResourceItem.model_validate(resp)

    def update(self, data: ioa_pm.PmResourceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmResourceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmResourceItem.model_validate(data)
        elif isinstance(data, str):
            data = PmResourceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmResourceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmResourceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmResourceItem.model_validate(data)
        elif isinstance(data, str):
            data = PmResourceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def pm_control_entry(self) -> PmControlEntryListNode:
        return PmControlEntryListNode(self._client, f"{self._path}/pm-control-entry", "pm-control-entry", PmControlEntryItemNode)

class PmResourceListNode(ListNode[PmResourceItemNode]):
    """Navigator for list pm-resource"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmResourceItem]:
        from ..data_models.ioa_pm import PmResourceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmResourceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmResourceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmResourceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmControlNode(Node):
    """Navigator for pm-control"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmControl:
        from ..data_models.ioa_pm import PmControl
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmControl.model_validate(resp)

    def update(self, data: ioa_pm.PmControl | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmControl

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmControl.model_validate(data)
        elif isinstance(data, str):
            data = PmControl.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.PmControl | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmControl

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmControl.model_validate(data)
        elif isinstance(data, str):
            data = PmControl.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pm_resource(self) -> PmResourceListNode:
        return PmResourceListNode(self._client, f"{self._path}/pm-resource", "pm-resource", PmResourceItemNode)

class PmThresholdProfileItemNode(ItemNode):
    """Navigator for list item pm-threshold-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmThresholdProfileItem:
        from ..data_models.ioa_pm import PmThresholdProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmThresholdProfileItem.model_validate(resp)

    def update(self, data: ioa_pm.PmThresholdProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmThresholdProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholdProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholdProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmThresholdProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmThresholdProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholdProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholdProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmThresholdProfileListNode(ListNode[PmThresholdProfileItemNode]):
    """Navigator for list pm-threshold-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmThresholdProfileItem]:
        from ..data_models.ioa_pm import PmThresholdProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmThresholdProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmThresholdProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmThresholdProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmProfileEntryItemNode(ItemNode):
    """Navigator for list item pm-profile-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmProfileEntryItem:
        from ..data_models.ioa_pm import PmProfileEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmProfileEntryItem.model_validate(resp)

    def update(self, data: ioa_pm.PmProfileEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmProfileEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmProfileEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = PmProfileEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmProfileEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmProfileEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmProfileEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = PmProfileEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def pm_threshold_profile(self) -> PmThresholdProfileListNode:
        return PmThresholdProfileListNode(self._client, f"{self._path}/pm-threshold-profile", "pm-threshold-profile", PmThresholdProfileItemNode)

class PmProfileEntryListNode(ListNode[PmProfileEntryItemNode]):
    """Navigator for list pm-profile-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmProfileEntryItem]:
        from ..data_models.ioa_pm import PmProfileEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmProfileEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmProfileEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmProfileEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmProfileNode(Node):
    """Navigator for pm-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmProfile:
        from ..data_models.ioa_pm import PmProfile
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmProfile.model_validate(resp)

    def update(self, data: ioa_pm.PmProfile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmProfile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmProfile.model_validate(data)
        elif isinstance(data, str):
            data = PmProfile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.PmProfile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmProfile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmProfile.model_validate(data)
        elif isinstance(data, str):
            data = PmProfile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pm_profile_entry(self) -> PmProfileEntryListNode:
        return PmProfileEntryListNode(self._client, f"{self._path}/pm-profile-entry", "pm-profile-entry", PmProfileEntryItemNode)

class PmParameterItemNode(ItemNode):
    """Navigator for list item pm-parameter"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmParameterItem:
        from ..data_models.ioa_pm import PmParameterItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmParameterItem.model_validate(resp)

    def update(self, data: ioa_pm.PmParameterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = PmParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmParameterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = PmParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmParameterListNode(ListNode[PmParameterItemNode]):
    """Navigator for list pm-parameter"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmParameterItem]:
        from ..data_models.ioa_pm import PmParameterItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmParameterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmCatalogNode(Node):
    """Navigator for pm-catalog"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmCatalog:
        from ..data_models.ioa_pm import PmCatalog
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmCatalog.model_validate(resp)

    def update(self, data: ioa_pm.PmCatalog | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmCatalog

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmCatalog.model_validate(data)
        elif isinstance(data, str):
            data = PmCatalog.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.PmCatalog | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmCatalog

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmCatalog.model_validate(data)
        elif isinstance(data, str):
            data = PmCatalog.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pm_parameter(self) -> PmParameterListNode:
        return PmParameterListNode(self._client, f"{self._path}/pm-parameter", "pm-parameter", PmParameterItemNode)

class PmNode(Node):
    """Navigator for pm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.Pm:
        from ..data_models.ioa_pm import Pm
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Pm.model_validate(resp)

    def update(self, data: ioa_pm.Pm | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import Pm

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Pm.model_validate(data)
        elif isinstance(data, str):
            data = Pm.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_pm.Pm | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import Pm

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Pm.model_validate(data)
        elif isinstance(data, str):
            data = Pm.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def real_time_pm_data(self) -> RealTimePmDataNode:
        return RealTimePmDataNode(self._client, f"{self._path}/real-time-pm-data", "real-time-pm-data")
    @property
    def current_pm_data(self) -> CurrentPmDataNode:
        return CurrentPmDataNode(self._client, f"{self._path}/current-pm-data", "current-pm-data")
    @property
    def history_pm_data(self) -> HistoryPmDataNode:
        return HistoryPmDataNode(self._client, f"{self._path}/history-pm-data", "history-pm-data")
    @property
    def pm_control(self) -> PmControlNode:
        return PmControlNode(self._client, f"{self._path}/pm-control", "pm-control")
    @property
    def pm_profile(self) -> PmProfileNode:
        return PmProfileNode(self._client, f"{self._path}/pm-profile", "pm-profile")
    @property
    def pm_catalog(self) -> PmCatalogNode:
        return PmCatalogNode(self._client, f"{self._path}/pm-catalog", "pm-catalog")

class FilterItemNode(ItemNode):
    """Navigator for list item filter"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.FilterItem:
        from ..data_models.ioa_pm import FilterItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FilterItem.model_validate(resp)

    def update(self, data: ioa_pm.FilterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import FilterItem

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

    def replace(self, data: ioa_pm.FilterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import FilterItem

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

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.FilterItem]:
        from ..data_models.ioa_pm import FilterItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FilterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.FilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.FilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmRecordItemNode(ItemNode):
    """Navigator for list item pm-record"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_pm.PmRecordItem:
        from ..data_models.ioa_pm import PmRecordItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmRecordItem.model_validate(resp)

    def update(self, data: ioa_pm.PmRecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmRecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmRecordItem.model_validate(data)
        elif isinstance(data, str):
            data = PmRecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_pm.PmRecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import PmRecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmRecordItem.model_validate(data)
        elif isinstance(data, str):
            data = PmRecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmRecordListNode(ListNode[PmRecordItemNode]):
    """Navigator for list pm-record"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_pm.PmRecordItem]:
        from ..data_models.ioa_pm import PmRecordItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmRecordItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_pm.PmRecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_pm.PmRecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class GetPmNode(Node):
    """Navigator for RPC get-pm"""

    def __call__(self, input_data: ioa_pm.GetPmInput | dict | str | None = None, **kwargs: Any) -> ioa_pm.GetPmOutput:
        from ..data_models.ioa_pm import GetPm, GetPmInput, GetPmOutput
        if input_data is None:
            input_data = GetPmInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetPmInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetPmInput.model_validate_json(input_data)

        rpc_data = GetPm(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-pm:output" in resp:
            data = resp.get("ioa-pm:output")
        else:
            data = resp

        return GetPmOutput.model_validate(data)

class ClearPmNode(Node):
    """Navigator for RPC clear-pm"""

    def __call__(self, input_data: ioa_pm.ClearPmInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_pm import ClearPm, ClearPmInput
        if input_data is None:
            input_data = ClearPmInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearPmInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearPmInput.model_validate_json(input_data)

        rpc_data = ClearPm(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)
