"""Auto-generated Pydantic models from YANG schemas"""

import re
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, TypeVar

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer

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
        raise ValueError(f"Value does not match pattern: {pattern}")
    return v

T = TypeVar("T")

def restconf_list_validator(v: Any) -> Any:
    """RESTCONF quirk: Truncated lists (via depth) often return {} instead of [].
    Also handles 'None' or missing data if needed.
    """
    if isinstance(v, dict) and not v:
        return []
    # In some truly cursed implementations, a single item list is returned as an object
    # but we will stick to the 'empty dict to list' fix for now.
    return v

# Define a reusable type for RESTCONF lists
RestconfList = Annotated[list[T], BeforeValidator(restconf_list_validator)]

class PayloadTypeEnum(str, Enum):
    """Enumeration for PayloadTypeEnum
    
    Values:
      * 100GBE: A generic payload type for all 100GBASE-X Ethernet clients when provisioning a digital XCON.
      * 400GBE: A generic payload type for all 400GBASE-X Ethernet clients when provisioning a digital XCON.
      * OTU4: A generic payload type for OTU4 Transport w/o FEC service.
      * 100G: A generic payload type for ODU4 switching services.
      * ODU2: A generic payload type for ODU2 switching services.
      * ODU2e: A generic payload type for ODU2e switching services.
      * 10GBE
      * OC192
      * STM64
      * 10G
      * 800GBE: A generic payload type for all 800GBASE-X Ethernet clients when provisioning a digital XCON.
      * empty: Not applicable for 2-step XCON approach.
    """

    _100GBE = "100GBE"
    _400GBE = "400GBE"
    OTU4 = "OTU4"
    _100G = "100G"
    ODU2 = "ODU2"
    ODU2E = "ODU2e"
    _10GBE = "10GBE"
    OC192 = "OC192"
    STM64 = "STM64"
    _10G = "10G"
    _800GBE = "800GBE"
    EMPTY = "empty"

class DirectionEnum(str, Enum):
    """Enumeration for DirectionEnum
    
    Values:
      * two-way
    """

    TWO_WAY = "two-way"

class CreateXconInput(YangBaseModel):
    """Input: None"""

    payload_type: PayloadTypeEnum | None = Field(json_schema_extra={"is_config": None}, description="Indicates a generic, high-level source (from) client payload type of the digital XCON.", default=None, alias="payload-type")
    direction: DirectionEnum | None = Field(json_schema_extra={"is_config": None}, description="Indicates whether the digital XCON is uni-directional (1-WAY) or bi-directional (2-WAY).", default=DirectionEnum.TWO_WAY)
    label: str | None = Field(json_schema_extra={"is_config": None}, description="User label.", min_length=0, max_length=256, default=None)
    circuit_id_suffix: str | None = Field(json_schema_extra={"is_config": None}, description="User configured circuit ID suffix.", min_length=0, max_length=48, default=None, alias="circuit-id-suffix")
    # Choice: source-facility
    # Case: src-existing-facility
    source: str | None = Field(json_schema_extra={"is_config": None}, description="Source end-point of the xcon. Must be an existing facility that can be used\nas a XCON end-point.", default=None)
    # Case: src-non-existing-facility
    src_parent_odu: str | None = Field(json_schema_extra={"is_config": None}, description="Name of the High Order parent ODU where to audst-create this ODU end-point.", default=None, alias="src-parent-odu")
    src_time_slots: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v))] | None = Field(json_schema_extra={"is_config": None}, description="List of time-slots to allocate to the automatically created LO-ODU.\nValue can be:\n- omitted/empty - in which case system will audst-allocate time-slots based on the src-instance-id,\n                  which becomes mandatory (this is only supported for non ODUflex scenarios.)\n- starting time-slot - system automatically allocates the rest of the time-slots sequentially\n                       from this starting point; will fail if those time-slots are not available\n- time-slot list - full list of time-slots, using a comma separated list, with 'x..y' representing\n                   ranges; the total number of time-slots need to match the associated payload-type\n                   (e.g. 80 time-slots for 100G payload, 320 time-slots for 400G payload, etc)", min_length=0, max_length=255, default=None, alias="src-time-slots")
    src_instance_id: int | None = Field(json_schema_extra={"is_config": None}, description="Optional parameter on LO-ODU creation, identifies the ODU within the parent/high-order ODU.\nIf not provided, it is automatically derived.\nMax value depends on capacity of the HO-ODU and of the odu-type.\n(ex: for creating an ODU4 in a HO ODUC8, instance can be between 1 and 8)\nNote: instance-id becomes mandatory if time-slots are not provided.", ge=1, default=None, alias="src-instance-id")
    # Choice: destination-facility
    # Case: dst-existing-facility
    destination: str | None = Field(json_schema_extra={"is_config": None}, description="Destination end-point of the xcon. Must be an existing facility that can be used\nas a XCON end-point.", default=None)
    # Case: dst-non-existing-facility
    dst_parent_odu: str | None = Field(json_schema_extra={"is_config": None}, description="Name of the High Order parent ODU where to audst-create this ODU end-point.", default=None, alias="dst-parent-odu")
    dst_time_slots: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v))] | None = Field(json_schema_extra={"is_config": None}, description="List of time-slots to allocate to the automatically created LO-ODU.\nValue can be:\n- omitted/empty - in which case system will audst-allocate time-slots based on the dst-instance-id,\n                  which becomes mandatory (this is only supported for non ODUflex scenarios.)\n- starting time-slot - system automatically allocates the rest of the time-slots sequentially\n                       from this starting point; will fail if those time-slots are not available\n- time-slot list - full list of time-slots, using a comma separated list, with 'x..y' representing\n                   ranges; the total number of time-slots need to match the associated payload-type\n                   (e.g. 80 time-slots for 100G payload, 320 time-slots for 400G payload, etc)", min_length=0, max_length=255, default=None, alias="dst-time-slots")
    dst_instance_id: int | None = Field(json_schema_extra={"is_config": None}, description="Optional parameter on LO-ODU creation, identifies the ODU within the parent/high-order ODU.\nIf not provided, it is automatically derived.\nMax value depends on capacity of the HO-ODU and of the odu-type.\n(ex: for creating an ODU4 in a HO ODUC8, instance can be between 1 and 8)\nNote: instance-id becomes mandatory if time-slots are not provided.", ge=1, default=None, alias="dst-instance-id")

class CreateXcon(BaseModel):
    """RPC: create-xcon"""
    input: CreateXconInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)
