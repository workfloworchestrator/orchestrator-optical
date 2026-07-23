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

class DirectionEnum(str, Enum):
    """Enumeration for DirectionEnum
    
    Values:
      * all
      * na: Not-applicable
      * ingress
      * egress
    """

    ALL = "all"
    NA = "na"
    INGRESS = "ingress"
    EGRESS = "egress"

class LocationEnum(str, Enum):
    """Enumeration for LocationEnum
    
    Values:
      * all
      * na: Not-applicable
      * near-end
      * far-end
    """

    ALL = "all"
    NA = "na"
    NEAR_END = "near-end"
    FAR_END = "far-end"

class PmUnitTypeEnum(str, Enum):
    """Enumeration for PmUnitTypeEnum
    
    Values:
      * na: Not applicable
      * dBm
      * ms
      * ps
      * ps/nm
      * dB
      * seconds
      * packets
      * events
      * octets
      * bits
      * blocks
      * times
      * percent
      * bit-ratio
      * C
      * frames
      * W
      * V
      * A
      * rpm
      * ps2
      * mA
      * words
      * cw
      * nm
      * bytes
      * errors
      * MHz
      * KiB
      * degrees
      * rads/s
    """

    NA = "na"
    DBM = "dBm"
    MS = "ms"
    PS = "ps"
    PS_NM = "ps/nm"
    DB = "dB"
    SECONDS = "seconds"
    PACKETS = "packets"
    EVENTS = "events"
    OCTETS = "octets"
    BITS = "bits"
    BLOCKS = "blocks"
    TIMES = "times"
    PERCENT = "percent"
    BIT_RATIO = "bit-ratio"
    C = "C"
    FRAMES = "frames"
    W = "W"
    V = "V"
    A = "A"
    RPM = "rpm"
    PS2 = "ps2"
    MA = "mA"
    WORDS = "words"
    CW = "cw"
    NM = "nm"
    BYTES = "bytes"
    ERRORS = "errors"
    MHZ = "MHz"
    KIB = "KiB"
    DEGREES = "degrees"
    RADS_S = "rads/s"

class RealTimePmItem(YangBaseModel):
    """Individual real-time-pm record. Contains data updated continuously in real-time."""

    resource: str = Field(json_schema_extra={"is_config": False}, description="Existing system resource.")
    resource_type: str | None = Field(json_schema_extra={"is_config": False}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    parameter: str = Field(json_schema_extra={"is_config": False}, description="PM parameter identifier (can be a counter or a gauge).")
    direction: DirectionEnum = Field(json_schema_extra={"is_config": False}, description="PM parameter direction.")
    location: LocationEnum = Field(json_schema_extra={"is_config": False}, description="PM parameter location.")
    pm_value: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter value. Provided for real-time PM and counters.", default=None, alias="pm-value")
    pm_value_min: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter minimum value. Provided for gauges.", default=None, alias="pm-value-min")
    pm_value_max: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter maximum value. Provided for gauges.", default=None, alias="pm-value-max")
    pm_value_avg: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter average value. Provided for gauges.", default=None, alias="pm-value-avg")
    pm_unit: PmUnitTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Unit of the PM parameter value.", default=None, alias="pm-unit")

class RealTimePmData(YangBaseModel):
    """Container for real-time-pm entries."""

    real_time_pm: RestconfList[RealTimePmItem] | None = Field(json_schema_extra={"is_config": False}, description="Individual real-time-pm record. Contains data updated continuously in real-time.", default=None, alias="real-time-pm")

class ValidityEnum(str, Enum):
    """Enumeration for ValidityEnum
    
    Values:
      * complete: valid throughout an entire period interval
      * suspect: either an error occurred during the period interval or the period interval in which measurements were taken is not the nominal one. (e.g. change of clock time, data-supervision being disabled)
      * partial: indicates that PM collection is still occurring for this bin, the collection has been continuously been collected since the start of the bin, and there were no invalid readings in the bin
    """

    COMPLETE = "complete"
    SUSPECT = "suspect"
    PARTIAL = "partial"

class CurrentPmItem(YangBaseModel):
    """Individual current-pm record. Contains the current bin being counted (bin zero)."""

    period: str = Field(json_schema_extra={"is_config": False}, description="Time period for PM data.")
    monitoring_date_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Monitoring date and time that this data refers to.\nFor real-time and current PM, it represents the start time of the PM data collection.\nFor history PM, it represents the start time of the bin.", default=None, alias="monitoring-date-time")
    resource: str = Field(json_schema_extra={"is_config": False}, description="Existing system resource.")
    resource_type: str | None = Field(json_schema_extra={"is_config": False}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    parameter: str = Field(json_schema_extra={"is_config": False}, description="PM parameter identifier (can be a counter or a gauge).")
    direction: DirectionEnum = Field(json_schema_extra={"is_config": False}, description="PM parameter direction.")
    location: LocationEnum = Field(json_schema_extra={"is_config": False}, description="PM parameter location.")
    pm_value: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter value. Provided for real-time PM and counters.", default=None, alias="pm-value")
    pm_value_min: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter minimum value. Provided for gauges.", default=None, alias="pm-value-min")
    pm_value_max: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter maximum value. Provided for gauges.", default=None, alias="pm-value-max")
    pm_value_avg: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter average value. Provided for gauges.", default=None, alias="pm-value-avg")
    pm_unit: PmUnitTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Unit of the PM parameter value.", default=None, alias="pm-unit")
    validity: ValidityEnum | None = Field(json_schema_extra={"is_config": False}, description="PM parameter validity.", default=None)

class CurrentPmData(YangBaseModel):
    """Container for current-pm entries."""

    current_pm: RestconfList[CurrentPmItem] | None = Field(json_schema_extra={"is_config": False}, description="Individual current-pm record. Contains the current bin being counted (bin zero).", default=None, alias="current-pm")

class HistoryPmItem(YangBaseModel):
    """Individual history-pm record. Contains performance bins (history records) stored in the system."""

    period: str = Field(json_schema_extra={"is_config": False}, description="Time period for PM data.")
    monitoring_date_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Monitoring date and time that this data refers to.\nFor real-time and current PM, it represents the start time of the PM data collection.\nFor history PM, it represents the start time of the bin.", default=None, alias="monitoring-date-time")
    resource: str = Field(json_schema_extra={"is_config": False}, description="Existing system resource.")
    resource_type: str | None = Field(json_schema_extra={"is_config": False}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    parameter: str = Field(json_schema_extra={"is_config": False}, description="PM parameter identifier (can be a counter or a gauge).")
    direction: DirectionEnum = Field(json_schema_extra={"is_config": False}, description="PM parameter direction.")
    location: LocationEnum = Field(json_schema_extra={"is_config": False}, description="PM parameter location.")
    pm_value: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter value. Provided for real-time PM and counters.", default=None, alias="pm-value")
    pm_value_min: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter minimum value. Provided for gauges.", default=None, alias="pm-value-min")
    pm_value_max: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter maximum value. Provided for gauges.", default=None, alias="pm-value-max")
    pm_value_avg: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="PM parameter average value. Provided for gauges.", default=None, alias="pm-value-avg")
    pm_unit: PmUnitTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Unit of the PM parameter value.", default=None, alias="pm-unit")
    validity: ValidityEnum | None = Field(json_schema_extra={"is_config": False}, description="PM parameter validity.", default=None)
    bin: int = Field(json_schema_extra={"is_config": False}, description="Bin number of history PM. Most recent bins have lowest numbers.", ge=0)

class HistoryPmData(YangBaseModel):
    """Container for history-pm entries."""

    history_pm: RestconfList[HistoryPmItem] | None = Field(json_schema_extra={"is_config": False}, description="Individual history-pm record. Contains performance bins (history records) stored in the system.", default=None, alias="history-pm")

class PmThresholdItem(YangBaseModel):
    """Per resource instance/parameter TCA threshold configuration. Needs to be explicitly created by the user, otherwise
    TCA configuration is done per resource-type (in the pm-threshold-profile list).
    This object allows to have per resource instance TCA threshold configuration, deviating from per resource-type TCA
    configuration.
    The absence of this object for a particular resource/parameter implies that the profile is used
    instead.
    """

    parameter: str = Field(json_schema_extra={"is_config": True}, description="PM parameter identifier (can be a counter or a gauge).")
    low_threshold: int | float | str | None = Field(json_schema_extra={"is_config": True}, description="Configured low threshold value for this parameter for this individual resource.", default=None, alias="low-threshold")
    high_threshold: int | float | str | None = Field(json_schema_extra={"is_config": True}, description="Configured high threshold value for this parameter for this individual resource.", default=None, alias="high-threshold")

class PmControlEntryItem(YangBaseModel):
    """PM configuration for one particular resource, for one particular period, direction and location."""

    period: str = Field(json_schema_extra={"is_config": True}, description="Time period for PM data.")
    direction: DirectionEnum = Field(json_schema_extra={"is_config": True}, description="PM parameter direction.")
    location: LocationEnum = Field(json_schema_extra={"is_config": True}, description="PM parameter location.")
    supported_parameters: RestconfList[str] | None = Field(json_schema_extra={"is_config": False}, description="List of PM parameters that this resource type supports for this direction/location.", default=None, alias="supported-parameters")
    data_supervision: bool | None = Field(json_schema_extra={"is_config": True}, description="PM data supervision for this resource.", default=None, alias="data-supervision")
    tca_supervision: bool | None = Field(json_schema_extra={"is_config": True}, description="TCA supervision for this resource.", default=None, alias="tca-supervision")
    pm_threshold: RestconfList[PmThresholdItem] | None = Field(json_schema_extra={"is_config": True}, description="Per resource instance/parameter TCA threshold configuration. Needs to be explicitly created by the user, otherwise\nTCA configuration is done per resource-type (in the pm-threshold-profile list).\nThis object allows to have per resource instance TCA threshold configuration, deviating from per resource-type TCA\nconfiguration.\nThe absence of this object for a particular resource/parameter implies that the profile is used\ninstead.", default=None, alias="pm-threshold")

class PmResourceItem(YangBaseModel):
    """PM configuration per resource instance."""

    resource: str = Field(json_schema_extra={"is_config": True}, description="Existing system resource.")
    resource_type: str | None = Field(json_schema_extra={"is_config": False}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    real_time_supervision: bool | None = Field(json_schema_extra={"is_config": True}, description="Real-time data supervision for this resource.", default=True, alias="real-time-supervision")
    real_time_data_last_reset: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Date and time of the last real time data reset for this resource. If the data was never reset, this is the date and time of this resource's creation.", default=None, alias="real-time-data-last-reset")
    pm_control_entry: RestconfList[PmControlEntryItem] | None = Field(json_schema_extra={"is_config": True}, description="PM configuration for one particular resource, for one particular period, direction and location.", default=None, alias="pm-control-entry")

class PmControl(YangBaseModel):
    """Configuration for currently existing resources in the system that support PM data."""

    pm_resource: RestconfList[PmResourceItem] | None = Field(json_schema_extra={"is_config": True}, description="PM configuration per resource instance.", default=None, alias="pm-resource")

class GlobalDataSupervisionEnum(str, Enum):
    """Enumeration for GlobalDataSupervisionEnum
    
    Values:
      * auto-enabled: Global enabling of PM data-supervision flag.
      * manual: PM data-supervision flag is controlled via pm-profile-entry, or directly per pm-control-entry.
    """

    AUTO_ENABLED = "auto-enabled"
    MANUAL = "manual"

class PmThresholdProfileItem(YangBaseModel):
    """PM configuration per parameter, for this resource type."""

    parameter: str = Field(json_schema_extra={"is_config": True}, description="PM parameter identifier (can be a counter or a gauge).")
    low_threshold: int | float | str | None = Field(json_schema_extra={"is_config": True}, description="Configured low threshold value for resources that have this parameter.", default=None, alias="low-threshold")
    high_threshold: int | float | str | None = Field(json_schema_extra={"is_config": True}, description="Configured high threshold value for resources that have this parameter.", default=None, alias="high-threshold")
    default_low_threshold: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="System defined default value for low threshold for this parameter.", default=None, alias="default-low-threshold")
    default_high_threshold: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="System defined default value for high threshold for this parameter.", default=None, alias="default-high-threshold")
    min_value: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="Minimum value for this parameter.", default=None, alias="min-value")
    max_value: int | float | str | None = Field(json_schema_extra={"is_config": False}, description="Maximum value for this parameter.", default=None, alias="max-value")

class PmProfileEntryItem(YangBaseModel):
    """PM configuration per resource type."""

    resource_type: str = Field(json_schema_extra={"is_config": True}, description="Type of resource.", alias="resource-type")
    period: str = Field(json_schema_extra={"is_config": True}, description="Time period for PM data.")
    direction: DirectionEnum = Field(json_schema_extra={"is_config": True}, description="PM parameter direction.")
    location: LocationEnum = Field(json_schema_extra={"is_config": True}, description="PM parameter location.")
    default_data_supervision: bool | None = Field(json_schema_extra={"is_config": True}, description="For newly created resources of this type, whether they have PM data supervision automatically enabled or not.", default=None, alias="default-data-supervision")
    default_tca_supervision: bool | None = Field(json_schema_extra={"is_config": True}, description="For newly created resources of this type, whether they have PM threshold crossing supervision automatically enabled or not.\n    Only on relevance for pm threshold profile.", default=None, alias="default-tca-supervision")
    pm_threshold_profile: RestconfList[PmThresholdProfileItem] | None = Field(json_schema_extra={"is_config": True}, description="PM configuration per parameter, for this resource type.", default=None, alias="pm-threshold-profile")

class PmProfile(YangBaseModel):
    """PM profile which contains information on all resources that support PM data, together with its related default configuration.
    Changing this configuration has impact on newly created objects.
    """

    global_data_supervision: GlobalDataSupervisionEnum | None = Field(json_schema_extra={"is_config": True}, description="This parameter provides a way to globally enable PM data-supervision without having to toggle it individually.", default=GlobalDataSupervisionEnum.MANUAL, alias="global-data-supervision")
    pm_profile_entry: RestconfList[PmProfileEntryItem] | None = Field(json_schema_extra={"is_config": True}, description="PM configuration per resource type.", default=None, alias="pm-profile-entry")

class TypeEnum(str, Enum):
    """Enumeration for TypeEnum
    
    Values:
      * counter: Counters are parameters that correspond to positive integer numbers, that can only increment over time.
      * gauge: Gauges are analogic values that are measured; they are available as instant, average, maximum and minimum values.
    """

    COUNTER = "counter"
    GAUGE = "gauge"

class PmParameterItem(YangBaseModel):
    """Catalog information for a single PM parameter."""

    parameter: str = Field(json_schema_extra={"is_config": False}, description="PM parameter identifier (can be a counter or a gauge).")
    units: PmUnitTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Units for this parameter.", default=None)
    type: TypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Type of PM parameter, it can be either a counter or a gauge.", default=None)

class PmCatalog(YangBaseModel):
    """PM catalog which contains information on all PM parameters, such as units and type"""

    pm_parameter: RestconfList[PmParameterItem] | None = Field(json_schema_extra={"is_config": False}, description="Catalog information for a single PM parameter.", default=None, alias="pm-parameter")

class Pm(YangBaseModel):
    """Top level container for all Performance Management (pm) data and configuration."""

    real_time_pm_data: RealTimePmData | None = Field(json_schema_extra={"is_config": False}, description="Container for real-time-pm entries.", default=None, alias="real-time-pm-data")
    current_pm_data: CurrentPmData | None = Field(json_schema_extra={"is_config": False}, description="Container for current-pm entries.", default=None, alias="current-pm-data")
    history_pm_data: HistoryPmData | None = Field(json_schema_extra={"is_config": False}, description="Container for history-pm entries.", default=None, alias="history-pm-data")
    pm_control: PmControl | None = Field(json_schema_extra={"is_config": True}, description="Configuration for currently existing resources in the system that support PM data.", default=None, alias="pm-control")
    pm_profile: PmProfile | None = Field(json_schema_extra={"is_config": True}, description="PM profile which contains information on all resources that support PM data, together with its related default configuration.\nChanging this configuration has impact on newly created objects.", default=None, alias="pm-profile")
    pm_catalog: PmCatalog | None = Field(json_schema_extra={"is_config": False}, description="PM catalog which contains information on all PM parameters, such as units and type", default=None, alias="pm-catalog")

class IoaPmData(YangBaseModel):
    """Root data model for ioa-pm"""

    pm: Pm | None = Field(json_schema_extra={"is_config": True}, description="Top level container for all Performance Management (pm) data and configuration.", default=None, alias="ioa-pm:pm")

class DataTypeEnum(str, Enum):
    """Enumeration for DataTypeEnum
    
    Values:
      * current
      * history
      * real-time
    """

    CURRENT = "current"
    HISTORY = "history"
    REAL_TIME = "real-time"

class FilterItem(YangBaseModel):
    """Set of parameters that create a filter for PM data.
    Multiple filters are considered with an AND logic.
    """

    filter_id: int = Field(json_schema_extra={"is_config": None}, description="Identifier for each filter, has no specific meaning.", ge=0, alias="filter-id")
    resource: str | None = Field(json_schema_extra={"is_config": None}, description="Existing system resource.", default=None)
    resource_type: str | None = Field(json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    parameter: str | None = Field(json_schema_extra={"is_config": None}, description="PM parameter identifier (can be a counter or a gauge).", default=None)
    direction: DirectionEnum | None = Field(json_schema_extra={"is_config": None}, description="PM parameter direction.", default=DirectionEnum.ALL)
    location: LocationEnum | None = Field(json_schema_extra={"is_config": None}, description="PM parameter location.", default=LocationEnum.ALL)

class PmRecordItem(YangBaseModel):
    """Individual PM record, containing one parameter value for one specific combination of resource, period and bin.
    The bin key is only used for history; current and real-time always use 0.
    """

    period: str = Field(json_schema_extra={"is_config": None}, description="Time period for PM data.")
    monitoring_date_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": None}, description="Monitoring date and time that this data refers to.\nFor real-time and current PM, it represents the start time of the PM data collection.\nFor history PM, it represents the start time of the bin.", default=None, alias="monitoring-date-time")
    resource: str = Field(json_schema_extra={"is_config": None}, description="Existing system resource.")
    resource_type: str | None = Field(json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    parameter: str = Field(json_schema_extra={"is_config": None}, description="PM parameter identifier (can be a counter or a gauge).")
    direction: DirectionEnum = Field(json_schema_extra={"is_config": None}, description="PM parameter direction.")
    location: LocationEnum = Field(json_schema_extra={"is_config": None}, description="PM parameter location.")
    pm_value: int | float | str | None = Field(json_schema_extra={"is_config": None}, description="PM parameter value. Provided for real-time PM and counters.", default=None, alias="pm-value")
    pm_value_min: int | float | str | None = Field(json_schema_extra={"is_config": None}, description="PM parameter minimum value. Provided for gauges.", default=None, alias="pm-value-min")
    pm_value_max: int | float | str | None = Field(json_schema_extra={"is_config": None}, description="PM parameter maximum value. Provided for gauges.", default=None, alias="pm-value-max")
    pm_value_avg: int | float | str | None = Field(json_schema_extra={"is_config": None}, description="PM parameter average value. Provided for gauges.", default=None, alias="pm-value-avg")
    pm_unit: PmUnitTypeEnum | None = Field(json_schema_extra={"is_config": None}, description="Unit of the PM parameter value.", default=None, alias="pm-unit")
    validity: ValidityEnum | None = Field(json_schema_extra={"is_config": None}, description="PM parameter validity.", default=None)
    bin: int = Field(json_schema_extra={"is_config": None}, description="Bin number of history PM. Most recent bins have lowest numbers.", ge=0)

class GetPmInput(YangBaseModel):
    """Input: None"""

    data_type: DataTypeEnum | None = Field(json_schema_extra={"is_config": None}, description="Type of PM data to retrieve.", default=DataTypeEnum.REAL_TIME, alias="data-type")
    period: str | None = Field(json_schema_extra={"is_config": None}, description="Time period for PM data.\n\nCondition (when): data-type != 'real-time'", default=None)
    reset_data: bool | None = Field(json_schema_extra={"is_config": None}, description="If true, clear the corresponding PM data after the request has been issued. This is only applicable to real-time PM.\n\nCondition (when): ../data-type = 'real-time'", default=False, alias="reset-data")
    number_of_records: int | None = Field(json_schema_extra={"is_config": None}, description="Maximum number of records that will be retrieved, per chassis.", ge=0, le=10000, default=1000, alias="number-of-records")
    skip_records: int | None = Field(json_schema_extra={"is_config": None}, description="Allows user to specify a number of records that will be skipped, so that\nthe total data can be fetched in multiple requests.\nExample:\n- system has 2300 PM records available\n- 1st get-pm with (number-of-records = 1000) and (skip-records = 0);    result has    0..1000 records\n- 2nd get-pm with (number-of-records = 1000) and (skip-records = 1000); result has 1001..2000 records\n- 3nd get-pm with (number-of-records = 1000) and (skip-records = 2000); result has 2001..2300 records", ge=0, default=0, alias="skip-records")
    start_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": None}, description="If provided, defines the start timestamp that will be considered to filter the PM results.\nIf not provided, the oldest data timestamp will be considered.\n\nCondition (when): data-type = 'history'", default=None, alias="start-time")
    end_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": None}, description="If provided, defines the end timestamp that will be considered to filter the PM results.\nIf not provided, the most recent data timestamp will be considered.\n\nCondition (when): data-type = 'history'", default=None, alias="end-time")
    start_bin: int | None = Field(json_schema_extra={"is_config": None}, description="If provided, defines the start bin number that will be considered to filter the PM results.\nIf not provided, the smallest bin number (most recent data) will be considered.\n\nCondition (when): data-type = 'history'", ge=1, default=None, alias="start-bin")
    end_bin: int | None = Field(json_schema_extra={"is_config": None}, description="If provided, defines the end bin number that will be considered to filter the PM results.\nIf not provided, the largest available bin number (oldest data) will be considered.\n\nCondition (when): data-type = 'history'", ge=1, default=None, alias="end-bin")
    chassis_scope: str | None = Field(json_schema_extra={"is_config": None}, description="Chassis scope of command.", default="all", alias="chassis-scope")
    filter: RestconfList[FilterItem] | None = Field(json_schema_extra={"is_config": None}, description="Set of parameters that create a filter for PM data.\nMultiple filters are considered with an AND logic.", default=None)

class GetPmOutput(YangBaseModel):
    """Output: None"""

    number_of_result_records: int | None = Field(json_schema_extra={"is_config": None}, description="Counter of the number of pm-records included in this response.\nNote: in a multi-chassis system, this reflects the value from the node controller chassis alone.", ge=0, default=None, alias="number-of-result-records")
    additional_records_available: bool | None = Field(json_schema_extra={"is_config": None}, description="If true, the system had more PM records than the ones that are being delivered.\nResult will contain only the configured number-of-records.", default=False, alias="additional-records-available")
    retrieval_date_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": None}, description="Represents the time at which the corresponding PM data is retrieved and returned.", default=None, alias="retrieval-date-time")
    pm_record: RestconfList[PmRecordItem] | None = Field(json_schema_extra={"is_config": None}, description="Individual PM record, containing one parameter value for one specific combination of resource, period and bin.\nThe bin key is only used for history; current and real-time always use 0.", default=None, alias="pm-record")

class GetPm(BaseModel):
    """RPC: get-pm"""
    input: GetPmInput
    output: GetPmOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)

class ClearPmInput(YangBaseModel):
    """Input: None"""

    data_type: DataTypeEnum = Field(json_schema_extra={"is_config": None}, description="Type of PM data to clear.", alias="data-type")
    period: str | None = Field(json_schema_extra={"is_config": None}, description="Time period for PM data.\n\nCondition (when): data-type != 'real-time'", default=None)
    direction: DirectionEnum | None = Field(json_schema_extra={"is_config": None}, description="PM parameter direction.", default=DirectionEnum.ALL)
    location: LocationEnum | None = Field(json_schema_extra={"is_config": None}, description="PM parameter location.", default=LocationEnum.ALL)
    resource: str | None = Field(json_schema_extra={"is_config": None}, description="Existing system resource.", default=None)
    resource_type: str | None = Field(json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type")
    AID: str | None = Field(json_schema_extra={"is_config": False}, description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.", min_length=1, max_length=64, default=None)
    chassis_scope: str | None = Field(json_schema_extra={"is_config": None}, description="Chassis scope of command.", default="all", alias="chassis-scope")

class ClearPm(BaseModel):
    """RPC: clear-pm"""
    input: ClearPmInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)
