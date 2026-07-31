from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import ioa_network_element


class CurrentFwItemNode(ItemNode):
    """Navigator for list item current-fw"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CurrentFwItem:
        from ..data_models.ioa_network_element import CurrentFwItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentFwItem.model_validate(resp)

    def update(self, data: ioa_network_element.CurrentFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CurrentFwItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentFwItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentFwItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CurrentFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CurrentFwItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentFwItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentFwItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CurrentFwListNode(ListNode[CurrentFwItemNode]):
    """Navigator for list current-fw"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CurrentFwItem]:
        from ..data_models.ioa_network_element import CurrentFwItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CurrentFwItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CurrentFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CurrentFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class InventoryNode(Node):
    """Navigator for inventory"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Inventory:
        from ..data_models.ioa_network_element import Inventory

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Inventory.model_validate(resp)

    def update(self, data: ioa_network_element.Inventory | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Inventory

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Inventory.model_validate(data)
        elif isinstance(data, str):
            data = Inventory.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Inventory | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Inventory

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Inventory.model_validate(data)
        elif isinstance(data, str):
            data = Inventory.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def current_fw(self) -> CurrentFwListNode:
        return CurrentFwListNode(self._client, f"{self._path}/current-fw", "current-fw", CurrentFwItemNode)


class SlotItemNode(ItemNode):
    """Navigator for list item slot"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SlotItem:
        from ..data_models.ioa_network_element import SlotItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SlotItem.model_validate(resp)

    def update(self, data: ioa_network_element.SlotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SlotItem

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

    def replace(self, data: ioa_network_element.SlotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SlotItem

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
    def inventory(self) -> InventoryNode:
        return InventoryNode(self._client, f"{self._path}/inventory", "inventory")


class SlotListNode(ListNode[SlotItemNode]):
    """Navigator for list slot"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SlotItem]:
        from ..data_models.ioa_network_element import SlotItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SlotItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SlotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SlotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ChassisItemNode(ItemNode):
    """Navigator for list item chassis"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ChassisItem:
        from ..data_models.ioa_network_element import ChassisItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChassisItem.model_validate(resp)

    def update(self, data: ioa_network_element.ChassisItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ChassisItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChassisItem.model_validate(data)
        elif isinstance(data, str):
            data = ChassisItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ChassisItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ChassisItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ChassisItem.model_validate(data)
        elif isinstance(data, str):
            data = ChassisItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def inventory(self) -> InventoryNode:
        return InventoryNode(self._client, f"{self._path}/inventory", "inventory")

    @property
    def slot(self) -> SlotListNode:
        return SlotListNode(self._client, f"{self._path}/slot", "slot", SlotItemNode)


class ChassisListNode(ListNode[ChassisItemNode]):
    """Navigator for list chassis"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ChassisItem]:
        from ..data_models.ioa_network_element import ChassisItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ChassisItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ChassisItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ChassisItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ControllerCardNode(Node):
    """Navigator for controller-card"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ControllerCard:
        from ..data_models.ioa_network_element import ControllerCard

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ControllerCard.model_validate(resp)

    def update(self, data: ioa_network_element.ControllerCard | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ControllerCard

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ControllerCard.model_validate(data)
        elif isinstance(data, str):
            data = ControllerCard.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.ControllerCard | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ControllerCard

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ControllerCard.model_validate(data)
        elif isinstance(data, str):
            data = ControllerCard.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class PropertyItemNode(ItemNode):
    """Navigator for list item property"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PropertyItem:
        from ..data_models.ioa_network_element import PropertyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PropertyItem.model_validate(resp)

    def update(self, data: ioa_network_element.PropertyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PropertyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PropertyItem.model_validate(data)
        elif isinstance(data, str):
            data = PropertyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.PropertyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PropertyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PropertyItem.model_validate(data)
        elif isinstance(data, str):
            data = PropertyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PropertyListNode(ListNode[PropertyItemNode]):
    """Navigator for list property"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.PropertyItem]:
        from ..data_models.ioa_network_element import PropertyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PropertyItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.PropertyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.PropertyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SerdesItemNode(ItemNode):
    """Navigator for list item serdes"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SerdesItem:
        from ..data_models.ioa_network_element import SerdesItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SerdesItem.model_validate(resp)

    def update(self, data: ioa_network_element.SerdesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SerdesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerdesItem.model_validate(data)
        elif isinstance(data, str):
            data = SerdesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SerdesItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SerdesItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerdesItem.model_validate(data)
        elif isinstance(data, str):
            data = SerdesItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SerdesListNode(ListNode[SerdesItemNode]):
    """Navigator for list serdes"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SerdesItem]:
        from ..data_models.ioa_network_element import SerdesItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SerdesItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SerdesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SerdesItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class TomNode(Node):
    """Navigator for tom"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Tom:
        from ..data_models.ioa_network_element import Tom

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Tom.model_validate(resp)

    def update(self, data: ioa_network_element.Tom | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Tom

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Tom.model_validate(data)
        elif isinstance(data, str):
            data = Tom.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Tom | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Tom

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Tom.model_validate(data)
        elif isinstance(data, str):
            data = Tom.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def serdes(self) -> SerdesListNode:
        return SerdesListNode(self._client, f"{self._path}/serdes", "serdes", SerdesItemNode)


class UsbNode(Node):
    """Navigator for usb"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Usb:
        from ..data_models.ioa_network_element import Usb

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Usb.model_validate(resp)

    def update(self, data: ioa_network_element.Usb | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Usb

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Usb.model_validate(data)
        elif isinstance(data, str):
            data = Usb.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Usb | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Usb

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Usb.model_validate(data)
        elif isinstance(data, str):
            data = Usb.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class CommEthNode(Node):
    """Navigator for comm-eth"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CommEth:
        from ..data_models.ioa_network_element import CommEth

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CommEth.model_validate(resp)

    def update(self, data: ioa_network_element.CommEth | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CommEth

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommEth.model_validate(data)
        elif isinstance(data, str):
            data = CommEth.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.CommEth | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CommEth

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommEth.model_validate(data)
        elif isinstance(data, str):
            data = CommEth.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class PortItemNode(ItemNode):
    """Navigator for list item port"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PortItem:
        from ..data_models.ioa_network_element import PortItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PortItem.model_validate(resp)

    def update(self, data: ioa_network_element.PortItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PortItem

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

    def replace(self, data: ioa_network_element.PortItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PortItem

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
    def tom(self) -> TomNode:
        return TomNode(self._client, f"{self._path}/tom", "tom")

    @property
    def usb(self) -> UsbNode:
        return UsbNode(self._client, f"{self._path}/usb", "usb")

    @property
    def comm_eth(self) -> CommEthNode:
        return CommEthNode(self._client, f"{self._path}/comm-eth", "comm-eth")

    @property
    def inventory(self) -> InventoryNode:
        return InventoryNode(self._client, f"{self._path}/inventory", "inventory")


class PortListNode(ListNode[PortItemNode]):
    """Navigator for list port"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.PortItem]:
        from ..data_models.ioa_network_element import PortItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PortItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.PortItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.PortItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ConsoleNode(Node):
    """Navigator for console"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Console:
        from ..data_models.ioa_network_element import Console

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Console.model_validate(resp)

    def update(self, data: ioa_network_element.Console | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Console

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

    def replace(self, data: ioa_network_element.Console | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Console

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


class ResourcesNode(Node):
    """Navigator for resources"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Resources:
        from ..data_models.ioa_network_element import Resources

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Resources.model_validate(resp)

    def update(self, data: ioa_network_element.Resources | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Resources

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Resources.model_validate(data)
        elif isinstance(data, str):
            data = Resources.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Resources | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Resources

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Resources.model_validate(data)
        elif isinstance(data, str):
            data = Resources.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SupportedAdvancedParameterItemNode(ItemNode):
    """Navigator for list item supported-advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedAdvancedParameterItem:
        from ..data_models.ioa_network_element import SupportedAdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedAdvancedParameterItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SupportedAdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportedAdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedAdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedAdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SupportedAdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportedAdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedAdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedAdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SupportedAdvancedParameterListNode(ListNode[SupportedAdvancedParameterItemNode]):
    """Navigator for list supported-advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedAdvancedParameterItem]:
        from ..data_models.ioa_network_element import SupportedAdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedAdvancedParameterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedAdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedAdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CapabilitiesNode(Node):
    """Navigator for capabilities"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Capabilities:
        from ..data_models.ioa_network_element import Capabilities

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Capabilities.model_validate(resp)

    def update(self, data: ioa_network_element.Capabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Capabilities

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

    def replace(self, data: ioa_network_element.Capabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Capabilities

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

    @property
    def supported_advanced_parameter(self) -> SupportedAdvancedParameterListNode:
        return SupportedAdvancedParameterListNode(
            self._client,
            f"{self._path}/supported-advanced-parameter",
            "supported-advanced-parameter",
            SupportedAdvancedParameterItemNode,
        )


class CardItemNode(ItemNode):
    """Navigator for list item card"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CardItem:
        from ..data_models.ioa_network_element import CardItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CardItem.model_validate(resp)

    def update(self, data: ioa_network_element.CardItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CardItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CardItem.model_validate(data)
        elif isinstance(data, str):
            data = CardItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CardItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CardItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CardItem.model_validate(data)
        elif isinstance(data, str):
            data = CardItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def slot(self) -> SlotListNode:
        return SlotListNode(self._client, f"{self._path}/slot", "slot", SlotItemNode)

    @property
    def controller_card(self) -> ControllerCardNode:
        return ControllerCardNode(self._client, f"{self._path}/controller-card", "controller-card")

    @property
    def property_(self) -> PropertyListNode:
        return PropertyListNode(self._client, f"{self._path}/property", "property", PropertyItemNode)

    @property
    def port(self) -> PortListNode:
        return PortListNode(self._client, f"{self._path}/port", "port", PortItemNode)

    @property
    def console(self) -> ConsoleNode:
        return ConsoleNode(self._client, f"{self._path}/console", "console")

    @property
    def resources(self) -> ResourcesNode:
        return ResourcesNode(self._client, f"{self._path}/resources", "resources")

    @property
    def capabilities(self) -> CapabilitiesNode:
        return CapabilitiesNode(self._client, f"{self._path}/capabilities", "capabilities")


class CardListNode(ListNode[CardItemNode]):
    """Navigator for list card"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CardItem]:
        from ..data_models.ioa_network_element import CardItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CardItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CardItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CardItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LedItemNode(ItemNode):
    """Navigator for list item led"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LedItem:
        from ..data_models.ioa_network_element import LedItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LedItem.model_validate(resp)

    def update(self, data: ioa_network_element.LedItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LedItem

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

    def replace(self, data: ioa_network_element.LedItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LedItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LedItem]:
        from ..data_models.ioa_network_element import LedItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LedItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LedItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LedItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LedsNode(Node):
    """Navigator for leds"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Leds:
        from ..data_models.ioa_network_element import Leds

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Leds.model_validate(resp)

    def update(self, data: ioa_network_element.Leds | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Leds

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

    def replace(self, data: ioa_network_element.Leds | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Leds

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


class SerdesTemplateEntryItemNode(ItemNode):
    """Navigator for list item serdes-template-entry"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SerdesTemplateEntryItem:
        from ..data_models.ioa_network_element import SerdesTemplateEntryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SerdesTemplateEntryItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SerdesTemplateEntryItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SerdesTemplateEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerdesTemplateEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = SerdesTemplateEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SerdesTemplateEntryItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SerdesTemplateEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerdesTemplateEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = SerdesTemplateEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SerdesTemplateEntryListNode(ListNode[SerdesTemplateEntryItemNode]):
    """Navigator for list serdes-template-entry"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SerdesTemplateEntryItem]:
        from ..data_models.ioa_network_element import SerdesTemplateEntryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SerdesTemplateEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SerdesTemplateEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SerdesTemplateEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SerdesTemplateItemNode(ItemNode):
    """Navigator for list item serdes-template"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SerdesTemplateItem:
        from ..data_models.ioa_network_element import SerdesTemplateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SerdesTemplateItem.model_validate(resp)

    def update(self, data: ioa_network_element.SerdesTemplateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SerdesTemplateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerdesTemplateItem.model_validate(data)
        elif isinstance(data, str):
            data = SerdesTemplateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SerdesTemplateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SerdesTemplateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerdesTemplateItem.model_validate(data)
        elif isinstance(data, str):
            data = SerdesTemplateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def serdes_template_entry(self) -> SerdesTemplateEntryListNode:
        return SerdesTemplateEntryListNode(
            self._client, f"{self._path}/serdes-template-entry", "serdes-template-entry", SerdesTemplateEntryItemNode
        )


class SerdesTemplateListNode(ListNode[SerdesTemplateItemNode]):
    """Navigator for list serdes-template"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SerdesTemplateItem]:
        from ..data_models.ioa_network_element import SerdesTemplateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SerdesTemplateItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SerdesTemplateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SerdesTemplateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EquipmentTemplatesNode(Node):
    """Navigator for equipment-templates"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.EquipmentTemplates:
        from ..data_models.ioa_network_element import EquipmentTemplates

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EquipmentTemplates.model_validate(resp)

    def update(self, data: ioa_network_element.EquipmentTemplates | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EquipmentTemplates

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EquipmentTemplates.model_validate(data)
        elif isinstance(data, str):
            data = EquipmentTemplates.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.EquipmentTemplates | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EquipmentTemplates

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EquipmentTemplates.model_validate(data)
        elif isinstance(data, str):
            data = EquipmentTemplates.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def serdes_template(self) -> SerdesTemplateListNode:
        return SerdesTemplateListNode(
            self._client, f"{self._path}/serdes-template", "serdes-template", SerdesTemplateItemNode
        )


class GlobalPowerProfileItemNode(ItemNode):
    """Navigator for list item global-power-profile"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.GlobalPowerProfileItem:
        from ..data_models.ioa_network_element import GlobalPowerProfileItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return GlobalPowerProfileItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.GlobalPowerProfileItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import GlobalPowerProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GlobalPowerProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = GlobalPowerProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.GlobalPowerProfileItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import GlobalPowerProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GlobalPowerProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = GlobalPowerProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class GlobalPowerProfileListNode(ListNode[GlobalPowerProfileItemNode]):
    """Navigator for list global-power-profile"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.GlobalPowerProfileItem]:
        from ..data_models.ioa_network_element import GlobalPowerProfileItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [GlobalPowerProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.GlobalPowerProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.GlobalPowerProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EquipmentPoliciesNode(Node):
    """Navigator for equipment-policies"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.EquipmentPolicies:
        from ..data_models.ioa_network_element import EquipmentPolicies

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EquipmentPolicies.model_validate(resp)

    def update(self, data: ioa_network_element.EquipmentPolicies | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EquipmentPolicies

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EquipmentPolicies.model_validate(data)
        elif isinstance(data, str):
            data = EquipmentPolicies.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.EquipmentPolicies | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EquipmentPolicies

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EquipmentPolicies.model_validate(data)
        elif isinstance(data, str):
            data = EquipmentPolicies.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def equipment_templates(self) -> EquipmentTemplatesNode:
        return EquipmentTemplatesNode(self._client, f"{self._path}/equipment-templates", "equipment-templates")

    @property
    def global_power_profile(self) -> GlobalPowerProfileListNode:
        return GlobalPowerProfileListNode(
            self._client, f"{self._path}/global-power-profile", "global-power-profile", GlobalPowerProfileItemNode
        )


class UnprovisionedInventoryItemNode(ItemNode):
    """Navigator for list item unprovisioned-inventory"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.UnprovisionedInventoryItem:
        from ..data_models.ioa_network_element import UnprovisionedInventoryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return UnprovisionedInventoryItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.UnprovisionedInventoryItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import UnprovisionedInventoryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UnprovisionedInventoryItem.model_validate(data)
        elif isinstance(data, str):
            data = UnprovisionedInventoryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.UnprovisionedInventoryItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import UnprovisionedInventoryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UnprovisionedInventoryItem.model_validate(data)
        elif isinstance(data, str):
            data = UnprovisionedInventoryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class UnprovisionedInventoryListNode(ListNode[UnprovisionedInventoryItemNode]):
    """Navigator for list unprovisioned-inventory"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.UnprovisionedInventoryItem]:
        from ..data_models.ioa_network_element import UnprovisionedInventoryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [UnprovisionedInventoryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.UnprovisionedInventoryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.UnprovisionedInventoryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EquipmentNode(Node):
    """Navigator for equipment"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Equipment:
        from ..data_models.ioa_network_element import Equipment

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Equipment.model_validate(resp)

    def update(self, data: ioa_network_element.Equipment | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Equipment

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Equipment.model_validate(data)
        elif isinstance(data, str):
            data = Equipment.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Equipment | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Equipment

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Equipment.model_validate(data)
        elif isinstance(data, str):
            data = Equipment.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def chassis(self) -> ChassisListNode:
        return ChassisListNode(self._client, f"{self._path}/chassis", "chassis", ChassisItemNode)

    @property
    def card(self) -> CardListNode:
        return CardListNode(self._client, f"{self._path}/card", "card", CardItemNode)

    @property
    def leds(self) -> LedsNode:
        return LedsNode(self._client, f"{self._path}/leds", "leds")

    @property
    def equipment_policies(self) -> EquipmentPoliciesNode:
        return EquipmentPoliciesNode(self._client, f"{self._path}/equipment-policies", "equipment-policies")

    @property
    def unprovisioned_inventory(self) -> UnprovisionedInventoryListNode:
        return UnprovisionedInventoryListNode(
            self._client,
            f"{self._path}/unprovisioned-inventory",
            "unprovisioned-inventory",
            UnprovisionedInventoryItemNode,
        )


class OtsDiagnosticsNode(Node):
    """Navigator for ots-diagnostics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtsDiagnostics:
        from ..data_models.ioa_network_element import OtsDiagnostics

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtsDiagnostics.model_validate(resp)

    def update(self, data: ioa_network_element.OtsDiagnostics | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtsDiagnostics

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

    def replace(self, data: ioa_network_element.OtsDiagnostics | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtsDiagnostics

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtsItem:
        from ..data_models.ioa_network_element import OtsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtsItem.model_validate(resp)

    def update(self, data: ioa_network_element.OtsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtsItem

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

    def replace(self, data: ioa_network_element.OtsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtsItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OtsItem]:
        from ..data_models.ioa_network_element import OtsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OtsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OtsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OtsRItemNode(ItemNode):
    """Navigator for list item ots-r"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtsRItem:
        from ..data_models.ioa_network_element import OtsRItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtsRItem.model_validate(resp)

    def update(self, data: ioa_network_element.OtsRItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtsRItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtsRItem.model_validate(data)
        elif isinstance(data, str):
            data = OtsRItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OtsRItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtsRItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtsRItem.model_validate(data)
        elif isinstance(data, str):
            data = OtsRItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OtsRListNode(ListNode[OtsRItemNode]):
    """Navigator for list ots-r"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OtsRItem]:
        from ..data_models.ioa_network_element import OtsRItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtsRItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OtsRItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OtsRItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OscItemNode(ItemNode):
    """Navigator for list item osc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OscItem:
        from ..data_models.ioa_network_element import OscItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OscItem.model_validate(resp)

    def update(self, data: ioa_network_element.OscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OscItem

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

    def replace(self, data: ioa_network_element.OscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OscItem

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


class OscListNode(ListNode[OscItemNode]):
    """Navigator for list osc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OscItem]:
        from ..data_models.ioa_network_element import OscItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OscItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OpsItemNode(ItemNode):
    """Navigator for list item ops"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OpsItem:
        from ..data_models.ioa_network_element import OpsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpsItem.model_validate(resp)

    def update(self, data: ioa_network_element.OpsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpsItem

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

    def replace(self, data: ioa_network_element.OpsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpsItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OpsItem]:
        from ..data_models.ioa_network_element import OpsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OpsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OpsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OmsItemNode(ItemNode):
    """Navigator for list item oms"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OmsItem:
        from ..data_models.ioa_network_element import OmsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OmsItem.model_validate(resp)

    def update(self, data: ioa_network_element.OmsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OmsItem

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

    def replace(self, data: ioa_network_element.OmsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OmsItem

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


class OmsListNode(ListNode[OmsItemNode]):
    """Navigator for list oms"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OmsItem]:
        from ..data_models.ioa_network_element import OmsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OmsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OmsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OmsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SpectrumControlItemNode(ItemNode):
    """Navigator for list item spectrum-control"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SpectrumControlItem:
        from ..data_models.ioa_network_element import SpectrumControlItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SpectrumControlItem.model_validate(resp)

    def update(self, data: ioa_network_element.SpectrumControlItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SpectrumControlItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpectrumControlItem.model_validate(data)
        elif isinstance(data, str):
            data = SpectrumControlItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SpectrumControlItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SpectrumControlItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpectrumControlItem.model_validate(data)
        elif isinstance(data, str):
            data = SpectrumControlItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SpectrumControlListNode(ListNode[SpectrumControlItemNode]):
    """Navigator for list spectrum-control"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SpectrumControlItem]:
        from ..data_models.ioa_network_element import SpectrumControlItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SpectrumControlItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SpectrumControlItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SpectrumControlItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SpectrumMonitoringItemNode(ItemNode):
    """Navigator for list item spectrum-monitoring"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SpectrumMonitoringItem:
        from ..data_models.ioa_network_element import SpectrumMonitoringItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SpectrumMonitoringItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SpectrumMonitoringItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SpectrumMonitoringItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpectrumMonitoringItem.model_validate(data)
        elif isinstance(data, str):
            data = SpectrumMonitoringItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SpectrumMonitoringItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SpectrumMonitoringItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpectrumMonitoringItem.model_validate(data)
        elif isinstance(data, str):
            data = SpectrumMonitoringItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SpectrumMonitoringListNode(ListNode[SpectrumMonitoringItemNode]):
    """Navigator for list spectrum-monitoring"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SpectrumMonitoringItem]:
        from ..data_models.ioa_network_element import SpectrumMonitoringItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SpectrumMonitoringItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SpectrumMonitoringItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SpectrumMonitoringItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SpectrumItemNode(ItemNode):
    """Navigator for list item spectrum"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SpectrumItem:
        from ..data_models.ioa_network_element import SpectrumItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SpectrumItem.model_validate(resp)

    def update(self, data: ioa_network_element.SpectrumItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SpectrumItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpectrumItem.model_validate(data)
        elif isinstance(data, str):
            data = SpectrumItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SpectrumItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SpectrumItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SpectrumItem.model_validate(data)
        elif isinstance(data, str):
            data = SpectrumItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def spectrum_control(self) -> SpectrumControlListNode:
        return SpectrumControlListNode(
            self._client, f"{self._path}/spectrum-control", "spectrum-control", SpectrumControlItemNode
        )

    @property
    def spectrum_monitoring(self) -> SpectrumMonitoringListNode:
        return SpectrumMonitoringListNode(
            self._client, f"{self._path}/spectrum-monitoring", "spectrum-monitoring", SpectrumMonitoringItemNode
        )


class SpectrumListNode(ListNode[SpectrumItemNode]):
    """Navigator for list spectrum"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SpectrumItem]:
        from ..data_models.ioa_network_element import SpectrumItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SpectrumItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SpectrumItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SpectrumItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OchmItemNode(ItemNode):
    """Navigator for list item ochm"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OchmItem:
        from ..data_models.ioa_network_element import OchmItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OchmItem.model_validate(resp)

    def update(self, data: ioa_network_element.OchmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OchmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchmItem.model_validate(data)
        elif isinstance(data, str):
            data = OchmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OchmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OchmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OchmItem.model_validate(data)
        elif isinstance(data, str):
            data = OchmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OchmListNode(ListNode[OchmItemNode]):
    """Navigator for list ochm"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OchmItem]:
        from ..data_models.ioa_network_element import OchmItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OchmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OchmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OchmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class McItemNode(ItemNode):
    """Navigator for list item mc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.McItem:
        from ..data_models.ioa_network_element import McItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return McItem.model_validate(resp)

    def update(self, data: ioa_network_element.McItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import McItem

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

    def replace(self, data: ioa_network_element.McItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import McItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.McItem]:
        from ..data_models.ioa_network_element import McItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [McItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.McItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.McItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NmcItemNode(ItemNode):
    """Navigator for list item nmc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NmcItem:
        from ..data_models.ioa_network_element import NmcItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NmcItem.model_validate(resp)

    def update(self, data: ioa_network_element.NmcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NmcItem

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

    def replace(self, data: ioa_network_element.NmcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NmcItem

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


class NmcListNode(ListNode[NmcItemNode]):
    """Navigator for list nmc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NmcItem]:
        from ..data_models.ioa_network_element import NmcItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NmcItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NmcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NmcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class RscItemNode(ItemNode):
    """Navigator for list item rsc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.RscItem:
        from ..data_models.ioa_network_element import RscItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RscItem.model_validate(resp)

    def update(self, data: ioa_network_element.RscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RscItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RscItem.model_validate(data)
        elif isinstance(data, str):
            data = RscItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.RscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RscItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RscItem.model_validate(data)
        elif isinstance(data, str):
            data = RscItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RscListNode(ListNode[RscItemNode]):
    """Navigator for list rsc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.RscItem]:
        from ..data_models.ioa_network_element import RscItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RscItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.RscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.RscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class PumpItemNode(ItemNode):
    """Navigator for list item pump"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PumpItem:
        from ..data_models.ioa_network_element import PumpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PumpItem.model_validate(resp)

    def update(self, data: ioa_network_element.PumpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PumpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PumpItem.model_validate(data)
        elif isinstance(data, str):
            data = PumpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.PumpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PumpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PumpItem.model_validate(data)
        elif isinstance(data, str):
            data = PumpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PumpListNode(ListNode[PumpItemNode]):
    """Navigator for list pump"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.PumpItem]:
        from ..data_models.ioa_network_element import PumpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PumpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.PumpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.PumpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SuperChannelGroupItemNode(ItemNode):
    """Navigator for list item super-channel-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SuperChannelGroupItem:
        from ..data_models.ioa_network_element import SuperChannelGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SuperChannelGroupItem.model_validate(resp)

    def update(self, data: ioa_network_element.SuperChannelGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SuperChannelGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SuperChannelGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = SuperChannelGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SuperChannelGroupItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SuperChannelGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SuperChannelGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = SuperChannelGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SuperChannelGroupListNode(ListNode[SuperChannelGroupItemNode]):
    """Navigator for list super-channel-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SuperChannelGroupItem]:
        from ..data_models.ioa_network_element import SuperChannelGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SuperChannelGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SuperChannelGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SuperChannelGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DigitalTriggerRegistrationNode(Node):
    """Navigator for digital-trigger-registration"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DigitalTriggerRegistration:
        from ..data_models.ioa_network_element import DigitalTriggerRegistration

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DigitalTriggerRegistration.model_validate(resp)

    def update(
        self, data: ioa_network_element.DigitalTriggerRegistration | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import DigitalTriggerRegistration

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DigitalTriggerRegistration.model_validate(data)
        elif isinstance(data, str):
            data = DigitalTriggerRegistration.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.DigitalTriggerRegistration | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import DigitalTriggerRegistration

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DigitalTriggerRegistration.model_validate(data)
        elif isinstance(data, str):
            data = DigitalTriggerRegistration.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SuperChannelItemNode(ItemNode):
    """Navigator for list item super-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SuperChannelItem:
        from ..data_models.ioa_network_element import SuperChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SuperChannelItem.model_validate(resp)

    def update(self, data: ioa_network_element.SuperChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SuperChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SuperChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = SuperChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SuperChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SuperChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SuperChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = SuperChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def digital_trigger_registration(self) -> DigitalTriggerRegistrationNode:
        return DigitalTriggerRegistrationNode(
            self._client, f"{self._path}/digital-trigger-registration", "digital-trigger-registration"
        )


class SuperChannelListNode(ListNode[SuperChannelItemNode]):
    """Navigator for list super-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SuperChannelItem]:
        from ..data_models.ioa_network_element import SuperChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SuperChannelItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SuperChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SuperChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AdvancedParameterItemNode(ItemNode):
    """Navigator for list item advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AdvancedParameterItem:
        from ..data_models.ioa_network_element import AdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AdvancedParameterItem.model_validate(resp)

    def update(self, data: ioa_network_element.AdvancedParameterItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = AdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.AdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import AdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = AdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AdvancedParameterListNode(ListNode[AdvancedParameterItemNode]):
    """Navigator for list advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AdvancedParameterItem]:
        from ..data_models.ioa_network_element import AdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AdvancedParameterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CurrentAdvancedParameterItemNode(ItemNode):
    """Navigator for list item current-advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CurrentAdvancedParameterItem:
        from ..data_models.ioa_network_element import CurrentAdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentAdvancedParameterItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.CurrentAdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import CurrentAdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentAdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentAdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.CurrentAdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import CurrentAdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentAdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentAdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CurrentAdvancedParameterListNode(ListNode[CurrentAdvancedParameterItemNode]):
    """Navigator for list current-advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CurrentAdvancedParameterItem]:
        from ..data_models.ioa_network_element import CurrentAdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CurrentAdvancedParameterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CurrentAdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CurrentAdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OpticalCarrierItemNode(ItemNode):
    """Navigator for list item optical-carrier"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OpticalCarrierItem:
        from ..data_models.ioa_network_element import OpticalCarrierItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalCarrierItem.model_validate(resp)

    def update(self, data: ioa_network_element.OpticalCarrierItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalCarrierItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalCarrierItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalCarrierItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OpticalCarrierItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalCarrierItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalCarrierItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalCarrierItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def advanced_parameter(self) -> AdvancedParameterListNode:
        return AdvancedParameterListNode(
            self._client, f"{self._path}/advanced-parameter", "advanced-parameter", AdvancedParameterItemNode
        )

    @property
    def current_advanced_parameter(self) -> CurrentAdvancedParameterListNode:
        return CurrentAdvancedParameterListNode(
            self._client,
            f"{self._path}/current-advanced-parameter",
            "current-advanced-parameter",
            CurrentAdvancedParameterItemNode,
        )


class OpticalCarrierListNode(ListNode[OpticalCarrierItemNode]):
    """Navigator for list optical-carrier"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OpticalCarrierItem]:
        from ..data_models.ioa_network_element import OpticalCarrierItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpticalCarrierItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OpticalCarrierItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OpticalCarrierItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OpticalChannelItemNode(ItemNode):
    """Navigator for list item optical-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OpticalChannelItem:
        from ..data_models.ioa_network_element import OpticalChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalChannelItem.model_validate(resp)

    def update(self, data: ioa_network_element.OpticalChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OpticalChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OpticalChannelListNode(ListNode[OpticalChannelItemNode]):
    """Navigator for list optical-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OpticalChannelItem]:
        from ..data_models.ioa_network_element import OpticalChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpticalChannelItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OpticalChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OpticalChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OtuDiagnosticsItemNode(ItemNode):
    """Navigator for list item otu-diagnostics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtuDiagnosticsItem:
        from ..data_models.ioa_network_element import OtuDiagnosticsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtuDiagnosticsItem.model_validate(resp)

    def update(self, data: ioa_network_element.OtuDiagnosticsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtuDiagnosticsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtuDiagnosticsItem.model_validate(data)
        elif isinstance(data, str):
            data = OtuDiagnosticsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OtuDiagnosticsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtuDiagnosticsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtuDiagnosticsItem.model_validate(data)
        elif isinstance(data, str):
            data = OtuDiagnosticsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OtuDiagnosticsListNode(ListNode[OtuDiagnosticsItemNode]):
    """Navigator for list otu-diagnostics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OtuDiagnosticsItem]:
        from ..data_models.ioa_network_element import OtuDiagnosticsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtuDiagnosticsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OtuDiagnosticsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OtuDiagnosticsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OtuItemNode(ItemNode):
    """Navigator for list item otu"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtuItem:
        from ..data_models.ioa_network_element import OtuItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtuItem.model_validate(resp)

    def update(self, data: ioa_network_element.OtuItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtuItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtuItem.model_validate(data)
        elif isinstance(data, str):
            data = OtuItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OtuItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtuItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtuItem.model_validate(data)
        elif isinstance(data, str):
            data = OtuItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def otu_diagnostics(self) -> OtuDiagnosticsListNode:
        return OtuDiagnosticsListNode(
            self._client, f"{self._path}/otu-diagnostics", "otu-diagnostics", OtuDiagnosticsItemNode
        )


class OtuListNode(ListNode[OtuItemNode]):
    """Navigator for list otu"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OtuItem]:
        from ..data_models.ioa_network_element import OtuItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtuItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OtuItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OtuItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OduDiagnosticsItemNode(ItemNode):
    """Navigator for list item odu-diagnostics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OduDiagnosticsItem:
        from ..data_models.ioa_network_element import OduDiagnosticsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OduDiagnosticsItem.model_validate(resp)

    def update(self, data: ioa_network_element.OduDiagnosticsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OduDiagnosticsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduDiagnosticsItem.model_validate(data)
        elif isinstance(data, str):
            data = OduDiagnosticsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OduDiagnosticsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OduDiagnosticsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OduDiagnosticsItem.model_validate(data)
        elif isinstance(data, str):
            data = OduDiagnosticsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OduDiagnosticsListNode(ListNode[OduDiagnosticsItemNode]):
    """Navigator for list odu-diagnostics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OduDiagnosticsItem]:
        from ..data_models.ioa_network_element import OduDiagnosticsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OduDiagnosticsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OduDiagnosticsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OduDiagnosticsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OduItemNode(ItemNode):
    """Navigator for list item odu"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OduItem:
        from ..data_models.ioa_network_element import OduItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OduItem.model_validate(resp)

    def update(self, data: ioa_network_element.OduItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OduItem

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

    def replace(self, data: ioa_network_element.OduItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OduItem

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
    def odu_diagnostics(self) -> OduDiagnosticsListNode:
        return OduDiagnosticsListNode(
            self._client, f"{self._path}/odu-diagnostics", "odu-diagnostics", OduDiagnosticsItemNode
        )


class OduListNode(ListNode[OduItemNode]):
    """Navigator for list odu"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OduItem]:
        from ..data_models.ioa_network_element import OduItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OduItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OduItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OduItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EthernetItemNode(ItemNode):
    """Navigator for list item ethernet"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.EthernetItem:
        from ..data_models.ioa_network_element import EthernetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EthernetItem.model_validate(resp)

    def update(self, data: ioa_network_element.EthernetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EthernetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EthernetItem.model_validate(data)
        elif isinstance(data, str):
            data = EthernetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.EthernetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EthernetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EthernetItem.model_validate(data)
        elif isinstance(data, str):
            data = EthernetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class EthernetListNode(ListNode[EthernetItemNode]):
    """Navigator for list ethernet"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.EthernetItem]:
        from ..data_models.ioa_network_element import EthernetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [EthernetItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.EthernetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.EthernetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class TribPtpItemNode(ItemNode):
    """Navigator for list item trib-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TribPtpItem:
        from ..data_models.ioa_network_element import TribPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TribPtpItem.model_validate(resp)

    def update(self, data: ioa_network_element.TribPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TribPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TribPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = TribPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.TribPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TribPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TribPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = TribPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TribPtpListNode(ListNode[TribPtpItemNode]):
    """Navigator for list trib-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TribPtpItem]:
        from ..data_models.ioa_network_element import TribPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TribPtpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TribPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TribPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CommChannelItemNode(ItemNode):
    """Navigator for list item comm-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CommChannelItem:
        from ..data_models.ioa_network_element import CommChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CommChannelItem.model_validate(resp)

    def update(self, data: ioa_network_element.CommChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CommChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = CommChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CommChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CommChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = CommChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CommChannelListNode(ListNode[CommChannelItemNode]):
    """Navigator for list comm-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CommChannelItem]:
        from ..data_models.ioa_network_element import CommChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CommChannelItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CommChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CommChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CidPtpItemNode(ItemNode):
    """Navigator for list item cid-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CidPtpItem:
        from ..data_models.ioa_network_element import CidPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CidPtpItem.model_validate(resp)

    def update(self, data: ioa_network_element.CidPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CidPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CidPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = CidPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CidPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CidPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CidPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = CidPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CidPtpListNode(ListNode[CidPtpItemNode]):
    """Navigator for list cid-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CidPtpItem]:
        from ..data_models.ioa_network_element import CidPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CidPtpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CidPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CidPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OpticalPtpItemNode(ItemNode):
    """Navigator for list item optical-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OpticalPtpItem:
        from ..data_models.ioa_network_element import OpticalPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalPtpItem.model_validate(resp)

    def update(self, data: ioa_network_element.OpticalPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OpticalPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OpticalPtpListNode(ListNode[OpticalPtpItemNode]):
    """Navigator for list optical-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OpticalPtpItem]:
        from ..data_models.ioa_network_element import OpticalPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpticalPtpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OpticalPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OpticalPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class MonitoredChannelItemNode(ItemNode):
    """Navigator for list item monitored-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.MonitoredChannelItem:
        from ..data_models.ioa_network_element import MonitoredChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return MonitoredChannelItem.model_validate(resp)

    def update(self, data: ioa_network_element.MonitoredChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import MonitoredChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MonitoredChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = MonitoredChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.MonitoredChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import MonitoredChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = MonitoredChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = MonitoredChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class MonitoredChannelListNode(ListNode[MonitoredChannelItemNode]):
    """Navigator for list monitored-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.MonitoredChannelItem]:
        from ..data_models.ioa_network_element import MonitoredChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [MonitoredChannelItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.MonitoredChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.MonitoredChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OcmPtpItemNode(ItemNode):
    """Navigator for list item ocm-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OcmPtpItem:
        from ..data_models.ioa_network_element import OcmPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcmPtpItem.model_validate(resp)

    def update(self, data: ioa_network_element.OcmPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcmPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = OcmPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OcmPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcmPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = OcmPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def monitored_channel(self) -> MonitoredChannelListNode:
        return MonitoredChannelListNode(
            self._client, f"{self._path}/monitored-channel", "monitored-channel", MonitoredChannelItemNode
        )


class OcmPtpListNode(ListNode[OcmPtpItemNode]):
    """Navigator for list ocm-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OcmPtpItem]:
        from ..data_models.ioa_network_element import OcmPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OcmPtpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OcmPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OcmPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OcmChannelItemNode(ItemNode):
    """Navigator for list item ocm-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OcmChannelItem:
        from ..data_models.ioa_network_element import OcmChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcmChannelItem.model_validate(resp)

    def update(self, data: ioa_network_element.OcmChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcmChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = OcmChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OcmChannelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcmChannelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmChannelItem.model_validate(data)
        elif isinstance(data, str):
            data = OcmChannelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OcmChannelListNode(ListNode[OcmChannelItemNode]):
    """Navigator for list ocm-channel"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OcmChannelItem]:
        from ..data_models.ioa_network_element import OcmChannelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OcmChannelItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OcmChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OcmChannelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OcmMpItemNode(ItemNode):
    """Navigator for list item ocm-mp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OcmMpItem:
        from ..data_models.ioa_network_element import OcmMpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcmMpItem.model_validate(resp)

    def update(self, data: ioa_network_element.OcmMpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcmMpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmMpItem.model_validate(data)
        elif isinstance(data, str):
            data = OcmMpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OcmMpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcmMpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcmMpItem.model_validate(data)
        elif isinstance(data, str):
            data = OcmMpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ocm_channel(self) -> OcmChannelListNode:
        return OcmChannelListNode(self._client, f"{self._path}/ocm-channel", "ocm-channel", OcmChannelItemNode)


class OcmMpListNode(ListNode[OcmMpItemNode]):
    """Navigator for list ocm-mp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OcmMpItem]:
        from ..data_models.ioa_network_element import OcmMpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OcmMpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OcmMpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OcmMpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OtdrPtpItemNode(ItemNode):
    """Navigator for list item otdr-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtdrPtpItem:
        from ..data_models.ioa_network_element import OtdrPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtdrPtpItem.model_validate(resp)

    def update(self, data: ioa_network_element.OtdrPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtdrPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtdrPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = OtdrPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OtdrPtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtdrPtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtdrPtpItem.model_validate(data)
        elif isinstance(data, str):
            data = OtdrPtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OtdrPtpListNode(ListNode[OtdrPtpItemNode]):
    """Navigator for list otdr-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OtdrPtpItem]:
        from ..data_models.ioa_network_element import OtdrPtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtdrPtpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OtdrPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OtdrPtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LinePtpItemNode(ItemNode):
    """Navigator for list item line-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LinePtpItem:
        from ..data_models.ioa_network_element import LinePtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LinePtpItem.model_validate(resp)

    def update(self, data: ioa_network_element.LinePtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LinePtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LinePtpItem.model_validate(data)
        elif isinstance(data, str):
            data = LinePtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.LinePtpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LinePtpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LinePtpItem.model_validate(data)
        elif isinstance(data, str):
            data = LinePtpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LinePtpListNode(ListNode[LinePtpItemNode]):
    """Navigator for list line-ptp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LinePtpItem]:
        from ..data_models.ioa_network_element import LinePtpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LinePtpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LinePtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LinePtpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FlexoItemNode(ItemNode):
    """Navigator for list item flexo"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FlexoItem:
        from ..data_models.ioa_network_element import FlexoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FlexoItem.model_validate(resp)

    def update(self, data: ioa_network_element.FlexoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FlexoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FlexoItem.model_validate(data)
        elif isinstance(data, str):
            data = FlexoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.FlexoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FlexoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FlexoItem.model_validate(data)
        elif isinstance(data, str):
            data = FlexoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FlexoListNode(ListNode[FlexoItemNode]):
    """Navigator for list flexo"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.FlexoItem]:
        from ..data_models.ioa_network_element import FlexoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FlexoItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.FlexoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.FlexoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FlexoGroupItemNode(ItemNode):
    """Navigator for list item flexo-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FlexoGroupItem:
        from ..data_models.ioa_network_element import FlexoGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FlexoGroupItem.model_validate(resp)

    def update(self, data: ioa_network_element.FlexoGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FlexoGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FlexoGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = FlexoGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.FlexoGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FlexoGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FlexoGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = FlexoGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FlexoGroupListNode(ListNode[FlexoGroupItemNode]):
    """Navigator for list flexo-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.FlexoGroupItem]:
        from ..data_models.ioa_network_element import FlexoGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FlexoGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.FlexoGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.FlexoGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DscItemNode(ItemNode):
    """Navigator for list item dsc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DscItem:
        from ..data_models.ioa_network_element import DscItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DscItem.model_validate(resp)

    def update(self, data: ioa_network_element.DscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DscItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DscItem.model_validate(data)
        elif isinstance(data, str):
            data = DscItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.DscItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DscItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DscItem.model_validate(data)
        elif isinstance(data, str):
            data = DscItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DscListNode(ListNode[DscItemNode]):
    """Navigator for list dsc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DscItem]:
        from ..data_models.ioa_network_element import DscItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DscItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DscItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DscGroupItemNode(ItemNode):
    """Navigator for list item dsc-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DscGroupItem:
        from ..data_models.ioa_network_element import DscGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DscGroupItem.model_validate(resp)

    def update(self, data: ioa_network_element.DscGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DscGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DscGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = DscGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.DscGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DscGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DscGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = DscGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DscGroupListNode(ListNode[DscGroupItemNode]):
    """Navigator for list dsc-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DscGroupItem]:
        from ..data_models.ioa_network_element import DscGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DscGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DscGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DscGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EthZrItemNode(ItemNode):
    """Navigator for list item eth-zr"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.EthZrItem:
        from ..data_models.ioa_network_element import EthZrItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EthZrItem.model_validate(resp)

    def update(self, data: ioa_network_element.EthZrItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EthZrItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EthZrItem.model_validate(data)
        elif isinstance(data, str):
            data = EthZrItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.EthZrItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EthZrItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EthZrItem.model_validate(data)
        elif isinstance(data, str):
            data = EthZrItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class EthZrListNode(ListNode[EthZrItemNode]):
    """Navigator for list eth-zr"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.EthZrItem]:
        from ..data_models.ioa_network_element import EthZrItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [EthZrItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.EthZrItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.EthZrItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OcItemNode(ItemNode):
    """Navigator for list item oc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OcItem:
        from ..data_models.ioa_network_element import OcItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcItem.model_validate(resp)

    def update(self, data: ioa_network_element.OcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcItem.model_validate(data)
        elif isinstance(data, str):
            data = OcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcItem.model_validate(data)
        elif isinstance(data, str):
            data = OcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OcListNode(ListNode[OcItemNode]):
    """Navigator for list oc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OcItem]:
        from ..data_models.ioa_network_element import OcItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OcItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class StmItemNode(ItemNode):
    """Navigator for list item stm"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.StmItem:
        from ..data_models.ioa_network_element import StmItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return StmItem.model_validate(resp)

    def update(self, data: ioa_network_element.StmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import StmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StmItem.model_validate(data)
        elif isinstance(data, str):
            data = StmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.StmItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import StmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = StmItem.model_validate(data)
        elif isinstance(data, str):
            data = StmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class StmListNode(ListNode[StmItemNode]):
    """Navigator for list stm"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.StmItem]:
        from ..data_models.ioa_network_element import StmItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [StmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.StmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.StmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FcItemNode(ItemNode):
    """Navigator for list item fc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FcItem:
        from ..data_models.ioa_network_element import FcItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FcItem.model_validate(resp)

    def update(self, data: ioa_network_element.FcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FcItem.model_validate(data)
        elif isinstance(data, str):
            data = FcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.FcItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FcItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FcItem.model_validate(data)
        elif isinstance(data, str):
            data = FcItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FcListNode(ListNode[FcItemNode]):
    """Navigator for list fc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.FcItem]:
        from ..data_models.ioa_network_element import FcItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FcItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.FcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.FcItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class InterlakenItemNode(ItemNode):
    """Navigator for list item interlaken"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.InterlakenItem:
        from ..data_models.ioa_network_element import InterlakenItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InterlakenItem.model_validate(resp)

    def update(self, data: ioa_network_element.InterlakenItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InterlakenItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InterlakenItem.model_validate(data)
        elif isinstance(data, str):
            data = InterlakenItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.InterlakenItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InterlakenItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InterlakenItem.model_validate(data)
        elif isinstance(data, str):
            data = InterlakenItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class InterlakenListNode(ListNode[InterlakenItemNode]):
    """Navigator for list interlaken"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.InterlakenItem]:
        from ..data_models.ioa_network_element import InterlakenItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InterlakenItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.InterlakenItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.InterlakenItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class McFItemNode(ItemNode):
    """Navigator for list item mc-f"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.McFItem:
        from ..data_models.ioa_network_element import McFItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return McFItem.model_validate(resp)

    def update(self, data: ioa_network_element.McFItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import McFItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = McFItem.model_validate(data)
        elif isinstance(data, str):
            data = McFItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.McFItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import McFItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = McFItem.model_validate(data)
        elif isinstance(data, str):
            data = McFItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class McFListNode(ListNode[McFItemNode]):
    """Navigator for list mc-f"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.McFItem]:
        from ..data_models.ioa_network_element import McFItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [McFItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.McFItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.McFItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NmcFItemNode(ItemNode):
    """Navigator for list item nmc-f"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NmcFItem:
        from ..data_models.ioa_network_element import NmcFItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NmcFItem.model_validate(resp)

    def update(self, data: ioa_network_element.NmcFItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NmcFItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcFItem.model_validate(data)
        elif isinstance(data, str):
            data = NmcFItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.NmcFItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NmcFItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NmcFItem.model_validate(data)
        elif isinstance(data, str):
            data = NmcFItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NmcFListNode(ListNode[NmcFItemNode]):
    """Navigator for list nmc-f"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NmcFItem]:
        from ..data_models.ioa_network_element import NmcFItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NmcFItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NmcFItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NmcFItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FacilitiesNode(Node):
    """Navigator for facilities"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Facilities:
        from ..data_models.ioa_network_element import Facilities

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Facilities.model_validate(resp)

    def update(self, data: ioa_network_element.Facilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Facilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Facilities.model_validate(data)
        elif isinstance(data, str):
            data = Facilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Facilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Facilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Facilities.model_validate(data)
        elif isinstance(data, str):
            data = Facilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ots(self) -> OtsListNode:
        return OtsListNode(self._client, f"{self._path}/ots", "ots", OtsItemNode)

    @property
    def ots_r(self) -> OtsRListNode:
        return OtsRListNode(self._client, f"{self._path}/ots-r", "ots-r", OtsRItemNode)

    @property
    def osc(self) -> OscListNode:
        return OscListNode(self._client, f"{self._path}/osc", "osc", OscItemNode)

    @property
    def ops(self) -> OpsListNode:
        return OpsListNode(self._client, f"{self._path}/ops", "ops", OpsItemNode)

    @property
    def oms(self) -> OmsListNode:
        return OmsListNode(self._client, f"{self._path}/oms", "oms", OmsItemNode)

    @property
    def spectrum(self) -> SpectrumListNode:
        return SpectrumListNode(self._client, f"{self._path}/spectrum", "spectrum", SpectrumItemNode)

    @property
    def ochm(self) -> OchmListNode:
        return OchmListNode(self._client, f"{self._path}/ochm", "ochm", OchmItemNode)

    @property
    def mc(self) -> McListNode:
        return McListNode(self._client, f"{self._path}/mc", "mc", McItemNode)

    @property
    def nmc(self) -> NmcListNode:
        return NmcListNode(self._client, f"{self._path}/nmc", "nmc", NmcItemNode)

    @property
    def rsc(self) -> RscListNode:
        return RscListNode(self._client, f"{self._path}/rsc", "rsc", RscItemNode)

    @property
    def pump(self) -> PumpListNode:
        return PumpListNode(self._client, f"{self._path}/pump", "pump", PumpItemNode)

    @property
    def super_channel_group(self) -> SuperChannelGroupListNode:
        return SuperChannelGroupListNode(
            self._client, f"{self._path}/super-channel-group", "super-channel-group", SuperChannelGroupItemNode
        )

    @property
    def super_channel(self) -> SuperChannelListNode:
        return SuperChannelListNode(self._client, f"{self._path}/super-channel", "super-channel", SuperChannelItemNode)

    @property
    def optical_carrier(self) -> OpticalCarrierListNode:
        return OpticalCarrierListNode(
            self._client, f"{self._path}/optical-carrier", "optical-carrier", OpticalCarrierItemNode
        )

    @property
    def optical_channel(self) -> OpticalChannelListNode:
        return OpticalChannelListNode(
            self._client, f"{self._path}/optical-channel", "optical-channel", OpticalChannelItemNode
        )

    @property
    def otu(self) -> OtuListNode:
        return OtuListNode(self._client, f"{self._path}/otu", "otu", OtuItemNode)

    @property
    def odu(self) -> OduListNode:
        return OduListNode(self._client, f"{self._path}/odu", "odu", OduItemNode)

    @property
    def ethernet(self) -> EthernetListNode:
        return EthernetListNode(self._client, f"{self._path}/ethernet", "ethernet", EthernetItemNode)

    @property
    def trib_ptp(self) -> TribPtpListNode:
        return TribPtpListNode(self._client, f"{self._path}/trib-ptp", "trib-ptp", TribPtpItemNode)

    @property
    def comm_channel(self) -> CommChannelListNode:
        return CommChannelListNode(self._client, f"{self._path}/comm-channel", "comm-channel", CommChannelItemNode)

    @property
    def cid_ptp(self) -> CidPtpListNode:
        return CidPtpListNode(self._client, f"{self._path}/cid-ptp", "cid-ptp", CidPtpItemNode)

    @property
    def optical_ptp(self) -> OpticalPtpListNode:
        return OpticalPtpListNode(self._client, f"{self._path}/optical-ptp", "optical-ptp", OpticalPtpItemNode)

    @property
    def ocm_ptp(self) -> OcmPtpListNode:
        return OcmPtpListNode(self._client, f"{self._path}/ocm-ptp", "ocm-ptp", OcmPtpItemNode)

    @property
    def ocm_mp(self) -> OcmMpListNode:
        return OcmMpListNode(self._client, f"{self._path}/ocm-mp", "ocm-mp", OcmMpItemNode)

    @property
    def otdr_ptp(self) -> OtdrPtpListNode:
        return OtdrPtpListNode(self._client, f"{self._path}/otdr-ptp", "otdr-ptp", OtdrPtpItemNode)

    @property
    def line_ptp(self) -> LinePtpListNode:
        return LinePtpListNode(self._client, f"{self._path}/line-ptp", "line-ptp", LinePtpItemNode)

    @property
    def flexo(self) -> FlexoListNode:
        return FlexoListNode(self._client, f"{self._path}/flexo", "flexo", FlexoItemNode)

    @property
    def flexo_group(self) -> FlexoGroupListNode:
        return FlexoGroupListNode(self._client, f"{self._path}/flexo-group", "flexo-group", FlexoGroupItemNode)

    @property
    def dsc(self) -> DscListNode:
        return DscListNode(self._client, f"{self._path}/dsc", "dsc", DscItemNode)

    @property
    def dsc_group(self) -> DscGroupListNode:
        return DscGroupListNode(self._client, f"{self._path}/dsc-group", "dsc-group", DscGroupItemNode)

    @property
    def eth_zr(self) -> EthZrListNode:
        return EthZrListNode(self._client, f"{self._path}/eth-zr", "eth-zr", EthZrItemNode)

    @property
    def oc(self) -> OcListNode:
        return OcListNode(self._client, f"{self._path}/oc", "oc", OcItemNode)

    @property
    def stm(self) -> StmListNode:
        return StmListNode(self._client, f"{self._path}/stm", "stm", StmItemNode)

    @property
    def fc(self) -> FcListNode:
        return FcListNode(self._client, f"{self._path}/fc", "fc", FcItemNode)

    @property
    def interlaken(self) -> InterlakenListNode:
        return InterlakenListNode(self._client, f"{self._path}/interlaken", "interlaken", InterlakenItemNode)

    @property
    def mc_f(self) -> McFListNode:
        return McFListNode(self._client, f"{self._path}/mc-f", "mc-f", McFItemNode)

    @property
    def nmc_f(self) -> NmcFListNode:
        return NmcFListNode(self._client, f"{self._path}/nmc-f", "nmc-f", NmcFItemNode)


class XconItemNode(ItemNode):
    """Navigator for list item xcon"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.XconItem:
        from ..data_models.ioa_network_element import XconItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return XconItem.model_validate(resp)

    def update(self, data: ioa_network_element.XconItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import XconItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = XconItem.model_validate(data)
        elif isinstance(data, str):
            data = XconItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.XconItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import XconItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = XconItem.model_validate(data)
        elif isinstance(data, str):
            data = XconItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class XconListNode(ListNode[XconItemNode]):
    """Navigator for list xcon"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.XconItem]:
        from ..data_models.ioa_network_element import XconItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [XconItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.XconItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.XconItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OxconItemNode(ItemNode):
    """Navigator for list item oxcon"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OxconItem:
        from ..data_models.ioa_network_element import OxconItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OxconItem.model_validate(resp)

    def update(self, data: ioa_network_element.OxconItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OxconItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OxconItem.model_validate(data)
        elif isinstance(data, str):
            data = OxconItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OxconItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OxconItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OxconItem.model_validate(data)
        elif isinstance(data, str):
            data = OxconItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OxconListNode(ListNode[OxconItemNode]):
    """Navigator for list oxcon"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OxconItem]:
        from ..data_models.ioa_network_element import OxconItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OxconItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OxconItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OxconItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SecureEntitySaProposalItemNode(ItemNode):
    """Navigator for list item secure-entity-sa-proposal"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SecureEntitySaProposalItem:
        from ..data_models.ioa_network_element import SecureEntitySaProposalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SecureEntitySaProposalItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SecureEntitySaProposalItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SecureEntitySaProposalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureEntitySaProposalItem.model_validate(data)
        elif isinstance(data, str):
            data = SecureEntitySaProposalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SecureEntitySaProposalItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SecureEntitySaProposalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureEntitySaProposalItem.model_validate(data)
        elif isinstance(data, str):
            data = SecureEntitySaProposalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SecureEntitySaProposalListNode(ListNode[SecureEntitySaProposalItemNode]):
    """Navigator for list secure-entity-sa-proposal"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SecureEntitySaProposalItem]:
        from ..data_models.ioa_network_element import SecureEntitySaProposalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SecureEntitySaProposalItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SecureEntitySaProposalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SecureEntitySaProposalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SecureEntityItemNode(ItemNode):
    """Navigator for list item secure-entity"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SecureEntityItem:
        from ..data_models.ioa_network_element import SecureEntityItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SecureEntityItem.model_validate(resp)

    def update(self, data: ioa_network_element.SecureEntityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecureEntityItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureEntityItem.model_validate(data)
        elif isinstance(data, str):
            data = SecureEntityItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SecureEntityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecureEntityItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureEntityItem.model_validate(data)
        elif isinstance(data, str):
            data = SecureEntityItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def secure_entity_sa_proposal(self) -> SecureEntitySaProposalListNode:
        return SecureEntitySaProposalListNode(
            self._client,
            f"{self._path}/secure-entity-sa-proposal",
            "secure-entity-sa-proposal",
            SecureEntitySaProposalItemNode,
        )


class SecureEntityListNode(ListNode[SecureEntityItemNode]):
    """Navigator for list secure-entity"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SecureEntityItem]:
        from ..data_models.ioa_network_element import SecureEntityItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SecureEntityItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SecureEntityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SecureEntityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DataPathEncryptionNode(Node):
    """Navigator for data-path-encryption"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DataPathEncryption:
        from ..data_models.ioa_network_element import DataPathEncryption

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DataPathEncryption.model_validate(resp)

    def update(self, data: ioa_network_element.DataPathEncryption | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DataPathEncryption

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DataPathEncryption.model_validate(data)
        elif isinstance(data, str):
            data = DataPathEncryption.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.DataPathEncryption | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DataPathEncryption

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DataPathEncryption.model_validate(data)
        elif isinstance(data, str):
            data = DataPathEncryption.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def secure_entity(self) -> SecureEntityListNode:
        return SecureEntityListNode(self._client, f"{self._path}/secure-entity", "secure-entity", SecureEntityItemNode)


class ServicesServicesNode(Node):
    """Navigator for services"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ServicesServices:
        from ..data_models.ioa_network_element import ServicesServices

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ServicesServices.model_validate(resp)

    def update(self, data: ioa_network_element.ServicesServices | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ServicesServices

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ServicesServices.model_validate(data)
        elif isinstance(data, str):
            data = ServicesServices.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.ServicesServices | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ServicesServices

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ServicesServices.model_validate(data)
        elif isinstance(data, str):
            data = ServicesServices.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def xcon(self) -> XconListNode:
        return XconListNode(self._client, f"{self._path}/xcon", "xcon", XconItemNode)

    @property
    def oxcon(self) -> OxconListNode:
        return OxconListNode(self._client, f"{self._path}/oxcon", "oxcon", OxconItemNode)

    @property
    def data_path_encryption(self) -> DataPathEncryptionNode:
        return DataPathEncryptionNode(self._client, f"{self._path}/data-path-encryption", "data-path-encryption")


class SecurityPoliciesNode(Node):
    """Navigator for security-policies"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SecurityPolicies:
        from ..data_models.ioa_network_element import SecurityPolicies

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SecurityPolicies.model_validate(resp)

    def update(self, data: ioa_network_element.SecurityPolicies | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecurityPolicies

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecurityPolicies.model_validate(data)
        elif isinstance(data, str):
            data = SecurityPolicies.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.SecurityPolicies | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecurityPolicies

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecurityPolicies.model_validate(data)
        elif isinstance(data, str):
            data = SecurityPolicies.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class AccessRuleItemNode(ItemNode):
    """Navigator for list item access-rule"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AccessRuleItem:
        from ..data_models.ioa_network_element import AccessRuleItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AccessRuleItem.model_validate(resp)

    def update(self, data: ioa_network_element.AccessRuleItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AccessRuleItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AccessRuleItem.model_validate(data)
        elif isinstance(data, str):
            data = AccessRuleItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AccessRuleItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AccessRuleItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AccessRuleItem.model_validate(data)
        elif isinstance(data, str):
            data = AccessRuleItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AccessRuleListNode(ListNode[AccessRuleItemNode]):
    """Navigator for list access-rule"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AccessRuleItem]:
        from ..data_models.ioa_network_element import AccessRuleItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AccessRuleItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AccessRuleItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AccessRuleItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AccessRuleListItemNode(ItemNode):
    """Navigator for list item access-rule-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AccessRuleListItem:
        from ..data_models.ioa_network_element import AccessRuleListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AccessRuleListItem.model_validate(resp)

    def update(self, data: ioa_network_element.AccessRuleListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AccessRuleListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AccessRuleListItem.model_validate(data)
        elif isinstance(data, str):
            data = AccessRuleListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AccessRuleListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AccessRuleListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AccessRuleListItem.model_validate(data)
        elif isinstance(data, str):
            data = AccessRuleListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def access_rule(self) -> AccessRuleListNode:
        return AccessRuleListNode(self._client, f"{self._path}/access-rule", "access-rule", AccessRuleItemNode)


class AccessRuleListListNode(ListNode[AccessRuleListItemNode]):
    """Navigator for list access-rule-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AccessRuleListItem]:
        from ..data_models.ioa_network_element import AccessRuleListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AccessRuleListItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AccessRuleListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AccessRuleListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AuthorizationNode(Node):
    """Navigator for authorization"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Authorization:
        from ..data_models.ioa_network_element import Authorization

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Authorization.model_validate(resp)

    def update(self, data: ioa_network_element.Authorization | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Authorization

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Authorization.model_validate(data)
        elif isinstance(data, str):
            data = Authorization.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Authorization | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Authorization

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Authorization.model_validate(data)
        elif isinstance(data, str):
            data = Authorization.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def access_rule_list(self) -> AccessRuleListListNode:
        return AccessRuleListListNode(
            self._client, f"{self._path}/access-rule-list", "access-rule-list", AccessRuleListItemNode
        )


class UserItemNode(ItemNode):
    """Navigator for list item user"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.UserItem:
        from ..data_models.ioa_network_element import UserItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return UserItem.model_validate(resp)

    def update(self, data: ioa_network_element.UserItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import UserItem

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

    def replace(self, data: ioa_network_element.UserItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import UserItem

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


class UserListNode(ListNode[UserItemNode]):
    """Navigator for list user"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.UserItem]:
        from ..data_models.ioa_network_element import UserItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [UserItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.UserItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.UserItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class UserGroupItemNode(ItemNode):
    """Navigator for list item user-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.UserGroupItem:
        from ..data_models.ioa_network_element import UserGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return UserGroupItem.model_validate(resp)

    def update(self, data: ioa_network_element.UserGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import UserGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UserGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = UserGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.UserGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import UserGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UserGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = UserGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class UserGroupListNode(ListNode[UserGroupItemNode]):
    """Navigator for list user-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.UserGroupItem]:
        from ..data_models.ioa_network_element import UserGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [UserGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.UserGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.UserGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SessionItemNode(ItemNode):
    """Navigator for list item session"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SessionItem:
        from ..data_models.ioa_network_element import SessionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SessionItem.model_validate(resp)

    def update(self, data: ioa_network_element.SessionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SessionItem

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

    def replace(self, data: ioa_network_element.SessionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SessionItem

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


class SessionListNode(ListNode[SessionItemNode]):
    """Navigator for list session"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SessionItem]:
        from ..data_models.ioa_network_element import SessionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SessionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SessionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SessionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AaaServerItemNode(ItemNode):
    """Navigator for list item aaa-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AaaServerItem:
        from ..data_models.ioa_network_element import AaaServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AaaServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.AaaServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AaaServerItem

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

    def replace(self, data: ioa_network_element.AaaServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AaaServerItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AaaServerItem]:
        from ..data_models.ioa_network_element import AaaServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AaaServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AaaServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AaaServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NiapNode(Node):
    """Navigator for niap"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Niap:
        from ..data_models.ioa_network_element import Niap

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Niap.model_validate(resp)

    def update(self, data: ioa_network_element.Niap | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Niap

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Niap.model_validate(data)
        elif isinstance(data, str):
            data = Niap.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Niap | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Niap

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Niap.model_validate(data)
        elif isinstance(data, str):
            data = Niap.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class DbProtectionSchemeNode(Node):
    """Navigator for db-protection-scheme"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DbProtectionScheme:
        from ..data_models.ioa_network_element import DbProtectionScheme

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DbProtectionScheme.model_validate(resp)

    def update(self, data: ioa_network_element.DbProtectionScheme | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DbProtectionScheme

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DbProtectionScheme.model_validate(data)
        elif isinstance(data, str):
            data = DbProtectionScheme.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.DbProtectionScheme | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DbProtectionScheme

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DbProtectionScheme.model_validate(data)
        elif isinstance(data, str):
            data = DbProtectionScheme.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class IskItemNode(ItemNode):
    """Navigator for list item ISK"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IskItem:
        from ..data_models.ioa_network_element import IskItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IskItem.model_validate(resp)

    def update(self, data: ioa_network_element.IskItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IskItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IskItem.model_validate(data)
        elif isinstance(data, str):
            data = IskItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.IskItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IskItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IskItem.model_validate(data)
        elif isinstance(data, str):
            data = IskItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class IskListNode(ListNode[IskItemNode]):
    """Navigator for list ISK"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.IskItem]:
        from ..data_models.ioa_network_element import IskItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [IskItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.IskItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.IskItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IsksNode(Node):
    """Navigator for ISKs"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Isks:
        from ..data_models.ioa_network_element import Isks

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Isks.model_validate(resp)

    def update(self, data: ioa_network_element.Isks | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Isks

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Isks.model_validate(data)
        elif isinstance(data, str):
            data = Isks.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Isks | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Isks

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Isks.model_validate(data)
        elif isinstance(data, str):
            data = Isks.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ISK(self) -> IskListNode:
        return IskListNode(self._client, f"{self._path}/ISK", "ISK", IskItemNode)


class KrkItemNode(ItemNode):
    """Navigator for list item KRK"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.KrkItem:
        from ..data_models.ioa_network_element import KrkItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return KrkItem.model_validate(resp)

    def update(self, data: ioa_network_element.KrkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import KrkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KrkItem.model_validate(data)
        elif isinstance(data, str):
            data = KrkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.KrkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import KrkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KrkItem.model_validate(data)
        elif isinstance(data, str):
            data = KrkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class KrkListNode(ListNode[KrkItemNode]):
    """Navigator for list KRK"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.KrkItem]:
        from ..data_models.ioa_network_element import KrkItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [KrkItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.KrkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.KrkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class KrksNode(Node):
    """Navigator for KRKs"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Krks:
        from ..data_models.ioa_network_element import Krks

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Krks.model_validate(resp)

    def update(self, data: ioa_network_element.Krks | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Krks

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Krks.model_validate(data)
        elif isinstance(data, str):
            data = Krks.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Krks | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Krks

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Krks.model_validate(data)
        elif isinstance(data, str):
            data = Krks.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def KRK(self) -> KrkListNode:
        return KrkListNode(self._client, f"{self._path}/KRK", "KRK", KrkItemNode)


class ImageKeysNode(Node):
    """Navigator for image-keys"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ImageKeys:
        from ..data_models.ioa_network_element import ImageKeys

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ImageKeys.model_validate(resp)

    def update(self, data: ioa_network_element.ImageKeys | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ImageKeys

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ImageKeys.model_validate(data)
        elif isinstance(data, str):
            data = ImageKeys.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.ImageKeys | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ImageKeys

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ImageKeys.model_validate(data)
        elif isinstance(data, str):
            data = ImageKeys.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ISKs(self) -> IsksNode:
        return IsksNode(self._client, f"{self._path}/ISKs", "ISKs")

    @property
    def KRKs(self) -> KrksNode:
        return KrksNode(self._client, f"{self._path}/KRKs", "KRKs")


class KeyReplacementPackageNode(Node):
    """Navigator for key-replacement-package"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.KeyReplacementPackage:
        from ..data_models.ioa_network_element import KeyReplacementPackage

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return KeyReplacementPackage.model_validate(resp)

    def update(self, data: ioa_network_element.KeyReplacementPackage | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import KeyReplacementPackage

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KeyReplacementPackage.model_validate(data)
        elif isinstance(data, str):
            data = KeyReplacementPackage.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.KeyReplacementPackage | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import KeyReplacementPackage

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = KeyReplacementPackage.model_validate(data)
        elif isinstance(data, str):
            data = KeyReplacementPackage.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class TrustedCertificateItemNode(ItemNode):
    """Navigator for list item trusted-certificate"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TrustedCertificateItem:
        from ..data_models.ioa_network_element import TrustedCertificateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TrustedCertificateItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.TrustedCertificateItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import TrustedCertificateItem

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

    def replace(
        self, data: ioa_network_element.TrustedCertificateItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import TrustedCertificateItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TrustedCertificateItem]:
        from ..data_models.ioa_network_element import TrustedCertificateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TrustedCertificateItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TrustedCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TrustedCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LocalCertificateItemNode(ItemNode):
    """Navigator for list item local-certificate"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LocalCertificateItem:
        from ..data_models.ioa_network_element import LocalCertificateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LocalCertificateItem.model_validate(resp)

    def update(self, data: ioa_network_element.LocalCertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LocalCertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LocalCertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = LocalCertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.LocalCertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LocalCertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LocalCertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = LocalCertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LocalCertificateListNode(ListNode[LocalCertificateItemNode]):
    """Navigator for list local-certificate"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LocalCertificateItem]:
        from ..data_models.ioa_network_element import LocalCertificateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LocalCertificateItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LocalCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LocalCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class PeerCertificateItemNode(ItemNode):
    """Navigator for list item peer-certificate"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PeerCertificateItem:
        from ..data_models.ioa_network_element import PeerCertificateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PeerCertificateItem.model_validate(resp)

    def update(self, data: ioa_network_element.PeerCertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PeerCertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PeerCertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = PeerCertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.PeerCertificateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PeerCertificateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PeerCertificateItem.model_validate(data)
        elif isinstance(data, str):
            data = PeerCertificateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PeerCertificateListNode(ListNode[PeerCertificateItemNode]):
    """Navigator for list peer-certificate"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.PeerCertificateItem]:
        from ..data_models.ioa_network_element import PeerCertificateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PeerCertificateItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.PeerCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.PeerCertificateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SecureApplicationItemNode(ItemNode):
    """Navigator for list item secure-application"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SecureApplicationItem:
        from ..data_models.ioa_network_element import SecureApplicationItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SecureApplicationItem.model_validate(resp)

    def update(self, data: ioa_network_element.SecureApplicationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecureApplicationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureApplicationItem.model_validate(data)
        elif isinstance(data, str):
            data = SecureApplicationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SecureApplicationItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SecureApplicationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureApplicationItem.model_validate(data)
        elif isinstance(data, str):
            data = SecureApplicationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SecureApplicationListNode(ListNode[SecureApplicationItemNode]):
    """Navigator for list secure-application"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SecureApplicationItem]:
        from ..data_models.ioa_network_element import SecureApplicationItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SecureApplicationItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SecureApplicationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SecureApplicationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SecureApplicationsNode(Node):
    """Navigator for secure-applications"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SecureApplications:
        from ..data_models.ioa_network_element import SecureApplications

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SecureApplications.model_validate(resp)

    def update(self, data: ioa_network_element.SecureApplications | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecureApplications

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureApplications.model_validate(data)
        elif isinstance(data, str):
            data = SecureApplications.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.SecureApplications | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SecureApplications

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecureApplications.model_validate(data)
        elif isinstance(data, str):
            data = SecureApplications.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def secure_application(self) -> SecureApplicationListNode:
        return SecureApplicationListNode(
            self._client, f"{self._path}/secure-application", "secure-application", SecureApplicationItemNode
        )


class CrlItemNode(ItemNode):
    """Navigator for list item crl"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CrlItem:
        from ..data_models.ioa_network_element import CrlItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CrlItem.model_validate(resp)

    def update(self, data: ioa_network_element.CrlItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CrlItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CrlItem.model_validate(data)
        elif isinstance(data, str):
            data = CrlItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CrlItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CrlItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CrlItem.model_validate(data)
        elif isinstance(data, str):
            data = CrlItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CrlListNode(ListNode[CrlItemNode]):
    """Navigator for list crl"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CrlItem]:
        from ..data_models.ioa_network_element import CrlItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CrlItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CrlItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CrlItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CrlsNode(Node):
    """Navigator for crls"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Crls:
        from ..data_models.ioa_network_element import Crls

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Crls.model_validate(resp)

    def update(self, data: ioa_network_element.Crls | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Crls

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Crls.model_validate(data)
        elif isinstance(data, str):
            data = Crls.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Crls | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Crls

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Crls.model_validate(data)
        elif isinstance(data, str):
            data = Crls.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def crl(self) -> CrlListNode:
        return CrlListNode(self._client, f"{self._path}/crl", "crl", CrlItemNode)


class CdpItemNode(ItemNode):
    """Navigator for list item cdp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CdpItem:
        from ..data_models.ioa_network_element import CdpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CdpItem.model_validate(resp)

    def update(self, data: ioa_network_element.CdpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CdpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CdpItem.model_validate(data)
        elif isinstance(data, str):
            data = CdpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CdpItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CdpItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CdpItem.model_validate(data)
        elif isinstance(data, str):
            data = CdpItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CdpListNode(ListNode[CdpItemNode]):
    """Navigator for list cdp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CdpItem]:
        from ..data_models.ioa_network_element import CdpItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CdpItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CdpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CdpItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CdpsNode(Node):
    """Navigator for cdps"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Cdps:
        from ..data_models.ioa_network_element import Cdps

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Cdps.model_validate(resp)

    def update(self, data: ioa_network_element.Cdps | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Cdps

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Cdps.model_validate(data)
        elif isinstance(data, str):
            data = Cdps.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Cdps | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Cdps

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Cdps.model_validate(data)
        elif isinstance(data, str):
            data = Cdps.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def cdp(self) -> CdpListNode:
        return CdpListNode(self._client, f"{self._path}/cdp", "cdp", CdpItemNode)


class OcspServerItemNode(ItemNode):
    """Navigator for list item ocsp-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OcspServerItem:
        from ..data_models.ioa_network_element import OcspServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcspServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.OcspServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcspServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcspServerItem.model_validate(data)
        elif isinstance(data, str):
            data = OcspServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OcspServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcspServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcspServerItem.model_validate(data)
        elif isinstance(data, str):
            data = OcspServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OcspServerListNode(ListNode[OcspServerItemNode]):
    """Navigator for list ocsp-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OcspServerItem]:
        from ..data_models.ioa_network_element import OcspServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OcspServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OcspServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OcspServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OcspServersNode(Node):
    """Navigator for ocsp-servers"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OcspServers:
        from ..data_models.ioa_network_element import OcspServers

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OcspServers.model_validate(resp)

    def update(self, data: ioa_network_element.OcspServers | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcspServers

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcspServers.model_validate(data)
        elif isinstance(data, str):
            data = OcspServers.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.OcspServers | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OcspServers

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OcspServers.model_validate(data)
        elif isinstance(data, str):
            data = OcspServers.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ocsp_server(self) -> OcspServerListNode:
        return OcspServerListNode(self._client, f"{self._path}/ocsp-server", "ocsp-server", OcspServerItemNode)


class CertificateRevocationNode(Node):
    """Navigator for certificate-revocation"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CertificateRevocation:
        from ..data_models.ioa_network_element import CertificateRevocation

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CertificateRevocation.model_validate(resp)

    def update(self, data: ioa_network_element.CertificateRevocation | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CertificateRevocation

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CertificateRevocation.model_validate(data)
        elif isinstance(data, str):
            data = CertificateRevocation.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.CertificateRevocation | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import CertificateRevocation

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CertificateRevocation.model_validate(data)
        elif isinstance(data, str):
            data = CertificateRevocation.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def crls(self) -> CrlsNode:
        return CrlsNode(self._client, f"{self._path}/crls", "crls")

    @property
    def cdps(self) -> CdpsNode:
        return CdpsNode(self._client, f"{self._path}/cdps", "cdps")

    @property
    def ocsp_servers(self) -> OcspServersNode:
        return OcspServersNode(self._client, f"{self._path}/ocsp-servers", "ocsp-servers")


class CertificatesNode(Node):
    """Navigator for certificates"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Certificates:
        from ..data_models.ioa_network_element import Certificates

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Certificates.model_validate(resp)

    def update(self, data: ioa_network_element.Certificates | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Certificates

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Certificates.model_validate(data)
        elif isinstance(data, str):
            data = Certificates.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Certificates | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Certificates

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Certificates.model_validate(data)
        elif isinstance(data, str):
            data = Certificates.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def trusted_certificate(self) -> TrustedCertificateListNode:
        return TrustedCertificateListNode(
            self._client, f"{self._path}/trusted-certificate", "trusted-certificate", TrustedCertificateItemNode
        )

    @property
    def local_certificate(self) -> LocalCertificateListNode:
        return LocalCertificateListNode(
            self._client, f"{self._path}/local-certificate", "local-certificate", LocalCertificateItemNode
        )

    @property
    def peer_certificate(self) -> PeerCertificateListNode:
        return PeerCertificateListNode(
            self._client, f"{self._path}/peer-certificate", "peer-certificate", PeerCertificateItemNode
        )

    @property
    def secure_applications(self) -> SecureApplicationsNode:
        return SecureApplicationsNode(self._client, f"{self._path}/secure-applications", "secure-applications")

    @property
    def certificate_revocation(self) -> CertificateRevocationNode:
        return CertificateRevocationNode(self._client, f"{self._path}/certificate-revocation", "certificate-revocation")


class Ipv4EndpointsItemNode(ItemNode):
    """Navigator for list item ipv4-endpoints"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ipv4EndpointsItem:
        from ..data_models.ioa_network_element import Ipv4EndpointsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv4EndpointsItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ipv4EndpointsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv4EndpointsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4EndpointsItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4EndpointsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ipv4EndpointsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv4EndpointsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4EndpointsItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4EndpointsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Ipv4EndpointsListNode(ListNode[Ipv4EndpointsItemNode]):
    """Navigator for list ipv4-endpoints"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ipv4EndpointsItem]:
        from ..data_models.ioa_network_element import Ipv4EndpointsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv4EndpointsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ipv4EndpointsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ipv4EndpointsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class Ipv6EndpointsItemNode(ItemNode):
    """Navigator for list item ipv6-endpoints"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ipv6EndpointsItem:
        from ..data_models.ioa_network_element import Ipv6EndpointsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv6EndpointsItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ipv6EndpointsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv6EndpointsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6EndpointsItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6EndpointsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ipv6EndpointsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv6EndpointsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6EndpointsItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6EndpointsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Ipv6EndpointsListNode(ListNode[Ipv6EndpointsItemNode]):
    """Navigator for list ipv6-endpoints"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ipv6EndpointsItem]:
        from ..data_models.ioa_network_element import Ipv6EndpointsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv6EndpointsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ipv6EndpointsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ipv6EndpointsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SupportingInterfaceItemNode(ItemNode):
    """Navigator for list item supporting-interface"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportingInterfaceItem:
        from ..data_models.ioa_network_element import SupportingInterfaceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportingInterfaceItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SupportingInterfaceItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportingInterfaceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportingInterfaceItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportingInterfaceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SupportingInterfaceItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportingInterfaceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportingInterfaceItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportingInterfaceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ipv4_endpoints(self) -> Ipv4EndpointsListNode:
        return Ipv4EndpointsListNode(
            self._client, f"{self._path}/ipv4-endpoints", "ipv4-endpoints", Ipv4EndpointsItemNode
        )

    @property
    def ipv6_endpoints(self) -> Ipv6EndpointsListNode:
        return Ipv6EndpointsListNode(
            self._client, f"{self._path}/ipv6-endpoints", "ipv6-endpoints", Ipv6EndpointsItemNode
        )


class SupportingInterfaceListNode(ListNode[SupportingInterfaceItemNode]):
    """Navigator for list supporting-interface"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportingInterfaceItem]:
        from ..data_models.ioa_network_element import SupportingInterfaceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportingInterfaceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportingInterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportingInterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EncryptionAlgorithmItemNode(ItemNode):
    """Navigator for list item encryption-algorithm"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.EncryptionAlgorithmItem:
        from ..data_models.ioa_network_element import EncryptionAlgorithmItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EncryptionAlgorithmItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.EncryptionAlgorithmItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import EncryptionAlgorithmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EncryptionAlgorithmItem.model_validate(data)
        elif isinstance(data, str):
            data = EncryptionAlgorithmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.EncryptionAlgorithmItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import EncryptionAlgorithmItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EncryptionAlgorithmItem.model_validate(data)
        elif isinstance(data, str):
            data = EncryptionAlgorithmItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class EncryptionAlgorithmListNode(ListNode[EncryptionAlgorithmItemNode]):
    """Navigator for list encryption-algorithm"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.EncryptionAlgorithmItem]:
        from ..data_models.ioa_network_element import EncryptionAlgorithmItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [EncryptionAlgorithmItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.EncryptionAlgorithmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.EncryptionAlgorithmItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IkeSaProposalItemNode(ItemNode):
    """Navigator for list item ike-sa-proposal"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IkeSaProposalItem:
        from ..data_models.ioa_network_element import IkeSaProposalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IkeSaProposalItem.model_validate(resp)

    def update(self, data: ioa_network_element.IkeSaProposalItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IkeSaProposalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IkeSaProposalItem.model_validate(data)
        elif isinstance(data, str):
            data = IkeSaProposalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.IkeSaProposalItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IkeSaProposalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IkeSaProposalItem.model_validate(data)
        elif isinstance(data, str):
            data = IkeSaProposalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def encryption_algorithm(self) -> EncryptionAlgorithmListNode:
        return EncryptionAlgorithmListNode(
            self._client, f"{self._path}/encryption-algorithm", "encryption-algorithm", EncryptionAlgorithmItemNode
        )


class IkeSaProposalListNode(ListNode[IkeSaProposalItemNode]):
    """Navigator for list ike-sa-proposal"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.IkeSaProposalItem]:
        from ..data_models.ioa_network_element import IkeSaProposalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [IkeSaProposalItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.IkeSaProposalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.IkeSaProposalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LocalSubnetItemNode(ItemNode):
    """Navigator for list item local-subnet"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LocalSubnetItem:
        from ..data_models.ioa_network_element import LocalSubnetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LocalSubnetItem.model_validate(resp)

    def update(self, data: ioa_network_element.LocalSubnetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LocalSubnetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LocalSubnetItem.model_validate(data)
        elif isinstance(data, str):
            data = LocalSubnetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.LocalSubnetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LocalSubnetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LocalSubnetItem.model_validate(data)
        elif isinstance(data, str):
            data = LocalSubnetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LocalSubnetListNode(ListNode[LocalSubnetItemNode]):
    """Navigator for list local-subnet"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LocalSubnetItem]:
        from ..data_models.ioa_network_element import LocalSubnetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LocalSubnetItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LocalSubnetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LocalSubnetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class RemoteSubnetItemNode(ItemNode):
    """Navigator for list item remote-subnet"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.RemoteSubnetItem:
        from ..data_models.ioa_network_element import RemoteSubnetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RemoteSubnetItem.model_validate(resp)

    def update(self, data: ioa_network_element.RemoteSubnetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RemoteSubnetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RemoteSubnetItem.model_validate(data)
        elif isinstance(data, str):
            data = RemoteSubnetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.RemoteSubnetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RemoteSubnetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RemoteSubnetItem.model_validate(data)
        elif isinstance(data, str):
            data = RemoteSubnetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RemoteSubnetListNode(ListNode[RemoteSubnetItemNode]):
    """Navigator for list remote-subnet"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.RemoteSubnetItem]:
        from ..data_models.ioa_network_element import RemoteSubnetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RemoteSubnetItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.RemoteSubnetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.RemoteSubnetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LocalPortsItemNode(ItemNode):
    """Navigator for list item local-ports"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LocalPortsItem:
        from ..data_models.ioa_network_element import LocalPortsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LocalPortsItem.model_validate(resp)

    def update(self, data: ioa_network_element.LocalPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LocalPortsItem

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

    def replace(self, data: ioa_network_element.LocalPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LocalPortsItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LocalPortsItem]:
        from ..data_models.ioa_network_element import LocalPortsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LocalPortsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LocalPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LocalPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class RemotePortsItemNode(ItemNode):
    """Navigator for list item remote-ports"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.RemotePortsItem:
        from ..data_models.ioa_network_element import RemotePortsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RemotePortsItem.model_validate(resp)

    def update(self, data: ioa_network_element.RemotePortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RemotePortsItem

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

    def replace(self, data: ioa_network_element.RemotePortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RemotePortsItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.RemotePortsItem]:
        from ..data_models.ioa_network_element import RemotePortsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RemotePortsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.RemotePortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.RemotePortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IpsecTrafficSelectorItemNode(ItemNode):
    """Navigator for list item ipsec-traffic-selector"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IpsecTrafficSelectorItem:
        from ..data_models.ioa_network_element import IpsecTrafficSelectorItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpsecTrafficSelectorItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.IpsecTrafficSelectorItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import IpsecTrafficSelectorItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecTrafficSelectorItem.model_validate(data)
        elif isinstance(data, str):
            data = IpsecTrafficSelectorItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.IpsecTrafficSelectorItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import IpsecTrafficSelectorItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecTrafficSelectorItem.model_validate(data)
        elif isinstance(data, str):
            data = IpsecTrafficSelectorItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def local_subnet(self) -> LocalSubnetListNode:
        return LocalSubnetListNode(self._client, f"{self._path}/local-subnet", "local-subnet", LocalSubnetItemNode)

    @property
    def remote_subnet(self) -> RemoteSubnetListNode:
        return RemoteSubnetListNode(self._client, f"{self._path}/remote-subnet", "remote-subnet", RemoteSubnetItemNode)

    @property
    def local_ports(self) -> LocalPortsListNode:
        return LocalPortsListNode(self._client, f"{self._path}/local-ports", "local-ports", LocalPortsItemNode)

    @property
    def remote_ports(self) -> RemotePortsListNode:
        return RemotePortsListNode(self._client, f"{self._path}/remote-ports", "remote-ports", RemotePortsItemNode)


class IpsecTrafficSelectorListNode(ListNode[IpsecTrafficSelectorItemNode]):
    """Navigator for list ipsec-traffic-selector"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.IpsecTrafficSelectorItem]:
        from ..data_models.ioa_network_element import IpsecTrafficSelectorItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [IpsecTrafficSelectorItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.IpsecTrafficSelectorItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.IpsecTrafficSelectorItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IpsecSaReKeyNode(Node):
    """Navigator for ipsec-sa-re-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IpsecSaReKey:
        from ..data_models.ioa_network_element import IpsecSaReKey

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpsecSaReKey.model_validate(resp)

    def update(self, data: ioa_network_element.IpsecSaReKey | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpsecSaReKey

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSaReKey.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSaReKey.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.IpsecSaReKey | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpsecSaReKey

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSaReKey.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSaReKey.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class IpsecSaProposalItemNode(ItemNode):
    """Navigator for list item ipsec-sa-proposal"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IpsecSaProposalItem:
        from ..data_models.ioa_network_element import IpsecSaProposalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpsecSaProposalItem.model_validate(resp)

    def update(self, data: ioa_network_element.IpsecSaProposalItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpsecSaProposalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSaProposalItem.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSaProposalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.IpsecSaProposalItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpsecSaProposalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSaProposalItem.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSaProposalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def encryption_algorithm(self) -> EncryptionAlgorithmListNode:
        return EncryptionAlgorithmListNode(
            self._client, f"{self._path}/encryption-algorithm", "encryption-algorithm", EncryptionAlgorithmItemNode
        )


class IpsecSaProposalListNode(ListNode[IpsecSaProposalItemNode]):
    """Navigator for list ipsec-sa-proposal"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.IpsecSaProposalItem]:
        from ..data_models.ioa_network_element import IpsecSaProposalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [IpsecSaProposalItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.IpsecSaProposalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.IpsecSaProposalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IpsecSpdEntryItemNode(ItemNode):
    """Navigator for list item ipsec-spd-entry"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IpsecSpdEntryItem:
        from ..data_models.ioa_network_element import IpsecSpdEntryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpsecSpdEntryItem.model_validate(resp)

    def update(self, data: ioa_network_element.IpsecSpdEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpsecSpdEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSpdEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSpdEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.IpsecSpdEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpsecSpdEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpsecSpdEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = IpsecSpdEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ipsec_traffic_selector(self) -> IpsecTrafficSelectorListNode:
        return IpsecTrafficSelectorListNode(
            self._client, f"{self._path}/ipsec-traffic-selector", "ipsec-traffic-selector", IpsecTrafficSelectorItemNode
        )

    @property
    def ipsec_sa_re_key(self) -> IpsecSaReKeyNode:
        return IpsecSaReKeyNode(self._client, f"{self._path}/ipsec-sa-re-key", "ipsec-sa-re-key")

    @property
    def ipsec_sa_proposal(self) -> IpsecSaProposalListNode:
        return IpsecSaProposalListNode(
            self._client, f"{self._path}/ipsec-sa-proposal", "ipsec-sa-proposal", IpsecSaProposalItemNode
        )


class IpsecSpdEntryListNode(ListNode[IpsecSpdEntryItemNode]):
    """Navigator for list ipsec-spd-entry"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.IpsecSpdEntryItem]:
        from ..data_models.ioa_network_element import IpsecSpdEntryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [IpsecSpdEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.IpsecSpdEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.IpsecSpdEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SecurityPolicyDatabaseNode(Node):
    """Navigator for security-policy-database"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SecurityPolicyDatabase:
        from ..data_models.ioa_network_element import SecurityPolicyDatabase

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SecurityPolicyDatabase.model_validate(resp)

    def update(
        self, data: ioa_network_element.SecurityPolicyDatabase | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SecurityPolicyDatabase

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecurityPolicyDatabase.model_validate(data)
        elif isinstance(data, str):
            data = SecurityPolicyDatabase.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SecurityPolicyDatabase | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SecurityPolicyDatabase

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SecurityPolicyDatabase.model_validate(data)
        elif isinstance(data, str):
            data = SecurityPolicyDatabase.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ipsec_spd_entry(self) -> IpsecSpdEntryListNode:
        return IpsecSpdEntryListNode(
            self._client, f"{self._path}/ipsec-spd-entry", "ipsec-spd-entry", IpsecSpdEntryItemNode
        )


class Ikev2PeerItemNode(ItemNode):
    """Navigator for list item ikev2-peer"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ikev2PeerItem:
        from ..data_models.ioa_network_element import Ikev2PeerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ikev2PeerItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ikev2PeerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ikev2PeerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ikev2PeerItem.model_validate(data)
        elif isinstance(data, str):
            data = Ikev2PeerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ikev2PeerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ikev2PeerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ikev2PeerItem.model_validate(data)
        elif isinstance(data, str):
            data = Ikev2PeerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ike_sa_proposal(self) -> IkeSaProposalListNode:
        return IkeSaProposalListNode(
            self._client, f"{self._path}/ike-sa-proposal", "ike-sa-proposal", IkeSaProposalItemNode
        )

    @property
    def security_policy_database(self) -> SecurityPolicyDatabaseNode:
        return SecurityPolicyDatabaseNode(
            self._client, f"{self._path}/security-policy-database", "security-policy-database"
        )


class Ikev2PeerListNode(ListNode[Ikev2PeerItemNode]):
    """Navigator for list ikev2-peer"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ikev2PeerItem]:
        from ..data_models.ioa_network_element import Ikev2PeerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ikev2PeerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ikev2PeerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ikev2PeerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class PeerAuthorizationDatabaseNode(Node):
    """Navigator for peer-authorization-database"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PeerAuthorizationDatabase:
        from ..data_models.ioa_network_element import PeerAuthorizationDatabase

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PeerAuthorizationDatabase.model_validate(resp)

    def update(
        self, data: ioa_network_element.PeerAuthorizationDatabase | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import PeerAuthorizationDatabase

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PeerAuthorizationDatabase.model_validate(data)
        elif isinstance(data, str):
            data = PeerAuthorizationDatabase.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.PeerAuthorizationDatabase | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import PeerAuthorizationDatabase

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PeerAuthorizationDatabase.model_validate(data)
        elif isinstance(data, str):
            data = PeerAuthorizationDatabase.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ikev2_peer(self) -> Ikev2PeerListNode:
        return Ikev2PeerListNode(self._client, f"{self._path}/ikev2-peer", "ikev2-peer", Ikev2PeerItemNode)


class Ikev2LocalInstanceItemNode(ItemNode):
    """Navigator for list item ikev2-local-instance"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ikev2LocalInstanceItem:
        from ..data_models.ioa_network_element import Ikev2LocalInstanceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ikev2LocalInstanceItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.Ikev2LocalInstanceItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import Ikev2LocalInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ikev2LocalInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = Ikev2LocalInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.Ikev2LocalInstanceItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import Ikev2LocalInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ikev2LocalInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = Ikev2LocalInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def supporting_interface(self) -> SupportingInterfaceListNode:
        return SupportingInterfaceListNode(
            self._client, f"{self._path}/supporting-interface", "supporting-interface", SupportingInterfaceItemNode
        )

    @property
    def peer_authorization_database(self) -> PeerAuthorizationDatabaseNode:
        return PeerAuthorizationDatabaseNode(
            self._client, f"{self._path}/peer-authorization-database", "peer-authorization-database"
        )


class Ikev2LocalInstanceListNode(ListNode[Ikev2LocalInstanceItemNode]):
    """Navigator for list ikev2-local-instance"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ikev2LocalInstanceItem]:
        from ..data_models.ioa_network_element import Ikev2LocalInstanceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ikev2LocalInstanceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ikev2LocalInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ikev2LocalInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class Ikev2Node(Node):
    """Navigator for ikev2"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ikev2:
        from ..data_models.ioa_network_element import Ikev2

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ikev2.model_validate(resp)

    def update(self, data: ioa_network_element.Ikev2 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ikev2

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ikev2.model_validate(data)
        elif isinstance(data, str):
            data = Ikev2.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ikev2 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ikev2

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ikev2.model_validate(data)
        elif isinstance(data, str):
            data = Ikev2.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def ikev2_local_instance(self) -> Ikev2LocalInstanceListNode:
        return Ikev2LocalInstanceListNode(
            self._client, f"{self._path}/ikev2-local-instance", "ikev2-local-instance", Ikev2LocalInstanceItemNode
        )


class FipsNode(Node):
    """Navigator for fips"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Fips:
        from ..data_models.ioa_network_element import Fips

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Fips.model_validate(resp)

    def update(self, data: ioa_network_element.Fips | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Fips

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fips.model_validate(data)
        elif isinstance(data, str):
            data = Fips.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Fips | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Fips

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Fips.model_validate(data)
        elif isinstance(data, str):
            data = Fips.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SecurityNode(Node):
    """Navigator for security"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Security:
        from ..data_models.ioa_network_element import Security

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Security.model_validate(resp)

    def update(self, data: ioa_network_element.Security | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Security

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

    def replace(self, data: ioa_network_element.Security | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Security

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
    def security_policies(self) -> SecurityPoliciesNode:
        return SecurityPoliciesNode(self._client, f"{self._path}/security-policies", "security-policies")

    @property
    def authorization(self) -> AuthorizationNode:
        return AuthorizationNode(self._client, f"{self._path}/authorization", "authorization")

    @property
    def user(self) -> UserListNode:
        return UserListNode(self._client, f"{self._path}/user", "user", UserItemNode)

    @property
    def user_group(self) -> UserGroupListNode:
        return UserGroupListNode(self._client, f"{self._path}/user-group", "user-group", UserGroupItemNode)

    @property
    def session(self) -> SessionListNode:
        return SessionListNode(self._client, f"{self._path}/session", "session", SessionItemNode)

    @property
    def aaa_server(self) -> AaaServerListNode:
        return AaaServerListNode(self._client, f"{self._path}/aaa-server", "aaa-server", AaaServerItemNode)

    @property
    def niap(self) -> NiapNode:
        return NiapNode(self._client, f"{self._path}/niap", "niap")

    @property
    def db_protection_scheme(self) -> DbProtectionSchemeNode:
        return DbProtectionSchemeNode(self._client, f"{self._path}/db-protection-scheme", "db-protection-scheme")

    @property
    def image_keys(self) -> ImageKeysNode:
        return ImageKeysNode(self._client, f"{self._path}/image-keys", "image-keys")

    @property
    def key_replacement_package(self) -> KeyReplacementPackageNode:
        return KeyReplacementPackageNode(
            self._client, f"{self._path}/key-replacement-package", "key-replacement-package"
        )

    @property
    def certificates(self) -> CertificatesNode:
        return CertificatesNode(self._client, f"{self._path}/certificates", "certificates")

    @property
    def ikev2(self) -> Ikev2Node:
        return Ikev2Node(self._client, f"{self._path}/ikev2", "ikev2")

    @property
    def fips(self) -> FipsNode:
        return FipsNode(self._client, f"{self._path}/fips", "fips")


class LogServerFacilityFilterItemNode(ItemNode):
    """Navigator for list item log-server-facility-filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LogServerFacilityFilterItem:
        from ..data_models.ioa_network_element import LogServerFacilityFilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogServerFacilityFilterItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.LogServerFacilityFilterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LogServerFacilityFilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogServerFacilityFilterItem.model_validate(data)
        elif isinstance(data, str):
            data = LogServerFacilityFilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.LogServerFacilityFilterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LogServerFacilityFilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogServerFacilityFilterItem.model_validate(data)
        elif isinstance(data, str):
            data = LogServerFacilityFilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LogServerFacilityFilterListNode(ListNode[LogServerFacilityFilterItemNode]):
    """Navigator for list log-server-facility-filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LogServerFacilityFilterItem]:
        from ..data_models.ioa_network_element import LogServerFacilityFilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogServerFacilityFilterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LogServerFacilityFilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LogServerFacilityFilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LogServerItemNode(ItemNode):
    """Navigator for list item log-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LogServerItem:
        from ..data_models.ioa_network_element import LogServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.LogServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LogServerItem

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

    def replace(self, data: ioa_network_element.LogServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LogServerItem

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
    def log_server_facility_filter(self) -> LogServerFacilityFilterListNode:
        return LogServerFacilityFilterListNode(
            self._client,
            f"{self._path}/log-server-facility-filter",
            "log-server-facility-filter",
            LogServerFacilityFilterItemNode,
        )


class LogServerListNode(ListNode[LogServerItemNode]):
    """Navigator for list log-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LogServerItem]:
        from ..data_models.ioa_network_element import LogServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LogServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LogServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LogFileFacilityFilterItemNode(ItemNode):
    """Navigator for list item log-file-facility-filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LogFileFacilityFilterItem:
        from ..data_models.ioa_network_element import LogFileFacilityFilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogFileFacilityFilterItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.LogFileFacilityFilterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LogFileFacilityFilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogFileFacilityFilterItem.model_validate(data)
        elif isinstance(data, str):
            data = LogFileFacilityFilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.LogFileFacilityFilterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LogFileFacilityFilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogFileFacilityFilterItem.model_validate(data)
        elif isinstance(data, str):
            data = LogFileFacilityFilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LogFileFacilityFilterListNode(ListNode[LogFileFacilityFilterItemNode]):
    """Navigator for list log-file-facility-filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LogFileFacilityFilterItem]:
        from ..data_models.ioa_network_element import LogFileFacilityFilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogFileFacilityFilterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LogFileFacilityFilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LogFileFacilityFilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LogFileItemNode(ItemNode):
    """Navigator for list item log-file"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LogFileItem:
        from ..data_models.ioa_network_element import LogFileItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogFileItem.model_validate(resp)

    def update(self, data: ioa_network_element.LogFileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LogFileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogFileItem.model_validate(data)
        elif isinstance(data, str):
            data = LogFileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.LogFileItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LogFileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogFileItem.model_validate(data)
        elif isinstance(data, str):
            data = LogFileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def log_file_facility_filter(self) -> LogFileFacilityFilterListNode:
        return LogFileFacilityFilterListNode(
            self._client,
            f"{self._path}/log-file-facility-filter",
            "log-file-facility-filter",
            LogFileFacilityFilterItemNode,
        )


class LogFileListNode(ListNode[LogFileItemNode]):
    """Navigator for list log-file"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LogFileItem]:
        from ..data_models.ioa_network_element import LogFileItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogFileItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LogFileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LogFileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LogConsoleFacilityFilterItemNode(ItemNode):
    """Navigator for list item log-console-facility-filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LogConsoleFacilityFilterItem:
        from ..data_models.ioa_network_element import LogConsoleFacilityFilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogConsoleFacilityFilterItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.LogConsoleFacilityFilterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LogConsoleFacilityFilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogConsoleFacilityFilterItem.model_validate(data)
        elif isinstance(data, str):
            data = LogConsoleFacilityFilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.LogConsoleFacilityFilterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LogConsoleFacilityFilterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogConsoleFacilityFilterItem.model_validate(data)
        elif isinstance(data, str):
            data = LogConsoleFacilityFilterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LogConsoleFacilityFilterListNode(ListNode[LogConsoleFacilityFilterItemNode]):
    """Navigator for list log-console-facility-filter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LogConsoleFacilityFilterItem]:
        from ..data_models.ioa_network_element import LogConsoleFacilityFilterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LogConsoleFacilityFilterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LogConsoleFacilityFilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LogConsoleFacilityFilterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LogConsoleNode(Node):
    """Navigator for log-console"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LogConsole:
        from ..data_models.ioa_network_element import LogConsole

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LogConsole.model_validate(resp)

    def update(self, data: ioa_network_element.LogConsole | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LogConsole

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogConsole.model_validate(data)
        elif isinstance(data, str):
            data = LogConsole.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.LogConsole | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LogConsole

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LogConsole.model_validate(data)
        elif isinstance(data, str):
            data = LogConsole.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def log_console_facility_filter(self) -> LogConsoleFacilityFilterListNode:
        return LogConsoleFacilityFilterListNode(
            self._client,
            f"{self._path}/log-console-facility-filter",
            "log-console-facility-filter",
            LogConsoleFacilityFilterItemNode,
        )


class SyslogNode(Node):
    """Navigator for syslog"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Syslog:
        from ..data_models.ioa_network_element import Syslog

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Syslog.model_validate(resp)

    def update(self, data: ioa_network_element.Syslog | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Syslog

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Syslog.model_validate(data)
        elif isinstance(data, str):
            data = Syslog.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Syslog | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Syslog

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Syslog.model_validate(data)
        elif isinstance(data, str):
            data = Syslog.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def log_server(self) -> LogServerListNode:
        return LogServerListNode(self._client, f"{self._path}/log-server", "log-server", LogServerItemNode)

    @property
    def log_file(self) -> LogFileListNode:
        return LogFileListNode(self._client, f"{self._path}/log-file", "log-file", LogFileItemNode)

    @property
    def log_console(self) -> LogConsoleNode:
        return LogConsoleNode(self._client, f"{self._path}/log-console", "log-console")


class SshHostKeyItemNode(ItemNode):
    """Navigator for list item ssh-host-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SshHostKeyItem:
        from ..data_models.ioa_network_element import SshHostKeyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SshHostKeyItem.model_validate(resp)

    def update(self, data: ioa_network_element.SshHostKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SshHostKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SshHostKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = SshHostKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SshHostKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SshHostKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SshHostKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = SshHostKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SshHostKeyListNode(ListNode[SshHostKeyItemNode]):
    """Navigator for list ssh-host-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SshHostKeyItem]:
        from ..data_models.ioa_network_element import SshHostKeyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SshHostKeyItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SshHostKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SshHostKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SshKnownHostItemNode(ItemNode):
    """Navigator for list item ssh-known-host"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SshKnownHostItem:
        from ..data_models.ioa_network_element import SshKnownHostItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SshKnownHostItem.model_validate(resp)

    def update(self, data: ioa_network_element.SshKnownHostItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SshKnownHostItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SshKnownHostItem.model_validate(data)
        elif isinstance(data, str):
            data = SshKnownHostItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SshKnownHostItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SshKnownHostItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SshKnownHostItem.model_validate(data)
        elif isinstance(data, str):
            data = SshKnownHostItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SshKnownHostListNode(ListNode[SshKnownHostItemNode]):
    """Navigator for list ssh-known-host"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SshKnownHostItem]:
        from ..data_models.ioa_network_element import SshKnownHostItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SshKnownHostItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SshKnownHostItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SshKnownHostItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SshAuthorizedKeyItemNode(ItemNode):
    """Navigator for list item ssh-authorized-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SshAuthorizedKeyItem:
        from ..data_models.ioa_network_element import SshAuthorizedKeyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SshAuthorizedKeyItem.model_validate(resp)

    def update(self, data: ioa_network_element.SshAuthorizedKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SshAuthorizedKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SshAuthorizedKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = SshAuthorizedKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SshAuthorizedKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SshAuthorizedKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SshAuthorizedKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = SshAuthorizedKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SshAuthorizedKeyListNode(ListNode[SshAuthorizedKeyItemNode]):
    """Navigator for list ssh-authorized-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SshAuthorizedKeyItem]:
        from ..data_models.ioa_network_element import SshAuthorizedKeyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SshAuthorizedKeyItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SshAuthorizedKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SshAuthorizedKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SshNode(Node):
    """Navigator for ssh"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ssh:
        from ..data_models.ioa_network_element import Ssh

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ssh.model_validate(resp)

    def update(self, data: ioa_network_element.Ssh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ssh

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

    def replace(self, data: ioa_network_element.Ssh | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ssh

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

    @property
    def ssh_host_key(self) -> SshHostKeyListNode:
        return SshHostKeyListNode(self._client, f"{self._path}/ssh-host-key", "ssh-host-key", SshHostKeyItemNode)

    @property
    def ssh_known_host(self) -> SshKnownHostListNode:
        return SshKnownHostListNode(
            self._client, f"{self._path}/ssh-known-host", "ssh-known-host", SshKnownHostItemNode
        )

    @property
    def ssh_authorized_key(self) -> SshAuthorizedKeyListNode:
        return SshAuthorizedKeyListNode(
            self._client, f"{self._path}/ssh-authorized-key", "ssh-authorized-key", SshAuthorizedKeyItemNode
        )


class CliAliasItemNode(ItemNode):
    """Navigator for list item cli-alias"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CliAliasItem:
        from ..data_models.ioa_network_element import CliAliasItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CliAliasItem.model_validate(resp)

    def update(self, data: ioa_network_element.CliAliasItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CliAliasItem

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

    def replace(self, data: ioa_network_element.CliAliasItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CliAliasItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CliAliasItem]:
        from ..data_models.ioa_network_element import CliAliasItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CliAliasItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CliAliasItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CliAliasItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CliSessionConfigItemNode(ItemNode):
    """Navigator for list item cli-session-config"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CliSessionConfigItem:
        from ..data_models.ioa_network_element import CliSessionConfigItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CliSessionConfigItem.model_validate(resp)

    def update(self, data: ioa_network_element.CliSessionConfigItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CliSessionConfigItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliSessionConfigItem.model_validate(data)
        elif isinstance(data, str):
            data = CliSessionConfigItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CliSessionConfigItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CliSessionConfigItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CliSessionConfigItem.model_validate(data)
        elif isinstance(data, str):
            data = CliSessionConfigItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CliSessionConfigListNode(ListNode[CliSessionConfigItemNode]):
    """Navigator for list cli-session-config"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CliSessionConfigItem]:
        from ..data_models.ioa_network_element import CliSessionConfigItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CliSessionConfigItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CliSessionConfigItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CliSessionConfigItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CliNode(Node):
    """Navigator for cli"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Cli:
        from ..data_models.ioa_network_element import Cli

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Cli.model_validate(resp)

    def update(self, data: ioa_network_element.Cli | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Cli

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

    def replace(self, data: ioa_network_element.Cli | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Cli

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
    def cli_session_config(self) -> CliSessionConfigListNode:
        return CliSessionConfigListNode(
            self._client, f"{self._path}/cli-session-config", "cli-session-config", CliSessionConfigItemNode
        )


class SerialConsoleNode(Node):
    """Navigator for serial-console"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SerialConsole:
        from ..data_models.ioa_network_element import SerialConsole

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SerialConsole.model_validate(resp)

    def update(self, data: ioa_network_element.SerialConsole | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SerialConsole

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerialConsole.model_validate(data)
        elif isinstance(data, str):
            data = SerialConsole.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.SerialConsole | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SerialConsole

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SerialConsole.model_validate(data)
        elif isinstance(data, str):
            data = SerialConsole.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NetconfNode(Node):
    """Navigator for netconf"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Netconf:
        from ..data_models.ioa_network_element import Netconf

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Netconf.model_validate(resp)

    def update(self, data: ioa_network_element.Netconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Netconf

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

    def replace(self, data: ioa_network_element.Netconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Netconf

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


class Tl1Node(Node):
    """Navigator for tl1"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Tl1:
        from ..data_models.ioa_network_element import Tl1

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Tl1.model_validate(resp)

    def update(self, data: ioa_network_element.Tl1 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Tl1

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Tl1.model_validate(data)
        elif isinstance(data, str):
            data = Tl1.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Tl1 | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Tl1

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Tl1.model_validate(data)
        elif isinstance(data, str):
            data = Tl1.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class RestconfNode(Node):
    """Navigator for restconf"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Restconf:
        from ..data_models.ioa_network_element import Restconf

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Restconf.model_validate(resp)

    def update(self, data: ioa_network_element.Restconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Restconf

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

    def replace(self, data: ioa_network_element.Restconf | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Restconf

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


class GrpcNode(Node):
    """Navigator for grpc"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Grpc:
        from ..data_models.ioa_network_element import Grpc

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Grpc.model_validate(resp)

    def update(self, data: ioa_network_element.Grpc | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Grpc

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

    def replace(self, data: ioa_network_element.Grpc | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Grpc

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


class SnmpCommunityItemNode(ItemNode):
    """Navigator for list item snmp-community"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SnmpCommunityItem:
        from ..data_models.ioa_network_element import SnmpCommunityItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SnmpCommunityItem.model_validate(resp)

    def update(self, data: ioa_network_element.SnmpCommunityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SnmpCommunityItem

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

    def replace(self, data: ioa_network_element.SnmpCommunityItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SnmpCommunityItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SnmpCommunityItem]:
        from ..data_models.ioa_network_element import SnmpCommunityItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SnmpCommunityItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SnmpCommunityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SnmpCommunityItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SnmpTargetItemNode(ItemNode):
    """Navigator for list item snmp-target"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SnmpTargetItem:
        from ..data_models.ioa_network_element import SnmpTargetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SnmpTargetItem.model_validate(resp)

    def update(self, data: ioa_network_element.SnmpTargetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SnmpTargetItem

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

    def replace(self, data: ioa_network_element.SnmpTargetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SnmpTargetItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SnmpTargetItem]:
        from ..data_models.ioa_network_element import SnmpTargetItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SnmpTargetItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SnmpTargetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SnmpTargetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class Snmpv3UserItemNode(ItemNode):
    """Navigator for list item snmpv3-user"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Snmpv3UserItem:
        from ..data_models.ioa_network_element import Snmpv3UserItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Snmpv3UserItem.model_validate(resp)

    def update(self, data: ioa_network_element.Snmpv3UserItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Snmpv3UserItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Snmpv3UserItem.model_validate(data)
        elif isinstance(data, str):
            data = Snmpv3UserItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Snmpv3UserItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Snmpv3UserItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Snmpv3UserItem.model_validate(data)
        elif isinstance(data, str):
            data = Snmpv3UserItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Snmpv3UserListNode(ListNode[Snmpv3UserItemNode]):
    """Navigator for list snmpv3-user"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Snmpv3UserItem]:
        from ..data_models.ioa_network_element import Snmpv3UserItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Snmpv3UserItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Snmpv3UserItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Snmpv3UserItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SnmpNode(Node):
    """Navigator for snmp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Snmp:
        from ..data_models.ioa_network_element import Snmp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Snmp.model_validate(resp)

    def update(self, data: ioa_network_element.Snmp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Snmp

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

    def replace(self, data: ioa_network_element.Snmp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Snmp

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
        return SnmpCommunityListNode(
            self._client, f"{self._path}/snmp-community", "snmp-community", SnmpCommunityItemNode
        )

    @property
    def snmp_target(self) -> SnmpTargetListNode:
        return SnmpTargetListNode(self._client, f"{self._path}/snmp-target", "snmp-target", SnmpTargetItemNode)

    @property
    def snmpv3_user(self) -> Snmpv3UserListNode:
        return Snmpv3UserListNode(self._client, f"{self._path}/snmpv3-user", "snmpv3-user", Snmpv3UserItemNode)


class HttpFileServerNode(Node):
    """Navigator for http-file-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.HttpFileServer:
        from ..data_models.ioa_network_element import HttpFileServer

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return HttpFileServer.model_validate(resp)

    def update(self, data: ioa_network_element.HttpFileServer | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import HttpFileServer

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HttpFileServer.model_validate(data)
        elif isinstance(data, str):
            data = HttpFileServer.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.HttpFileServer | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import HttpFileServer

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HttpFileServer.model_validate(data)
        elif isinstance(data, str):
            data = HttpFileServer.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class DialOutServerItemNode(ItemNode):
    """Navigator for list item dial-out-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DialOutServerItem:
        from ..data_models.ioa_network_element import DialOutServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DialOutServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.DialOutServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DialOutServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialOutServerItem.model_validate(data)
        elif isinstance(data, str):
            data = DialOutServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.DialOutServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DialOutServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DialOutServerItem.model_validate(data)
        elif isinstance(data, str):
            data = DialOutServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DialOutServerListNode(ListNode[DialOutServerItemNode]):
    """Navigator for list dial-out-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DialOutServerItem]:
        from ..data_models.ioa_network_element import DialOutServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DialOutServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DialOutServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DialOutServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DataModelItemNode(ItemNode):
    """Navigator for list item data-model"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DataModelItem:
        from ..data_models.ioa_network_element import DataModelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DataModelItem.model_validate(resp)

    def update(self, data: ioa_network_element.DataModelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DataModelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DataModelItem.model_validate(data)
        elif isinstance(data, str):
            data = DataModelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.DataModelItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DataModelItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DataModelItem.model_validate(data)
        elif isinstance(data, str):
            data = DataModelItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DataModelListNode(ListNode[DataModelItemNode]):
    """Navigator for list data-model"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DataModelItem]:
        from ..data_models.ioa_network_element import DataModelItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DataModelItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DataModelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DataModelItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FastTelemetryNode(Node):
    """Navigator for fast-telemetry"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FastTelemetry:
        from ..data_models.ioa_network_element import FastTelemetry

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FastTelemetry.model_validate(resp)

    def update(self, data: ioa_network_element.FastTelemetry | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FastTelemetry

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FastTelemetry.model_validate(data)
        elif isinstance(data, str):
            data = FastTelemetry.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.FastTelemetry | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FastTelemetry

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FastTelemetry.model_validate(data)
        elif isinstance(data, str):
            data = FastTelemetry.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class HighSpeedMonitoringNode(Node):
    """Navigator for high-speed-monitoring"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.HighSpeedMonitoring:
        from ..data_models.ioa_network_element import HighSpeedMonitoring

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return HighSpeedMonitoring.model_validate(resp)

    def update(self, data: ioa_network_element.HighSpeedMonitoring | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import HighSpeedMonitoring

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HighSpeedMonitoring.model_validate(data)
        elif isinstance(data, str):
            data = HighSpeedMonitoring.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.HighSpeedMonitoring | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import HighSpeedMonitoring

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = HighSpeedMonitoring.model_validate(data)
        elif isinstance(data, str):
            data = HighSpeedMonitoring.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NotificationTypeItemNode(ItemNode):
    """Navigator for list item notification-type"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NotificationTypeItem:
        from ..data_models.ioa_network_element import NotificationTypeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NotificationTypeItem.model_validate(resp)

    def update(self, data: ioa_network_element.NotificationTypeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NotificationTypeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NotificationTypeItem.model_validate(data)
        elif isinstance(data, str):
            data = NotificationTypeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.NotificationTypeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NotificationTypeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NotificationTypeItem.model_validate(data)
        elif isinstance(data, str):
            data = NotificationTypeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NotificationTypeListNode(ListNode[NotificationTypeItemNode]):
    """Navigator for list notification-type"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NotificationTypeItem]:
        from ..data_models.ioa_network_element import NotificationTypeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NotificationTypeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NotificationTypeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NotificationTypeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NotificationStreamItemNode(ItemNode):
    """Navigator for list item notification-stream"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NotificationStreamItem:
        from ..data_models.ioa_network_element import NotificationStreamItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NotificationStreamItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.NotificationStreamItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import NotificationStreamItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NotificationStreamItem.model_validate(data)
        elif isinstance(data, str):
            data = NotificationStreamItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.NotificationStreamItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import NotificationStreamItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NotificationStreamItem.model_validate(data)
        elif isinstance(data, str):
            data = NotificationStreamItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NotificationStreamListNode(ListNode[NotificationStreamItemNode]):
    """Navigator for list notification-stream"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NotificationStreamItem]:
        from ..data_models.ioa_network_element import NotificationStreamItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NotificationStreamItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NotificationStreamItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NotificationStreamItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NotificationsNode(Node):
    """Navigator for notifications"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Notifications:
        from ..data_models.ioa_network_element import Notifications

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Notifications.model_validate(resp)

    def update(self, data: ioa_network_element.Notifications | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Notifications

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Notifications.model_validate(data)
        elif isinstance(data, str):
            data = Notifications.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Notifications | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Notifications

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Notifications.model_validate(data)
        elif isinstance(data, str):
            data = Notifications.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def notification_type(self) -> NotificationTypeListNode:
        return NotificationTypeListNode(
            self._client, f"{self._path}/notification-type", "notification-type", NotificationTypeItemNode
        )

    @property
    def notification_stream(self) -> NotificationStreamListNode:
        return NotificationStreamListNode(
            self._client, f"{self._path}/notification-stream", "notification-stream", NotificationStreamItemNode
        )


class ProtocolsNode(Node):
    """Navigator for protocols"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Protocols:
        from ..data_models.ioa_network_element import Protocols

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Protocols.model_validate(resp)

    def update(self, data: ioa_network_element.Protocols | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Protocols

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

    def replace(self, data: ioa_network_element.Protocols | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Protocols

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
    def ssh(self) -> SshNode:
        return SshNode(self._client, f"{self._path}/ssh", "ssh")

    @property
    def cli(self) -> CliNode:
        return CliNode(self._client, f"{self._path}/cli", "cli")

    @property
    def serial_console(self) -> SerialConsoleNode:
        return SerialConsoleNode(self._client, f"{self._path}/serial-console", "serial-console")

    @property
    def netconf(self) -> NetconfNode:
        return NetconfNode(self._client, f"{self._path}/netconf", "netconf")

    @property
    def tl1(self) -> Tl1Node:
        return Tl1Node(self._client, f"{self._path}/tl1", "tl1")

    @property
    def restconf(self) -> RestconfNode:
        return RestconfNode(self._client, f"{self._path}/restconf", "restconf")

    @property
    def grpc(self) -> GrpcNode:
        return GrpcNode(self._client, f"{self._path}/grpc", "grpc")

    @property
    def snmp(self) -> SnmpNode:
        return SnmpNode(self._client, f"{self._path}/snmp", "snmp")

    @property
    def http_file_server(self) -> HttpFileServerNode:
        return HttpFileServerNode(self._client, f"{self._path}/http-file-server", "http-file-server")

    @property
    def dial_out_server(self) -> DialOutServerListNode:
        return DialOutServerListNode(
            self._client, f"{self._path}/dial-out-server", "dial-out-server", DialOutServerItemNode
        )

    @property
    def data_model(self) -> DataModelListNode:
        return DataModelListNode(self._client, f"{self._path}/data-model", "data-model", DataModelItemNode)

    @property
    def fast_telemetry(self) -> FastTelemetryNode:
        return FastTelemetryNode(self._client, f"{self._path}/fast-telemetry", "fast-telemetry")

    @property
    def high_speed_monitoring(self) -> HighSpeedMonitoringNode:
        return HighSpeedMonitoringNode(self._client, f"{self._path}/high-speed-monitoring", "high-speed-monitoring")

    @property
    def notifications(self) -> NotificationsNode:
        return NotificationsNode(self._client, f"{self._path}/notifications", "notifications")


class TaskItemNode(ItemNode):
    """Navigator for list item task"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TaskItem:
        from ..data_models.ioa_network_element import TaskItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TaskItem.model_validate(resp)

    def update(self, data: ioa_network_element.TaskItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TaskItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TaskItem.model_validate(data)
        elif isinstance(data, str):
            data = TaskItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.TaskItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TaskItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TaskItem.model_validate(data)
        elif isinstance(data, str):
            data = TaskItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TaskListNode(ListNode[TaskItemNode]):
    """Navigator for list task"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TaskItem]:
        from ..data_models.ioa_network_element import TaskItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TaskItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TaskItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TaskItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ScheduledTasksNode(Node):
    """Navigator for scheduled-tasks"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ScheduledTasks:
        from ..data_models.ioa_network_element import ScheduledTasks

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ScheduledTasks.model_validate(resp)

    def update(self, data: ioa_network_element.ScheduledTasks | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ScheduledTasks

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ScheduledTasks.model_validate(data)
        elif isinstance(data, str):
            data = ScheduledTasks.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.ScheduledTasks | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ScheduledTasks

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ScheduledTasks.model_validate(data)
        elif isinstance(data, str):
            data = ScheduledTasks.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def task(self) -> TaskListNode:
        return TaskListNode(self._client, f"{self._path}/task", "task", TaskItemNode)


class ZtpNode(Node):
    """Navigator for ztp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ztp:
        from ..data_models.ioa_network_element import Ztp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ztp.model_validate(resp)

    def update(self, data: ioa_network_element.Ztp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ztp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ztp.model_validate(data)
        elif isinstance(data, str):
            data = Ztp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ztp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ztp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ztp.model_validate(data)
        elif isinstance(data, str):
            data = Ztp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class TransferStatusItemNode(ItemNode):
    """Navigator for list item transfer-status"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TransferStatusItem:
        from ..data_models.ioa_network_element import TransferStatusItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TransferStatusItem.model_validate(resp)

    def update(self, data: ioa_network_element.TransferStatusItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TransferStatusItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TransferStatusItem.model_validate(data)
        elif isinstance(data, str):
            data = TransferStatusItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.TransferStatusItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TransferStatusItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TransferStatusItem.model_validate(data)
        elif isinstance(data, str):
            data = TransferStatusItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TransferStatusListNode(ListNode[TransferStatusItemNode]):
    """Navigator for list transfer-status"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TransferStatusItem]:
        from ..data_models.ioa_network_element import TransferStatusItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TransferStatusItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TransferStatusItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TransferStatusItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class TransferNode(Node):
    """Navigator for transfer"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Transfer:
        from ..data_models.ioa_network_element import Transfer

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Transfer.model_validate(resp)

    def update(self, data: ioa_network_element.Transfer | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Transfer

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Transfer.model_validate(data)
        elif isinstance(data, str):
            data = Transfer.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Transfer | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Transfer

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Transfer.model_validate(data)
        elif isinstance(data, str):
            data = Transfer.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def transfer_status(self) -> TransferStatusListNode:
        return TransferStatusListNode(
            self._client, f"{self._path}/transfer-status", "transfer-status", TransferStatusItemNode
        )


class Ipv4AddressItemNode(ItemNode):
    """Navigator for list item ipv4-address"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ipv4AddressItem:
        from ..data_models.ioa_network_element import Ipv4AddressItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv4AddressItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ipv4AddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv4AddressItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4AddressItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4AddressItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ipv4AddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv4AddressItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4AddressItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4AddressItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Ipv4AddressListNode(ListNode[Ipv4AddressItemNode]):
    """Navigator for list ipv4-address"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ipv4AddressItem]:
        from ..data_models.ioa_network_element import Ipv4AddressItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv4AddressItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ipv4AddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ipv4AddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class Ipv6AddressItemNode(ItemNode):
    """Navigator for list item ipv6-address"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ipv6AddressItem:
        from ..data_models.ioa_network_element import Ipv6AddressItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv6AddressItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ipv6AddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv6AddressItem

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

    def replace(self, data: ioa_network_element.Ipv6AddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv6AddressItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ipv6AddressItem]:
        from ..data_models.ioa_network_element import Ipv6AddressItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv6AddressItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ipv6AddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ipv6AddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class InterfaceItemNode(ItemNode):
    """Navigator for list item interface"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.InterfaceItem:
        from ..data_models.ioa_network_element import InterfaceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InterfaceItem.model_validate(resp)

    def update(self, data: ioa_network_element.InterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InterfaceItem

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

    def replace(self, data: ioa_network_element.InterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InterfaceItem

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
    def ipv4_address(self) -> Ipv4AddressListNode:
        return Ipv4AddressListNode(self._client, f"{self._path}/ipv4-address", "ipv4-address", Ipv4AddressItemNode)

    @property
    def ipv6_address(self) -> Ipv6AddressListNode:
        return Ipv6AddressListNode(self._client, f"{self._path}/ipv6-address", "ipv6-address", Ipv6AddressItemNode)


class InterfaceListNode(ListNode[InterfaceItemNode]):
    """Navigator for list interface"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.InterfaceItem]:
        from ..data_models.ioa_network_element import InterfaceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InterfaceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.InterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.InterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class VrfItemNode(ItemNode):
    """Navigator for list item vrf"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.VrfItem:
        from ..data_models.ioa_network_element import VrfItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return VrfItem.model_validate(resp)

    def update(self, data: ioa_network_element.VrfItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import VrfItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = VrfItem.model_validate(data)
        elif isinstance(data, str):
            data = VrfItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.VrfItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import VrfItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = VrfItem.model_validate(data)
        elif isinstance(data, str):
            data = VrfItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class VrfListNode(ListNode[VrfItemNode]):
    """Navigator for list vrf"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.VrfItem]:
        from ..data_models.ioa_network_element import VrfItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [VrfItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.VrfItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.VrfItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class Ipv4StaticRouteItemNode(ItemNode):
    """Navigator for list item ipv4-static-route"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ipv4StaticRouteItem:
        from ..data_models.ioa_network_element import Ipv4StaticRouteItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv4StaticRouteItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ipv4StaticRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv4StaticRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4StaticRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4StaticRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ipv4StaticRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv4StaticRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv4StaticRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv4StaticRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Ipv4StaticRouteListNode(ListNode[Ipv4StaticRouteItemNode]):
    """Navigator for list ipv4-static-route"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ipv4StaticRouteItem]:
        from ..data_models.ioa_network_element import Ipv4StaticRouteItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv4StaticRouteItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ipv4StaticRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ipv4StaticRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class Ipv6StaticRouteItemNode(ItemNode):
    """Navigator for list item ipv6-static-route"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ipv6StaticRouteItem:
        from ..data_models.ioa_network_element import Ipv6StaticRouteItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ipv6StaticRouteItem.model_validate(resp)

    def update(self, data: ioa_network_element.Ipv6StaticRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv6StaticRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6StaticRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6StaticRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.Ipv6StaticRouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ipv6StaticRouteItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ipv6StaticRouteItem.model_validate(data)
        elif isinstance(data, str):
            data = Ipv6StaticRouteItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class Ipv6StaticRouteListNode(ListNode[Ipv6StaticRouteItemNode]):
    """Navigator for list ipv6-static-route"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ipv6StaticRouteItem]:
        from ..data_models.ioa_network_element import Ipv6StaticRouteItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ipv6StaticRouteItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ipv6StaticRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ipv6StaticRouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OspfAreaRangeItemNode(ItemNode):
    """Navigator for list item ospf-area-range"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OspfAreaRangeItem:
        from ..data_models.ioa_network_element import OspfAreaRangeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfAreaRangeItem.model_validate(resp)

    def update(self, data: ioa_network_element.OspfAreaRangeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfAreaRangeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfAreaRangeItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfAreaRangeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OspfAreaRangeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfAreaRangeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfAreaRangeItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfAreaRangeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OspfAreaRangeListNode(ListNode[OspfAreaRangeItemNode]):
    """Navigator for list ospf-area-range"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OspfAreaRangeItem]:
        from ..data_models.ioa_network_element import OspfAreaRangeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfAreaRangeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OspfAreaRangeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OspfAreaRangeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AuthKeyNode(Node):
    """Navigator for auth-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AuthKey:
        from ..data_models.ioa_network_element import AuthKey

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AuthKey.model_validate(resp)

    def update(self, data: ioa_network_element.AuthKey | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AuthKey

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AuthKey.model_validate(data)
        elif isinstance(data, str):
            data = AuthKey.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.AuthKey | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AuthKey

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AuthKey.model_validate(data)
        elif isinstance(data, str):
            data = AuthKey.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class Ospfv3IpsecSecurityAssociationItemNode(ItemNode):
    """Navigator for list item ospfv3-ipsec-security-association"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ospfv3IpsecSecurityAssociationItem:
        from ..data_models.ioa_network_element import Ospfv3IpsecSecurityAssociationItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ospfv3IpsecSecurityAssociationItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.Ospfv3IpsecSecurityAssociationItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import Ospfv3IpsecSecurityAssociationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ospfv3IpsecSecurityAssociationItem.model_validate(data)
        elif isinstance(data, str):
            data = Ospfv3IpsecSecurityAssociationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.Ospfv3IpsecSecurityAssociationItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import Ospfv3IpsecSecurityAssociationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Ospfv3IpsecSecurityAssociationItem.model_validate(data)
        elif isinstance(data, str):
            data = Ospfv3IpsecSecurityAssociationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def auth_key(self) -> AuthKeyNode:
        return AuthKeyNode(self._client, f"{self._path}/auth-key", "auth-key")


class Ospfv3IpsecSecurityAssociationListNode(ListNode[Ospfv3IpsecSecurityAssociationItemNode]):
    """Navigator for list ospfv3-ipsec-security-association"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.Ospfv3IpsecSecurityAssociationItem]:
        from ..data_models.ioa_network_element import Ospfv3IpsecSecurityAssociationItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [Ospfv3IpsecSecurityAssociationItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.Ospfv3IpsecSecurityAssociationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.Ospfv3IpsecSecurityAssociationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OspfInterfaceItemNode(ItemNode):
    """Navigator for list item ospf-interface"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OspfInterfaceItem:
        from ..data_models.ioa_network_element import OspfInterfaceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfInterfaceItem.model_validate(resp)

    def update(self, data: ioa_network_element.OspfInterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfInterfaceItem

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

    def replace(self, data: ioa_network_element.OspfInterfaceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfInterfaceItem

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
    def ospfv3_ipsec_security_association(self) -> Ospfv3IpsecSecurityAssociationListNode:
        return Ospfv3IpsecSecurityAssociationListNode(
            self._client,
            f"{self._path}/ospfv3-ipsec-security-association",
            "ospfv3-ipsec-security-association",
            Ospfv3IpsecSecurityAssociationItemNode,
        )


class OspfInterfaceListNode(ListNode[OspfInterfaceItemNode]):
    """Navigator for list ospf-interface"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OspfInterfaceItem]:
        from ..data_models.ioa_network_element import OspfInterfaceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfInterfaceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OspfInterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OspfInterfaceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OspfAreaItemNode(ItemNode):
    """Navigator for list item ospf-area"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OspfAreaItem:
        from ..data_models.ioa_network_element import OspfAreaItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfAreaItem.model_validate(resp)

    def update(self, data: ioa_network_element.OspfAreaItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfAreaItem

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

    def replace(self, data: ioa_network_element.OspfAreaItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfAreaItem

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
    def ospf_area_range(self) -> OspfAreaRangeListNode:
        return OspfAreaRangeListNode(
            self._client, f"{self._path}/ospf-area-range", "ospf-area-range", OspfAreaRangeItemNode
        )

    @property
    def ospf_interface(self) -> OspfInterfaceListNode:
        return OspfInterfaceListNode(
            self._client, f"{self._path}/ospf-interface", "ospf-interface", OspfInterfaceItemNode
        )


class OspfAreaListNode(ListNode[OspfAreaItemNode]):
    """Navigator for list ospf-area"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OspfAreaItem]:
        from ..data_models.ioa_network_element import OspfAreaItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfAreaItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OspfAreaItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OspfAreaItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OspfInstanceItemNode(ItemNode):
    """Navigator for list item ospf-instance"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OspfInstanceItem:
        from ..data_models.ioa_network_element import OspfInstanceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OspfInstanceItem.model_validate(resp)

    def update(self, data: ioa_network_element.OspfInstanceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OspfInstanceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OspfInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OspfInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = OspfInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ospf_area(self) -> OspfAreaListNode:
        return OspfAreaListNode(self._client, f"{self._path}/ospf-area", "ospf-area", OspfAreaItemNode)


class OspfInstanceListNode(ListNode[OspfInstanceItemNode]):
    """Navigator for list ospf-instance"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OspfInstanceItem]:
        from ..data_models.ioa_network_element import OspfInstanceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OspfInstanceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OspfInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OspfInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IpMonitoringItemNode(ItemNode):
    """Navigator for list item ip-monitoring"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.IpMonitoringItem:
        from ..data_models.ioa_network_element import IpMonitoringItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return IpMonitoringItem.model_validate(resp)

    def update(self, data: ioa_network_element.IpMonitoringItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpMonitoringItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpMonitoringItem.model_validate(data)
        elif isinstance(data, str):
            data = IpMonitoringItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.IpMonitoringItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import IpMonitoringItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = IpMonitoringItem.model_validate(data)
        elif isinstance(data, str):
            data = IpMonitoringItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class IpMonitoringListNode(ListNode[IpMonitoringItemNode]):
    """Navigator for list ip-monitoring"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.IpMonitoringItem]:
        from ..data_models.ioa_network_element import IpMonitoringItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [IpMonitoringItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.IpMonitoringItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.IpMonitoringItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class BgpNetworkItemNode(ItemNode):
    """Navigator for list item bgp-network"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.BgpNetworkItem:
        from ..data_models.ioa_network_element import BgpNetworkItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BgpNetworkItem.model_validate(resp)

    def update(self, data: ioa_network_element.BgpNetworkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import BgpNetworkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNetworkItem.model_validate(data)
        elif isinstance(data, str):
            data = BgpNetworkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.BgpNetworkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import BgpNetworkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpNetworkItem.model_validate(data)
        elif isinstance(data, str):
            data = BgpNetworkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class BgpNetworkListNode(ListNode[BgpNetworkItemNode]):
    """Navigator for list bgp-network"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.BgpNetworkItem]:
        from ..data_models.ioa_network_element import BgpNetworkItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [BgpNetworkItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.BgpNetworkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.BgpNetworkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class BgpNeighborItemNode(ItemNode):
    """Navigator for list item bgp-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.BgpNeighborItem:
        from ..data_models.ioa_network_element import BgpNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BgpNeighborItem.model_validate(resp)

    def update(self, data: ioa_network_element.BgpNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import BgpNeighborItem

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

    def replace(self, data: ioa_network_element.BgpNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import BgpNeighborItem

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
    def bgp_network(self) -> BgpNetworkListNode:
        return BgpNetworkListNode(self._client, f"{self._path}/bgp-network", "bgp-network", BgpNetworkItemNode)


class BgpNeighborListNode(ListNode[BgpNeighborItemNode]):
    """Navigator for list bgp-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.BgpNeighborItem]:
        from ..data_models.ioa_network_element import BgpNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [BgpNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.BgpNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.BgpNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class BgpInstanceItemNode(ItemNode):
    """Navigator for list item bgp-instance"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.BgpInstanceItem:
        from ..data_models.ioa_network_element import BgpInstanceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return BgpInstanceItem.model_validate(resp)

    def update(self, data: ioa_network_element.BgpInstanceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import BgpInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = BgpInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.BgpInstanceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import BgpInstanceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = BgpInstanceItem.model_validate(data)
        elif isinstance(data, str):
            data = BgpInstanceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def bgp_neighbor(self) -> BgpNeighborListNode:
        return BgpNeighborListNode(self._client, f"{self._path}/bgp-neighbor", "bgp-neighbor", BgpNeighborItemNode)


class BgpInstanceListNode(ListNode[BgpInstanceItemNode]):
    """Navigator for list bgp-instance"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.BgpInstanceItem]:
        from ..data_models.ioa_network_element import BgpInstanceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [BgpInstanceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.BgpInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.BgpInstanceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class BgpNode(Node):
    """Navigator for bgp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Bgp:
        from ..data_models.ioa_network_element import Bgp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Bgp.model_validate(resp)

    def update(self, data: ioa_network_element.Bgp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Bgp

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

    def replace(self, data: ioa_network_element.Bgp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Bgp

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
    def bgp_instance(self) -> BgpInstanceListNode:
        return BgpInstanceListNode(self._client, f"{self._path}/bgp-instance", "bgp-instance", BgpInstanceItemNode)


class RoutingNode(Node):
    """Navigator for routing"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Routing:
        from ..data_models.ioa_network_element import Routing

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Routing.model_validate(resp)

    def update(self, data: ioa_network_element.Routing | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Routing

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

    def replace(self, data: ioa_network_element.Routing | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Routing

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
    def ipv4_static_route(self) -> Ipv4StaticRouteListNode:
        return Ipv4StaticRouteListNode(
            self._client, f"{self._path}/ipv4-static-route", "ipv4-static-route", Ipv4StaticRouteItemNode
        )

    @property
    def ipv6_static_route(self) -> Ipv6StaticRouteListNode:
        return Ipv6StaticRouteListNode(
            self._client, f"{self._path}/ipv6-static-route", "ipv6-static-route", Ipv6StaticRouteItemNode
        )

    @property
    def ospf_instance(self) -> OspfInstanceListNode:
        return OspfInstanceListNode(self._client, f"{self._path}/ospf-instance", "ospf-instance", OspfInstanceItemNode)

    @property
    def ip_monitoring(self) -> IpMonitoringListNode:
        return IpMonitoringListNode(self._client, f"{self._path}/ip-monitoring", "ip-monitoring", IpMonitoringItemNode)

    @property
    def bgp(self) -> BgpNode:
        return BgpNode(self._client, f"{self._path}/bgp", "bgp")


class NextHopItemNode(ItemNode):
    """Navigator for list item next-hop"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NextHopItem:
        from ..data_models.ioa_network_element import NextHopItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NextHopItem.model_validate(resp)

    def update(self, data: ioa_network_element.NextHopItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NextHopItem

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

    def replace(self, data: ioa_network_element.NextHopItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NextHopItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NextHopItem]:
        from ..data_models.ioa_network_element import NextHopItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NextHopItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NextHopItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NextHopItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class RouteItemNode(ItemNode):
    """Navigator for list item route"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.RouteItem:
        from ..data_models.ioa_network_element import RouteItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RouteItem.model_validate(resp)

    def update(self, data: ioa_network_element.RouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RouteItem

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

    def replace(self, data: ioa_network_element.RouteItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RouteItem

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
    def next_hop(self) -> NextHopListNode:
        return NextHopListNode(self._client, f"{self._path}/next-hop", "next-hop", NextHopItemNode)


class RouteListNode(ListNode[RouteItemNode]):
    """Navigator for list route"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.RouteItem]:
        from ..data_models.ioa_network_element import RouteItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RouteItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.RouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.RouteItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class RibItemNode(ItemNode):
    """Navigator for list item rib"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.RibItem:
        from ..data_models.ioa_network_element import RibItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RibItem.model_validate(resp)

    def update(self, data: ioa_network_element.RibItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RibItem

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

    def replace(self, data: ioa_network_element.RibItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import RibItem

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


class RibListNode(ListNode[RibItemNode]):
    """Navigator for list rib"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.RibItem]:
        from ..data_models.ioa_network_element import RibItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RibItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.RibItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.RibItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AceItemNode(ItemNode):
    """Navigator for list item ace"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AceItem:
        from ..data_models.ioa_network_element import AceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AceItem.model_validate(resp)

    def update(self, data: ioa_network_element.AceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AceItem

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

    def replace(self, data: ioa_network_element.AceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AceItem

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


class AceListNode(ListNode[AceItemNode]):
    """Navigator for list ace"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AceItem]:
        from ..data_models.ioa_network_element import AceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AclItemNode(ItemNode):
    """Navigator for list item acl"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AclItem:
        from ..data_models.ioa_network_element import AclItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AclItem.model_validate(resp)

    def update(self, data: ioa_network_element.AclItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AclItem

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

    def replace(self, data: ioa_network_element.AclItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AclItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AclItem]:
        from ..data_models.ioa_network_element import AclItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AclItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AclItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AclItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AccessControlListNode(Node):
    """Navigator for access-control-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AccessControlList:
        from ..data_models.ioa_network_element import AccessControlList

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AccessControlList.model_validate(resp)

    def update(self, data: ioa_network_element.AccessControlList | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AccessControlList

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AccessControlList.model_validate(data)
        elif isinstance(data, str):
            data = AccessControlList.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.AccessControlList | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AccessControlList

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AccessControlList.model_validate(data)
        elif isinstance(data, str):
            data = AccessControlList.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def acl(self) -> AclListNode:
        return AclListNode(self._client, f"{self._path}/acl", "acl", AclItemNode)


class DnsServerItemNode(ItemNode):
    """Navigator for list item dns-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DnsServerItem:
        from ..data_models.ioa_network_element import DnsServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DnsServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.DnsServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DnsServerItem

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

    def replace(self, data: ioa_network_element.DnsServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DnsServerItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DnsServerItem]:
        from ..data_models.ioa_network_element import DnsServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DnsServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DnsServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DnsServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DnsNode(Node):
    """Navigator for dns"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Dns:
        from ..data_models.ioa_network_element import Dns

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Dns.model_validate(resp)

    def update(self, data: ioa_network_element.Dns | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Dns

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

    def replace(self, data: ioa_network_element.Dns | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Dns

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


class NwXconnectItemNode(ItemNode):
    """Navigator for list item nw-xconnect"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NwXconnectItem:
        from ..data_models.ioa_network_element import NwXconnectItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NwXconnectItem.model_validate(resp)

    def update(self, data: ioa_network_element.NwXconnectItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NwXconnectItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NwXconnectItem.model_validate(data)
        elif isinstance(data, str):
            data = NwXconnectItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.NwXconnectItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NwXconnectItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NwXconnectItem.model_validate(data)
        elif isinstance(data, str):
            data = NwXconnectItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NwXconnectListNode(ListNode[NwXconnectItemNode]):
    """Navigator for list nw-xconnect"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NwXconnectItem]:
        from ..data_models.ioa_network_element import NwXconnectItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NwXconnectItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NwXconnectItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NwXconnectItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NetworkXconnectNode(Node):
    """Navigator for network-xconnect"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NetworkXconnect:
        from ..data_models.ioa_network_element import NetworkXconnect

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NetworkXconnect.model_validate(resp)

    def update(self, data: ioa_network_element.NetworkXconnect | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NetworkXconnect

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NetworkXconnect.model_validate(data)
        elif isinstance(data, str):
            data = NetworkXconnect.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.NetworkXconnect | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NetworkXconnect

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NetworkXconnect.model_validate(data)
        elif isinstance(data, str):
            data = NetworkXconnect.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def nw_xconnect(self) -> NwXconnectListNode:
        return NwXconnectListNode(self._client, f"{self._path}/nw-xconnect", "nw-xconnect", NwXconnectItemNode)


class NetworkingServicesNode(Node):
    """Navigator for networking-services"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NetworkingServices:
        from ..data_models.ioa_network_element import NetworkingServices

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NetworkingServices.model_validate(resp)

    def update(self, data: ioa_network_element.NetworkingServices | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NetworkingServices

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NetworkingServices.model_validate(data)
        elif isinstance(data, str):
            data = NetworkingServices.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.NetworkingServices | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NetworkingServices

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NetworkingServices.model_validate(data)
        elif isinstance(data, str):
            data = NetworkingServices.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def network_xconnect(self) -> NetworkXconnectNode:
        return NetworkXconnectNode(self._client, f"{self._path}/network-xconnect", "network-xconnect")


class NetworkingNode(Node):
    """Navigator for networking"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Networking:
        from ..data_models.ioa_network_element import Networking

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Networking.model_validate(resp)

    def update(self, data: ioa_network_element.Networking | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Networking

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

    def replace(self, data: ioa_network_element.Networking | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Networking

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
    def vrf(self) -> VrfListNode:
        return VrfListNode(self._client, f"{self._path}/vrf", "vrf", VrfItemNode)

    @property
    def routing(self) -> RoutingNode:
        return RoutingNode(self._client, f"{self._path}/routing", "routing")

    @property
    def rib(self) -> RibListNode:
        return RibListNode(self._client, f"{self._path}/rib", "rib", RibItemNode)

    @property
    def access_control_list(self) -> AccessControlListNode:
        return AccessControlListNode(self._client, f"{self._path}/access-control-list", "access-control-list")

    @property
    def dns(self) -> DnsNode:
        return DnsNode(self._client, f"{self._path}/dns", "dns")

    @property
    def networking_services(self) -> NetworkingServicesNode:
        return NetworkingServicesNode(self._client, f"{self._path}/networking-services", "networking-services")


class ClockNode(Node):
    """Navigator for clock"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Clock:
        from ..data_models.ioa_network_element import Clock

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Clock.model_validate(resp)

    def update(self, data: ioa_network_element.Clock | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Clock

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Clock.model_validate(data)
        elif isinstance(data, str):
            data = Clock.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Clock | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Clock

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Clock.model_validate(data)
        elif isinstance(data, str):
            data = Clock.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NtpKeyItemNode(ItemNode):
    """Navigator for list item ntp-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NtpKeyItem:
        from ..data_models.ioa_network_element import NtpKeyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NtpKeyItem.model_validate(resp)

    def update(self, data: ioa_network_element.NtpKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NtpKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = NtpKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.NtpKeyItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NtpKeyItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpKeyItem.model_validate(data)
        elif isinstance(data, str):
            data = NtpKeyItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NtpKeyListNode(ListNode[NtpKeyItemNode]):
    """Navigator for list ntp-key"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NtpKeyItem]:
        from ..data_models.ioa_network_element import NtpKeyItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NtpKeyItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NtpKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NtpKeyItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NtpServerStatusNode(Node):
    """Navigator for ntp-server-status"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NtpServerStatus:
        from ..data_models.ioa_network_element import NtpServerStatus

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NtpServerStatus.model_validate(resp)

    def update(self, data: ioa_network_element.NtpServerStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NtpServerStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpServerStatus.model_validate(data)
        elif isinstance(data, str):
            data = NtpServerStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.NtpServerStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NtpServerStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpServerStatus.model_validate(data)
        elif isinstance(data, str):
            data = NtpServerStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class NtpServerItemNode(ItemNode):
    """Navigator for list item ntp-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NtpServerItem:
        from ..data_models.ioa_network_element import NtpServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NtpServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.NtpServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NtpServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpServerItem.model_validate(data)
        elif isinstance(data, str):
            data = NtpServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.NtpServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NtpServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NtpServerItem.model_validate(data)
        elif isinstance(data, str):
            data = NtpServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def ntp_server_status(self) -> NtpServerStatusNode:
        return NtpServerStatusNode(self._client, f"{self._path}/ntp-server-status", "ntp-server-status")


class NtpServerListNode(ListNode[NtpServerItemNode]):
    """Navigator for list ntp-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NtpServerItem]:
        from ..data_models.ioa_network_element import NtpServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NtpServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NtpServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NtpServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NtpNode(Node):
    """Navigator for ntp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ntp:
        from ..data_models.ioa_network_element import Ntp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ntp.model_validate(resp)

    def update(self, data: ioa_network_element.Ntp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ntp

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

    def replace(self, data: ioa_network_element.Ntp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ntp

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
    def ntp_key(self) -> NtpKeyListNode:
        return NtpKeyListNode(self._client, f"{self._path}/ntp-key", "ntp-key", NtpKeyItemNode)

    @property
    def ntp_server(self) -> NtpServerListNode:
        return NtpServerListNode(self._client, f"{self._path}/ntp-server", "ntp-server", NtpServerItemNode)


class SwControlRuleItemNode(ItemNode):
    """Navigator for list item sw-control-rule"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwControlRuleItem:
        from ..data_models.ioa_network_element import SwControlRuleItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwControlRuleItem.model_validate(resp)

    def update(self, data: ioa_network_element.SwControlRuleItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwControlRuleItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwControlRuleItem.model_validate(data)
        elif isinstance(data, str):
            data = SwControlRuleItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SwControlRuleItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwControlRuleItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwControlRuleItem.model_validate(data)
        elif isinstance(data, str):
            data = SwControlRuleItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SwControlRuleListNode(ListNode[SwControlRuleItemNode]):
    """Navigator for list sw-control-rule"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SwControlRuleItem]:
        from ..data_models.ioa_network_element import SwControlRuleItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SwControlRuleItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SwControlRuleItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SwControlRuleItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SwServiceItemNode(ItemNode):
    """Navigator for list item sw-service"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwServiceItem:
        from ..data_models.ioa_network_element import SwServiceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwServiceItem.model_validate(resp)

    def update(self, data: ioa_network_element.SwServiceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwServiceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwServiceItem.model_validate(data)
        elif isinstance(data, str):
            data = SwServiceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SwServiceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwServiceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwServiceItem.model_validate(data)
        elif isinstance(data, str):
            data = SwServiceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SwServiceListNode(ListNode[SwServiceItemNode]):
    """Navigator for list sw-service"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SwServiceItem]:
        from ..data_models.ioa_network_element import SwServiceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SwServiceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SwServiceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SwServiceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SwContainerItemNode(ItemNode):
    """Navigator for list item sw-container"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwContainerItem:
        from ..data_models.ioa_network_element import SwContainerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwContainerItem.model_validate(resp)

    def update(self, data: ioa_network_element.SwContainerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwContainerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwContainerItem.model_validate(data)
        elif isinstance(data, str):
            data = SwContainerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SwContainerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwContainerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwContainerItem.model_validate(data)
        elif isinstance(data, str):
            data = SwContainerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SwContainerListNode(ListNode[SwContainerItemNode]):
    """Navigator for list sw-container"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SwContainerItem]:
        from ..data_models.ioa_network_element import SwContainerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SwContainerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SwContainerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SwContainerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SwServicesNode(Node):
    """Navigator for sw-services"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwServices:
        from ..data_models.ioa_network_element import SwServices

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwServices.model_validate(resp)

    def update(self, data: ioa_network_element.SwServices | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwServices

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwServices.model_validate(data)
        elif isinstance(data, str):
            data = SwServices.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.SwServices | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwServices

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwServices.model_validate(data)
        elif isinstance(data, str):
            data = SwServices.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def sw_control_rule(self) -> SwControlRuleListNode:
        return SwControlRuleListNode(
            self._client, f"{self._path}/sw-control-rule", "sw-control-rule", SwControlRuleItemNode
        )

    @property
    def sw_service(self) -> SwServiceListNode:
        return SwServiceListNode(self._client, f"{self._path}/sw-service", "sw-service", SwServiceItemNode)

    @property
    def sw_container(self) -> SwContainerListNode:
        return SwContainerListNode(self._client, f"{self._path}/sw-container", "sw-container", SwContainerItemNode)


class FileServerItemNode(ItemNode):
    """Navigator for list item file-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FileServerItem:
        from ..data_models.ioa_network_element import FileServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FileServerItem.model_validate(resp)

    def update(self, data: ioa_network_element.FileServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FileServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileServerItem.model_validate(data)
        elif isinstance(data, str):
            data = FileServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.FileServerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FileServerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileServerItem.model_validate(data)
        elif isinstance(data, str):
            data = FileServerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class FileServerListNode(ListNode[FileServerItemNode]):
    """Navigator for list file-server"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.FileServerItem]:
        from ..data_models.ioa_network_element import FileServerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FileServerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.FileServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.FileServerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FileServersNode(Node):
    """Navigator for file-servers"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FileServers:
        from ..data_models.ioa_network_element import FileServers

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FileServers.model_validate(resp)

    def update(self, data: ioa_network_element.FileServers | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FileServers

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileServers.model_validate(data)
        elif isinstance(data, str):
            data = FileServers.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.FileServers | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FileServers

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FileServers.model_validate(data)
        elif isinstance(data, str):
            data = FileServers.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def file_server(self) -> FileServerListNode:
        return FileServerListNode(self._client, f"{self._path}/file-server", "file-server", FileServerItemNode)


class UpgradeStatusItemNode(ItemNode):
    """Navigator for list item upgrade-status"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.UpgradeStatusItem:
        from ..data_models.ioa_network_element import UpgradeStatusItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return UpgradeStatusItem.model_validate(resp)

    def update(self, data: ioa_network_element.UpgradeStatusItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import UpgradeStatusItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UpgradeStatusItem.model_validate(data)
        elif isinstance(data, str):
            data = UpgradeStatusItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.UpgradeStatusItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import UpgradeStatusItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UpgradeStatusItem.model_validate(data)
        elif isinstance(data, str):
            data = UpgradeStatusItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class UpgradeStatusListNode(ListNode[UpgradeStatusItemNode]):
    """Navigator for list upgrade-status"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.UpgradeStatusItem]:
        from ..data_models.ioa_network_element import UpgradeStatusItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [UpgradeStatusItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.UpgradeStatusItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.UpgradeStatusItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SwSubcomponentItemNode(ItemNode):
    """Navigator for list item sw-subcomponent"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwSubcomponentItem:
        from ..data_models.ioa_network_element import SwSubcomponentItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwSubcomponentItem.model_validate(resp)

    def update(self, data: ioa_network_element.SwSubcomponentItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwSubcomponentItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwSubcomponentItem.model_validate(data)
        elif isinstance(data, str):
            data = SwSubcomponentItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SwSubcomponentItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwSubcomponentItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwSubcomponentItem.model_validate(data)
        elif isinstance(data, str):
            data = SwSubcomponentItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SwSubcomponentListNode(ListNode[SwSubcomponentItemNode]):
    """Navigator for list sw-subcomponent"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SwSubcomponentItem]:
        from ..data_models.ioa_network_element import SwSubcomponentItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SwSubcomponentItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SwSubcomponentItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SwSubcomponentItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SwComponentItemNode(ItemNode):
    """Navigator for list item sw-component"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwComponentItem:
        from ..data_models.ioa_network_element import SwComponentItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwComponentItem.model_validate(resp)

    def update(self, data: ioa_network_element.SwComponentItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwComponentItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwComponentItem.model_validate(data)
        elif isinstance(data, str):
            data = SwComponentItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SwComponentItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwComponentItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SwComponentItem.model_validate(data)
        elif isinstance(data, str):
            data = SwComponentItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def sw_subcomponent(self) -> SwSubcomponentListNode:
        return SwSubcomponentListNode(
            self._client, f"{self._path}/sw-subcomponent", "sw-subcomponent", SwSubcomponentItemNode
        )


class SwComponentListNode(ListNode[SwComponentItemNode]):
    """Navigator for list sw-component"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SwComponentItem]:
        from ..data_models.ioa_network_element import SwComponentItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SwComponentItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SwComponentItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SwComponentItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class PackagedFwItemNode(ItemNode):
    """Navigator for list item packaged-fw"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PackagedFwItem:
        from ..data_models.ioa_network_element import PackagedFwItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PackagedFwItem.model_validate(resp)

    def update(self, data: ioa_network_element.PackagedFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PackagedFwItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PackagedFwItem.model_validate(data)
        elif isinstance(data, str):
            data = PackagedFwItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.PackagedFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PackagedFwItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PackagedFwItem.model_validate(data)
        elif isinstance(data, str):
            data = PackagedFwItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PackagedFwListNode(ListNode[PackagedFwItemNode]):
    """Navigator for list packaged-fw"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.PackagedFwItem]:
        from ..data_models.ioa_network_element import PackagedFwItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PackagedFwItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.PackagedFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.PackagedFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SoftwareLoadItemNode(ItemNode):
    """Navigator for list item software-load"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SoftwareLoadItem:
        from ..data_models.ioa_network_element import SoftwareLoadItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SoftwareLoadItem.model_validate(resp)

    def update(self, data: ioa_network_element.SoftwareLoadItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SoftwareLoadItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SoftwareLoadItem.model_validate(data)
        elif isinstance(data, str):
            data = SoftwareLoadItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SoftwareLoadItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SoftwareLoadItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SoftwareLoadItem.model_validate(data)
        elif isinstance(data, str):
            data = SoftwareLoadItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def sw_component(self) -> SwComponentListNode:
        return SwComponentListNode(self._client, f"{self._path}/sw-component", "sw-component", SwComponentItemNode)

    @property
    def packaged_fw(self) -> PackagedFwListNode:
        return PackagedFwListNode(self._client, f"{self._path}/packaged-fw", "packaged-fw", PackagedFwItemNode)


class SoftwareLoadListNode(ListNode[SoftwareLoadItemNode]):
    """Navigator for list software-load"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SoftwareLoadItem]:
        from ..data_models.ioa_network_element import SoftwareLoadItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SoftwareLoadItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SoftwareLoadItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SoftwareLoadItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ManifestComponentItemNode(ItemNode):
    """Navigator for list item manifest-component"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ManifestComponentItem:
        from ..data_models.ioa_network_element import ManifestComponentItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ManifestComponentItem.model_validate(resp)

    def update(self, data: ioa_network_element.ManifestComponentItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ManifestComponentItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManifestComponentItem.model_validate(data)
        elif isinstance(data, str):
            data = ManifestComponentItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.ManifestComponentItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ManifestComponentItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManifestComponentItem.model_validate(data)
        elif isinstance(data, str):
            data = ManifestComponentItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ManifestComponentListNode(ListNode[ManifestComponentItemNode]):
    """Navigator for list manifest-component"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ManifestComponentItem]:
        from ..data_models.ioa_network_element import ManifestComponentItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ManifestComponentItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ManifestComponentItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ManifestComponentItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ManifestFirmwareItemNode(ItemNode):
    """Navigator for list item manifest-firmware"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ManifestFirmwareItem:
        from ..data_models.ioa_network_element import ManifestFirmwareItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ManifestFirmwareItem.model_validate(resp)

    def update(self, data: ioa_network_element.ManifestFirmwareItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ManifestFirmwareItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManifestFirmwareItem.model_validate(data)
        elif isinstance(data, str):
            data = ManifestFirmwareItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ManifestFirmwareItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ManifestFirmwareItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManifestFirmwareItem.model_validate(data)
        elif isinstance(data, str):
            data = ManifestFirmwareItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ManifestFirmwareListNode(ListNode[ManifestFirmwareItemNode]):
    """Navigator for list manifest-firmware"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ManifestFirmwareItem]:
        from ..data_models.ioa_network_element import ManifestFirmwareItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ManifestFirmwareItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ManifestFirmwareItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ManifestFirmwareItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class FruInfoItemNode(ItemNode):
    """Navigator for list item fru-info"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FruInfoItem:
        from ..data_models.ioa_network_element import FruInfoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FruInfoItem.model_validate(resp)

    def update(self, data: ioa_network_element.FruInfoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FruInfoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FruInfoItem.model_validate(data)
        elif isinstance(data, str):
            data = FruInfoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.FruInfoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FruInfoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = FruInfoItem.model_validate(data)
        elif isinstance(data, str):
            data = FruInfoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def manifest_component(self) -> ManifestComponentListNode:
        return ManifestComponentListNode(
            self._client, f"{self._path}/manifest-component", "manifest-component", ManifestComponentItemNode
        )

    @property
    def manifest_firmware(self) -> ManifestFirmwareListNode:
        return ManifestFirmwareListNode(
            self._client, f"{self._path}/manifest-firmware", "manifest-firmware", ManifestFirmwareItemNode
        )


class FruInfoListNode(ListNode[FruInfoItemNode]):
    """Navigator for list fru-info"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.FruInfoItem]:
        from ..data_models.ioa_network_element import FruInfoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FruInfoItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.FruInfoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.FruInfoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DownloadedImageItemNode(ItemNode):
    """Navigator for list item downloaded-image"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DownloadedImageItem:
        from ..data_models.ioa_network_element import DownloadedImageItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DownloadedImageItem.model_validate(resp)

    def update(self, data: ioa_network_element.DownloadedImageItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DownloadedImageItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DownloadedImageItem.model_validate(data)
        elif isinstance(data, str):
            data = DownloadedImageItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.DownloadedImageItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DownloadedImageItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DownloadedImageItem.model_validate(data)
        elif isinstance(data, str):
            data = DownloadedImageItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DownloadedImageListNode(ListNode[DownloadedImageItemNode]):
    """Navigator for list downloaded-image"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DownloadedImageItem]:
        from ..data_models.ioa_network_element import DownloadedImageItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DownloadedImageItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DownloadedImageItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DownloadedImageItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ManifestItemNode(ItemNode):
    """Navigator for list item manifest"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ManifestItem:
        from ..data_models.ioa_network_element import ManifestItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ManifestItem.model_validate(resp)

    def update(self, data: ioa_network_element.ManifestItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ManifestItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManifestItem.model_validate(data)
        elif isinstance(data, str):
            data = ManifestItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ManifestItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ManifestItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManifestItem.model_validate(data)
        elif isinstance(data, str):
            data = ManifestItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def fru_info(self) -> FruInfoListNode:
        return FruInfoListNode(self._client, f"{self._path}/fru-info", "fru-info", FruInfoItemNode)

    @property
    def downloaded_image(self) -> DownloadedImageListNode:
        return DownloadedImageListNode(
            self._client, f"{self._path}/downloaded-image", "downloaded-image", DownloadedImageItemNode
        )


class ManifestListNode(ListNode[ManifestItemNode]):
    """Navigator for list manifest"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ManifestItem]:
        from ..data_models.ioa_network_element import ManifestItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ManifestItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ManifestItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ManifestItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DownloadsNode(Node):
    """Navigator for downloads"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Downloads:
        from ..data_models.ioa_network_element import Downloads

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Downloads.model_validate(resp)

    def update(self, data: ioa_network_element.Downloads | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Downloads

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Downloads.model_validate(data)
        elif isinstance(data, str):
            data = Downloads.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Downloads | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Downloads

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Downloads.model_validate(data)
        elif isinstance(data, str):
            data = Downloads.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def manifest(self) -> ManifestListNode:
        return ManifestListNode(self._client, f"{self._path}/manifest", "manifest", ManifestItemNode)


class ThirdPartyAppInfoItemNode(ItemNode):
    """Navigator for list item third-party-app-info"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ThirdPartyAppInfoItem:
        from ..data_models.ioa_network_element import ThirdPartyAppInfoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ThirdPartyAppInfoItem.model_validate(resp)

    def update(self, data: ioa_network_element.ThirdPartyAppInfoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ThirdPartyAppInfoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ThirdPartyAppInfoItem.model_validate(data)
        elif isinstance(data, str):
            data = ThirdPartyAppInfoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.ThirdPartyAppInfoItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ThirdPartyAppInfoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ThirdPartyAppInfoItem.model_validate(data)
        elif isinstance(data, str):
            data = ThirdPartyAppInfoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ThirdPartyAppInfoListNode(ListNode[ThirdPartyAppInfoItemNode]):
    """Navigator for list third-party-app-info"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ThirdPartyAppInfoItem]:
        from ..data_models.ioa_network_element import ThirdPartyAppInfoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ThirdPartyAppInfoItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ThirdPartyAppInfoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ThirdPartyAppInfoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SoftwareLocationItemNode(ItemNode):
    """Navigator for list item software-location"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SoftwareLocationItem:
        from ..data_models.ioa_network_element import SoftwareLocationItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SoftwareLocationItem.model_validate(resp)

    def update(self, data: ioa_network_element.SoftwareLocationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SoftwareLocationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SoftwareLocationItem.model_validate(data)
        elif isinstance(data, str):
            data = SoftwareLocationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SoftwareLocationItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SoftwareLocationItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SoftwareLocationItem.model_validate(data)
        elif isinstance(data, str):
            data = SoftwareLocationItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def software_load(self) -> SoftwareLoadListNode:
        return SoftwareLoadListNode(self._client, f"{self._path}/software-load", "software-load", SoftwareLoadItemNode)

    @property
    def third_party_app_info(self) -> ThirdPartyAppInfoListNode:
        return ThirdPartyAppInfoListNode(
            self._client, f"{self._path}/third-party-app-info", "third-party-app-info", ThirdPartyAppInfoItemNode
        )


class SoftwareLocationListNode(ListNode[SoftwareLocationItemNode]):
    """Navigator for list software-location"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SoftwareLocationItem]:
        from ..data_models.ioa_network_element import SoftwareLocationItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SoftwareLocationItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SoftwareLocationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SoftwareLocationItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ThirdPartyAppItemNode(ItemNode):
    """Navigator for list item third-party-app"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ThirdPartyAppItem:
        from ..data_models.ioa_network_element import ThirdPartyAppItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ThirdPartyAppItem.model_validate(resp)

    def update(self, data: ioa_network_element.ThirdPartyAppItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ThirdPartyAppItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ThirdPartyAppItem.model_validate(data)
        elif isinstance(data, str):
            data = ThirdPartyAppItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ThirdPartyAppItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ThirdPartyAppItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ThirdPartyAppItem.model_validate(data)
        elif isinstance(data, str):
            data = ThirdPartyAppItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ThirdPartyAppListNode(ListNode[ThirdPartyAppItemNode]):
    """Navigator for list third-party-app"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ThirdPartyAppItem]:
        from ..data_models.ioa_network_element import ThirdPartyAppItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ThirdPartyAppItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ThirdPartyAppItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ThirdPartyAppItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ThirdPartyFwItemNode(ItemNode):
    """Navigator for list item third-party-fw"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ThirdPartyFwItem:
        from ..data_models.ioa_network_element import ThirdPartyFwItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ThirdPartyFwItem.model_validate(resp)

    def update(self, data: ioa_network_element.ThirdPartyFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ThirdPartyFwItem

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

    def replace(self, data: ioa_network_element.ThirdPartyFwItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ThirdPartyFwItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ThirdPartyFwItem]:
        from ..data_models.ioa_network_element import ThirdPartyFwItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ThirdPartyFwItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ThirdPartyFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ThirdPartyFwItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SwManagementNode(Node):
    """Navigator for sw-management"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SwManagement:
        from ..data_models.ioa_network_element import SwManagement

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SwManagement.model_validate(resp)

    def update(self, data: ioa_network_element.SwManagement | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwManagement

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

    def replace(self, data: ioa_network_element.SwManagement | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SwManagement

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
    def upgrade_status(self) -> UpgradeStatusListNode:
        return UpgradeStatusListNode(
            self._client, f"{self._path}/upgrade-status", "upgrade-status", UpgradeStatusItemNode
        )

    @property
    def software_load(self) -> SoftwareLoadListNode:
        return SoftwareLoadListNode(self._client, f"{self._path}/software-load", "software-load", SoftwareLoadItemNode)

    @property
    def downloads(self) -> DownloadsNode:
        return DownloadsNode(self._client, f"{self._path}/downloads", "downloads")

    @property
    def software_location(self) -> SoftwareLocationListNode:
        return SoftwareLocationListNode(
            self._client, f"{self._path}/software-location", "software-location", SoftwareLocationItemNode
        )

    @property
    def third_party_app(self) -> ThirdPartyAppListNode:
        return ThirdPartyAppListNode(
            self._client, f"{self._path}/third-party-app", "third-party-app", ThirdPartyAppItemNode
        )

    @property
    def third_party_fw(self) -> ThirdPartyFwListNode:
        return ThirdPartyFwListNode(
            self._client, f"{self._path}/third-party-fw", "third-party-fw", ThirdPartyFwItemNode
        )


class DatabaseItemNode(ItemNode):
    """Navigator for list item database"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DatabaseItem:
        from ..data_models.ioa_network_element import DatabaseItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DatabaseItem.model_validate(resp)

    def update(self, data: ioa_network_element.DatabaseItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DatabaseItem

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

    def replace(self, data: ioa_network_element.DatabaseItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DatabaseItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DatabaseItem]:
        from ..data_models.ioa_network_element import DatabaseItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DatabaseItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DatabaseItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DatabaseItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SubscriptionPathItemNode(ItemNode):
    """Navigator for list item subscription-path"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SubscriptionPathItem:
        from ..data_models.ioa_network_element import SubscriptionPathItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SubscriptionPathItem.model_validate(resp)

    def update(self, data: ioa_network_element.SubscriptionPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SubscriptionPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubscriptionPathItem.model_validate(data)
        elif isinstance(data, str):
            data = SubscriptionPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SubscriptionPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SubscriptionPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubscriptionPathItem.model_validate(data)
        elif isinstance(data, str):
            data = SubscriptionPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SubscriptionPathListNode(ListNode[SubscriptionPathItemNode]):
    """Navigator for list subscription-path"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SubscriptionPathItem]:
        from ..data_models.ioa_network_element import SubscriptionPathItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SubscriptionPathItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SubscriptionPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SubscriptionPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CurrentSubscriptionItemNode(ItemNode):
    """Navigator for list item current-subscription"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CurrentSubscriptionItem:
        from ..data_models.ioa_network_element import CurrentSubscriptionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CurrentSubscriptionItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.CurrentSubscriptionItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import CurrentSubscriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentSubscriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentSubscriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.CurrentSubscriptionItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import CurrentSubscriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CurrentSubscriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = CurrentSubscriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def subscription_path(self) -> SubscriptionPathListNode:
        return SubscriptionPathListNode(
            self._client, f"{self._path}/subscription-path", "subscription-path", SubscriptionPathItemNode
        )


class CurrentSubscriptionListNode(ListNode[CurrentSubscriptionItemNode]):
    """Navigator for list current-subscription"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CurrentSubscriptionItem]:
        from ..data_models.ioa_network_element import CurrentSubscriptionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CurrentSubscriptionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CurrentSubscriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CurrentSubscriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SubscriptionsNode(Node):
    """Navigator for subscriptions"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Subscriptions:
        from ..data_models.ioa_network_element import Subscriptions

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Subscriptions.model_validate(resp)

    def update(self, data: ioa_network_element.Subscriptions | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Subscriptions

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

    def replace(self, data: ioa_network_element.Subscriptions | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Subscriptions

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
    def current_subscription(self) -> CurrentSubscriptionListNode:
        return CurrentSubscriptionListNode(
            self._client, f"{self._path}/current-subscription", "current-subscription", CurrentSubscriptionItemNode
        )


class TelemetryNode(Node):
    """Navigator for telemetry"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Telemetry:
        from ..data_models.ioa_network_element import Telemetry

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Telemetry.model_validate(resp)

    def update(self, data: ioa_network_element.Telemetry | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Telemetry

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Telemetry.model_validate(data)
        elif isinstance(data, str):
            data = Telemetry.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Telemetry | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Telemetry

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Telemetry.model_validate(data)
        elif isinstance(data, str):
            data = Telemetry.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def subscriptions(self) -> SubscriptionsNode:
        return SubscriptionsNode(self._client, f"{self._path}/subscriptions", "subscriptions")


class RecoveryNode(Node):
    """Navigator for recovery"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Recovery:
        from ..data_models.ioa_network_element import Recovery

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Recovery.model_validate(resp)

    def update(self, data: ioa_network_element.Recovery | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Recovery

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Recovery.model_validate(data)
        elif isinstance(data, str):
            data = Recovery.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Recovery | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Recovery

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Recovery.model_validate(data)
        elif isinstance(data, str):
            data = Recovery.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class TemplateItemNode(ItemNode):
    """Navigator for list item template"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TemplateItem:
        from ..data_models.ioa_network_element import TemplateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TemplateItem.model_validate(resp)

    def update(self, data: ioa_network_element.TemplateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TemplateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TemplateItem.model_validate(data)
        elif isinstance(data, str):
            data = TemplateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.TemplateItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TemplateItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TemplateItem.model_validate(data)
        elif isinstance(data, str):
            data = TemplateItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TemplateListNode(ListNode[TemplateItemNode]):
    """Navigator for list template"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TemplateItem]:
        from ..data_models.ioa_network_element import TemplateItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TemplateItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TemplateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TemplateItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class TemplateGroupItemNode(ItemNode):
    """Navigator for list item template-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TemplateGroupItem:
        from ..data_models.ioa_network_element import TemplateGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TemplateGroupItem.model_validate(resp)

    def update(self, data: ioa_network_element.TemplateGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TemplateGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TemplateGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = TemplateGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.TemplateGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TemplateGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TemplateGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = TemplateGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def template(self) -> TemplateListNode:
        return TemplateListNode(self._client, f"{self._path}/template", "template", TemplateItemNode)


class TemplateGroupListNode(ListNode[TemplateGroupItemNode]):
    """Navigator for list template-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TemplateGroupItem]:
        from ..data_models.ioa_network_element import TemplateGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TemplateGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TemplateGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TemplateGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class TemplatesNode(Node):
    """Navigator for templates"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Templates:
        from ..data_models.ioa_network_element import Templates

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Templates.model_validate(resp)

    def update(self, data: ioa_network_element.Templates | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Templates

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Templates.model_validate(data)
        elif isinstance(data, str):
            data = Templates.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Templates | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Templates

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Templates.model_validate(data)
        elif isinstance(data, str):
            data = Templates.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def template_group(self) -> TemplateGroupListNode:
        return TemplateGroupListNode(
            self._client, f"{self._path}/template-group", "template-group", TemplateGroupItemNode
        )


class SystemPoliciesNode(Node):
    """Navigator for system-policies"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SystemPolicies:
        from ..data_models.ioa_network_element import SystemPolicies

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SystemPolicies.model_validate(resp)

    def update(self, data: ioa_network_element.SystemPolicies | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SystemPolicies

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SystemPolicies.model_validate(data)
        elif isinstance(data, str):
            data = SystemPolicies.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.SystemPolicies | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SystemPolicies

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SystemPolicies.model_validate(data)
        elif isinstance(data, str):
            data = SystemPolicies.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SystemSystemNode(Node):
    """Navigator for system"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SystemSystem:
        from ..data_models.ioa_network_element import SystemSystem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SystemSystem.model_validate(resp)

    def update(self, data: ioa_network_element.SystemSystem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SystemSystem

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

    def replace(self, data: ioa_network_element.SystemSystem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SystemSystem

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
    def security(self) -> SecurityNode:
        return SecurityNode(self._client, f"{self._path}/security", "security")

    @property
    def syslog(self) -> SyslogNode:
        return SyslogNode(self._client, f"{self._path}/syslog", "syslog")

    @property
    def protocols(self) -> ProtocolsNode:
        return ProtocolsNode(self._client, f"{self._path}/protocols", "protocols")

    @property
    def scheduled_tasks(self) -> ScheduledTasksNode:
        return ScheduledTasksNode(self._client, f"{self._path}/scheduled-tasks", "scheduled-tasks")

    @property
    def ztp(self) -> ZtpNode:
        return ZtpNode(self._client, f"{self._path}/ztp", "ztp")

    @property
    def transfer(self) -> TransferNode:
        return TransferNode(self._client, f"{self._path}/transfer", "transfer")

    @property
    def networking(self) -> NetworkingNode:
        return NetworkingNode(self._client, f"{self._path}/networking", "networking")

    @property
    def clock(self) -> ClockNode:
        return ClockNode(self._client, f"{self._path}/clock", "clock")

    @property
    def ntp(self) -> NtpNode:
        return NtpNode(self._client, f"{self._path}/ntp", "ntp")

    @property
    def sw_services(self) -> SwServicesNode:
        return SwServicesNode(self._client, f"{self._path}/sw-services", "sw-services")

    @property
    def file_servers(self) -> FileServersNode:
        return FileServersNode(self._client, f"{self._path}/file-servers", "file-servers")

    @property
    def sw_management(self) -> SwManagementNode:
        return SwManagementNode(self._client, f"{self._path}/sw-management", "sw-management")

    @property
    def database(self) -> DatabaseListNode:
        return DatabaseListNode(self._client, f"{self._path}/database", "database", DatabaseItemNode)

    @property
    def telemetry(self) -> TelemetryNode:
        return TelemetryNode(self._client, f"{self._path}/telemetry", "telemetry")

    @property
    def recovery(self) -> RecoveryNode:
        return RecoveryNode(self._client, f"{self._path}/recovery", "recovery")

    @property
    def templates(self) -> TemplatesNode:
        return TemplatesNode(self._client, f"{self._path}/templates", "templates")

    @property
    def system_policies(self) -> SystemPoliciesNode:
        return SystemPoliciesNode(self._client, f"{self._path}/system-policies", "system-policies")


class SupportedGainRangeItemNode(ItemNode):
    """Navigator for list item supported-gain-range"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedGainRangeItem:
        from ..data_models.ioa_network_element import SupportedGainRangeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedGainRangeItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SupportedGainRangeItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportedGainRangeItem

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

    def replace(
        self, data: ioa_network_element.SupportedGainRangeItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportedGainRangeItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedGainRangeItem]:
        from ..data_models.ioa_network_element import SupportedGainRangeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedGainRangeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedGainRangeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedGainRangeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AmplifierItemNode(ItemNode):
    """Navigator for list item amplifier"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AmplifierItem:
        from ..data_models.ioa_network_element import AmplifierItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AmplifierItem.model_validate(resp)

    def update(self, data: ioa_network_element.AmplifierItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AmplifierItem

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

    def replace(self, data: ioa_network_element.AmplifierItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AmplifierItem

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
        return SupportedGainRangeListNode(
            self._client, f"{self._path}/supported-gain-range", "supported-gain-range", SupportedGainRangeItemNode
        )


class AmplifierListNode(ListNode[AmplifierItemNode]):
    """Navigator for list amplifier"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AmplifierItem]:
        from ..data_models.ioa_network_element import AmplifierItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AmplifierItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AmplifierItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AmplifierItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class PumpPowerItemNode(ItemNode):
    """Navigator for list item pump-power"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.PumpPowerItem:
        from ..data_models.ioa_network_element import PumpPowerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PumpPowerItem.model_validate(resp)

    def update(self, data: ioa_network_element.PumpPowerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PumpPowerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PumpPowerItem.model_validate(data)
        elif isinstance(data, str):
            data = PumpPowerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.PumpPowerItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import PumpPowerItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PumpPowerItem.model_validate(data)
        elif isinstance(data, str):
            data = PumpPowerItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PumpPowerListNode(ListNode[PumpPowerItemNode]):
    """Navigator for list pump-power"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.PumpPowerItem]:
        from ..data_models.ioa_network_element import PumpPowerItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PumpPowerItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.PumpPowerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.PumpPowerItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AmplifierRamanItemNode(ItemNode):
    """Navigator for list item amplifier-raman"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AmplifierRamanItem:
        from ..data_models.ioa_network_element import AmplifierRamanItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AmplifierRamanItem.model_validate(resp)

    def update(self, data: ioa_network_element.AmplifierRamanItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AmplifierRamanItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AmplifierRamanItem.model_validate(data)
        elif isinstance(data, str):
            data = AmplifierRamanItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AmplifierRamanItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AmplifierRamanItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AmplifierRamanItem.model_validate(data)
        elif isinstance(data, str):
            data = AmplifierRamanItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def pump_power(self) -> PumpPowerListNode:
        return PumpPowerListNode(self._client, f"{self._path}/pump-power", "pump-power", PumpPowerItemNode)


class AmplifierRamanListNode(ListNode[AmplifierRamanItemNode]):
    """Navigator for list amplifier-raman"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AmplifierRamanItem]:
        from ..data_models.ioa_network_element import AmplifierRamanItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AmplifierRamanItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AmplifierRamanItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AmplifierRamanItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AmplifierTofItemNode(ItemNode):
    """Navigator for list item amplifier-tof"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AmplifierTofItem:
        from ..data_models.ioa_network_element import AmplifierTofItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AmplifierTofItem.model_validate(resp)

    def update(self, data: ioa_network_element.AmplifierTofItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AmplifierTofItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AmplifierTofItem.model_validate(data)
        elif isinstance(data, str):
            data = AmplifierTofItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AmplifierTofItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AmplifierTofItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AmplifierTofItem.model_validate(data)
        elif isinstance(data, str):
            data = AmplifierTofItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AmplifierTofListNode(ListNode[AmplifierTofItemNode]):
    """Navigator for list amplifier-tof"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AmplifierTofItem]:
        from ..data_models.ioa_network_element import AmplifierTofItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AmplifierTofItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AmplifierTofItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AmplifierTofItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ConnectionPortsItemNode(ItemNode):
    """Navigator for list item connection-ports"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ConnectionPortsItem:
        from ..data_models.ioa_network_element import ConnectionPortsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ConnectionPortsItem.model_validate(resp)

    def update(self, data: ioa_network_element.ConnectionPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ConnectionPortsItem

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

    def replace(self, data: ioa_network_element.ConnectionPortsItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ConnectionPortsItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ConnectionPortsItem]:
        from ..data_models.ioa_network_element import ConnectionPortsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ConnectionPortsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ConnectionPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ConnectionPortsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ModulesDegreeItemNode(ItemNode):
    """Navigator for list item modules-degree"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ModulesDegreeItem:
        from ..data_models.ioa_network_element import ModulesDegreeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ModulesDegreeItem.model_validate(resp)

    def update(self, data: ioa_network_element.ModulesDegreeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ModulesDegreeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModulesDegreeItem.model_validate(data)
        elif isinstance(data, str):
            data = ModulesDegreeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ModulesDegreeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ModulesDegreeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModulesDegreeItem.model_validate(data)
        elif isinstance(data, str):
            data = ModulesDegreeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ModulesDegreeListNode(ListNode[ModulesDegreeItemNode]):
    """Navigator for list modules-degree"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ModulesDegreeItem]:
        from ..data_models.ioa_network_element import ModulesDegreeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ModulesDegreeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ModulesDegreeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ModulesDegreeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DegreeItemNode(ItemNode):
    """Navigator for list item degree"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DegreeItem:
        from ..data_models.ioa_network_element import DegreeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DegreeItem.model_validate(resp)

    def update(self, data: ioa_network_element.DegreeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DegreeItem

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

    def replace(self, data: ioa_network_element.DegreeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DegreeItem

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
    def connection_ports(self) -> ConnectionPortsListNode:
        return ConnectionPortsListNode(
            self._client, f"{self._path}/connection-ports", "connection-ports", ConnectionPortsItemNode
        )

    @property
    def modules_degree(self) -> ModulesDegreeListNode:
        return ModulesDegreeListNode(
            self._client, f"{self._path}/modules-degree", "modules-degree", ModulesDegreeItemNode
        )


class DegreeListNode(ListNode[DegreeItemNode]):
    """Navigator for list degree"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DegreeItem]:
        from ..data_models.ioa_network_element import DegreeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DegreeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DegreeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DegreeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class DirectionItemNode(ItemNode):
    """Navigator for list item direction"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.DirectionItem:
        from ..data_models.ioa_network_element import DirectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DirectionItem.model_validate(resp)

    def update(self, data: ioa_network_element.DirectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DirectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DirectionItem.model_validate(data)
        elif isinstance(data, str):
            data = DirectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.DirectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import DirectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DirectionItem.model_validate(data)
        elif isinstance(data, str):
            data = DirectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DirectionListNode(ListNode[DirectionItemNode]):
    """Navigator for list direction"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.DirectionItem]:
        from ..data_models.ioa_network_element import DirectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DirectionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.DirectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.DirectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ModulesAdgItemNode(ItemNode):
    """Navigator for list item modules-adg"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ModulesAdgItem:
        from ..data_models.ioa_network_element import ModulesAdgItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ModulesAdgItem.model_validate(resp)

    def update(self, data: ioa_network_element.ModulesAdgItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ModulesAdgItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModulesAdgItem.model_validate(data)
        elif isinstance(data, str):
            data = ModulesAdgItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ModulesAdgItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ModulesAdgItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ModulesAdgItem.model_validate(data)
        elif isinstance(data, str):
            data = ModulesAdgItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ModulesAdgListNode(ListNode[ModulesAdgItemNode]):
    """Navigator for list modules-adg"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ModulesAdgItem]:
        from ..data_models.ioa_network_element import ModulesAdgItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ModulesAdgItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ModulesAdgItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ModulesAdgItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AdgItemNode(ItemNode):
    """Navigator for list item adg"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AdgItem:
        from ..data_models.ioa_network_element import AdgItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AdgItem.model_validate(resp)

    def update(self, data: ioa_network_element.AdgItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AdgItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AdgItem.model_validate(data)
        elif isinstance(data, str):
            data = AdgItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AdgItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AdgItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AdgItem.model_validate(data)
        elif isinstance(data, str):
            data = AdgItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def modules_adg(self) -> ModulesAdgListNode:
        return ModulesAdgListNode(self._client, f"{self._path}/modules-adg", "modules-adg", ModulesAdgItemNode)


class AdgListNode(ListNode[AdgItemNode]):
    """Navigator for list adg"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AdgItem]:
        from ..data_models.ioa_network_element import AdgItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AdgItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AdgItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AdgItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AseIdlerServiceItemNode(ItemNode):
    """Navigator for list item ase-idler-service"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AseIdlerServiceItem:
        from ..data_models.ioa_network_element import AseIdlerServiceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AseIdlerServiceItem.model_validate(resp)

    def update(self, data: ioa_network_element.AseIdlerServiceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AseIdlerServiceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AseIdlerServiceItem.model_validate(data)
        elif isinstance(data, str):
            data = AseIdlerServiceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AseIdlerServiceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AseIdlerServiceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AseIdlerServiceItem.model_validate(data)
        elif isinstance(data, str):
            data = AseIdlerServiceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AseIdlerServiceListNode(ListNode[AseIdlerServiceItemNode]):
    """Navigator for list ase-idler-service"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AseIdlerServiceItem]:
        from ..data_models.ioa_network_element import AseIdlerServiceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AseIdlerServiceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AseIdlerServiceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AseIdlerServiceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AseIdlerSourceItemNode(ItemNode):
    """Navigator for list item ase-idler-source"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AseIdlerSourceItem:
        from ..data_models.ioa_network_element import AseIdlerSourceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AseIdlerSourceItem.model_validate(resp)

    def update(self, data: ioa_network_element.AseIdlerSourceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AseIdlerSourceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AseIdlerSourceItem.model_validate(data)
        elif isinstance(data, str):
            data = AseIdlerSourceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AseIdlerSourceItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AseIdlerSourceItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AseIdlerSourceItem.model_validate(data)
        elif isinstance(data, str):
            data = AseIdlerSourceItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AseIdlerSourceListNode(ListNode[AseIdlerSourceItemNode]):
    """Navigator for list ase-idler-source"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AseIdlerSourceItem]:
        from ..data_models.ioa_network_element import AseIdlerSourceItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AseIdlerSourceItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AseIdlerSourceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AseIdlerSourceItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OtdrItemNode(ItemNode):
    """Navigator for list item otdr"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OtdrItem:
        from ..data_models.ioa_network_element import OtdrItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OtdrItem.model_validate(resp)

    def update(self, data: ioa_network_element.OtdrItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtdrItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtdrItem.model_validate(data)
        elif isinstance(data, str):
            data = OtdrItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OtdrItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OtdrItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OtdrItem.model_validate(data)
        elif isinstance(data, str):
            data = OtdrItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OtdrListNode(ListNode[OtdrItemNode]):
    """Navigator for list otdr"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OtdrItem]:
        from ..data_models.ioa_network_element import OtdrItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OtdrItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OtdrItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OtdrItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NeFunctionNode(Node):
    """Navigator for ne-function"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NeFunction:
        from ..data_models.ioa_network_element import NeFunction

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NeFunction.model_validate(resp)

    def update(self, data: ioa_network_element.NeFunction | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NeFunction

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NeFunction.model_validate(data)
        elif isinstance(data, str):
            data = NeFunction.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.NeFunction | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NeFunction

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NeFunction.model_validate(data)
        elif isinstance(data, str):
            data = NeFunction.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def amplifier(self) -> AmplifierListNode:
        return AmplifierListNode(self._client, f"{self._path}/amplifier", "amplifier", AmplifierItemNode)

    @property
    def amplifier_raman(self) -> AmplifierRamanListNode:
        return AmplifierRamanListNode(
            self._client, f"{self._path}/amplifier-raman", "amplifier-raman", AmplifierRamanItemNode
        )

    @property
    def amplifier_tof(self) -> AmplifierTofListNode:
        return AmplifierTofListNode(self._client, f"{self._path}/amplifier-tof", "amplifier-tof", AmplifierTofItemNode)

    @property
    def degree(self) -> DegreeListNode:
        return DegreeListNode(self._client, f"{self._path}/degree", "degree", DegreeItemNode)

    @property
    def direction(self) -> DirectionListNode:
        return DirectionListNode(self._client, f"{self._path}/direction", "direction", DirectionItemNode)

    @property
    def adg(self) -> AdgListNode:
        return AdgListNode(self._client, f"{self._path}/adg", "adg", AdgItemNode)

    @property
    def ase_idler_service(self) -> AseIdlerServiceListNode:
        return AseIdlerServiceListNode(
            self._client, f"{self._path}/ase-idler-service", "ase-idler-service", AseIdlerServiceItemNode
        )

    @property
    def ase_idler_source(self) -> AseIdlerSourceListNode:
        return AseIdlerSourceListNode(
            self._client, f"{self._path}/ase-idler-source", "ase-idler-source", AseIdlerSourceItemNode
        )

    @property
    def otdr(self) -> OtdrListNode:
        return OtdrListNode(self._client, f"{self._path}/otdr", "otdr", OtdrItemNode)


class ManagementAddressLocalItemNode(ItemNode):
    """Navigator for list item management-address-local"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ManagementAddressLocalItem:
        from ..data_models.ioa_network_element import ManagementAddressLocalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ManagementAddressLocalItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.ManagementAddressLocalItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ManagementAddressLocalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManagementAddressLocalItem.model_validate(data)
        elif isinstance(data, str):
            data = ManagementAddressLocalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.ManagementAddressLocalItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ManagementAddressLocalItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManagementAddressLocalItem.model_validate(data)
        elif isinstance(data, str):
            data = ManagementAddressLocalItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ManagementAddressLocalListNode(ListNode[ManagementAddressLocalItemNode]):
    """Navigator for list management-address-local"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ManagementAddressLocalItem]:
        from ..data_models.ioa_network_element import ManagementAddressLocalItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ManagementAddressLocalItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ManagementAddressLocalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ManagementAddressLocalItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LldpLocalInfoItemNode(ItemNode):
    """Navigator for list item lldp-local-info"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LldpLocalInfoItem:
        from ..data_models.ioa_network_element import LldpLocalInfoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LldpLocalInfoItem.model_validate(resp)

    def update(self, data: ioa_network_element.LldpLocalInfoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LldpLocalInfoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpLocalInfoItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpLocalInfoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.LldpLocalInfoItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LldpLocalInfoItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpLocalInfoItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpLocalInfoItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def management_address_local(self) -> ManagementAddressLocalListNode:
        return ManagementAddressLocalListNode(
            self._client,
            f"{self._path}/management-address-local",
            "management-address-local",
            ManagementAddressLocalItemNode,
        )


class LldpLocalInfoListNode(ListNode[LldpLocalInfoItemNode]):
    """Navigator for list lldp-local-info"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LldpLocalInfoItem]:
        from ..data_models.ioa_network_element import LldpLocalInfoItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LldpLocalInfoItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LldpLocalInfoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LldpLocalInfoItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ManagementAddressItemNode(ItemNode):
    """Navigator for list item management-address"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ManagementAddressItem:
        from ..data_models.ioa_network_element import ManagementAddressItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ManagementAddressItem.model_validate(resp)

    def update(self, data: ioa_network_element.ManagementAddressItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ManagementAddressItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManagementAddressItem.model_validate(data)
        elif isinstance(data, str):
            data = ManagementAddressItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.ManagementAddressItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ManagementAddressItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ManagementAddressItem.model_validate(data)
        elif isinstance(data, str):
            data = ManagementAddressItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ManagementAddressListNode(ListNode[ManagementAddressItemNode]):
    """Navigator for list management-address"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ManagementAddressItem]:
        from ..data_models.ioa_network_element import ManagementAddressItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ManagementAddressItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ManagementAddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ManagementAddressItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CustomTlvItemNode(ItemNode):
    """Navigator for list item custom-tlv"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CustomTlvItem:
        from ..data_models.ioa_network_element import CustomTlvItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CustomTlvItem.model_validate(resp)

    def update(self, data: ioa_network_element.CustomTlvItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CustomTlvItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CustomTlvItem.model_validate(data)
        elif isinstance(data, str):
            data = CustomTlvItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CustomTlvItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CustomTlvItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CustomTlvItem.model_validate(data)
        elif isinstance(data, str):
            data = CustomTlvItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CustomTlvListNode(ListNode[CustomTlvItemNode]):
    """Navigator for list custom-tlv"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CustomTlvItem]:
        from ..data_models.ioa_network_element import CustomTlvItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CustomTlvItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CustomTlvItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CustomTlvItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LldpNeighborItemNode(ItemNode):
    """Navigator for list item lldp-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LldpNeighborItem:
        from ..data_models.ioa_network_element import LldpNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LldpNeighborItem.model_validate(resp)

    def update(self, data: ioa_network_element.LldpNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LldpNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.LldpNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import LldpNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def management_address(self) -> ManagementAddressListNode:
        return ManagementAddressListNode(
            self._client, f"{self._path}/management-address", "management-address", ManagementAddressItemNode
        )

    @property
    def custom_tlv(self) -> CustomTlvListNode:
        return CustomTlvListNode(self._client, f"{self._path}/custom-tlv", "custom-tlv", CustomTlvItemNode)


class LldpNeighborListNode(ListNode[LldpNeighborItemNode]):
    """Navigator for list lldp-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LldpNeighborItem]:
        from ..data_models.ioa_network_element import LldpNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LldpNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LldpNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LldpNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LldpPortStatisticsItemNode(ItemNode):
    """Navigator for list item lldp-port-statistics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.LldpPortStatisticsItem:
        from ..data_models.ioa_network_element import LldpPortStatisticsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return LldpPortStatisticsItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.LldpPortStatisticsItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LldpPortStatisticsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpPortStatisticsItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpPortStatisticsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.LldpPortStatisticsItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import LldpPortStatisticsItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = LldpPortStatisticsItem.model_validate(data)
        elif isinstance(data, str):
            data = LldpPortStatisticsItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class LldpPortStatisticsListNode(ListNode[LldpPortStatisticsItemNode]):
    """Navigator for list lldp-port-statistics"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.LldpPortStatisticsItem]:
        from ..data_models.ioa_network_element import LldpPortStatisticsItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [LldpPortStatisticsItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.LldpPortStatisticsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.LldpPortStatisticsItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LldpNode(Node):
    """Navigator for lldp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Lldp:
        from ..data_models.ioa_network_element import Lldp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Lldp.model_validate(resp)

    def update(self, data: ioa_network_element.Lldp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Lldp

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

    def replace(self, data: ioa_network_element.Lldp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Lldp

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

    @property
    def lldp_local_info(self) -> LldpLocalInfoListNode:
        return LldpLocalInfoListNode(
            self._client, f"{self._path}/lldp-local-info", "lldp-local-info", LldpLocalInfoItemNode
        )

    @property
    def lldp_neighbor(self) -> LldpNeighborListNode:
        return LldpNeighborListNode(self._client, f"{self._path}/lldp-neighbor", "lldp-neighbor", LldpNeighborItemNode)

    @property
    def lldp_port_statistics(self) -> LldpPortStatisticsListNode:
        return LldpPortStatisticsListNode(
            self._client, f"{self._path}/lldp-port-statistics", "lldp-port-statistics", LldpPortStatisticsItemNode
        )


class CarrierNeighborItemNode(ItemNode):
    """Navigator for list item carrier-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CarrierNeighborItem:
        from ..data_models.ioa_network_element import CarrierNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CarrierNeighborItem.model_validate(resp)

    def update(self, data: ioa_network_element.CarrierNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CarrierNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CarrierNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = CarrierNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CarrierNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CarrierNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CarrierNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = CarrierNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CarrierNeighborListNode(ListNode[CarrierNeighborItemNode]):
    """Navigator for list carrier-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CarrierNeighborItem]:
        from ..data_models.ioa_network_element import CarrierNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CarrierNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CarrierNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CarrierNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class IcdpNode(Node):
    """Navigator for icdp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Icdp:
        from ..data_models.ioa_network_element import Icdp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Icdp.model_validate(resp)

    def update(self, data: ioa_network_element.Icdp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Icdp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Icdp.model_validate(data)
        elif isinstance(data, str):
            data = Icdp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Icdp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Icdp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Icdp.model_validate(data)
        elif isinstance(data, str):
            data = Icdp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def carrier_neighbor(self) -> CarrierNeighborListNode:
        return CarrierNeighborListNode(
            self._client, f"{self._path}/carrier-neighbor", "carrier-neighbor", CarrierNeighborItemNode
        )


class InciNeighborItemNode(ItemNode):
    """Navigator for list item inci-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.InciNeighborItem:
        from ..data_models.ioa_network_element import InciNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InciNeighborItem.model_validate(resp)

    def update(self, data: ioa_network_element.InciNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InciNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InciNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = InciNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.InciNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InciNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InciNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = InciNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class InciNeighborListNode(ListNode[InciNeighborItemNode]):
    """Navigator for list inci-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.InciNeighborItem]:
        from ..data_models.ioa_network_element import InciNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InciNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.InciNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.InciNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class InciNode(Node):
    """Navigator for inci"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Inci:
        from ..data_models.ioa_network_element import Inci

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Inci.model_validate(resp)

    def update(self, data: ioa_network_element.Inci | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Inci

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Inci.model_validate(data)
        elif isinstance(data, str):
            data = Inci.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Inci | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Inci

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Inci.model_validate(data)
        elif isinstance(data, str):
            data = Inci.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def inci_neighbor(self) -> InciNeighborListNode:
        return InciNeighborListNode(self._client, f"{self._path}/inci-neighbor", "inci-neighbor", InciNeighborItemNode)


class CableIdStatusNode(Node):
    """Navigator for cable-id-status"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CableIdStatus:
        from ..data_models.ioa_network_element import CableIdStatus

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CableIdStatus.model_validate(resp)

    def update(self, data: ioa_network_element.CableIdStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CableIdStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CableIdStatus.model_validate(data)
        elif isinstance(data, str):
            data = CableIdStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.CableIdStatus | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CableIdStatus

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CableIdStatus.model_validate(data)
        elif isinstance(data, str):
            data = CableIdStatus.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class SupportingFiberConnectionNode(Node):
    """Navigator for supporting-fiber-connection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportingFiberConnection:
        from ..data_models.ioa_network_element import SupportingFiberConnection

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportingFiberConnection.model_validate(resp)

    def update(
        self, data: ioa_network_element.SupportingFiberConnection | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportingFiberConnection

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportingFiberConnection.model_validate(data)
        elif isinstance(data, str):
            data = SupportingFiberConnection.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SupportingFiberConnection | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportingFiberConnection

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportingFiberConnection.model_validate(data)
        elif isinstance(data, str):
            data = SupportingFiberConnection.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class CableIdPathItemNode(ItemNode):
    """Navigator for list item cable-id-path"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CableIdPathItem:
        from ..data_models.ioa_network_element import CableIdPathItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CableIdPathItem.model_validate(resp)

    def update(self, data: ioa_network_element.CableIdPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CableIdPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CableIdPathItem.model_validate(data)
        elif isinstance(data, str):
            data = CableIdPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.CableIdPathItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CableIdPathItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CableIdPathItem.model_validate(data)
        elif isinstance(data, str):
            data = CableIdPathItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def supporting_fiber_connection(self) -> SupportingFiberConnectionNode:
        return SupportingFiberConnectionNode(
            self._client, f"{self._path}/supporting-fiber-connection", "supporting-fiber-connection"
        )


class CableIdPathListNode(ListNode[CableIdPathItemNode]):
    """Navigator for list cable-id-path"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.CableIdPathItem]:
        from ..data_models.ioa_network_element import CableIdPathItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CableIdPathItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.CableIdPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.CableIdPathItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CableIdNode(Node):
    """Navigator for cable-id"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.CableId:
        from ..data_models.ioa_network_element import CableId

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CableId.model_validate(resp)

    def update(self, data: ioa_network_element.CableId | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CableId

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CableId.model_validate(data)
        elif isinstance(data, str):
            data = CableId.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.CableId | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import CableId

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CableId.model_validate(data)
        elif isinstance(data, str):
            data = CableId.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def cable_id_status(self) -> CableIdStatusNode:
        return CableIdStatusNode(self._client, f"{self._path}/cable-id-status", "cable-id-status")

    @property
    def cable_id_path(self) -> CableIdPathListNode:
        return CableIdPathListNode(self._client, f"{self._path}/cable-id-path", "cable-id-path", CableIdPathItemNode)


class FiberConnectionItemNode(ItemNode):
    """Navigator for list item fiber-connection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.FiberConnectionItem:
        from ..data_models.ioa_network_element import FiberConnectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return FiberConnectionItem.model_validate(resp)

    def update(self, data: ioa_network_element.FiberConnectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FiberConnectionItem

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

    def replace(self, data: ioa_network_element.FiberConnectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import FiberConnectionItem

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

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.FiberConnectionItem]:
        from ..data_models.ioa_network_element import FiberConnectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [FiberConnectionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.FiberConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.FiberConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ExternalFiberConnectionItemNode(ItemNode):
    """Navigator for list item external-fiber-connection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ExternalFiberConnectionItem:
        from ..data_models.ioa_network_element import ExternalFiberConnectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ExternalFiberConnectionItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.ExternalFiberConnectionItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ExternalFiberConnectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ExternalFiberConnectionItem.model_validate(data)
        elif isinstance(data, str):
            data = ExternalFiberConnectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.ExternalFiberConnectionItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ExternalFiberConnectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ExternalFiberConnectionItem.model_validate(data)
        elif isinstance(data, str):
            data = ExternalFiberConnectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ExternalFiberConnectionListNode(ListNode[ExternalFiberConnectionItemNode]):
    """Navigator for list external-fiber-connection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ExternalFiberConnectionItem]:
        from ..data_models.ioa_network_element import ExternalFiberConnectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ExternalFiberConnectionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ExternalFiberConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ExternalFiberConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SubmarineLinkItemNode(ItemNode):
    """Navigator for list item submarine-link"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SubmarineLinkItem:
        from ..data_models.ioa_network_element import SubmarineLinkItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SubmarineLinkItem.model_validate(resp)

    def update(self, data: ioa_network_element.SubmarineLinkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SubmarineLinkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubmarineLinkItem.model_validate(data)
        elif isinstance(data, str):
            data = SubmarineLinkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SubmarineLinkItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SubmarineLinkItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubmarineLinkItem.model_validate(data)
        elif isinstance(data, str):
            data = SubmarineLinkItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SubmarineLinkListNode(ListNode[SubmarineLinkItemNode]):
    """Navigator for list submarine-link"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SubmarineLinkItem]:
        from ..data_models.ioa_network_element import SubmarineLinkItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SubmarineLinkItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SubmarineLinkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SubmarineLinkItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class NctConnectionItemNode(ItemNode):
    """Navigator for list item nct-connection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.NctConnectionItem:
        from ..data_models.ioa_network_element import NctConnectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NctConnectionItem.model_validate(resp)

    def update(self, data: ioa_network_element.NctConnectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NctConnectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NctConnectionItem.model_validate(data)
        elif isinstance(data, str):
            data = NctConnectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.NctConnectionItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import NctConnectionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NctConnectionItem.model_validate(data)
        elif isinstance(data, str):
            data = NctConnectionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NctConnectionListNode(ListNode[NctConnectionItemNode]):
    """Navigator for list nct-connection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.NctConnectionItem]:
        from ..data_models.ioa_network_element import NctConnectionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NctConnectionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.NctConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.NctConnectionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class LinksNode(Node):
    """Navigator for links"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Links:
        from ..data_models.ioa_network_element import Links

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Links.model_validate(resp)

    def update(self, data: ioa_network_element.Links | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Links

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Links.model_validate(data)
        elif isinstance(data, str):
            data = Links.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Links | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Links

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Links.model_validate(data)
        elif isinstance(data, str):
            data = Links.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def fiber_connection(self) -> FiberConnectionListNode:
        return FiberConnectionListNode(
            self._client, f"{self._path}/fiber-connection", "fiber-connection", FiberConnectionItemNode
        )

    @property
    def external_fiber_connection(self) -> ExternalFiberConnectionListNode:
        return ExternalFiberConnectionListNode(
            self._client,
            f"{self._path}/external-fiber-connection",
            "external-fiber-connection",
            ExternalFiberConnectionItemNode,
        )

    @property
    def submarine_link(self) -> SubmarineLinkListNode:
        return SubmarineLinkListNode(
            self._client, f"{self._path}/submarine-link", "submarine-link", SubmarineLinkItemNode
        )

    @property
    def nct_connection(self) -> NctConnectionListNode:
        return NctConnectionListNode(
            self._client, f"{self._path}/nct-connection", "nct-connection", NctConnectionItemNode
        )


class AutodNeighborItemNode(ItemNode):
    """Navigator for list item autoD-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AutodNeighborItem:
        from ..data_models.ioa_network_element import AutodNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AutodNeighborItem.model_validate(resp)

    def update(self, data: ioa_network_element.AutodNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AutodNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AutodNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = AutodNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.AutodNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AutodNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AutodNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = AutodNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AutodNeighborListNode(ListNode[AutodNeighborItemNode]):
    """Navigator for list autoD-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.AutodNeighborItem]:
        from ..data_models.ioa_network_element import AutodNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AutodNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.AutodNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.AutodNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AutoDiscoveryNode(Node):
    """Navigator for auto-discovery"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.AutoDiscovery:
        from ..data_models.ioa_network_element import AutoDiscovery

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AutoDiscovery.model_validate(resp)

    def update(self, data: ioa_network_element.AutoDiscovery | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AutoDiscovery

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AutoDiscovery.model_validate(data)
        elif isinstance(data, str):
            data = AutoDiscovery.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.AutoDiscovery | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import AutoDiscovery

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AutoDiscovery.model_validate(data)
        elif isinstance(data, str):
            data = AutoDiscovery.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def autoD_neighbor(self) -> AutodNeighborListNode:
        return AutodNeighborListNode(
            self._client, f"{self._path}/autoD-neighbor", "autoD-neighbor", AutodNeighborItemNode
        )


class InterfaceNeighborItemNode(ItemNode):
    """Navigator for list item interface-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.InterfaceNeighborItem:
        from ..data_models.ioa_network_element import InterfaceNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return InterfaceNeighborItem.model_validate(resp)

    def update(self, data: ioa_network_element.InterfaceNeighborItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import InterfaceNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InterfaceNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = InterfaceNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.InterfaceNeighborItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import InterfaceNeighborItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = InterfaceNeighborItem.model_validate(data)
        elif isinstance(data, str):
            data = InterfaceNeighborItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class InterfaceNeighborListNode(ListNode[InterfaceNeighborItemNode]):
    """Navigator for list interface-neighbor"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.InterfaceNeighborItem]:
        from ..data_models.ioa_network_element import InterfaceNeighborItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [InterfaceNeighborItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.InterfaceNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.InterfaceNeighborItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SndpNode(Node):
    """Navigator for sndp"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Sndp:
        from ..data_models.ioa_network_element import Sndp

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Sndp.model_validate(resp)

    def update(self, data: ioa_network_element.Sndp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Sndp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Sndp.model_validate(data)
        elif isinstance(data, str):
            data = Sndp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Sndp | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Sndp

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Sndp.model_validate(data)
        elif isinstance(data, str):
            data = Sndp.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def interface_neighbor(self) -> InterfaceNeighborListNode:
        return InterfaceNeighborListNode(
            self._client, f"{self._path}/interface-neighbor", "interface-neighbor", InterfaceNeighborItemNode
        )


class TopologyNode(Node):
    """Navigator for topology"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Topology:
        from ..data_models.ioa_network_element import Topology

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Topology.model_validate(resp)

    def update(self, data: ioa_network_element.Topology | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Topology

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Topology.model_validate(data)
        elif isinstance(data, str):
            data = Topology.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Topology | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Topology

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Topology.model_validate(data)
        elif isinstance(data, str):
            data = Topology.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def lldp(self) -> LldpNode:
        return LldpNode(self._client, f"{self._path}/lldp", "lldp")

    @property
    def icdp(self) -> IcdpNode:
        return IcdpNode(self._client, f"{self._path}/icdp", "icdp")

    @property
    def inci(self) -> InciNode:
        return InciNode(self._client, f"{self._path}/inci", "inci")

    @property
    def cable_id(self) -> CableIdNode:
        return CableIdNode(self._client, f"{self._path}/cable-id", "cable-id")

    @property
    def links(self) -> LinksNode:
        return LinksNode(self._client, f"{self._path}/links", "links")

    @property
    def auto_discovery(self) -> AutoDiscoveryNode:
        return AutoDiscoveryNode(self._client, f"{self._path}/auto-discovery", "auto-discovery")

    @property
    def sndp(self) -> SndpNode:
        return SndpNode(self._client, f"{self._path}/sndp", "sndp")


class ApplicationDescriptionItemNode(ItemNode):
    """Navigator for list item application-description"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ApplicationDescriptionItem:
        from ..data_models.ioa_network_element import ApplicationDescriptionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ApplicationDescriptionItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.ApplicationDescriptionItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ApplicationDescriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ApplicationDescriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = ApplicationDescriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.ApplicationDescriptionItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import ApplicationDescriptionItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ApplicationDescriptionItem.model_validate(data)
        elif isinstance(data, str):
            data = ApplicationDescriptionItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ApplicationDescriptionListNode(ListNode[ApplicationDescriptionItemNode]):
    """Navigator for list application-description"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ApplicationDescriptionItem]:
        from ..data_models.ioa_network_element import ApplicationDescriptionItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ApplicationDescriptionItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ApplicationDescriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ApplicationDescriptionItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GadtNode(Node):
    """Navigator for gadt"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Gadt:
        from ..data_models.ioa_network_element import Gadt

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Gadt.model_validate(resp)

    def update(self, data: ioa_network_element.Gadt | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gadt

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gadt.model_validate(data)
        elif isinstance(data, str):
            data = Gadt.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Gadt | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gadt

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gadt.model_validate(data)
        elif isinstance(data, str):
            data = Gadt.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def application_description(self) -> ApplicationDescriptionListNode:
        return ApplicationDescriptionListNode(
            self._client,
            f"{self._path}/application-description",
            "application-description",
            ApplicationDescriptionItemNode,
        )


class SupportedSlotItemNode(ItemNode):
    """Navigator for list item supported-slot"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedSlotItem:
        from ..data_models.ioa_network_element import SupportedSlotItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedSlotItem.model_validate(resp)

    def update(self, data: ioa_network_element.SupportedSlotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedSlotItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedSlotItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedSlotItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SupportedSlotItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedSlotItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedSlotItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedSlotItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SupportedSlotListNode(ListNode[SupportedSlotItemNode]):
    """Navigator for list supported-slot"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedSlotItem]:
        from ..data_models.ioa_network_element import SupportedSlotItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedSlotItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedSlotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedSlotItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SupportedChassisItemNode(ItemNode):
    """Navigator for list item supported-chassis"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedChassisItem:
        from ..data_models.ioa_network_element import SupportedChassisItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedChassisItem.model_validate(resp)

    def update(self, data: ioa_network_element.SupportedChassisItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedChassisItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedChassisItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedChassisItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SupportedChassisItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedChassisItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedChassisItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedChassisItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def supported_slot(self) -> SupportedSlotListNode:
        return SupportedSlotListNode(
            self._client, f"{self._path}/supported-slot", "supported-slot", SupportedSlotItemNode
        )


class SupportedChassisListNode(ListNode[SupportedChassisItemNode]):
    """Navigator for list supported-chassis"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedChassisItem]:
        from ..data_models.ioa_network_element import SupportedChassisItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedChassisItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedChassisItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedChassisItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SupportedPowerProfileItemNode(ItemNode):
    """Navigator for list item supported-power-profile"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedPowerProfileItem:
        from ..data_models.ioa_network_element import SupportedPowerProfileItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedPowerProfileItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.SupportedPowerProfileItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportedPowerProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedPowerProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedPowerProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SupportedPowerProfileItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SupportedPowerProfileItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedPowerProfileItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedPowerProfileItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SupportedPowerProfileListNode(ListNode[SupportedPowerProfileItemNode]):
    """Navigator for list supported-power-profile"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedPowerProfileItem]:
        from ..data_models.ioa_network_element import SupportedPowerProfileItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedPowerProfileItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedPowerProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedPowerProfileItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SupportedTomItemNode(ItemNode):
    """Navigator for list item supported-tom"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedTomItem:
        from ..data_models.ioa_network_element import SupportedTomItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedTomItem.model_validate(resp)

    def update(self, data: ioa_network_element.SupportedTomItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedTomItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedTomItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedTomItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SupportedTomItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedTomItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedTomItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedTomItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SupportedTomListNode(ListNode[SupportedTomItemNode]):
    """Navigator for list supported-tom"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedTomItem]:
        from ..data_models.ioa_network_element import SupportedTomItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedTomItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedTomItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedTomItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SupportedPortItemNode(ItemNode):
    """Navigator for list item supported-port"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedPortItem:
        from ..data_models.ioa_network_element import SupportedPortItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedPortItem.model_validate(resp)

    def update(self, data: ioa_network_element.SupportedPortItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedPortItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedPortItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedPortItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SupportedPortItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedPortItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedPortItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedPortItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def supported_tom(self) -> SupportedTomListNode:
        return SupportedTomListNode(self._client, f"{self._path}/supported-tom", "supported-tom", SupportedTomItemNode)


class SupportedPortListNode(ListNode[SupportedPortItemNode]):
    """Navigator for list supported-port"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedPortItem]:
        from ..data_models.ioa_network_element import SupportedPortItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedPortItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedPortItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedPortItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class SubtypeConstraintItemNode(ItemNode):
    """Navigator for list item subtype-constraint"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SubtypeConstraintItem:
        from ..data_models.ioa_network_element import SubtypeConstraintItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SubtypeConstraintItem.model_validate(resp)

    def update(self, data: ioa_network_element.SubtypeConstraintItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SubtypeConstraintItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubtypeConstraintItem.model_validate(data)
        elif isinstance(data, str):
            data = SubtypeConstraintItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.SubtypeConstraintItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import SubtypeConstraintItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SubtypeConstraintItem.model_validate(data)
        elif isinstance(data, str):
            data = SubtypeConstraintItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class SubtypeConstraintListNode(ListNode[SubtypeConstraintItemNode]):
    """Navigator for list subtype-constraint"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SubtypeConstraintItem]:
        from ..data_models.ioa_network_element import SubtypeConstraintItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SubtypeConstraintItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SubtypeConstraintItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SubtypeConstraintItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GsctNode(Node):
    """Navigator for gsct"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Gsct:
        from ..data_models.ioa_network_element import Gsct

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Gsct.model_validate(resp)

    def update(self, data: ioa_network_element.Gsct | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gsct

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gsct.model_validate(data)
        elif isinstance(data, str):
            data = Gsct.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Gsct | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gsct

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gsct.model_validate(data)
        elif isinstance(data, str):
            data = Gsct.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def subtype_constraint(self) -> SubtypeConstraintListNode:
        return SubtypeConstraintListNode(
            self._client, f"{self._path}/subtype-constraint", "subtype-constraint", SubtypeConstraintItemNode
        )


class GoldenCarrierModeItemNode(ItemNode):
    """Navigator for list item golden-carrier-mode"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.GoldenCarrierModeItem:
        from ..data_models.ioa_network_element import GoldenCarrierModeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return GoldenCarrierModeItem.model_validate(resp)

    def update(self, data: ioa_network_element.GoldenCarrierModeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import GoldenCarrierModeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GoldenCarrierModeItem.model_validate(data)
        elif isinstance(data, str):
            data = GoldenCarrierModeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.GoldenCarrierModeItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import GoldenCarrierModeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GoldenCarrierModeItem.model_validate(data)
        elif isinstance(data, str):
            data = GoldenCarrierModeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class GoldenCarrierModeListNode(ListNode[GoldenCarrierModeItemNode]):
    """Navigator for list golden-carrier-mode"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.GoldenCarrierModeItem]:
        from ..data_models.ioa_network_element import GoldenCarrierModeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [GoldenCarrierModeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.GoldenCarrierModeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.GoldenCarrierModeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GcmtNode(Node):
    """Navigator for gcmt"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Gcmt:
        from ..data_models.ioa_network_element import Gcmt

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Gcmt.model_validate(resp)

    def update(self, data: ioa_network_element.Gcmt | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gcmt

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gcmt.model_validate(data)
        elif isinstance(data, str):
            data = Gcmt.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Gcmt | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gcmt

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gcmt.model_validate(data)
        elif isinstance(data, str):
            data = Gcmt.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def golden_carrier_mode(self) -> GoldenCarrierModeListNode:
        return GoldenCarrierModeListNode(
            self._client, f"{self._path}/golden-carrier-mode", "golden-carrier-mode", GoldenCarrierModeItemNode
        )


class GoldenAdvancedParameterItemNode(ItemNode):
    """Navigator for list item golden-advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.GoldenAdvancedParameterItem:
        from ..data_models.ioa_network_element import GoldenAdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return GoldenAdvancedParameterItem.model_validate(resp)

    def update(
        self, data: ioa_network_element.GoldenAdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import GoldenAdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GoldenAdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = GoldenAdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.GoldenAdvancedParameterItem | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import GoldenAdvancedParameterItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = GoldenAdvancedParameterItem.model_validate(data)
        elif isinstance(data, str):
            data = GoldenAdvancedParameterItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class GoldenAdvancedParameterListNode(ListNode[GoldenAdvancedParameterItemNode]):
    """Navigator for list golden-advanced-parameter"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.GoldenAdvancedParameterItem]:
        from ..data_models.ioa_network_element import GoldenAdvancedParameterItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [GoldenAdvancedParameterItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.GoldenAdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.GoldenAdvancedParameterItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GaptNode(Node):
    """Navigator for gapt"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Gapt:
        from ..data_models.ioa_network_element import Gapt

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Gapt.model_validate(resp)

    def update(self, data: ioa_network_element.Gapt | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gapt

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gapt.model_validate(data)
        elif isinstance(data, str):
            data = Gapt.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Gapt | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Gapt

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Gapt.model_validate(data)
        elif isinstance(data, str):
            data = Gapt.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def golden_advanced_parameter(self) -> GoldenAdvancedParameterListNode:
        return GoldenAdvancedParameterListNode(
            self._client,
            f"{self._path}/golden-advanced-parameter",
            "golden-advanced-parameter",
            GoldenAdvancedParameterItemNode,
        )


class SupportedCardItemNode(ItemNode):
    """Navigator for list item supported-card"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SupportedCardItem:
        from ..data_models.ioa_network_element import SupportedCardItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SupportedCardItem.model_validate(resp)

    def update(self, data: ioa_network_element.SupportedCardItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedCardItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedCardItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedCardItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.SupportedCardItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SupportedCardItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SupportedCardItem.model_validate(data)
        elif isinstance(data, str):
            data = SupportedCardItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def supported_power_profile(self) -> SupportedPowerProfileListNode:
        return SupportedPowerProfileListNode(
            self._client,
            f"{self._path}/supported-power-profile",
            "supported-power-profile",
            SupportedPowerProfileItemNode,
        )

    @property
    def supported_port(self) -> SupportedPortListNode:
        return SupportedPortListNode(
            self._client, f"{self._path}/supported-port", "supported-port", SupportedPortItemNode
        )

    @property
    def gsct(self) -> GsctNode:
        return GsctNode(self._client, f"{self._path}/gsct", "gsct")

    @property
    def supported_slot(self) -> SupportedSlotListNode:
        return SupportedSlotListNode(
            self._client, f"{self._path}/supported-slot", "supported-slot", SupportedSlotItemNode
        )

    @property
    def gcmt(self) -> GcmtNode:
        return GcmtNode(self._client, f"{self._path}/gcmt", "gcmt")

    @property
    def gapt(self) -> GaptNode:
        return GaptNode(self._client, f"{self._path}/gapt", "gapt")


class SupportedCardListNode(ListNode[SupportedCardItemNode]):
    """Navigator for list supported-card"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.SupportedCardItem]:
        from ..data_models.ioa_network_element import SupportedCardItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [SupportedCardItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.SupportedCardItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.SupportedCardItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class TomTypeItemNode(ItemNode):
    """Navigator for list item tom-type"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.TomTypeItem:
        from ..data_models.ioa_network_element import TomTypeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return TomTypeItem.model_validate(resp)

    def update(self, data: ioa_network_element.TomTypeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TomTypeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TomTypeItem.model_validate(data)
        elif isinstance(data, str):
            data = TomTypeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.TomTypeItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import TomTypeItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = TomTypeItem.model_validate(data)
        elif isinstance(data, str):
            data = TomTypeItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class TomTypeListNode(ListNode[TomTypeItemNode]):
    """Navigator for list tom-type"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.TomTypeItem]:
        from ..data_models.ioa_network_element import TomTypeItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [TomTypeItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.TomTypeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.TomTypeItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class EquipmentCapabilitiesNode(Node):
    """Navigator for equipment-capabilities"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.EquipmentCapabilities:
        from ..data_models.ioa_network_element import EquipmentCapabilities

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return EquipmentCapabilities.model_validate(resp)

    def update(self, data: ioa_network_element.EquipmentCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import EquipmentCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EquipmentCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = EquipmentCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(
        self, data: ioa_network_element.EquipmentCapabilities | dict | str | None = None, **kwargs: Any
    ) -> None:
        from ..data_models.ioa_network_element import EquipmentCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = EquipmentCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = EquipmentCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def gadt(self) -> GadtNode:
        return GadtNode(self._client, f"{self._path}/gadt", "gadt")

    @property
    def supported_chassis(self) -> SupportedChassisListNode:
        return SupportedChassisListNode(
            self._client, f"{self._path}/supported-chassis", "supported-chassis", SupportedChassisItemNode
        )

    @property
    def supported_card(self) -> SupportedCardListNode:
        return SupportedCardListNode(
            self._client, f"{self._path}/supported-card", "supported-card", SupportedCardItemNode
        )

    @property
    def tom_type(self) -> TomTypeListNode:
        return TomTypeListNode(self._client, f"{self._path}/tom-type", "tom-type", TomTypeItemNode)


class OadmCapabilitiesNode(Node):
    """Navigator for oadm-capabilities"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OadmCapabilities:
        from ..data_models.ioa_network_element import OadmCapabilities

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OadmCapabilities.model_validate(resp)

    def update(self, data: ioa_network_element.OadmCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OadmCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OadmCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = OadmCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.OadmCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OadmCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OadmCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = OadmCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)


class L0CapabilitiesNode(Node):
    """Navigator for l0-capabilities"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.L0Capabilities:
        from ..data_models.ioa_network_element import L0Capabilities

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return L0Capabilities.model_validate(resp)

    def update(self, data: ioa_network_element.L0Capabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import L0Capabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = L0Capabilities.model_validate(data)
        elif isinstance(data, str):
            data = L0Capabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.L0Capabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import L0Capabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = L0Capabilities.model_validate(data)
        elif isinstance(data, str):
            data = L0Capabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def oadm_capabilities(self) -> OadmCapabilitiesNode:
        return OadmCapabilitiesNode(self._client, f"{self._path}/oadm-capabilities", "oadm-capabilities")


class SystemCapabilitiesNode(Node):
    """Navigator for system-capabilities"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.SystemCapabilities:
        from ..data_models.ioa_network_element import SystemCapabilities

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return SystemCapabilities.model_validate(resp)

    def update(self, data: ioa_network_element.SystemCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SystemCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SystemCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = SystemCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.SystemCapabilities | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import SystemCapabilities

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = SystemCapabilities.model_validate(data)
        elif isinstance(data, str):
            data = SystemCapabilities.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def equipment_capabilities(self) -> EquipmentCapabilitiesNode:
        return EquipmentCapabilitiesNode(self._client, f"{self._path}/equipment-capabilities", "equipment-capabilities")

    @property
    def l0_capabilities(self) -> L0CapabilitiesNode:
        return L0CapabilitiesNode(self._client, f"{self._path}/l0-capabilities", "l0-capabilities")


class ProtectionUnitItemNode(ItemNode):
    """Navigator for list item protection-unit"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ProtectionUnitItem:
        from ..data_models.ioa_network_element import ProtectionUnitItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ProtectionUnitItem.model_validate(resp)

    def update(self, data: ioa_network_element.ProtectionUnitItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ProtectionUnitItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ProtectionUnitItem.model_validate(data)
        elif isinstance(data, str):
            data = ProtectionUnitItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ProtectionUnitItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ProtectionUnitItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ProtectionUnitItem.model_validate(data)
        elif isinstance(data, str):
            data = ProtectionUnitItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ProtectionUnitListNode(ListNode[ProtectionUnitItemNode]):
    """Navigator for list protection-unit"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ProtectionUnitItem]:
        from ..data_models.ioa_network_element import ProtectionUnitItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ProtectionUnitItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ProtectionUnitItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ProtectionUnitItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ProtectionGroupItemNode(ItemNode):
    """Navigator for list item protection-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ProtectionGroupItem:
        from ..data_models.ioa_network_element import ProtectionGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ProtectionGroupItem.model_validate(resp)

    def update(self, data: ioa_network_element.ProtectionGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ProtectionGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ProtectionGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = ProtectionGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.ProtectionGroupItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ProtectionGroupItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ProtectionGroupItem.model_validate(data)
        elif isinstance(data, str):
            data = ProtectionGroupItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def protection_unit(self) -> ProtectionUnitListNode:
        return ProtectionUnitListNode(
            self._client, f"{self._path}/protection-unit", "protection-unit", ProtectionUnitItemNode
        )


class ProtectionGroupListNode(ListNode[ProtectionGroupItemNode]):
    """Navigator for list protection-group"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.ProtectionGroupItem]:
        from ..data_models.ioa_network_element import ProtectionGroupItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ProtectionGroupItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.ProtectionGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.ProtectionGroupItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class OpticalSwitchItemNode(ItemNode):
    """Navigator for list item optical-switch"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.OpticalSwitchItem:
        from ..data_models.ioa_network_element import OpticalSwitchItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return OpticalSwitchItem.model_validate(resp)

    def update(self, data: ioa_network_element.OpticalSwitchItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalSwitchItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalSwitchItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalSwitchItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_network_element.OpticalSwitchItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import OpticalSwitchItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = OpticalSwitchItem.model_validate(data)
        elif isinstance(data, str):
            data = OpticalSwitchItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class OpticalSwitchListNode(ListNode[OpticalSwitchItemNode]):
    """Navigator for list optical-switch"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_network_element.OpticalSwitchItem]:
        from ..data_models.ioa_network_element import OpticalSwitchItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [OpticalSwitchItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_network_element.OpticalSwitchItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_network_element.OpticalSwitchItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ProtectionNode(Node):
    """Navigator for protection"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Protection:
        from ..data_models.ioa_network_element import Protection

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Protection.model_validate(resp)

    def update(self, data: ioa_network_element.Protection | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Protection

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Protection.model_validate(data)
        elif isinstance(data, str):
            data = Protection.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)

    def replace(self, data: ioa_network_element.Protection | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Protection

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = Protection.model_validate(data)
        elif isinstance(data, str):
            data = Protection.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def protection_group(self) -> ProtectionGroupListNode:
        return ProtectionGroupListNode(
            self._client, f"{self._path}/protection-group", "protection-group", ProtectionGroupItemNode
        )

    @property
    def optical_switch(self) -> OpticalSwitchListNode:
        return OpticalSwitchListNode(
            self._client, f"{self._path}/optical-switch", "optical-switch", OpticalSwitchItemNode
        )


class NeNode(Node):
    """Navigator for ne"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.Ne:
        from ..data_models.ioa_network_element import Ne

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return Ne.model_validate(resp)

    def update(self, data: ioa_network_element.Ne | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ne

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

    def replace(self, data: ioa_network_element.Ne | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import Ne

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
    def equipment(self) -> EquipmentNode:
        return EquipmentNode(self._client, f"{self._path}/equipment", "equipment")

    @property
    def facilities(self) -> FacilitiesNode:
        return FacilitiesNode(self._client, f"{self._path}/facilities", "facilities")

    @property
    def services(self) -> ServicesServicesNode:
        return ServicesServicesNode(self._client, f"{self._path}/services", "services")

    @property
    def system(self) -> SystemSystemNode:
        return SystemSystemNode(self._client, f"{self._path}/system", "system")

    @property
    def ne_function(self) -> NeFunctionNode:
        return NeFunctionNode(self._client, f"{self._path}/ne-function", "ne-function")

    @property
    def topology(self) -> TopologyNode:
        return TopologyNode(self._client, f"{self._path}/topology", "topology")

    @property
    def system_capabilities(self) -> SystemCapabilitiesNode:
        return SystemCapabilitiesNode(self._client, f"{self._path}/system-capabilities", "system-capabilities")

    @property
    def protection(self) -> ProtectionNode:
        return ProtectionNode(self._client, f"{self._path}/protection", "protection")


class ChangedByNode(Node):
    """Navigator for changed-by"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_network_element.ChangedBy:
        from ..data_models.ioa_network_element import ChangedBy

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ChangedBy.model_validate(resp)

    def update(self, data: ioa_network_element.ChangedBy | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ChangedBy

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

    def replace(self, data: ioa_network_element.ChangedBy | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_network_element import ChangedBy

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
