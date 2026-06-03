from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import ioa_user_data

class NamedValueSetItemNode(ItemNode):
    """Navigator for list item named-value-set"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_user_data.NamedValueSetItem:
        from ..data_models.ioa_user_data import NamedValueSetItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return NamedValueSetItem.model_validate(resp)

    def update(self, data: ioa_user_data.NamedValueSetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_user_data import NamedValueSetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NamedValueSetItem.model_validate(data)
        elif isinstance(data, str):
            data = NamedValueSetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_user_data.NamedValueSetItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_user_data import NamedValueSetItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = NamedValueSetItem.model_validate(data)
        elif isinstance(data, str):
            data = NamedValueSetItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class NamedValueSetListNode(ListNode[NamedValueSetItemNode]):
    """Navigator for list named-value-set"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_user_data.NamedValueSetItem]:
        from ..data_models.ioa_user_data import NamedValueSetItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [NamedValueSetItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_user_data.NamedValueSetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_user_data.NamedValueSetItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class DbEntryItemNode(ItemNode):
    """Navigator for list item db-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_user_data.DbEntryItem:
        from ..data_models.ioa_user_data import DbEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DbEntryItem.model_validate(resp)

    def update(self, data: ioa_user_data.DbEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_user_data import DbEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DbEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = DbEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_user_data.DbEntryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_user_data import DbEntryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DbEntryItem.model_validate(data)
        elif isinstance(data, str):
            data = DbEntryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def named_value_set(self) -> NamedValueSetListNode:
        return NamedValueSetListNode(self._client, f"{self._path}/named-value-set", "named-value-set", NamedValueSetItemNode)

class DbEntryListNode(ListNode[DbEntryItemNode]):
    """Navigator for list db-entry"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> list[ioa_user_data.DbEntryItem]:
        from ..data_models.ioa_user_data import DbEntryItem
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DbEntryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_user_data.DbEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_user_data.DbEntryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)

class UserDataNode(Node):
    """Navigator for user-data"""

    def retrieve(self, *, content: str = "all", with_defaults: str = "report-all", depth: int | str = 2, fields: list[str] | None = None) -> ioa_user_data.UserData:
        from ..data_models.ioa_user_data import UserData
        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return UserData.model_validate(resp)

    def update(self, data: ioa_user_data.UserData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_user_data import UserData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UserData.model_validate(data)
        elif isinstance(data, str):
            data = UserData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._update(**payload)


    def replace(self, data: ioa_user_data.UserData | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_user_data import UserData

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = UserData.model_validate(data)
        elif isinstance(data, str):
            data = UserData.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)

        return self._replace(**payload)

    @property
    def db_entry(self) -> DbEntryListNode:
        return DbEntryListNode(self._client, f"{self._path}/db-entry", "db-entry", DbEntryItemNode)
