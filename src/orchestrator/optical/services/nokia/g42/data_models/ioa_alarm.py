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


Decimal64 = Annotated[Decimal, PlainSerializer(format_at_least_two_places, return_type=str)]
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
      * na
      * ingress
      * egress
    """

    NA = "na"
    INGRESS = "ingress"
    EGRESS = "egress"


class LocationEnum(str, Enum):
    """Enumeration for LocationEnum

    Values:
      * na
      * near-end
      * far-end
    """

    NA = "na"
    NEAR_END = "near-end"
    FAR_END = "far-end"


class SeverityEnum(str, Enum):
    """Enumeration for SeverityEnum

    Values:
      * indeterminate
      * critical
      * major
      * minor
      * warning
      * not-reported
      * event
      * cleared
    """

    INDETERMINATE = "indeterminate"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    NOT_REPORTED = "not-reported"
    EVENT = "event"
    CLEARED = "cleared"


class ServiceAffectingEnum(str, Enum):
    """Enumeration for ServiceAffectingEnum

    Values:
      * indeterminate
      * sa
      * nsa
      * sa-nsa
    """

    INDETERMINATE = "indeterminate"
    SA = "sa"
    NSA = "nsa"
    SA_NSA = "sa-nsa"


class AlarmCategoryEnum(str, Enum):
    """Enumeration for AlarmCategoryEnum

    Values:
      * communication
      * facility
      * equipment
      * environmental
      * processing-error
      * software
      * quality-of-service
      * security: Security category for alarms.
    """

    COMMUNICATION = "communication"
    FACILITY = "facility"
    EQUIPMENT = "equipment"
    ENVIRONMENTAL = "environmental"
    PROCESSING_ERROR = "processing-error"
    SOFTWARE = "software"
    QUALITY_OF_SERVICE = "quality-of-service"
    SECURITY = "security"


class OperatorStateEnum(str, Enum):
    """Enumeration for OperatorStateEnum

    Values:
      * none: The alarm is not being taken care of.
      * ack: The alarm is being taken care of. Corrective action not taken yet or has failed.
      * closed: Corrective action taken successfully.
    """

    NONE = "none"
    ACK = "ack"
    CLOSED = "closed"


class AlarmItem(YangBaseModel):
    """Alarm instance that represents a raised alarm, when entry is created, or a cleared alarm,
    when entry is deleted.
    """

    alarm_id: str = Field(
        json_schema_extra={"is_config": False},
        description="Unique identifier of the alarm.\nBased on resource + probable cause.\nNote: this id is intended as an alarm identifier, but it is not intended to provide any additional information.\nOther fields exist to provide this additional information.",
        min_length=0,
        max_length=128,
        alias="alarm-id",
    )
    resource: str | None = Field(
        json_schema_extra={"is_config": False}, description="Existing system resource.", default=None
    )
    resource_type: str | None = Field(
        json_schema_extra={"is_config": False}, description="Type of resource.", default=None, alias="resource-type"
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    alarm_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of alarm, based on an abbreviated code.",
        default=None,
        alias="alarm-type",
    )
    alarm_type_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Human friendly description of the type of the alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="alarm-type-description",
    )
    direction: DirectionEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Direction of the alarm.", default=None
    )
    location: LocationEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Location of the alarm.", default=None
    )
    perceived_severity: SeverityEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Severity of the alarm.",
        default=None,
        alias="perceived-severity",
    )
    reported_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Occurrence timestamp for the alarm.",
        default=None,
        alias="reported-time",
    )
    service_affecting: ServiceAffectingEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on whether this alarm is service affecting or not.",
        default=None,
        alias="service-affecting",
    )
    alarm_category: AlarmCategoryEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Category of the alarm type.",
        default=None,
        alias="alarm-category",
    )
    additional_details: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Free string with additional relevant information provided by the system.",
        min_length=0,
        max_length=256,
        default=None,
        alias="additional-details",
    )
    corrective_action: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System provided information on how to correct the situation that triggered this alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="corrective-action",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": False}, description="User label.", min_length=0, max_length=256, default=None
    )
    last_changed_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of the last change occured in the alarm.",
        default=None,
        alias="last-changed-time",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )
    operator_state: OperatorStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="State of the alarm according with operator action.",
        default=OperatorStateEnum.NONE,
        alias="operator-state",
    )
    operator_text: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Text provided by operator when changing alarm state.",
        min_length=0,
        max_length=256,
        default=None,
        alias="operator-text",
    )
    operator_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Username that last changed the state of this alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="operator-name",
    )
    operator_last_action: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp when the alarm was last changed by operator.",
        default=None,
        alias="operator-last-action",
    )


class CurrentAlarms(YangBaseModel):
    """List of currently raised alarms."""

    number_of_alarms: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of currently raised alarms.",
        ge=0,
        default=None,
        alias="number-of-alarms",
    )
    last_changed: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of the last change in the current alarm list (either a raise or clear event).",
        default=None,
        alias="last-changed",
    )
    alarm: RestconfList[AlarmItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Alarm instance that represents a raised alarm, when entry is created, or a cleared alarm,\nwhen entry is deleted.",
        default=None,
    )


class ArcBehaviorEnum(str, Enum):
    """Enumeration for ArcBehaviorEnum

    Values:
      * leave-alarms: When ARC is set to 'inhibit', leaves current alarms in a raised mode.
      * clear-alarms: When ARC is set to 'inhibit', clears current alarms.
    """

    LEAVE_ALARMS = "leave-alarms"
    CLEAR_ALARMS = "clear-alarms"


class UserSeverityEnum(str, Enum):
    """Enumeration for UserSeverityEnum

    Values:
      * critical
      * major
      * minor
      * warning
      * not-reported
      * event
    """

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    NOT_REPORTED = "not-reported"
    EVENT = "event"


class AlarmSeverityEntryItem(YangBaseModel):
    """Individual entry in alarm-severity-profile, allows to configure the severity for one particular alarm."""

    resource_type: str = Field(
        json_schema_extra={"is_config": True}, description="Type of resource.", alias="resource-type"
    )
    alarm_type: str = Field(
        json_schema_extra={"is_config": True},
        description="Type of alarm, based on an abbreviated code.",
        alias="alarm-type",
    )
    direction: DirectionEnum = Field(
        json_schema_extra={"is_config": True}, description="Configured direction for the current resource type."
    )
    location: LocationEnum = Field(
        json_schema_extra={"is_config": True}, description="Configured location for the current resource type."
    )
    severity: UserSeverityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Configured severity for the current resource type.",
        default=None,
    )
    service_affecting: ServiceAffectingEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Configured service affecting for the current resource type.",
        default=None,
        alias="service-affecting",
    )


class AlarmSeverityProfile(YangBaseModel):
    """Container for all alarm-severity-entries (ASAP table)."""

    alarm_severity_entry: RestconfList[AlarmSeverityEntryItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Individual entry in alarm-severity-profile, allows to configure the severity for one particular alarm.",
        default=None,
        alias="alarm-severity-entry",
    )


class AlarmControl(YangBaseModel):
    """Object related with alarm management control"""

    arc_behavior: ArcBehaviorEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="System wide alarm-reporting-control (ARC) behavior switch.",
        default=ArcBehaviorEnum.LEAVE_ALARMS,
        alias="arc-behavior",
    )
    alarm_severity_profile: AlarmSeverityProfile | None = Field(
        json_schema_extra={"is_config": True},
        description="Container for all alarm-severity-entries (ASAP table).",
        default=None,
        alias="alarm-severity-profile",
    )


class AlarmInventoryItem(YangBaseModel):
    """Inventory with all possible alarm types for the system, containing
    static information for each alarm type.
    """

    alarm_type: str = Field(
        json_schema_extra={"is_config": False},
        description="Type of alarm, based on an abbreviated code.",
        alias="alarm-type",
    )
    resource_type: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of resources to which this alarm applies.",
        default=None,
        alias="resource-type",
    )
    alarm_category: RestconfList[AlarmCategoryEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of possible categories of this alarm type. The same alarm may have different categories, depending on the resource-type it applies to.",
        default=None,
        alias="alarm-category",
    )
    alarm_type_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Human friendly description of the type of the alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="alarm-type-description",
    )
    corrective_action: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System provided information on how to correct the situation that triggered this alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="corrective-action",
    )
    default_severity: RestconfList[UserSeverityEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of possible default severities for this alarm type. The same alarm may have different default severities depending of the resource-type it applies to.",
        default=None,
        alias="default-severity",
    )
    service_affecting: ServiceAffectingEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on whether this alarm is service affecting or not. In some cases, the same alarm may be simultaneously 'sa' and 'nsa', depending on the resource-type it applies to.",
        default=None,
        alias="service-affecting",
    )
    can_be_cleared_by_user: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on whether this alarm can be cleared by the user or not.",
        default=False,
        alias="can-be-cleared-by-user",
    )


class Alarms(YangBaseModel):
    """Top level container for all system alarms, which are defined as an
    undesirable state in a resource that requires corrective action.
    """

    current_alarms: CurrentAlarms | None = Field(
        json_schema_extra={"is_config": False},
        description="List of currently raised alarms.",
        default=None,
        alias="current-alarms",
    )
    alarm_control: AlarmControl | None = Field(
        json_schema_extra={"is_config": True},
        description="Object related with alarm management control",
        default=None,
        alias="alarm-control",
    )
    alarm_inventory: RestconfList[AlarmInventoryItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Inventory with all possible alarm types for the system, containing\nstatic information for each alarm type.",
        default=None,
        alias="alarm-inventory",
    )


class IoaAlarmData(YangBaseModel):
    """Root data model for ioa-alarm"""

    alarms: Alarms | None = Field(
        json_schema_extra={"is_config": True},
        description="Top level container for all system alarms, which are defined as an\nundesirable state in a resource that requires corrective action.",
        default=None,
        alias="ioa-alarm:alarms",
    )


class SetAlarmStateInput(YangBaseModel):
    """Input: None"""

    state: OperatorStateEnum = Field(json_schema_extra={"is_config": None}, description="Alarm state.")
    acknowledge_text: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Optional text that will be stored in the alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="acknowledge-text",
    )
    # Choice: target
    # Case: all-alarms
    all_alarms: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Acknowledge all currently raised alarms.",
        default=None,
        alias="all-alarms",
    )
    # Case: alarm-id-list
    alarm_id_list: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="List of alarm-ids to change the state.",
        min_length=0,
        max_length=128,
        default=None,
        alias="alarm-id-list",
    )


class SetAlarmState(BaseModel):
    """RPC: set-alarm-state"""

    input: SetAlarmStateInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearAlarmInput(YangBaseModel):
    """Input: None"""

    alarm_type: str = Field(
        json_schema_extra={"is_config": None},
        description="Type of alarm to be cleared.\nNote: only some alarms are eligible to be cleared using this operation; see alarm-inventory/can-be-cleared-by-user for details.",
        alias="alarm-type",
    )
    resource: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="Resource of alarm to be cleared.\nMay be one or more resources assocaited with the provided alarm-type.",
        default=None,
    )


class ClearAlarm(BaseModel):
    """RPC: clear-alarm"""

    input: ClearAlarmInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DirectionEnum_1(str, Enum):
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


class LocationEnum_1(str, Enum):
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


class ConditionItem(YangBaseModel):
    """List: condition"""

    alarm_id: str = Field(
        json_schema_extra={"is_config": None},
        description="Unique identifier of the alarm.\nBased on resource + probable cause.\nNote: this id is intended as an alarm identifier, but it is not intended to provide any additional information.\nOther fields exist to provide this additional information.",
        min_length=0,
        max_length=128,
        alias="alarm-id",
    )
    resource: str | None = Field(
        json_schema_extra={"is_config": None}, description="Existing system resource.", default=None
    )
    resource_type: str | None = Field(
        json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type"
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    alarm_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of alarm, based on an abbreviated code.",
        default=None,
        alias="alarm-type",
    )
    alarm_type_description: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Human friendly description of the type of the alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="alarm-type-description",
    )
    direction: DirectionEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Direction of the alarm.", default=None
    )
    location: LocationEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Location of the alarm.", default=None
    )
    perceived_severity: SeverityEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Severity of the alarm.",
        default=None,
        alias="perceived-severity",
    )
    reported_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Occurrence timestamp for the alarm.",
        default=None,
        alias="reported-time",
    )
    service_affecting: ServiceAffectingEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Information on whether this alarm is service affecting or not.",
        default=None,
        alias="service-affecting",
    )
    alarm_category: AlarmCategoryEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Category of the alarm type.",
        default=None,
        alias="alarm-category",
    )
    additional_details: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Free string with additional relevant information provided by the system.",
        min_length=0,
        max_length=256,
        default=None,
        alias="additional-details",
    )
    corrective_action: str | None = Field(
        json_schema_extra={"is_config": None},
        description="System provided information on how to correct the situation that triggered this alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="corrective-action",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": None}, description="User label.", min_length=0, max_length=256, default=None
    )
    last_changed_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Timestamp of the last change occured in the alarm.",
        default=None,
        alias="last-changed-time",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class GetConditionsInput(YangBaseModel):
    """Input: None"""

    resource: str | None = Field(
        json_schema_extra={"is_config": None}, description="Existing system resource.", default=None
    )
    resource_type: str | None = Field(
        json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type"
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    alarm_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of alarm, based on an abbreviated code.",
        default=None,
        alias="alarm-type",
    )
    direction: DirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": None}, description="Direction of the condition.", default=DirectionEnum_1.ALL
    )
    location: LocationEnum_1 | None = Field(
        json_schema_extra={"is_config": None}, description="Location of the condition.", default=LocationEnum_1.ALL
    )


class GetConditionsOutput(YangBaseModel):
    """Output: None"""

    condition: RestconfList[ConditionItem] | None = Field(json_schema_extra={"is_config": None}, default=None)


class GetConditions(BaseModel):
    """RPC: get-conditions"""

    input: GetConditionsInput
    output: GetConditionsOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class AlarmNotificationNotification(YangBaseModel):
    """Notification that is used to report a raise or clear event for an alarm."""

    ne_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="NE name associated with this event.",
        default=None,
        alias="ne-name",
    )
    notification_id: Uint64 | None = Field(
        json_schema_extra={"is_config": None},
        description="Notification id associated with this event.\nNotification id is a number that always increments with each notification,\nand that with a system reboot will keep increasing (even with a buffer added to it),\nguaranteeing that the id always grows.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="notification-id",
    )
    alarm_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Unique identifier of the alarm.\nBased on resource + probable cause.\nNote: this id is intended as an alarm identifier, but it is not intended to provide any additional information.\nOther fields exist to provide this additional information.",
        min_length=0,
        max_length=128,
        default=None,
        alias="alarm-id",
    )
    resource: str | None = Field(
        json_schema_extra={"is_config": None}, description="Existing system resource.", default=None
    )
    resource_type: str | None = Field(
        json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type"
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    alarm_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of alarm, based on an abbreviated code.",
        default=None,
        alias="alarm-type",
    )
    alarm_type_description: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Human friendly description of the type of the alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="alarm-type-description",
    )
    direction: DirectionEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Direction of the alarm.", default=None
    )
    location: LocationEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Location of the alarm.", default=None
    )
    perceived_severity: SeverityEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Severity of the alarm.",
        default=None,
        alias="perceived-severity",
    )
    reported_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Occurrence timestamp for the alarm.",
        default=None,
        alias="reported-time",
    )
    service_affecting: ServiceAffectingEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Information on whether this alarm is service affecting or not.",
        default=None,
        alias="service-affecting",
    )
    alarm_category: AlarmCategoryEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Category of the alarm type.",
        default=None,
        alias="alarm-category",
    )
    additional_details: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Free string with additional relevant information provided by the system.",
        min_length=0,
        max_length=256,
        default=None,
        alias="additional-details",
    )
    corrective_action: str | None = Field(
        json_schema_extra={"is_config": None},
        description="System provided information on how to correct the situation that triggered this alarm.",
        min_length=0,
        max_length=256,
        default=None,
        alias="corrective-action",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": None}, description="User label.", min_length=0, max_length=256, default=None
    )
    last_changed_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Timestamp of the last change occured in the alarm.",
        default=None,
        alias="last-changed-time",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )
