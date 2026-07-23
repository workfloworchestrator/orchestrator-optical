from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import ioa_alarm

class AlarmItemNode(ItemNode):
    """Navigator for list item alarm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.AlarmItem:
        from ..data_models.ioa_alarm import AlarmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmItem.model_validate(resp)

    def update(self, data: ioa_alarm.AlarmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_alarm.AlarmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AlarmListNode(ListNode[AlarmItemNode]):
    """Navigator for list alarm"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_alarm.AlarmItem]:
        from ..data_models.ioa_alarm import AlarmItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AlarmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_alarm.AlarmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_alarm.AlarmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CurrentAlarmsNode(Node):
    """Navigator for current-alarms"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.CurrentAlarms:
        from ..data_models.ioa_alarm import CurrentAlarms
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentAlarms.model_validate(resp)

    def update(self, data: ioa_alarm.CurrentAlarms | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import CurrentAlarms

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentAlarms.model_validate(data)
        elif isinstance(data, str):
            data = CurrentAlarms.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_alarm.CurrentAlarms | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import CurrentAlarms

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentAlarms.model_validate(data)
        elif isinstance(data, str):
            data = CurrentAlarms.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def alarm(self) -> AlarmListNode:
        return AlarmListNode(self._client, f"{self._path}/alarm", "alarm", AlarmItemNode)

class AlarmSeverityEntryItemNode(ItemNode):
    """Navigator for list item alarm-severity-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.AlarmSeverityEntryItem:
        from ..data_models.ioa_alarm import AlarmSeverityEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmSeverityEntryItem.model_validate(resp)

    def update(self, data: ioa_alarm.AlarmSeverityEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmSeverityEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmSeverityEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmSeverityEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_alarm.AlarmSeverityEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmSeverityEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmSeverityEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmSeverityEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AlarmSeverityEntryListNode(ListNode[AlarmSeverityEntryItemNode]):
    """Navigator for list alarm-severity-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_alarm.AlarmSeverityEntryItem]:
        from ..data_models.ioa_alarm import AlarmSeverityEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AlarmSeverityEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_alarm.AlarmSeverityEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_alarm.AlarmSeverityEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AlarmSeverityProfileNode(Node):
    """Navigator for alarm-severity-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.AlarmSeverityProfile:
        from ..data_models.ioa_alarm import AlarmSeverityProfile
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmSeverityProfile.model_validate(resp)

    def update(self, data: ioa_alarm.AlarmSeverityProfile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmSeverityProfile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmSeverityProfile.model_validate(data)
        elif isinstance(data, str):
            data = AlarmSeverityProfile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_alarm.AlarmSeverityProfile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmSeverityProfile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmSeverityProfile.model_validate(data)
        elif isinstance(data, str):
            data = AlarmSeverityProfile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def alarm_severity_entry(self) -> AlarmSeverityEntryListNode:
        return AlarmSeverityEntryListNode(self._client, f"{self._path}/alarm-severity-entry", "alarm-severity-entry", AlarmSeverityEntryItemNode)

class AlarmControlNode(Node):
    """Navigator for alarm-control"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.AlarmControl:
        from ..data_models.ioa_alarm import AlarmControl
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmControl.model_validate(resp)

    def update(self, data: ioa_alarm.AlarmControl | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmControl

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmControl.model_validate(data)
        elif isinstance(data, str):
            data = AlarmControl.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_alarm.AlarmControl | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmControl

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmControl.model_validate(data)
        elif isinstance(data, str):
            data = AlarmControl.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def alarm_severity_profile(self) -> AlarmSeverityProfileNode:
        return AlarmSeverityProfileNode(self._client, f"{self._path}/alarm-severity-profile", "alarm-severity-profile")

class AlarmInventoryItemNode(ItemNode):
    """Navigator for list item alarm-inventory"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.AlarmInventoryItem:
        from ..data_models.ioa_alarm import AlarmInventoryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmInventoryItem.model_validate(resp)

    def update(self, data: ioa_alarm.AlarmInventoryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmInventoryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmInventoryItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmInventoryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_alarm.AlarmInventoryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import AlarmInventoryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmInventoryItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmInventoryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AlarmInventoryListNode(ListNode[AlarmInventoryItemNode]):
    """Navigator for list alarm-inventory"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_alarm.AlarmInventoryItem]:
        from ..data_models.ioa_alarm import AlarmInventoryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AlarmInventoryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_alarm.AlarmInventoryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_alarm.AlarmInventoryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AlarmsNode(Node):
    """Navigator for alarms"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.Alarms:
        from ..data_models.ioa_alarm import Alarms
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Alarms.model_validate(resp)

    def update(self, data: ioa_alarm.Alarms | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import Alarms

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Alarms.model_validate(data)
        elif isinstance(data, str):
            data = Alarms.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_alarm.Alarms | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import Alarms

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Alarms.model_validate(data)
        elif isinstance(data, str):
            data = Alarms.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def current_alarms(self) -> CurrentAlarmsNode:
        return CurrentAlarmsNode(self._client, f"{self._path}/current-alarms", "current-alarms")
    @property
    def alarm_control(self) -> AlarmControlNode:
        return AlarmControlNode(self._client, f"{self._path}/alarm-control", "alarm-control")
    @property
    def alarm_inventory(self) -> AlarmInventoryListNode:
        return AlarmInventoryListNode(self._client, f"{self._path}/alarm-inventory", "alarm-inventory", AlarmInventoryItemNode)

class SetAlarmStateNode(Node):
    """Navigator for RPC set-alarm-state"""

    def __call__(self, input_data: ioa_alarm.SetAlarmStateInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import SetAlarmState, SetAlarmStateInput
        if input_data is None:
            input_data = SetAlarmStateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = SetAlarmStateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SetAlarmStateInput.model_validate_json(input_data)

        rpc_data = SetAlarmState(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

class ClearAlarmNode(Node):
    """Navigator for RPC clear-alarm"""

    def __call__(self, input_data: ioa_alarm.ClearAlarmInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import ClearAlarm, ClearAlarmInput
        if input_data is None:
            input_data = ClearAlarmInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearAlarmInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearAlarmInput.model_validate_json(input_data)

        rpc_data = ClearAlarm(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

class ConditionItemNode(ItemNode):
    """Navigator for list item condition"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_alarm.ConditionItem:
        from ..data_models.ioa_alarm import ConditionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ConditionItem.model_validate(resp)

    def update(self, data: ioa_alarm.ConditionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import ConditionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ConditionItem.model_validate(data)
        elif isinstance(data, str):
            data = ConditionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_alarm.ConditionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_alarm import ConditionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ConditionItem.model_validate(data)
        elif isinstance(data, str):
            data = ConditionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ConditionListNode(ListNode[ConditionItemNode]):
    """Navigator for list condition"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_alarm.ConditionItem]:
        from ..data_models.ioa_alarm import ConditionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ConditionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_alarm.ConditionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_alarm.ConditionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class GetConditionsNode(Node):
    """Navigator for RPC get-conditions"""

    def __call__(self, input_data: ioa_alarm.GetConditionsInput | dict | str | None = None, **kwargs: Any) -> ioa_alarm.GetConditionsOutput:
        from ..data_models.ioa_alarm import GetConditions, GetConditionsInput, GetConditionsOutput
        if input_data is None:
            input_data = GetConditionsInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetConditionsInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetConditionsInput.model_validate_json(input_data)

        rpc_data = GetConditions(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-alarm:output" in resp:
            data = resp.get("ioa-alarm:output")
        else:
            data = resp

        return GetConditionsOutput.model_validate(data)
