"""Auto-generated Pydantic models from YANG schemas"""

import re
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer

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

class OperationTypeEnum(str, Enum):
    """Enumeration for OperationTypeEnum
    
    Values:
      * force: Forced switch to a target, e.g. working or protection.
      * lockout: Lockout of protection.
      * manual: Manual switch to a target, e.g. working or protection.
      * clear: clear current command.
    """

    FORCE = "force"
    LOCKOUT = "lockout"
    MANUAL = "manual"
    CLEAR = "clear"

class SwitchTargetEnum(str, Enum):
    """Enumeration for SwitchTargetEnum
    
    Values:
      * working: Switch to working leg
      * protection: Switch to protecting leg
    """

    WORKING = "working"
    PROTECTION = "protection"

class ProtectionSwitchInput(YangBaseModel):
    """Input: None"""

    protection_group: str = Field(json_schema_extra={'is_config': None}, description='The target of the switch command.', alias="protection-group")
    operation_type: OperationTypeEnum = Field(json_schema_extra={'is_config': None}, description='The type of protection switch command', alias="operation-type")
    switch_target: SwitchTargetEnum | None = Field(json_schema_extra={'is_config': None}, description="The target of the switch command, which is not needed for release and lockout operation.\n\nCondition (when): (../operation-type != 'lockout') and (../operation-type != 'clear')", default=None, alias="switch-target")

class ProtectionSwitch(BaseModel):
    """RPC: protection-switch"""
    input: ProtectionSwitchInput

    model_config = ConfigDict(extra='forbid', validate_assignment=True, defer_build=True)
