from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class YangBaseModel(BaseModel):
    """Base for all YANG-derived models.
    Add exclude fields based on json_schema_extra['is_config'] and content required.
    """
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        defer_build=True,
        validate_default=True
    )

    def model_dump(self, *, content: Literal["config", "all", "nonconfig"] = "all", **kwargs: Any) -> dict[str, Any]:
        # Force JSON mode to ensure 64-bit numbers become strings and Enums become values
        kwargs.setdefault("mode", "json")
        kwargs.setdefault("by_alias", True)

        if content == "all":
            return super().model_dump(**kwargs)

        cls = type(self)
        exclude: set[str] = set()
        for field_name, field_info in cls.model_fields.items():
            is_config = field_info.json_schema_extra.get("is_config", True)
            if content == "config" and not is_config:
                exclude.add(field_name)
            if content == "nonconfig" and is_config:
                exclude.add(field_name)


        # Merge with any exclude the caller already passed
        user_exclude = kwargs.get("exclude")
        if user_exclude:
            if isinstance(user_exclude, (set, list, tuple)):
                exclude |= set(user_exclude)
            else: # dict-style exclude not implemented yet
                raise NotImplementedError

        kwargs["exclude"] = exclude if exclude else None
        return super().model_dump(**kwargs)

