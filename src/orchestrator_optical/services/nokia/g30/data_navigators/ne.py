from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import ne

class TemperatureDetailsItemNode(ItemNode):
    """Navigator for list item temperature-details"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TemperatureDetailsItem:
        from ..data_models.ne import TemperatureDetailsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TemperatureDetailsItem.model_validate(resp)

    def update(self, data: ne.TemperatureDetailsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TemperatureDetailsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TemperatureDetailsItem.model_validate(data)
        elif isinstance(data, str):
            data = TemperatureDetailsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.TemperatureDetailsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TemperatureDetailsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TemperatureDetailsItem.model_validate(data)
        elif isinstance(data, str):
            data = TemperatureDetailsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TemperatureDetailsListNode(ListNode[TemperatureDetailsItemNode]):
    """Navigator for list temperature-details"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.TemperatureDetailsItem]:
        from ..data_models.ne import TemperatureDetailsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TemperatureDetailsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.TemperatureDetailsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.TemperatureDetailsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PerCoreUtilizationItemNode(ItemNode):
    """Navigator for list item per-core-utilization"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PerCoreUtilizationItem:
        from ..data_models.ne import PerCoreUtilizationItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PerCoreUtilizationItem.model_validate(resp)

    def update(self, data: ne.PerCoreUtilizationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PerCoreUtilizationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PerCoreUtilizationItem.model_validate(data)
        elif isinstance(data, str):
            data = PerCoreUtilizationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PerCoreUtilizationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PerCoreUtilizationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PerCoreUtilizationItem.model_validate(data)
        elif isinstance(data, str):
            data = PerCoreUtilizationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PerCoreUtilizationListNode(ListNode[PerCoreUtilizationItemNode]):
    """Navigator for list per-core-utilization"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PerCoreUtilizationItem]:
        from ..data_models.ne import PerCoreUtilizationItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PerCoreUtilizationItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PerCoreUtilizationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PerCoreUtilizationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CpuStateNode(Node):
    """Navigator for cpu-state"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CpuState:
        from ..data_models.ne import CpuState
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CpuState.model_validate(resp)

    def update(self, data: ne.CpuState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CpuState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CpuState.model_validate(data)
        elif isinstance(data, str):
            data = CpuState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.CpuState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CpuState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CpuState.model_validate(data)
        elif isinstance(data, str):
            data = CpuState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def per_core_utilization(self) -> PerCoreUtilizationListNode:
        return PerCoreUtilizationListNode(self._client, f"{self._path}/per-core-utilization", "per-core-utilization", PerCoreUtilizationItemNode)

class MemoryStateNode(Node):
    """Navigator for memory-state"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.MemoryState:
        from ..data_models.ne import MemoryState
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return MemoryState.model_validate(resp)

    def update(self, data: ne.MemoryState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MemoryState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MemoryState.model_validate(data)
        elif isinstance(data, str):
            data = MemoryState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.MemoryState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MemoryState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MemoryState.model_validate(data)
        elif isinstance(data, str):
            data = MemoryState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OtdrNode(Node):
    """Navigator for otdr"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otdr:
        from ..data_models.ne import Otdr
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otdr.model_validate(resp)

    def update(self, data: ne.Otdr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otdr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otdr.model_validate(data)
        elif isinstance(data, str):
            data = Otdr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otdr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otdr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otdr.model_validate(data)
        elif isinstance(data, str):
            data = Otdr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OpticalPowerLaneItemNode(ItemNode):
    """Navigator for list item optical-power-lane"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OpticalPowerLaneItem:
        from ..data_models.ne import OpticalPowerLaneItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalPowerLaneItem.model_validate(resp)

    def update(self, data: ne.OpticalPowerLaneItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpticalPowerLaneItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalPowerLaneItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalPowerLaneItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OpticalPowerLaneItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpticalPowerLaneItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalPowerLaneItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalPowerLaneItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OpticalPowerLaneListNode(ListNode[OpticalPowerLaneItemNode]):
    """Navigator for list optical-power-lane"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OpticalPowerLaneItem]:
        from ..data_models.ne import OpticalPowerLaneItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpticalPowerLaneItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OpticalPowerLaneItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OpticalPowerLaneItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class TestSignalFacilityStatusNode(Node):
    """Navigator for test-signal-facility-status"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TestSignalFacilityStatus:
        from ..data_models.ne import TestSignalFacilityStatus
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TestSignalFacilityStatus.model_validate(resp)

    def update(self, data: ne.TestSignalFacilityStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TestSignalFacilityStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TestSignalFacilityStatus.model_validate(data)
        elif isinstance(data, str):
            data = TestSignalFacilityStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.TestSignalFacilityStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TestSignalFacilityStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TestSignalFacilityStatus.model_validate(data)
        elif isinstance(data, str):
            data = TestSignalFacilityStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class RemoteManAddressesItemNode(ItemNode):
    """Navigator for list item remote-man-addresses"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RemoteManAddressesItem:
        from ..data_models.ne import RemoteManAddressesItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RemoteManAddressesItem.model_validate(resp)

    def update(self, data: ne.RemoteManAddressesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RemoteManAddressesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RemoteManAddressesItem.model_validate(data)
        elif isinstance(data, str):
            data = RemoteManAddressesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RemoteManAddressesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RemoteManAddressesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RemoteManAddressesItem.model_validate(data)
        elif isinstance(data, str):
            data = RemoteManAddressesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RemoteManAddressesListNode(ListNode[RemoteManAddressesItemNode]):
    """Navigator for list remote-man-addresses"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RemoteManAddressesItem]:
        from ..data_models.ne import RemoteManAddressesItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RemoteManAddressesItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RemoteManAddressesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RemoteManAddressesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class LldpRemoteSystemItemNode(ItemNode):
    """Navigator for list item lldp-remote-system"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.LldpRemoteSystemItem:
        from ..data_models.ne import LldpRemoteSystemItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LldpRemoteSystemItem.model_validate(resp)

    def update(self, data: ne.LldpRemoteSystemItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LldpRemoteSystemItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpRemoteSystemItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpRemoteSystemItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.LldpRemoteSystemItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LldpRemoteSystemItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpRemoteSystemItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpRemoteSystemItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def remote_man_addresses(self) -> RemoteManAddressesListNode:
        return RemoteManAddressesListNode(self._client, f"{self._path}/remote-man-addresses", "remote-man-addresses", RemoteManAddressesItemNode)

class LldpRemoteSystemListNode(ListNode[LldpRemoteSystemItemNode]):
    """Navigator for list lldp-remote-system"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.LldpRemoteSystemItem]:
        from ..data_models.ne import LldpRemoteSystemItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LldpRemoteSystemItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.LldpRemoteSystemItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.LldpRemoteSystemItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class BitErrorRatePreFecNode(Node):
    """Navigator for bit-error-rate-pre-fec"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.BitErrorRatePreFec:
        from ..data_models.ne import BitErrorRatePreFec
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BitErrorRatePreFec.model_validate(resp)

    def update(self, data: ne.BitErrorRatePreFec | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BitErrorRatePreFec

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BitErrorRatePreFec.model_validate(data)
        elif isinstance(data, str):
            data = BitErrorRatePreFec.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.BitErrorRatePreFec | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BitErrorRatePreFec

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BitErrorRatePreFec.model_validate(data)
        elif isinstance(data, str):
            data = BitErrorRatePreFec.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class BitErrorRatePostFecNode(Node):
    """Navigator for bit-error-rate-post-fec"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.BitErrorRatePostFec:
        from ..data_models.ne import BitErrorRatePostFec
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BitErrorRatePostFec.model_validate(resp)

    def update(self, data: ne.BitErrorRatePostFec | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BitErrorRatePostFec

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BitErrorRatePostFec.model_validate(data)
        elif isinstance(data, str):
            data = BitErrorRatePostFec.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.BitErrorRatePostFec | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BitErrorRatePostFec

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BitErrorRatePostFec.model_validate(data)
        elif isinstance(data, str):
            data = BitErrorRatePostFec.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InUtilizationNode(Node):
    """Navigator for in-utilization"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InUtilization:
        from ..data_models.ne import InUtilization
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InUtilization.model_validate(resp)

    def update(self, data: ne.InUtilization | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InUtilization

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InUtilization.model_validate(data)
        elif isinstance(data, str):
            data = InUtilization.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InUtilization | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InUtilization

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InUtilization.model_validate(data)
        elif isinstance(data, str):
            data = InUtilization.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutUtilizationNode(Node):
    """Navigator for out-utilization"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutUtilization:
        from ..data_models.ne import OutUtilization
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutUtilization.model_validate(resp)

    def update(self, data: ne.OutUtilization | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutUtilization

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutUtilization.model_validate(data)
        elif isinstance(data, str):
            data = OutUtilization.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutUtilization | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutUtilization

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutUtilization.model_validate(data)
        elif isinstance(data, str):
            data = OutUtilization.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InBackgroundBlockErrorRateNode(Node):
    """Navigator for in-background-block-error-rate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InBackgroundBlockErrorRate:
        from ..data_models.ne import InBackgroundBlockErrorRate
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InBackgroundBlockErrorRate.model_validate(resp)

    def update(self, data: ne.InBackgroundBlockErrorRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InBackgroundBlockErrorRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InBackgroundBlockErrorRate.model_validate(data)
        elif isinstance(data, str):
            data = InBackgroundBlockErrorRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InBackgroundBlockErrorRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InBackgroundBlockErrorRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InBackgroundBlockErrorRate.model_validate(data)
        elif isinstance(data, str):
            data = InBackgroundBlockErrorRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutBackgroundBlockErrorRateNode(Node):
    """Navigator for out-background-block-error-rate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutBackgroundBlockErrorRate:
        from ..data_models.ne import OutBackgroundBlockErrorRate
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutBackgroundBlockErrorRate.model_validate(resp)

    def update(self, data: ne.OutBackgroundBlockErrorRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutBackgroundBlockErrorRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutBackgroundBlockErrorRate.model_validate(data)
        elif isinstance(data, str):
            data = OutBackgroundBlockErrorRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutBackgroundBlockErrorRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutBackgroundBlockErrorRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutBackgroundBlockErrorRate.model_validate(data)
        elif isinstance(data, str):
            data = OutBackgroundBlockErrorRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InSeverelyErroredSecondsRateNode(Node):
    """Navigator for in-severely-errored-seconds-rate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InSeverelyErroredSecondsRate:
        from ..data_models.ne import InSeverelyErroredSecondsRate
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InSeverelyErroredSecondsRate.model_validate(resp)

    def update(self, data: ne.InSeverelyErroredSecondsRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InSeverelyErroredSecondsRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InSeverelyErroredSecondsRate.model_validate(data)
        elif isinstance(data, str):
            data = InSeverelyErroredSecondsRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InSeverelyErroredSecondsRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InSeverelyErroredSecondsRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InSeverelyErroredSecondsRate.model_validate(data)
        elif isinstance(data, str):
            data = InSeverelyErroredSecondsRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutSeverelyErroredSecondsRateNode(Node):
    """Navigator for out-severely-errored-seconds-rate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutSeverelyErroredSecondsRate:
        from ..data_models.ne import OutSeverelyErroredSecondsRate
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutSeverelyErroredSecondsRate.model_validate(resp)

    def update(self, data: ne.OutSeverelyErroredSecondsRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutSeverelyErroredSecondsRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutSeverelyErroredSecondsRate.model_validate(data)
        elif isinstance(data, str):
            data = OutSeverelyErroredSecondsRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutSeverelyErroredSecondsRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutSeverelyErroredSecondsRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutSeverelyErroredSecondsRate.model_validate(data)
        elif isinstance(data, str):
            data = OutSeverelyErroredSecondsRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class StatisticsNode(Node):
    """Navigator for statistics"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Statistics:
        from ..data_models.ne import Statistics
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Statistics.model_validate(resp)

    def update(self, data: ne.Statistics | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Statistics

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Statistics.model_validate(data)
        elif isinstance(data, str):
            data = Statistics.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Statistics | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Statistics

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Statistics.model_validate(data)
        elif isinstance(data, str):
            data = Statistics.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def bit_error_rate_pre_fec(self) -> BitErrorRatePreFecNode:
        return BitErrorRatePreFecNode(self._client, f"{self._path}/bit-error-rate-pre-fec", "bit-error-rate-pre-fec")
    @property
    def bit_error_rate_post_fec(self) -> BitErrorRatePostFecNode:
        return BitErrorRatePostFecNode(self._client, f"{self._path}/bit-error-rate-post-fec", "bit-error-rate-post-fec")
    @property
    def in_utilization(self) -> InUtilizationNode:
        return InUtilizationNode(self._client, f"{self._path}/in-utilization", "in-utilization")
    @property
    def out_utilization(self) -> OutUtilizationNode:
        return OutUtilizationNode(self._client, f"{self._path}/out-utilization", "out-utilization")
    @property
    def in_background_block_error_rate(self) -> InBackgroundBlockErrorRateNode:
        return InBackgroundBlockErrorRateNode(self._client, f"{self._path}/in-background-block-error-rate", "in-background-block-error-rate")
    @property
    def out_background_block_error_rate(self) -> OutBackgroundBlockErrorRateNode:
        return OutBackgroundBlockErrorRateNode(self._client, f"{self._path}/out-background-block-error-rate", "out-background-block-error-rate")
    @property
    def in_severely_errored_seconds_rate(self) -> InSeverelyErroredSecondsRateNode:
        return InSeverelyErroredSecondsRateNode(self._client, f"{self._path}/in-severely-errored-seconds-rate", "in-severely-errored-seconds-rate")
    @property
    def out_severely_errored_seconds_rate(self) -> OutSeverelyErroredSecondsRateNode:
        return OutSeverelyErroredSecondsRateNode(self._client, f"{self._path}/out-severely-errored-seconds-rate", "out-severely-errored-seconds-rate")

class OduEncryptionNode(Node):
    """Navigator for odu-encryption"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OduEncryption:
        from ..data_models.ne import OduEncryption
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OduEncryption.model_validate(resp)

    def update(self, data: ne.OduEncryption | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OduEncryption

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduEncryption.model_validate(data)
        elif isinstance(data, str):
            data = OduEncryption.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OduEncryption | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OduEncryption

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduEncryption.model_validate(data)
        elif isinstance(data, str):
            data = OduEncryption.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OduDelayNode(Node):
    """Navigator for odu-delay"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OduDelay:
        from ..data_models.ne import OduDelay
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OduDelay.model_validate(resp)

    def update(self, data: ne.OduDelay | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OduDelay

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduDelay.model_validate(data)
        elif isinstance(data, str):
            data = OduDelay.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OduDelay | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OduDelay

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduDelay.model_validate(data)
        elif isinstance(data, str):
            data = OduDelay.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class TestSignalStatusNode(Node):
    """Navigator for test-signal-status"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TestSignalStatus:
        from ..data_models.ne import TestSignalStatus
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TestSignalStatus.model_validate(resp)

    def update(self, data: ne.TestSignalStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TestSignalStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TestSignalStatus.model_validate(data)
        elif isinstance(data, str):
            data = TestSignalStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.TestSignalStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TestSignalStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TestSignalStatus.model_validate(data)
        elif isinstance(data, str):
            data = TestSignalStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OduItemNode(ItemNode):
    """Navigator for list item odu"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OduItem:
        from ..data_models.ne import OduItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OduItem.model_validate(resp)

    def update(self, data: ne.OduItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OduItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduItem.model_validate(data)
        elif isinstance(data, str):
            data = OduItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OduItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OduItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduItem.model_validate(data)
        elif isinstance(data, str):
            data = OduItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def odu_encryption(self) -> OduEncryptionNode:
        return OduEncryptionNode(self._client, f"{self._path}/odu-encryption", "odu-encryption")
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def test_signal_status(self) -> TestSignalStatusNode:
        return TestSignalStatusNode(self._client, f"{self._path}/test-signal-status", "test-signal-status")

class OduListNode(ListNode[OduItemNode]):
    """Navigator for list odu"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OduItem]:
        from ..data_models.ne import OduItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OduItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OduItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OduItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class Eth10gNode(Node):
    """Navigator for eth10g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Eth10g:
        from ..data_models.ne import Eth10g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Eth10g.model_validate(resp)

    def update(self, data: ne.Eth10g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth10g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth10g.model_validate(data)
        elif isinstance(data, str):
            data = Eth10g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Eth10g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth10g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth10g.model_validate(data)
        elif isinstance(data, str):
            data = Eth10g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def lldp_remote_system(self) -> LldpRemoteSystemListNode:
        return LldpRemoteSystemListNode(self._client, f"{self._path}/lldp-remote-system", "lldp-remote-system", LldpRemoteSystemItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Eth40gNode(Node):
    """Navigator for eth40g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Eth40g:
        from ..data_models.ne import Eth40g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Eth40g.model_validate(resp)

    def update(self, data: ne.Eth40g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth40g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth40g.model_validate(data)
        elif isinstance(data, str):
            data = Eth40g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Eth40g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth40g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth40g.model_validate(data)
        elif isinstance(data, str):
            data = Eth40g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def lldp_remote_system(self) -> LldpRemoteSystemListNode:
        return LldpRemoteSystemListNode(self._client, f"{self._path}/lldp-remote-system", "lldp-remote-system", LldpRemoteSystemItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Eth100gNode(Node):
    """Navigator for eth100g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Eth100g:
        from ..data_models.ne import Eth100g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Eth100g.model_validate(resp)

    def update(self, data: ne.Eth100g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth100g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth100g.model_validate(data)
        elif isinstance(data, str):
            data = Eth100g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Eth100g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth100g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth100g.model_validate(data)
        elif isinstance(data, str):
            data = Eth100g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def lldp_remote_system(self) -> LldpRemoteSystemListNode:
        return LldpRemoteSystemListNode(self._client, f"{self._path}/lldp-remote-system", "lldp-remote-system", LldpRemoteSystemItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Eth400gNode(Node):
    """Navigator for eth400g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Eth400g:
        from ..data_models.ne import Eth400g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Eth400g.model_validate(resp)

    def update(self, data: ne.Eth400g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth400g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth400g.model_validate(data)
        elif isinstance(data, str):
            data = Eth400g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Eth400g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth400g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth400g.model_validate(data)
        elif isinstance(data, str):
            data = Eth400g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def lldp_remote_system(self) -> LldpRemoteSystemListNode:
        return LldpRemoteSystemListNode(self._client, f"{self._path}/lldp-remote-system", "lldp-remote-system", LldpRemoteSystemItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otu4Node(Node):
    """Navigator for otu4"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otu4:
        from ..data_models.ne import Otu4
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otu4.model_validate(resp)

    def update(self, data: ne.Otu4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otu4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otu4.model_validate(data)
        elif isinstance(data, str):
            data = Otu4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otu4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otu4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otu4.model_validate(data)
        elif isinstance(data, str):
            data = Otu4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otu2Node(Node):
    """Navigator for otu2"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otu2:
        from ..data_models.ne import Otu2
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otu2.model_validate(resp)

    def update(self, data: ne.Otu2 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otu2

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otu2.model_validate(data)
        elif isinstance(data, str):
            data = Otu2.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otu2 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otu2

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otu2.model_validate(data)
        elif isinstance(data, str):
            data = Otu2.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otu2eNode(Node):
    """Navigator for otu2e"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otu2e:
        from ..data_models.ne import Otu2e
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otu2e.model_validate(resp)

    def update(self, data: ne.Otu2e | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otu2e

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otu2e.model_validate(data)
        elif isinstance(data, str):
            data = Otu2e.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otu2e | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otu2e

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otu2e.model_validate(data)
        elif isinstance(data, str):
            data = Otu2e.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Oc192Node(Node):
    """Navigator for oc192"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Oc192:
        from ..data_models.ne import Oc192
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Oc192.model_validate(resp)

    def update(self, data: ne.Oc192 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Oc192

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Oc192.model_validate(data)
        elif isinstance(data, str):
            data = Oc192.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Oc192 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Oc192

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Oc192.model_validate(data)
        elif isinstance(data, str):
            data = Oc192.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Oc48Node(Node):
    """Navigator for oc48"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Oc48:
        from ..data_models.ne import Oc48
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Oc48.model_validate(resp)

    def update(self, data: ne.Oc48 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Oc48

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Oc48.model_validate(data)
        elif isinstance(data, str):
            data = Oc48.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Oc48 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Oc48

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Oc48.model_validate(data)
        elif isinstance(data, str):
            data = Oc48.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Stm64Node(Node):
    """Navigator for stm64"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Stm64:
        from ..data_models.ne import Stm64
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Stm64.model_validate(resp)

    def update(self, data: ne.Stm64 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Stm64

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Stm64.model_validate(data)
        elif isinstance(data, str):
            data = Stm64.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Stm64 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Stm64

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Stm64.model_validate(data)
        elif isinstance(data, str):
            data = Stm64.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Stm16Node(Node):
    """Navigator for stm16"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Stm16:
        from ..data_models.ne import Stm16
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Stm16.model_validate(resp)

    def update(self, data: ne.Stm16 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Stm16

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Stm16.model_validate(data)
        elif isinstance(data, str):
            data = Stm16.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Stm16 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Stm16

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Stm16.model_validate(data)
        elif isinstance(data, str):
            data = Stm16.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Wan10gSonetNode(Node):
    """Navigator for wan10g-sonet"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Wan10gSonet:
        from ..data_models.ne import Wan10gSonet
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Wan10gSonet.model_validate(resp)

    def update(self, data: ne.Wan10gSonet | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Wan10gSonet

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Wan10gSonet.model_validate(data)
        elif isinstance(data, str):
            data = Wan10gSonet.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Wan10gSonet | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Wan10gSonet

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Wan10gSonet.model_validate(data)
        elif isinstance(data, str):
            data = Wan10gSonet.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Wan10gSdhNode(Node):
    """Navigator for wan10g-sdh"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Wan10gSdh:
        from ..data_models.ne import Wan10gSdh
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Wan10gSdh.model_validate(resp)

    def update(self, data: ne.Wan10gSdh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Wan10gSdh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Wan10gSdh.model_validate(data)
        elif isinstance(data, str):
            data = Wan10gSdh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Wan10gSdh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Wan10gSdh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Wan10gSdh.model_validate(data)
        elif isinstance(data, str):
            data = Wan10gSdh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Fc1gNode(Node):
    """Navigator for fc1g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Fc1g:
        from ..data_models.ne import Fc1g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Fc1g.model_validate(resp)

    def update(self, data: ne.Fc1g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc1g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc1g.model_validate(data)
        elif isinstance(data, str):
            data = Fc1g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Fc1g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc1g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc1g.model_validate(data)
        elif isinstance(data, str):
            data = Fc1g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Fc4gNode(Node):
    """Navigator for fc4g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Fc4g:
        from ..data_models.ne import Fc4g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Fc4g.model_validate(resp)

    def update(self, data: ne.Fc4g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc4g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc4g.model_validate(data)
        elif isinstance(data, str):
            data = Fc4g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Fc4g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc4g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc4g.model_validate(data)
        elif isinstance(data, str):
            data = Fc4g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Fc8gNode(Node):
    """Navigator for fc8g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Fc8g:
        from ..data_models.ne import Fc8g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Fc8g.model_validate(resp)

    def update(self, data: ne.Fc8g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc8g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc8g.model_validate(data)
        elif isinstance(data, str):
            data = Fc8g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Fc8g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc8g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc8g.model_validate(data)
        elif isinstance(data, str):
            data = Fc8g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class Fc16gNode(Node):
    """Navigator for fc16g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Fc16g:
        from ..data_models.ne import Fc16g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Fc16g.model_validate(resp)

    def update(self, data: ne.Fc16g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc16g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc16g.model_validate(data)
        elif isinstance(data, str):
            data = Fc16g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Fc16g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fc16g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fc16g.model_validate(data)
        elif isinstance(data, str):
            data = Fc16g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class InOpticalPowerNode(Node):
    """Navigator for in-optical-power"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InOpticalPower:
        from ..data_models.ne import InOpticalPower
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InOpticalPower.model_validate(resp)

    def update(self, data: ne.InOpticalPower | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPower

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPower.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPower.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InOpticalPower | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPower

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPower.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPower.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutOpticalPowerNode(Node):
    """Navigator for out-optical-power"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutOpticalPower:
        from ..data_models.ne import OutOpticalPower
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutOpticalPower.model_validate(resp)

    def update(self, data: ne.OutOpticalPower | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPower

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPower.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPower.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutOpticalPower | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPower

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPower.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPower.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class Otuc2Node(Node):
    """Navigator for otuc2"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc2:
        from ..data_models.ne import Otuc2
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc2.model_validate(resp)

    def update(self, data: ne.Otuc2 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc2

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc2.model_validate(data)
        elif isinstance(data, str):
            data = Otuc2.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc2 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc2

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc2.model_validate(data)
        elif isinstance(data, str):
            data = Otuc2.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otuc3Node(Node):
    """Navigator for otuc3"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc3:
        from ..data_models.ne import Otuc3
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc3.model_validate(resp)

    def update(self, data: ne.Otuc3 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc3

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc3.model_validate(data)
        elif isinstance(data, str):
            data = Otuc3.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc3 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc3

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc3.model_validate(data)
        elif isinstance(data, str):
            data = Otuc3.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otuc6Node(Node):
    """Navigator for otuc6"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc6:
        from ..data_models.ne import Otuc6
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc6.model_validate(resp)

    def update(self, data: ne.Otuc6 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc6

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc6.model_validate(data)
        elif isinstance(data, str):
            data = Otuc6.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc6 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc6

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc6.model_validate(data)
        elif isinstance(data, str):
            data = Otuc6.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class SubportItemNode(ItemNode):
    """Navigator for list item subport"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SubportItem:
        from ..data_models.ne import SubportItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SubportItem.model_validate(resp)

    def update(self, data: ne.SubportItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SubportItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubportItem.model_validate(data)
        elif isinstance(data, str):
            data = SubportItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SubportItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SubportItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubportItem.model_validate(data)
        elif isinstance(data, str):
            data = SubportItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def eth10g(self) -> Eth10gNode:
        return Eth10gNode(self._client, f"{self._path}/eth10g", "eth10g")
    @property
    def eth40g(self) -> Eth40gNode:
        return Eth40gNode(self._client, f"{self._path}/eth40g", "eth40g")
    @property
    def eth100g(self) -> Eth100gNode:
        return Eth100gNode(self._client, f"{self._path}/eth100g", "eth100g")
    @property
    def eth400g(self) -> Eth400gNode:
        return Eth400gNode(self._client, f"{self._path}/eth400g", "eth400g")
    @property
    def otu4(self) -> Otu4Node:
        return Otu4Node(self._client, f"{self._path}/otu4", "otu4")
    @property
    def otu2(self) -> Otu2Node:
        return Otu2Node(self._client, f"{self._path}/otu2", "otu2")
    @property
    def otu2e(self) -> Otu2eNode:
        return Otu2eNode(self._client, f"{self._path}/otu2e", "otu2e")
    @property
    def oc192(self) -> Oc192Node:
        return Oc192Node(self._client, f"{self._path}/oc192", "oc192")
    @property
    def oc48(self) -> Oc48Node:
        return Oc48Node(self._client, f"{self._path}/oc48", "oc48")
    @property
    def stm64(self) -> Stm64Node:
        return Stm64Node(self._client, f"{self._path}/stm64", "stm64")
    @property
    def stm16(self) -> Stm16Node:
        return Stm16Node(self._client, f"{self._path}/stm16", "stm16")
    @property
    def wan10g_sonet(self) -> Wan10gSonetNode:
        return Wan10gSonetNode(self._client, f"{self._path}/wan10g-sonet", "wan10g-sonet")
    @property
    def wan10g_sdh(self) -> Wan10gSdhNode:
        return Wan10gSdhNode(self._client, f"{self._path}/wan10g-sdh", "wan10g-sdh")
    @property
    def fc1g(self) -> Fc1gNode:
        return Fc1gNode(self._client, f"{self._path}/fc1g", "fc1g")
    @property
    def fc4g(self) -> Fc4gNode:
        return Fc4gNode(self._client, f"{self._path}/fc4g", "fc4g")
    @property
    def fc8g(self) -> Fc8gNode:
        return Fc8gNode(self._client, f"{self._path}/fc8g", "fc8g")
    @property
    def fc16g(self) -> Fc16gNode:
        return Fc16gNode(self._client, f"{self._path}/fc16g", "fc16g")
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def otuc2(self) -> Otuc2Node:
        return Otuc2Node(self._client, f"{self._path}/otuc2", "otuc2")
    @property
    def otuc3(self) -> Otuc3Node:
        return Otuc3Node(self._client, f"{self._path}/otuc3", "otuc3")
    @property
    def otuc6(self) -> Otuc6Node:
        return Otuc6Node(self._client, f"{self._path}/otuc6", "otuc6")

class SubportListNode(ListNode[SubportItemNode]):
    """Navigator for list subport"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SubportItem]:
        from ..data_models.ne import SubportItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SubportItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SubportItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SubportItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ChannelStatesItemNode(ItemNode):
    """Navigator for list item channel-states"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ChannelStatesItem:
        from ..data_models.ne import ChannelStatesItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChannelStatesItem.model_validate(resp)

    def update(self, data: ne.ChannelStatesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChannelStatesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChannelStatesItem.model_validate(data)
        elif isinstance(data, str):
            data = ChannelStatesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ChannelStatesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChannelStatesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChannelStatesItem.model_validate(data)
        elif isinstance(data, str):
            data = ChannelStatesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ChannelStatesListNode(ListNode[ChannelStatesItemNode]):
    """Navigator for list channel-states"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ChannelStatesItem]:
        from ..data_models.ne import ChannelStatesItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ChannelStatesItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ChannelStatesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ChannelStatesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DiagnosticAlarmThresholdsItemNode(ItemNode):
    """Navigator for list item diagnostic-alarm-thresholds"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DiagnosticAlarmThresholdsItem:
        from ..data_models.ne import DiagnosticAlarmThresholdsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DiagnosticAlarmThresholdsItem.model_validate(resp)

    def update(self, data: ne.DiagnosticAlarmThresholdsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DiagnosticAlarmThresholdsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DiagnosticAlarmThresholdsItem.model_validate(data)
        elif isinstance(data, str):
            data = DiagnosticAlarmThresholdsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DiagnosticAlarmThresholdsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DiagnosticAlarmThresholdsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DiagnosticAlarmThresholdsItem.model_validate(data)
        elif isinstance(data, str):
            data = DiagnosticAlarmThresholdsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DiagnosticAlarmThresholdsListNode(ListNode[DiagnosticAlarmThresholdsItemNode]):
    """Navigator for list diagnostic-alarm-thresholds"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DiagnosticAlarmThresholdsItem]:
        from ..data_models.ne import DiagnosticAlarmThresholdsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DiagnosticAlarmThresholdsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DiagnosticAlarmThresholdsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DiagnosticAlarmThresholdsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class QsfpSignalIntegrityLaneItemNode(ItemNode):
    """Navigator for list item qsfp-signal-integrity-lane"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.QsfpSignalIntegrityLaneItem:
        from ..data_models.ne import QsfpSignalIntegrityLaneItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return QsfpSignalIntegrityLaneItem.model_validate(resp)

    def update(self, data: ne.QsfpSignalIntegrityLaneItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import QsfpSignalIntegrityLaneItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = QsfpSignalIntegrityLaneItem.model_validate(data)
        elif isinstance(data, str):
            data = QsfpSignalIntegrityLaneItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.QsfpSignalIntegrityLaneItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import QsfpSignalIntegrityLaneItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = QsfpSignalIntegrityLaneItem.model_validate(data)
        elif isinstance(data, str):
            data = QsfpSignalIntegrityLaneItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class QsfpSignalIntegrityLaneListNode(ListNode[QsfpSignalIntegrityLaneItemNode]):
    """Navigator for list qsfp-signal-integrity-lane"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.QsfpSignalIntegrityLaneItem]:
        from ..data_models.ne import QsfpSignalIntegrityLaneItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [QsfpSignalIntegrityLaneItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.QsfpSignalIntegrityLaneItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.QsfpSignalIntegrityLaneItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class QsfpSignalIntegrityNode(Node):
    """Navigator for qsfp-signal-integrity"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.QsfpSignalIntegrity:
        from ..data_models.ne import QsfpSignalIntegrity
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return QsfpSignalIntegrity.model_validate(resp)

    def update(self, data: ne.QsfpSignalIntegrity | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import QsfpSignalIntegrity

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = QsfpSignalIntegrity.model_validate(data)
        elif isinstance(data, str):
            data = QsfpSignalIntegrity.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.QsfpSignalIntegrity | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import QsfpSignalIntegrity

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = QsfpSignalIntegrity.model_validate(data)
        elif isinstance(data, str):
            data = QsfpSignalIntegrity.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def qsfp_signal_integrity_lane(self) -> QsfpSignalIntegrityLaneListNode:
        return QsfpSignalIntegrityLaneListNode(self._client, f"{self._path}/qsfp-signal-integrity-lane", "qsfp-signal-integrity-lane", QsfpSignalIntegrityLaneItemNode)

class PluggableNode(Node):
    """Navigator for pluggable"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Pluggable:
        from ..data_models.ne import Pluggable
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Pluggable.model_validate(resp)

    def update(self, data: ne.Pluggable | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Pluggable

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Pluggable.model_validate(data)
        elif isinstance(data, str):
            data = Pluggable.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Pluggable | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Pluggable

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Pluggable.model_validate(data)
        elif isinstance(data, str):
            data = Pluggable.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def channel_states(self) -> ChannelStatesListNode:
        return ChannelStatesListNode(self._client, f"{self._path}/channel-states", "channel-states", ChannelStatesItemNode)
    @property
    def diagnostic_alarm_thresholds(self) -> DiagnosticAlarmThresholdsListNode:
        return DiagnosticAlarmThresholdsListNode(self._client, f"{self._path}/diagnostic-alarm-thresholds", "diagnostic-alarm-thresholds", DiagnosticAlarmThresholdsItemNode)
    @property
    def qsfp_signal_integrity(self) -> QsfpSignalIntegrityNode:
        return QsfpSignalIntegrityNode(self._client, f"{self._path}/qsfp-signal-integrity", "qsfp-signal-integrity")

class DifferentialGroupDelayNode(Node):
    """Navigator for differential-group-delay"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DifferentialGroupDelay:
        from ..data_models.ne import DifferentialGroupDelay
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DifferentialGroupDelay.model_validate(resp)

    def update(self, data: ne.DifferentialGroupDelay | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DifferentialGroupDelay

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DifferentialGroupDelay.model_validate(data)
        elif isinstance(data, str):
            data = DifferentialGroupDelay.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.DifferentialGroupDelay | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DifferentialGroupDelay

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DifferentialGroupDelay.model_validate(data)
        elif isinstance(data, str):
            data = DifferentialGroupDelay.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ChromaticDispersionNode(Node):
    """Navigator for chromatic-dispersion"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ChromaticDispersion:
        from ..data_models.ne import ChromaticDispersion
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChromaticDispersion.model_validate(resp)

    def update(self, data: ne.ChromaticDispersion | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChromaticDispersion

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChromaticDispersion.model_validate(data)
        elif isinstance(data, str):
            data = ChromaticDispersion.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ChromaticDispersion | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChromaticDispersion

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChromaticDispersion.model_validate(data)
        elif isinstance(data, str):
            data = ChromaticDispersion.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OsnrNode(Node):
    """Navigator for osnr"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Osnr:
        from ..data_models.ne import Osnr
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Osnr.model_validate(resp)

    def update(self, data: ne.Osnr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Osnr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Osnr.model_validate(data)
        elif isinstance(data, str):
            data = Osnr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Osnr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Osnr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Osnr.model_validate(data)
        elif isinstance(data, str):
            data = Osnr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class QFactorNode(Node):
    """Navigator for q-factor"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.QFactor:
        from ..data_models.ne import QFactor
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return QFactor.model_validate(resp)

    def update(self, data: ne.QFactor | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import QFactor

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = QFactor.model_validate(data)
        elif isinstance(data, str):
            data = QFactor.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.QFactor | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import QFactor

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = QFactor.model_validate(data)
        elif isinstance(data, str):
            data = QFactor.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class PolarizationDependentLossNode(Node):
    """Navigator for polarization-dependent-loss"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PolarizationDependentLoss:
        from ..data_models.ne import PolarizationDependentLoss
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PolarizationDependentLoss.model_validate(resp)

    def update(self, data: ne.PolarizationDependentLoss | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PolarizationDependentLoss

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PolarizationDependentLoss.model_validate(data)
        elif isinstance(data, str):
            data = PolarizationDependentLoss.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PolarizationDependentLoss | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PolarizationDependentLoss

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PolarizationDependentLoss.model_validate(data)
        elif isinstance(data, str):
            data = PolarizationDependentLoss.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InOpticalFrequencyNode(Node):
    """Navigator for in-optical-frequency"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InOpticalFrequency:
        from ..data_models.ne import InOpticalFrequency
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InOpticalFrequency.model_validate(resp)

    def update(self, data: ne.InOpticalFrequency | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalFrequency

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalFrequency.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalFrequency.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InOpticalFrequency | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalFrequency

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalFrequency.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalFrequency.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutOpticalFrequencyNode(Node):
    """Navigator for out-optical-frequency"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutOpticalFrequency:
        from ..data_models.ne import OutOpticalFrequency
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutOpticalFrequency.model_validate(resp)

    def update(self, data: ne.OutOpticalFrequency | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalFrequency

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalFrequency.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalFrequency.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutOpticalFrequency | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalFrequency

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalFrequency.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalFrequency.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SopChangeRateNode(Node):
    """Navigator for sop-change-rate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SopChangeRate:
        from ..data_models.ne import SopChangeRate
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SopChangeRate.model_validate(resp)

    def update(self, data: ne.SopChangeRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SopChangeRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SopChangeRate.model_validate(data)
        elif isinstance(data, str):
            data = SopChangeRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SopChangeRate | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SopChangeRate

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SopChangeRate.model_validate(data)
        elif isinstance(data, str):
            data = SopChangeRate.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class Otuc4Node(Node):
    """Navigator for otuc4"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc4:
        from ..data_models.ne import Otuc4
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc4.model_validate(resp)

    def update(self, data: ne.Otuc4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc4.model_validate(data)
        elif isinstance(data, str):
            data = Otuc4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc4.model_validate(data)
        elif isinstance(data, str):
            data = Otuc4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otuc5Node(Node):
    """Navigator for otuc5"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc5:
        from ..data_models.ne import Otuc5
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc5.model_validate(resp)

    def update(self, data: ne.Otuc5 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc5

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc5.model_validate(data)
        elif isinstance(data, str):
            data = Otuc5.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc5 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc5

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc5.model_validate(data)
        elif isinstance(data, str):
            data = Otuc5.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otuc7Node(Node):
    """Navigator for otuc7"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc7:
        from ..data_models.ne import Otuc7
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc7.model_validate(resp)

    def update(self, data: ne.Otuc7 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc7

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc7.model_validate(data)
        elif isinstance(data, str):
            data = Otuc7.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc7 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc7

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc7.model_validate(data)
        elif isinstance(data, str):
            data = Otuc7.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otuc9Node(Node):
    """Navigator for otuc9"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc9:
        from ..data_models.ne import Otuc9
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc9.model_validate(resp)

    def update(self, data: ne.Otuc9 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc9

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc9.model_validate(data)
        elif isinstance(data, str):
            data = Otuc9.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc9 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc9

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc9.model_validate(data)
        elif isinstance(data, str):
            data = Otuc9.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class Otuc11Node(Node):
    """Navigator for otuc11"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Otuc11:
        from ..data_models.ne import Otuc11
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Otuc11.model_validate(resp)

    def update(self, data: ne.Otuc11 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc11

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc11.model_validate(data)
        elif isinstance(data, str):
            data = Otuc11.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Otuc11 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Otuc11

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Otuc11.model_validate(data)
        elif isinstance(data, str):
            data = Otuc11.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class OchOsNode(Node):
    """Navigator for och-os"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OchOs:
        from ..data_models.ne import OchOs
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OchOs.model_validate(resp)

    def update(self, data: ne.OchOs | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchOs

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchOs.model_validate(data)
        elif isinstance(data, str):
            data = OchOs.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OchOs | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchOs

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchOs.model_validate(data)
        elif isinstance(data, str):
            data = OchOs.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def otuc2(self) -> Otuc2Node:
        return Otuc2Node(self._client, f"{self._path}/otuc2", "otuc2")
    @property
    def otuc3(self) -> Otuc3Node:
        return Otuc3Node(self._client, f"{self._path}/otuc3", "otuc3")
    @property
    def otuc4(self) -> Otuc4Node:
        return Otuc4Node(self._client, f"{self._path}/otuc4", "otuc4")
    @property
    def otuc5(self) -> Otuc5Node:
        return Otuc5Node(self._client, f"{self._path}/otuc5", "otuc5")
    @property
    def otuc6(self) -> Otuc6Node:
        return Otuc6Node(self._client, f"{self._path}/otuc6", "otuc6")
    @property
    def otuc7(self) -> Otuc7Node:
        return Otuc7Node(self._client, f"{self._path}/otuc7", "otuc7")
    @property
    def otuc9(self) -> Otuc9Node:
        return Otuc9Node(self._client, f"{self._path}/otuc9", "otuc9")
    @property
    def otuc11(self) -> Otuc11Node:
        return Otuc11Node(self._client, f"{self._path}/otuc11", "otuc11")
    @property
    def otu4(self) -> Otu4Node:
        return Otu4Node(self._client, f"{self._path}/otu4", "otu4")
    @property
    def otu2(self) -> Otu2Node:
        return Otu2Node(self._client, f"{self._path}/otu2", "otu2")
    @property
    def otu2e(self) -> Otu2eNode:
        return Otu2eNode(self._client, f"{self._path}/otu2e", "otu2e")

class OtdrPortNode(Node):
    """Navigator for otdr-port"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OtdrPort:
        from ..data_models.ne import OtdrPort
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtdrPort.model_validate(resp)

    def update(self, data: ne.OtdrPort | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OtdrPort

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtdrPort.model_validate(data)
        elif isinstance(data, str):
            data = OtdrPort.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OtdrPort | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OtdrPort

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtdrPort.model_validate(data)
        elif isinstance(data, str):
            data = OtdrPort.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class MonitoredChannelsItemNode(ItemNode):
    """Navigator for list item monitored-channels"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.MonitoredChannelsItem:
        from ..data_models.ne import MonitoredChannelsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return MonitoredChannelsItem.model_validate(resp)

    def update(self, data: ne.MonitoredChannelsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MonitoredChannelsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MonitoredChannelsItem.model_validate(data)
        elif isinstance(data, str):
            data = MonitoredChannelsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.MonitoredChannelsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MonitoredChannelsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MonitoredChannelsItem.model_validate(data)
        elif isinstance(data, str):
            data = MonitoredChannelsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class MonitoredChannelsListNode(ListNode[MonitoredChannelsItemNode]):
    """Navigator for list monitored-channels"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.MonitoredChannelsItem]:
        from ..data_models.ne import MonitoredChannelsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [MonitoredChannelsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.MonitoredChannelsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.MonitoredChannelsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OcmPortNode(Node):
    """Navigator for ocm-port"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OcmPort:
        from ..data_models.ne import OcmPort
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcmPort.model_validate(resp)

    def update(self, data: ne.OcmPort | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OcmPort

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmPort.model_validate(data)
        elif isinstance(data, str):
            data = OcmPort.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OcmPort | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OcmPort

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmPort.model_validate(data)
        elif isinstance(data, str):
            data = OcmPort.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def monitored_channels(self) -> MonitoredChannelsListNode:
        return MonitoredChannelsListNode(self._client, f"{self._path}/monitored-channels", "monitored-channels", MonitoredChannelsItemNode)

class InOpticalPowerLaneHighNode(Node):
    """Navigator for in-optical-power-lane-high"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InOpticalPowerLaneHigh:
        from ..data_models.ne import InOpticalPowerLaneHigh
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InOpticalPowerLaneHigh.model_validate(resp)

    def update(self, data: ne.InOpticalPowerLaneHigh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPowerLaneHigh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPowerLaneHigh.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPowerLaneHigh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InOpticalPowerLaneHigh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPowerLaneHigh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPowerLaneHigh.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPowerLaneHigh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InOpticalPowerLaneLowNode(Node):
    """Navigator for in-optical-power-lane-low"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InOpticalPowerLaneLow:
        from ..data_models.ne import InOpticalPowerLaneLow
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InOpticalPowerLaneLow.model_validate(resp)

    def update(self, data: ne.InOpticalPowerLaneLow | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPowerLaneLow

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPowerLaneLow.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPowerLaneLow.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InOpticalPowerLaneLow | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPowerLaneLow

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPowerLaneLow.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPowerLaneLow.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InOpticalPowerLaneTotalNode(Node):
    """Navigator for in-optical-power-lane-total"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InOpticalPowerLaneTotal:
        from ..data_models.ne import InOpticalPowerLaneTotal
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InOpticalPowerLaneTotal.model_validate(resp)

    def update(self, data: ne.InOpticalPowerLaneTotal | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPowerLaneTotal

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPowerLaneTotal.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPowerLaneTotal.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InOpticalPowerLaneTotal | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InOpticalPowerLaneTotal

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InOpticalPowerLaneTotal.model_validate(data)
        elif isinstance(data, str):
            data = InOpticalPowerLaneTotal.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutOpticalPowerLaneHighNode(Node):
    """Navigator for out-optical-power-lane-high"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutOpticalPowerLaneHigh:
        from ..data_models.ne import OutOpticalPowerLaneHigh
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutOpticalPowerLaneHigh.model_validate(resp)

    def update(self, data: ne.OutOpticalPowerLaneHigh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPowerLaneHigh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPowerLaneHigh.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPowerLaneHigh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutOpticalPowerLaneHigh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPowerLaneHigh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPowerLaneHigh.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPowerLaneHigh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutOpticalPowerLaneLowNode(Node):
    """Navigator for out-optical-power-lane-low"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutOpticalPowerLaneLow:
        from ..data_models.ne import OutOpticalPowerLaneLow
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutOpticalPowerLaneLow.model_validate(resp)

    def update(self, data: ne.OutOpticalPowerLaneLow | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPowerLaneLow

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPowerLaneLow.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPowerLaneLow.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutOpticalPowerLaneLow | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPowerLaneLow

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPowerLaneLow.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPowerLaneLow.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutOpticalPowerLaneTotalNode(Node):
    """Navigator for out-optical-power-lane-total"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutOpticalPowerLaneTotal:
        from ..data_models.ne import OutOpticalPowerLaneTotal
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutOpticalPowerLaneTotal.model_validate(resp)

    def update(self, data: ne.OutOpticalPowerLaneTotal | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPowerLaneTotal

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPowerLaneTotal.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPowerLaneTotal.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutOpticalPowerLaneTotal | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutOpticalPowerLaneTotal

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutOpticalPowerLaneTotal.model_validate(data)
        elif isinstance(data, str):
            data = OutOpticalPowerLaneTotal.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class Eth1gNode(Node):
    """Navigator for eth1g"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Eth1g:
        from ..data_models.ne import Eth1g
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Eth1g.model_validate(resp)

    def update(self, data: ne.Eth1g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth1g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth1g.model_validate(data)
        elif isinstance(data, str):
            data = Eth1g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Eth1g | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Eth1g

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Eth1g.model_validate(data)
        elif isinstance(data, str):
            data = Eth1g.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def test_signal_facility_status(self) -> TestSignalFacilityStatusNode:
        return TestSignalFacilityStatusNode(self._client, f"{self._path}/test-signal-facility-status", "test-signal-facility-status")
    @property
    def lldp_remote_system(self) -> LldpRemoteSystemListNode:
        return LldpRemoteSystemListNode(self._client, f"{self._path}/lldp-remote-system", "lldp-remote-system", LldpRemoteSystemItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

class PortItemNode(ItemNode):
    """Navigator for list item port"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PortItem:
        from ..data_models.ne import PortItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PortItem.model_validate(resp)

    def update(self, data: ne.PortItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PortItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PortItem.model_validate(data)
        elif isinstance(data, str):
            data = PortItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PortItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PortItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PortItem.model_validate(data)
        elif isinstance(data, str):
            data = PortItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def optical_power_lane(self) -> OpticalPowerLaneListNode:
        return OpticalPowerLaneListNode(self._client, f"{self._path}/optical-power-lane", "optical-power-lane", OpticalPowerLaneItemNode)
    @property
    def subport(self) -> SubportListNode:
        return SubportListNode(self._client, f"{self._path}/subport", "subport", SubportItemNode)
    @property
    def pluggable(self) -> PluggableNode:
        return PluggableNode(self._client, f"{self._path}/pluggable", "pluggable")
    @property
    def och_os(self) -> OchOsNode:
        return OchOsNode(self._client, f"{self._path}/och-os", "och-os")
    @property
    def eth10g(self) -> Eth10gNode:
        return Eth10gNode(self._client, f"{self._path}/eth10g", "eth10g")
    @property
    def eth40g(self) -> Eth40gNode:
        return Eth40gNode(self._client, f"{self._path}/eth40g", "eth40g")
    @property
    def eth100g(self) -> Eth100gNode:
        return Eth100gNode(self._client, f"{self._path}/eth100g", "eth100g")
    @property
    def eth400g(self) -> Eth400gNode:
        return Eth400gNode(self._client, f"{self._path}/eth400g", "eth400g")
    @property
    def otu4(self) -> Otu4Node:
        return Otu4Node(self._client, f"{self._path}/otu4", "otu4")
    @property
    def otu2(self) -> Otu2Node:
        return Otu2Node(self._client, f"{self._path}/otu2", "otu2")
    @property
    def otu2e(self) -> Otu2eNode:
        return Otu2eNode(self._client, f"{self._path}/otu2e", "otu2e")
    @property
    def oc192(self) -> Oc192Node:
        return Oc192Node(self._client, f"{self._path}/oc192", "oc192")
    @property
    def oc48(self) -> Oc48Node:
        return Oc48Node(self._client, f"{self._path}/oc48", "oc48")
    @property
    def stm64(self) -> Stm64Node:
        return Stm64Node(self._client, f"{self._path}/stm64", "stm64")
    @property
    def stm16(self) -> Stm16Node:
        return Stm16Node(self._client, f"{self._path}/stm16", "stm16")
    @property
    def wan10g_sonet(self) -> Wan10gSonetNode:
        return Wan10gSonetNode(self._client, f"{self._path}/wan10g-sonet", "wan10g-sonet")
    @property
    def wan10g_sdh(self) -> Wan10gSdhNode:
        return Wan10gSdhNode(self._client, f"{self._path}/wan10g-sdh", "wan10g-sdh")
    @property
    def fc1g(self) -> Fc1gNode:
        return Fc1gNode(self._client, f"{self._path}/fc1g", "fc1g")
    @property
    def fc4g(self) -> Fc4gNode:
        return Fc4gNode(self._client, f"{self._path}/fc4g", "fc4g")
    @property
    def fc8g(self) -> Fc8gNode:
        return Fc8gNode(self._client, f"{self._path}/fc8g", "fc8g")
    @property
    def fc16g(self) -> Fc16gNode:
        return Fc16gNode(self._client, f"{self._path}/fc16g", "fc16g")
    @property
    def otdr_port(self) -> OtdrPortNode:
        return OtdrPortNode(self._client, f"{self._path}/otdr-port", "otdr-port")
    @property
    def ocm_port(self) -> OcmPortNode:
        return OcmPortNode(self._client, f"{self._path}/ocm-port", "ocm-port")
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")
    @property
    def eth1g(self) -> Eth1gNode:
        return Eth1gNode(self._client, f"{self._path}/eth1g", "eth1g")

class PortListNode(ListNode[PortItemNode]):
    """Navigator for list port"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PortItem]:
        from ..data_models.ne import PortItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PortItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PortItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PortItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SupportedGainRangeItemNode(ItemNode):
    """Navigator for list item supported-gain-range"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SupportedGainRangeItem:
        from ..data_models.ne import SupportedGainRangeItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedGainRangeItem.model_validate(resp)

    def update(self, data: ne.SupportedGainRangeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SupportedGainRangeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedGainRangeItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedGainRangeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SupportedGainRangeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SupportedGainRangeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedGainRangeItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedGainRangeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SupportedGainRangeListNode(ListNode[SupportedGainRangeItemNode]):
    """Navigator for list supported-gain-range"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SupportedGainRangeItem]:
        from ..data_models.ne import SupportedGainRangeItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedGainRangeItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SupportedGainRangeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SupportedGainRangeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AmplifierItemNode(ItemNode):
    """Navigator for list item amplifier"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AmplifierItem:
        from ..data_models.ne import AmplifierItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AmplifierItem.model_validate(resp)

    def update(self, data: ne.AmplifierItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AmplifierItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AmplifierItem.model_validate(data)
        elif isinstance(data, str):
            data = AmplifierItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AmplifierItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AmplifierItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AmplifierItem.model_validate(data)
        elif isinstance(data, str):
            data = AmplifierItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def supported_gain_range(self) -> SupportedGainRangeListNode:
        return SupportedGainRangeListNode(self._client, f"{self._path}/supported-gain-range", "supported-gain-range", SupportedGainRangeItemNode)

class AmplifierListNode(ListNode[AmplifierItemNode]):
    """Navigator for list amplifier"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AmplifierItem]:
        from ..data_models.ne import AmplifierItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AmplifierItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AmplifierItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AmplifierItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class TdcItemNode(ItemNode):
    """Navigator for list item tdc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TdcItem:
        from ..data_models.ne import TdcItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TdcItem.model_validate(resp)

    def update(self, data: ne.TdcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TdcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TdcItem.model_validate(data)
        elif isinstance(data, str):
            data = TdcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.TdcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TdcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TdcItem.model_validate(data)
        elif isinstance(data, str):
            data = TdcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TdcListNode(ListNode[TdcItemNode]):
    """Navigator for list tdc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.TdcItem]:
        from ..data_models.ne import TdcItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TdcItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.TdcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.TdcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OpsItemNode(ItemNode):
    """Navigator for list item ops"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OpsItem:
        from ..data_models.ne import OpsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpsItem.model_validate(resp)

    def update(self, data: ne.OpsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpsItem.model_validate(data)
        elif isinstance(data, str):
            data = OpsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OpsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpsItem.model_validate(data)
        elif isinstance(data, str):
            data = OpsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OpsListNode(ListNode[OpsItemNode]):
    """Navigator for list ops"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OpsItem]:
        from ..data_models.ne import OpsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OpsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OpsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ModuleTemperatureNode(Node):
    """Navigator for module-temperature"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ModuleTemperature:
        from ..data_models.ne import ModuleTemperature
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ModuleTemperature.model_validate(resp)

    def update(self, data: ne.ModuleTemperature | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ModuleTemperature

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModuleTemperature.model_validate(data)
        elif isinstance(data, str):
            data = ModuleTemperature.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ModuleTemperature | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ModuleTemperature

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModuleTemperature.model_validate(data)
        elif isinstance(data, str):
            data = ModuleTemperature.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SubcardNode(Node):
    """Navigator for subcard"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Subcard:
        from ..data_models.ne import Subcard
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Subcard.model_validate(resp)

    def update(self, data: ne.Subcard | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Subcard

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Subcard.model_validate(data)
        elif isinstance(data, str):
            data = Subcard.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Subcard | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Subcard

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Subcard.model_validate(data)
        elif isinstance(data, str):
            data = Subcard.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def otdr(self) -> OtdrNode:
        return OtdrNode(self._client, f"{self._path}/otdr", "otdr")
    @property
    def port(self) -> PortListNode:
        return PortListNode(self._client, f"{self._path}/port", "port", PortItemNode)
    @property
    def amplifier(self) -> AmplifierListNode:
        return AmplifierListNode(self._client, f"{self._path}/amplifier", "amplifier", AmplifierItemNode)
    @property
    def tdc(self) -> TdcListNode:
        return TdcListNode(self._client, f"{self._path}/tdc", "tdc", TdcItemNode)
    @property
    def ops(self) -> OpsListNode:
        return OpsListNode(self._client, f"{self._path}/ops", "ops", OpsItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class SubslotItemNode(ItemNode):
    """Navigator for list item subslot"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SubslotItem:
        from ..data_models.ne import SubslotItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SubslotItem.model_validate(resp)

    def update(self, data: ne.SubslotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SubslotItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubslotItem.model_validate(data)
        elif isinstance(data, str):
            data = SubslotItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SubslotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SubslotItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubslotItem.model_validate(data)
        elif isinstance(data, str):
            data = SubslotItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def subcard(self) -> SubcardNode:
        return SubcardNode(self._client, f"{self._path}/subcard", "subcard")

class SubslotListNode(ListNode[SubslotItemNode]):
    """Navigator for list subslot"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SubslotItem]:
        from ..data_models.ne import SubslotItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SubslotItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SubslotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SubslotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CardNode(Node):
    """Navigator for card"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Card:
        from ..data_models.ne import Card
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Card.model_validate(resp)

    def update(self, data: ne.Card | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Card

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Card.model_validate(data)
        elif isinstance(data, str):
            data = Card.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Card | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Card

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Card.model_validate(data)
        elif isinstance(data, str):
            data = Card.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def temperature_details(self) -> TemperatureDetailsListNode:
        return TemperatureDetailsListNode(self._client, f"{self._path}/temperature-details", "temperature-details", TemperatureDetailsItemNode)
    @property
    def cpu_state(self) -> CpuStateNode:
        return CpuStateNode(self._client, f"{self._path}/cpu-state", "cpu-state")
    @property
    def memory_state(self) -> MemoryStateNode:
        return MemoryStateNode(self._client, f"{self._path}/memory-state", "memory-state")
    @property
    def subslot(self) -> SubslotListNode:
        return SubslotListNode(self._client, f"{self._path}/subslot", "subslot", SubslotItemNode)
    @property
    def port(self) -> PortListNode:
        return PortListNode(self._client, f"{self._path}/port", "port", PortItemNode)
    @property
    def amplifier(self) -> AmplifierListNode:
        return AmplifierListNode(self._client, f"{self._path}/amplifier", "amplifier", AmplifierItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class SlotItemNode(ItemNode):
    """Navigator for list item slot"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SlotItem:
        from ..data_models.ne import SlotItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SlotItem.model_validate(resp)

    def update(self, data: ne.SlotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SlotItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SlotItem.model_validate(data)
        elif isinstance(data, str):
            data = SlotItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SlotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SlotItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SlotItem.model_validate(data)
        elif isinstance(data, str):
            data = SlotItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def card(self) -> CardNode:
        return CardNode(self._client, f"{self._path}/card", "card")

class SlotListNode(ListNode[SlotItemNode]):
    """Navigator for list slot"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SlotItem]:
        from ..data_models.ne import SlotItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SlotItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SlotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SlotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class InletTemperatureNode(Node):
    """Navigator for inlet-temperature"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InletTemperature:
        from ..data_models.ne import InletTemperature
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InletTemperature.model_validate(resp)

    def update(self, data: ne.InletTemperature | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InletTemperature

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InletTemperature.model_validate(data)
        elif isinstance(data, str):
            data = InletTemperature.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InletTemperature | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InletTemperature

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InletTemperature.model_validate(data)
        elif isinstance(data, str):
            data = InletTemperature.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OutletTemperatureNode(Node):
    """Navigator for outlet-temperature"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OutletTemperature:
        from ..data_models.ne import OutletTemperature
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OutletTemperature.model_validate(resp)

    def update(self, data: ne.OutletTemperature | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutletTemperature

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutletTemperature.model_validate(data)
        elif isinstance(data, str):
            data = OutletTemperature.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OutletTemperature | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OutletTemperature

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OutletTemperature.model_validate(data)
        elif isinstance(data, str):
            data = OutletTemperature.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ShelfItemNode(ItemNode):
    """Navigator for list item shelf"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ShelfItem:
        from ..data_models.ne import ShelfItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ShelfItem.model_validate(resp)

    def update(self, data: ne.ShelfItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ShelfItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ShelfItem.model_validate(data)
        elif isinstance(data, str):
            data = ShelfItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ShelfItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ShelfItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ShelfItem.model_validate(data)
        elif isinstance(data, str):
            data = ShelfItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def slot(self) -> SlotListNode:
        return SlotListNode(self._client, f"{self._path}/slot", "slot", SlotItemNode)
    @property
    def temperature_details(self) -> TemperatureDetailsListNode:
        return TemperatureDetailsListNode(self._client, f"{self._path}/temperature-details", "temperature-details", TemperatureDetailsItemNode)
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class ShelfListNode(ListNode[ShelfItemNode]):
    """Navigator for list shelf"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ShelfItem]:
        from ..data_models.ne import ShelfItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ShelfItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ShelfItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ShelfItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class InventoryItemNode(ItemNode):
    """Navigator for list item inventory"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InventoryItem:
        from ..data_models.ne import InventoryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InventoryItem.model_validate(resp)

    def update(self, data: ne.InventoryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InventoryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InventoryItem.model_validate(data)
        elif isinstance(data, str):
            data = InventoryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.InventoryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InventoryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InventoryItem.model_validate(data)
        elif isinstance(data, str):
            data = InventoryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class InventoryListNode(ListNode[InventoryItemNode]):
    """Navigator for list inventory"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.InventoryItem]:
        from ..data_models.ne import InventoryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InventoryItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.InventoryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.InventoryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class InventoryDataNode(Node):
    """Navigator for inventory-data"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InventoryData:
        from ..data_models.ne import InventoryData
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InventoryData.model_validate(resp)

    def update(self, data: ne.InventoryData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InventoryData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InventoryData.model_validate(data)
        elif isinstance(data, str):
            data = InventoryData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.InventoryData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InventoryData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InventoryData.model_validate(data)
        elif isinstance(data, str):
            data = InventoryData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def inventory(self) -> InventoryListNode:
        return InventoryListNode(self._client, f"{self._path}/inventory", "inventory", InventoryItemNode)

class LedItemNode(ItemNode):
    """Navigator for list item led"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.LedItem:
        from ..data_models.ne import LedItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LedItem.model_validate(resp)

    def update(self, data: ne.LedItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LedItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LedItem.model_validate(data)
        elif isinstance(data, str):
            data = LedItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.LedItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LedItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LedItem.model_validate(data)
        elif isinstance(data, str):
            data = LedItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LedListNode(ListNode[LedItemNode]):
    """Navigator for list led"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.LedItem]:
        from ..data_models.ne import LedItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LedItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.LedItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.LedItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class LedsNode(Node):
    """Navigator for leds"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Leds:
        from ..data_models.ne import Leds
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Leds.model_validate(resp)

    def update(self, data: ne.Leds | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Leds

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Leds.model_validate(data)
        elif isinstance(data, str):
            data = Leds.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Leds | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Leds

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Leds.model_validate(data)
        elif isinstance(data, str):
            data = Leds.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def led(self) -> LedListNode:
        return LedListNode(self._client, f"{self._path}/led", "led", LedItemNode)

class CrsItemNode(ItemNode):
    """Navigator for list item CRS"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CrsItem:
        from ..data_models.ne import CrsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CrsItem.model_validate(resp)

    def update(self, data: ne.CrsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CrsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CrsItem.model_validate(data)
        elif isinstance(data, str):
            data = CrsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.CrsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CrsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CrsItem.model_validate(data)
        elif isinstance(data, str):
            data = CrsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CrsListNode(ListNode[CrsItemNode]):
    """Navigator for list CRS"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.CrsItem]:
        from ..data_models.ne import CrsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CrsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.CrsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.CrsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class FiberConnectionItemNode(ItemNode):
    """Navigator for list item fiber-connection"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.FiberConnectionItem:
        from ..data_models.ne import FiberConnectionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FiberConnectionItem.model_validate(resp)

    def update(self, data: ne.FiberConnectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FiberConnectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FiberConnectionItem.model_validate(data)
        elif isinstance(data, str):
            data = FiberConnectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.FiberConnectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FiberConnectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FiberConnectionItem.model_validate(data)
        elif isinstance(data, str):
            data = FiberConnectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FiberConnectionListNode(ListNode[FiberConnectionItemNode]):
    """Navigator for list fiber-connection"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.FiberConnectionItem]:
        from ..data_models.ne import FiberConnectionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FiberConnectionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.FiberConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.FiberConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class InternalLinkItemNode(ItemNode):
    """Navigator for list item internal-link"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InternalLinkItem:
        from ..data_models.ne import InternalLinkItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InternalLinkItem.model_validate(resp)

    def update(self, data: ne.InternalLinkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InternalLinkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InternalLinkItem.model_validate(data)
        elif isinstance(data, str):
            data = InternalLinkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.InternalLinkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InternalLinkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InternalLinkItem.model_validate(data)
        elif isinstance(data, str):
            data = InternalLinkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class InternalLinkListNode(ListNode[InternalLinkItemNode]):
    """Navigator for list internal-link"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.InternalLinkItem]:
        from ..data_models.ne import InternalLinkItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InternalLinkItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.InternalLinkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.InternalLinkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OtsDiagnosticsNode(Node):
    """Navigator for ots-diagnostics"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OtsDiagnostics:
        from ..data_models.ne import OtsDiagnostics
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtsDiagnostics.model_validate(resp)

    def update(self, data: ne.OtsDiagnostics | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OtsDiagnostics

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtsDiagnostics.model_validate(data)
        elif isinstance(data, str):
            data = OtsDiagnostics.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OtsDiagnostics | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OtsDiagnostics

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtsDiagnostics.model_validate(data)
        elif isinstance(data, str):
            data = OtsDiagnostics.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OtsItemNode(ItemNode):
    """Navigator for list item ots"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OtsItem:
        from ..data_models.ne import OtsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtsItem.model_validate(resp)

    def update(self, data: ne.OtsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OtsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtsItem.model_validate(data)
        elif isinstance(data, str):
            data = OtsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OtsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OtsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtsItem.model_validate(data)
        elif isinstance(data, str):
            data = OtsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ots_diagnostics(self) -> OtsDiagnosticsNode:
        return OtsDiagnosticsNode(self._client, f"{self._path}/ots-diagnostics", "ots-diagnostics")

class OtsListNode(ListNode[OtsItemNode]):
    """Navigator for list ots"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OtsItem]:
        from ..data_models.ne import OtsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OtsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OtsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OpticalReturnLossNode(Node):
    """Navigator for optical-return-loss"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OpticalReturnLoss:
        from ..data_models.ne import OpticalReturnLoss
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalReturnLoss.model_validate(resp)

    def update(self, data: ne.OpticalReturnLoss | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpticalReturnLoss

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalReturnLoss.model_validate(data)
        elif isinstance(data, str):
            data = OpticalReturnLoss.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OpticalReturnLoss | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpticalReturnLoss

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalReturnLoss.model_validate(data)
        elif isinstance(data, str):
            data = OpticalReturnLoss.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OmsItemNode(ItemNode):
    """Navigator for list item oms"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OmsItem:
        from ..data_models.ne import OmsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OmsItem.model_validate(resp)

    def update(self, data: ne.OmsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OmsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OmsItem.model_validate(data)
        elif isinstance(data, str):
            data = OmsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OmsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OmsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OmsItem.model_validate(data)
        elif isinstance(data, str):
            data = OmsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class OmsListNode(ListNode[OmsItemNode]):
    """Navigator for list oms"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OmsItem]:
        from ..data_models.ne import OmsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OmsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OmsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OmsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DelayMeasurementDistanceNode(Node):
    """Navigator for delay-measurement-distance"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DelayMeasurementDistance:
        from ..data_models.ne import DelayMeasurementDistance
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DelayMeasurementDistance.model_validate(resp)

    def update(self, data: ne.DelayMeasurementDistance | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DelayMeasurementDistance

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DelayMeasurementDistance.model_validate(data)
        elif isinstance(data, str):
            data = DelayMeasurementDistance.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.DelayMeasurementDistance | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DelayMeasurementDistance

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DelayMeasurementDistance.model_validate(data)
        elif isinstance(data, str):
            data = DelayMeasurementDistance.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class RoundTripDelayNode(Node):
    """Navigator for round-trip-delay"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RoundTripDelay:
        from ..data_models.ne import RoundTripDelay
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RoundTripDelay.model_validate(resp)

    def update(self, data: ne.RoundTripDelay | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RoundTripDelay

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RoundTripDelay.model_validate(data)
        elif isinstance(data, str):
            data = RoundTripDelay.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.RoundTripDelay | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RoundTripDelay

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RoundTripDelay.model_validate(data)
        elif isinstance(data, str):
            data = RoundTripDelay.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class RtdBaselineNode(Node):
    """Navigator for rtd-baseline"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RtdBaseline:
        from ..data_models.ne import RtdBaseline
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RtdBaseline.model_validate(resp)

    def update(self, data: ne.RtdBaseline | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RtdBaseline

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RtdBaseline.model_validate(data)
        elif isinstance(data, str):
            data = RtdBaseline.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.RtdBaseline | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RtdBaseline

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RtdBaseline.model_validate(data)
        elif isinstance(data, str):
            data = RtdBaseline.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OscItemNode(ItemNode):
    """Navigator for list item osc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OscItem:
        from ..data_models.ne import OscItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OscItem.model_validate(resp)

    def update(self, data: ne.OscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OscItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OscItem.model_validate(data)
        elif isinstance(data, str):
            data = OscItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OscItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OscItem.model_validate(data)
        elif isinstance(data, str):
            data = OscItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class OscListNode(ListNode[OscItemNode]):
    """Navigator for list osc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OscItem]:
        from ..data_models.ne import OscItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OscItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class GoptItemNode(ItemNode):
    """Navigator for list item gopt"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.GoptItem:
        from ..data_models.ne import GoptItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return GoptItem.model_validate(resp)

    def update(self, data: ne.GoptItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import GoptItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GoptItem.model_validate(data)
        elif isinstance(data, str):
            data = GoptItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.GoptItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import GoptItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GoptItem.model_validate(data)
        elif isinstance(data, str):
            data = GoptItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class GoptListNode(ListNode[GoptItemNode]):
    """Navigator for list gopt"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.GoptItem]:
        from ..data_models.ne import GoptItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [GoptItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.GoptItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.GoptItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OchInputNode(Node):
    """Navigator for och-input"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OchInput:
        from ..data_models.ne import OchInput
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OchInput.model_validate(resp)

    def update(self, data: ne.OchInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchInput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchInput.model_validate(data)
        elif isinstance(data, str):
            data = OchInput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OchInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchInput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchInput.model_validate(data)
        elif isinstance(data, str):
            data = OchInput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OchOutputNode(Node):
    """Navigator for och-output"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OchOutput:
        from ..data_models.ne import OchOutput
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OchOutput.model_validate(resp)

    def update(self, data: ne.OchOutput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchOutput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchOutput.model_validate(data)
        elif isinstance(data, str):
            data = OchOutput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OchOutput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchOutput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchOutput.model_validate(data)
        elif isinstance(data, str):
            data = OchOutput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class OchOpticalAttenuationNode(Node):
    """Navigator for och-optical-attenuation"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OchOpticalAttenuation:
        from ..data_models.ne import OchOpticalAttenuation
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OchOpticalAttenuation.model_validate(resp)

    def update(self, data: ne.OchOpticalAttenuation | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchOpticalAttenuation

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchOpticalAttenuation.model_validate(data)
        elif isinstance(data, str):
            data = OchOpticalAttenuation.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OchOpticalAttenuation | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchOpticalAttenuation

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchOpticalAttenuation.model_validate(data)
        elif isinstance(data, str):
            data = OchOpticalAttenuation.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def och_input(self) -> OchInputNode:
        return OchInputNode(self._client, f"{self._path}/och-input", "och-input")
    @property
    def och_output(self) -> OchOutputNode:
        return OchOutputNode(self._client, f"{self._path}/och-output", "och-output")

class OchItemNode(ItemNode):
    """Navigator for list item och"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OchItem:
        from ..data_models.ne import OchItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OchItem.model_validate(resp)

    def update(self, data: ne.OchItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchItem.model_validate(data)
        elif isinstance(data, str):
            data = OchItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OchItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OchItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchItem.model_validate(data)
        elif isinstance(data, str):
            data = OchItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def och_optical_attenuation(self) -> OchOpticalAttenuationNode:
        return OchOpticalAttenuationNode(self._client, f"{self._path}/och-optical-attenuation", "och-optical-attenuation")

class OchListNode(ListNode[OchItemNode]):
    """Navigator for list och"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OchItem]:
        from ..data_models.ne import OchItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OchItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OchItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OchItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class McItemNode(ItemNode):
    """Navigator for list item mc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.McItem:
        from ..data_models.ne import McItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return McItem.model_validate(resp)

    def update(self, data: ne.McItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import McItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = McItem.model_validate(data)
        elif isinstance(data, str):
            data = McItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.McItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import McItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = McItem.model_validate(data)
        elif isinstance(data, str):
            data = McItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class McListNode(ListNode[McItemNode]):
    """Navigator for list mc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.McItem]:
        from ..data_models.ne import McItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [McItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.McItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.McItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class NmcInputNode(Node):
    """Navigator for nmc-input"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NmcInput:
        from ..data_models.ne import NmcInput
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NmcInput.model_validate(resp)

    def update(self, data: ne.NmcInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcInput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcInput.model_validate(data)
        elif isinstance(data, str):
            data = NmcInput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.NmcInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcInput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcInput.model_validate(data)
        elif isinstance(data, str):
            data = NmcInput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NmcOutputNode(Node):
    """Navigator for nmc-output"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NmcOutput:
        from ..data_models.ne import NmcOutput
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NmcOutput.model_validate(resp)

    def update(self, data: ne.NmcOutput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcOutput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcOutput.model_validate(data)
        elif isinstance(data, str):
            data = NmcOutput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.NmcOutput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcOutput

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcOutput.model_validate(data)
        elif isinstance(data, str):
            data = NmcOutput.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NmcOpticalAttenuationNode(Node):
    """Navigator for nmc-optical-attenuation"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NmcOpticalAttenuation:
        from ..data_models.ne import NmcOpticalAttenuation
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NmcOpticalAttenuation.model_validate(resp)

    def update(self, data: ne.NmcOpticalAttenuation | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcOpticalAttenuation

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcOpticalAttenuation.model_validate(data)
        elif isinstance(data, str):
            data = NmcOpticalAttenuation.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.NmcOpticalAttenuation | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcOpticalAttenuation

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcOpticalAttenuation.model_validate(data)
        elif isinstance(data, str):
            data = NmcOpticalAttenuation.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def nmc_input(self) -> NmcInputNode:
        return NmcInputNode(self._client, f"{self._path}/nmc-input", "nmc-input")
    @property
    def nmc_output(self) -> NmcOutputNode:
        return NmcOutputNode(self._client, f"{self._path}/nmc-output", "nmc-output")

class NmcItemNode(ItemNode):
    """Navigator for list item nmc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NmcItem:
        from ..data_models.ne import NmcItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NmcItem.model_validate(resp)

    def update(self, data: ne.NmcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcItem.model_validate(data)
        elif isinstance(data, str):
            data = NmcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.NmcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NmcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcItem.model_validate(data)
        elif isinstance(data, str):
            data = NmcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def nmc_optical_attenuation(self) -> NmcOpticalAttenuationNode:
        return NmcOpticalAttenuationNode(self._client, f"{self._path}/nmc-optical-attenuation", "nmc-optical-attenuation")
    @property
    def statistics(self) -> StatisticsNode:
        return StatisticsNode(self._client, f"{self._path}/statistics", "statistics")

class NmcListNode(ListNode[NmcItemNode]):
    """Navigator for list nmc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.NmcItem]:
        from ..data_models.ne import NmcItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NmcItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.NmcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.NmcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OpticalInterfacesNode(Node):
    """Navigator for optical-interfaces"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OpticalInterfaces:
        from ..data_models.ne import OpticalInterfaces
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalInterfaces.model_validate(resp)

    def update(self, data: ne.OpticalInterfaces | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpticalInterfaces

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalInterfaces.model_validate(data)
        elif isinstance(data, str):
            data = OpticalInterfaces.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.OpticalInterfaces | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OpticalInterfaces

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalInterfaces.model_validate(data)
        elif isinstance(data, str):
            data = OpticalInterfaces.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ots(self) -> OtsListNode:
        return OtsListNode(self._client, f"{self._path}/ots", "ots", OtsItemNode)
    @property
    def oms(self) -> OmsListNode:
        return OmsListNode(self._client, f"{self._path}/oms", "oms", OmsItemNode)
    @property
    def osc(self) -> OscListNode:
        return OscListNode(self._client, f"{self._path}/osc", "osc", OscItemNode)
    @property
    def gopt(self) -> GoptListNode:
        return GoptListNode(self._client, f"{self._path}/gopt", "gopt", GoptItemNode)
    @property
    def och(self) -> OchListNode:
        return OchListNode(self._client, f"{self._path}/och", "och", OchItemNode)
    @property
    def mc(self) -> McListNode:
        return McListNode(self._client, f"{self._path}/mc", "mc", McItemNode)
    @property
    def nmc(self) -> NmcListNode:
        return NmcListNode(self._client, f"{self._path}/nmc", "nmc", NmcItemNode)

class OcrsItemNode(ItemNode):
    """Navigator for list item OCRS"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OcrsItem:
        from ..data_models.ne import OcrsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcrsItem.model_validate(resp)

    def update(self, data: ne.OcrsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OcrsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcrsItem.model_validate(data)
        elif isinstance(data, str):
            data = OcrsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OcrsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OcrsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcrsItem.model_validate(data)
        elif isinstance(data, str):
            data = OcrsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OcrsListNode(ListNode[OcrsItemNode]):
    """Navigator for list OCRS"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OcrsItem]:
        from ..data_models.ne import OcrsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OcrsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OcrsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OcrsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ModulesItemNode(ItemNode):
    """Navigator for list item modules"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ModulesItem:
        from ..data_models.ne import ModulesItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ModulesItem.model_validate(resp)

    def update(self, data: ne.ModulesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ModulesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModulesItem.model_validate(data)
        elif isinstance(data, str):
            data = ModulesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ModulesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ModulesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModulesItem.model_validate(data)
        elif isinstance(data, str):
            data = ModulesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ModulesListNode(ListNode[ModulesItemNode]):
    """Navigator for list modules"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ModulesItem]:
        from ..data_models.ne import ModulesItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ModulesItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ModulesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ModulesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ConnectionPortsItemNode(ItemNode):
    """Navigator for list item connection-ports"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ConnectionPortsItem:
        from ..data_models.ne import ConnectionPortsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ConnectionPortsItem.model_validate(resp)

    def update(self, data: ne.ConnectionPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ConnectionPortsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ConnectionPortsItem.model_validate(data)
        elif isinstance(data, str):
            data = ConnectionPortsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ConnectionPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ConnectionPortsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ConnectionPortsItem.model_validate(data)
        elif isinstance(data, str):
            data = ConnectionPortsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ConnectionPortsListNode(ListNode[ConnectionPortsItemNode]):
    """Navigator for list connection-ports"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ConnectionPortsItem]:
        from ..data_models.ne import ConnectionPortsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ConnectionPortsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ConnectionPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ConnectionPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AssociatedOtdrPortNode(Node):
    """Navigator for associated-otdr-port"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AssociatedOtdrPort:
        from ..data_models.ne import AssociatedOtdrPort
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AssociatedOtdrPort.model_validate(resp)

    def update(self, data: ne.AssociatedOtdrPort | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AssociatedOtdrPort

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AssociatedOtdrPort.model_validate(data)
        elif isinstance(data, str):
            data = AssociatedOtdrPort.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AssociatedOtdrPort | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AssociatedOtdrPort

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AssociatedOtdrPort.model_validate(data)
        elif isinstance(data, str):
            data = AssociatedOtdrPort.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class McCapabilitiesNode(Node):
    """Navigator for mc-capabilities"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.McCapabilities:
        from ..data_models.ne import McCapabilities
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return McCapabilities.model_validate(resp)

    def update(self, data: ne.McCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import McCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = McCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = McCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.McCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import McCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = McCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = McCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class DegreeItemNode(ItemNode):
    """Navigator for list item degree"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DegreeItem:
        from ..data_models.ne import DegreeItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DegreeItem.model_validate(resp)

    def update(self, data: ne.DegreeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DegreeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DegreeItem.model_validate(data)
        elif isinstance(data, str):
            data = DegreeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DegreeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DegreeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DegreeItem.model_validate(data)
        elif isinstance(data, str):
            data = DegreeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def modules(self) -> ModulesListNode:
        return ModulesListNode(self._client, f"{self._path}/modules", "modules", ModulesItemNode)
    @property
    def connection_ports(self) -> ConnectionPortsListNode:
        return ConnectionPortsListNode(self._client, f"{self._path}/connection-ports", "connection-ports", ConnectionPortsItemNode)
    @property
    def associated_otdr_port(self) -> AssociatedOtdrPortNode:
        return AssociatedOtdrPortNode(self._client, f"{self._path}/associated-otdr-port", "associated-otdr-port")
    @property
    def mc_capabilities(self) -> McCapabilitiesNode:
        return McCapabilitiesNode(self._client, f"{self._path}/mc-capabilities", "mc-capabilities")

class DegreeListNode(ListNode[DegreeItemNode]):
    """Navigator for list degree"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DegreeItem]:
        from ..data_models.ne import DegreeItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DegreeItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DegreeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DegreeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SharedRiskGroupItemNode(ItemNode):
    """Navigator for list item shared-risk-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SharedRiskGroupItem:
        from ..data_models.ne import SharedRiskGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SharedRiskGroupItem.model_validate(resp)

    def update(self, data: ne.SharedRiskGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SharedRiskGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SharedRiskGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = SharedRiskGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SharedRiskGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SharedRiskGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SharedRiskGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = SharedRiskGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def modules(self) -> ModulesListNode:
        return ModulesListNode(self._client, f"{self._path}/modules", "modules", ModulesItemNode)
    @property
    def mc_capabilities(self) -> McCapabilitiesNode:
        return McCapabilitiesNode(self._client, f"{self._path}/mc-capabilities", "mc-capabilities")

class SharedRiskGroupListNode(ListNode[SharedRiskGroupItemNode]):
    """Navigator for list shared-risk-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SharedRiskGroupItem]:
        from ..data_models.ne import SharedRiskGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SharedRiskGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SharedRiskGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SharedRiskGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ServicesNode(Node):
    """Navigator for services"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Services:
        from ..data_models.ne import Services
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Services.model_validate(resp)

    def update(self, data: ne.Services | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Services

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Services.model_validate(data)
        elif isinstance(data, str):
            data = Services.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Services | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Services

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Services.model_validate(data)
        elif isinstance(data, str):
            data = Services.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def CRS(self) -> CrsListNode:
        return CrsListNode(self._client, f"{self._path}/CRS", "CRS", CrsItemNode)
    @property
    def fiber_connection(self) -> FiberConnectionListNode:
        return FiberConnectionListNode(self._client, f"{self._path}/fiber-connection", "fiber-connection", FiberConnectionItemNode)
    @property
    def internal_link(self) -> InternalLinkListNode:
        return InternalLinkListNode(self._client, f"{self._path}/internal-link", "internal-link", InternalLinkItemNode)
    @property
    def optical_interfaces(self) -> OpticalInterfacesNode:
        return OpticalInterfacesNode(self._client, f"{self._path}/optical-interfaces", "optical-interfaces")
    @property
    def OCRS(self) -> OcrsListNode:
        return OcrsListNode(self._client, f"{self._path}/OCRS", "OCRS", OcrsItemNode)
    @property
    def degree(self) -> DegreeListNode:
        return DegreeListNode(self._client, f"{self._path}/degree", "degree", DegreeItemNode)
    @property
    def shared_risk_group(self) -> SharedRiskGroupListNode:
        return SharedRiskGroupListNode(self._client, f"{self._path}/shared-risk-group", "shared-risk-group", SharedRiskGroupItemNode)

class AlarmProfileEntryItemNode(ItemNode):
    """Navigator for list item alarm-profile-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AlarmProfileEntryItem:
        from ..data_models.ne import AlarmProfileEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmProfileEntryItem.model_validate(resp)

    def update(self, data: ne.AlarmProfileEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AlarmProfileEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmProfileEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmProfileEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AlarmProfileEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AlarmProfileEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmProfileEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmProfileEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AlarmProfileEntryListNode(ListNode[AlarmProfileEntryItemNode]):
    """Navigator for list alarm-profile-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AlarmProfileEntryItem]:
        from ..data_models.ne import AlarmProfileEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AlarmProfileEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AlarmProfileEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AlarmProfileEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AlarmProfileItemNode(ItemNode):
    """Navigator for list item alarm-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AlarmProfileItem:
        from ..data_models.ne import AlarmProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AlarmProfileItem.model_validate(resp)

    def update(self, data: ne.AlarmProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AlarmProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AlarmProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AlarmProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AlarmProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = AlarmProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def alarm_profile_entry(self) -> AlarmProfileEntryListNode:
        return AlarmProfileEntryListNode(self._client, f"{self._path}/alarm-profile-entry", "alarm-profile-entry", AlarmProfileEntryItemNode)

class AlarmProfileListNode(ListNode[AlarmProfileItemNode]):
    """Navigator for list alarm-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AlarmProfileItem]:
        from ..data_models.ne import AlarmProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AlarmProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AlarmProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AlarmProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class StandingConditionItemNode(ItemNode):
    """Navigator for list item standing-condition"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.StandingConditionItem:
        from ..data_models.ne import StandingConditionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return StandingConditionItem.model_validate(resp)

    def update(self, data: ne.StandingConditionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import StandingConditionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StandingConditionItem.model_validate(data)
        elif isinstance(data, str):
            data = StandingConditionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.StandingConditionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import StandingConditionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StandingConditionItem.model_validate(data)
        elif isinstance(data, str):
            data = StandingConditionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class StandingConditionListNode(ListNode[StandingConditionItemNode]):
    """Navigator for list standing-condition"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.StandingConditionItem]:
        from ..data_models.ne import StandingConditionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [StandingConditionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.StandingConditionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.StandingConditionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class FaultNode(Node):
    """Navigator for fault"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Fault:
        from ..data_models.ne import Fault
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Fault.model_validate(resp)

    def update(self, data: ne.Fault | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fault

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fault.model_validate(data)
        elif isinstance(data, str):
            data = Fault.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Fault | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Fault

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fault.model_validate(data)
        elif isinstance(data, str):
            data = Fault.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def alarm_profile(self) -> AlarmProfileListNode:
        return AlarmProfileListNode(self._client, f"{self._path}/alarm-profile", "alarm-profile", AlarmProfileItemNode)
    @property
    def standing_condition(self) -> StandingConditionListNode:
        return StandingConditionListNode(self._client, f"{self._path}/standing-condition", "standing-condition", StandingConditionItemNode)

class PmThresholdsValueItemNode(ItemNode):
    """Navigator for list item pm-thresholds-value"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PmThresholdsValueItem:
        from ..data_models.ne import PmThresholdsValueItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmThresholdsValueItem.model_validate(resp)

    def update(self, data: ne.PmThresholdsValueItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PmThresholdsValueItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholdsValueItem.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholdsValueItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PmThresholdsValueItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PmThresholdsValueItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholdsValueItem.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholdsValueItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PmThresholdsValueListNode(ListNode[PmThresholdsValueItemNode]):
    """Navigator for list pm-thresholds-value"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PmThresholdsValueItem]:
        from ..data_models.ne import PmThresholdsValueItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmThresholdsValueItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PmThresholdsValueItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PmThresholdsValueItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PmThresholdsNode(Node):
    """Navigator for pm-thresholds"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PmThresholds:
        from ..data_models.ne import PmThresholds
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmThresholds.model_validate(resp)

    def update(self, data: ne.PmThresholds | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PmThresholds

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholds.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholds.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PmThresholds | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PmThresholds

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmThresholds.model_validate(data)
        elif isinstance(data, str):
            data = PmThresholds.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pm_thresholds_value(self) -> PmThresholdsValueListNode:
        return PmThresholdsValueListNode(self._client, f"{self._path}/pm-thresholds-value", "pm-thresholds-value", PmThresholdsValueItemNode)

class PmPointItemNode(ItemNode):
    """Navigator for list item pm-point"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PmPointItem:
        from ..data_models.ne import PmPointItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PmPointItem.model_validate(resp)

    def update(self, data: ne.PmPointItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PmPointItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmPointItem.model_validate(data)
        elif isinstance(data, str):
            data = PmPointItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PmPointItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PmPointItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PmPointItem.model_validate(data)
        elif isinstance(data, str):
            data = PmPointItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def pm_thresholds(self) -> PmThresholdsNode:
        return PmThresholdsNode(self._client, f"{self._path}/pm-thresholds", "pm-thresholds")

class PmPointListNode(ListNode[PmPointItemNode]):
    """Navigator for list pm-point"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PmPointItem]:
        from ..data_models.ne import PmPointItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PmPointItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PmPointItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PmPointItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PerformanceNode(Node):
    """Navigator for performance"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Performance:
        from ..data_models.ne import Performance
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Performance.model_validate(resp)

    def update(self, data: ne.Performance | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Performance

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Performance.model_validate(data)
        elif isinstance(data, str):
            data = Performance.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Performance | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Performance

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Performance.model_validate(data)
        elif isinstance(data, str):
            data = Performance.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pm_point(self) -> PmPointListNode:
        return PmPointListNode(self._client, f"{self._path}/pm-point", "pm-point", PmPointItemNode)

class ShelfPowerConsumptionItemNode(ItemNode):
    """Navigator for list item shelf-power-consumption"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ShelfPowerConsumptionItem:
        from ..data_models.ne import ShelfPowerConsumptionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ShelfPowerConsumptionItem.model_validate(resp)

    def update(self, data: ne.ShelfPowerConsumptionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ShelfPowerConsumptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ShelfPowerConsumptionItem.model_validate(data)
        elif isinstance(data, str):
            data = ShelfPowerConsumptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ShelfPowerConsumptionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ShelfPowerConsumptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ShelfPowerConsumptionItem.model_validate(data)
        elif isinstance(data, str):
            data = ShelfPowerConsumptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ShelfPowerConsumptionListNode(ListNode[ShelfPowerConsumptionItemNode]):
    """Navigator for list shelf-power-consumption"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ShelfPowerConsumptionItem]:
        from ..data_models.ne import ShelfPowerConsumptionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ShelfPowerConsumptionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ShelfPowerConsumptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ShelfPowerConsumptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PowerConsumptionNode(Node):
    """Navigator for power-consumption"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PowerConsumption:
        from ..data_models.ne import PowerConsumption
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PowerConsumption.model_validate(resp)

    def update(self, data: ne.PowerConsumption | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PowerConsumption

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PowerConsumption.model_validate(data)
        elif isinstance(data, str):
            data = PowerConsumption.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PowerConsumption | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PowerConsumption

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PowerConsumption.model_validate(data)
        elif isinstance(data, str):
            data = PowerConsumption.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def shelf_power_consumption(self) -> ShelfPowerConsumptionListNode:
        return ShelfPowerConsumptionListNode(self._client, f"{self._path}/shelf-power-consumption", "shelf-power-consumption", ShelfPowerConsumptionItemNode)

class L2DcnNode(Node):
    """Navigator for l2-dcn"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.L2Dcn:
        from ..data_models.ne import L2Dcn
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return L2Dcn.model_validate(resp)

    def update(self, data: ne.L2Dcn | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import L2Dcn

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = L2Dcn.model_validate(data)
        elif isinstance(data, str):
            data = L2Dcn.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.L2Dcn | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import L2Dcn

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = L2Dcn.model_validate(data)
        elif isinstance(data, str):
            data = L2Dcn.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class EthernetNode(Node):
    """Navigator for ethernet"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ethernet:
        from ..data_models.ne import Ethernet
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ethernet.model_validate(resp)

    def update(self, data: ne.Ethernet | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ethernet

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ethernet.model_validate(data)
        elif isinstance(data, str):
            data = Ethernet.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ethernet | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ethernet

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ethernet.model_validate(data)
        elif isinstance(data, str):
            data = Ethernet.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class PppNode(Node):
    """Navigator for ppp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ppp:
        from ..data_models.ne import Ppp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ppp.model_validate(resp)

    def update(self, data: ne.Ppp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ppp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ppp.model_validate(data)
        elif isinstance(data, str):
            data = Ppp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ppp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ppp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ppp.model_validate(data)
        elif isinstance(data, str):
            data = Ppp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class IpAddressNode(Node):
    """Navigator for ip-address"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.IpAddress:
        from ..data_models.ne import IpAddress
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpAddress.model_validate(resp)

    def update(self, data: ne.IpAddress | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpAddress

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpAddress.model_validate(data)
        elif isinstance(data, str):
            data = IpAddress.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.IpAddress | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpAddress

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpAddress.model_validate(data)
        elif isinstance(data, str):
            data = IpAddress.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class IpUnnumberedNode(Node):
    """Navigator for ip-unnumbered"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.IpUnnumbered:
        from ..data_models.ne import IpUnnumbered
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpUnnumbered.model_validate(resp)

    def update(self, data: ne.IpUnnumbered | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpUnnumbered

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpUnnumbered.model_validate(data)
        elif isinstance(data, str):
            data = IpUnnumbered.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.IpUnnumbered | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpUnnumbered

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpUnnumbered.model_validate(data)
        elif isinstance(data, str):
            data = IpUnnumbered.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class Ipv4Node(Node):
    """Navigator for ipv4"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ipv4:
        from ..data_models.ne import Ipv4
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv4.model_validate(resp)

    def update(self, data: ne.Ipv4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipv4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ipv4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipv4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ip_address(self) -> IpAddressNode:
        return IpAddressNode(self._client, f"{self._path}/ip-address", "ip-address")
    @property
    def ip_unnumbered(self) -> IpUnnumberedNode:
        return IpUnnumberedNode(self._client, f"{self._path}/ip-unnumbered", "ip-unnumbered")

class Ipv6AddressItemNode(ItemNode):
    """Navigator for list item ipv6-address"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ipv6AddressItem:
        from ..data_models.ne import Ipv6AddressItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv6AddressItem.model_validate(resp)

    def update(self, data: ne.Ipv6AddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipv6AddressItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6AddressItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6AddressItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.Ipv6AddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipv6AddressItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6AddressItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6AddressItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Ipv6AddressListNode(ListNode[Ipv6AddressItemNode]):
    """Navigator for list ipv6-address"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.Ipv6AddressItem]:
        from ..data_models.ne import Ipv6AddressItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv6AddressItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.Ipv6AddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.Ipv6AddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class Ipv6Node(Node):
    """Navigator for ipv6"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ipv6:
        from ..data_models.ne import Ipv6
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv6.model_validate(resp)

    def update(self, data: ne.Ipv6 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipv6

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ipv6 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipv6

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ipv6_address(self) -> Ipv6AddressListNode:
        return Ipv6AddressListNode(self._client, f"{self._path}/ipv6-address", "ipv6-address", Ipv6AddressItemNode)

class OscxNode(Node):
    """Navigator for oscx"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Oscx:
        from ..data_models.ne import Oscx
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Oscx.model_validate(resp)

    def update(self, data: ne.Oscx | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Oscx

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Oscx.model_validate(data)
        elif isinstance(data, str):
            data = Oscx.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Oscx | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Oscx

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Oscx.model_validate(data)
        elif isinstance(data, str):
            data = Oscx.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class InterfaceItemNode(ItemNode):
    """Navigator for list item interface"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.InterfaceItem:
        from ..data_models.ne import InterfaceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InterfaceItem.model_validate(resp)

    def update(self, data: ne.InterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InterfaceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InterfaceItem.model_validate(data)
        elif isinstance(data, str):
            data = InterfaceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.InterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import InterfaceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InterfaceItem.model_validate(data)
        elif isinstance(data, str):
            data = InterfaceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ethernet(self) -> EthernetNode:
        return EthernetNode(self._client, f"{self._path}/ethernet", "ethernet")
    @property
    def ppp(self) -> PppNode:
        return PppNode(self._client, f"{self._path}/ppp", "ppp")
    @property
    def ipv4(self) -> Ipv4Node:
        return Ipv4Node(self._client, f"{self._path}/ipv4", "ipv4")
    @property
    def ipv6(self) -> Ipv6Node:
        return Ipv6Node(self._client, f"{self._path}/ipv6", "ipv6")
    @property
    def oscx(self) -> OscxNode:
        return OscxNode(self._client, f"{self._path}/oscx", "oscx")

class InterfaceListNode(ListNode[InterfaceItemNode]):
    """Navigator for list interface"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.InterfaceItem]:
        from ..data_models.ne import InterfaceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InterfaceItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.InterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.InterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class NextHopItemNode(ItemNode):
    """Navigator for list item next-hop"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NextHopItem:
        from ..data_models.ne import NextHopItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NextHopItem.model_validate(resp)

    def update(self, data: ne.NextHopItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NextHopItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NextHopItem.model_validate(data)
        elif isinstance(data, str):
            data = NextHopItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.NextHopItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NextHopItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NextHopItem.model_validate(data)
        elif isinstance(data, str):
            data = NextHopItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NextHopListNode(ListNode[NextHopItemNode]):
    """Navigator for list next-hop"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.NextHopItem]:
        from ..data_models.ne import NextHopItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NextHopItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.NextHopItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.NextHopItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class StaticRouteItemNode(ItemNode):
    """Navigator for list item static-route"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.StaticRouteItem:
        from ..data_models.ne import StaticRouteItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return StaticRouteItem.model_validate(resp)

    def update(self, data: ne.StaticRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import StaticRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StaticRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = StaticRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.StaticRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import StaticRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StaticRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = StaticRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def next_hop(self) -> NextHopListNode:
        return NextHopListNode(self._client, f"{self._path}/next-hop", "next-hop", NextHopItemNode)

class StaticRouteListNode(ListNode[StaticRouteItemNode]):
    """Navigator for list static-route"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.StaticRouteItem]:
        from ..data_models.ne import StaticRouteItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [StaticRouteItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.StaticRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.StaticRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OspfAdjacencyItemNode(ItemNode):
    """Navigator for list item ospf-adjacency"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OspfAdjacencyItem:
        from ..data_models.ne import OspfAdjacencyItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfAdjacencyItem.model_validate(resp)

    def update(self, data: ne.OspfAdjacencyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfAdjacencyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfAdjacencyItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfAdjacencyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OspfAdjacencyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfAdjacencyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfAdjacencyItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfAdjacencyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OspfAdjacencyListNode(ListNode[OspfAdjacencyItemNode]):
    """Navigator for list ospf-adjacency"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OspfAdjacencyItem]:
        from ..data_models.ne import OspfAdjacencyItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfAdjacencyItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OspfAdjacencyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OspfAdjacencyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OspfInterfaceItemNode(ItemNode):
    """Navigator for list item ospf-interface"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OspfInterfaceItem:
        from ..data_models.ne import OspfInterfaceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfInterfaceItem.model_validate(resp)

    def update(self, data: ne.OspfInterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfInterfaceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfInterfaceItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfInterfaceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OspfInterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfInterfaceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfInterfaceItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfInterfaceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ospf_adjacency(self) -> OspfAdjacencyListNode:
        return OspfAdjacencyListNode(self._client, f"{self._path}/ospf-adjacency", "ospf-adjacency", OspfAdjacencyItemNode)

class OspfInterfaceListNode(ListNode[OspfInterfaceItemNode]):
    """Navigator for list ospf-interface"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OspfInterfaceItem]:
        from ..data_models.ne import OspfInterfaceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfInterfaceItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OspfInterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OspfInterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OspfAreaItemNode(ItemNode):
    """Navigator for list item ospf-area"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OspfAreaItem:
        from ..data_models.ne import OspfAreaItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfAreaItem.model_validate(resp)

    def update(self, data: ne.OspfAreaItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfAreaItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfAreaItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfAreaItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OspfAreaItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfAreaItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfAreaItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfAreaItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ospf_interface(self) -> OspfInterfaceListNode:
        return OspfInterfaceListNode(self._client, f"{self._path}/ospf-interface", "ospf-interface", OspfInterfaceItemNode)

class OspfAreaListNode(ListNode[OspfAreaItemNode]):
    """Navigator for list ospf-area"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OspfAreaItem]:
        from ..data_models.ne import OspfAreaItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfAreaItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OspfAreaItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OspfAreaItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OspfNode(Node):
    """Navigator for ospf"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ospf:
        from ..data_models.ne import Ospf
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ospf.model_validate(resp)

    def update(self, data: ne.Ospf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ospf

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ospf.model_validate(data)
        elif isinstance(data, str):
            data = Ospf.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ospf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ospf

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ospf.model_validate(data)
        elif isinstance(data, str):
            data = Ospf.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ospf_area(self) -> OspfAreaListNode:
        return OspfAreaListNode(self._client, f"{self._path}/ospf-area", "ospf-area", OspfAreaItemNode)

class BgpNeighborTimersNode(Node):
    """Navigator for bgp-neighbor-timers"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.BgpNeighborTimers:
        from ..data_models.ne import BgpNeighborTimers
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BgpNeighborTimers.model_validate(resp)

    def update(self, data: ne.BgpNeighborTimers | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BgpNeighborTimers

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNeighborTimers.model_validate(data)
        elif isinstance(data, str):
            data = BgpNeighborTimers.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.BgpNeighborTimers | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BgpNeighborTimers

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNeighborTimers.model_validate(data)
        elif isinstance(data, str):
            data = BgpNeighborTimers.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class BgpNeighborTransportNode(Node):
    """Navigator for bgp-neighbor-transport"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.BgpNeighborTransport:
        from ..data_models.ne import BgpNeighborTransport
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BgpNeighborTransport.model_validate(resp)

    def update(self, data: ne.BgpNeighborTransport | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BgpNeighborTransport

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNeighborTransport.model_validate(data)
        elif isinstance(data, str):
            data = BgpNeighborTransport.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.BgpNeighborTransport | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BgpNeighborTransport

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNeighborTransport.model_validate(data)
        elif isinstance(data, str):
            data = BgpNeighborTransport.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class BgpNeighborItemNode(ItemNode):
    """Navigator for list item bgp-neighbor"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.BgpNeighborItem:
        from ..data_models.ne import BgpNeighborItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BgpNeighborItem.model_validate(resp)

    def update(self, data: ne.BgpNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BgpNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = BgpNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.BgpNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import BgpNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = BgpNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def bgp_neighbor_timers(self) -> BgpNeighborTimersNode:
        return BgpNeighborTimersNode(self._client, f"{self._path}/bgp-neighbor-timers", "bgp-neighbor-timers")
    @property
    def bgp_neighbor_transport(self) -> BgpNeighborTransportNode:
        return BgpNeighborTransportNode(self._client, f"{self._path}/bgp-neighbor-transport", "bgp-neighbor-transport")

class BgpNeighborListNode(ListNode[BgpNeighborItemNode]):
    """Navigator for list bgp-neighbor"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.BgpNeighborItem]:
        from ..data_models.ne import BgpNeighborItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [BgpNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.BgpNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.BgpNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class BgpNode(Node):
    """Navigator for bgp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Bgp:
        from ..data_models.ne import Bgp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Bgp.model_validate(resp)

    def update(self, data: ne.Bgp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Bgp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Bgp.model_validate(data)
        elif isinstance(data, str):
            data = Bgp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Bgp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Bgp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Bgp.model_validate(data)
        elif isinstance(data, str):
            data = Bgp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def bgp_neighbor(self) -> BgpNeighborListNode:
        return BgpNeighborListNode(self._client, f"{self._path}/bgp-neighbor", "bgp-neighbor", BgpNeighborItemNode)

class RoutingProtocolItemNode(ItemNode):
    """Navigator for list item routing-protocol"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RoutingProtocolItem:
        from ..data_models.ne import RoutingProtocolItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RoutingProtocolItem.model_validate(resp)

    def update(self, data: ne.RoutingProtocolItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RoutingProtocolItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RoutingProtocolItem.model_validate(data)
        elif isinstance(data, str):
            data = RoutingProtocolItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RoutingProtocolItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RoutingProtocolItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RoutingProtocolItem.model_validate(data)
        elif isinstance(data, str):
            data = RoutingProtocolItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def static_route(self) -> StaticRouteListNode:
        return StaticRouteListNode(self._client, f"{self._path}/static-route", "static-route", StaticRouteItemNode)
    @property
    def ospf(self) -> OspfNode:
        return OspfNode(self._client, f"{self._path}/ospf", "ospf")
    @property
    def bgp(self) -> BgpNode:
        return BgpNode(self._client, f"{self._path}/bgp", "bgp")

class RoutingProtocolListNode(ListNode[RoutingProtocolItemNode]):
    """Navigator for list routing-protocol"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RoutingProtocolItem]:
        from ..data_models.ne import RoutingProtocolItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RoutingProtocolItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RoutingProtocolItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RoutingProtocolItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class NextHopNode(Node):
    """Navigator for next-hop"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NextHop:
        from ..data_models.ne import NextHop
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NextHop.model_validate(resp)

    def update(self, data: ne.NextHop | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NextHop

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NextHop.model_validate(data)
        elif isinstance(data, str):
            data = NextHop.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.NextHop | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NextHop

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NextHop.model_validate(data)
        elif isinstance(data, str):
            data = NextHop.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class RouteItemNode(ItemNode):
    """Navigator for list item route"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RouteItem:
        from ..data_models.ne import RouteItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RouteItem.model_validate(resp)

    def update(self, data: ne.RouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RouteItem.model_validate(data)
        elif isinstance(data, str):
            data = RouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RouteItem.model_validate(data)
        elif isinstance(data, str):
            data = RouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def next_hop(self) -> NextHopNode:
        return NextHopNode(self._client, f"{self._path}/next-hop", "next-hop")

class RouteListNode(ListNode[RouteItemNode]):
    """Navigator for list route"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RouteItem]:
        from ..data_models.ne import RouteItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RouteItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class HmoRouteItemNode(ItemNode):
    """Navigator for list item hmo-route"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.HmoRouteItem:
        from ..data_models.ne import HmoRouteItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return HmoRouteItem.model_validate(resp)

    def update(self, data: ne.HmoRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import HmoRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HmoRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = HmoRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.HmoRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import HmoRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HmoRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = HmoRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def next_hop(self) -> NextHopNode:
        return NextHopNode(self._client, f"{self._path}/next-hop", "next-hop")

class HmoRouteListNode(ListNode[HmoRouteItemNode]):
    """Navigator for list hmo-route"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.HmoRouteItem]:
        from ..data_models.ne import HmoRouteItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [HmoRouteItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.HmoRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.HmoRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RibItemNode(ItemNode):
    """Navigator for list item rib"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RibItem:
        from ..data_models.ne import RibItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RibItem.model_validate(resp)

    def update(self, data: ne.RibItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RibItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RibItem.model_validate(data)
        elif isinstance(data, str):
            data = RibItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RibItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RibItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RibItem.model_validate(data)
        elif isinstance(data, str):
            data = RibItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def route(self) -> RouteListNode:
        return RouteListNode(self._client, f"{self._path}/route", "route", RouteItemNode)
    @property
    def hmo_route(self) -> HmoRouteListNode:
        return HmoRouteListNode(self._client, f"{self._path}/hmo-route", "hmo-route", HmoRouteItemNode)

class RibListNode(ListNode[RibItemNode]):
    """Navigator for list rib"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RibItem]:
        from ..data_models.ne import RibItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RibItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RibItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RibItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class NeighborItemNode(ItemNode):
    """Navigator for list item neighbor"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NeighborItem:
        from ..data_models.ne import NeighborItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NeighborItem.model_validate(resp)

    def update(self, data: ne.NeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = NeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.NeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = NeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NeighborListNode(ListNode[NeighborItemNode]):
    """Navigator for list neighbor"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.NeighborItem]:
        from ..data_models.ne import NeighborItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.NeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.NeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class NeighborsItemNode(ItemNode):
    """Navigator for list item neighbors"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NeighborsItem:
        from ..data_models.ne import NeighborsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NeighborsItem.model_validate(resp)

    def update(self, data: ne.NeighborsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NeighborsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NeighborsItem.model_validate(data)
        elif isinstance(data, str):
            data = NeighborsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.NeighborsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NeighborsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NeighborsItem.model_validate(data)
        elif isinstance(data, str):
            data = NeighborsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def neighbor(self) -> NeighborListNode:
        return NeighborListNode(self._client, f"{self._path}/neighbor", "neighbor", NeighborItemNode)

class NeighborsListNode(ListNode[NeighborsItemNode]):
    """Navigator for list neighbors"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.NeighborsItem]:
        from ..data_models.ne import NeighborsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NeighborsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.NeighborsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.NeighborsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RoutingNode(Node):
    """Navigator for routing"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Routing:
        from ..data_models.ne import Routing
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Routing.model_validate(resp)

    def update(self, data: ne.Routing | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Routing

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Routing.model_validate(data)
        elif isinstance(data, str):
            data = Routing.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Routing | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Routing

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Routing.model_validate(data)
        elif isinstance(data, str):
            data = Routing.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def routing_protocol(self) -> RoutingProtocolListNode:
        return RoutingProtocolListNode(self._client, f"{self._path}/routing-protocol", "routing-protocol", RoutingProtocolItemNode)
    @property
    def rib(self) -> RibListNode:
        return RibListNode(self._client, f"{self._path}/rib", "rib", RibItemNode)
    @property
    def neighbors(self) -> NeighborsListNode:
        return NeighborsListNode(self._client, f"{self._path}/neighbors", "neighbors", NeighborsItemNode)

class PppProfileItemNode(ItemNode):
    """Navigator for list item ppp-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PppProfileItem:
        from ..data_models.ne import PppProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PppProfileItem.model_validate(resp)

    def update(self, data: ne.PppProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PppProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PppProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = PppProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PppProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PppProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PppProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = PppProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PppProfileListNode(ListNode[PppProfileItemNode]):
    """Navigator for list ppp-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PppProfileItem]:
        from ..data_models.ne import PppProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PppProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PppProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PppProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class OspfLinkProfileItemNode(ItemNode):
    """Navigator for list item ospf-link-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.OspfLinkProfileItem:
        from ..data_models.ne import OspfLinkProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfLinkProfileItem.model_validate(resp)

    def update(self, data: ne.OspfLinkProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfLinkProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfLinkProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfLinkProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.OspfLinkProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import OspfLinkProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfLinkProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfLinkProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OspfLinkProfileListNode(ListNode[OspfLinkProfileItemNode]):
    """Navigator for list ospf-link-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.OspfLinkProfileItem]:
        from ..data_models.ne import OspfLinkProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfLinkProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.OspfLinkProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.OspfLinkProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ProfilesNode(Node):
    """Navigator for profiles"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Profiles:
        from ..data_models.ne import Profiles
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Profiles.model_validate(resp)

    def update(self, data: ne.Profiles | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Profiles

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Profiles.model_validate(data)
        elif isinstance(data, str):
            data = Profiles.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Profiles | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Profiles

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Profiles.model_validate(data)
        elif isinstance(data, str):
            data = Profiles.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ppp_profile(self) -> PppProfileListNode:
        return PppProfileListNode(self._client, f"{self._path}/ppp-profile", "ppp-profile", PppProfileItemNode)
    @property
    def ospf_link_profile(self) -> OspfLinkProfileListNode:
        return OspfLinkProfileListNode(self._client, f"{self._path}/ospf-link-profile", "ospf-link-profile", OspfLinkProfileItemNode)

class PreSharedNode(Node):
    """Navigator for pre-shared"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PreShared:
        from ..data_models.ne import PreShared
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PreShared.model_validate(resp)

    def update(self, data: ne.PreShared | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PreShared

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PreShared.model_validate(data)
        elif isinstance(data, str):
            data = PreShared.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PreShared | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PreShared

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PreShared.model_validate(data)
        elif isinstance(data, str):
            data = PreShared.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class PeerAuthenticationNode(Node):
    """Navigator for peer-authentication"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PeerAuthentication:
        from ..data_models.ne import PeerAuthentication
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PeerAuthentication.model_validate(resp)

    def update(self, data: ne.PeerAuthentication | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PeerAuthentication

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PeerAuthentication.model_validate(data)
        elif isinstance(data, str):
            data = PeerAuthentication.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PeerAuthentication | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PeerAuthentication

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PeerAuthentication.model_validate(data)
        elif isinstance(data, str):
            data = PeerAuthentication.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pre_shared(self) -> PreSharedNode:
        return PreSharedNode(self._client, f"{self._path}/pre-shared", "pre-shared")

class PadEntryItemNode(ItemNode):
    """Navigator for list item pad-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PadEntryItem:
        from ..data_models.ne import PadEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PadEntryItem.model_validate(resp)

    def update(self, data: ne.PadEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PadEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PadEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = PadEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PadEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PadEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PadEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = PadEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def peer_authentication(self) -> PeerAuthenticationNode:
        return PeerAuthenticationNode(self._client, f"{self._path}/peer-authentication", "peer-authentication")

class PadEntryListNode(ListNode[PadEntryItemNode]):
    """Navigator for list pad-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PadEntryItem]:
        from ..data_models.ne import PadEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PadEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PadEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PadEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PadNode(Node):
    """Navigator for pad"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Pad:
        from ..data_models.ne import Pad
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Pad.model_validate(resp)

    def update(self, data: ne.Pad | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Pad

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Pad.model_validate(data)
        elif isinstance(data, str):
            data = Pad.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Pad | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Pad

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Pad.model_validate(data)
        elif isinstance(data, str):
            data = Pad.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pad_entry(self) -> PadEntryListNode:
        return PadEntryListNode(self._client, f"{self._path}/pad-entry", "pad-entry", PadEntryItemNode)

class IkeSaLifetimeNode(Node):
    """Navigator for ike-sa-lifetime"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.IkeSaLifetime:
        from ..data_models.ne import IkeSaLifetime
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IkeSaLifetime.model_validate(resp)

    def update(self, data: ne.IkeSaLifetime | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IkeSaLifetime

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IkeSaLifetime.model_validate(data)
        elif isinstance(data, str):
            data = IkeSaLifetime.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.IkeSaLifetime | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IkeSaLifetime

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IkeSaLifetime.model_validate(data)
        elif isinstance(data, str):
            data = IkeSaLifetime.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class LocalPortsItemNode(ItemNode):
    """Navigator for list item local-ports"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.LocalPortsItem:
        from ..data_models.ne import LocalPortsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LocalPortsItem.model_validate(resp)

    def update(self, data: ne.LocalPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LocalPortsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LocalPortsItem.model_validate(data)
        elif isinstance(data, str):
            data = LocalPortsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.LocalPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LocalPortsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LocalPortsItem.model_validate(data)
        elif isinstance(data, str):
            data = LocalPortsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LocalPortsListNode(ListNode[LocalPortsItemNode]):
    """Navigator for list local-ports"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.LocalPortsItem]:
        from ..data_models.ne import LocalPortsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LocalPortsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.LocalPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.LocalPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RemotePortsItemNode(ItemNode):
    """Navigator for list item remote-ports"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RemotePortsItem:
        from ..data_models.ne import RemotePortsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RemotePortsItem.model_validate(resp)

    def update(self, data: ne.RemotePortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RemotePortsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RemotePortsItem.model_validate(data)
        elif isinstance(data, str):
            data = RemotePortsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RemotePortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RemotePortsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RemotePortsItem.model_validate(data)
        elif isinstance(data, str):
            data = RemotePortsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RemotePortsListNode(ListNode[RemotePortsItemNode]):
    """Navigator for list remote-ports"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RemotePortsItem]:
        from ..data_models.ne import RemotePortsItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RemotePortsItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RemotePortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RemotePortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class TrafficSelectorNode(Node):
    """Navigator for traffic-selector"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TrafficSelector:
        from ..data_models.ne import TrafficSelector
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TrafficSelector.model_validate(resp)

    def update(self, data: ne.TrafficSelector | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TrafficSelector

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TrafficSelector.model_validate(data)
        elif isinstance(data, str):
            data = TrafficSelector.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.TrafficSelector | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TrafficSelector

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TrafficSelector.model_validate(data)
        elif isinstance(data, str):
            data = TrafficSelector.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def local_ports(self) -> LocalPortsListNode:
        return LocalPortsListNode(self._client, f"{self._path}/local-ports", "local-ports", LocalPortsItemNode)
    @property
    def remote_ports(self) -> RemotePortsListNode:
        return RemotePortsListNode(self._client, f"{self._path}/remote-ports", "remote-ports", RemotePortsItemNode)

class EspAlgorithmsNode(Node):
    """Navigator for esp-algorithms"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.EspAlgorithms:
        from ..data_models.ne import EspAlgorithms
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EspAlgorithms.model_validate(resp)

    def update(self, data: ne.EspAlgorithms | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import EspAlgorithms

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EspAlgorithms.model_validate(data)
        elif isinstance(data, str):
            data = EspAlgorithms.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.EspAlgorithms | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import EspAlgorithms

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EspAlgorithms.model_validate(data)
        elif isinstance(data, str):
            data = EspAlgorithms.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class IpsecSaCfgNode(Node):
    """Navigator for ipsec-sa-cfg"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.IpsecSaCfg:
        from ..data_models.ne import IpsecSaCfg
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpsecSaCfg.model_validate(resp)

    def update(self, data: ne.IpsecSaCfg | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpsecSaCfg

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSaCfg.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSaCfg.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.IpsecSaCfg | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpsecSaCfg

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSaCfg.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSaCfg.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def esp_algorithms(self) -> EspAlgorithmsNode:
        return EspAlgorithmsNode(self._client, f"{self._path}/esp-algorithms", "esp-algorithms")

class ProcessingInfoNode(Node):
    """Navigator for processing-info"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ProcessingInfo:
        from ..data_models.ne import ProcessingInfo
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ProcessingInfo.model_validate(resp)

    def update(self, data: ne.ProcessingInfo | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ProcessingInfo

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ProcessingInfo.model_validate(data)
        elif isinstance(data, str):
            data = ProcessingInfo.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ProcessingInfo | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ProcessingInfo

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ProcessingInfo.model_validate(data)
        elif isinstance(data, str):
            data = ProcessingInfo.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ipsec_sa_cfg(self) -> IpsecSaCfgNode:
        return IpsecSaCfgNode(self._client, f"{self._path}/ipsec-sa-cfg", "ipsec-sa-cfg")

class IpsecPolicyConfigNode(Node):
    """Navigator for ipsec-policy-config"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.IpsecPolicyConfig:
        from ..data_models.ne import IpsecPolicyConfig
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpsecPolicyConfig.model_validate(resp)

    def update(self, data: ne.IpsecPolicyConfig | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpsecPolicyConfig

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecPolicyConfig.model_validate(data)
        elif isinstance(data, str):
            data = IpsecPolicyConfig.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.IpsecPolicyConfig | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IpsecPolicyConfig

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecPolicyConfig.model_validate(data)
        elif isinstance(data, str):
            data = IpsecPolicyConfig.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def traffic_selector(self) -> TrafficSelectorNode:
        return TrafficSelectorNode(self._client, f"{self._path}/traffic-selector", "traffic-selector")
    @property
    def processing_info(self) -> ProcessingInfoNode:
        return ProcessingInfoNode(self._client, f"{self._path}/processing-info", "processing-info")

class SpdEntryItemNode(ItemNode):
    """Navigator for list item spd-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SpdEntryItem:
        from ..data_models.ne import SpdEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SpdEntryItem.model_validate(resp)

    def update(self, data: ne.SpdEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SpdEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpdEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = SpdEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SpdEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SpdEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpdEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = SpdEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ipsec_policy_config(self) -> IpsecPolicyConfigNode:
        return IpsecPolicyConfigNode(self._client, f"{self._path}/ipsec-policy-config", "ipsec-policy-config")

class SpdEntryListNode(ListNode[SpdEntryItemNode]):
    """Navigator for list spd-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SpdEntryItem]:
        from ..data_models.ne import SpdEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SpdEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SpdEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SpdEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SpdNode(Node):
    """Navigator for spd"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Spd:
        from ..data_models.ne import Spd
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Spd.model_validate(resp)

    def update(self, data: ne.Spd | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Spd

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Spd.model_validate(data)
        elif isinstance(data, str):
            data = Spd.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Spd | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Spd

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Spd.model_validate(data)
        elif isinstance(data, str):
            data = Spd.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def spd_entry(self) -> SpdEntryListNode:
        return SpdEntryListNode(self._client, f"{self._path}/spd-entry", "spd-entry", SpdEntryItemNode)

class ChildSaLifetimeNode(Node):
    """Navigator for child-sa-lifetime"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ChildSaLifetime:
        from ..data_models.ne import ChildSaLifetime
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChildSaLifetime.model_validate(resp)

    def update(self, data: ne.ChildSaLifetime | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChildSaLifetime

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChildSaLifetime.model_validate(data)
        elif isinstance(data, str):
            data = ChildSaLifetime.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ChildSaLifetime | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChildSaLifetime

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChildSaLifetime.model_validate(data)
        elif isinstance(data, str):
            data = ChildSaLifetime.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ChildSaInfoNode(Node):
    """Navigator for child-sa-info"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ChildSaInfo:
        from ..data_models.ne import ChildSaInfo
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChildSaInfo.model_validate(resp)

    def update(self, data: ne.ChildSaInfo | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChildSaInfo

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChildSaInfo.model_validate(data)
        elif isinstance(data, str):
            data = ChildSaInfo.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ChildSaInfo | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChildSaInfo

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChildSaInfo.model_validate(data)
        elif isinstance(data, str):
            data = ChildSaInfo.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def child_sa_lifetime(self) -> ChildSaLifetimeNode:
        return ChildSaLifetimeNode(self._client, f"{self._path}/child-sa-lifetime", "child-sa-lifetime")

class IkeStateNode(Node):
    """Navigator for ike-state"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.IkeState:
        from ..data_models.ne import IkeState
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IkeState.model_validate(resp)

    def update(self, data: ne.IkeState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IkeState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IkeState.model_validate(data)
        elif isinstance(data, str):
            data = IkeState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.IkeState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import IkeState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IkeState.model_validate(data)
        elif isinstance(data, str):
            data = IkeState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ConnEntryItemNode(ItemNode):
    """Navigator for list item conn-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ConnEntryItem:
        from ..data_models.ne import ConnEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ConnEntryItem.model_validate(resp)

    def update(self, data: ne.ConnEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ConnEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ConnEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = ConnEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ConnEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ConnEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ConnEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = ConnEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ike_sa_lifetime(self) -> IkeSaLifetimeNode:
        return IkeSaLifetimeNode(self._client, f"{self._path}/ike-sa-lifetime", "ike-sa-lifetime")
    @property
    def spd(self) -> SpdNode:
        return SpdNode(self._client, f"{self._path}/spd", "spd")
    @property
    def child_sa_info(self) -> ChildSaInfoNode:
        return ChildSaInfoNode(self._client, f"{self._path}/child-sa-info", "child-sa-info")
    @property
    def ike_state(self) -> IkeStateNode:
        return IkeStateNode(self._client, f"{self._path}/ike-state", "ike-state")

class ConnEntryListNode(ListNode[ConnEntryItemNode]):
    """Navigator for list conn-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ConnEntryItem]:
        from ..data_models.ne import ConnEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ConnEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ConnEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ConnEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class IpsecNode(Node):
    """Navigator for ipsec"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ipsec:
        from ..data_models.ne import Ipsec
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipsec.model_validate(resp)

    def update(self, data: ne.Ipsec | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipsec

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipsec.model_validate(data)
        elif isinstance(data, str):
            data = Ipsec.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ipsec | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ipsec

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipsec.model_validate(data)
        elif isinstance(data, str):
            data = Ipsec.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def pad(self) -> PadNode:
        return PadNode(self._client, f"{self._path}/pad", "pad")
    @property
    def conn_entry(self) -> ConnEntryListNode:
        return ConnEntryListNode(self._client, f"{self._path}/conn-entry", "conn-entry", ConnEntryItemNode)

class AclIpv4Node(Node):
    """Navigator for acl-ipv4"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclIpv4:
        from ..data_models.ne import AclIpv4
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclIpv4.model_validate(resp)

    def update(self, data: ne.AclIpv4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclIpv4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclIpv4.model_validate(data)
        elif isinstance(data, str):
            data = AclIpv4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AclIpv4 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclIpv4

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclIpv4.model_validate(data)
        elif isinstance(data, str):
            data = AclIpv4.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class AclIpv6Node(Node):
    """Navigator for acl-ipv6"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclIpv6:
        from ..data_models.ne import AclIpv6
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclIpv6.model_validate(resp)

    def update(self, data: ne.AclIpv6 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclIpv6

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclIpv6.model_validate(data)
        elif isinstance(data, str):
            data = AclIpv6.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AclIpv6 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclIpv6

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclIpv6.model_validate(data)
        elif isinstance(data, str):
            data = AclIpv6.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class AclTcpNode(Node):
    """Navigator for acl-tcp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclTcp:
        from ..data_models.ne import AclTcp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclTcp.model_validate(resp)

    def update(self, data: ne.AclTcp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclTcp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclTcp.model_validate(data)
        elif isinstance(data, str):
            data = AclTcp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AclTcp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclTcp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclTcp.model_validate(data)
        elif isinstance(data, str):
            data = AclTcp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class AclUdpNode(Node):
    """Navigator for acl-udp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclUdp:
        from ..data_models.ne import AclUdp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclUdp.model_validate(resp)

    def update(self, data: ne.AclUdp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclUdp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclUdp.model_validate(data)
        elif isinstance(data, str):
            data = AclUdp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AclUdp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclUdp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclUdp.model_validate(data)
        elif isinstance(data, str):
            data = AclUdp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class AclSnmpcommunityNode(Node):
    """Navigator for acl-snmpcommunity"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclSnmpcommunity:
        from ..data_models.ne import AclSnmpcommunity
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclSnmpcommunity.model_validate(resp)

    def update(self, data: ne.AclSnmpcommunity | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclSnmpcommunity

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclSnmpcommunity.model_validate(data)
        elif isinstance(data, str):
            data = AclSnmpcommunity.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AclSnmpcommunity | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclSnmpcommunity

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclSnmpcommunity.model_validate(data)
        elif isinstance(data, str):
            data = AclSnmpcommunity.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class MatchesNode(Node):
    """Navigator for matches"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Matches:
        from ..data_models.ne import Matches
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Matches.model_validate(resp)

    def update(self, data: ne.Matches | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Matches

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Matches.model_validate(data)
        elif isinstance(data, str):
            data = Matches.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Matches | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Matches

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Matches.model_validate(data)
        elif isinstance(data, str):
            data = Matches.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def acl_ipv4(self) -> AclIpv4Node:
        return AclIpv4Node(self._client, f"{self._path}/acl-ipv4", "acl-ipv4")
    @property
    def acl_ipv6(self) -> AclIpv6Node:
        return AclIpv6Node(self._client, f"{self._path}/acl-ipv6", "acl-ipv6")
    @property
    def acl_tcp(self) -> AclTcpNode:
        return AclTcpNode(self._client, f"{self._path}/acl-tcp", "acl-tcp")
    @property
    def acl_udp(self) -> AclUdpNode:
        return AclUdpNode(self._client, f"{self._path}/acl-udp", "acl-udp")
    @property
    def acl_snmpcommunity(self) -> AclSnmpcommunityNode:
        return AclSnmpcommunityNode(self._client, f"{self._path}/acl-snmpcommunity", "acl-snmpcommunity")

class AceItemNode(ItemNode):
    """Navigator for list item ace"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AceItem:
        from ..data_models.ne import AceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AceItem.model_validate(resp)

    def update(self, data: ne.AceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AceItem.model_validate(data)
        elif isinstance(data, str):
            data = AceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AceItem.model_validate(data)
        elif isinstance(data, str):
            data = AceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def matches(self) -> MatchesNode:
        return MatchesNode(self._client, f"{self._path}/matches", "matches")

class AceListNode(ListNode[AceItemNode]):
    """Navigator for list ace"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AceItem]:
        from ..data_models.ne import AceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AceItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AclItemNode(ItemNode):
    """Navigator for list item acl"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclItem:
        from ..data_models.ne import AclItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclItem.model_validate(resp)

    def update(self, data: ne.AclItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclItem.model_validate(data)
        elif isinstance(data, str):
            data = AclItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AclItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclItem.model_validate(data)
        elif isinstance(data, str):
            data = AclItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ace(self) -> AceListNode:
        return AceListNode(self._client, f"{self._path}/ace", "ace", AceItemNode)

class AclListNode(ListNode[AclItemNode]):
    """Navigator for list acl"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AclItem]:
        from ..data_models.ne import AclItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AclItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AclItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AclItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AclSetItemNode(ItemNode):
    """Navigator for list item acl-set"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclSetItem:
        from ..data_models.ne import AclSetItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclSetItem.model_validate(resp)

    def update(self, data: ne.AclSetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclSetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclSetItem.model_validate(data)
        elif isinstance(data, str):
            data = AclSetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AclSetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclSetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclSetItem.model_validate(data)
        elif isinstance(data, str):
            data = AclSetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AclSetListNode(ListNode[AclSetItemNode]):
    """Navigator for list acl-set"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AclSetItem]:
        from ..data_models.ne import AclSetItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AclSetItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AclSetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AclSetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AclLocalServiceItemNode(ItemNode):
    """Navigator for list item acl-local-service"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclLocalServiceItem:
        from ..data_models.ne import AclLocalServiceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclLocalServiceItem.model_validate(resp)

    def update(self, data: ne.AclLocalServiceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclLocalServiceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclLocalServiceItem.model_validate(data)
        elif isinstance(data, str):
            data = AclLocalServiceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AclLocalServiceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclLocalServiceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclLocalServiceItem.model_validate(data)
        elif isinstance(data, str):
            data = AclLocalServiceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def acl_set(self) -> AclSetListNode:
        return AclSetListNode(self._client, f"{self._path}/acl-set", "acl-set", AclSetItemNode)

class AclLocalServiceListNode(ListNode[AclLocalServiceItemNode]):
    """Navigator for list acl-local-service"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AclLocalServiceItem]:
        from ..data_models.ne import AclLocalServiceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AclLocalServiceItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AclLocalServiceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AclLocalServiceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AclAttachmentPointsNode(Node):
    """Navigator for acl-attachment-points"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AclAttachmentPoints:
        from ..data_models.ne import AclAttachmentPoints
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclAttachmentPoints.model_validate(resp)

    def update(self, data: ne.AclAttachmentPoints | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclAttachmentPoints

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclAttachmentPoints.model_validate(data)
        elif isinstance(data, str):
            data = AclAttachmentPoints.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.AclAttachmentPoints | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AclAttachmentPoints

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AclAttachmentPoints.model_validate(data)
        elif isinstance(data, str):
            data = AclAttachmentPoints.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def acl_local_service(self) -> AclLocalServiceListNode:
        return AclLocalServiceListNode(self._client, f"{self._path}/acl-local-service", "acl-local-service", AclLocalServiceItemNode)

class DnsServerItemNode(ItemNode):
    """Navigator for list item dns-server"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DnsServerItem:
        from ..data_models.ne import DnsServerItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DnsServerItem.model_validate(resp)

    def update(self, data: ne.DnsServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DnsServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DnsServerItem.model_validate(data)
        elif isinstance(data, str):
            data = DnsServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DnsServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DnsServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DnsServerItem.model_validate(data)
        elif isinstance(data, str):
            data = DnsServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DnsServerListNode(ListNode[DnsServerItemNode]):
    """Navigator for list dns-server"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DnsServerItem]:
        from ..data_models.ne import DnsServerItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DnsServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DnsServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DnsServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DnsNode(Node):
    """Navigator for dns"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Dns:
        from ..data_models.ne import Dns
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Dns.model_validate(resp)

    def update(self, data: ne.Dns | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Dns

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Dns.model_validate(data)
        elif isinstance(data, str):
            data = Dns.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Dns | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Dns

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Dns.model_validate(data)
        elif isinstance(data, str):
            data = Dns.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def dns_server(self) -> DnsServerListNode:
        return DnsServerListNode(self._client, f"{self._path}/dns-server", "dns-server", DnsServerItemNode)

class NetworkingNode(Node):
    """Navigator for networking"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Networking:
        from ..data_models.ne import Networking
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Networking.model_validate(resp)

    def update(self, data: ne.Networking | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Networking

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Networking.model_validate(data)
        elif isinstance(data, str):
            data = Networking.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Networking | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Networking

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Networking.model_validate(data)
        elif isinstance(data, str):
            data = Networking.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def interface(self) -> InterfaceListNode:
        return InterfaceListNode(self._client, f"{self._path}/interface", "interface", InterfaceItemNode)
    @property
    def routing(self) -> RoutingNode:
        return RoutingNode(self._client, f"{self._path}/routing", "routing")
    @property
    def profiles(self) -> ProfilesNode:
        return ProfilesNode(self._client, f"{self._path}/profiles", "profiles")
    @property
    def ipsec(self) -> IpsecNode:
        return IpsecNode(self._client, f"{self._path}/ipsec", "ipsec")
    @property
    def acl(self) -> AclListNode:
        return AclListNode(self._client, f"{self._path}/acl", "acl", AclItemNode)
    @property
    def acl_attachment_points(self) -> AclAttachmentPointsNode:
        return AclAttachmentPointsNode(self._client, f"{self._path}/acl-attachment-points", "acl-attachment-points")
    @property
    def dns(self) -> DnsNode:
        return DnsNode(self._client, f"{self._path}/dns", "dns")

class AuthorizedKeyItemNode(ItemNode):
    """Navigator for list item authorized-key"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AuthorizedKeyItem:
        from ..data_models.ne import AuthorizedKeyItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AuthorizedKeyItem.model_validate(resp)

    def update(self, data: ne.AuthorizedKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AuthorizedKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AuthorizedKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = AuthorizedKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AuthorizedKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AuthorizedKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AuthorizedKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = AuthorizedKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AuthorizedKeyListNode(ListNode[AuthorizedKeyItemNode]):
    """Navigator for list authorized-key"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AuthorizedKeyItem]:
        from ..data_models.ne import AuthorizedKeyItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AuthorizedKeyItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AuthorizedKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AuthorizedKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class Snmpv3Node(Node):
    """Navigator for snmpv3"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Snmpv3:
        from ..data_models.ne import Snmpv3
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Snmpv3.model_validate(resp)

    def update(self, data: ne.Snmpv3 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Snmpv3

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Snmpv3.model_validate(data)
        elif isinstance(data, str):
            data = Snmpv3.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Snmpv3 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Snmpv3

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Snmpv3.model_validate(data)
        elif isinstance(data, str):
            data = Snmpv3.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class UserItemNode(ItemNode):
    """Navigator for list item user"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.UserItem:
        from ..data_models.ne import UserItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return UserItem.model_validate(resp)

    def update(self, data: ne.UserItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import UserItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UserItem.model_validate(data)
        elif isinstance(data, str):
            data = UserItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.UserItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import UserItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UserItem.model_validate(data)
        elif isinstance(data, str):
            data = UserItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def authorized_key(self) -> AuthorizedKeyListNode:
        return AuthorizedKeyListNode(self._client, f"{self._path}/authorized-key", "authorized-key", AuthorizedKeyItemNode)
    @property
    def snmpv3(self) -> Snmpv3Node:
        return Snmpv3Node(self._client, f"{self._path}/snmpv3", "snmpv3")

class UserListNode(ListNode[UserItemNode]):
    """Navigator for list user"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.UserItem]:
        from ..data_models.ne import UserItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [UserItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.UserItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.UserItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CliConfigNode(Node):
    """Navigator for cli-config"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CliConfig:
        from ..data_models.ne import CliConfig
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CliConfig.model_validate(resp)

    def update(self, data: ne.CliConfig | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CliConfig

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliConfig.model_validate(data)
        elif isinstance(data, str):
            data = CliConfig.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.CliConfig | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CliConfig

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliConfig.model_validate(data)
        elif isinstance(data, str):
            data = CliConfig.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SessionItemNode(ItemNode):
    """Navigator for list item session"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SessionItem:
        from ..data_models.ne import SessionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SessionItem.model_validate(resp)

    def update(self, data: ne.SessionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SessionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SessionItem.model_validate(data)
        elif isinstance(data, str):
            data = SessionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SessionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SessionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SessionItem.model_validate(data)
        elif isinstance(data, str):
            data = SessionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def cli_config(self) -> CliConfigNode:
        return CliConfigNode(self._client, f"{self._path}/cli-config", "cli-config")

class SessionListNode(ListNode[SessionItemNode]):
    """Navigator for list session"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SessionItem]:
        from ..data_models.ne import SessionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SessionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SessionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SessionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class AaaServerItemNode(ItemNode):
    """Navigator for list item aaa-server"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.AaaServerItem:
        from ..data_models.ne import AaaServerItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AaaServerItem.model_validate(resp)

    def update(self, data: ne.AaaServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AaaServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AaaServerItem.model_validate(data)
        elif isinstance(data, str):
            data = AaaServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.AaaServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import AaaServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AaaServerItem.model_validate(data)
        elif isinstance(data, str):
            data = AaaServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AaaServerListNode(ListNode[AaaServerItemNode]):
    """Navigator for list aaa-server"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.AaaServerItem]:
        from ..data_models.ne import AaaServerItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AaaServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.AaaServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.AaaServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class KeySyncSessionItemNode(ItemNode):
    """Navigator for list item key-sync-session"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.KeySyncSessionItem:
        from ..data_models.ne import KeySyncSessionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return KeySyncSessionItem.model_validate(resp)

    def update(self, data: ne.KeySyncSessionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import KeySyncSessionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KeySyncSessionItem.model_validate(data)
        elif isinstance(data, str):
            data = KeySyncSessionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.KeySyncSessionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import KeySyncSessionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KeySyncSessionItem.model_validate(data)
        elif isinstance(data, str):
            data = KeySyncSessionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class KeySyncSessionListNode(ListNode[KeySyncSessionItemNode]):
    """Navigator for list key-sync-session"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.KeySyncSessionItem]:
        from ..data_models.ne import KeySyncSessionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [KeySyncSessionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.KeySyncSessionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.KeySyncSessionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PskMapItemNode(ItemNode):
    """Navigator for list item psk-map"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PskMapItem:
        from ..data_models.ne import PskMapItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PskMapItem.model_validate(resp)

    def update(self, data: ne.PskMapItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PskMapItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PskMapItem.model_validate(data)
        elif isinstance(data, str):
            data = PskMapItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.PskMapItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PskMapItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PskMapItem.model_validate(data)
        elif isinstance(data, str):
            data = PskMapItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PskMapListNode(ListNode[PskMapItemNode]):
    """Navigator for list psk-map"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.PskMapItem]:
        from ..data_models.ne import PskMapItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PskMapItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.PskMapItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.PskMapItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PskMapsNode(Node):
    """Navigator for psk-maps"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PskMaps:
        from ..data_models.ne import PskMaps
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PskMaps.model_validate(resp)

    def update(self, data: ne.PskMaps | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PskMaps

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PskMaps.model_validate(data)
        elif isinstance(data, str):
            data = PskMaps.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PskMaps | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PskMaps

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PskMaps.model_validate(data)
        elif isinstance(data, str):
            data = PskMaps.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def psk_map(self) -> PskMapListNode:
        return PskMapListNode(self._client, f"{self._path}/psk-map", "psk-map", PskMapItemNode)

class CertificateChainItemNode(ItemNode):
    """Navigator for list item certificate-chain"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CertificateChainItem:
        from ..data_models.ne import CertificateChainItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CertificateChainItem.model_validate(resp)

    def update(self, data: ne.CertificateChainItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CertificateChainItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CertificateChainItem.model_validate(data)
        elif isinstance(data, str):
            data = CertificateChainItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.CertificateChainItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CertificateChainItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CertificateChainItem.model_validate(data)
        elif isinstance(data, str):
            data = CertificateChainItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CertificateChainListNode(ListNode[CertificateChainItemNode]):
    """Navigator for list certificate-chain"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.CertificateChainItem]:
        from ..data_models.ne import CertificateChainItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CertificateChainItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.CertificateChainItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.CertificateChainItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CertificateItemNode(ItemNode):
    """Navigator for list item certificate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CertificateItem:
        from ..data_models.ne import CertificateItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CertificateItem.model_validate(resp)

    def update(self, data: ne.CertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = CertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.CertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = CertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def certificate_chain(self) -> CertificateChainListNode:
        return CertificateChainListNode(self._client, f"{self._path}/certificate-chain", "certificate-chain", CertificateChainItemNode)

class CertificateListNode(ListNode[CertificateItemNode]):
    """Navigator for list certificate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.CertificateItem]:
        from ..data_models.ne import CertificateItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CertificateItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.CertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.CertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class KeyItemNode(ItemNode):
    """Navigator for list item key"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.KeyItem:
        from ..data_models.ne import KeyItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return KeyItem.model_validate(resp)

    def update(self, data: ne.KeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import KeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KeyItem.model_validate(data)
        elif isinstance(data, str):
            data = KeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.KeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import KeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KeyItem.model_validate(data)
        elif isinstance(data, str):
            data = KeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def certificate(self) -> CertificateListNode:
        return CertificateListNode(self._client, f"{self._path}/certificate", "certificate", CertificateItemNode)

class KeyListNode(ListNode[KeyItemNode]):
    """Navigator for list key"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.KeyItem]:
        from ..data_models.ne import KeyItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [KeyItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.KeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.KeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class TrustedCertificateItemNode(ItemNode):
    """Navigator for list item trusted-certificate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TrustedCertificateItem:
        from ..data_models.ne import TrustedCertificateItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TrustedCertificateItem.model_validate(resp)

    def update(self, data: ne.TrustedCertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TrustedCertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TrustedCertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = TrustedCertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.TrustedCertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TrustedCertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TrustedCertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = TrustedCertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TrustedCertificateListNode(ListNode[TrustedCertificateItemNode]):
    """Navigator for list trusted-certificate"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.TrustedCertificateItem]:
        from ..data_models.ne import TrustedCertificateItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TrustedCertificateItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.TrustedCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.TrustedCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class TrustedCertificateGroupItemNode(ItemNode):
    """Navigator for list item trusted-certificate-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TrustedCertificateGroupItem:
        from ..data_models.ne import TrustedCertificateGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TrustedCertificateGroupItem.model_validate(resp)

    def update(self, data: ne.TrustedCertificateGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TrustedCertificateGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TrustedCertificateGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = TrustedCertificateGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.TrustedCertificateGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TrustedCertificateGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TrustedCertificateGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = TrustedCertificateGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def trusted_certificate(self) -> TrustedCertificateListNode:
        return TrustedCertificateListNode(self._client, f"{self._path}/trusted-certificate", "trusted-certificate", TrustedCertificateItemNode)

class TrustedCertificateGroupListNode(ListNode[TrustedCertificateGroupItemNode]):
    """Navigator for list trusted-certificate-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.TrustedCertificateGroupItem]:
        from ..data_models.ne import TrustedCertificateGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TrustedCertificateGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.TrustedCertificateGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.TrustedCertificateGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class KeystoreNode(Node):
    """Navigator for keystore"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Keystore:
        from ..data_models.ne import Keystore
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Keystore.model_validate(resp)

    def update(self, data: ne.Keystore | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Keystore

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Keystore.model_validate(data)
        elif isinstance(data, str):
            data = Keystore.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Keystore | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Keystore

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Keystore.model_validate(data)
        elif isinstance(data, str):
            data = Keystore.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def key(self) -> KeyListNode:
        return KeyListNode(self._client, f"{self._path}/key", "key", KeyItemNode)
    @property
    def trusted_certificate_group(self) -> TrustedCertificateGroupListNode:
        return TrustedCertificateGroupListNode(self._client, f"{self._path}/trusted-certificate-group", "trusted-certificate-group", TrustedCertificateGroupItemNode)

class SecurityNode(Node):
    """Navigator for security"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Security:
        from ..data_models.ne import Security
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Security.model_validate(resp)

    def update(self, data: ne.Security | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Security

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Security.model_validate(data)
        elif isinstance(data, str):
            data = Security.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Security | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Security

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Security.model_validate(data)
        elif isinstance(data, str):
            data = Security.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def user(self) -> UserListNode:
        return UserListNode(self._client, f"{self._path}/user", "user", UserItemNode)
    @property
    def session(self) -> SessionListNode:
        return SessionListNode(self._client, f"{self._path}/session", "session", SessionItemNode)
    @property
    def aaa_server(self) -> AaaServerListNode:
        return AaaServerListNode(self._client, f"{self._path}/aaa-server", "aaa-server", AaaServerItemNode)
    @property
    def key_sync_session(self) -> KeySyncSessionListNode:
        return KeySyncSessionListNode(self._client, f"{self._path}/key-sync-session", "key-sync-session", KeySyncSessionItemNode)
    @property
    def psk_maps(self) -> PskMapsNode:
        return PskMapsNode(self._client, f"{self._path}/psk-maps", "psk-maps")
    @property
    def keystore(self) -> KeystoreNode:
        return KeystoreNode(self._client, f"{self._path}/keystore", "keystore")

class DatabaseItemNode(ItemNode):
    """Navigator for list item database"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DatabaseItem:
        from ..data_models.ne import DatabaseItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DatabaseItem.model_validate(resp)

    def update(self, data: ne.DatabaseItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DatabaseItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DatabaseItem.model_validate(data)
        elif isinstance(data, str):
            data = DatabaseItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DatabaseItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DatabaseItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DatabaseItem.model_validate(data)
        elif isinstance(data, str):
            data = DatabaseItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DatabaseListNode(ListNode[DatabaseItemNode]):
    """Navigator for list database"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DatabaseItem]:
        from ..data_models.ne import DatabaseItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DatabaseItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DatabaseItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DatabaseItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class FwVersionMapItemNode(ItemNode):
    """Navigator for list item fw-version-map"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.FwVersionMapItem:
        from ..data_models.ne import FwVersionMapItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FwVersionMapItem.model_validate(resp)

    def update(self, data: ne.FwVersionMapItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FwVersionMapItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FwVersionMapItem.model_validate(data)
        elif isinstance(data, str):
            data = FwVersionMapItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.FwVersionMapItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FwVersionMapItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FwVersionMapItem.model_validate(data)
        elif isinstance(data, str):
            data = FwVersionMapItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FwVersionMapListNode(ListNode[FwVersionMapItemNode]):
    """Navigator for list fw-version-map"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.FwVersionMapItem]:
        from ..data_models.ne import FwVersionMapItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FwVersionMapItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.FwVersionMapItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.FwVersionMapItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SoftwareloadItemNode(ItemNode):
    """Navigator for list item softwareload"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SoftwareloadItem:
        from ..data_models.ne import SoftwareloadItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SoftwareloadItem.model_validate(resp)

    def update(self, data: ne.SoftwareloadItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SoftwareloadItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SoftwareloadItem.model_validate(data)
        elif isinstance(data, str):
            data = SoftwareloadItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SoftwareloadItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SoftwareloadItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SoftwareloadItem.model_validate(data)
        elif isinstance(data, str):
            data = SoftwareloadItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def database(self) -> DatabaseListNode:
        return DatabaseListNode(self._client, f"{self._path}/database", "database", DatabaseItemNode)
    @property
    def fw_version_map(self) -> FwVersionMapListNode:
        return FwVersionMapListNode(self._client, f"{self._path}/fw-version-map", "fw-version-map", FwVersionMapItemNode)

class SoftwareloadListNode(ListNode[SoftwareloadItemNode]):
    """Navigator for list softwareload"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SoftwareloadItem]:
        from ..data_models.ne import SoftwareloadItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SoftwareloadItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SoftwareloadItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SoftwareloadItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CurrentFwVersionItemNode(ItemNode):
    """Navigator for list item current-fw-version"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CurrentFwVersionItem:
        from ..data_models.ne import CurrentFwVersionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentFwVersionItem.model_validate(resp)

    def update(self, data: ne.CurrentFwVersionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CurrentFwVersionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentFwVersionItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentFwVersionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.CurrentFwVersionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CurrentFwVersionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentFwVersionItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentFwVersionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CurrentFwVersionListNode(ListNode[CurrentFwVersionItemNode]):
    """Navigator for list current-fw-version"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.CurrentFwVersionItem]:
        from ..data_models.ne import CurrentFwVersionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CurrentFwVersionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.CurrentFwVersionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.CurrentFwVersionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class ThirdPartyFwItemNode(ItemNode):
    """Navigator for list item third-party-fw"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ThirdPartyFwItem:
        from ..data_models.ne import ThirdPartyFwItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ThirdPartyFwItem.model_validate(resp)

    def update(self, data: ne.ThirdPartyFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ThirdPartyFwItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ThirdPartyFwItem.model_validate(data)
        elif isinstance(data, str):
            data = ThirdPartyFwItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.ThirdPartyFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ThirdPartyFwItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ThirdPartyFwItem.model_validate(data)
        elif isinstance(data, str):
            data = ThirdPartyFwItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ThirdPartyFwListNode(ListNode[ThirdPartyFwItemNode]):
    """Navigator for list third-party-fw"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.ThirdPartyFwItem]:
        from ..data_models.ne import ThirdPartyFwItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ThirdPartyFwItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.ThirdPartyFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.ThirdPartyFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RollbackPointItemNode(ItemNode):
    """Navigator for list item rollback-point"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RollbackPointItem:
        from ..data_models.ne import RollbackPointItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RollbackPointItem.model_validate(resp)

    def update(self, data: ne.RollbackPointItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RollbackPointItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RollbackPointItem.model_validate(data)
        elif isinstance(data, str):
            data = RollbackPointItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RollbackPointItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RollbackPointItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RollbackPointItem.model_validate(data)
        elif isinstance(data, str):
            data = RollbackPointItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RollbackPointListNode(ListNode[RollbackPointItemNode]):
    """Navigator for list rollback-point"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RollbackPointItem]:
        from ..data_models.ne import RollbackPointItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RollbackPointItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RollbackPointItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RollbackPointItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SwManagementNode(Node):
    """Navigator for sw-management"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SwManagement:
        from ..data_models.ne import SwManagement
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwManagement.model_validate(resp)

    def update(self, data: ne.SwManagement | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SwManagement

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwManagement.model_validate(data)
        elif isinstance(data, str):
            data = SwManagement.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SwManagement | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SwManagement

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwManagement.model_validate(data)
        elif isinstance(data, str):
            data = SwManagement.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def softwareload(self) -> SoftwareloadListNode:
        return SoftwareloadListNode(self._client, f"{self._path}/softwareload", "softwareload", SoftwareloadItemNode)
    @property
    def current_fw_version(self) -> CurrentFwVersionListNode:
        return CurrentFwVersionListNode(self._client, f"{self._path}/current-fw-version", "current-fw-version", CurrentFwVersionItemNode)
    @property
    def third_party_fw(self) -> ThirdPartyFwListNode:
        return ThirdPartyFwListNode(self._client, f"{self._path}/third-party-fw", "third-party-fw", ThirdPartyFwItemNode)
    @property
    def rollback_point(self) -> RollbackPointListNode:
        return RollbackPointListNode(self._client, f"{self._path}/rollback-point", "rollback-point", RollbackPointItemNode)

class LogFacilityItemNode(ItemNode):
    """Navigator for list item log-facility"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.LogFacilityItem:
        from ..data_models.ne import LogFacilityItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogFacilityItem.model_validate(resp)

    def update(self, data: ne.LogFacilityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LogFacilityItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogFacilityItem.model_validate(data)
        elif isinstance(data, str):
            data = LogFacilityItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.LogFacilityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LogFacilityItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogFacilityItem.model_validate(data)
        elif isinstance(data, str):
            data = LogFacilityItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LogFacilityListNode(ListNode[LogFacilityItemNode]):
    """Navigator for list log-facility"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.LogFacilityItem]:
        from ..data_models.ne import LogFacilityItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogFacilityItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.LogFacilityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.LogFacilityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class LogForwardingSelectorNode(Node):
    """Navigator for log-forwarding-selector"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.LogForwardingSelector:
        from ..data_models.ne import LogForwardingSelector
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogForwardingSelector.model_validate(resp)

    def update(self, data: ne.LogForwardingSelector | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LogForwardingSelector

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogForwardingSelector.model_validate(data)
        elif isinstance(data, str):
            data = LogForwardingSelector.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.LogForwardingSelector | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LogForwardingSelector

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogForwardingSelector.model_validate(data)
        elif isinstance(data, str):
            data = LogForwardingSelector.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def log_facility(self) -> LogFacilityListNode:
        return LogFacilityListNode(self._client, f"{self._path}/log-facility", "log-facility", LogFacilityItemNode)

class LogServerItemNode(ItemNode):
    """Navigator for list item log-server"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.LogServerItem:
        from ..data_models.ne import LogServerItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogServerItem.model_validate(resp)

    def update(self, data: ne.LogServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LogServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogServerItem.model_validate(data)
        elif isinstance(data, str):
            data = LogServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.LogServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import LogServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogServerItem.model_validate(data)
        elif isinstance(data, str):
            data = LogServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def log_forwarding_selector(self) -> LogForwardingSelectorNode:
        return LogForwardingSelectorNode(self._client, f"{self._path}/log-forwarding-selector", "log-forwarding-selector")

class LogServerListNode(ListNode[LogServerItemNode]):
    """Navigator for list log-server"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.LogServerItem]:
        from ..data_models.ne import LogServerItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.LogServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.LogServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SensorPathItemNode(ItemNode):
    """Navigator for list item sensor-path"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SensorPathItem:
        from ..data_models.ne import SensorPathItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SensorPathItem.model_validate(resp)

    def update(self, data: ne.SensorPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorPathItem.model_validate(data)
        elif isinstance(data, str):
            data = SensorPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SensorPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorPathItem.model_validate(data)
        elif isinstance(data, str):
            data = SensorPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SensorPathListNode(ListNode[SensorPathItemNode]):
    """Navigator for list sensor-path"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SensorPathItem]:
        from ..data_models.ne import SensorPathItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SensorPathItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SensorPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SensorPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SensorPathsNode(Node):
    """Navigator for sensor-paths"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SensorPaths:
        from ..data_models.ne import SensorPaths
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SensorPaths.model_validate(resp)

    def update(self, data: ne.SensorPaths | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorPaths

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorPaths.model_validate(data)
        elif isinstance(data, str):
            data = SensorPaths.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SensorPaths | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorPaths

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorPaths.model_validate(data)
        elif isinstance(data, str):
            data = SensorPaths.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def sensor_path(self) -> SensorPathListNode:
        return SensorPathListNode(self._client, f"{self._path}/sensor-path", "sensor-path", SensorPathItemNode)

class SensorGroupItemNode(ItemNode):
    """Navigator for list item sensor-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SensorGroupItem:
        from ..data_models.ne import SensorGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SensorGroupItem.model_validate(resp)

    def update(self, data: ne.SensorGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = SensorGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SensorGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = SensorGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def sensor_paths(self) -> SensorPathsNode:
        return SensorPathsNode(self._client, f"{self._path}/sensor-paths", "sensor-paths")

class SensorGroupListNode(ListNode[SensorGroupItemNode]):
    """Navigator for list sensor-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SensorGroupItem]:
        from ..data_models.ne import SensorGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SensorGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SensorGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SensorGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SensorGroupsNode(Node):
    """Navigator for sensor-groups"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SensorGroups:
        from ..data_models.ne import SensorGroups
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SensorGroups.model_validate(resp)

    def update(self, data: ne.SensorGroups | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorGroups

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorGroups.model_validate(data)
        elif isinstance(data, str):
            data = SensorGroups.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SensorGroups | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorGroups

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorGroups.model_validate(data)
        elif isinstance(data, str):
            data = SensorGroups.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def sensor_group(self) -> SensorGroupListNode:
        return SensorGroupListNode(self._client, f"{self._path}/sensor-group", "sensor-group", SensorGroupItemNode)

class DestinationItemNode(ItemNode):
    """Navigator for list item destination"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DestinationItem:
        from ..data_models.ne import DestinationItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DestinationItem.model_validate(resp)

    def update(self, data: ne.DestinationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationItem.model_validate(data)
        elif isinstance(data, str):
            data = DestinationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DestinationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationItem.model_validate(data)
        elif isinstance(data, str):
            data = DestinationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DestinationListNode(ListNode[DestinationItemNode]):
    """Navigator for list destination"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DestinationItem]:
        from ..data_models.ne import DestinationItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DestinationItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DestinationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DestinationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DestinationsNode(Node):
    """Navigator for destinations"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Destinations:
        from ..data_models.ne import Destinations
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Destinations.model_validate(resp)

    def update(self, data: ne.Destinations | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Destinations

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Destinations.model_validate(data)
        elif isinstance(data, str):
            data = Destinations.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Destinations | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Destinations

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Destinations.model_validate(data)
        elif isinstance(data, str):
            data = Destinations.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def destination(self) -> DestinationListNode:
        return DestinationListNode(self._client, f"{self._path}/destination", "destination", DestinationItemNode)

class DestinationGroupItemNode(ItemNode):
    """Navigator for list item destination-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DestinationGroupItem:
        from ..data_models.ne import DestinationGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DestinationGroupItem.model_validate(resp)

    def update(self, data: ne.DestinationGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = DestinationGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DestinationGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = DestinationGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def destinations(self) -> DestinationsNode:
        return DestinationsNode(self._client, f"{self._path}/destinations", "destinations")

class DestinationGroupListNode(ListNode[DestinationGroupItemNode]):
    """Navigator for list destination-group"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DestinationGroupItem]:
        from ..data_models.ne import DestinationGroupItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DestinationGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DestinationGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DestinationGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DestinationGroupsNode(Node):
    """Navigator for destination-groups"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DestinationGroups:
        from ..data_models.ne import DestinationGroups
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DestinationGroups.model_validate(resp)

    def update(self, data: ne.DestinationGroups | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationGroups

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationGroups.model_validate(data)
        elif isinstance(data, str):
            data = DestinationGroups.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.DestinationGroups | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationGroups

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationGroups.model_validate(data)
        elif isinstance(data, str):
            data = DestinationGroups.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def destination_group(self) -> DestinationGroupListNode:
        return DestinationGroupListNode(self._client, f"{self._path}/destination-group", "destination-group", DestinationGroupItemNode)

class SensorProfileItemNode(ItemNode):
    """Navigator for list item sensor-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SensorProfileItem:
        from ..data_models.ne import SensorProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SensorProfileItem.model_validate(resp)

    def update(self, data: ne.SensorProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = SensorProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SensorProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = SensorProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SensorProfileListNode(ListNode[SensorProfileItemNode]):
    """Navigator for list sensor-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SensorProfileItem]:
        from ..data_models.ne import SensorProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SensorProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SensorProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SensorProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SensorProfilesNode(Node):
    """Navigator for sensor-profiles"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SensorProfiles:
        from ..data_models.ne import SensorProfiles
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SensorProfiles.model_validate(resp)

    def update(self, data: ne.SensorProfiles | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorProfiles

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorProfiles.model_validate(data)
        elif isinstance(data, str):
            data = SensorProfiles.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SensorProfiles | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SensorProfiles

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SensorProfiles.model_validate(data)
        elif isinstance(data, str):
            data = SensorProfiles.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def sensor_profile(self) -> SensorProfileListNode:
        return SensorProfileListNode(self._client, f"{self._path}/sensor-profile", "sensor-profile", SensorProfileItemNode)

class DestinationProfileItemNode(ItemNode):
    """Navigator for list item destination-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DestinationProfileItem:
        from ..data_models.ne import DestinationProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DestinationProfileItem.model_validate(resp)

    def update(self, data: ne.DestinationProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = DestinationProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DestinationProfileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = DestinationProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DestinationProfileListNode(ListNode[DestinationProfileItemNode]):
    """Navigator for list destination-profile"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DestinationProfileItem]:
        from ..data_models.ne import DestinationProfileItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DestinationProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DestinationProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DestinationProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DestinationProfilesNode(Node):
    """Navigator for destination-profiles"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DestinationProfiles:
        from ..data_models.ne import DestinationProfiles
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DestinationProfiles.model_validate(resp)

    def update(self, data: ne.DestinationProfiles | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationProfiles

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationProfiles.model_validate(data)
        elif isinstance(data, str):
            data = DestinationProfiles.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.DestinationProfiles | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DestinationProfiles

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DestinationProfiles.model_validate(data)
        elif isinstance(data, str):
            data = DestinationProfiles.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def destination_profile(self) -> DestinationProfileListNode:
        return DestinationProfileListNode(self._client, f"{self._path}/destination-profile", "destination-profile", DestinationProfileItemNode)

class DialOutSubscriptionItemNode(ItemNode):
    """Navigator for list item dial-out-subscription"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DialOutSubscriptionItem:
        from ..data_models.ne import DialOutSubscriptionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DialOutSubscriptionItem.model_validate(resp)

    def update(self, data: ne.DialOutSubscriptionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialOutSubscriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialOutSubscriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = DialOutSubscriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DialOutSubscriptionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialOutSubscriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialOutSubscriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = DialOutSubscriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def sensor_profiles(self) -> SensorProfilesNode:
        return SensorProfilesNode(self._client, f"{self._path}/sensor-profiles", "sensor-profiles")
    @property
    def destination_profiles(self) -> DestinationProfilesNode:
        return DestinationProfilesNode(self._client, f"{self._path}/destination-profiles", "destination-profiles")

class DialOutSubscriptionListNode(ListNode[DialOutSubscriptionItemNode]):
    """Navigator for list dial-out-subscription"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DialOutSubscriptionItem]:
        from ..data_models.ne import DialOutSubscriptionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DialOutSubscriptionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DialOutSubscriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DialOutSubscriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class PersistentNode(Node):
    """Navigator for persistent"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Persistent:
        from ..data_models.ne import Persistent
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Persistent.model_validate(resp)

    def update(self, data: ne.Persistent | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Persistent

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Persistent.model_validate(data)
        elif isinstance(data, str):
            data = Persistent.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Persistent | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Persistent

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Persistent.model_validate(data)
        elif isinstance(data, str):
            data = Persistent.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def dial_out_subscription(self) -> DialOutSubscriptionListNode:
        return DialOutSubscriptionListNode(self._client, f"{self._path}/dial-out-subscription", "dial-out-subscription", DialOutSubscriptionItemNode)

class StateDialInSubscriptionNode(Node):
    """Navigator for state-dial-in-subscription"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.StateDialInSubscription:
        from ..data_models.ne import StateDialInSubscription
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return StateDialInSubscription.model_validate(resp)

    def update(self, data: ne.StateDialInSubscription | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import StateDialInSubscription

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StateDialInSubscription.model_validate(data)
        elif isinstance(data, str):
            data = StateDialInSubscription.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.StateDialInSubscription | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import StateDialInSubscription

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StateDialInSubscription.model_validate(data)
        elif isinstance(data, str):
            data = StateDialInSubscription.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class PathStateNode(Node):
    """Navigator for path-state"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.PathState:
        from ..data_models.ne import PathState
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PathState.model_validate(resp)

    def update(self, data: ne.PathState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PathState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PathState.model_validate(data)
        elif isinstance(data, str):
            data = PathState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.PathState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import PathState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PathState.model_validate(data)
        elif isinstance(data, str):
            data = PathState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class DialInSensorPathItemNode(ItemNode):
    """Navigator for list item dial-in-sensor-path"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DialInSensorPathItem:
        from ..data_models.ne import DialInSensorPathItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DialInSensorPathItem.model_validate(resp)

    def update(self, data: ne.DialInSensorPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialInSensorPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialInSensorPathItem.model_validate(data)
        elif isinstance(data, str):
            data = DialInSensorPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DialInSensorPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialInSensorPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialInSensorPathItem.model_validate(data)
        elif isinstance(data, str):
            data = DialInSensorPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def path_state(self) -> PathStateNode:
        return PathStateNode(self._client, f"{self._path}/path-state", "path-state")

class DialInSensorPathListNode(ListNode[DialInSensorPathItemNode]):
    """Navigator for list dial-in-sensor-path"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DialInSensorPathItem]:
        from ..data_models.ne import DialInSensorPathItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DialInSensorPathItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DialInSensorPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DialInSensorPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DialInSensorPathsNode(Node):
    """Navigator for dial-in-sensor-paths"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DialInSensorPaths:
        from ..data_models.ne import DialInSensorPaths
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DialInSensorPaths.model_validate(resp)

    def update(self, data: ne.DialInSensorPaths | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialInSensorPaths

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialInSensorPaths.model_validate(data)
        elif isinstance(data, str):
            data = DialInSensorPaths.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.DialInSensorPaths | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialInSensorPaths

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialInSensorPaths.model_validate(data)
        elif isinstance(data, str):
            data = DialInSensorPaths.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def dial_in_sensor_path(self) -> DialInSensorPathListNode:
        return DialInSensorPathListNode(self._client, f"{self._path}/dial-in-sensor-path", "dial-in-sensor-path", DialInSensorPathItemNode)

class DialInSubscriptionItemNode(ItemNode):
    """Navigator for list item dial-in-subscription"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DialInSubscriptionItem:
        from ..data_models.ne import DialInSubscriptionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DialInSubscriptionItem.model_validate(resp)

    def update(self, data: ne.DialInSubscriptionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialInSubscriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialInSubscriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = DialInSubscriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.DialInSubscriptionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DialInSubscriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialInSubscriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = DialInSubscriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def state_dial_in_subscription(self) -> StateDialInSubscriptionNode:
        return StateDialInSubscriptionNode(self._client, f"{self._path}/state-dial-in-subscription", "state-dial-in-subscription")
    @property
    def dial_in_sensor_paths(self) -> DialInSensorPathsNode:
        return DialInSensorPathsNode(self._client, f"{self._path}/dial-in-sensor-paths", "dial-in-sensor-paths")

class DialInSubscriptionListNode(ListNode[DialInSubscriptionItemNode]):
    """Navigator for list dial-in-subscription"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.DialInSubscriptionItem]:
        from ..data_models.ne import DialInSubscriptionItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DialInSubscriptionItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.DialInSubscriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.DialInSubscriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DynamicNode(Node):
    """Navigator for dynamic"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Dynamic:
        from ..data_models.ne import Dynamic
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Dynamic.model_validate(resp)

    def update(self, data: ne.Dynamic | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Dynamic

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Dynamic.model_validate(data)
        elif isinstance(data, str):
            data = Dynamic.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Dynamic | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Dynamic

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Dynamic.model_validate(data)
        elif isinstance(data, str):
            data = Dynamic.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def dial_in_subscription(self) -> DialInSubscriptionListNode:
        return DialInSubscriptionListNode(self._client, f"{self._path}/dial-in-subscription", "dial-in-subscription", DialInSubscriptionItemNode)

class SubscriptionsNode(Node):
    """Navigator for subscriptions"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Subscriptions:
        from ..data_models.ne import Subscriptions
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Subscriptions.model_validate(resp)

    def update(self, data: ne.Subscriptions | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Subscriptions

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Subscriptions.model_validate(data)
        elif isinstance(data, str):
            data = Subscriptions.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Subscriptions | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Subscriptions

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Subscriptions.model_validate(data)
        elif isinstance(data, str):
            data = Subscriptions.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def persistent(self) -> PersistentNode:
        return PersistentNode(self._client, f"{self._path}/persistent", "persistent")
    @property
    def dynamic(self) -> DynamicNode:
        return DynamicNode(self._client, f"{self._path}/dynamic", "dynamic")

class TelemetrySystemNode(Node):
    """Navigator for telemetry-system"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TelemetrySystem:
        from ..data_models.ne import TelemetrySystem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TelemetrySystem.model_validate(resp)

    def update(self, data: ne.TelemetrySystem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TelemetrySystem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TelemetrySystem.model_validate(data)
        elif isinstance(data, str):
            data = TelemetrySystem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.TelemetrySystem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TelemetrySystem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TelemetrySystem.model_validate(data)
        elif isinstance(data, str):
            data = TelemetrySystem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def sensor_groups(self) -> SensorGroupsNode:
        return SensorGroupsNode(self._client, f"{self._path}/sensor-groups", "sensor-groups")
    @property
    def destination_groups(self) -> DestinationGroupsNode:
        return DestinationGroupsNode(self._client, f"{self._path}/destination-groups", "destination-groups")
    @property
    def subscriptions(self) -> SubscriptionsNode:
        return SubscriptionsNode(self._client, f"{self._path}/subscriptions", "subscriptions")

class FileManagementNode(Node):
    """Navigator for file-management"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.FileManagement:
        from ..data_models.ne import FileManagement
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FileManagement.model_validate(resp)

    def update(self, data: ne.FileManagement | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FileManagement

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileManagement.model_validate(data)
        elif isinstance(data, str):
            data = FileManagement.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.FileManagement | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FileManagement

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileManagement.model_validate(data)
        elif isinstance(data, str):
            data = FileManagement.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def log_server(self) -> LogServerListNode:
        return LogServerListNode(self._client, f"{self._path}/log-server", "log-server", LogServerItemNode)
    @property
    def telemetry_system(self) -> TelemetrySystemNode:
        return TelemetrySystemNode(self._client, f"{self._path}/telemetry-system", "telemetry-system")

class LldpNode(Node):
    """Navigator for lldp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Lldp:
        from ..data_models.ne import Lldp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Lldp.model_validate(resp)

    def update(self, data: ne.Lldp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Lldp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Lldp.model_validate(data)
        elif isinstance(data, str):
            data = Lldp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Lldp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Lldp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Lldp.model_validate(data)
        elif isinstance(data, str):
            data = Lldp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NtpAssociationStatusNode(Node):
    """Navigator for ntp-association-status"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NtpAssociationStatus:
        from ..data_models.ne import NtpAssociationStatus
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NtpAssociationStatus.model_validate(resp)

    def update(self, data: ne.NtpAssociationStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NtpAssociationStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpAssociationStatus.model_validate(data)
        elif isinstance(data, str):
            data = NtpAssociationStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.NtpAssociationStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NtpAssociationStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpAssociationStatus.model_validate(data)
        elif isinstance(data, str):
            data = NtpAssociationStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NtpAssociationItemNode(ItemNode):
    """Navigator for list item ntp-association"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.NtpAssociationItem:
        from ..data_models.ne import NtpAssociationItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NtpAssociationItem.model_validate(resp)

    def update(self, data: ne.NtpAssociationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NtpAssociationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpAssociationItem.model_validate(data)
        elif isinstance(data, str):
            data = NtpAssociationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.NtpAssociationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import NtpAssociationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpAssociationItem.model_validate(data)
        elif isinstance(data, str):
            data = NtpAssociationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ntp_association_status(self) -> NtpAssociationStatusNode:
        return NtpAssociationStatusNode(self._client, f"{self._path}/ntp-association-status", "ntp-association-status")

class NtpAssociationListNode(ListNode[NtpAssociationItemNode]):
    """Navigator for list ntp-association"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.NtpAssociationItem]:
        from ..data_models.ne import NtpAssociationItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NtpAssociationItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.NtpAssociationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.NtpAssociationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class NtpNode(Node):
    """Navigator for ntp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ntp:
        from ..data_models.ne import Ntp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ntp.model_validate(resp)

    def update(self, data: ne.Ntp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ntp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ntp.model_validate(data)
        elif isinstance(data, str):
            data = Ntp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ntp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ntp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ntp.model_validate(data)
        elif isinstance(data, str):
            data = Ntp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ntp_association(self) -> NtpAssociationListNode:
        return NtpAssociationListNode(self._client, f"{self._path}/ntp-association", "ntp-association", NtpAssociationItemNode)

class TimeManagerNode(Node):
    """Navigator for time-manager"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.TimeManager:
        from ..data_models.ne import TimeManager
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TimeManager.model_validate(resp)

    def update(self, data: ne.TimeManager | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TimeManager

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TimeManager.model_validate(data)
        elif isinstance(data, str):
            data = TimeManager.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.TimeManager | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import TimeManager

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TimeManager.model_validate(data)
        elif isinstance(data, str):
            data = TimeManager.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ntp(self) -> NtpNode:
        return NtpNode(self._client, f"{self._path}/ntp", "ntp")

class ZtcNode(Node):
    """Navigator for ztc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ztc:
        from ..data_models.ne import Ztc
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ztc.model_validate(resp)

    def update(self, data: ne.Ztc | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ztc

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ztc.model_validate(data)
        elif isinstance(data, str):
            data = Ztc.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ztc | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ztc

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ztc.model_validate(data)
        elif isinstance(data, str):
            data = Ztc.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ConsoleNode(Node):
    """Navigator for console"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Console:
        from ..data_models.ne import Console
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Console.model_validate(resp)

    def update(self, data: ne.Console | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Console

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Console.model_validate(data)
        elif isinstance(data, str):
            data = Console.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Console | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Console

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Console.model_validate(data)
        elif isinstance(data, str):
            data = Console.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SshNode(Node):
    """Navigator for ssh"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ssh:
        from ..data_models.ne import Ssh
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ssh.model_validate(resp)

    def update(self, data: ne.Ssh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ssh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ssh.model_validate(data)
        elif isinstance(data, str):
            data = Ssh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ssh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ssh

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ssh.model_validate(data)
        elif isinstance(data, str):
            data = Ssh.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SnmpCommunityItemNode(ItemNode):
    """Navigator for list item snmp-community"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SnmpCommunityItem:
        from ..data_models.ne import SnmpCommunityItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SnmpCommunityItem.model_validate(resp)

    def update(self, data: ne.SnmpCommunityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SnmpCommunityItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SnmpCommunityItem.model_validate(data)
        elif isinstance(data, str):
            data = SnmpCommunityItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SnmpCommunityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SnmpCommunityItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SnmpCommunityItem.model_validate(data)
        elif isinstance(data, str):
            data = SnmpCommunityItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SnmpCommunityListNode(ListNode[SnmpCommunityItemNode]):
    """Navigator for list snmp-community"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SnmpCommunityItem]:
        from ..data_models.ne import SnmpCommunityItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SnmpCommunityItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SnmpCommunityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SnmpCommunityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SnmpTargetItemNode(ItemNode):
    """Navigator for list item snmp-target"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SnmpTargetItem:
        from ..data_models.ne import SnmpTargetItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SnmpTargetItem.model_validate(resp)

    def update(self, data: ne.SnmpTargetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SnmpTargetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SnmpTargetItem.model_validate(data)
        elif isinstance(data, str):
            data = SnmpTargetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.SnmpTargetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SnmpTargetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SnmpTargetItem.model_validate(data)
        elif isinstance(data, str):
            data = SnmpTargetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SnmpTargetListNode(ListNode[SnmpTargetItemNode]):
    """Navigator for list snmp-target"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.SnmpTargetItem]:
        from ..data_models.ne import SnmpTargetItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SnmpTargetItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.SnmpTargetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.SnmpTargetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SnmpNode(Node):
    """Navigator for snmp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Snmp:
        from ..data_models.ne import Snmp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Snmp.model_validate(resp)

    def update(self, data: ne.Snmp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Snmp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Snmp.model_validate(data)
        elif isinstance(data, str):
            data = Snmp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Snmp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Snmp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Snmp.model_validate(data)
        elif isinstance(data, str):
            data = Snmp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def snmp_community(self) -> SnmpCommunityListNode:
        return SnmpCommunityListNode(self._client, f"{self._path}/snmp-community", "snmp-community", SnmpCommunityItemNode)
    @property
    def snmp_target(self) -> SnmpTargetListNode:
        return SnmpTargetListNode(self._client, f"{self._path}/snmp-target", "snmp-target", SnmpTargetItemNode)

class RestconfNode(Node):
    """Navigator for restconf"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Restconf:
        from ..data_models.ne import Restconf
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Restconf.model_validate(resp)

    def update(self, data: ne.Restconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Restconf

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Restconf.model_validate(data)
        elif isinstance(data, str):
            data = Restconf.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Restconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Restconf

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Restconf.model_validate(data)
        elif isinstance(data, str):
            data = Restconf.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class CliAliasItemNode(ItemNode):
    """Navigator for list item cli-alias"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CliAliasItem:
        from ..data_models.ne import CliAliasItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CliAliasItem.model_validate(resp)

    def update(self, data: ne.CliAliasItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CliAliasItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliAliasItem.model_validate(data)
        elif isinstance(data, str):
            data = CliAliasItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.CliAliasItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CliAliasItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliAliasItem.model_validate(data)
        elif isinstance(data, str):
            data = CliAliasItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CliAliasListNode(ListNode[CliAliasItemNode]):
    """Navigator for list cli-alias"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.CliAliasItem]:
        from ..data_models.ne import CliAliasItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CliAliasItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.CliAliasItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.CliAliasItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CliScriptItemNode(ItemNode):
    """Navigator for list item cli-script"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.CliScriptItem:
        from ..data_models.ne import CliScriptItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CliScriptItem.model_validate(resp)

    def update(self, data: ne.CliScriptItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CliScriptItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliScriptItem.model_validate(data)
        elif isinstance(data, str):
            data = CliScriptItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.CliScriptItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import CliScriptItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliScriptItem.model_validate(data)
        elif isinstance(data, str):
            data = CliScriptItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CliScriptListNode(ListNode[CliScriptItemNode]):
    """Navigator for list cli-script"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.CliScriptItem]:
        from ..data_models.ne import CliScriptItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CliScriptItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.CliScriptItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.CliScriptItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CliNode(Node):
    """Navigator for cli"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Cli:
        from ..data_models.ne import Cli
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Cli.model_validate(resp)

    def update(self, data: ne.Cli | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Cli

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Cli.model_validate(data)
        elif isinstance(data, str):
            data = Cli.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Cli | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Cli

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Cli.model_validate(data)
        elif isinstance(data, str):
            data = Cli.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def cli_alias(self) -> CliAliasListNode:
        return CliAliasListNode(self._client, f"{self._path}/cli-alias", "cli-alias", CliAliasItemNode)
    @property
    def cli_script(self) -> CliScriptListNode:
        return CliScriptListNode(self._client, f"{self._path}/cli-script", "cli-script", CliScriptItemNode)

class NetconfNode(Node):
    """Navigator for netconf"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Netconf:
        from ..data_models.ne import Netconf
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Netconf.model_validate(resp)

    def update(self, data: ne.Netconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Netconf

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Netconf.model_validate(data)
        elif isinstance(data, str):
            data = Netconf.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Netconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Netconf

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Netconf.model_validate(data)
        elif isinstance(data, str):
            data = Netconf.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class GrpcNode(Node):
    """Navigator for grpc"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Grpc:
        from ..data_models.ne import Grpc
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Grpc.model_validate(resp)

    def update(self, data: ne.Grpc | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Grpc

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Grpc.model_validate(data)
        elif isinstance(data, str):
            data = Grpc.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Grpc | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Grpc

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Grpc.model_validate(data)
        elif isinstance(data, str):
            data = Grpc.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class WebguiNode(Node):
    """Navigator for webgui"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Webgui:
        from ..data_models.ne import Webgui
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Webgui.model_validate(resp)

    def update(self, data: ne.Webgui | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Webgui

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Webgui.model_validate(data)
        elif isinstance(data, str):
            data = Webgui.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Webgui | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Webgui

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Webgui.model_validate(data)
        elif isinstance(data, str):
            data = Webgui.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ModelSelectionNode(Node):
    """Navigator for model-selection"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ModelSelection:
        from ..data_models.ne import ModelSelection
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ModelSelection.model_validate(resp)

    def update(self, data: ne.ModelSelection | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ModelSelection

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModelSelection.model_validate(data)
        elif isinstance(data, str):
            data = ModelSelection.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ModelSelection | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ModelSelection

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModelSelection.model_validate(data)
        elif isinstance(data, str):
            data = ModelSelection.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class DeleteFileNode(Node):
    """Navigator for delete-file"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.DeleteFile:
        from ..data_models.ne import DeleteFile
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DeleteFile.model_validate(resp)

    def update(self, data: ne.DeleteFile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DeleteFile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DeleteFile.model_validate(data)
        elif isinstance(data, str):
            data = DeleteFile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.DeleteFile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import DeleteFile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DeleteFile.model_validate(data)
        elif isinstance(data, str):
            data = DeleteFile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class ShowFileNode(Node):
    """Navigator for show-file"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ShowFile:
        from ..data_models.ne import ShowFile
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ShowFile.model_validate(resp)

    def update(self, data: ne.ShowFile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ShowFile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ShowFile.model_validate(data)
        elif isinstance(data, str):
            data = ShowFile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ShowFile | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ShowFile

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ShowFile.model_validate(data)
        elif isinstance(data, str):
            data = ShowFile.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class FileTransferNode(Node):
    """Navigator for file-transfer"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.FileTransfer:
        from ..data_models.ne import FileTransfer
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FileTransfer.model_validate(resp)

    def update(self, data: ne.FileTransfer | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FileTransfer

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileTransfer.model_validate(data)
        elif isinstance(data, str):
            data = FileTransfer.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.FileTransfer | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import FileTransfer

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileTransfer.model_validate(data)
        elif isinstance(data, str):
            data = FileTransfer.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class MultishelfFileManagementItemNode(ItemNode):
    """Navigator for list item multishelf-file-management"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.MultishelfFileManagementItem:
        from ..data_models.ne import MultishelfFileManagementItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return MultishelfFileManagementItem.model_validate(resp)

    def update(self, data: ne.MultishelfFileManagementItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MultishelfFileManagementItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MultishelfFileManagementItem.model_validate(data)
        elif isinstance(data, str):
            data = MultishelfFileManagementItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.MultishelfFileManagementItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MultishelfFileManagementItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MultishelfFileManagementItem.model_validate(data)
        elif isinstance(data, str):
            data = MultishelfFileManagementItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def delete_file(self) -> DeleteFileNode:
        return DeleteFileNode(self._client, f"{self._path}/delete-file", "delete-file")
    @property
    def show_file(self) -> ShowFileNode:
        return ShowFileNode(self._client, f"{self._path}/show-file", "show-file")
    @property
    def file_transfer(self) -> FileTransferNode:
        return FileTransferNode(self._client, f"{self._path}/file-transfer", "file-transfer")

class MultishelfFileManagementListNode(ListNode[MultishelfFileManagementItemNode]):
    """Navigator for list multishelf-file-management"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.MultishelfFileManagementItem]:
        from ..data_models.ne import MultishelfFileManagementItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [MultishelfFileManagementItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.MultishelfFileManagementItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.MultishelfFileManagementItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class SwStageNotificationNode(Node):
    """Navigator for sw-stage-notification"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SwStageNotification:
        from ..data_models.ne import SwStageNotification
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwStageNotification.model_validate(resp)

    def update(self, data: ne.SwStageNotification | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SwStageNotification

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwStageNotification.model_validate(data)
        elif isinstance(data, str):
            data = SwStageNotification.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SwStageNotification | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SwStageNotification

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwStageNotification.model_validate(data)
        elif isinstance(data, str):
            data = SwStageNotification.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SwActivateNotificationNode(Node):
    """Navigator for sw-activate-notification"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SwActivateNotification:
        from ..data_models.ne import SwActivateNotification
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwActivateNotification.model_validate(resp)

    def update(self, data: ne.SwActivateNotification | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SwActivateNotification

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwActivateNotification.model_validate(data)
        elif isinstance(data, str):
            data = SwActivateNotification.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SwActivateNotification | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SwActivateNotification

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwActivateNotification.model_validate(data)
        elif isinstance(data, str):
            data = SwActivateNotification.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class MultishelfSwManagementItemNode(ItemNode):
    """Navigator for list item multishelf-sw-management"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.MultishelfSwManagementItem:
        from ..data_models.ne import MultishelfSwManagementItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return MultishelfSwManagementItem.model_validate(resp)

    def update(self, data: ne.MultishelfSwManagementItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MultishelfSwManagementItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MultishelfSwManagementItem.model_validate(data)
        elif isinstance(data, str):
            data = MultishelfSwManagementItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.MultishelfSwManagementItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MultishelfSwManagementItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MultishelfSwManagementItem.model_validate(data)
        elif isinstance(data, str):
            data = MultishelfSwManagementItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def sw_stage_notification(self) -> SwStageNotificationNode:
        return SwStageNotificationNode(self._client, f"{self._path}/sw-stage-notification", "sw-stage-notification")
    @property
    def sw_activate_notification(self) -> SwActivateNotificationNode:
        return SwActivateNotificationNode(self._client, f"{self._path}/sw-activate-notification", "sw-activate-notification")

class MultishelfSwManagementListNode(ListNode[MultishelfSwManagementItemNode]):
    """Navigator for list multishelf-sw-management"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.MultishelfSwManagementItem]:
        from ..data_models.ne import MultishelfSwManagementItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [MultishelfSwManagementItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.MultishelfSwManagementItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.MultishelfSwManagementItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class MultishelfDiscoveryItemNode(ItemNode):
    """Navigator for list item multishelf-discovery"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.MultishelfDiscoveryItem:
        from ..data_models.ne import MultishelfDiscoveryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return MultishelfDiscoveryItem.model_validate(resp)

    def update(self, data: ne.MultishelfDiscoveryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MultishelfDiscoveryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MultishelfDiscoveryItem.model_validate(data)
        elif isinstance(data, str):
            data = MultishelfDiscoveryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.MultishelfDiscoveryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import MultishelfDiscoveryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MultishelfDiscoveryItem.model_validate(data)
        elif isinstance(data, str):
            data = MultishelfDiscoveryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class MultishelfDiscoveryListNode(ListNode[MultishelfDiscoveryItemNode]):
    """Navigator for list multishelf-discovery"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.MultishelfDiscoveryItem]:
        from ..data_models.ne import MultishelfDiscoveryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [MultishelfDiscoveryItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.MultishelfDiscoveryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.MultishelfDiscoveryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class CapabilitiesNode(Node):
    """Navigator for capabilities"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Capabilities:
        from ..data_models.ne import Capabilities
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Capabilities.model_validate(resp)

    def update(self, data: ne.Capabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Capabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Capabilities.model_validate(data)
        elif isinstance(data, str):
            data = Capabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Capabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Capabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Capabilities.model_validate(data)
        elif isinstance(data, str):
            data = Capabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SystemSystemNode(Node):
    """Navigator for system"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.SystemSystem:
        from ..data_models.ne import SystemSystem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SystemSystem.model_validate(resp)

    def update(self, data: ne.SystemSystem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SystemSystem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SystemSystem.model_validate(data)
        elif isinstance(data, str):
            data = SystemSystem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.SystemSystem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import SystemSystem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SystemSystem.model_validate(data)
        elif isinstance(data, str):
            data = SystemSystem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def power_consumption(self) -> PowerConsumptionNode:
        return PowerConsumptionNode(self._client, f"{self._path}/power-consumption", "power-consumption")
    @property
    def l2_dcn(self) -> L2DcnNode:
        return L2DcnNode(self._client, f"{self._path}/l2-dcn", "l2-dcn")
    @property
    def networking(self) -> NetworkingNode:
        return NetworkingNode(self._client, f"{self._path}/networking", "networking")
    @property
    def security(self) -> SecurityNode:
        return SecurityNode(self._client, f"{self._path}/security", "security")
    @property
    def sw_management(self) -> SwManagementNode:
        return SwManagementNode(self._client, f"{self._path}/sw-management", "sw-management")
    @property
    def file_management(self) -> FileManagementNode:
        return FileManagementNode(self._client, f"{self._path}/file-management", "file-management")
    @property
    def lldp(self) -> LldpNode:
        return LldpNode(self._client, f"{self._path}/lldp", "lldp")
    @property
    def time_manager(self) -> TimeManagerNode:
        return TimeManagerNode(self._client, f"{self._path}/time-manager", "time-manager")
    @property
    def ztc(self) -> ZtcNode:
        return ZtcNode(self._client, f"{self._path}/ztc", "ztc")
    @property
    def console(self) -> ConsoleNode:
        return ConsoleNode(self._client, f"{self._path}/console", "console")
    @property
    def ssh(self) -> SshNode:
        return SshNode(self._client, f"{self._path}/ssh", "ssh")
    @property
    def snmp(self) -> SnmpNode:
        return SnmpNode(self._client, f"{self._path}/snmp", "snmp")
    @property
    def restconf(self) -> RestconfNode:
        return RestconfNode(self._client, f"{self._path}/restconf", "restconf")
    @property
    def cli(self) -> CliNode:
        return CliNode(self._client, f"{self._path}/cli", "cli")
    @property
    def netconf(self) -> NetconfNode:
        return NetconfNode(self._client, f"{self._path}/netconf", "netconf")
    @property
    def grpc(self) -> GrpcNode:
        return GrpcNode(self._client, f"{self._path}/grpc", "grpc")
    @property
    def webgui(self) -> WebguiNode:
        return WebguiNode(self._client, f"{self._path}/webgui", "webgui")
    @property
    def model_selection(self) -> ModelSelectionNode:
        return ModelSelectionNode(self._client, f"{self._path}/model-selection", "model-selection")
    @property
    def multishelf_file_management(self) -> MultishelfFileManagementListNode:
        return MultishelfFileManagementListNode(self._client, f"{self._path}/multishelf-file-management", "multishelf-file-management", MultishelfFileManagementItemNode)
    @property
    def multishelf_sw_management(self) -> MultishelfSwManagementListNode:
        return MultishelfSwManagementListNode(self._client, f"{self._path}/multishelf-sw-management", "multishelf-sw-management", MultishelfSwManagementItemNode)
    @property
    def multishelf_discovery(self) -> MultishelfDiscoveryListNode:
        return MultishelfDiscoveryListNode(self._client, f"{self._path}/multishelf-discovery", "multishelf-discovery", MultishelfDiscoveryItemNode)
    @property
    def capabilities(self) -> CapabilitiesNode:
        return CapabilitiesNode(self._client, f"{self._path}/capabilities", "capabilities")

class RstpBridgePortTableItemNode(ItemNode):
    """Navigator for list item rstp-bridge-port-table"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpBridgePortTableItem:
        from ..data_models.ne import RstpBridgePortTableItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpBridgePortTableItem.model_validate(resp)

    def update(self, data: ne.RstpBridgePortTableItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgePortTableItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgePortTableItem.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgePortTableItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RstpBridgePortTableItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgePortTableItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgePortTableItem.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgePortTableItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RstpBridgePortTableListNode(ListNode[RstpBridgePortTableItemNode]):
    """Navigator for list rstp-bridge-port-table"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RstpBridgePortTableItem]:
        from ..data_models.ne import RstpBridgePortTableItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RstpBridgePortTableItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RstpBridgePortTableItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RstpBridgePortTableItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RstpConfigNode(Node):
    """Navigator for rstp-config"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpConfig:
        from ..data_models.ne import RstpConfig
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpConfig.model_validate(resp)

    def update(self, data: ne.RstpConfig | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpConfig

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpConfig.model_validate(data)
        elif isinstance(data, str):
            data = RstpConfig.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.RstpConfig | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpConfig

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpConfig.model_validate(data)
        elif isinstance(data, str):
            data = RstpConfig.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def rstp_bridge_port_table(self) -> RstpBridgePortTableListNode:
        return RstpBridgePortTableListNode(self._client, f"{self._path}/rstp-bridge-port-table", "rstp-bridge-port-table", RstpBridgePortTableItemNode)

class RstpBridgeAttrNode(Node):
    """Navigator for rstp-bridge-attr"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpBridgeAttr:
        from ..data_models.ne import RstpBridgeAttr
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpBridgeAttr.model_validate(resp)

    def update(self, data: ne.RstpBridgeAttr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgeAttr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgeAttr.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgeAttr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.RstpBridgeAttr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgeAttr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgeAttr.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgeAttr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class RstpBridgePortStateTableItemNode(ItemNode):
    """Navigator for list item rstp-bridge-port-state-table"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpBridgePortStateTableItem:
        from ..data_models.ne import RstpBridgePortStateTableItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpBridgePortStateTableItem.model_validate(resp)

    def update(self, data: ne.RstpBridgePortStateTableItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgePortStateTableItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgePortStateTableItem.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgePortStateTableItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RstpBridgePortStateTableItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgePortStateTableItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgePortStateTableItem.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgePortStateTableItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RstpBridgePortStateTableListNode(ListNode[RstpBridgePortStateTableItemNode]):
    """Navigator for list rstp-bridge-port-state-table"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RstpBridgePortStateTableItem]:
        from ..data_models.ne import RstpBridgePortStateTableItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RstpBridgePortStateTableItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RstpBridgePortStateTableItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RstpBridgePortStateTableItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RstpBridgePortStateAttrNode(Node):
    """Navigator for rstp-bridge-port-state-attr"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpBridgePortStateAttr:
        from ..data_models.ne import RstpBridgePortStateAttr
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpBridgePortStateAttr.model_validate(resp)

    def update(self, data: ne.RstpBridgePortStateAttr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgePortStateAttr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgePortStateAttr.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgePortStateAttr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.RstpBridgePortStateAttr | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgePortStateAttr

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgePortStateAttr.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgePortStateAttr.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def rstp_bridge_port_state_table(self) -> RstpBridgePortStateTableListNode:
        return RstpBridgePortStateTableListNode(self._client, f"{self._path}/rstp-bridge-port-state-table", "rstp-bridge-port-state-table", RstpBridgePortStateTableItemNode)

class RstpStateNode(Node):
    """Navigator for rstp-state"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpState:
        from ..data_models.ne import RstpState
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpState.model_validate(resp)

    def update(self, data: ne.RstpState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpState.model_validate(data)
        elif isinstance(data, str):
            data = RstpState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.RstpState | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpState

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpState.model_validate(data)
        elif isinstance(data, str):
            data = RstpState.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def rstp_bridge_attr(self) -> RstpBridgeAttrNode:
        return RstpBridgeAttrNode(self._client, f"{self._path}/rstp-bridge-attr", "rstp-bridge-attr")
    @property
    def rstp_bridge_port_state_attr(self) -> RstpBridgePortStateAttrNode:
        return RstpBridgePortStateAttrNode(self._client, f"{self._path}/rstp-bridge-port-state-attr", "rstp-bridge-port-state-attr")

class RstpBridgeInstanceItemNode(ItemNode):
    """Navigator for list item rstp-bridge-instance"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.RstpBridgeInstanceItem:
        from ..data_models.ne import RstpBridgeInstanceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RstpBridgeInstanceItem.model_validate(resp)

    def update(self, data: ne.RstpBridgeInstanceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgeInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgeInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgeInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ne.RstpBridgeInstanceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import RstpBridgeInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RstpBridgeInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = RstpBridgeInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def rstp_config(self) -> RstpConfigNode:
        return RstpConfigNode(self._client, f"{self._path}/rstp-config", "rstp-config")
    @property
    def rstp_state(self) -> RstpStateNode:
        return RstpStateNode(self._client, f"{self._path}/rstp-state", "rstp-state")

class RstpBridgeInstanceListNode(ListNode[RstpBridgeInstanceItemNode]):
    """Navigator for list rstp-bridge-instance"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ne.RstpBridgeInstanceItem]:
        from ..data_models.ne import RstpBridgeInstanceItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RstpBridgeInstanceItem.model_validate(item) for item in resp]

    def create(self, data: list[ne.RstpBridgeInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ne.RstpBridgeInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class RstpNode(Node):
    """Navigator for rstp"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Rstp:
        from ..data_models.ne import Rstp
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Rstp.model_validate(resp)

    def update(self, data: ne.Rstp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Rstp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Rstp.model_validate(data)
        elif isinstance(data, str):
            data = Rstp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Rstp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Rstp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Rstp.model_validate(data)
        elif isinstance(data, str):
            data = Rstp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def rstp_bridge_instance(self) -> RstpBridgeInstanceListNode:
        return RstpBridgeInstanceListNode(self._client, f"{self._path}/rstp-bridge-instance", "rstp-bridge-instance", RstpBridgeInstanceItemNode)

class ProtocolsNode(Node):
    """Navigator for protocols"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Protocols:
        from ..data_models.ne import Protocols
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Protocols.model_validate(resp)

    def update(self, data: ne.Protocols | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Protocols

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Protocols.model_validate(data)
        elif isinstance(data, str):
            data = Protocols.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Protocols | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Protocols

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Protocols.model_validate(data)
        elif isinstance(data, str):
            data = Protocols.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def rstp(self) -> RstpNode:
        return RstpNode(self._client, f"{self._path}/rstp", "rstp")

class NeNode(Node):
    """Navigator for ne"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.Ne:
        from ..data_models.ne import Ne
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ne.model_validate(resp)

    def update(self, data: ne.Ne | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ne

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ne.model_validate(data)
        elif isinstance(data, str):
            data = Ne.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.Ne | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import Ne

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ne.model_validate(data)
        elif isinstance(data, str):
            data = Ne.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def shelf(self) -> ShelfListNode:
        return ShelfListNode(self._client, f"{self._path}/shelf", "shelf", ShelfItemNode)
    @property
    def inventory_data(self) -> InventoryDataNode:
        return InventoryDataNode(self._client, f"{self._path}/inventory-data", "inventory-data")
    @property
    def leds(self) -> LedsNode:
        return LedsNode(self._client, f"{self._path}/leds", "leds")
    @property
    def services(self) -> ServicesNode:
        return ServicesNode(self._client, f"{self._path}/services", "services")
    @property
    def fault(self) -> FaultNode:
        return FaultNode(self._client, f"{self._path}/fault", "fault")
    @property
    def performance(self) -> PerformanceNode:
        return PerformanceNode(self._client, f"{self._path}/performance", "performance")
    @property
    def system(self) -> SystemSystemNode:
        return SystemSystemNode(self._client, f"{self._path}/system", "system")
    @property
    def protocols(self) -> ProtocolsNode:
        return ProtocolsNode(self._client, f"{self._path}/protocols", "protocols")

class ChangedByNode(Node):
    """Navigator for changed-by"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ne.ChangedBy:
        from ..data_models.ne import ChangedBy
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChangedBy.model_validate(resp)

    def update(self, data: ne.ChangedBy | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChangedBy

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChangedBy.model_validate(data)
        elif isinstance(data, str):
            data = ChangedBy.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ne.ChangedBy | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ne import ChangedBy

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChangedBy.model_validate(data)
        elif isinstance(data, str):
            data = ChangedBy.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

