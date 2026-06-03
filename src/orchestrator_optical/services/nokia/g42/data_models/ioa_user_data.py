"""Auto-generated Pydantic models from YANG schemas"""

import re
from decimal import Decimal
from typing import Annotated, Any, TypeVar

from pydantic import AfterValidator, BeforeValidator, Field, PlainSerializer

from ._base import YangBaseModel


# RFC 7951: 64-bit numbers MUST be represented as JSON strings.
# here we use PlainSerializer to ensure string output during JSON serialization (mode='json').
def format_at_least_two_places(v: Decimal) -> str:
    # Normalize to remove unnecessary trailing zeros (e.g., 1.500 -> 1.5)
    v = v.normalize()
     
    # Exponent 0 = integer (1), -1 = one decimal (1.1), -2 = two decimals (1.11)
    # If it's greater than -2, it means we have 0 or 1 decimal places.
    if v.as_tuple().exponent > -2:
        return format(v.quantize(Decimal("0.01")), "f")
    
    # Otherwise, return the normalized string (keeps 3+ decimal places)
    return format(v, "f")

Decimal64 = Annotated[
    Decimal, 
    PlainSerializer(format_at_least_two_places, return_type=str)
]
Uint64 = Annotated[int, PlainSerializer(lambda v: str(v), return_type=str)]
Int64 = Annotated[int, PlainSerializer(lambda v: str(v), return_type=str)]

def check_pattern(pattern: str, v: str) -> str:
    if isinstance(v, str) and not re.match(pattern, v):
        raise ValueError(f'Value does not match pattern: {pattern}')
    return v

T = TypeVar("T")

def restconf_list_validator(v: Any) -> Any:
    """
    RESTCONF quirk: Truncated lists (via depth) often return {} instead of [].
    Also handles 'None' or missing data if needed.
    """
    if isinstance(v, dict) and not v:
        return []
    # In some truly cursed implementations, a single item list is returned as an object
    # but we will stick to the 'empty dict to list' fix for now.
    return v

# Define a reusable type for RESTCONF lists
RestconfList = Annotated[list[T], BeforeValidator(restconf_list_validator)]

class NamedValueSetItem(YangBaseModel):
    """Set of named values associated with the DB entry. Useful for storing multi-attribute information (record)."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern('^(?:([A-Za-z0-9_\\-.,]*))$', v))] = Field(json_schema_extra={'is_config': True}, description='Name of the value item.', min_length=1, max_length=64)
    value: str | None = Field(json_schema_extra={'is_config': True}, description='Value item.', min_length=0, max_length=1024, default=None)

class DbEntryItem(YangBaseModel):
    """DB for storing multiple user created entries keyed by name."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern('^(?:([A-Za-z0-9_\\-.,]*))$', v))] = Field(json_schema_extra={'is_config': True}, description='Name of the DB entry.', min_length=1, max_length=64)
    value: str | None = Field(json_schema_extra={'is_config': True}, description='Value associated with the entry.', min_length=0, max_length=1024, default=None)
    named_value_set: RestconfList[NamedValueSetItem] | None = Field(json_schema_extra={'is_config': True}, description='Set of named values associated with the DB entry. Useful for storing multi-attribute information (record).', default=None, alias="named-value-set")

class UserData(YangBaseModel):
    """Container to store user created data on the network element."""

    db_entry: RestconfList[DbEntryItem] | None = Field(json_schema_extra={'is_config': True}, description='DB for storing multiple user created entries keyed by name.', default=None, alias="db-entry")

class IoaUserDataData(YangBaseModel):
    """Root data model for ioa-user-data"""

    user_data: UserData | None = Field(json_schema_extra={'is_config': True}, description='Container to store user created data on the network element.', default=None, alias="ioa-user-data:user-data")
