"""Auto-generated Pydantic models from YANG schemas"""

import re
from decimal import Decimal
from enum import Enum
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


class NodeTypeEnum(str, Enum):
    """Enumeration for NodeTypeEnum

    Values:
      * XPDR: Xponder Node Type.
      * ILA: In-Line Amplifier.
      * OADM: Optical Add/Drop Multiplexer
    """

    XPDR = "XPDR"
    ILA = "ILA"
    OADM = "OADM"


class L0ModeOpEnum(str, Enum):
    """Enumeration for L0ModeOpEnum

    Values:
      * standard: GX OLS Standard mode.
      * slte: Submarine LTE.
      * hsc-ols: Hyperscale OLS (HSC OLS), Open Line System.
    """

    STANDARD = "standard"
    SLTE = "slte"
    HSC_OLS = "hsc-ols"


class OperStateEnum(str, Enum):
    """Enumeration for OperStateEnum

    Values:
      * enabled
      * disabled
    """

    ENABLED = "enabled"
    DISABLED = "disabled"


class AlarmReportControlEnum(str, Enum):
    """Enumeration for AlarmReportControlEnum

    Values:
      * allowed: Alarm reporting is allowed.
      * inhibited: Alarm reporting is inhibited.
    """

    ALLOWED = "allowed"
    INHIBITED = "inhibited"


class ChassisRoleEnum(str, Enum):
    """Enumeration for ChassisRoleEnum

    Values:
      * unknown: Chassis role is not determined yet
      * main-chassis: The chassis is designated as a main-chassis of the Multi-chassis NE.
      * sub-chassis: The chassis is designated as a sub-chassis of the Multi-chassis NE.
    """

    UNKNOWN = "unknown"
    MAIN_CHASSIS = "main-chassis"
    SUB_CHASSIS = "sub-chassis"


class AdminStateEnum(str, Enum):
    """Enumeration for AdminStateEnum

    Values:
      * lock
      * unlock
      * maintenance
    """

    LOCK = "lock"
    UNLOCK = "unlock"
    MAINTENANCE = "maintenance"


class ExpectedPemTypeEnum(str, Enum):
    """Enumeration for ExpectedPemTypeEnum

    Values:
      * DC: DC PEM
      * AC-high-line: High-line (220V) AC PEM
      * AC-low-line: Low-line (110V) AC PEM
      * HV-DC: High Voltage DC PEM
      * AC-high-line-HP: High-line (220V) AC PEM High Power
      * AC-low-line-HP: Low-line (110V) AC PEM High Power
      * DC-HP: DC PEM High Power
    """

    DC = "DC"
    AC_HIGH_LINE = "AC-high-line"
    AC_LOW_LINE = "AC-low-line"
    HV_DC = "HV-DC"
    AC_HIGH_LINE_HP = "AC-high-line-HP"
    AC_LOW_LINE_HP = "AC-low-line-HP"
    DC_HP = "DC-HP"


class ExpectedFanTypeEnum(str, Enum):
    """Enumeration for ExpectedFanTypeEnum

    Values:
      * single-rotar: Standard FAN type.
      * counter-rotating: Counter rotating FAN type.
    """

    SINGLE_ROTAR = "single-rotar"
    COUNTER_ROTATING = "counter-rotating"


class FilterMaintenanceIntervalEnum(str, Enum):
    """Enumeration for FilterMaintenanceIntervalEnum

    Values:
      * never: No removable dust filter or no replacement required.
      * interval-1-month: 1 month interval for filter replacement.
      * interval-2-months: 2 months interval for filter replacement.
      * interval-4-months: 4 months interval for filter replacement.
      * interval-6-months: 6 months interval for filter replacement.
      * interval-8-months: 8 months interval for filter replacement.
      * interval-10-months: 10 months interval for filter replacement.
      * interval-12-months: 1 year interval for filter replacement.
    """

    NEVER = "never"
    INTERVAL_1_MONTH = "interval-1-month"
    INTERVAL_2_MONTHS = "interval-2-months"
    INTERVAL_4_MONTHS = "interval-4-months"
    INTERVAL_6_MONTHS = "interval-6-months"
    INTERVAL_8_MONTHS = "interval-8-months"
    INTERVAL_10_MONTHS = "interval-10-months"
    INTERVAL_12_MONTHS = "interval-12-months"


class PowerRedundancyEnum(str, Enum):
    """Enumeration for PowerRedundancyEnum

    Values:
      * one-plus-one: PEM is redundant within a bank of 2 PEMs.
      * one-for-n: PEM is redundant against any other PEM.
    """

    ONE_PLUS_ONE = "one-plus-one"
    ONE_FOR_N = "one-for-n"


class FwStatusEnum(str, Enum):
    """Enumeration for FwStatusEnum

    Values:
      * not-applicable: Equipment doesn't have upgradable firmware.
      * current: Current firmware is up-to-date.
      * not-current: Current firmware is not up-to-date against the expected one. Note: this value is used when no further details exist regarding the reason why it is not-current.
      * unavailable: Information on firmware status is currently unavailable.
      * compatible: Current firmware is compatible with the expected one, but not exactly the same.
      * not-current-coldboot-required: Current firmware is not up-to-date and a coldboot is required to make it up-to-date.
      * not-current-warmboot-required: Current firmware is not up-to-date and a warmboot is required to make it up-to-date.
      * install-in-progress: Firmware is currently being installed.
    """

    NOT_APPLICABLE = "not-applicable"
    CURRENT = "current"
    NOT_CURRENT = "not-current"
    UNAVAILABLE = "unavailable"
    COMPATIBLE = "compatible"
    NOT_CURRENT_COLDBOOT_REQUIRED = "not-current-coldboot-required"
    NOT_CURRENT_WARMBOOT_REQUIRED = "not-current-warmboot-required"
    INSTALL_IN_PROGRESS = "install-in-progress"


class CurrentFwItem(YangBaseModel):
    """List of current firmware available in the card."""

    fw_name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the firmware.",
        min_length=0,
        max_length=32,
        alias="fw-name",
    )
    fw_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Current version of the firmware.",
        min_length=0,
        max_length=32,
        default=None,
        alias="fw-version",
    )
    expected_fw_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Expected version of the firmware.",
        min_length=0,
        max_length=32,
        default=None,
        alias="expected-fw-version",
    )
    fw_status: FwStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Status for this particular firmware.",
        default=FwStatusEnum.UNAVAILABLE,
        alias="fw-status",
    )


class Inventory(YangBaseModel):
    """Inventory data for a present FRU."""

    hardware_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Hardware version of this FRU.",
        default=None,
        alias="hardware-version",
    )
    actual_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="FRU type of actual equipment.",
        default=None,
        alias="actual-type",
    )
    actual_subtype: str | None = Field(
        json_schema_extra={"is_config": False},
        description="FRU subtype of actual equipment - only available if applicable.",
        default=None,
        alias="actual-subtype",
    )
    sw_support_revision: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Software revision currently installed.",
        ge=0,
        default=0,
        alias="sw-support-revision",
    )
    PON: str | None = Field(
        json_schema_extra={"is_config": False}, description="Current PON of the equipment.", default=None
    )
    serial_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Serial number of the equipment.",
        min_length=1,
        max_length=16,
        default=None,
        alias="serial-number",
    )
    clei: str | None = Field(
        json_schema_extra={"is_config": False}, description="Common Language Equipment Identifier.", default=None
    )
    vendor: str | None = Field(
        json_schema_extra={"is_config": False}, description="Vendor of this equipment.", default=None
    )
    part_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Part number for this equipment.",
        default=None,
        alias="part-number",
    )
    manufacture_date: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Manufacture Date in a date-time format (YYYY-MM-DDThh:mm:ssZ) or 'NA' if not available.",
        default=None,
        alias="manufacture-date",
    )
    insertion_date: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Insertion Date in a date-time format (YYYY-MM-DDThh:mm:ssZ) or 'NA' if not available.",
        default=None,
        alias="insertion-date",
    )
    number_of_lanes: int | None = Field(
        json_schema_extra={"is_config": False},
        description="When applicatible, provides number of supported optical lanes in this equipment.",
        ge=0,
        default=None,
        alias="number-of-lanes",
    )
    vendor_compliance_code: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Vendor Compliance Code information for 3rd party TOMs.",
        min_length=0,
        max_length=128,
        default=None,
        alias="vendor-compliance-code",
    )
    fw_status: FwStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Summary status for all the firmware for this card.",
        default=FwStatusEnum.NOT_APPLICABLE,
        alias="fw-status",
    )
    current_fw: RestconfList[CurrentFwItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of current firmware available in the card.",
        default=None,
        alias="current-fw",
    )
    sub_inventory: str | None = Field(
        json_schema_extra={"is_config": False},
        description="For TOM-adapter, this holds the information of the plugged-in equipment to the adapter.",
        min_length=0,
        max_length=1000,
        default=None,
        alias="sub-inventory",
    )


class SlotItem(YangBaseModel):
    """Slot equipment holder details."""

    name: str = Field(json_schema_extra={"is_config": False}, description="Slot name.")
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    supported_type: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of supported types in this equipment holder.\nIf a specific type is provisioned, the list has only that type.",
        min_length=0,
        max_length=32,
        default=None,
        alias="supported-type",
    )
    installed_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently installed type in this equipment holder. If empty, means no FRU is present.",
        min_length=0,
        max_length=32,
        default=None,
        alias="installed-type",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    current_equipment: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Name of the equipment that is currently required in this slot.",
        min_length=1,
        max_length=64,
        default=None,
        alias="current-equipment",
    )
    inventory: Inventory | None = Field(
        json_schema_extra={"is_config": False}, description="Inventory data for a present FRU.", default=None
    )


class ChassisItem(YangBaseModel):
    """Chassis configuration and state."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Chassis name.", min_length=1, max_length=64
    )
    is_node_controller: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Tells if this chassis the node controller of this NE.",
        default=None,
        alias="is-node-controller",
    )
    chassis_role: ChassisRoleEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies the role of the chassis in a multi-chassis NE.",
        default=ChassisRoleEnum.UNKNOWN,
        alias="chassis-role",
    )
    expected_serial_number: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Inform the NC the serial number of a sub-chassis. For the main-chassis, the value is auto-filled with its own serial number",
        min_length=0,
        max_length=16,
        default=None,
        alias="expected-serial-number",
    )
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore.",
            min_length=0,
            max_length=256,
            default=None,
            alias="alias-name",
        )
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    required_type: str = Field(
        json_schema_extra={"is_config": True}, description="Chassis type.", alias="required-type"
    )
    required_subtype: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The subtype of the chassis",
        min_length=0,
        max_length=32,
        default=None,
        alias="required-subtype",
    )
    chassis_location: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User defined location",
        min_length=0,
        max_length=128,
        default=None,
        alias="chassis-location",
    )
    rack_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User defined rack name (withing the location)",
        min_length=0,
        max_length=128,
        default=None,
        alias="rack-name",
    )
    position_in_rack: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Position of the chassis within the rack.",
        ge=0,
        default=None,
        alias="position-in-rack",
    )
    expected_pem_type: ExpectedPemTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines what is the expected type of PEMs that this chassis will have.\nIt is not possible to configure each PEM slot individually, as all PEMs need to be of the same type.",
        default=ExpectedPemTypeEnum.DC,
        alias="expected-pem-type",
    )
    expected_fan_type: ExpectedFanTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines what is the expected type of FANs that this chassis will have.\nIt is not possible to configure each FAN slot individually, this needs to be done at the chassis level.",
        default=ExpectedFanTypeEnum.COUNTER_ROTATING,
        alias="expected-fan-type",
    )
    pem_under_voltage_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Under voltage threshold on PEM input feed.",
        default=None,
        alias="pem-under-voltage-threshold",
    )
    pem_over_voltage_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Over voltage threshold on PEM input feed.",
        default=None,
        alias="pem-over-voltage-threshold",
    )
    total_available_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Total available power at the chassis level, considering the power provided by all enabled PEMs and the\npower-redundancy mode.",
        default=None,
        alias="total-available-power",
    )
    actual_power_draw: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Real time actual power draw.\nSame as chassis real-time PM parameter 'actual-power-draw'.",
        default=None,
        alias="actual-power-draw",
    )
    reserved_power_draw: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Theoretical worst case total power draw of the chassis that includes\nall equipment operating at their max power.",
        default=None,
        alias="reserved-power-draw",
    )
    actual_power_draw_alarm_threshold: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Threshold for raising the PWRDRAW alarm, in percentage.\nThe alarm is raised if:\nactual-power-draw > (total-available-power * actual-power-draw-alarm-threshold)\nThe smallest this percentage is, the more conservative the alarm will be.\nIf value is zero, then alarm is disabled.\nNOTE: This attribute is only supported for chassis types that support power-control.",
        ge=0,
        le=100,
        default=None,
        alias="actual-power-draw-alarm-threshold",
    )
    configured_ambient_temperature: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Configured ambient temperature for the chassis, used to compute the FRU's power consumption.",
        ge=0,
        default=None,
        alias="configured-ambient-temperature",
    )
    filter_maintenance_interval: FilterMaintenanceIntervalEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration for the filter replacement.\nWhen the configured time interval expires, system reports an alarm indicating that dust filter needs to be replaced.",
        default=FilterMaintenanceIntervalEnum.NEVER,
        alias="filter-maintenance-interval",
    )
    filter_insertion_date: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Filter insertion date, if applicable.\n\nCondition (when): ../filter-maintenance-interval != 'never'",
        default="never",
        alias="filter-insertion-date",
    )
    power_redundancy: PowerRedundancyEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of the PEM redundancy mode.",
        default=PowerRedundancyEnum.ONE_PLUS_ONE,
        alias="power-redundancy",
    )
    no_switchover: OperStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="If enabled, the standby controller will be locked out from taking over the active card. This means no manual or autonomous switchovers will happen.",
        default=OperStateEnum.DISABLED,
        alias="no-switchover",
    )
    active_controller_slot: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies the active controller slot name. A change to this attribute implies a switchover has happened.",
        default="none",
        alias="active-controller-slot",
    )
    equipment_discovery_ready: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Represents the equipment discovery state for the current chassis.\nIt will remain as 'false' until all equipment was discovered during startup.\nEquipment added after startup will not contribute to the update of this state.",
        default=False,
        alias="equipment-discovery-ready",
    )
    alarm_report_ready: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Represents the alarm monitoring state for this chassis.\nAfter a system restart, alarms are kept persistent for a grace minute period,\nafter which they will be cleared, unless they are reconfirmed.\nThis state provides visibility whether that grace period has passed or not.\nWhen this state is true, there are no more cached alarms raised.",
        default=False,
        alias="alarm-report-ready",
    )
    inventory: Inventory | None = Field(
        json_schema_extra={"is_config": False}, description="Inventory data for a present FRU.", default=None
    )
    slot: RestconfList[SlotItem] | None = Field(
        json_schema_extra={"is_config": False}, description="Slot equipment holder details.", default=None
    )


class CategoryEnum(str, Enum):
    """Enumeration for CategoryEnum

    Values:
      * controller
      * line-card
      * fan
      * power-supply
      * other
      * carrier-card
      * blank
    """

    CONTROLLER = "controller"
    LINE_CARD = "line-card"
    FAN = "fan"
    POWER_SUPPLY = "power-supply"
    OTHER = "other"
    CARRIER_CARD = "carrier-card"
    BLANK = "blank"


class RedundancyStatusEnum(str, Enum):
    """Enumeration for RedundancyStatusEnum

    Values:
      * active
      * standby
      * not-in-service
    """

    ACTIVE = "active"
    STANDBY = "standby"
    NOT_IN_SERVICE = "not-in-service"


class RedundancyStandbyStatusEnum(str, Enum):
    """Enumeration for RedundancyStandbyStatusEnum

    Values:
      * ready-synchronized: Standby controller is sync and ready.
      * not-ready-synchronizing: Standby controller synchronizing data with active controller.
      * not-ready-synchronize-fail: Synchronization fail.
      * lock-out: Protection in lock-out state.
      * card-not-present: Standby card is not present
    """

    READY_SYNCHRONIZED = "ready-synchronized"
    NOT_READY_SYNCHRONIZING = "not-ready-synchronizing"
    NOT_READY_SYNCHRONIZE_FAIL = "not-ready-synchronize-fail"
    LOCK_OUT = "lock-out"
    CARD_NOT_PRESENT = "card-not-present"


class ControllerCard(YangBaseModel):
    """Container of parameters related with controller cards."""

    redundancy_status: RedundancyStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Controller state.",
        default=RedundancyStatusEnum.NOT_IN_SERVICE,
        alias="redundancy-status",
    )
    redundancy_standby_status: RedundancyStandbyStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="State of the controller redundancy.",
        default=RedundancyStandbyStatusEnum.NOT_READY_SYNCHRONIZING,
        alias="redundancy-standby-status",
    )
    number_of_switchover_events: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of times that an active controller card has switchover. Value only visibile on active controller card.",
        ge=0,
        default=None,
        alias="number-of-switchover-events",
    )
    time_of_last_switchover: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of the last controller switchover event. Value only visible on active controller card.",
        default=None,
        alias="time-of-last-switchover",
    )
    additional_details: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Additional details for synchronization status.",
        min_length=0,
        max_length=128,
        default=None,
        alias="additional-details",
    )


class PropertyItem(YangBaseModel):
    """Type specific property, auto instanciated by the system, but configurable by the user."""

    name: str = Field(json_schema_extra={"is_config": True}, description="Name of the property.")
    value: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Value of the property. Will always be a 'string', even if it corresponds to a number or other type.",
        default=None,
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Description of this property, including type restrictions.",
        min_length=0,
        max_length=512,
        default=None,
    )


class PortTypeEnum(str, Enum):
    """Enumeration for PortTypeEnum

    Values:
      * line: Refers to line-side 'colored' CWDM or DWDM optical module/transceiver.
      * tributary: Refers to standard 'grey' interfaces/transceivers to interface with other client equipment.
      * usb: USB port.
      * comm: Communication ports.
      * uplink: Refers to ports of an aggregation function that connect to an adjunct line function.
      * tributary-subport: Same as tributary, but for scenarios where the main tributary port is split into multiple subports.
      * optical: General optical port, with or without monitoring function.
      * otdr: Generic OTDR function, except for external OTDR measurement.
      * pluggable: Port function represents the L0 module cage for pluggable interfaces.
      * ocm: OCM port.
      * extension: Port that can be used for generic extension functions.
    """

    LINE = "line"
    TRIBUTARY = "tributary"
    USB = "usb"
    COMM = "comm"
    UPLINK = "uplink"
    TRIBUTARY_SUBPORT = "tributary-subport"
    OPTICAL = "optical"
    OTDR = "otdr"
    PLUGGABLE = "pluggable"
    OCM = "ocm"
    EXTENSION = "extension"


class DirectionEnum(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * not-applicable: Not applicable.
      * tx: Tx direction.
      * rx: Rx direction.
      * rxtx: Both Rx and Tx directions.
    """

    NOT_APPLICABLE = "not-applicable"
    TX = "tx"
    RX = "rx"
    RXTX = "rxtx"


class ExternalConnectivityEnum(str, Enum):
    """Enumeration for ExternalConnectivityEnum

    Values:
      * no: Port has no NMS external connectivity.
      * yes: Port has NMS external connectivity.
    """

    NO = "no"
    YES = "yes"


class PhyModeEnum(str, Enum):
    """Enumeration for PhyModeEnum

    Values:
      * passive: Passive device, no date-rate, or Cable ID.
      * 100GE: 100GE
      * 200GE: 200GE
      * 400GE: 400GE
      * 4x100GE: 4x100GE
      * 100G: 100G
      * 4x10G: 4x10G
      * 4x10GE: 4x10GE
      * 1GE: 1GE
      * 2G5: 2G5
      * 10G: 10G
      * 10GE: 10GE
      * 2G5E: 2G5E
      * 40GE: 40GE
      * 40G: 40G
      * 4x100G: 4x100G
      * 200G: 200G
      * 155M: OC-3 (155M/ 1G) OSC
      * 2x100GE: 2x100GE
      * 1G: 1G
      * 4G: 4G
      * 400G: 400G
      * 2G: 2G
      * 8G: 8G
      * 16G: 16G
      * 32G: 32G
      * 622M: STM4
      * 4x16G: 4x16G
      * 4x8G: 4x8G
      * 2x32G: 2x32G
      * AMP-TOF: Amplifier-TOF
      * 800GE: 800GE
      * 2xOTU4: 2xOTU4
      * 2x400GE: 2x400GE
    """

    PASSIVE = "passive"
    _100GE = "100GE"
    _200GE = "200GE"
    _400GE = "400GE"
    _4X100GE = "4x100GE"
    _100G = "100G"
    _4X10G = "4x10G"
    _4X10GE = "4x10GE"
    _1GE = "1GE"
    _2G5 = "2G5"
    _10G = "10G"
    _10GE = "10GE"
    _2G5E = "2G5E"
    _40GE = "40GE"
    _40G = "40G"
    _4X100G = "4x100G"
    _200G = "200G"
    _155M = "155M"
    _2X100GE = "2x100GE"
    _1G = "1G"
    _4G = "4G"
    _400G = "400G"
    _2G = "2G"
    _8G = "8G"
    _16G = "16G"
    _32G = "32G"
    _622M = "622M"
    _4X16G = "4x16G"
    _4X8G = "4x8G"
    _2X32G = "2x32G"
    AMP_TOF = "AMP-TOF"
    _800GE = "800GE"
    _2XOTU4 = "2xOTU4"
    _2X400GE = "2x400GE"


class EnableSwitchEnum(str, Enum):
    """Enumeration for EnableSwitchEnum

    Values:
      * disabled
      * enabled
    """

    DISABLED = "disabled"
    ENABLED = "enabled"


class UpgradeStatusEnum(str, Enum):
    """Enumeration for UpgradeStatusEnum

    Values:
      * idle: Upgrade status not available.
      * in-progress: Upgrade install is in progress.
      * success: Upgrade installed.
      * failed: Upgrade instalation failed.
      * unknown: Upgrade status not known.
    """

    IDLE = "idle"
    IN_PROGRESS = "in-progress"
    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN = "unknown"


class StatusEnum(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * set: Parameter set.
      * unknown: Parameter unknown.
      * in-progress: Parameter in progress.
      * failed: Parameter failed.
      * not-supported: Parameter not supported.
    """

    SET = "set"
    UNKNOWN = "unknown"
    IN_PROGRESS = "in-progress"
    FAILED = "failed"
    NOT_SUPPORTED = "not-supported"


class SerdesItem(YangBaseModel):
    """The user configured (or overridden) set of serializer/desserializer."""

    name: str = Field(
        json_schema_extra={"is_config": True},
        description="Name of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    value: str = Field(
        json_schema_extra={"is_config": True},
        description="Value of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="State of the advanced parameter (as observable on the system) once it is configured.",
        default=StatusEnum.UNKNOWN,
    )


class Tom(YangBaseModel):
    """TOM (Transceiver Optical Module) pluggable information."""

    required_type: str = Field(
        json_schema_extra={"is_config": True}, description="The type of the TOM.", alias="required-type"
    )
    required_subtype: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The subtype of the TOM.",
        min_length=0,
        max_length=32,
        default=None,
        alias="required-subtype",
    )
    phy_mode: PhyModeEnum | None = Field(
        json_schema_extra={"is_config": True}, description="Configured Phy Mode.", default=None, alias="phy-mode"
    )
    supported_phy_modes: RestconfList[PhyModeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of supported Phy Modes by this TOM type.",
        default=None,
        alias="supported-phy-modes",
    )
    power_class_override: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Used to override the power class for 3rd party TOM.",
        default=None,
        alias="power-class-override",
    )
    upgrade_status: UpgradeStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current upgrade status.",
        default=UpgradeStatusEnum.IDLE,
        alias="upgrade-status",
    )
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore.",
            min_length=0,
            max_length=256,
            default=None,
            alias="alias-name",
        )
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    enable_serdes: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls enabling/disabling of configuring TOM SerDes.",
        default=False,
        alias="enable-serdes",
    )
    serdes: RestconfList[SerdesItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="The user configured (or overridden) set of serializer/desserializer.\n\nCondition (when): ../enable-serdes = 'true'",
        default=None,
    )


class TypeEnum(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * storage: USB port can be used for file storage, and supports associated file management operations.
      * power-supply: USB port can be used to power additional external equipment (for example, passive shelves).
    """

    STORAGE = "storage"
    POWER_SUPPLY = "power-supply"


class Usb(YangBaseModel):
    """Represents the USB function of this port."""

    type: TypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="The role that this usb port has.", default=None
    )
    present: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes the presence state of the USB connector.",
        default=False,
    )
    available_space: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The current available storage space in the file-system associated with this USB port.\n\nCondition (when): ../type = 'storage' and ../present = 'true'",
        ge=0,
        default=None,
        alias="available-space",
    )
    total_space: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The total storage space available in the file-system associated with this USB port.\n\nCondition (when): ../type = 'storage' and ../present = 'true'",
        ge=0,
        default=None,
        alias="total-space",
    )
    usb_path: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Local filesystem path on where this USB file-system is mounted; this can be used as a target/source for file transfer operations.\n\nCondition (when): ../type = 'storage' and ../present = 'true'",
        min_length=0,
        max_length=32,
        default=None,
        alias="usb-path",
    )


class DuplexModeEnum(str, Enum):
    """Enumeration for DuplexModeEnum

    Values:
      * unknown: Link is currently disconnected or initializing.
      * full: Full duplex.
      * half: Half duplex.
    """

    UNKNOWN = "unknown"
    FULL = "full"
    HALF = "half"


class EthernetRateEnum(str, Enum):
    """Enumeration for EthernetRateEnum

    Values:
      * unknown
      * 1
      * 10
      * 100
      * 1000
      * 10000
      * maximum
    """

    UNKNOWN = "unknown"
    _1 = "1"
    _10 = "10"
    _100 = "100"
    _1000 = "1000"
    _10000 = "10000"
    MAXIMUM = "maximum"


class FlowControlEnum(str, Enum):
    """Enumeration for FlowControlEnum

    Values:
      * unknown: Link is currently disconnected or initializing.
      * disabled: No pause frames are supported.
      * bi-directional: Symmetric flow (transmit and receive).
      * egress-only: Transmit direction only.
      * ingress-only: Receive direction only.
    """

    UNKNOWN = "unknown"
    DISABLED = "disabled"
    BI_DIRECTIONAL = "bi-directional"
    EGRESS_ONLY = "egress-only"
    INGRESS_ONLY = "ingress-only"


class RedundancyStateEnum(str, Enum):
    """Enumeration for RedundancyStateEnum

    Values:
      * none: No redundancy.
      * active: Port is active.
      * standby: Port is on standby.
    """

    NONE = "none"
    ACTIVE = "active"
    STANDBY = "standby"


class ModeEnum(str, Enum):
    """Enumeration for ModeEnum

    Values:
      * L1: L1 ETH User Channel Mode.
      * L3: L3 IP Mode(Default).
    """

    L1 = "L1"
    L3 = "L3"


class LldpAdminStatusEnum(str, Enum):
    """Enumeration for LldpAdminStatusEnum

    Values:
      * tx-only: LLDP agent transmits LLDP frames on this port but it does not store connected remote system information.
      * rx-only: LLDP agent receives, but it does not transmit LLDP frames on this port.
      * tx-and-rx: LLDP agent transmits and receives LLDP frames on this port.
      * disabled: LLDP agent does not transmit or receive LLDP frames on this port.
    """

    TX_ONLY = "tx-only"
    RX_ONLY = "rx-only"
    TX_AND_RX = "tx-and-rx"
    DISABLED = "disabled"


class CommEth(YangBaseModel):
    """Communication ethernet port."""

    auto_negotiation: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Auto negotiation mode.",
        default=EnableSwitchEnum.ENABLED,
        alias="auto-negotiation",
    )
    mtu: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The maximum transmission unit size in octets for the physical Ethernet port.",
        ge=1280,
        le=9202,
        default=1500,
    )
    duplex_mode: DuplexModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Duplex mode; only valid if auto-negotiation is disabled.\n\nCondition (when): ../auto-negotiation = 'disabled'",
        default=DuplexModeEnum.FULL,
        alias="duplex-mode",
    )
    operational_duplex_mode: DuplexModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Operational duplex mode.",
        default=DuplexModeEnum.UNKNOWN,
        alias="operational-duplex-mode",
    )
    rate: EthernetRateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Required Ethernet rate; only valid if auto-negotiation is disabled.\n\nCondition (when): ../auto-negotiation = 'disabled'",
        default=EthernetRateEnum.MAXIMUM,
    )
    operational_rate: EthernetRateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Operational Ethernet rate.",
        default=EthernetRateEnum.UNKNOWN,
        alias="operational-rate",
    )
    flow_control: FlowControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the type of flow control to be supported.\n\nCondition (when): ../auto-negotiation = 'disabled'",
        default=FlowControlEnum.DISABLED,
        alias="flow-control",
    )
    operational_flow_control: FlowControlEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Operational flow control.",
        default=FlowControlEnum.UNKNOWN,
        alias="operational-flow-control",
    )
    redundancy_state: RedundancyStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Redundancy state of the comm port.",
        default=RedundancyStateEnum.NONE,
        alias="redundancy-state",
    )
    mac_address: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="MAC Address of the port.",
        default="00:00:00:00:00:00",
        alias="mac-address",
    )
    lldp_transmit_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The interval to transmit LLDP Tx TLVs.",
        ge=1,
        le=16383,
        default=30,
        alias="lldp-transmit-interval",
    )
    lldp_mgmt_addr_if: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify which interface's IP address to be used for management address.",
        min_length=1,
        max_length=64,
        default=None,
        alias="lldp-mgmt-addr-if",
    )
    mode: ModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the mode of operation of control channel.",
        default=ModeEnum.L3,
    )
    lldp_admin_status: LldpAdminStatusEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="LLDP operational mode for this port.",
        default=LldpAdminStatusEnum.DISABLED,
        alias="lldp-admin-status",
    )


class PortItem(YangBaseModel):
    """Generic card port."""

    name: str = Field(json_schema_extra={"is_config": True}, description="Port name.")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore.",
            min_length=0,
            max_length=256,
            default=None,
            alias="alias-name",
        )
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    port_type: PortTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The port type. Each port type supports different features and services.",
        default=None,
        alias="port-type",
    )
    direction: DirectionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Direction of the port.",
        default=DirectionEnum.NOT_APPLICABLE,
    )
    parent_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the parent port. Only applicable for sub-ports.",
        default=None,
        alias="parent-port",
    )
    subport_list: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of sub-ports associated with this port.\nOnly applicable when this port is a parent port.",
        default=None,
        alias="subport-list",
    )
    hosted_interface: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Top level interface hosted in this port.",
        default=None,
        alias="hosted-interface",
    )
    supported_type: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of supported types in this equipment holder.\nIf a specific type is provisioned, the list has only that type.",
        min_length=0,
        max_length=32,
        default=None,
        alias="supported-type",
    )
    installed_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently installed type in this equipment holder. If empty, means no FRU is present.",
        min_length=0,
        max_length=32,
        default=None,
        alias="installed-type",
    )
    connected_to: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicate neighbour port entity to which the current port is connected to.\nThis is not validated by the NE and can be used by the customers (or NMS) for topology construction.\nThis parameter is available independently on any automated discovery mechanisms that may exist in the port.",
        min_length=0,
        max_length=128,
        default=None,
        alias="connected-to",
    )
    external_connectivity: ExternalConnectivityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates whether the port is connected or to be connected externally or not.",
        default=ExternalConnectivityEnum.NO,
        alias="external-connectivity",
    )
    diverse_routing: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls enabling/disabling of diverse routing capability.",
        default=False,
        alias="diverse-routing",
    )
    tom: Tom | None = Field(
        json_schema_extra={"is_config": True},
        description="TOM (Transceiver Optical Module) pluggable information.",
        default=None,
    )
    usb: Usb | None = Field(
        json_schema_extra={"is_config": False}, description="Represents the USB function of this port.", default=None
    )
    comm_eth: CommEth | None = Field(
        json_schema_extra={"is_config": True},
        description="Communication ethernet port.",
        default=None,
        alias="comm-eth",
    )
    inventory: Inventory | None = Field(
        json_schema_extra={"is_config": False}, description="Inventory data for a present FRU.", default=None
    )


class BaudRateEnum(str, Enum):
    """Enumeration for BaudRateEnum

    Values:
      * auto-sensing: System will auto-detect the baud-rate based on 'ENTER' presses on serial console client side. The detected baud-rate is then locked, and shown in the 'actual-baudrate' parameter. Note: not all cards support auto-sensing capability.
      * 9600
      * 19200
      * 38400
      * 57600
      * 115200
    """

    AUTO_SENSING = "auto-sensing"
    _9600 = "9600"
    _19200 = "19200"
    _38400 = "38400"
    _57600 = "57600"
    _115200 = "115200"


class ConsoleBaudRateEnum(str, Enum):
    """Enumeration for ConsoleBaudRateEnum

    Values:
      * unknown
      * 9600
      * 19200
      * 38400
      * 57600
      * 115200
    """

    UNKNOWN = "unknown"
    _9600 = "9600"
    _19200 = "19200"
    _38400 = "38400"
    _57600 = "57600"
    _115200 = "115200"


class AutoSensingStateEnum(str, Enum):
    """Enumeration for AutoSensingStateEnum

    Values:
      * sensing: Represents that the auto-sensing algorithm is active, waiting for 'ENTER' presses on serial console client side.
      * locked: Auto-sensing algorithm already discovered the port's baud-rate (visible in the actual-baud-rate parameter), and has locked that value. No further auto-sensing is performed until baud-rate is reconfigured or card reboots.
    """

    SENSING = "sensing"
    LOCKED = "locked"


class LocalSwitchEnum(str, Enum):
    """Enumeration for LocalSwitchEnum

    Values:
      * use-global-switch: Console switch is using the global switch configuration.
      * force-enable: Console switch is enabled.
      * force-disable: Console switch is disabled.
    """

    USE_GLOBAL_SWITCH = "use-global-switch"
    FORCE_ENABLE = "force-enable"
    FORCE_DISABLE = "force-disable"


class Console(YangBaseModel):
    """Parameters associated with this card's serial console port."""

    baud_rate: BaudRateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured baud-rate for this card's console port.\nDefault value is card type specific.",
        default=None,
        alias="baud-rate",
    )
    actual_baud_rate: ConsoleBaudRateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual baud-rate for this card's console port.\nIf auto-sensing is enabled, this will reveal the detected baud-rate.\nIf a fixed baud-rate is configured, this will match the configured baud-rate.",
        default=None,
        alias="actual-baud-rate",
    )
    auto_sensing_state: AutoSensingStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current state of the auto-sensing mechanism.\nOnly visible if auto-sensing is enabled for this port.\n\nCondition (when): ../baud-rate = 'auto-sensing'",
        default=AutoSensingStateEnum.SENSING,
        alias="auto-sensing-state",
    )
    local_switch: LocalSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines the global access to all card's console port. Access can be overridden per console port at the card level.",
        default=LocalSwitchEnum.USE_GLOBAL_SWITCH,
        alias="local-switch",
    )
    status: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current status of the console for this card.",
        default=EnableSwitchEnum.ENABLED,
    )


class Resources(YangBaseModel):
    """Resources of this particular card. Resource details will differ with each card type."""

    supported_carriers: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Names of the carriers that are supported by this card.\nTo be used upon super-channel creation.",
        min_length=1,
        max_length=32,
        default=None,
        alias="supported-carriers",
    )
    unassigned_carriers: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Names of the carriers that are not yet assigned to a super-channel in this card.",
        min_length=1,
        max_length=32,
        default=None,
        alias="unassigned-carriers",
    )
    supported_sub_components: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Names of sub-components present in this card, which can be addressed for certain operations like restart.",
        min_length=1,
        max_length=32,
        default=None,
        alias="supported-sub-components",
    )
    internal_cell_switch_total_bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Total internal cell-switch bandwidth.",
        default=0,
        alias="internal-cell-switch-total-bandwidth",
    )
    internal_cell_switch_available_bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Available internal cell-switch bandwidth.",
        default=0,
        alias="internal-cell-switch-available-bandwidth",
    )
    paired_slot_total_bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Total supported bandwidth for the paired slot connection. This is applicable only for card models that support paired mode.",
        default=0,
        alias="paired-slot-total-bandwidth",
    )
    paired_slot_available_bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Available bandwidth for the paired slot connection. This is applicable only for card models that support paired mode.",
        default=0,
        alias="paired-slot-available-bandwidth",
    )


class DirectionEnum_1(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * transmit
      * receive
      * transmit-and-receive
    """

    TRANSMIT = "transmit"
    RECEIVE = "receive"
    TRANSMIT_AND_RECEIVE = "transmit-and-receive"


class ConfigurationImpactEnum(str, Enum):
    """Enumeration for ConfigurationImpactEnum

    Values:
      * no-change
      * no-reacquire
      * reacquire
      * full-config-pll-change
      * full-config-no-pll-change
    """

    NO_CHANGE = "no-change"
    NO_REACQUIRE = "no-reacquire"
    REACQUIRE = "reacquire"
    FULL_CONFIG_PLL_CHANGE = "full-config-pll-change"
    FULL_CONFIG_NO_PLL_CHANGE = "full-config-no-pll-change"


class ServiceImpactEnum(str, Enum):
    """Enumeration for ServiceImpactEnum

    Values:
      * service-affecting
      * non-service-affecting
    """

    SERVICE_AFFECTING = "service-affecting"
    NON_SERVICE_AFFECTING = "non-service-affecting"


class SupportedAdvancedParameterItem(YangBaseModel):
    """A set of all optical carrier advanced parameters discovered from the equipment."""

    name: str = Field(
        json_schema_extra={"is_config": False},
        description="The name of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A human readable description of this advanced parameter.",
        min_length=0,
        max_length=256,
        default=None,
    )
    type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the data type of the advanced parameter.",
        min_length=0,
        max_length=255,
        default=None,
    )
    supported_values: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This list indicates the possible values that this parameter can take as input. It is a list of ranges.\n   E.g.'1-4, 10-14' indicating two ranges from 1 to 4 and 10 to 14. Or it could be a list of discrete\n   numbers like '10, 20, 30, 40'. Spaces are optional.",
        min_length=0,
        max_length=256,
        default=None,
        alias="supported-values",
    )
    direction: DirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Advanced parameter is applicable to the specified direction.",
        default=None,
    )
    multiplicity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies number of values user need to enter for this advanced parameter.\n   Same range or allowed-values will apply for each entry.",
        ge=0,
        default=None,
    )
    configuration_impact: ConfigurationImpactEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies the configuration steps to apply the change.",
        default=None,
        alias="configuration-impact",
    )
    service_impact: ServiceImpactEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies if applying this parameter change causes service impact. If it is service impacting, user must perform admin lock/maintenance/ToDO operation.",
        default=None,
        alias="service-impact",
    )


class Capabilities(YangBaseModel):
    """Generic card capabilities. Capabilities details will differ with each card type."""

    supported_advanced_parameter: RestconfList[SupportedAdvancedParameterItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="A set of all optical carrier advanced parameters discovered from the equipment.",
        default=None,
        alias="supported-advanced-parameter",
    )


class CardItem(YangBaseModel):
    """Card base object.This object has parameters that are common to all existing card types (controller, fan, etc)."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Card identifier.", min_length=1, max_length=64
    )
    required_type: str = Field(
        json_schema_extra={"is_config": True}, description="Required card type.", alias="required-type"
    )
    required_subtype: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The subtype of the card",
        min_length=0,
        max_length=32,
        default=None,
        alias="required-subtype",
    )
    card_mode: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured card-mode, identifies specific card functionality.",
        min_length=0,
        max_length=20,
        default=None,
        alias="card-mode",
    )
    category: CategoryEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Card category.", default=None
    )
    chassis_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Chassis where this card is located.",
        min_length=1,
        max_length=64,
        alias="chassis-name",
    )
    slot_name: str = Field(
        json_schema_extra={"is_config": True}, description="Slot where this card is located.", alias="slot-name"
    )
    subslot_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Subslot where this card is located, e.g. 1-2.3 (slot 2, subslot 3).\n'subslot-name' can only be set on (sub)card creation.",
        default=None,
        alias="subslot-name",
    )
    max_power_draw: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum power draw for this card.",
        default=None,
        alias="max-power-draw",
    )
    power_profile: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User configured power draw for this card.",
        min_length=0,
        max_length=16,
        default=None,
        alias="power-profile",
    )
    last_reboot_reason: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reason why the last reboot was done.",
        default=None,
        alias="last-reboot-reason",
    )
    last_reboot_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of the last reboot event of a card.",
        default=None,
        alias="last-reboot-time",
    )
    parent_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Name of the parent card, only applicable for subcard(s).",
            min_length=1,
            max_length=64,
            default=None,
            alias="parent-card",
        )
    )
    subcard_list: (
        RestconfList[Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))]] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="List of sub-cards associated with this card.\nOnly applicable for carrier cards.",
        min_length=1,
        max_length=64,
        default=None,
        alias="subcard-list",
    )
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore.",
            min_length=0,
            max_length=256,
            default=None,
            alias="alias-name",
        )
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    slot: RestconfList[SlotItem] | None = Field(
        json_schema_extra={"is_config": False}, description="Slot equipment holder details.", default=None
    )
    controller_card: ControllerCard | None = Field(
        json_schema_extra={"is_config": True},
        description="Container of parameters related with controller cards.",
        default=None,
        alias="controller-card",
    )
    property: RestconfList[PropertyItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Type specific property, auto instanciated by the system, but configurable by the user.",
        default=None,
    )
    port: RestconfList[PortItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Generic card port.", default=None
    )
    console: Console | None = Field(
        json_schema_extra={"is_config": True},
        description="Parameters associated with this card's serial console port.",
        default=None,
    )
    resources: Resources | None = Field(
        json_schema_extra={"is_config": False},
        description="Resources of this particular card. Resource details will differ with each card type.",
        default=None,
    )
    capabilities: Capabilities | None = Field(
        json_schema_extra={"is_config": False},
        description="Generic card capabilities. Capabilities details will differ with each card type.",
        default=None,
    )


class StatusEnum_1(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * not-available: LED status not available.
      * off: LED is turned off and has no color.
      * yellow: LED is turned on with yellow color.
      * flashing-yellow: LED is flashing, alternating between off and yellow color.
      * green: LED is turned on with green color.
      * flashing-green: LED is flashing, alternating between off and green color.
      * red: LED is turned on with red color.
      * flashing-red: LED is flashing, alternating between off and red color.
      * cycling-with-off: LED is cycling between all supported colors, including off state.
      * cycling: LED is cycling between all supported colors (excluding off state) - used for lamp test.
      * amber: LED is turned on with amber color.
      * flashing-amber: LED is flashing, alternating between off and amber color.
    """

    NOT_AVAILABLE = "not-available"
    OFF = "off"
    YELLOW = "yellow"
    FLASHING_YELLOW = "flashing-yellow"
    GREEN = "green"
    FLASHING_GREEN = "flashing-green"
    RED = "red"
    FLASHING_RED = "flashing-red"
    CYCLING_WITH_OFF = "cycling-with-off"
    CYCLING = "cycling"
    AMBER = "amber"
    FLASHING_AMBER = "flashing-amber"


class LedItem(YangBaseModel):
    """Representation of a LED in a FRU.
    Object exists even if FRU is not physically present.
    """

    location: str = Field(
        json_schema_extra={"is_config": False},
        description="AID of equipment location of the LED (may be a chassis, card or a port AID).",
        min_length=1,
        max_length=32,
    )
    name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the LED within the FRU.",
        min_length=1,
        max_length=16,
    )
    status: StatusEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Current color status of the LED.",
        default=StatusEnum_1.NOT_AVAILABLE,
    )


class Leds(YangBaseModel):
    """Container of all equipment LEDs."""

    led: RestconfList[LedItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Representation of a LED in a FRU.\nObject exists even if FRU is not physically present.",
        default=None,
    )


class ChassisAssignmentModeEnum(str, Enum):
    """Enumeration for ChassisAssignmentModeEnum

    Values:
      * manual: Manual mode where sub-chassis ID is assigned either via user configuration or ZTP mechanism.
    """

    MANUAL = "manual"


class CommEthLocationEnum(str, Enum):
    """Enumeration for CommEthLocationEnum

    Values:
      * prefer-dcn-in-front: The DCN port is at the front of the chassis.  Depending on the chassis type, may imply that the CRAFT port is at the back.
      * prefer-dcn-in-back: The DCN port is at the back of the chassis.  If the chassis supports this option, implies that the CRAFT port is at the front.
      * eth5-as-craft: ETH5 is configured as CRAFT in G34c.
      * eth5-as-dcn: ETH5 is configured as DCN-2 in G34c.
    """

    PREFER_DCN_IN_FRONT = "prefer-dcn-in-front"
    PREFER_DCN_IN_BACK = "prefer-dcn-in-back"
    ETH5_AS_CRAFT = "eth5-as-craft"
    ETH5_AS_DCN = "eth5-as-dcn"


class SerdesTemplateEntryItem(YangBaseModel):
    """An individual entry to the serdes-template, composed
    of a serdes parameter name and associated value.
    """

    name: str = Field(
        json_schema_extra={"is_config": True}, description="Name of the serdes parameter.", min_length=0, max_length=256
    )
    value: str = Field(
        json_schema_extra={"is_config": True},
        description="Value of the serdes parameter.",
        min_length=0,
        max_length=256,
    )


class SerdesTemplateItem(YangBaseModel):
    """A template that allows to auto-configure serdes for 3rd party TOMs.
    serdes-templates are created by the user per tom-part-number and apply to all line cards that support serdes;
    when a TOM is plugged-in with that part-number, the template will be automatically applied.
    User can narrow down when the template is applied by providing both a list of applicable card-types, and ports,
    but all card-types and ports are considered by default.
    Manual configuration of serdes can still be done separately, and will be kept even if it deviates from the template.
    Switching a TOM with another TOM with a different part-number will imply a reset of the
    serdes configuration, and re-apply of the new template (if existing).
    Application of serdes-templates is dependent on the use-serdes-templates flag being set to 'true'.
    User can force the re-application of a serdes-template by using the 'apply-template' command.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name of the serdes-template.",
        min_length=1,
        max_length=64,
    )
    tom_part_number: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The TOM part-number to which this template applies.\nIf not provided, uses the same value as the template name.",
        min_length=1,
        max_length=16,
        default=None,
        alias="tom-part-number",
    )
    card_types_applicable: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="The list of card-types to which this template applies, or 'all' if all card-types are to be considered (default).",
        min_length=1,
        max_length=16,
        default=None,
        alias="card-types-applicable",
    )
    ports_applicable: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="The list of ports to which this template is applicable, or 'all' if all ports are to be considered (default).",
        min_length=0,
        max_length=16,
        default=None,
        alias="ports-applicable",
    )
    serdes_template_entry: RestconfList[SerdesTemplateEntryItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="An individual entry to the serdes-template, composed\nof a serdes parameter name and associated value.",
        default=None,
        alias="serdes-template-entry",
    )


class EquipmentTemplates(YangBaseModel):
    """Container for templates associated with equipment."""

    use_serdes_templates: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether serdes-templates are globally enabled or not. See description of 'serdes-template' list for details.\nOn enabling: templates are not automatically applies; they'll be applied from that moment onward.\nOn disabling: no impact; existing serdes configuration is kept on all TOMs, independently on whether they were applied via template or manually.",
        default=False,
        alias="use-serdes-templates",
    )
    serdes_template: RestconfList[SerdesTemplateItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A template that allows to auto-configure serdes for 3rd party TOMs.\nserdes-templates are created by the user per tom-part-number and apply to all line cards that support serdes;\nwhen a TOM is plugged-in with that part-number, the template will be automatically applied.\nUser can narrow down when the template is applied by providing both a list of applicable card-types, and ports,\nbut all card-types and ports are considered by default.\nManual configuration of serdes can still be done separately, and will be kept even if it deviates from the template.\nSwitching a TOM with another TOM with a different part-number will imply a reset of the\nserdes configuration, and re-apply of the new template (if existing).\nApplication of serdes-templates is dependent on the use-serdes-templates flag being set to 'true'.\nUser can force the re-application of a serdes-template by using the 'apply-template' command.",
        default=None,
        alias="serdes-template",
    )


class GlobalPowerProfileItem(YangBaseModel):
    """Allows configuration of the power profile used for all instances of a given
    card type, if that card supports power-profiles.
    Alternatively, the global-power-profile can be disabled, which means each card
    instance will have its own power profile individually configurable.
    Changing the global-power-profile will have impact on both existing card instances,
    as well as newly created card instances.
    Power profiles are a way to categorize the power estimation for the system.
    """

    card_type: str = Field(
        json_schema_extra={"is_config": True},
        description="The card-type associated with this global-power-profile configuration.",
        alias="card-type",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether this global-power-profile is enabled.\nIf enabled, both existing and newly created instances of card-type will have its power-profile set to\nthe selected global value.\nIf disabled, each card instance has the ability to configure its own power-profile.\nThe enabling of the global profile is only allowed if all chassis have enough available-power.",
        default=False,
    )
    profile_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Globally used profile-name for this card-type, if enabled.\nNeeds to match an existing supported-power-profile name for this card.\nAttribute has no impact if global profile is not enabled.\nThe changing of the global profile is only allowed if all chassis have enough available-power.",
        min_length=0,
        max_length=16,
        default=None,
        alias="profile-name",
    )


class EquipmentPolicies(YangBaseModel):
    """Container with all existing equipment policies."""

    tom_auto_migration: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables automatic update of tom subtype based on present equipment.\nThis update may have direct impact on existing configurations.\nNote1: this has impact on tom subtype migration, but not for tom type migration (e.g. no update between QSFPDD and QSFP28).\nNote2: Besides this flag, supported-port capabilities can define it's own behavior if a TOM should be auto migrated. For example,\n       for ILAx sposc1 port specifically, TOM auto migration is disabled.",
        default=EnableSwitchEnum.ENABLED,
        alias="tom-auto-migration",
    )
    auto_assigned_directions: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables automatic direction assignment when a card that supports directions is provisioned.",
        default=EnableSwitchEnum.ENABLED,
        alias="auto-assigned-directions",
    )
    auto_assigned_degrees: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables automatic degree assignment when a card that supports degree(s) is provisioned.",
        default=EnableSwitchEnum.DISABLED,
        alias="auto-assigned-degrees",
    )
    cable_id_control: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="It enables or disables the cable ID verification. In SLTE (l0-mode-op = SLTE) mode, it is automatically enabled. It can be enabled or disabled by the user (default is disabled).",
        default=EnableSwitchEnum.DISABLED,
        alias="cable-id-control",
    )
    chassis_assignment_mode: ChassisAssignmentModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Determine if the chassis id assignment is done manually or automatically.",
        default=ChassisAssignmentModeEnum.MANUAL,
        alias="chassis-assignment-mode",
    )
    comm_eth_location: CommEthLocationEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Physical location of the communication ethernet ports.",
        default=CommEthLocationEnum.PREFER_DCN_IN_FRONT,
        alias="comm-eth-location",
    )
    equipment_templates: EquipmentTemplates | None = Field(
        json_schema_extra={"is_config": True},
        description="Container for templates associated with equipment.",
        default=None,
        alias="equipment-templates",
    )
    global_power_profile: RestconfList[GlobalPowerProfileItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows configuration of the power profile used for all instances of a given\ncard type, if that card supports power-profiles.\nAlternatively, the global-power-profile can be disabled, which means each card\ninstance will have its own power profile individually configurable.\nChanging the global-power-profile will have impact on both existing card instances,\nas well as newly created card instances.\nPower profiles are a way to categorize the power estimation for the system.",
        default=None,
        alias="global-power-profile",
    )


class UnprovisionedInventoryItem(YangBaseModel):
    """List of detected inventory but not yet accepted by the Node Controller in Multi-Chassis configuration."""

    chassis_serial_number: str = Field(
        json_schema_extra={"is_config": False},
        description="The residing chassis serial number.",
        min_length=0,
        max_length=16,
        alias="chassis-serial-number",
    )
    slot_name: str = Field(
        json_schema_extra={"is_config": False},
        description="The residing slot name for the equipment. If the equipment is the chassis, the slot-name is empty",
        min_length=0,
        max_length=16,
        alias="slot-name",
    )
    hardware_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Hardware version of this FRU.",
        default=None,
        alias="hardware-version",
    )
    actual_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="FRU type of actual equipment.",
        default=None,
        alias="actual-type",
    )
    actual_subtype: str | None = Field(
        json_schema_extra={"is_config": False},
        description="FRU subtype of actual equipment - only available if applicable.",
        default=None,
        alias="actual-subtype",
    )
    sw_support_revision: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Software revision currently installed.",
        ge=0,
        default=0,
        alias="sw-support-revision",
    )
    PON: str | None = Field(
        json_schema_extra={"is_config": False}, description="Current PON of the equipment.", default=None
    )
    serial_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Serial number of the equipment.",
        min_length=1,
        max_length=16,
        default=None,
        alias="serial-number",
    )
    clei: str | None = Field(
        json_schema_extra={"is_config": False}, description="Common Language Equipment Identifier.", default=None
    )
    vendor: str | None = Field(
        json_schema_extra={"is_config": False}, description="Vendor of this equipment.", default=None
    )
    part_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Part number for this equipment.",
        default=None,
        alias="part-number",
    )
    manufacture_date: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Manufacture Date in a date-time format (YYYY-MM-DDThh:mm:ssZ) or 'NA' if not available.",
        default=None,
        alias="manufacture-date",
    )
    detection_timestamp: (
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
        description="Timestamp with the last time the unprovisioned equipment was detected by the Node Controller.",
        default=None,
        alias="detection-timestamp",
    )


class Equipment(YangBaseModel):
    """Container for all equipment related resources."""

    chassis: RestconfList[ChassisItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Chassis configuration and state.", default=None
    )
    card: RestconfList[CardItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Card base object.This object has parameters that are common to all existing card types (controller, fan, etc).",
        default=None,
    )
    leds: Leds | None = Field(
        json_schema_extra={"is_config": False}, description="Container of all equipment LEDs.", default=None
    )
    equipment_policies: EquipmentPolicies | None = Field(
        json_schema_extra={"is_config": True},
        description="Container with all existing equipment policies.",
        default=None,
        alias="equipment-policies",
    )
    unprovisioned_inventory: RestconfList[UnprovisionedInventoryItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of detected inventory but not yet accepted by the Node Controller in Multi-Chassis configuration.",
        default=None,
        alias="unprovisioned-inventory",
    )


class ManagedByEnum(str, Enum):
    """Enumeration for ManagedByEnum

    Values:
      * system
      * user
    """

    SYSTEM = "system"
    USER = "user"


class OscCompatibilityEnum(str, Enum):
    """Enumeration for OscCompatibilityEnum

    Values:
      * osc-g30: General GX OSC compatibility.
      * osc-7100: 7100 compatibility.
    """

    OSC_G30 = "osc-g30"
    OSC_7100 = "osc-7100"


class FiberTypeEnum(str, Enum):
    """Enumeration for FiberTypeEnum

    Values:
      * not-applicable: Not Applicable
      * auto: Automatic fiber-type: only for OTDR
      * SSMF: Standard Single Mode Fiber
      * LEAF: Large Effective Area Fiber
      * TWRS: True Wave Reduced Slope
      * TWC: True Wave Classic
      * AllWave: AllWave
      * DSF: Dispersion Shifted Fiber
      * LS: LS Fiber
      * PureSilica: Pure Silica
      * TWReach: True Wave Reach
      * VistaCor: VistaCor
      * Teralight: Teralight
      * DrakaLL: Draka Long Line
      * TWPlus: True Wave Plus
      * TWMinus: True Wave Minus
      * PSLC: Pure Silice Large Core
      * ULL: Ultra Low Loss fiber
      * SMF-ULL: SMF Ultra Low Loss fiber
      * not-configured: Fiber-type is not known, or not configured.
    """

    NOT_APPLICABLE = "not-applicable"
    AUTO = "auto"
    SSMF = "SSMF"
    LEAF = "LEAF"
    TWRS = "TWRS"
    TWC = "TWC"
    ALLWAVE = "AllWave"
    DSF = "DSF"
    LS = "LS"
    PURESILICA = "PureSilica"
    TWREACH = "TWReach"
    VISTACOR = "VistaCor"
    TERALIGHT = "Teralight"
    DRAKALL = "DrakaLL"
    TWPLUS = "TWPlus"
    TWMINUS = "TWMinus"
    PSLC = "PSLC"
    ULL = "ULL"
    SMF_ULL = "SMF-ULL"
    NOT_CONFIGURED = "not-configured"


class SpanLossReferenceEnum(str, Enum):
    """Enumeration for SpanLossReferenceEnum

    Values:
      * measured: Span Loss is measured.
      * configured: Span Loss is explicitly configured.
    """

    MEASURED = "measured"
    CONFIGURED = "configured"


class TargetPowerSettingEnum(str, Enum):
    """Enumeration for TargetPowerSettingEnum

    Values:
      * manual: Users configures target values for oxcon.
      * auto: System calculates target values for oxcon.
    """

    MANUAL = "manual"
    AUTO = "auto"


class LaserSafetyModeEnum(str, Enum):
    """Enumeration for LaserSafetyModeEnum

    Values:
      * OPLM: Optical Power Limited Mode (OPLM)
      * APSD: Automatic Power Shut Down (APSD)
    """

    OPLM = "OPLM"
    APSD = "APSD"


class LoadingPolicyEnum(str, Enum):
    """Enumeration for LoadingPolicyEnum

    Values:
      * slte-policy-1: slte-policy-1 is a conservative loading policy. Loading parameters for this policy are managed internally.
      * slte-policy-2: slte-policy-2 is a more aggressive loading policy. Loading parameters for this policy are managed internally.
    """

    SLTE_POLICY_1 = "slte-policy-1"
    SLTE_POLICY_2 = "slte-policy-2"


class TtiStyleEnum(str, Enum):
    """Enumeration for TtiStyleEnum

    Values:
      * ITU-T-G709: TTI is split into SAPI, DAPI and OPER bytes.
      * proprietary: TTI is a single 64 byte string.
    """

    ITU_T_G709 = "ITU-T-G709"
    PROPRIETARY = "proprietary"


class OtsDiagnostics(YangBaseModel):
    """OTS diagnostics"""

    tti_style: TtiStyleEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="TTI Style is set by application based on l0 mode operation, not configurable by user.",
        default=TtiStyleEnum.ITU_T_G709,
        alias="tti-style",
    )
    nmoper_alarm_reporting: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates if a Neighbor Mismatch TTI Operator-Specific field based (NMOPER) alarm is reported or not.",
        default=EnableSwitchEnum.DISABLED,
        alias="nmoper-alarm-reporting",
    )
    expected_operator: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected operator specific bytes.",
        default="",
        alias="expected-operator",
    )
    tx_operator: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Filled by the System. Cannot be written by the user.",
        default=None,
        alias="tx-operator",
    )
    rx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received operation specific bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.",
        default=None,
        alias="rx-operator",
    )
    tti_port_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="port-id in OTS tti is the AID of the port but limited to 32 printable characters.\n\nCondition (when): ../tti-style = 'proprietary'",
        min_length=0,
        max_length=32,
        default=None,
        alias="tti-port-id",
    )


class OtsItem(YangBaseModel):
    """OTS: Optical Transmission Section facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    osc_compatibility: OscCompatibilityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Informs the system about the connected 7100 compatibility required.",
        default=OscCompatibilityEnum.OSC_G30,
        alias="osc-compatibility",
    )
    enable_dcn_interworking: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls whether DCN interworking with 7100 is required.\n\nCondition (when): ../osc-compatibility = 'osc-7100'",
        default=False,
        alias="enable-dcn-interworking",
    )
    osc_less_support: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="'true' if OTS port supports OSC-less operation.",
        default=True,
        alias="osc-less-support",
    )
    osc_less: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="OSC-less mode is required to provide interworking with systems with no compatible OSC\nor spans with losses not compatible with the OSC budget.",
        default=EnableSwitchEnum.DISABLED,
        alias="osc-less",
    )
    fiber_type_rx: FiberTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Fiber Type (OTS receiver) allows PCL to know the 'intercept' and 'slope'.",
        default=FiberTypeEnum.SSMF,
        alias="fiber-type-rx",
    )
    fiber_type_tx: FiberTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Fiber Type (OTS transmitter) allows PCL to know the 'intercept' and 'slope'.",
        default=FiberTypeEnum.SSMF,
        alias="fiber-type-tx",
    )
    fiber_length_tx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmitting Fiber Length",
        default="auto",
        alias="fiber-length-tx",
    )
    fiber_length_rx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Receiving Fiber Length.",
        default="auto",
        alias="fiber-length-rx",
    )
    fiber_length_derived_rx: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Estimated fiber length, calculated from the configured fiber-type\nand span loss measured via OSC powers.",
        default=None,
        alias="fiber-length-derived-rx",
    )
    fiber_length_derived_tx: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Estimated fiber length, calculated from the configured fiber-type\nand span loss measured via OSC powers.",
        default=None,
        alias="fiber-length-derived-tx",
    )
    fiber_spectral_attenuation_tilt_tx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Since different transmission bands are supported, it is simpler\nto enter this parameter independent of the transmission bandwidth,\nhence per Terahertz.",
        default="unspecified",
        alias="fiber-spectral-attenuation-tilt-tx",
    )
    fiber_spectral_attenuation_tilt_rx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Since different transmission bands are supported, it is simpler\nto enter this parameter independent of the transmission bandwidth,\nhence per Terahertz.",
        default="unspecified",
        alias="fiber-spectral-attenuation-tilt-rx",
    )
    raman_coefficient_tx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Raman coefficient per Terahertz.\nSince different transmission bands are supported, it is simpler to enter this parameter\nindependent of the transmission bandwidth, hence per Terahertz.\nRequired for tilt control (if tilt-control-mode = auto).\nConfiguration mode depends on tilt-control-mode.",
        default="not-applicable",
        alias="raman-coefficient-tx",
    )
    raman_coefficient_rx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Raman coefficient per Terahertz.\nSince different transmission bands are supported, it is simpler to enter this parameter\nindependent of the transmission bandwidth, hence per Terahertz.\nRequired for tilt control (if tilt-control-mode = auto).\nConfiguration mode depends on tilt-control-mode.",
        default="not-applicable",
        alias="raman-coefficient-rx",
    )
    span_loss_reference: SpanLossReferenceEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Configures span-loss source intended to be used by the system to calculate automatic target powers.",
        default=SpanLossReferenceEnum.MEASURED,
        alias="span-loss-reference",
    )
    span_loss_alarm_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Configures the threshold for the SPAN-LOSS-HIGH alarm.\n\nCondition (when): ../osc-less = 'disabled'",
        ge=0,
        default=99,
        alias="span-loss-alarm-threshold",
    )
    span_loss_transmit: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Fiber loss on the transmitter side (OTS-so).\nThis is only the loss of the fiber.\nAdditional loss such as coming from patch panel is entered via the external-attenuation parameters.",
        ge=0,
        default=None,
        alias="span-loss-transmit",
    )
    span_loss_receive: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Fiber loss on the receiver side. (OTS-sk)\nThis is only the loss of the fiber.",
        ge=0,
        default=None,
        alias="span-loss-receive",
    )
    span_loss_derived_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Measured span loss (based on OSC).\nThe value includes the losses external to the fiber.\n\nCondition (when): ../osc-less = 'disabled'",
        ge=0,
        le=99,
        default=0,
        alias="span-loss-derived-rx",
    )
    span_loss_derived_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Measured span loss transmit.\n\nCondition (when): ../osc-less = 'disabled'",
        ge=0,
        le=99,
        default=0,
        alias="span-loss-derived-tx",
    )
    external_attenuation_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="External padding attenuation at transmitting direction.\nRequired for tilt control.",
        ge=0,
        le=30,
        default=None,
        alias="external-attenuation-tx",
    )
    external_attenuation_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="External padding attenuation at receiving direction,\nfor example, a patch-panel.",
        ge=0,
        le=30,
        default=None,
        alias="external-attenuation-rx",
    )
    span_loss_aging_margin_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Used by system for defining value of span loss high alarm.",
        ge=0,
        le=10,
        default=1.0,
        alias="span-loss-aging-margin-rx",
    )
    target_power_setting: TargetPowerSettingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows automatic configuration of target values for oxcon.",
        default=TargetPowerSettingEnum.AUTO,
        alias="target-power-setting",
    )
    laser_safety_mode: LaserSafetyModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Laser Safety Mode of the OTS instance.",
        default=LaserSafetyModeEnum.OPLM,
        alias="laser-safety-mode",
    )
    loading_policy: LoadingPolicyEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This is to indicate which policy to be used for a degree internally by Loading Manager for filtering loading requests.",
        default=LoadingPolicyEnum.SLTE_POLICY_1,
        alias="loading-policy",
    )
    ots_diagnostics: OtsDiagnostics | None = Field(
        json_schema_extra={"is_config": True}, description="OTS diagnostics", default=None, alias="ots-diagnostics"
    )


class OtsRItem(YangBaseModel):
    """OTS: Optical Transmission Section facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    required_fiber_type_rx: FiberTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The required Fiber Type on the DWDM Line, with reference for the Rx fiber.\nOnly of relevance if control-mode = auto.\nAnd: when there is no fiber-connection.",
        default=FiberTypeEnum.SSMF,
        alias="required-fiber-type-rx",
    )
    configured_fiber_type_rx: FiberTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The configured fiber-type-rx on EDFA.\nIf control-mode = auto, it is simply the rx.required-fiber-type.",
        default=None,
        alias="configured-fiber-type-rx",
    )
    fiber_length_rx: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Receiving Fiber Length",
        default="unspecified",
        alias="fiber-length-rx",
    )
    configured_fiber_length_rx: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="The configured (receiving) fiber-length-rx on the amplifier.",
        default=None,
        alias="configured-fiber-length-rx",
    )
    span_loss_receive: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The Span Loss at the receiving dwdm-line.",
        ge=0,
        le=99,
        default=99,
        alias="span-loss-receive",
    )
    span_loss_at_amplifier: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The Span Loss detected at amplifier, when there is a fiber-connection from/ RPB to the amplifier.",
        ge=0,
        le=99,
        default=99,
        alias="span-loss-at-amplifier",
    )
    external_attenuation_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Loss between Patch panel and the Raman dwdm-line Rx.",
        ge=0,
        le=30,
        default=None,
        alias="external-attenuation-rx",
    )
    delta_pointloss: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Delta Pointloss (Rx)\nAdditional attenuation that can be determined after turning up pumps.\nThis is the fiber contribution for the pointloss: to be fine tuned in the field.\nThis additional optical attenuation may be due to e.g. bad splice at dwdm-line Rx, higher att. than 0.1 dB.",
        default="not-applicable",
        alias="delta-pointloss",
    )
    power_actual_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical power received, where applicable.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-rx",
    )
    connected_reference: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the degree the Raman is connected to.\nIn ILA node-type(s), the direction the Raman is connected to (1 means direction 1-2, 2 means 2-1).",
        ge=0,
        default=0,
        alias="connected-reference",
    )


class TypeOfOscMonitoringModeEnum(str, Enum):
    """Enumeration for TypeOfOscMonitoringModeEnum

    Values:
      * intrusive: Intrusive monitoring; OSC TTP
      * non-intrusive: Non-intrusive monitoring; OSC CTP
    """

    INTRUSIVE = "intrusive"
    NON_INTRUSIVE = "non-intrusive"


class OscModeEnum(str, Enum):
    """Enumeration for OscModeEnum

    Values:
      * OC3: G30 Series OC-3 OSC (155Mbit/s datarate)
      * 1GE: G30 Series 1GE OSC (1.22Gbit/s datarate)
    """

    OC3 = "OC3"
    _1GE = "1GE"


class OscControlEnum(str, Enum):
    """Enumeration for OscControlEnum

    Values:
      * auto: Automatic OSC power control
      * manual: Manual OSC power control
    """

    AUTO = "auto"
    MANUAL = "manual"


class OscItem(YangBaseModel):
    """Represents the Optical Supervision Channel (OSC) facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    monitoring_mode: TypeOfOscMonitoringModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The monitoring mode on the OSC TP.",
        default=TypeOfOscMonitoringModeEnum.INTRUSIVE,
        alias="monitoring-mode",
    )
    oscc_support: bool | None = Field(
        json_schema_extra={"is_config": False}, description="OSC Control support.", default=True, alias="oscc-support"
    )
    osc_mode: OscModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="OC-3 OSC format.\n\nCondition (when): ../monitoring-mode='intrusive'",
        default=OscModeEnum.OC3,
        alias="osc-mode",
    )
    osc_wavelength: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the wavelength of the OSC channel transmitted\n\nCondition (when): ../monitoring-mode='intrusive'",
        le=1700.0,
        default=0.0,
        alias="osc-wavelength",
    )
    osc_control: OscControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="OSC control configuration.",
        default=OscControlEnum.AUTO,
        alias="osc-control",
    )
    target_output_power: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmit OSC power.",
        default="na",
        alias="target-output-power",
    )
    tx_power_adjustment: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Adjustment to the automatically calculated Tx power target.",
        ge=-6,
        le=6,
        default=0,
        alias="tx-power-adjustment",
    )
    voa_attenuation_target_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Target Rx VOA value in case of manual control mode.",
        ge=0,
        le=30,
        default=10,
        alias="voa-attenuation-target-rx",
    )
    voa_attenuation_actual_rx: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Reports the actual VOA value as configured.\nSystem returns not-applicable when card or SFP is not actually equipped.\n\nCondition (when): ../monitoring-mode='intrusive'",
        default=None,
        alias="voa-attenuation-actual-rx",
    )
    power_actual_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Received, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-rx",
    )
    power_actual_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Transmitted, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-tx",
    )


class RoleEnum(str, Enum):
    """Enumeration for RoleEnum

    Values:
      * general-purpose: Indicates the underlying (L0) port may be used for express connections, or to add/drop traffic.
      * tributary: Single Wavelength. Indicates the underlying (L0) port is connected to a transponder, or ellegible to be connected to a transponder.
      * multi-carrier: Multiple Wavlength. Indicates the underlying (L0) port is connected to several carriers, either directly or indirectly (using a coupler/ splitter or AWG).
      * ase-input: ASE Input role for RD port. Note: ASE Input option is only available on specific RD port(s), in SLTE l0-mode-op
    """

    GENERAL_PURPOSE = "general-purpose"
    TRIBUTARY = "tributary"
    MULTI_CARRIER = "multi-carrier"
    ASE_INPUT = "ase-input"


class OpsItem(YangBaseModel):
    """OPS: Optical Physical Section facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    role: RoleEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows the user to configure the port role.",
        default=RoleEnum.GENERAL_PURPOSE,
    )
    supported_roles: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The SYSTEM exposes what configurations are possible, for the purpose\nof managers being able to offer the appropriate options for the configuration of OPS role.\nBits indicate the role possibilities:\n- this is fully dependent on card (and sometimes on card-mode), refer to the 'portsdata' definition.",
        default=None,
        alias="supported-roles",
    )
    locally_reserved: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Exposes to the user whether the particular port (e.g. of an RD ADE port) is reserved for ASE Idler traffic.\n\nCondition (when): /ne/l0-mode-op = 'slte'",
        default=False,
        alias="locally-reserved",
    )


class TypeOfOmsMonitoringModeEnum(str, Enum):
    """Enumeration for TypeOfOmsMonitoringModeEnum

    Values:
      * intrusive: Intrusive monitoring (TTP)
      * not-monitored: OMS-nim functionality, but no OCM (e.g. no DGE) required
      * non-intrusive: Non-intrusive, with optional monitoring (CTP)
      * dge-fixed-attenuation: Fixed attenuation, due to connected interstage device
      * ila-with-equalization: Full equalization (DGE) operation.
      * terminal: FOADM ILAx OADM node-type Operation.
      * integrated-equalization: Full equalization with integrated DGE
    """

    INTRUSIVE = "intrusive"
    NOT_MONITORED = "not-monitored"
    NON_INTRUSIVE = "non-intrusive"
    DGE_FIXED_ATTENUATION = "dge-fixed-attenuation"
    ILA_WITH_EQUALIZATION = "ila-with-equalization"
    TERMINAL = "terminal"
    INTEGRATED_EQUALIZATION = "integrated-equalization"


class BandsSupportedLinkEnum(str, Enum):
    """Enumeration for BandsSupportedLinkEnum

    Values:
      * not-applicable: Not applicable for non DWDM-line OMS.
      * standardC-band-only: Only standard C-band supported.
      * standardC-and-superC-band: Super-C and standard C-band supported.
      * standardL-band-only: Only standard L-band supported.
    """

    NOT_APPLICABLE = "not-applicable"
    STANDARDC_BAND_ONLY = "standardC-band-only"
    STANDARDC_AND_SUPERC_BAND = "standardC-and-superC-band"
    STANDARDL_BAND_ONLY = "standardL-band-only"


class TransmissionBandEnum(str, Enum):
    """Enumeration for TransmissionBandEnum

    Values:
      * not-applicable: Transmission band not applicable.
      * standardC-band: Standard C-band (4.85 THz).
      * superC-band: SuperC-band (6.1 THz).
      * standardL-band: Standard L-band (4.85 THz).
      * standardC-standardL-band: Standard C or Standard L band.
    """

    NOT_APPLICABLE = "not-applicable"
    STANDARDC_BAND = "standardC-band"
    SUPERC_BAND = "superC-band"
    STANDARDL_BAND = "standardL-band"
    STANDARDC_STANDARDL_BAND = "standardC-standardL-band"


class GridTypeEnum(str, Enum):
    """Enumeration for GridTypeEnum

    Values:
      * fixed-50G-96ch: 50GHz fixed grid with 96 channels in C-band.
      * fixed-100G-48ch: 100GHz fixed grid with 48 channels in C-band.
      * fixed-75G-64ch: 75GHz fixed grid with 64 channels in C-band.
      * flexible: Flexible grid.
      * fixed-75G-64ch-oif: 75GHz fixed grid with 64 channels in C-band, OIF 400ZR standard grid.
      * fixed-50G-7100: 50GHz fixed grid with 88 channels in C-band.
      * fixed-150G-40ch: 150GHz fixed grid with 40 channels in C-band.
    """

    FIXED_50G_96CH = "fixed-50G-96ch"
    FIXED_100G_48CH = "fixed-100G-48ch"
    FIXED_75G_64CH = "fixed-75G-64ch"
    FLEXIBLE = "flexible"
    FIXED_75G_64CH_OIF = "fixed-75G-64ch-oif"
    FIXED_50G_7100 = "fixed-50G-7100"
    FIXED_150G_40CH = "fixed-150G-40ch"


class SupportedBandAndGridEnum(str, Enum):
    """Enumeration for SupportedBandAndGridEnum

    Values:
      * not-applicable: Not applicable.
      * flexible-c-band-only: Flexible C-band without fixed-grid characterization.
      * general-c-band: 4.85THz C-band/6.1THz SuperC-band, fixed or flexi-grid.
      * general-fixed-c-band: 4.85 THz 50GHz, 75GHz or 100GHz, C-band support.
      * general-l-band: 4.85THz L-band.
      * flexible-band: standardC-band or standardL-band.
    """

    NOT_APPLICABLE = "not-applicable"
    FLEXIBLE_C_BAND_ONLY = "flexible-c-band-only"
    GENERAL_C_BAND = "general-c-band"
    GENERAL_FIXED_C_BAND = "general-fixed-c-band"
    GENERAL_L_BAND = "general-l-band"
    FLEXIBLE_BAND = "flexible-band"


class AttControlModeEnum(str, Enum):
    """Enumeration for AttControlModeEnum

    Values:
      * not-applicable: Not applicable.
      * auto: Automatic attenuation control mode in which system will decide the attenuation value.
      * manual: Manual attenuation control mode in which target attenuation will be used.
    """

    NOT_APPLICABLE = "not-applicable"
    AUTO = "auto"
    MANUAL = "manual"


class OmsItem(YangBaseModel):
    """OMS: Optical Multiplex Section facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    monitoring_mode: TypeOfOmsMonitoringModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="OMS monitoring mode",
        default=TypeOfOmsMonitoringModeEnum.INTRUSIVE,
        alias="monitoring-mode",
    )
    wss_less: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="True if there is no WSS component in the Degree.",
        default=False,
        alias="wss-less",
    )
    assigned_degree: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Display degree number when card is added in modules-degree.",
        ge=0,
        default=0,
        alias="assigned-degree",
    )
    power_actual_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Received, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-rx",
    )
    power_actual_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Transmitted, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-tx",
    )
    bands_supported_link: BandsSupportedLinkEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The evaluated link capability, based on OSC information.",
        default=BandsSupportedLinkEnum.STANDARDC_BAND_ONLY,
        alias="bands-supported-link",
    )
    band_allowed: TransmissionBandEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The allowed band for Rx / Tx at this OMS facility.",
        default=None,
        alias="band-allowed",
    )
    band_actual: TransmissionBandEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual band negotiated at the link.",
        default=None,
        alias="band-actual",
    )
    band_target: TransmissionBandEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Derived band at ILA amplifier, or received band from OSC.",
        default=TransmissionBandEnum.NOT_APPLICABLE,
        alias="band-target",
    )
    configured_spectrum: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of lower and upper frequency values of the usable spectrum configured for SLTE deployments.",
        default=None,
        alias="configured-spectrum",
    )
    lower_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The lowest frequency an mc/ nmc can be using.\nDefault is 191.3 THz (standardC-band lowest frequency).",
        ge=0,
        default=191300000,
        alias="lower-frequency",
    )
    upper_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The highest frequency an mc/ nmc can be using.\nDefault is 196.15 THz (standardC-band highest frequency).",
        ge=0,
        default=196150000,
        alias="upper-frequency",
    )
    target_output_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="OMS Target Output Power\n\nCondition (when): /ne/l0-mode-op ='slte'",
        ge=-55.0,
        le=55.0,
        default=5,
        alias="target-output-power",
    )
    grid_mode: GridTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates Grid type of the OMS layer.\n- flexible: allows user to create/ delete of MC with different widths;\n- otherwise, allows user to create MC with specific width (and delete accordingly).\n\nCondition (when): ../monitoring-mode = 'intrusive' or ../monitoring-mode = 'terminal'",
        default=GridTypeEnum.FLEXIBLE,
        alias="grid-mode",
    )
    grid_mode_support: SupportedBandAndGridEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Which C-band is supported, for the purpose of grid-mode configuration.",
        default=SupportedBandAndGridEnum.GENERAL_C_BAND,
        alias="grid-mode-support",
    )
    attenuation_control_mode_rx: AttControlModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Attenuation control mode Rx (input) of the channel applicable to all channels of the OMS.\n\nCondition (when): ../monitoring-mode = 'intrusive' or ../monitoring-mode = 'ila-with-equalization' or ../monitoring-mode = 'integrated-equalization'",
        default=AttControlModeEnum.AUTO,
        alias="attenuation-control-mode-rx",
    )
    attenuation_control_mode_tx: AttControlModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Attenuation control mode Tx (output) of the channel applicable to all channels of the OMS.\n\nCondition (when): ../monitoring-mode = 'intrusive'",
        default=AttControlModeEnum.AUTO,
        alias="attenuation-control-mode-tx",
    )


class DirectionEnum_2(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * ingress
      * egress
    """

    INGRESS = "ingress"
    EGRESS = "egress"


class SpectrumControlItem(YangBaseModel):
    """DGE optical attenuation"""

    direction: DirectionEnum_2 = Field(json_schema_extra={"is_config": True}, description="Ingress or Egress direction")
    center_frequency: int = Field(
        json_schema_extra={"is_config": True}, description="Band slice center-frequency", ge=0, alias="center-frequency"
    )
    width: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Detected width from spectrum-monitoring. 0 means unmatched.",
        ge=0,
        default=0,
    )
    attenuation_actual: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual calculated attenuation.",
        default="0",
        alias="attenuation-actual",
    )
    attenuation_target: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="User configuration for the intended attenuation.",
        ge=0,
        le=30,
        default=None,
        alias="attenuation-target",
    )
    target_output_power: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="The intended target output power for the spectra.",
        default=None,
        alias="target-output-power",
    )


class SpectrumMonitoringItem(YangBaseModel):
    """DGE optical attenuation"""

    direction: DirectionEnum_2 = Field(
        json_schema_extra={"is_config": False}, description="Ingress or Egress direction"
    )
    center_frequency: int = Field(
        json_schema_extra={"is_config": False},
        description="Band slice center-frequency",
        ge=0,
        alias="center-frequency",
    )
    width: int | None = Field(
        json_schema_extra={"is_config": False}, description="Received nmc width", ge=0, default=50000
    )
    lower_frequency: int = Field(
        json_schema_extra={"is_config": False},
        description="Lower Frequency of a Media Channel.",
        ge=0,
        alias="lower-frequency",
    )
    upper_frequency: int = Field(
        json_schema_extra={"is_config": False},
        description="Upper Frequency of a Media Channel.",
        ge=0,
        alias="upper-frequency",
    )
    target_actual_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Value: as calculated by Power Control if target-power-setting = auto.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="target-actual-power",
    )
    power_actual: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently received power (-99: no power).",
        ge=-99.0,
        le=99.0,
        default=-99,
        alias="power-actual",
    )
    psd_actual: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently calculated PSD. The Power Spectral Density does not depend on the spectra width.",
        default="not-applicable",
        alias="psd-actual",
    )


class SpectrumItem(YangBaseModel):
    """OMS specific equalization within interstage access; and monitoring."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    dge_in_use: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Reports true if corresponding OMS monitoring-mode is ila-with-equalization",
        default=None,
        alias="dge-in-use",
    )
    attenuation_setting: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Entire spectrum attenuation",
        ge=0,
        le=30,
        default=0,
        alias="attenuation-setting",
    )
    spectrum_control: RestconfList[SpectrumControlItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="DGE optical attenuation",
        default=None,
        alias="spectrum-control",
    )
    spectrum_monitoring: RestconfList[SpectrumMonitoringItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="DGE optical attenuation",
        default=None,
        alias="spectrum-monitoring",
    )


class OchmItem(YangBaseModel):
    """ochm: Optical Channel non-intrusive monitoring.
    ECDP within OMS-nim.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    direction: DirectionEnum_2 | None = Field(
        json_schema_extra={"is_config": False}, description="Ingress or Egress direction", default=None
    )
    power_actual: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power measurement upon last OCM scan.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual",
    )


class McItem(YangBaseModel):
    """MC: Media Channel.
    A media association that represents both the topology (i.e., the path throughthe media) and the resource (i.e., frequency slot or effective frequency slot) that it occupies.
    In IOA, the frequency-slot is provided by the lower and upper-frequency.
    Media Channel minimum width: 50 GHz.
    Media Channel maximum width: 200 GHz.
    For C-band: Start Frequency:191300000 MHz and End Frequency:196150000 MHz.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    parent_oms: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Parent Media Channel. Only set by creation.\nThe referenced supporting-card must be part of a Degree (cannot be in an ADG).",
        min_length=1,
        max_length=64,
        alias="parent-oms",
    )
    center_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Center Frequency of the MC, determined by the SYSTEM.",
        ge=0,
        default=None,
        alias="center-frequency",
    )
    lower_frequency: int = Field(
        json_schema_extra={"is_config": True},
        description="Lower Frequency of a Media Channel.",
        ge=0,
        alias="lower-frequency",
    )
    upper_frequency: int = Field(
        json_schema_extra={"is_config": True},
        description="Upper Frequency of a Media Channel.",
        ge=0,
        alias="upper-frequency",
    )
    slot_width: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Slot width, as calculated by the system, from upper-frequency - lower-frequency.",
        ge=0,
        default=None,
        alias="slot-width",
    )


class ActivationStateTypeEnum(str, Enum):
    """Enumeration for ActivationStateTypeEnum

    Values:
      * not-applicable: Not applicable.
      * activated: In activated state.
      * partially-activated: In partially activated state.
      * faulted: In faulted state.
      * deactivated: In deactivated state.
    """

    NOT_APPLICABLE = "not-applicable"
    ACTIVATED = "activated"
    PARTIALLY_ACTIVATED = "partially-activated"
    FAULTED = "faulted"
    DEACTIVATED = "deactivated"


class AseInsertionControlEnum(str, Enum):
    """Enumeration for AseInsertionControlEnum

    Values:
      * adg-input-delta: ASE insertion criteria is power delta on ADG input power.
    """

    ADG_INPUT_DELTA = "adg-input-delta"


class NmcItem(YangBaseModel):
    """NMC: Network Media Channel facility.
    A network media channel is a logical entity representing the optical signal carrying the service.
    The optical signal is also referred to as optical carrier.
    NMC is defined by its center frequency and width.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    parent_facility: str = Field(
        json_schema_extra={"is_config": True},
        description="Parent facility: can be either a Media Channel or an OMS. Only set on creation.",
        alias="parent-facility",
    )
    och_connection: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="NMC redux - optical channel connection.",
        default=False,
        alias="och-connection",
    )
    monitoring_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="System reports this attribute, to indicate whether the NMC is intended\nto be in use (instead of simply being pre-provisioned);\nenabled if NMC is a member of an 'oxcon'.",
        default=EnableSwitchEnum.DISABLED,
        alias="monitoring-state",
    )
    center_frequency: int = Field(
        json_schema_extra={"is_config": True},
        description="Nominal Center Frequency of the NMC",
        ge=0,
        alias="center-frequency",
    )
    width: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Network Media Channel frequency width; unit is MHz.\nThe value in GHz should be equivalent to the baud rate (GBd) configured on the connected transponder line interface line port.",
        ge=0,
        default=35000,
    )
    input_power_min: str | float | None = Field(
        json_schema_extra={"is_config": True}, description="Minimum Input Power.", default=None, alias="input-power-min"
    )
    input_power_max: str | float | None = Field(
        json_schema_extra={"is_config": True}, description="Maximum Input Power.", default=None, alias="input-power-max"
    )
    input_power_typical: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Typical Input Power.",
        default=None,
        alias="input-power-typical",
    )
    input_power_min_offset: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Minimum Input Power offset, of relevance for NMCs within MCs.",
        ge=-30,
        le=30,
        default=0,
        alias="input-power-min-offset",
    )
    input_psd_min: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Calculated by the SYSTEM from input-power-min.",
        default=None,
        alias="input-psd-min",
    )
    input_psd_max: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Calculated by the SYSTEM from input-power-max.",
        default=None,
        alias="input-psd-max",
    )
    input_psd_typical: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Calculated by the SYSTEM from input-power-typ.",
        default=None,
        alias="input-psd-typical",
    )
    input_attenuation_actual: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual input attentuation.",
        default=None,
        alias="input-attenuation-actual",
    )
    input_attenuation_target: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable target input attentuation.",
        default=None,
        alias="input-attenuation-target",
    )
    output_attenuation_offset: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable target output attenuation offset.",
        default="0",
        alias="output-attenuation-offset",
    )
    input_attenuation_offset: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable target input attenuation offset.",
        default="0",
        alias="input-attenuation-offset",
    )
    output_attenuation_actual: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual output attentuation.",
        default=None,
        alias="output-attenuation-actual",
    )
    output_attenuation_target: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable target output attentuation.",
        default=None,
        alias="output-attenuation-target",
    )
    power_actual_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Received, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-rx",
    )
    power_actual_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Transmitted, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-tx",
    )
    ase_power_actual_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="ASE power of the protection ASE.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="ase-power-actual-tx",
    )
    ase_activation_state: ActivationStateTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Activation state of the protection ASE.",
        default=None,
        alias="ase-activation-state",
    )
    psd_actual_rx: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Calculated by the SYSTEM from power-actual-rx (i.e. dependent on spectrum width).",
        default=None,
        alias="psd-actual-rx",
    )
    psd_actual_tx: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Calculated by the SYSTEM from power-actual-tx (i.e. dependent on spectrum width).",
        default=None,
        alias="psd-actual-tx",
    )
    ase_insertion_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates if the ASE Idler insertion on NMC failure is enabled.",
        default=EnableSwitchEnum.DISABLED,
        alias="ase-insertion-enable",
    )
    ase_insertion_soak_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The duration for which NMC failure should be soaked before proceeding with ASE Idler injection if ASE insertion is enabled.",
        ge=0,
        le=600,
        default=5,
        alias="ase-insertion-soak-timer",
    )
    ase_insertion_control: AseInsertionControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the criteria for ASE Insertion. This is applicable only when ASE insertion is enabled.",
        default=AseInsertionControlEnum.ADG_INPUT_DELTA,
        alias="ase-insertion-control",
    )
    ase_insertion_delta: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="This is the amount by which the signal power must drop below the reference power for the NMC to initiate a replacement of the NMC with ASE (NMC-P).",
        ge=0,
        le=20,
        default=7,
        alias="ase-insertion-delta",
    )


class RscItem(YangBaseModel):
    """Raman Supervisory Channel: Raman card Pilot Tone facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    rsc_power_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The received Pilot Tone integrated power.",
        ge=-99.0,
        le=99.0,
        default=-99,
        alias="rsc-power-rx",
    )
    rsc_power_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The transmitted Pilot Tone integrated power.",
        ge=-99.0,
        le=99.0,
        default=-99,
        alias="rsc-power-tx",
    )


class PumpTypeEnum(str, Enum):
    """Enumeration for PumpTypeEnum

    Values:
      * raman-pump: (Backward) Raman Pump
    """

    RAMAN_PUMP = "raman-pump"


class PumpItem(YangBaseModel):
    """Raman Pump individual monitoring."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    pump_type: PumpTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Type of Pump.", default=None, alias="pump-type"
    )


class LineSystemModeEnum(str, Enum):
    """Enumeration for LineSystemModeEnum

    Values:
      * openwave: GX WDM channels over non-GX line system.
    """

    OPENWAVE = "openwave"


class SuperChannelGroupItem(YangBaseModel):
    """Super-channel Group facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    auto_in_service_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Auto-in-service switch for this facility.",
        default=False,
        alias="auto-in-service-enabled",
    )
    valid_signal_time: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable time that represents a detection of a valid signal.\nUsed for auto-in-service mechanism.",
        ge=0,
        le=7200,
        default=480,
        alias="valid-signal-time",
    )
    remaining_valid_signal_time: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual remaining time for this facility to be automatically enabled by the\nauto-in-service mechanism.",
        ge=0,
        le=7200,
        default=None,
        alias="remaining-valid-signal-time",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    line_system_mode: LineSystemModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the specific mode of power control configured\non the L1 transponder, and specifically, on this particular SCG port within\nthe L1 transponder. The attribute indicates the L1 <-> L0 local power controls\nto adjust the Tx power from the L1 transponder towards the L0 line-system\ncard (such as a WSS or Mux or Amplifier).",
        default=LineSystemModeEnum.OPENWAVE,
        alias="line-system-mode",
    )
    openwave_contention_check: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables DNA assisted contention control mechanism in openwave mode.\n    Only of relevance for line system mode openwave",
        default=False,
        alias="openwave-contention-check",
    )
    expected_total_tx_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Theoretical total TX power at Front Panel calculated based on per carrier Target TX power value.\n    Only of relevance for line system mode openwave",
        ge=-55.0,
        le=55.0,
        default=-55.00,
        alias="expected-total-tx-power",
    )


class ClientModeEnum(str, Enum):
    """Enumeration for ClientModeEnum

    Values:
      * ethernet
      * ethernet-otn
      * otn
      * unknown
    """

    ETHERNET = "ethernet"
    ETHERNET_OTN = "ethernet-otn"
    OTN = "otn"
    UNKNOWN = "unknown"


class SopTrackingModeEnum(str, Enum):
    """Enumeration for SopTrackingModeEnum

    Values:
      * normal: Normal SOP tracking mode.
      * lightning: Lightning SOP tracking mode.
    """

    NORMAL = "normal"
    LIGHTNING = "lightning"


class ContentionCheckStatusEnum(str, Enum):
    """Enumeration for ContentionCheckStatusEnum

    Values:
      * pending: Contention check is pending on DNA side.
      * success: Successful contention validation by DNA.
      * failed: Failed contention validation by DNA.
      * overridden: Explict user override of this function.
    """

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    OVERRIDDEN = "overridden"


class DtEncapsulationEnum(str, Enum):
    """Enumeration for DtEncapsulationEnum

    Values:
      * gre: Digital trigger encapsulation is Generic Routing Encapsulation.
      * simple-ip: Digital trigger encapsulation is Simple IP.
    """

    GRE = "gre"
    SIMPLE_IP = "simple-ip"


class DigitalTriggerRegistration(YangBaseModel):
    """Atttributes related to digital trigger fault registration from line system."""

    neighbor_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="ID of provisioned neighbor. Local reference to the neighbor.",
            min_length=1,
            max_length=64,
            default=None,
            alias="neighbor-id",
        )
    )
    remote_node_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Remote NE Name.",
        min_length=0,
        max_length=128,
        default=None,
        alias="remote-node-name",
    )
    remote_ne_ip: str | None = Field(
        json_schema_extra={"is_config": False},
        description="IP address of the remote NE that has registered for DT fault updates. 0.0.0.0 means that no ip is set to remote-ne-ip.",
        default="0.0.0.0",
        alias="remote-ne-ip",
    )
    remote_end_point: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the remote end point that has registered for DT fault updates.",
        min_length=0,
        max_length=128,
        default=None,
        alias="remote-end-point",
    )
    local_flow_id: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Flow ID assigned by GX node for this connection.",
        ge=0,
        default=None,
        alias="local-flow-id",
    )
    remote_flow_id: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Flow ID received from remote NE.",
        ge=0,
        default=None,
        alias="remote-flow-id",
    )
    dt_encapsulation: DtEncapsulationEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Encapsulation option.",
        default=DtEncapsulationEnum.GRE,
        alias="dt-encapsulation",
    )
    last_update: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Time of last fault registration request.",
        default="never",
        alias="last-update",
    )


class SuperChannelItem(YangBaseModel):
    """Unified channel of optical carriers. Can have many optical channels."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    carriers: RestconfList[str] = Field(
        json_schema_extra={"is_config": True},
        description="A list of carriers that are bound to this superchannel.\nPossible values can be any card/resources/supported-carriers.",
        min_length=1,
        max_length=32,
    )
    carrier_mode: str = Field(
        json_schema_extra={"is_config": True},
        description="Unique identifier of the carrier mode this super-channel is configured as.\nPossible carrier-modes are listed in the golden-carrier-mode list.",
        min_length=0,
        max_length=15,
        alias="carrier-mode",
    )
    actual_carrier_mode: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual carrier-mode.",
        min_length=0,
        max_length=15,
        default=None,
        alias="actual-carrier-mode",
    )
    capacity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The net capacity of the optical carrier.",
        ge=0,
        default=None,
    )
    client_mode: ClientModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This indicates digital client modes of the signal\nthat is mapped into, and transported by the carriers within this\nsuperchannel.",
        default=None,
        alias="client-mode",
    )
    baud_rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The modulated symbol rate.",
        default=None,
        alias="baud-rate",
    )
    application: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport application ID this mode is optimized for.",
        min_length=1,
        max_length=15,
        default=None,
    )
    sop_tracking_mode: SopTrackingModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport SOP tracking mode this mode is optimized for.",
        default=SopTrackingModeEnum.NORMAL,
        alias="sop-tracking-mode",
    )
    spectral_bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Spectral bandwith associated with this carrier(s).",
        default=None,
        alias="spectral-bandwidth",
    )
    contention_check_status: ContentionCheckStatusEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Contention Check state, set via DNA in openwave mode.\nOnly applicable if openwave-contention-check is enabled at super-channel-group level.",
        default=ContentionCheckStatusEnum.PENDING,
        alias="contention-check-status",
    )
    digital_trigger_registration: DigitalTriggerRegistration | None = Field(
        json_schema_extra={"is_config": False},
        description="Atttributes related to digital trigger fault registration from line system.",
        default=None,
        alias="digital-trigger-registration",
    )


class CarrierTypeEnum(str, Enum):
    """Enumeration for CarrierTypeEnum

    Values:
      * ICE6
      * ZR
      * ZR+
      * OTN
      * ICE7: ICE7 carrier.
    """

    ICE6 = "ICE6"
    ZR = "ZR"
    ZR_PLUS = "ZR+"
    OTN = "OTN"
    ICE7 = "ICE7"


class MediaInterfaceEnum(str, Enum):
    """Enumeration for MediaInterfaceEnum

    Values:
      * 400ZR-CFEC-DP-16QAM
    """

    _400ZR_CFEC_DP_16QAM = "400ZR-CFEC-DP-16QAM"


class GridSpacingEnum(str, Enum):
    """Enumeration for GridSpacingEnum

    Values:
      * 100
      * 75
      * 50
      * 33
      * 25
      * 12.5
      * 6.25
      * 3.125
    """

    _100 = "100"
    _75 = "75"
    _50 = "50"
    _33 = "33"
    _25 = "25"
    _12_5 = "12.5"
    _6_25 = "6.25"
    _3_125 = "3.125"


class ModulationFormatEnum(str, Enum):
    """Enumeration for ModulationFormatEnum

    Values:
      * not-applicable
      * DP-QPSK
      * DP-16QAM
      * DP-8QAM
      * BPSK
      * DP-16QAM-E
      * DP-16QAM-PS
      * DP-SPQPSK
      * DP-SPQPSK-QPSK
      * DP-SP16QAM
      * DP-32QAM
      * DP-SP16QAM-16QAM
      * DP-QPSK-SP16QAM
      * DP-64QAM
      * DP-16QAM-32QAM
      * DP-32QAM-64QAM
    """

    NOT_APPLICABLE = "not-applicable"
    DP_QPSK = "DP-QPSK"
    DP_16QAM = "DP-16QAM"
    DP_8QAM = "DP-8QAM"
    BPSK = "BPSK"
    DP_16QAM_E = "DP-16QAM-E"
    DP_16QAM_PS = "DP-16QAM-PS"
    DP_SPQPSK = "DP-SPQPSK"
    DP_SPQPSK_QPSK = "DP-SPQPSK-QPSK"
    DP_SP16QAM = "DP-SP16QAM"
    DP_32QAM = "DP-32QAM"
    DP_SP16QAM_16QAM = "DP-SP16QAM-16QAM"
    DP_QPSK_SP16QAM = "DP-QPSK-SP16QAM"
    DP_64QAM = "DP-64QAM"
    DP_16QAM_32QAM = "DP-16QAM-32QAM"
    DP_32QAM_64QAM = "DP-32QAM-64QAM"


class LineEncodingEnum(str, Enum):
    """Enumeration for LineEncodingEnum

    Values:
      * non-differential
      * differential
    """

    NON_DIFFERENTIAL = "non-differential"
    DIFFERENTIAL = "differential"


class AdvancedParameterItem(YangBaseModel):
    """The user configured (or overridden) set of advanced parameters."""

    name: str = Field(
        json_schema_extra={"is_config": True},
        description="Name of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    value: str = Field(
        json_schema_extra={"is_config": True},
        description="Value of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="State of the advanced parameter (as observable on the system) once it is configured.",
        default=StatusEnum.UNKNOWN,
    )


class CurrentAdvancedParameterItem(YangBaseModel):
    """The current value for a supported advanced parameter."""

    name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    value: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Value of the advanced parameter.",
        min_length=0,
        max_length=256,
        default=None,
    )


class LoopbackEnum(str, Enum):
    """Enumeration for LoopbackEnum

    Values:
      * none
      * facility
      * terminal
    """

    NONE = "none"
    FACILITY = "facility"
    TERMINAL = "terminal"


class OpticalCarrierItem(YangBaseModel):
    """Optical carrier facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    frequency: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="The center frequency this carrier is tuned to. Zero means 'not configured'.",
        default="0",
    )
    frequency_offset: int | None = Field(
        json_schema_extra={"is_config": True},
        description="A super set range for line and client side carrier, specific sub-range is depend on application. Frequency-offset can be used for bright tuning\nof the wavelengths.\nOnce set, the frequency will slowly change (over 1-10s) without affecting service.",
        ge=-6000,
        le=6000,
        default=0,
        alias="frequency-offset",
    )
    wavelength: Decimal64 | None = Field(
        json_schema_extra={"is_config": False}, description="The wavelength of the optical carrier.", default=None
    )
    tx_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The optical carrier's transmit power into the fiber from the transponder's optics.\nNOTE: The accuracy of the Tx Power can be adjusted in steps of 0.5 dBm.",
        ge=-55.0,
        le=55.0,
        default=-6.0,
        alias="tx-power",
    )
    pre_fec_q_sig_deg_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold based on which the PRE-FEC-Q-SIGNAL-DEGRADE alarm is raised.\n0 implies threshold crossing alarming disabled.\nSpecific sub-range is per carrier use-case.",
        le=9.6,
        default=6.0,
        alias="pre-fec-q-sig-deg-threshold",
    )
    pre_fec_q_sig_deg_hysteresis: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Hysteresis to account for raising of the PRE-FEC-Q-SIGNAL-DEGRADE alarm.",
        ge=0.1,
        le=1.0,
        default=0.5,
        alias="pre-fec-q-sig-deg-hysteresis",
    )
    carrier_type: CarrierTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Intent is to differentiate the multiple CarierCTPs.",
        default=CarrierTypeEnum.ICE6,
        alias="carrier-type",
    )
    carrier_mode: str | None = Field(
        json_schema_extra={"is_config": True},
        description="An acronymized code (handle) that is indicative of the optical carrier line mode (4-tuple) combination.\nThe format is as follows:\n   <Capacity><ClientMode>.<Baud Rate><Application ID>\nExamples:\n   - 600E.84P\n   - 100X.73U\n   - 325M.66P",
        min_length=0,
        max_length=15,
        default=None,
        alias="carrier-mode",
    )
    actual_carrier_mode: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual carrier-mode.",
        min_length=0,
        max_length=15,
        default=None,
        alias="actual-carrier-mode",
    )
    capacity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The net capacity of the optical carrier.",
        ge=0,
        default=None,
    )
    client_mode: ClientModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This indicates digital client modes of the signal\nthat is mapped into, and transported by the carriers within this\nsuperchannel.",
        default=None,
        alias="client-mode",
    )
    baud_rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The modulated symbol rate.",
        default=None,
        alias="baud-rate",
    )
    application: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport application ID this mode is optimized for.",
        min_length=1,
        max_length=15,
        default=None,
    )
    sop_tracking_mode: SopTrackingModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport SOP tracking mode this mode is optimized for.",
        default=SopTrackingModeEnum.NORMAL,
        alias="sop-tracking-mode",
    )
    media_interface: MediaInterfaceEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Media interface type of ZR tom.",
        default=MediaInterfaceEnum._400ZR_CFEC_DP_16QAM,
        alias="media-interface",
    )
    grid_spacing: GridSpacingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Fixed Grid tunability for new 3rd party TOM.",
        default=GridSpacingEnum._100,
        alias="grid-spacing",
    )
    spectral_bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Spectral bandwith associated with this carrier(s).",
        default=None,
        alias="spectral-bandwidth",
    )
    tx_cd: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured transmit pre-compensation chromatic dispersion.",
        ge=-211000.0,
        le=211000.0,
        default=0.0,
        alias="tx-cd",
    )
    dgd_high_threshold: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The threshold to raise the DGD-OORH alarm.",
        ge=180,
        le=350,
        default=300,
        alias="dgd-high-threshold",
    )
    post_fec_q_sig_deg_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold based on which the POST-FEC-Q-SIGNAL-DEGRADE alarm is raised.",
        ge=12.5,
        le=18.0,
        default=18,
        alias="post-fec-q-sig-deg-threshold",
    )
    post_fec_q_sig_deg_hysteresis: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Hysteresis to account for raising of the POST-FEC-Q-SIGNAL-DEGRADE alarm.",
        ge=0.1,
        le=3.0,
        default=2.5,
        alias="post-fec-q-sig-deg-hysteresis",
    )
    rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": True}, description="Carried signal basic rate class.", default=None
    )
    modulation_format: ModulationFormatEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Current modulation format.",
        default=None,
        alias="modulation-format",
    )
    line_encoding: LineEncodingEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently line-encoding mode.",
        default=LineEncodingEnum.NON_DIFFERENTIAL,
        alias="line-encoding",
    )
    rx_frequency: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="The rx laser frequency. Special for 0 means it is same as tx laser frequency.",
        default="0",
        alias="rx-frequency",
    )
    rx_attenuation: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="This is to support configurable optical attenuation at receiver side which is based on the hardware capability on the port.",
        ge=-55.0,
        le=55.0,
        default=0.0,
        alias="rx-attenuation",
    )
    tx_filter_roll_off: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmitter filter roll off factor.",
        ge=0.01,
        le=1.0,
        default=0.2,
        alias="tx-filter-roll-off",
    )
    preemphasis: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Preemphasis of transmitted signal.",
        default=EnableSwitchEnum.ENABLED,
    )
    preemphasis_value: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Preemphasis of transmitted signal.",
        ge=0.0,
        le=3.0,
        default=1.0,
        alias="preemphasis-value",
    )
    cd_range_low: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Low value of chromatic dispersion search range.",
        default=-45000,
        alias="cd-range-low",
    )
    cd_range_high: int | None = Field(
        json_schema_extra={"is_config": True},
        description="high value of chromatic dispersion search range.",
        default=45000,
        alias="cd-range-high",
    )
    cd_compensation_mode: OscControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="chromatic dispersion compensation value source mode.",
        default=OscControlEnum.AUTO,
        alias="cd-compensation-mode",
    )
    cd_compensation_value: int | None = Field(
        json_schema_extra={"is_config": True},
        description="manual chromatic dispersion compensation value",
        default=None,
        alias="cd-compensation-value",
    )
    fast_sop_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify if enable fast SOP (state of polarization) change tracking; if enabled, the interface\n   will tolerate very fast SOP and transient.",
        default=EnableSwitchEnum.DISABLED,
        alias="fast-sop-mode",
    )
    BICHM: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The BICHM (bit interleaved coded hybrid modulation) incremental step in 1/128 bits/symbol added to base modulation bits/symbol for the hybrid modes modulation-format.\n0: Base modulation format bits/symbol;\n1: 1/128 bits/symbol added to base modulation format bits/symbol;\n...\n127: 127/128 bits/symbol added to base modulation format bits/symbol",
        ge=0,
        le=127,
        default=64,
    )
    propagate_shutdown: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="When the attribute value is set to yes, the transmit laser will\nbe shutdown if the whole service of the direction has signal failure,\nthe function mainly used in regeneration node to propagate signal failure as LOS.",
        default=EnableSwitchEnum.DISABLED,
        alias="propagate-shutdown",
    )
    propagate_shutdown_holdoff_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The hold off time of propagate shutdown.",
        ge=0,
        le=2000,
        default=0,
        alias="propagate-shutdown-holdoff-timer",
    )
    actual_rx_frequency: str | int | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual rx laser frequency for coherent interface with separating Lo laser from Tx.\n0 means Lo and Tx share the same laser where 'frequency' attriute will indicate both Tx and Rx.",
        default="0",
        alias="actual-rx-frequency",
    )
    actual_frequency: str | int | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual laser frequency.\nIf rx-frequency is 0, it reflects both Rx and Tx frequency for coherent interface.",
        default="0",
        alias="actual-frequency",
    )
    enable_advanced_parameters: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls enabling/disabling of configuring advanced parameters for this object.",
        default=False,
        alias="enable-advanced-parameters",
    )
    sop_data_collection: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls enabling/disabling sop data collection, providing the collection interval in ms.\n    Only of relevance for carrier type ICE6.",
        default="disabled",
        alias="sop-data-collection",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )
    sop_vector: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The RX SOP (State Of Polarization) Stokes Vector S1 S2 S3, Example: 0.96, -0.12, -0.22.\n    Only of relevance for carrier type OTN.",
        min_length=0,
        max_length=18,
        default="",
        alias="sop-vector",
    )
    client_slew_rate: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Network to client direction PLL slew rate in ppm-steps for all clients supported by the optical-carrier.",
        ge=1,
        le=256,
        default=1,
        alias="client-slew-rate",
    )
    advanced_parameter: RestconfList[AdvancedParameterItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="The user configured (or overridden) set of advanced parameters.\n\nCondition (when): ../enable-advanced-parameters = 'true'",
        default=None,
        alias="advanced-parameter",
    )
    current_advanced_parameter: RestconfList[CurrentAdvancedParameterItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="The current value for a supported advanced parameter.",
        default=None,
        alias="current-advanced-parameter",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )


class OpticalChannelItem(YangBaseModel):
    """The OCh is a dummy, place-holder object merely
    existing for the purposes of object model hierarchy. All
    attributes of OCh are marked as read-only.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )


class OtuTypeEnum(str, Enum):
    """Enumeration for OtuTypeEnum

    Values:
      * OTUCn: OTUCn protocol layer.
      * OTUCni: GX proprietary OTUCni protocol layer.
      * OTUCni-M: GX proprietary OTUCni protocol layer.
      * OTU4: OTU4 protocol layer.
      * OTU2: OTU2 protocol layer.
      * OTU2e: OTU2e protocol layer.
      * OTUflex: OTU-flex protocol layer.
    """

    OTUCN = "OTUCn"
    OTUCNI = "OTUCni"
    OTUCNI_M = "OTUCni-M"
    OTU4 = "OTU4"
    OTU2 = "OTU2"
    OTU2E = "OTU2e"
    OTUFLEX = "OTUflex"


class ServiceModeEnum(str, Enum):
    """Enumeration for ServiceModeEnum

    Values:
      * none
      * network-wrapper: Map non-OTN signal into ODUs.
      * adaptation: Multiplexing scenarios.
      * switching: Map OTN signal (e.g. OTU) into ODUs.
      * transport: Transport OTN signal (e.g. OTU) into line side ODUs.
    """

    NONE = "none"
    NETWORK_WRAPPER = "network-wrapper"
    ADAPTATION = "adaptation"
    SWITCHING = "switching"
    TRANSPORT = "transport"


class FecTypeEnum(str, Enum):
    """Enumeration for FecTypeEnum

    Values:
      * cfec
      * ofec
      * G709
      * noFEC
      * i4: EFEC-I4
      * i7: EFEC-I7
      * sdfec15: 15% SDFEC-Differential
      * sdfec15nd: 15% SDFEC-Non-Differential
      * staircase7: 7% HDFEC Staircase
      * ufec7: 7% UFEC
      * sdfec20: 20% SD-FEC
      * RS-528_514: 100GbE fec-type
      * RS-544_514: 100/200/400GbE fec-type
      * sdfec15nd2: 15% SDFEC-Non-Differential 2
      * sdfec27nd: 27% SDFEC-Non-Differential
    """

    CFEC = "cfec"
    OFEC = "ofec"
    G709 = "G709"
    NOFEC = "noFEC"
    I4 = "i4"
    I7 = "i7"
    SDFEC15 = "sdfec15"
    SDFEC15ND = "sdfec15nd"
    STAIRCASE7 = "staircase7"
    UFEC7 = "ufec7"
    SDFEC20 = "sdfec20"
    RS_528_514 = "RS-528_514"
    RS_544_514 = "RS-544_514"
    SDFEC15ND2 = "sdfec15nd2"
    SDFEC27ND = "sdfec27nd"


class MappingModeEnum(str, Enum):
    """Enumeration for MappingModeEnum

    Values:
      * GMP: Generic Mapping Procedure
      * BMP: BMP mapping
      * openZR+: mapping mode for ZR
      * FlexE-4x100G: FlexE-4x100G for split lamda feature
      * GFP-F: GFP-F
      * GFP-F-extOPU2: GFP-F-extOPU2
      * AMP: AMP
      * iGMP: For Ethernet client which is INFN proprietary Async mapping
      * none: For OTU4 client with Acacia GL2 DSP or Marvel Canopus DSP based module
      * split-BMP-ODUflex: odu client split lambda for oduflexo line
    """

    GMP = "GMP"
    BMP = "BMP"
    OPENZR_PLUS = "openZR+"
    FLEXE_4X100G = "FlexE-4x100G"
    GFP_F = "GFP-F"
    GFP_F_EXTOPU2 = "GFP-F-extOPU2"
    AMP = "AMP"
    IGMP = "iGMP"
    NONE = "none"
    SPLIT_BMP_ODUFLEX = "split-BMP-ODUflex"


class LoopbackModeEnum(str, Enum):
    """Enumeration for LoopbackModeEnum

    Values:
      * loopback: loopback the signal, insert a maintenance signal
      * loopback-and-continue: loopback the signal, insert a maintenance signal and bridge (continue) the signal downstream
    """

    LOOPBACK = "loopback"
    LOOPBACK_AND_CONTINUE = "loopback-and-continue"


class MonitoringModeEnum(str, Enum):
    """Enumeration for MonitoringModeEnum

    Values:
      * unused: Unused
      * intrusive: Intrusive monitoring
      * non-intrusive: Non-intrusive monitoring
      * limited-non-intrusive: Non-intrusive monitoring
    """

    UNUSED = "unused"
    INTRUSIVE = "intrusive"
    NON_INTRUSIVE = "non-intrusive"
    LIMITED_NON_INTRUSIVE = "limited-non-intrusive"


class TtiMismatchAlarmReportingEnum(str, Enum):
    """Enumeration for TtiMismatchAlarmReportingEnum

    Values:
      * disabled: No TTI match checking
      * full-64-bytes: Compares entire TTI 64 bytes (proprietary style)
      * SAPI: Comparing SAPI only (ITU style)
      * DAPI: Comparing DAPI only (ITU style)
      * OPER: Comparing Operator Specific only (ITU style)
      * SAPI_DAPI: Comparing SAPI + DAPI (ITU style)
      * SAPI_OPER: Comparing SAPI + OPER (ITU style)
      * DAPI_OPER: Comparing DAPI + OPER (ITU style)
      * SAPI_DAPI_OPER: Comparing SAPI + DAPI + OPER (ITU style)
    """

    DISABLED = "disabled"
    FULL_64_BYTES = "full-64-bytes"
    SAPI = "SAPI"
    DAPI = "DAPI"
    OPER = "OPER"
    SAPI_DAPI = "SAPI_DAPI"
    SAPI_OPER = "SAPI_OPER"
    DAPI_OPER = "DAPI_OPER"
    SAPI_DAPI_OPER = "SAPI_DAPI_OPER"


class OtuDiagnosticsItem(YangBaseModel):
    """Set of attributes associated with OTU diagnostics.Each direction has their own values."""

    direction: DirectionEnum_2 = Field(
        json_schema_extra={"is_config": True}, description="Diagnostics direction.Can be ingress or egress."
    )
    monitoring_mode: MonitoringModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The monitoring mode on the ODU/OTU client.",
        default=MonitoringModeEnum.INTRUSIVE,
        alias="monitoring-mode",
    )
    tti_style: TtiStyleEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured mode of the TTI for this OTU/ODU client or OTS.",
        default=TtiStyleEnum.ITU_T_G709,
        alias="tti-style",
    )
    tti_mismatch_alarm_reporting: TtiMismatchAlarmReportingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates if TTI-Mismatch (TIM) alarm is reported or not.\nIf it is to be reported, indicates the criteria based on with the TIM alarm is reported.",
        default=TtiMismatchAlarmReportingEnum.DISABLED,
        alias="tti-mismatch-alarm-reporting",
    )
    tx_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmit TTI - Sent by this facility to the far-end remote facility.\n\nCondition (when): tti-style = 'proprietary'",
        default=None,
        alias="tx-tti",
    )
    rx_tti: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="Receive TTI - Received by this facility from the far-end remote facility.\n\nCondition (when): tti-style = 'proprietary'",
        default=None,
        alias="rx-tti",
    )
    rx_tti_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Receive TTI in HEX.\n\nCondition (when): tti-style = 'proprietary'",
        default=None,
        alias="rx-tti-hex",
    )
    expected_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Expected TTI - The TTI this facility expects to receive from the far-end remote facility.\n\nCondition (when): tti-style = 'proprietary'",
        default="",
        alias="expected-tti",
    )
    expected_sapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected SAPI (Source Access Point Identifier).\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="expected-sapi",
    )
    expected_dapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected DAPI (Destination Access Point Identifier).\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="expected-dapi",
    )
    expected_operator: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected operator specific bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="expected-operator",
    )
    tx_operator: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The transmitted operator specific bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="tx-operator",
    )
    rx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received operation specific bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-operator",
    )
    tx_sapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The transmitted SAPI bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="tx-sapi",
    )
    tx_dapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The transmitted DAPI bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="tx-dapi",
    )
    rx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received SAPI bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-sapi",
    )
    rx_sapi_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received SAPI in HEX.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-sapi-hex",
    )
    rx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received DAPI bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-dapi",
    )
    rx_dapi_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received DAPI in HEX.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-dapi-hex",
    )
    rx_operator_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received operator in HEX.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-operator-hex",
    )
    tim_act_enabled: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Support configurable TIM action which decide if insert maintenance signal per TIM: enable or disable, default disable",
        default=EnableSwitchEnum.DISABLED,
        alias="tim-act-enabled",
    )
    nmoper_alarm_reporting: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates if a Neighbor Mismatch TTI Operator-Specific field based (NMOPER) alarm is reported or not.",
        default=EnableSwitchEnum.DISABLED,
        alias="nmoper-alarm-reporting",
    )
    degrade_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error\nthreshold for each of those seconds for the purposes of SDBER detection.",
        ge=2,
        le=10,
        default=7,
        alias="degrade-interval",
    )
    degrade_threshold: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold in percentage of block errors versus total blocks at which a degrade-interval number of seconds\nwill be considered degraded for the purposes of SDBER detection.",
        ge=0,
        le=100,
        default=30,
        alias="degrade-threshold",
    )


class OtuItem(YangBaseModel):
    """Facility describing the OTUCn/OTUk according with standard ITU-T G.709."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    otu_type: OtuTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The protocol type of the OTUk/OTUCn client.",
        default=None,
        alias="otu-type",
    )
    rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The speed/rate of the OTUk/OTUCn client interface.",
        default=None,
    )
    otu_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A system-defined user friendly name for this otu, considering both the type and the rate.\nExamples: OTUC4, OTUC5i90",
        min_length=0,
        max_length=32,
        default=None,
        alias="otu-name",
    )
    service_mode: ServiceModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute is to align with legacy  OTN virtualization attribute (SM).\nThe 'service mode' attribute indicates the OTUk/OTUCn client's treatment/processing\nvis-a-vis the service type (OTN multiplexing, OTU transport, ...)",
        default=ServiceModeEnum.NONE,
        alias="service-mode",
    )
    service_mode_qualifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute is to align with legacy  OTN virtualization attribute (SMQ).\nThe 'service mode qualifier' attribute further adds to the 'service mode' attribute\nto indicate the OTUk/OTUCn client's contained payload vis-a-vis the service type\n(OTN multiplexing, OTU transport, ...)",
        default="none",
        alias="service-mode-qualifier",
    )
    fec_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured Forward Error Correction (FEC) mode on the OTUk/OTUCn client.",
        default=EnableSwitchEnum.ENABLED,
        alias="fec-mode",
    )
    fec_generation_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured FEC generation mode on the OTUk/OTUCn client towards the far-end receiver.",
        default=EnableSwitchEnum.ENABLED,
        alias="fec-generation-mode",
    )
    fec_type: FecTypeEnum | None = Field(
        json_schema_extra={"is_config": True}, description="The FEC type", default=FecTypeEnum.NOFEC, alias="fec-type"
    )
    tx_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The tx mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=MappingModeEnum.NONE,
        alias="tx-mapping-mode",
    )
    expected_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=MappingModeEnum.NONE,
        alias="expected-mapping-mode",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )
    parent: str | None = Field(
        json_schema_extra={"is_config": True}, description="For line OTU, indicates the parent facility.", default=None
    )
    time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Time slots of the ODU.",
        min_length=0,
        max_length=255,
        default=None,
        alias="time-slots",
    )
    otu_diagnostics: RestconfList[OtuDiagnosticsItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Set of attributes associated with OTU diagnostics.Each direction has their own values.",
        default=None,
        alias="otu-diagnostics",
    )


class OduTypeEnum(str, Enum):
    """Enumeration for OduTypeEnum

    Values:
      * ODUCn: OTUCn protocol layer.
      * ODUCni: GX proprietary OTUCni protocol layer.
      * ODUCni-M: GX proprietary OTUCni protocol layer.
      * ODU4: ODU4 protocol layer.
      * ODU4i: GX proprietary ODU4i protocol layer.
      * ODUflexi: GX proprietary ODUflexi protocol layer.
      * ODUflex: ODU-flex protocol layer.
      * ODU0: ODU0 protocol layer.
      * ODU1: ODU1 protocol layer.
      * ODU2: ODU2 protocol layer.
      * ODU2e: ODU2e protocol layer.
    """

    ODUCN = "ODUCn"
    ODUCNI = "ODUCni"
    ODUCNI_M = "ODUCni-M"
    ODU4 = "ODU4"
    ODU4I = "ODU4i"
    ODUFLEXI = "ODUflexi"
    ODUFLEX = "ODUflex"
    ODU0 = "ODU0"
    ODU1 = "ODU1"
    ODU2 = "ODU2"
    ODU2E = "ODU2e"


class ClassEnum(str, Enum):
    """Enumeration for ClassEnum

    Values:
      * high-order: Indicates all HO-ODUCn/HO-ODUk entities
      * low-order: Indicates all LO-ODUCn/LO-ODUk/LO-ODUj entities
      * mapped: Indicates a mapped non-OTN or OTN client signal, i.e. a terminated ODUk or and adapted ODUk acc. to the functional model.
    """

    HIGH_ORDER = "high-order"
    LOW_ORDER = "low-order"
    MAPPED = "mapped"


class ClientDefectIndicatorEnum(str, Enum):
    """Enumeration for ClientDefectIndicatorEnum

    Values:
      * local-degraded
      * remote-degraded
      * local-and-remote-degraded
      * none
      * unknown
    """

    LOCAL_DEGRADED = "local-degraded"
    REMOTE_DEGRADED = "remote-degraded"
    LOCAL_AND_REMOTE_DEGRADED = "local-and-remote-degraded"
    NONE = "none"
    UNKNOWN = "unknown"


class ClientSignalTypeEnum(str, Enum):
    """Enumeration for ClientSignalTypeEnum

    Values:
      * not-applicable
      * 200GBE
      * 400GBE
      * FC4G
      * FC8G
      * FC16G
      * FC32G
    """

    NOT_APPLICABLE = "not-applicable"
    _200GBE = "200GBE"
    _400GBE = "400GBE"
    FC4G = "FC4G"
    FC8G = "FC8G"
    FC16G = "FC16G"
    FC32G = "FC32G"


class SignalTypeEnum(str, Enum):
    """Enumeration for SignalTypeEnum

    Values:
      * none: Indicates that test pattern generation is disabled.
      * PRBS31Q: Defined in G.709 OPU PRBS with inverted PN31 quaternary.
      * PRBS13Q: Defined in G.709 OPU PRBS with inverted PN13 quaternary.
      * scrambled-idles: Idle frame defined in 802.3 Clause 82.2.10.
      * PRBS9: Defined in G.709 OPU PRBS with non-inverted PN9.
      * PRBS31: Defined in G.709 OPU PRBS with inverted PN31.
      * PRBS31_NONINV: Defined in G.709 OPU PRBS with non-inverted PN31.
    """

    NONE = "none"
    PRBS31Q = "PRBS31Q"
    PRBS13Q = "PRBS13Q"
    SCRAMBLED_IDLES = "scrambled-idles"
    PRBS9 = "PRBS9"
    PRBS31 = "PRBS31"
    PRBS31_NONINV = "PRBS31_NONINV"


class PrbsDirectionEnum(str, Enum):
    """Enumeration for PrbsDirectionEnum

    Values:
      * ingress
      * egress
      * both
    """

    INGRESS = "ingress"
    EGRESS = "egress"
    BOTH = "both"


class OduDiagnosticsItem(YangBaseModel):
    """Set of attributes associated with ODU diagnostics.Each direction has their own values."""

    direction: DirectionEnum_2 = Field(
        json_schema_extra={"is_config": True}, description="Diagnostics direction.Can be ingress or egress."
    )
    monitoring_mode: MonitoringModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The monitoring mode on the ODU/OTU client.",
        default=MonitoringModeEnum.INTRUSIVE,
        alias="monitoring-mode",
    )
    tti_style: TtiStyleEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured mode of the TTI for this OTU/ODU client or OTS.",
        default=TtiStyleEnum.ITU_T_G709,
        alias="tti-style",
    )
    tti_mismatch_alarm_reporting: TtiMismatchAlarmReportingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates if TTI-Mismatch (TIM) alarm is reported or not.\nIf it is to be reported, indicates the criteria based on with the TIM alarm is reported.",
        default=TtiMismatchAlarmReportingEnum.DISABLED,
        alias="tti-mismatch-alarm-reporting",
    )
    tx_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmit TTI - Sent by this facility to the far-end remote facility.\n\nCondition (when): tti-style = 'proprietary'",
        default=None,
        alias="tx-tti",
    )
    rx_tti: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="Receive TTI - Received by this facility from the far-end remote facility.\n\nCondition (when): tti-style = 'proprietary'",
        default=None,
        alias="rx-tti",
    )
    rx_tti_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Receive TTI in HEX.\n\nCondition (when): tti-style = 'proprietary'",
        default=None,
        alias="rx-tti-hex",
    )
    expected_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Expected TTI - The TTI this facility expects to receive from the far-end remote facility.\n\nCondition (when): tti-style = 'proprietary'",
        default="",
        alias="expected-tti",
    )
    expected_sapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected SAPI (Source Access Point Identifier).\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="expected-sapi",
    )
    expected_dapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected DAPI (Destination Access Point Identifier).\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="expected-dapi",
    )
    expected_operator: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected operator specific bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="expected-operator",
    )
    tx_operator: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The transmitted operator specific bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="tx-operator",
    )
    rx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received operation specific bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-operator",
    )
    tx_sapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The transmitted SAPI bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="tx-sapi",
    )
    tx_dapi: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The transmitted DAPI bytes.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default="",
        alias="tx-dapi",
    )
    rx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received SAPI bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-sapi",
    )
    rx_sapi_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received SAPI in HEX.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-sapi-hex",
    )
    rx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received DAPI bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-dapi",
    )
    rx_dapi_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received DAPI in HEX.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-dapi-hex",
    )
    rx_operator_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received operator in HEX.\n\nCondition (when): tti-style = 'ITU-T-G709'",
        default=None,
        alias="rx-operator-hex",
    )
    tim_act_enabled: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Support configurable TIM action which decide if insert maintenance signal per TIM: enable or disable, default disable",
        default=EnableSwitchEnum.DISABLED,
        alias="tim-act-enabled",
    )
    degrade_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error\nthreshold for each of those seconds for the purposes of SDBER detection.",
        ge=2,
        le=10,
        default=7,
        alias="degrade-interval",
    )
    degrade_threshold: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold in percentage of block errors versus total blocks at which a degrade-interval number of seconds\nwill be considered degraded for the purposes of SDBER detection.",
        ge=0,
        le=100,
        default=30,
        alias="degrade-threshold",
    )
    test_signal_type: SignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of test pattern that is injected.",
        default=SignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: PrbsDirectionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The direction of the test signal.",
        default=PrbsDirectionEnum.INGRESS,
        alias="test-signal-direction",
    )
    test_signal_monitoring: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitor the incoming test signals for diagnostics.",
        default=False,
        alias="test-signal-monitoring",
    )
    test_signal_monitoring_type: SignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of test pattern that is monitored.",
        default=SignalTypeEnum.NONE,
        alias="test-signal-monitoring-type",
    )


class OduItem(YangBaseModel):
    """ODUCni/ODUki facility, representing both line side and client side ODUs.
    Represents both GX proprietary line-side ODUki/ODUCni protocol, as well as ITU standard ODUk/OCUCn protocol
    Represents both high order and low order ODUs.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.USER,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    parent_odu: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="For low order ODUs, points to the the parent HO-ODU name.",
        min_length=1,
        max_length=64,
        default=None,
        alias="parent-odu",
    )
    odu_type: OduTypeEnum = Field(
        json_schema_extra={"is_config": True},
        description="The protocol type of the ODUk/ODUCn client.",
        alias="odu-type",
    )
    rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The speed/rate of the ODUk/ODUCn client interface.",
        default=None,
    )
    odu_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A system-defined user friendly name for this odu, considering both the type and the rate.\nExamples: ODU4, ODUC8i",
        min_length=0,
        max_length=32,
        default=None,
        alias="odu-name",
    )
    class_: ClassEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute indicates the class/category of the ODUCn/ODUk entity.\n'High order' refers to the top-most ODUCn/ODUk entity that is created by the system.\nAll other children ODUk/ODUj entites are categorized as 'low order' (i.e., supported\nby another high-order ODUCn/ODUk). This attribute is set by the system based on the order\nof creation of these entities (system created v/s user created).",
        default=ClassEnum.LOW_ORDER,
        alias="class",
    )
    service_mode: ServiceModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute is to align with legacy  OTN virtualization attribute (SM).\nThe 'service mode' attribute indicates the ODUk/ODUCn client's treatment/processing\nvis-a-vis the service type (OTN multiplexing, OTU transport, ...)",
        default=ServiceModeEnum.NONE,
        alias="service-mode",
    )
    service_mode_qualifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute is to align with legacy  OTN virtualization attribute (SMQ).\nThe 'service mode qualifier' attribute further adds to the 'service mode' attribute\nto indicate the ODUk/ODUCn client's contained payload vis-a-vis the service type\n(OTN multiplexing, OTU transport, ...)",
        default="none",
        alias="service-mode-qualifier",
    )
    trib_port_number: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Number of OPUk/OPUCn trib port that are part of this ODUk/ODUCn container.",
        ge=1,
        default=None,
        alias="trib-port-number",
    )
    time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Time slots of the ODU.",
        min_length=0,
        max_length=255,
        default=None,
        alias="time-slots",
    )
    opucn_time_slots: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((([0-9]+(\\.[0-9]+)?)+(\\.\\.([0-9]+(\\.[0-9]+)?))?)(,(([0-9]+(\\.[0-9]+)?)+(\\.\\.([0-9]+(\\.[0-9]+)?))?))*))$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Opucn Time slots of the ODUCn.",
        min_length=0,
        max_length=500,
        default=None,
        alias="opucn-time-slots",
    )
    instance_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Optional parameter on LO-ODU creation, identifies the ODU within the parent/high-order ODU.\nIf not provided, it is automatically derived.\nMax value depends on capacity of the HO-ODU and of the odu-type.\n(ex: for creating an ODU4 in a HO ODUC8, instance can be between 1 and 8)",
        ge=1,
        default=None,
        alias="instance-id",
    )
    total_time_slots: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of OPUk/OPUCn time slots that are part of this ODUk/ODUCn container.\n\nCondition (when): ../class = 'high-order'",
        ge=0,
        default=None,
        alias="total-time-slots",
    )
    available_time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="A list of all OPUk/OPUCn time-slots that are available for provisioning new services.\n\nCondition (when): ../class='high-order'",
        min_length=0,
        max_length=255,
        default=None,
        alias="available-time-slots",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )
    accepted_trib_port_number: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received and accepted Tributary Port Number for the LO-ODU entity.",
        min_length=0,
        max_length=255,
        default=None,
        alias="accepted-trib-port-number",
    )
    expected_trib_port_number: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Expected Tributary Port Number for the LO-ODU entity.",
        ge=1,
        default=None,
        alias="expected-trib-port-number",
    )
    accepted_time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received and accepted TS for the LO-ODU entity.",
        min_length=0,
        max_length=255,
        default=None,
        alias="accepted-time-slots",
    )
    expected_time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Expected TS for the LO-ODU entity.",
        min_length=0,
        max_length=255,
        default=None,
        alias="expected-time-slots",
    )
    rx_msi: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Received and accepted MSI values (up to 80), including a valid/invalid indication\n(valid if acceptance process successful, invalid if not; when invalid the last accepted MSI set is shown).",
        min_length=0,
        max_length=512,
        default=None,
        alias="rx-msi",
    )
    rx_msi_hex: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Received and accepted MSI hex values (up to 80) (if acceptance process was not successful the last accepted MSI set is shown).",
        min_length=0,
        max_length=512,
        default=None,
        alias="rx-msi-hex",
    )
    expected_msi: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Expected MSI values (up to 80). For format see rx-msi without valid/invalid flag.\nUser-friendly representation of expected-msi-hex.",
        min_length=0,
        max_length=512,
        default=None,
        alias="expected-msi",
    )
    expected_msi_hex: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Expected MSI hex values (up to 80).",
        min_length=0,
        max_length=512,
        default=None,
        alias="expected-msi-hex",
    )
    client_defect_indicator: ClientDefectIndicatorEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates current defect status on client side.",
        default=ClientDefectIndicatorEnum.NONE,
        alias="client-defect-indicator",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )
    rx_payload_type: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Received payload-type of ODU.",
        default=None,
        alias="rx-payload-type",
    )
    tx_payload_type: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Transmitter payload-type of ODU",
        default=None,
        alias="tx-payload-type",
    )
    expected_payload_type: (
        RestconfList[
            Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))]
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Expected payload-type of ODU",
        default=None,
        alias="expected-payload-type",
    )
    delay_measurement_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The enable switching of delay-measurement function, when applicable.",
        default=EnableSwitchEnum.DISABLED,
        alias="delay-measurement-enable",
    )
    msim_config: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies MSIM alarm reporting or not when msi value received not followed G.709 definition.",
        default=EnableSwitchEnum.ENABLED,
        alias="msim-config",
    )
    client_signal_type: ClientSignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Client signal type for ODUflex  CBR client.\nApplied to 200/400 GBE client on CHM1R and FC4/8/16 for UTM2\nIt is set automatically for the client side ODU,\nand need to be configured by the user at line side ODUj.\nUsed for rate matching and bandwidth validation in the odu cross connection.",
        default=ClientSignalTypeEnum.NOT_APPLICABLE,
        alias="client-signal-type",
    )
    used_resources: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of used resources.",
        default=None,
        alias="used-resources",
    )
    odu_diagnostics: RestconfList[OduDiagnosticsItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Set of attributes associated with ODU diagnostics.Each direction has their own values.",
        default=None,
        alias="odu-diagnostics",
    )


class FecAbilityEnum(str, Enum):
    """Enumeration for FecAbilityEnum

    Values:
      * supported
      * not-supported
    """

    SUPPORTED = "supported"
    NOT_SUPPORTED = "not-supported"


class TimingModeEnum(str, Enum):
    """Enumeration for TimingModeEnum

    Values:
      * transparent: Transparent timing mode
      * retimed: Retimed timing mode
    """

    TRANSPARENT = "transparent"
    RETIMED = "retimed"


class UpiValueEnum(str, Enum):
    """Enumeration for UpiValueEnum

    Values:
      * not-applicable
      * g709
      * gsupp43
    """

    NOT_APPLICABLE = "not-applicable"
    G709 = "g709"
    GSUPP43 = "gsupp43"


class LldpModeEnum(str, Enum):
    """Enumeration for LldpModeEnum

    Values:
      * disabled
      * snoop
      * drop
      * snoop-and-drop
    """

    DISABLED = "disabled"
    SNOOP = "snoop"
    DROP = "drop"
    SNOOP_AND_DROP = "snoop-and-drop"


class EthernetItem(YangBaseModel):
    """Ethernet facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    client_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The protocol type of the Ethernet client.",
        default=None,
        alias="client-type",
    )
    service_mode: ServiceModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode for the ethernet facility.",
        default=ServiceModeEnum.TRANSPORT,
        alias="service-mode",
    )
    service_mode_qualifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode qualifier for the ethernet facility.",
        default="none",
        alias="service-mode-qualifier",
    )
    max_packet_length: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Maximum transfer unit for ethernet facility, in octets.",
        ge=1280,
        le=18000,
        default=1518,
        alias="max-packet-length",
    )
    speed: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The speed/rate of the Ethernet client interfaces.",
        default=None,
    )
    fec_ability: FecAbilityEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the Ethernet client's capability to support FEC (Forward Error Correction).",
        default=FecAbilityEnum.NOT_SUPPORTED,
        alias="fec-ability",
    )
    fec_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured FEC mode on the Ethernet client. Default is dependent on configured client type.",
        default=EnableSwitchEnum.DISABLED,
        alias="fec-mode",
    )
    tx_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The tx mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=None,
        alias="tx-mapping-mode",
    )
    expected_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=None,
        alias="expected-mapping-mode",
    )
    time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Time slots of the ethernet.",
        min_length=0,
        max_length=255,
        default=None,
        alias="time-slots",
    )
    line_port: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify the line port for the client. Can only be configured when mapping mode is openZR+.",
        default=None,
        alias="line-port",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )
    fec_degraded_ser_monitoring: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows to enable monitoring for FEC-DEGRADED-SER alarm.",
        default=EnableSwitchEnum.DISABLED,
        alias="fec-degraded-ser-monitoring",
    )
    fec_degraded_ser_activate_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="FEC-DEGRADED-SER alarm asserted if average SER, computed over accumulated\nFEC symbol errors in the monitoring period exceed this threshold.",
        ge=1e-10,
        le=0.0001,
        default=0.00001,
        alias="fec-degraded-ser-activate-threshold",
    )
    fec_degraded_ser_deactivate_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="FEC-DEGRADED-SER alarm cleared if average SER, computed over accumulated FEC\nsymbol errors in the monitoring period is below this threshold.",
        ge=8e-11,
        le=8e-05,
        default=0.000008,
        alias="fec-degraded-ser-deactivate-threshold",
    )
    fec_degraded_ser_monitoring_period: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitoring period duration over which FEC symbol errors are accumulated for asserting or clearing of FEC-DEGRADED-SER alarm.",
        ge=1,
        le=50,
        default=10,
        alias="fec-degraded-ser-monitoring-period",
    )
    timing_mode: TimingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The timing mode of the client.",
        default=TimingModeEnum.TRANSPARENT,
        alias="timing-mode",
    )
    test_signal_type: SignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of test pattern that is injected.",
        default=SignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: PrbsDirectionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The direction of the test signal.",
        default=PrbsDirectionEnum.EGRESS,
        alias="test-signal-direction",
    )
    test_signal_monitoring: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitor the incoming test signals for diagnostics.",
        default=False,
        alias="test-signal-monitoring",
    )
    transmit_inter_packet_gap: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The minimum transmit IPG(Inter-Packet Gap) value.",
        ge=8,
        le=12,
        default=8,
        alias="transmit-inter-packet-gap",
    )
    gfp_payload_fcs: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable/disable GFP payload FCS(Frame Check Sequence).",
        default=EnableSwitchEnum.DISABLED,
        alias="gfp-payload-fcs",
    )
    upi_value: UpiValueEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The value of UPI(User Payload Identifier) in GFP-F-extOPU2 mapping mode for 10GBE.",
        default=UpiValueEnum.G709,
        alias="upi-value",
    )
    lldp_admin_status: LldpAdminStatusEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="LLDP operational mode for this port.",
        default=LldpAdminStatusEnum.DISABLED,
        alias="lldp-admin-status",
    )
    lldp_ingress_mode: LldpModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="If lldp enabled, define what is the LLDP behavior for this direction.\n\nCondition (when): ../lldp-admin-status != 'disabled'",
        default=LldpModeEnum.DISABLED,
        alias="lldp-ingress-mode",
    )
    lldp_egress_mode: LldpModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="If lldp enabled, define what is the LLDP behavior for this direction.\n\nCondition (when): ../lldp-admin-status != 'disabled'",
        default=LldpModeEnum.DISABLED,
        alias="lldp-egress-mode",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class ServiceTypeEnum(str, Enum):
    """Enumeration for ServiceTypeEnum

    Values:
      * 100GBE
      * 400GBE
      * OTU4
      * 4x100GBE
      * OTU2
      * OTU2e
      * 1GBE
      * 10GBE
      * OC48
      * OC192
      * STM16
      * STM64
      * 4x10G
      * 4x10GBE
      * 2x100GBE
      * FC1G
      * FC4G
      * FC8G
      * FC16G
      * FC32G
      * FC2G
      * STM1
      * STM4
      * OC3
      * OC12
      * interlaken
      * 4x16G
      * 4x8G
      * 2x32G
      * 800GBE
      * 800GBE-ETC
      * 2xOTU4
      * 2x400GBE
      * not-applicable
    """

    _100GBE = "100GBE"
    _400GBE = "400GBE"
    OTU4 = "OTU4"
    _4X100GBE = "4x100GBE"
    OTU2 = "OTU2"
    OTU2E = "OTU2e"
    _1GBE = "1GBE"
    _10GBE = "10GBE"
    OC48 = "OC48"
    OC192 = "OC192"
    STM16 = "STM16"
    STM64 = "STM64"
    _4X10G = "4x10G"
    _4X10GBE = "4x10GBE"
    _2X100GBE = "2x100GBE"
    FC1G = "FC1G"
    FC4G = "FC4G"
    FC8G = "FC8G"
    FC16G = "FC16G"
    FC32G = "FC32G"
    FC2G = "FC2G"
    STM1 = "STM1"
    STM4 = "STM4"
    OC3 = "OC3"
    OC12 = "OC12"
    INTERLAKEN = "interlaken"
    _4X16G = "4x16G"
    _4X8G = "4x8G"
    _2X32G = "2x32G"
    _800GBE = "800GBE"
    _800GBE_ETC = "800GBE-ETC"
    _2XOTU4 = "2xOTU4"
    _2X400GBE = "2x400GBE"
    NOT_APPLICABLE = "not-applicable"


class DisableActionEnum(str, Enum):
    """Enumeration for DisableActionEnum

    Values:
      * laser-shut-off
      * send-idles
      * send-lf
      * send-ais-l
      * odu-ais
      * none
      * send-gais
      * send-ms-ais
      * e-code
      * send-nos
    """

    LASER_SHUT_OFF = "laser-shut-off"
    SEND_IDLES = "send-idles"
    SEND_LF = "send-lf"
    SEND_AIS_L = "send-ais-l"
    ODU_AIS = "odu-ais"
    NONE = "none"
    SEND_GAIS = "send-gais"
    SEND_MS_AIS = "send-ms-ais"
    E_CODE = "e-code"
    SEND_NOS = "send-nos"


class TribPtpItem(YangBaseModel):
    """Basic TribPTP facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    auto_in_service_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Auto-in-service switch for this facility.",
        default=False,
        alias="auto-in-service-enabled",
    )
    valid_signal_time: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable time that represents a detection of a valid signal.\nUsed for auto-in-service mechanism.",
        ge=0,
        le=7200,
        default=480,
        alias="valid-signal-time",
    )
    remaining_valid_signal_time: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual remaining time for this facility to be automatically enabled by the\nauto-in-service mechanism.",
        ge=0,
        le=7200,
        default=None,
        alias="remaining-valid-signal-time",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    service_type: ServiceTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The protocol type of the client that is being transported via the tributary optical transceiver module (TOM).",
        default=ServiceTypeEnum.NOT_APPLICABLE,
        alias="service-type",
    )
    tributary_disable_action: DisableActionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Tributary Disable Action (TDA) indicates what action the NE performs towards the client equipment\n(connected over the TOM) when a line-side failure is observed. This includes shutting off laser\nor inserting a appropriate replacement signal.",
        default=DisableActionEnum.LASER_SHUT_OFF,
        alias="tributary-disable-action",
    )
    tributary_disable_holdoff_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The hold off time of client shutdown or replacement signal at egress direction.\n0 means holdoff functionality disabled",
        ge=0,
        le=10000,
        default=0,
        alias="tributary-disable-holdoff-timer",
    )
    near_end_tda: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The switching of near end TDA.",
        default=EnableSwitchEnum.DISABLED,
        alias="near-end-tda",
    )
    tda_degrade_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The switching of defect BERSD-ODU trig ALS",
        default=EnableSwitchEnum.DISABLED,
        alias="tda-degrade-mode",
    )
    forward_defect_trigger: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Forward Defect TDA Trigger indicates on the egress, if NE receives a client forward defect\n(e.g., LF, ODU-AIS) whether to let it flow through towards the line side (network side) or\ntrigger an egress TDA action",
        default=True,
        alias="forward-defect-trigger",
    )
    egress_port_list: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of port AIDs that are bound to this trib-ptp for diverse-routing.",
        min_length=1,
        max_length=32,
        default=None,
        alias="egress-port-list",
    )
    power_threshold_low: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The default system threshold (known as 'Sensitivity') that triggers the OPR-OORL alarm\n(i.e., when the optical power received is below this value). Note that this is hardware dependent,\nbased on the type of the optical transceiver (TOM).",
        ge=-55.0,
        le=55.0,
        default=None,
        alias="power-threshold-low",
    )
    power_threshold_low_offset: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="A user configurable attribute that results in the 'effective lower threshold' based on which\nthe system raises the OPR-OORL alarm. The effective threshold will be (threshold-low + threshold-low-offset).",
        ge=-55.0,
        le=55.0,
        default=0.0,
        alias="power-threshold-low-offset",
    )
    power_threshold_high: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The default system threshold (known as 'Overload') that triggers the OPR-OORH alarm\n(i.e., when the optical power received is greater than this value). Note that this is\nhardware dependent, based on the type of the optical transceiver (TOM).",
        ge=-55.0,
        le=55.0,
        default=None,
        alias="power-threshold-high",
    )
    power_threshold_high_offset: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="A user configurable attribute that results in the 'effective upper threshold' based on\nwhich the system raises the OPR-OORH alarm. The effective threshold will be (threshold-high + threshold-high-offset).",
        ge=-55.0,
        le=55.0,
        default=0.0,
        alias="power-threshold-high-offset",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class TypeEnum_1(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * OFEC-CC: Control channel available due to GX's proprietry optical FEC overhead. The rate of OFEC-CC (in case of Gen6) is 17.6 Mbps for each 100G optical carrier capacity. For instance, in an 800G optical carrier, the OFEC-CC will be (8 x 17.6 = 140.8 Mbps).
      * GCC0: GCC0 bytes within OTUk overhead.
      * GCC1: GCC1 bytes within ODUk overhead.
      * OSCX1: OSCX1 bytes.
      * OSCX2: OSCX2 bytes.
      * OSCX3: OSCX3 connectivity.
      * OSCX4: OSCX4 connectivity.
      * OSCX5: OSCX5 for L1 Aux user-channel.
      * FCC1: FCC overhead.
      * FCC1-UC: FCC1-UC overhead.
      * 1GE-OSCX1: 1GE-OSCX1 connectivity.
      * 1GE-OSCX2: 1GE-OSCX2 connectivity.
    """

    OFEC_CC = "OFEC-CC"
    GCC0 = "GCC0"
    GCC1 = "GCC1"
    OSCX1 = "OSCX1"
    OSCX2 = "OSCX2"
    OSCX3 = "OSCX3"
    OSCX4 = "OSCX4"
    OSCX5 = "OSCX5"
    FCC1 = "FCC1"
    FCC1_UC = "FCC1-UC"
    _1GE_OSCX1 = "1GE-OSCX1"
    _1GE_OSCX2 = "1GE-OSCX2"


class FcsLengthEnum(str, Enum):
    """Enumeration for FcsLengthEnum

    Values:
      * 16
      * 32
    """

    _16 = "16"
    _32 = "32"


class CommChannelItem(YangBaseModel):
    """Communication Channel facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    type: TypeEnum_1 = Field(
        json_schema_extra={"is_config": True}, description="Indicates the type of control channel."
    )
    bandwidth: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the control channel's bandwidth/capacity.\nThis is system determined based on the underlying facilities that support this control channel.",
        default=None,
    )
    mtu: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The maximum transmission unit size in octets for comm channel.",
        ge=1280,
        le=9202,
        default=1500,
    )
    parent: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Parent object of the comm-channel.\n    Only of relevance when type is GCC0 or GCC1 or FCC1-UC.",
        default=None,
    )
    fcs_length: FcsLengthEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies whether the Frame Check Sequence(FCS) is a 16-bit or 32-bit value.",
        default=FcsLengthEnum._16,
        alias="fcs-length",
    )
    mru: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies the MRU(Maximum-Receive-Unit) in the Information and Padding fields.",
        ge=64,
        le=1500,
        default=1500,
    )
    restart_timer: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies the restart timer of the PPP protocol in seconds.",
        ge=1,
        le=10,
        default=3,
        alias="restart-timer",
    )
    max_failure: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies the maximum failure value of the PPP protocol. Max-Failure\nindicates the number of Configure-Nak packets sent without sending\na Configure-Ack before assuming that configuration is not converging.\nAny further Configure-Nak packets for peer requested options are\nconverted to Configure-Reject packets, and locally desired options\nare no longer appended.",
        ge=2,
        le=10,
        default=5,
        alias="max-failure",
    )
    peer_address: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The IP address on the peer node.",
        default="0.0.0.0",
        alias="peer-address",
    )
    mode: ModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the mode of operation of control channel.",
        default=ModeEnum.L3,
    )


class CidPtpItem(YangBaseModel):
    """List of cid-ptp facilities."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    used: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="It is true when CableID functionality is supported.",
        default=False,
    )


class PtpTypeEnum(str, Enum):
    """Enumeration for PtpTypeEnum

    Values:
      * dwdm-line: DWDM line PTP
      * dwdm: System side DWDM, or other filter DWDM PTP
      * osc: OSC PTP
      * sposc: SPOSC PTP
      * ade: ADE: Add/ Drop or Express PTP
      * ad: ADE: Add/ Drop PTP (no express option)
      * fac: BAX Facility port PTP
      * ase-idler: ASE Idler PTP
    """

    DWDM_LINE = "dwdm-line"
    DWDM = "dwdm"
    OSC = "osc"
    SPOSC = "sposc"
    ADE = "ade"
    AD = "ad"
    FAC = "fac"
    ASE_IDLER = "ase-idler"


class ActualPowerSupportEnum(str, Enum):
    """Enumeration for ActualPowerSupportEnum

    Values:
      * not-applicable: Not available or not applicable.
      * power-rx-tx: Power actual Rx and Tx.
      * power-rx: Power actual Rx only.
      * ocm: OCM dependent power actual.
      * power-tx: Power actual Tx only.
    """

    NOT_APPLICABLE = "not-applicable"
    POWER_RX_TX = "power-rx-tx"
    POWER_RX = "power-rx"
    OCM = "ocm"
    POWER_TX = "power-tx"


class BandRequiredEnum(str, Enum):
    """Enumeration for BandRequiredEnum

    Values:
      * not-applicable: Required tranmission band(s) not applicable.
      * standardC-band: Required transmission band StandardC-band (4.85 THz or HSC OLS StandardC-band).
      * superC-band: Required tranmission band SuperC-band (6.1 THz).
      * standardL-band: Required tranmission band StandardL-band (HSC OLS).
      * standardC-standardL-bands: StandardC-band (HSC OLS standardC-band) and StandardL-band for HSC OLS.
    """

    NOT_APPLICABLE = "not-applicable"
    STANDARDC_BAND = "standardC-band"
    SUPERC_BAND = "superC-band"
    STANDARDL_BAND = "standardL-band"
    STANDARDC_STANDARDL_BANDS = "standardC-standardL-bands"


class OpticalPtpItem(YangBaseModel):
    """List of Optical PTP facilities."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    ptp_type: PtpTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Type of Optical PTP.", default=None, alias="ptp-type"
    )
    port_direction_convention: str | None = Field(
        json_schema_extra={"is_config": False},
        description="IOA port (PTP) direction convention.\n\nCondition (when): /ne/node-type='ILA'",
        min_length=3,
        max_length=6,
        default=None,
        alias="port-direction-convention",
    )
    laser_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The emitting pump (e.g. booster) laser state.\nRD amplifiers: source (Tx) pump disabled.\nRPB: Pump Laser, and actual traffic emitted from dwdm-line port: sink or source.\nOnly of relevance for DWDM line ports.",
        default=None,
        alias="laser-state",
    )
    ase_source_connected: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether PTP is connected from an ASE Idler (connection from 'Out') or not.",
        default=False,
        alias="ase-source-connected",
    )
    actual_power_support: ActualPowerSupportEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Port power monitoring support.",
        default=ActualPowerSupportEnum.NOT_APPLICABLE,
        alias="actual-power-support",
    )
    power_actual_rx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical power received, where applicable.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-rx",
    )
    power_actual_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical power transmitted, where applicable.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-tx",
    )
    fix_rx_attenuation: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Fixed Attenuator before port Rx. 0 (dB) is equivalent to no fixed attenuator.",
        ge=0,
        le=30,
        default=None,
        alias="fix-rx-attenuation",
    )
    monitoring_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="System reports this attribute, to indicate whether the optical-ptp is intended\nto be in use (instead of simply being pre-provisioned);\nwhen optical-ptp is created the the monitoring-state need to be calculated:\n- 'disabled' for a combination of card/ptp-type\n- 'enabled' in all other cases.",
        default=EnableSwitchEnum.ENABLED,
        alias="monitoring-state",
    )
    band_required: BandRequiredEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Required Transmission Band(s) for the DWDM-line port.",
        default=None,
        alias="band-required",
    )
    bands_supported: RestconfList[TransmissionBandEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of bands supported by a card's port.\n\nCondition (when): ../ptp-type = 'dwdm-line' or ../ptp-type = 'dwdm' or ../ptp-type = 'ad' or ../ptp-type = 'ade'",
        default=None,
        alias="bands-supported",
    )


class MonitoredChannelItem(YangBaseModel):
    """List of detected carriers within the configured oxcon(s)."""

    frequency: int = Field(
        json_schema_extra={"is_config": False}, description="Nominal Center Frequency of the carrier (channel).", ge=0
    )
    monitored_optical_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Measured power for the corresponding carrier (channel).",
        ge=-99.0,
        le=99.0,
        default=-99,
        alias="monitored-optical-power",
    )
    monitored_width: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Carrier (channel) width configured at the NMC within the oxcon source/destination; 0 stands for no valid carrier now.",
        ge=0,
        default=0,
        alias="monitored-width",
    )


class OcmPtpItem(YangBaseModel):
    """List of OCM PTPs."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    ocm_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables regular power monitoring.",
        default=EnableSwitchEnum.DISABLED,
        alias="ocm-enable",
    )
    ad_direction: DirectionEnum_2 | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference to the AD (coupler/ splitter) DWDM port.",
        default=DirectionEnum_2.INGRESS,
        alias="ad-direction",
    )
    last_measurement: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Last OCM scan measurement.",
        default="never",
        alias="last-measurement",
    )
    adg_number: int | None = Field(
        json_schema_extra={"is_config": False},
        description="ADG reference.",
        ge=0,
        le=110,
        default=0,
        alias="adg-number",
    )
    monitoring_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="System reports 'enabled' when complete connectivity at AD is established, and OCM measurement is possible.",
        default=EnableSwitchEnum.DISABLED,
        alias="monitoring-state",
    )
    monitored_channel: RestconfList[MonitoredChannelItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of detected carriers within the configured oxcon(s).",
        default=None,
        alias="monitored-channel",
    )


class OcmChannelItem(YangBaseModel):
    """List of detected carriers within the configured oxcon(s)."""

    lower_frequency: int = Field(
        json_schema_extra={"is_config": False},
        description="Lower frequency of the corresponding spectrum power (OPM-pwr point).",
        ge=0,
        alias="lower-frequency",
    )
    upper_frequency: int = Field(
        json_schema_extra={"is_config": False},
        description="Upper frequency of the corresponding spectrum power (OPM-pwr point).",
        ge=0,
        alias="upper-frequency",
    )
    opm_pwr: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Parameter Monitor - power.",
        ge=-99.0,
        le=99.0,
        default=-99,
        alias="opm-pwr",
    )
    connected: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Yields 'true' if the channel is configured (involved in an oxcon).",
        default=False,
    )


class OcmMpItem(YangBaseModel):
    """List of OCM Monitoring Points - monitored channels OPM Powers."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    ocm_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables regular power monitoring.",
        default=EnableSwitchEnum.ENABLED,
        alias="ocm-enable",
    )
    monitored_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The port that is being monitored.\nCan be different of supporting-port for a non-integrated OCM.",
        default="not-applicable",
        alias="monitored-port",
    )
    ad_direction: DirectionEnum_2 | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference to the AD (coupler/ splitter) DWDM port.",
        default=DirectionEnum_2.INGRESS,
        alias="ad-direction",
    )
    monitoring_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="System reports 'enabled' when OMS reference exists.",
        default=EnableSwitchEnum.ENABLED,
        alias="monitoring-state",
    )
    ocm_channel: RestconfList[OcmChannelItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of detected carriers within the configured oxcon(s).",
        default=None,
        alias="ocm-channel",
    )


class OtdrMeasurementSpeedEnum(str, Enum):
    """Enumeration for OtdrMeasurementSpeedEnum

    Values:
      * fast: Approximate acquisition time: 1 second.
      * medium: Approximate acquisition time: 15 seconds.
      * slow: Approximate acquisition time: 1 minute.
      * precision: Approximate acquisition time: 3..5 minutes.
      * auto: Indicates that the measurement speed shall be selected automatically.
      * high-precision: Approximate acquisition time: 5..7 minutes.
    """

    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    PRECISION = "precision"
    AUTO = "auto"
    HIGH_PRECISION = "high-precision"


class OtdrPtpItem(YangBaseModel):
    """Otdr-ptp container containing attrbutes suppoting OTDR ptp per port."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    otdr_range: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the distance range as a basis to calculate the measurement repetition period .",
        default="auto",
        alias="otdr-range",
    )
    otdr_pulse_width: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the OTDR pulse width. Pulse-width will decide dynamic range together with other OTDR measurement parameters.",
        default="auto",
        alias="otdr-pulse-width",
    )
    otdr_measurement_speed: OtdrMeasurementSpeedEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This parameter influences the acquisition time, by varying the number of single pulse measurements that are used to calculate an average measurement result.",
        default=OtdrMeasurementSpeedEnum.AUTO,
        alias="otdr-measurement-speed",
    )
    otdr_ior: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the group index of refraction (IOR) of the fiber to be measured by OTDR.",
        default="auto",
        alias="otdr-ior",
    )
    otdr_fiber_type: FiberTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the fiber type of the fiber to be measured by OTDR.In case the value is unknown,the evaluation software shall behave identical as for the value SSMF.",
        default=FiberTypeEnum.AUTO,
        alias="otdr-fiber-type",
    )
    otdr_resolution: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the OTDR data sampling resolution.",
        default="auto",
        alias="otdr-resolution",
    )
    otdr_last_measurement: (
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
        description="otdr-last-measurement in a date-time format (YYYY-MM-DDThh:mm:ssZ).",
        default="0000-01-01T00:00:00.00Z",
        alias="otdr-last-measurement",
    )
    otdr_last_measurement_file: str | None = Field(
        json_schema_extra={"is_config": False},
        description="File name will display when the measurement ends with success.",
        min_length=0,
        max_length=100,
        default=None,
        alias="otdr-last-measurement-file",
    )
    otdr_fiber_break_distance: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="In case the OTDR has clearly identified a fiber break in the last measurement, this attribute shall contain the distance of the fiber break.",
        default="not-available",
        alias="otdr-fiber-break-distance",
    )
    launching_fiber_length: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="Launching fibre length.",
        default="0",
        alias="launching-fiber-length",
    )


class ServiceTypeEnum_1(str, Enum):
    """Enumeration for ServiceTypeEnum

    Values:
      * not-applicable: No service mode.
      * DP-16QAM-200G: 200G rate class carrier signal with DP-16QAM modulation format.
      * DP-QPSK-100G: 100G rate class carrier signal with DP-QPSK modulation format.
      * DP-8QAM-200G: 200G rate class carrier signal with DP-8QAM modulation format.
      * DP-16QAM-100G: 200G rate class carrier signal with DP-16QAM modulation format.
      * DP-16QAM-100G-EX: 200G rate class carrier signal with DP-16QAM modulation format.
      * DP-16QAM-400G: 400G rate class carrier signal with DP-16QAM modulation format.
      * DP-8QAM-300G: 300G rate class carrier signal with DP-8QAM modulation format.
      * DP-QPSK-200G: 200G rate class carrier signal with DP-QPSK modulation format.
      * OTU2: ITUT G.709 10.70 gigabits per second Optical channel Transport Unit.
      * OTU2e: ITUT G.709 11.09 gigabits per second Optical channel Transport Unit.
      * DP-16QAM-E-400G: 400G rate class E signal with DP-16QAM-E modulation format.
      * DP-16QAM-400G-OpenZR+: 400G rate class OpenZR+ signal with DP-16QAM modulation format.
      * DP-16QAM-PS-400G: 400G rate class PS mode signal with DP-16QAM-PS modulation format.
      * DP-16QAM-200G-EX
      * DP-QPSK-100G-EX
      * DP-16QAM-400G-EX
      * DP-8QAM-300G-EX
      * DP-QPSK-200G-EX
      * DP-SPQPSK-100G: 100G rate class carrier signal with DP-SPQPSK modulation format.
      * DP-SPQPSK-QPSK-100G: 100G rate class carrier signal with DP-SPQPSK-QPSK modulation format.
      * DP-SP16QAM-200G: 200G rate class carrier signal with DP-SP16QAM modulation format.
      * DP-32QAM-200G: 200G rate class carrier signal with DP-32QAM modulation format.
      * DP-SP16QAM-16QAM-200G: 200G rate class carrier signal with DP-SP16QAM-16QAM modulation format.
      * DP-QPSK-SP16QAM-200G: 200G rate class carrier signal with DP-QPSK-SP16QAM modulation format.
      * DP-SPQPSK-QPSK-200G: 200G rate class carrier signal with DP-SPQPSK-QPSK modulation format.
      * DP-16QAM-300G: 300G rate class carrier signal with DP-16QAM modulation format.
      * DP-SP16QAM-300G: 300G rate class carrier signal with DP-SP16QAM modulation format.
      * DP-32QAM-300G: 300G rate class carrier signal with DP-32QAM modulation format.
      * DP-64QAM-300G: 300G rate class carrier signal with DP-64QAM modulation format.
      * DP-32QAM-64QAM-300G: 300G rate class carrier signal with DP-32QAM-64QAM modulation format.
      * DP-SP16QAM-16QAM-300G: 300G rate class carrier signal with DP-SP16QAM-16QAM modulation format.
      * DP-QPSK-SP16QAM-300G: 300G rate class carrier signal with DP-QPSK-SP16QAM modulation format.
      * DP-32QAM-400G: 400G rate class carrier signal with DP-32QAM modulation format.
      * DP-64QAM-400G: 400G rate class carrier signal with DP-64QAM modulation format.
      * DP-16QAM-32QAM-400G: 400G rate class carrier signal with DP-16QAM-32QAM modulation format.
      * DP-SP16QAM-16QAM-400G: 400G rate class carrier signal with DP-SP16QAM-16QAM modulation format.
      * DP-32QAM-500G: 500G rate class carrier signal with DP-32QAM modulation format.
      * DP-64QAM-500G: 500G rate class carrier signal with DP-64QAM modulation format.
      * DP-32QAM-64QAM-500G: 500G rate class carrier signal with DP-32QAM-64QAM modulation format.
      * DP-16QAM-32QAM-500G: 500G rate class carrier signal with DP-16QAM-32QAM modulation format.
      * DP-64QAM-600G: 600G rate class carrier signal with DP-64QAM modulation format.
      * DP-32QAM-64QAM-600G: 600G rate class carrier signal with DP-32QAM-64QAM modulation format.
      * DP-SP16QAM-300G-C: couple 2*150G rate class carrier signal with DP-SP16QAM modulation format.
      * DP-QPSK-SP16QAM-300G-C: couple 2*150G rate class carrier signal with DP-QPSK-SP16QAM modulation format.
      * DP-16QAM-32QAM-500G-C: couple 2*250G rate class carrier signal with DP-16QAM-32QAM modulation format.
      * DP-16QAM-500G-C: couple 2*250G rate class carrier signal with DP-16QAM modulation format.
      * DP-SP16QAM-500G-C: couple 2*250G rate class carrier signal with DP-SP16QAM modulation format.
      * DP-QPSK-SP16QAM-500G-C: couple 2*250G rate class carrier signal with DP-QPSK-SP16QAM modulation format.
      * DP-32QAM-64QAM-700G-C: couple 2*350G rate class carrier signal with DP-32QAM-64QAM modulation format.
      * DP-16QAM-700G-C: couple 2*350G rate class carrier signal with DP-16QAM modulation format.
      * DP-SP16QAM-16QAM-700G-C: couple 2*350G rate class carrier signal with DP-SP16QAM-16QAM modulation format.
      * DP-32QAM-900G-C: couple 2*450G rate class carrier signal with DP-32QAM modulation format.
      * DP-16QAM-32QAM-900G-C: couple 2*450G rate class carrier signal with DP-16QAM-32QAM modulation format.
      * DP-32QAM-64QAM-1100G-C: couple 2*550G rate class carrier signal with DP-32QAM-64QAM modulation format.
      * ICE7-LINE: ICE7 carrier-level-mode.
    """

    NOT_APPLICABLE = "not-applicable"
    DP_16QAM_200G = "DP-16QAM-200G"
    DP_QPSK_100G = "DP-QPSK-100G"
    DP_8QAM_200G = "DP-8QAM-200G"
    DP_16QAM_100G = "DP-16QAM-100G"
    DP_16QAM_100G_EX = "DP-16QAM-100G-EX"
    DP_16QAM_400G = "DP-16QAM-400G"
    DP_8QAM_300G = "DP-8QAM-300G"
    DP_QPSK_200G = "DP-QPSK-200G"
    OTU2 = "OTU2"
    OTU2E = "OTU2e"
    DP_16QAM_E_400G = "DP-16QAM-E-400G"
    DP_16QAM_400G_OPENZR_PLUS = "DP-16QAM-400G-OpenZR+"
    DP_16QAM_PS_400G = "DP-16QAM-PS-400G"
    DP_16QAM_200G_EX = "DP-16QAM-200G-EX"
    DP_QPSK_100G_EX = "DP-QPSK-100G-EX"
    DP_16QAM_400G_EX = "DP-16QAM-400G-EX"
    DP_8QAM_300G_EX = "DP-8QAM-300G-EX"
    DP_QPSK_200G_EX = "DP-QPSK-200G-EX"
    DP_SPQPSK_100G = "DP-SPQPSK-100G"
    DP_SPQPSK_QPSK_100G = "DP-SPQPSK-QPSK-100G"
    DP_SP16QAM_200G = "DP-SP16QAM-200G"
    DP_32QAM_200G = "DP-32QAM-200G"
    DP_SP16QAM_16QAM_200G = "DP-SP16QAM-16QAM-200G"
    DP_QPSK_SP16QAM_200G = "DP-QPSK-SP16QAM-200G"
    DP_SPQPSK_QPSK_200G = "DP-SPQPSK-QPSK-200G"
    DP_16QAM_300G = "DP-16QAM-300G"
    DP_SP16QAM_300G = "DP-SP16QAM-300G"
    DP_32QAM_300G = "DP-32QAM-300G"
    DP_64QAM_300G = "DP-64QAM-300G"
    DP_32QAM_64QAM_300G = "DP-32QAM-64QAM-300G"
    DP_SP16QAM_16QAM_300G = "DP-SP16QAM-16QAM-300G"
    DP_QPSK_SP16QAM_300G = "DP-QPSK-SP16QAM-300G"
    DP_32QAM_400G = "DP-32QAM-400G"
    DP_64QAM_400G = "DP-64QAM-400G"
    DP_16QAM_32QAM_400G = "DP-16QAM-32QAM-400G"
    DP_SP16QAM_16QAM_400G = "DP-SP16QAM-16QAM-400G"
    DP_32QAM_500G = "DP-32QAM-500G"
    DP_64QAM_500G = "DP-64QAM-500G"
    DP_32QAM_64QAM_500G = "DP-32QAM-64QAM-500G"
    DP_16QAM_32QAM_500G = "DP-16QAM-32QAM-500G"
    DP_64QAM_600G = "DP-64QAM-600G"
    DP_32QAM_64QAM_600G = "DP-32QAM-64QAM-600G"
    DP_SP16QAM_300G_C = "DP-SP16QAM-300G-C"
    DP_QPSK_SP16QAM_300G_C = "DP-QPSK-SP16QAM-300G-C"
    DP_16QAM_32QAM_500G_C = "DP-16QAM-32QAM-500G-C"
    DP_16QAM_500G_C = "DP-16QAM-500G-C"
    DP_SP16QAM_500G_C = "DP-SP16QAM-500G-C"
    DP_QPSK_SP16QAM_500G_C = "DP-QPSK-SP16QAM-500G-C"
    DP_32QAM_64QAM_700G_C = "DP-32QAM-64QAM-700G-C"
    DP_16QAM_700G_C = "DP-16QAM-700G-C"
    DP_SP16QAM_16QAM_700G_C = "DP-SP16QAM-16QAM-700G-C"
    DP_32QAM_900G_C = "DP-32QAM-900G-C"
    DP_16QAM_32QAM_900G_C = "DP-16QAM-32QAM-900G-C"
    DP_32QAM_64QAM_1100G_C = "DP-32QAM-64QAM-1100G-C"
    ICE7_LINE = "ICE7-LINE"


class LinePtpItem(YangBaseModel):
    """Basic LinePTP facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    auto_in_service_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Auto-in-service switch for this facility.",
        default=False,
        alias="auto-in-service-enabled",
    )
    valid_signal_time: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable time that represents a detection of a valid signal.\nUsed for auto-in-service mechanism.",
        ge=0,
        le=7200,
        default=480,
        alias="valid-signal-time",
    )
    remaining_valid_signal_time: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual remaining time for this facility to be automatically enabled by the\nauto-in-service mechanism.",
        ge=0,
        le=7200,
        default=None,
        alias="remaining-valid-signal-time",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    service_type: ServiceTypeEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="service-type to provison line side service.",
        default=ServiceTypeEnum_1.NOT_APPLICABLE,
        alias="service-type",
    )
    line_system_mode: LineSystemModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the specific mode of power control configured\non the L1 transponder, and specifically, on this particular Line port within\nthe L1 transponder. The attribute indicates the L1 <-> L0 local power controls\nto adjust the Tx power from the L1 transponder towards the L0 line-system\ncard (such as a WSS or Mux or Amplifier).",
        default=LineSystemModeEnum.OPENWAVE,
        alias="line-system-mode",
    )
    available_resources: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of available resources.",
        default=None,
        alias="available-resources",
    )
    used_resources: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of used resources.",
        default=None,
        alias="used-resources",
    )
    power_threshold_low: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The default system threshold (known as 'Sensitivity') that triggers the OPR-OORL alarm\n(i.e., when the optical power received is below this value). Note that this is hardware dependent,\nbased on the type of the optical transceiver (TOM).",
        ge=-55.0,
        le=55.0,
        default=None,
        alias="power-threshold-low",
    )
    power_threshold_low_offset: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="A user configurable attribute that results in the 'effective lower threshold' based on which\nthe system raises the OPR-OORL alarm. The effective threshold will be (threshold-low + threshold-low-offset).",
        ge=-55.0,
        le=55.0,
        default=0.0,
        alias="power-threshold-low-offset",
    )
    power_threshold_high: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The default system threshold (known as 'Overload') that triggers the OPR-OORH alarm\n(i.e., when the optical power received is greater than this value). Note that this is\nhardware dependent, based on the type of the optical transceiver (TOM).",
        ge=-55.0,
        le=55.0,
        default=None,
        alias="power-threshold-high",
    )
    power_threshold_high_offset: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="A user configurable attribute that results in the 'effective upper threshold' based on\nwhich the system raises the OPR-OORH alarm. The effective threshold will be (threshold-high + threshold-high-offset).",
        ge=-55.0,
        le=55.0,
        default=0.0,
        alias="power-threshold-high-offset",
    )


class FoicTypeEnum(str, Enum):
    """Enumeration for FoicTypeEnum

    Values:
      * foic1.2
      * foic1.4
      * foic2.4
      * foic2.8
      * foic3.6
      * foic4.8
      * foic4.16
      * foic1.1: 100G with 1 members of 100G
      * foic2.2: 200G with 2 members of 100G
      * foic3.3: 300G with 3 members of 100G
      * foic4.4: 400G with 4 members of 100G
      * foic5.5: 500G with 5 members of 100G
      * foic6.6: 600G with 6 members of 100G
      * foic7.7: 700G with 7 members of 100G
      * foic8.8: 800G with 8 members of 100G
      * foic9.9: 900G with 9 members of 100G
      * foic10.10: 1000G with 10 members of 100G
      * foic11.11: 1100G with 11 members of 100G
      * foic12.12: 1200G with 12 members of 100G
    """

    FOIC1_2 = "foic1.2"
    FOIC1_4 = "foic1.4"
    FOIC2_4 = "foic2.4"
    FOIC2_8 = "foic2.8"
    FOIC3_6 = "foic3.6"
    FOIC4_8 = "foic4.8"
    FOIC4_16 = "foic4.16"
    FOIC1_1 = "foic1.1"
    FOIC2_2 = "foic2.2"
    FOIC3_3 = "foic3.3"
    FOIC4_4 = "foic4.4"
    FOIC5_5 = "foic5.5"
    FOIC6_6 = "foic6.6"
    FOIC7_7 = "foic7.7"
    FOIC8_8 = "foic8.8"
    FOIC9_9 = "foic9.9"
    FOIC10_10 = "foic10.10"
    FOIC11_11 = "foic11.11"
    FOIC12_12 = "foic12.12"


class FlexoItem(YangBaseModel):
    """Facility describing the flexo. Refer to G.709.1 and G.709.3"""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    foic_type: FoicTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="FOICx.k lanes means using k parallel lanes to carry a FlexO-x interface, where order x signifies the interface rate in units of 100G.\nA unique FOICx.k identification (G.709.3 FlexO-LR and G.709.1 FlexO-SR).",
        default=FoicTypeEnum.FOIC4_8,
        alias="foic-type",
    )
    fec_type: FecTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="The FEC type", default=FecTypeEnum.OFEC, alias="fec-type"
    )
    iid: RestconfList[Annotated[int, Field(ge=1), Field(le=254)]] | None = Field(
        json_schema_extra={"is_config": True},
        description="Uniquely identify each member of a group and the order of each member in the group.\nThis information is required in the reordering process.\nDon’t need to be sequential.",
        default=None,
    )
    accepted_group_id: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received group instance on the FlexO interface.",
        default=None,
        alias="accepted-group-id",
    )
    accepted_iid: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": False},
        description="The received iid on the FlexO interface.",
        default=None,
        alias="accepted-iid",
    )


class FlexoTypeEnum(str, Enum):
    """Enumeration for FlexoTypeEnum

    Values:
      * enh-zr: Proprietary enhanced-zr framing.
    """

    ENH_ZR = "enh-zr"


class TimeSlotGranularityEnum(str, Enum):
    """Enumeration for TimeSlotGranularityEnum

    Values:
      * 100G: Time slot granularity. For example, 1200Gbps line capacity = 12x100Gbps time slots.
    """

    _100G = "100G"


class FlexoGroupItem(YangBaseModel):
    """Facility describing the flexo-group."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    carriers: RestconfList[str] = Field(
        json_schema_extra={"is_config": True},
        description="A list of carriers that are bound to this facilities.\nPossible values can be any card/resources/supported-carriers.",
        min_length=1,
        max_length=32,
    )
    rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": True}, description="Carried signal basic rate class", default=None
    )
    modulation_format: ModulationFormatEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Current modulation format",
        default=None,
        alias="modulation-format",
    )
    fec_type: FecTypeEnum | None = Field(
        json_schema_extra={"is_config": True}, description="The FEC type", default=FecTypeEnum.OFEC, alias="fec-type"
    )
    group_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="20bits, indicate the interface group instance\nthat the FlexO-x interface is a member of.\nIt will be unique in the NE",
        ge=1,
        le=1048575,
        default=None,
        alias="group-id",
    )
    expected_gid: int | None = Field(
        json_schema_extra={"is_config": True},
        description="If the expected-gid > 0 then the system shall\ncompare accepted-gid and expected-gid",
        ge=0,
        le=1048575,
        default=0,
        alias="expected-gid",
    )
    flexo_type: FlexoTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of standard or proprietary flexo format the facilities conforms to.",
        default=FlexoTypeEnum.ENH_ZR,
        alias="flexo-type",
    )
    total_time_slots: int | None = Field(
        json_schema_extra={"is_config": False}, description="TBD.", ge=0, default=None, alias="total-time-slots"
    )
    available_time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="The available time slots in the FlexO Group.",
        min_length=0,
        max_length=255,
        default=None,
        alias="available-time-slots",
    )
    time_slot_granularity: TimeSlotGranularityEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="TBD.",
        default=TimeSlotGranularityEnum._100G,
        alias="time-slot-granularity",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )


class DscItem(YangBaseModel):
    """Facility describing the dsc. Refer to G.709.1 and G.709.3"""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )


class DscGroupItem(YangBaseModel):
    """Facility describing the dsc-group."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    carriers: str = Field(
        json_schema_extra={"is_config": True},
        description="The carrier associated to this facility.\nPossible values can be any card/resources/supported-carriers.",
        min_length=1,
        max_length=32,
    )
    rate: Decimal64 = Field(json_schema_extra={"is_config": True}, description="Carried signal basic rate class")
    instance_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="For identifying the dsc-group logic number, is added to the dsc-group model for creation.\nThe attribute is optional and will be automatically created if not specified.\nThe maximum value of the instance-id will be calculated based on the capacity of the line mode and the dsc-group rate\n(ex: for creating an 100G dsc-group from 400G 16QAM line mode, instance can be between 1 and 4)",
        ge=1,
        default=None,
        alias="instance-id",
    )
    group_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Optional parameter on dsc-group creation, specifies the dsc-group group number that the dsc is a member of for a given optical-carrier.\nIf not provided, it is automatically assigned by system.\n(ex: for creating an 100G dsc-group from 400G 16QAM line mode, group-id can be 1/3/5/7)",
        ge=1,
        default=None,
        alias="group-id",
    )
    pre_fec_q_sig_deg_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold based on which the PRE-FEC-Q-SIGNAL-DEGRADE alarm is raised.\n0 implies threshold crossing alarming disabled.\nSpecific sub-range is per carrier use-case.",
        le=9.6,
        default=None,
        alias="pre-fec-q-sig-deg-threshold",
    )
    pre_fec_q_sig_deg_hysteresis: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Hysteresis to account for raising of the PRE-FEC-Q-SIGNAL-DEGRADE alarm.",
        ge=0.1,
        le=1.0,
        default=0.5,
        alias="pre-fec-q-sig-deg-hysteresis",
    )
    post_fec_q_sig_deg_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold based on which the POST-FEC-Q-SIGNAL-DEGRADE alarm is raised.",
        ge=12.5,
        le=18.0,
        default=18.0,
        alias="post-fec-q-sig-deg-threshold",
    )
    post_fec_q_sig_deg_hysteresis: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Hysteresis to account for raising of the POST-FEC-Q-SIGNAL-DEGRADE alarm.",
        ge=0.1,
        le=1.0,
        default=0.5,
        alias="post-fec-q-sig-deg-hysteresis",
    )
    dgd_high_threshold: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold to raise the DGD-OORH alarm.",
        ge=25,
        le=400,
        default=100,
        alias="dgd-high-threshold",
    )


class InterfaceTypeEnum(str, Enum):
    """Enumeration for InterfaceTypeEnum

    Values:
      * 400ZR: Media-interface 400ZR-CFEC-DP-16QAM
    """

    _400ZR = "400ZR"


class LinkDegradeIndicationEnum(str, Enum):
    """Enumeration for LinkDegradeIndicationEnum

    Values:
      * none: No Link degradation
      * local-degraded: Link has local degradation
      * remote-degraded: Link has remote degradation
      * local-and-remote-degraded: Link has local and remote degradation
    """

    NONE = "none"
    LOCAL_DEGRADED = "local-degraded"
    REMOTE_DEGRADED = "remote-degraded"
    LOCAL_AND_REMOTE_DEGRADED = "local-and-remote-degraded"


class EthZrItem(YangBaseModel):
    """Facility describing the Eth-ZR."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    carriers: RestconfList[str] = Field(
        json_schema_extra={"is_config": True},
        description="A list of carriers that are bound to this facilities.\nPossible values can be any card/resources/supported-carriers.",
        min_length=1,
        max_length=32,
    )
    interface_type: InterfaceTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Interface type of ZR tom.",
        default=InterfaceTypeEnum._400ZR,
        alias="interface-type",
    )
    rate: Decimal64 = Field(json_schema_extra={"is_config": True}, description="Carried signal basic rate class")
    modulation_format: ModulationFormatEnum = Field(
        json_schema_extra={"is_config": True}, description="Current modulation format", alias="modulation-format"
    )
    fec_type: FecTypeEnum | None = Field(
        json_schema_extra={"is_config": True}, description="The FEC type", default=FecTypeEnum.OFEC, alias="fec-type"
    )
    total_time_slots: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The member of the slots to be supported as times of 100G: rate-class/100.",
        ge=0,
        default=None,
        alias="total-time-slots",
    )
    available_time_slots: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="A list of time-slots that are available for provisioning new services.",
        min_length=0,
        max_length=255,
        default=None,
        alias="available-time-slots",
    )
    fdd_monitoring: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured FEC Detected Degrade (FDD) monitoring mode.",
        default=EnableSwitchEnum.DISABLED,
        alias="fdd-monitoring",
    )
    fdd_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold for FEC Detected Degrade (FDD) alarm.",
        ge=1e-09,
        le=0.1,
        default=0.0195,
        alias="fdd-threshold",
    )
    fdd_clear_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold for FEC Detected Degrade (FDD) alarm clear.",
        ge=1e-09,
        le=0.1,
        default=0.01062,
        alias="fdd-clear-threshold",
    )
    fed_monitoring: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured FEC Excessive Degrade (FED) monitoring mode.",
        default=EnableSwitchEnum.DISABLED,
        alias="fed-monitoring",
    )
    fed_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold for FEC Excessive Degrade.",
        ge=1e-09,
        le=0.1,
        default=0.0206,
        alias="fed-threshold",
    )
    fed_clear_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold for FEC Excessive Degrade (FED) alarm clear.",
        ge=1e-09,
        le=0.1,
        default=0.01125,
        alias="fed-clear-threshold",
    )
    link_degrade_indication: LinkDegradeIndicationEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The local and remote link degradation status.",
        default=LinkDegradeIndicationEnum.NONE,
        alias="link-degrade-indication",
    )
    loopback_host_interface: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback on host interface. Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
        alias="loopback-host-interface",
    )
    loopback_modem_interface: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback on modem interface. Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
        alias="loopback-modem-interface",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class OcTypeEnum(str, Enum):
    """Enumeration for OcTypeEnum

    Values:
      * OC-48
      * OC-192
      * OC-3
      * OC-12
    """

    OC_48 = "OC-48"
    OC_192 = "OC-192"
    OC_3 = "OC-3"
    OC_12 = "OC-12"


class TtiStyleEnum_1(str, Enum):
    """Enumeration for TtiStyleEnum

    Values:
      * 1: Single-byte trace (used for section access point identifiers with repetitive byte).
      * 15: 16-byte trace (used for section access point identifiers acc. to ITU-T G.831, cl. 3) with the first byte representing the CRC-7, which is auto-calculated, and 15 bytes to be configured.
    """

    _1 = "1"
    _15 = "15"


class OcItem(YangBaseModel):
    """Optical Carrier - level M, e.g. M=48, 192."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    oc_type: OcTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of SONET signal.\nLevel N of OC-N (Optical Carrier level N).",
        default=None,
        alias="oc-type",
    )
    speed: Decimal64 | None = Field(
        json_schema_extra={"is_config": False}, description="The speed of client interface.", default=None
    )
    tx_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The tx mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=MappingModeEnum.BMP,
        alias="tx-mapping-mode",
    )
    expected_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=MappingModeEnum.BMP,
        alias="expected-mapping-mode",
    )
    service_mode: ServiceModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode for the tdm facility.",
        default=ServiceModeEnum.NONE,
        alias="service-mode",
    )
    service_mode_qualifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode qualifier for the tdm facility.",
        default="none",
        alias="service-mode-qualifier",
    )
    tti_style: TtiStyleEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured mode of the TTI.",
        default=TtiStyleEnum_1._1,
        alias="tti-style",
    )
    tim_monitor: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The enable switching of tim defect monitor mode.",
        default=EnableSwitchEnum.DISABLED,
        alias="tim-monitor",
    )
    tx_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmit TTI - Sent by this facility to the far-end remote facility.",
        default=None,
        alias="tx-tti",
    )
    rx_tti: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="Receive TTI - Received by this facility from the far-end remote facility.",
        default=None,
        alias="rx-tti",
    )
    rx_tti_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False}, description="Receive TTI in HEX.", default=None, alias="rx-tti-hex"
    )
    expected_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Expected TTI - The TTI this facility expects to receive from the far-end remote facility.",
        default="",
        alias="expected-tti",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )
    test_signal_type: SignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of test pattern that is injected.",
        default=SignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: PrbsDirectionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The direction of the test signal.",
        default=PrbsDirectionEnum.EGRESS,
        alias="test-signal-direction",
    )
    test_signal_monitoring: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitor the incoming test signals for diagnostics.",
        default=False,
        alias="test-signal-monitoring",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class StmTypeEnum(str, Enum):
    """Enumeration for StmTypeEnum

    Values:
      * STM-16
      * STM-64
      * STM-1
      * STM-4
    """

    STM_16 = "STM-16"
    STM_64 = "STM-64"
    STM_1 = "STM-1"
    STM_4 = "STM-4"


class StmItem(YangBaseModel):
    """Synchronous Transport Module N, e.g. N=16, 64. Reference [ITU-T G.691]."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    stm_type: StmTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The type of SDH signal (STM-N).",
        default=None,
        alias="stm-type",
    )
    speed: Decimal64 | None = Field(
        json_schema_extra={"is_config": False}, description="The speed of client interface.", default=None
    )
    tx_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The tx mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=MappingModeEnum.BMP,
        alias="tx-mapping-mode",
    )
    expected_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=MappingModeEnum.BMP,
        alias="expected-mapping-mode",
    )
    service_mode: ServiceModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode for the tdm facility.",
        default=ServiceModeEnum.NONE,
        alias="service-mode",
    )
    service_mode_qualifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode qualifier for the tdm facility.",
        default="none",
        alias="service-mode-qualifier",
    )
    tti_style: TtiStyleEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured mode of the TTI.",
        default=TtiStyleEnum_1._1,
        alias="tti-style",
    )
    tim_monitor: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The enable switching of tim defect monitor mode.",
        default=EnableSwitchEnum.DISABLED,
        alias="tim-monitor",
    )
    tx_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Transmit TTI - Sent by this facility to the far-end remote facility.",
        default=None,
        alias="tx-tti",
    )
    rx_tti: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="Receive TTI - Received by this facility from the far-end remote facility.",
        default=None,
        alias="rx-tti",
    )
    rx_tti_hex: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x(([0-9A-Fa-f])([0-9A-Fa-f]))*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False}, description="Receive TTI in HEX.", default=None, alias="rx-tti-hex"
    )
    expected_tti: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Expected TTI - The TTI this facility expects to receive from the far-end remote facility.",
        default="",
        alias="expected-tti",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )
    test_signal_type: SignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of test pattern that is injected.",
        default=SignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: PrbsDirectionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The direction of the test signal.",
        default=PrbsDirectionEnum.EGRESS,
        alias="test-signal-direction",
    )
    test_signal_monitoring: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitor the incoming test signals for diagnostics.",
        default=False,
        alias="test-signal-monitoring",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class FcTypeEnum(str, Enum):
    """Enumeration for FcTypeEnum

    Values:
      * FC1G
      * FC4G
      * FC2G
      * FC8G
      * FC16G
      * FC32G
    """

    FC1G = "FC1G"
    FC4G = "FC4G"
    FC2G = "FC2G"
    FC8G = "FC8G"
    FC16G = "FC16G"
    FC32G = "FC32G"


class FcItem(YangBaseModel):
    """FC facility."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    fc_type: FcTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="The type of fc signal.", default=None, alias="fc-type"
    )
    service_mode: ServiceModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode for the fc facility.",
        default=ServiceModeEnum.TRANSPORT,
        alias="service-mode",
    )
    service_mode_qualifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Service mode qualifier for the fc facility.",
        default="none",
        alias="service-mode-qualifier",
    )
    speed: Decimal64 | None = Field(
        json_schema_extra={"is_config": False}, description="The speed/rate of the fc client interfaces.", default=None
    )
    tx_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The tx mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=None,
        alias="tx-mapping-mode",
    )
    expected_mapping_mode: MappingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The expected mapping mode of client port. The possible values are dependent on the HW and configuration.",
        default=None,
        alias="expected-mapping-mode",
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )
    loopback_mode: LoopbackModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates loopback action for facility or terminal.",
        default=None,
        alias="loopback-mode",
    )
    test_signal_type: SignalTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of test pattern that is injected.",
        default=SignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: PrbsDirectionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The direction of the test signal.",
        default=PrbsDirectionEnum.INGRESS,
        alias="test-signal-direction",
    )
    test_signal_monitoring: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitor the incoming test signals for diagnostics.",
        default=False,
        alias="test-signal-monitoring",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class InterlakenItem(YangBaseModel):
    """IOA YANG model describing the interlaken interface, which is used to monitor the interlaken connection
    between the paired slot on G30 via front DAC cable (not applicable to G30c). This would be attached to
    the TribPtps to manage the interlaken interface between the paired cards.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, configurable name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.SYSTEM,
        alias="managed-by",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    capacity: Decimal64 | None = Field(
        json_schema_extra={"is_config": False}, description="Total capacity for interlaken interface.", default=None
    )
    loopback: LoopbackEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Loopback mode.Useful to debug on the fiber connection.",
        default=LoopbackEnum.NONE,
    )


class McFItem(YangBaseModel):
    """MC-F: Media Channel Filler."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, Assigned name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    lower_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Lower Frequency of a Media Channel.",
        ge=0,
        default=None,
        alias="lower-frequency",
    )
    upper_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Upper Frequency of a Media Channel.",
        ge=0,
        default=None,
        alias="upper-frequency",
    )
    slot_width: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Slot width, as calculated by the system, from upper-frequency - lower-frequency.",
        ge=0,
        default=None,
        alias="slot-width",
    )


class NmcFItem(YangBaseModel):
    """NMC: Network Media Channel Filler (ASE) facility.
    A network media channel is a logical entity representing the optical signal carrying the service.
    The optical signal is also referred to as optical carrier.
    NM CFiller (ASE) is defined by its center frequency and width.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A generic, assigned name for every facility.",
        min_length=1,
        max_length=64,
    )
    supporting_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the parent facilities.",
        default=None,
        alias="supporting-facilities",
    )
    supported_facilities: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="An XPath reference to the children facilities.",
        default=None,
        alias="supported-facilities",
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this facility",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Ports that hold this facility",
        default=None,
        alias="supporting-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    alloc_lower_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Allocated Lower Frequency of the NMC Filler",
        ge=0,
        default=None,
        alias="alloc-lower-frequency",
    )
    alloc_upper_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Allocated Upper Frequency of the NMC Filler",
        ge=0,
        default=None,
        alias="alloc-upper-frequency",
    )
    alloc_bandwidth: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Allocated BandWdith of the NMC Filler",
        ge=0,
        default=75000,
        alias="alloc-bandwidth",
    )
    actual_lower_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual lower Frequency of the NMC Filler",
        ge=0,
        default=None,
        alias="actual-lower-frequency",
    )
    actual_upper_frequency: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual Upper Frequency of the NMC Filler",
        ge=0,
        default=None,
        alias="actual-upper-frequency",
    )
    actual_bandwidth: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual BandWdith of the NMC Filler",
        ge=0,
        default=0,
        alias="actual-bandwidth",
    )
    power_actual_tx: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Optical Power Transmitted, actual measurement.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-actual-tx",
    )


class Facilities(YangBaseModel):
    """The top-level facility root node under which all other facilities are present."""

    ots: RestconfList[OtsItem] | None = Field(
        json_schema_extra={"is_config": True}, description="OTS: Optical Transmission Section facility.", default=None
    )
    ots_r: RestconfList[OtsRItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="OTS: Optical Transmission Section facility.",
        default=None,
        alias="ots-r",
    )
    osc: RestconfList[OscItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Represents the Optical Supervision Channel (OSC) facility.",
        default=None,
    )
    ops: RestconfList[OpsItem] | None = Field(
        json_schema_extra={"is_config": True}, description="OPS: Optical Physical Section facility.", default=None
    )
    oms: RestconfList[OmsItem] | None = Field(
        json_schema_extra={"is_config": True}, description="OMS: Optical Multiplex Section facility.", default=None
    )
    spectrum: RestconfList[SpectrumItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="OMS specific equalization within interstage access; and monitoring.",
        default=None,
    )
    ochm: RestconfList[OchmItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="ochm: Optical Channel non-intrusive monitoring.\nECDP within OMS-nim.",
        default=None,
    )
    mc: RestconfList[McItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="MC: Media Channel.\nA media association that represents both the topology (i.e., the path throughthe media) and the resource (i.e., frequency slot or effective frequency slot) that it occupies.\nIn IOA, the frequency-slot is provided by the lower and upper-frequency.\nMedia Channel minimum width: 50 GHz.\nMedia Channel maximum width: 200 GHz.\nFor C-band: Start Frequency:191300000 MHz and End Frequency:196150000 MHz.",
        default=None,
    )
    nmc: RestconfList[NmcItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="NMC: Network Media Channel facility.\nA network media channel is a logical entity representing the optical signal carrying the service.\nThe optical signal is also referred to as optical carrier.\nNMC is defined by its center frequency and width.",
        default=None,
    )
    rsc: RestconfList[RscItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Raman Supervisory Channel: Raman card Pilot Tone facility.",
        default=None,
    )
    pump: RestconfList[PumpItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Raman Pump individual monitoring.", default=None
    )
    super_channel_group: RestconfList[SuperChannelGroupItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Super-channel Group facility.",
        default=None,
        alias="super-channel-group",
    )
    super_channel: RestconfList[SuperChannelItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Unified channel of optical carriers. Can have many optical channels.",
        default=None,
        alias="super-channel",
    )
    optical_carrier: RestconfList[OpticalCarrierItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Optical carrier facility.",
        default=None,
        alias="optical-carrier",
    )
    optical_channel: RestconfList[OpticalChannelItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="The OCh is a dummy, place-holder object merely\nexisting for the purposes of object model hierarchy. All\nattributes of OCh are marked as read-only.",
        default=None,
        alias="optical-channel",
    )
    otu: RestconfList[OtuItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Facility describing the OTUCn/OTUk according with standard ITU-T G.709.",
        default=None,
    )
    odu: RestconfList[OduItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="ODUCni/ODUki facility, representing both line side and client side ODUs.\nRepresents both GX proprietary line-side ODUki/ODUCni protocol, as well as ITU standard ODUk/OCUCn protocol\nRepresents both high order and low order ODUs.",
        default=None,
    )
    ethernet: RestconfList[EthernetItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Ethernet facility.", default=None
    )
    trib_ptp: RestconfList[TribPtpItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Basic TribPTP facility.", default=None, alias="trib-ptp"
    )
    comm_channel: RestconfList[CommChannelItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Communication Channel facility.",
        default=None,
        alias="comm-channel",
    )
    cid_ptp: RestconfList[CidPtpItem] | None = Field(
        json_schema_extra={"is_config": True}, description="List of cid-ptp facilities.", default=None, alias="cid-ptp"
    )
    optical_ptp: RestconfList[OpticalPtpItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of Optical PTP facilities.",
        default=None,
        alias="optical-ptp",
    )
    ocm_ptp: RestconfList[OcmPtpItem] | None = Field(
        json_schema_extra={"is_config": True}, description="List of OCM PTPs.", default=None, alias="ocm-ptp"
    )
    ocm_mp: RestconfList[OcmMpItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of OCM Monitoring Points - monitored channels OPM Powers.",
        default=None,
        alias="ocm-mp",
    )
    otdr_ptp: RestconfList[OtdrPtpItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Otdr-ptp container containing attrbutes suppoting OTDR ptp per port.",
        default=None,
        alias="otdr-ptp",
    )
    line_ptp: RestconfList[LinePtpItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Basic LinePTP facility.", default=None, alias="line-ptp"
    )
    flexo: RestconfList[FlexoItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Facility describing the flexo. Refer to G.709.1 and G.709.3",
        default=None,
    )
    flexo_group: RestconfList[FlexoGroupItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Facility describing the flexo-group.",
        default=None,
        alias="flexo-group",
    )
    dsc: RestconfList[DscItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Facility describing the dsc. Refer to G.709.1 and G.709.3",
        default=None,
    )
    dsc_group: RestconfList[DscGroupItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Facility describing the dsc-group.",
        default=None,
        alias="dsc-group",
    )
    eth_zr: RestconfList[EthZrItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Facility describing the Eth-ZR.",
        default=None,
        alias="eth-zr",
    )
    oc: RestconfList[OcItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Optical Carrier - level M, e.g. M=48, 192.", default=None
    )
    stm: RestconfList[StmItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Synchronous Transport Module N, e.g. N=16, 64. Reference [ITU-T G.691].",
        default=None,
    )
    fc: RestconfList[FcItem] | None = Field(
        json_schema_extra={"is_config": True}, description="FC facility.", default=None
    )
    interlaken: RestconfList[InterlakenItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="IOA YANG model describing the interlaken interface, which is used to monitor the interlaken connection\nbetween the paired slot on G30 via front DAC cable (not applicable to G30c). This would be attached to\nthe TribPtps to manage the interlaken interface between the paired cards.",
        default=None,
    )
    mc_f: RestconfList[McFItem] | None = Field(
        json_schema_extra={"is_config": True}, description="MC-F: Media Channel Filler.", default=None, alias="mc-f"
    )
    nmc_f: RestconfList[NmcFItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="NMC: Network Media Channel Filler (ASE) facility.\nA network media channel is a logical entity representing the optical signal carrying the service.\nThe optical signal is also referred to as optical carrier.\nNM CFiller (ASE) is defined by its center frequency and width.",
        default=None,
        alias="nmc-f",
    )


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


class DirectionEnum_3(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * two-way
    """

    TWO_WAY = "two-way"


class PayloadTreatmentEnum(str, Enum):
    """Enumeration for PayloadTreatmentEnum

    Values:
      * transport: payload-treatment for ethernet ctp xcon.
      * transport-without-fec: payload-treatment for client otu4 and line odu4 xcon when PT is OTU4.
      * switching: payload-treatment for client odu4 and line odu4 xcon when PT is 100G.
      * regen: payload-treatment for two line lo-odu4 xcon when PT is OTU4.
      * regen-switching: payload-treatment for two line lo-odu4 xcon when PT is 100G.
    """

    TRANSPORT = "transport"
    TRANSPORT_WITHOUT_FEC = "transport-without-fec"
    SWITCHING = "switching"
    REGEN = "regen"
    REGEN_SWITCHING = "regen-switching"


class NetworkMappingTypeEnum(str, Enum):
    """Enumeration for NetworkMappingTypeEnum

    Values:
      * NA: To be used where mapping is not applicable
      * ODUCn: OTUCn protocol layer.
      * ODUCni: GX proprietary OTUCni protocol layer.
      * ODUCni-M: GX proprietary OTUCni protocol layer.
      * ODU4: ODU4 protocol layer.
      * ODU4i: GX proprietary ODU4i protocol layer.
      * ODUflexi: GX proprietary ODUflexi protocol layer.
      * ODUflex: ODU-flex protocol layer.
      * ODU0: ODU0 protocol layer.
      * ODU1: ODU1 protocol layer.
      * ODU2: ODU2 protocol layer.
      * ODU2e: ODU2e protocol layer.
      * ODU2_AMP: AMP mapping
      * ODU2_BMP: BMP mapping
    """

    NA = "NA"
    ODUCN = "ODUCn"
    ODUCNI = "ODUCni"
    ODUCNI_M = "ODUCni-M"
    ODU4 = "ODU4"
    ODU4I = "ODU4i"
    ODUFLEXI = "ODUflexi"
    ODUFLEX = "ODUflex"
    ODU0 = "ODU0"
    ODU1 = "ODU1"
    ODU2 = "ODU2"
    ODU2E = "ODU2e"
    ODU2_AMP = "ODU2_AMP"
    ODU2_BMP = "ODU2_BMP"


class TypeEnum_2(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * add
      * drop
      * add-drop
      * express
    """

    ADD = "add"
    DROP = "drop"
    ADD_DROP = "add-drop"
    EXPRESS = "express"


class ProtectionTypeEnum(str, Enum):
    """Enumeration for ProtectionTypeEnum

    Values:
      * y-cable
      * snc-n
      * snc-i
      * unprotected
    """

    Y_CABLE = "y-cable"
    SNC_N = "snc-n"
    SNC_I = "snc-i"
    UNPROTECTED = "unprotected"


class XconItem(YangBaseModel):
    """Layer 1 digital services that are currently provisioned in the system.
    This includes pre-provisoned XCONs too.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A user configured name for the XCON.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    source: str = Field(
        json_schema_extra={"is_config": True},
        description="The source end-point between which the XCON needs to be created.",
    )
    destination: str = Field(
        json_schema_extra={"is_config": True},
        description="The destination end-point between which the XCON needs to be created.",
    )
    payload_type: PayloadTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates a generic, high-level source (from) client payload type of the digital XCON.",
        default=None,
        alias="payload-type",
    )
    direction: DirectionEnum_3 | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates whether the digital XCON is uni-directional (1-WAY) or bi-directional (2-WAY).",
        default=DirectionEnum_3.TWO_WAY,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    circuit_id_suffix: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User configured circuit ID suffix.",
        min_length=0,
        max_length=48,
        default=None,
        alias="circuit-id-suffix",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this xcon was system created or not. Only user created xcon can be user deleted.",
        default=ManagedByEnum.USER,
        alias="managed-by",
    )
    payload_treatment: PayloadTreatmentEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates a generic payload treatment value of the digital XCON.",
        default=None,
        alias="payload-treatment",
    )
    network_mapping: NetworkMappingTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the server layer protocol type that supports this XCON.",
        default=None,
        alias="network-mapping",
    )
    type: TypeEnum_2 | None = Field(json_schema_extra={"is_config": False}, description="Type of XCON.", default=None)
    protection_type: ProtectionTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Represents the protection type this XCON has.",
        default=ProtectionTypeEnum.UNPROTECTED,
        alias="protection-type",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="System configured circuit ID, present in XCONs and associated facilities.\nFor facilities, circuit-id is only filled in if an associated XCON exists.\n   Format of this ID is:\n   <timestamp>|<ne-name>|<XCON-AID>|<user-configured-sufix>\n   Example:\n   2020-05-05T21:06:02Z|GX|1-4-T9,1-4-L1-1-ODUji#1|my-suffix\n\n   Timestamp is the NE time at xcon creation, in UTC.\n   If necessary, ne-name will be truncated so that total length remains at 128 characters.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )
    from_adaptation: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicate server layer adaptation at client side.",
        default=None,
        alias="from-adaptation",
    )
    to_adaptation: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicate server layer adaptation at line side.",
        default=None,
        alias="to-adaptation",
    )
    used_resources: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of resources being used by this XCON besides the two main source/destination end-points.",
        min_length=0,
        max_length=64,
        default=None,
        alias="used-resources",
    )


class ActivationModeEnum(str, Enum):
    """Enumeration for ActivationModeEnum

    Values:
      * automatic: System manages the upgrade/ downgrade of the service.
      * manual: User or controller need to orchestrate the upgrade/downgrade of the service.
    """

    AUTOMATIC = "automatic"
    MANUAL = "manual"


class AutoRecoveryStateEnum(str, Enum):
    """Enumeration for AutoRecoveryStateEnum

    Values:
      * not-applicable: ase-insertion-enable='disabled', or in terrestrial mode.
      * active: Valid reference trace is available, toggling limit not reached.
      * failed: Toggling limit exceeded.
      * not-available: No reference trace is available with NRM FSM in Active state.
      * waiting-for-reference: Reference Power not yet available.
    """

    NOT_APPLICABLE = "not-applicable"
    ACTIVE = "active"
    FAILED = "failed"
    NOT_AVAILABLE = "not-available"
    WAITING_FOR_REFERENCE = "waiting-for-reference"


class ActivationRequestTypeEnum(str, Enum):
    """Enumeration for ActivationRequestTypeEnum

    Values:
      * no-request: No request.
      * activate: In Activate request.
      * deactivate: In deactivate request.
    """

    NO_REQUEST = "no-request"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"


class DirectionEnum_4(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * two-way: Two-way indicates the OXcon is bi-directional.
      * one-way: One-way indicates the OXcon is uni-directional
    """

    TWO_WAY = "two-way"
    ONE_WAY = "one-way"


class OxconItem(YangBaseModel):
    """List of Optical Cross Connections (OXcon)."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A user configured name for the OXcon.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    managed_by: ManagedByEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this managed entity was system created or not.\nOnly user created entities can be user deleted.",
        default=ManagedByEnum.USER,
        alias="managed-by",
    )
    activation_mode: ActivationModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="OXCON Activation Mode (it is set-by-create, cannot be changed).",
        default=ActivationModeEnum.AUTOMATIC,
        alias="activation-mode",
    )
    auto_recovery_state: AutoRecoveryStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Auto Recovery State.\n\nCondition (when): /ne/l0-mode-op = 'slte'",
        default=AutoRecoveryStateEnum.NOT_APPLICABLE,
        alias="auto-recovery-state",
    )
    activation_request_fwd: ActivationRequestTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This(rw) attribute controls the state of activation at A->Z direction.",
        default=None,
        alias="activation-request-fwd",
    )
    activation_request_bwd: ActivationRequestTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This(rw) attribute controls the state of activation at Z->A direction.",
        default=None,
        alias="activation-request-bwd",
    )
    activation_state_fwd: ActivationStateTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This(rw) attribute controls the state of activation at A->Z direction.",
        default=None,
        alias="activation-state-fwd",
    )
    activation_state_bwd: ActivationStateTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This(rw) attribute controls the state of activation at Z->A direction.",
        default=None,
        alias="activation-state-bwd",
    )
    source: str = Field(
        json_schema_extra={"is_config": True}, description="The source end-point required for OXcon creation."
    )
    destination: str = Field(
        json_schema_extra={"is_config": True}, description="The destination end-point required for OXcon creation."
    )
    direction: DirectionEnum_4 | None = Field(
        json_schema_extra={"is_config": True}, description="Set-by-create OXcon type.", default=DirectionEnum_4.TWO_WAY
    )
    monitored: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Monitoring/ not-monitored indication; does not change during oxcon lifetime.",
        default=True,
    )
    target_output_power_src: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The source interface target power.\n    Only of relevance for power working mode and two-way OXcon.",
        ge=-55.0,
        le=55.0,
        default=0,
        alias="target-output-power-src",
    )
    target_output_power_dst: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The destination interface target power.\n    Only of relevance when connecting regular NMC.",
        ge=-55.0,
        le=55.0,
        default=0,
        alias="target-output-power-dst",
    )
    target_actual_power_dst: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Value: as calculated by Power Control if target-power-setting = auto;\notherwise it is the exact value configured at target-output-power-dst/ src.\n   Only of relevance when connecting regular NMC.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="target-actual-power-dst",
    )
    target_actual_power_src: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Value: as calculated by Power Control if target-power-setting = auto;\notherwise it is the exact value configured at target-output-power-dst/ src.\n   Only of relevance when connecting regular NMC.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="target-actual-power-src",
    )
    target_actual_psd_dst: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual PSD destination.\n    Only of relevance when connecting regular NMC.",
        default=None,
        alias="target-actual-psd-dst",
    )
    target_actual_psd_src: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual PSD source.\n    Only of relevance when connecting regular NMC.",
        default=None,
        alias="target-actual-psd-src",
    )
    circuit_id: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Path/ service name of optical cross-connection.",
        min_length=0,
        max_length=128,
        default=None,
        alias="circuit-id",
    )


class SupportingEntityTypeEnum(str, Enum):
    """Enumeration for SupportingEntityTypeEnum

    Values:
      * wavelength-encryption: The secure entity type is an optical carrier.
      * odu-encryption: The secure entity type is ODU.
    """

    WAVELENGTH_ENCRYPTION = "wavelength-encryption"
    ODU_ENCRYPTION = "odu-encryption"


class ReKeyFailPolicyEnum(str, Enum):
    """Enumeration for ReKeyFailPolicyEnum

    Values:
      * kill-traffic: Bring down the data path encrypted service if re-key was unsuccessful.
      * continue-traffic: Continue the data path encrypted service even if re-key was unsuccessful.
    """

    KILL_TRAFFIC = "kill-traffic"
    CONTINUE_TRAFFIC = "continue-traffic"


class EncryptionAlgorithmEnum(str, Enum):
    """Enumeration for EncryptionAlgorithmEnum

    Values:
      * null: NULL encryption, used when authentication-only (no confidentiality) usage is desired
      * aes-gcm-8: AES-GCM with 8-byte ICV.
      * aes-gcm-12: AES-GCM with 12-byte ICV.
      * aes-gcm-16: AES-GCM with 16-byte ICV.
      * aes-ctr: AES-CTR mode.
      * aes-cbc: AES-CBC mode.
      * aes-ccm-8: AES-CCM with 8-byte ICV.
      * aes-ccm-12: AES-CCM with 12-byte ICV.
      * aes-ccm-16: AES-CCM with 16-byte ICV.
      * chacha20-poly1305: ChaCha20/Poly1305 with 128 bit ICV
    """

    NULL = "null"
    AES_GCM_8 = "aes-gcm-8"
    AES_GCM_12 = "aes-gcm-12"
    AES_GCM_16 = "aes-gcm-16"
    AES_CTR = "aes-ctr"
    AES_CBC = "aes-cbc"
    AES_CCM_8 = "aes-ccm-8"
    AES_CCM_12 = "aes-ccm-12"
    AES_CCM_16 = "aes-ccm-16"
    CHACHA20_POLY1305 = "chacha20-poly1305"


class EncryptionKeyLengthEnum(str, Enum):
    """Enumeration for EncryptionKeyLengthEnum

    Values:
      * none
      * key-length-128
      * key-length-192
      * key-length-256
    """

    NONE = "none"
    KEY_LENGTH_128 = "key-length-128"
    KEY_LENGTH_192 = "key-length-192"
    KEY_LENGTH_256 = "key-length-256"


class IntegrityAlgorithmEnum(str, Enum):
    """Enumeration for IntegrityAlgorithmEnum

    Values:
      * none: Can be used only when the encryption algorithm uses authenticated encryption/AEAD (such as AES-GCM). Cannot be used with other non AEAD encryption algorithms such as AES-CTR or AES-CBC.
      * hmac-sha2-256-128
      * hmac-sha2-384-192
      * hmac-sha2-512-256
      * hmac-sha1-160
      * hmac-sha1-96
    """

    NONE = "none"
    HMAC_SHA2_256_128 = "hmac-sha2-256-128"
    HMAC_SHA2_384_192 = "hmac-sha2-384-192"
    HMAC_SHA2_512_256 = "hmac-sha2-512-256"
    HMAC_SHA1_160 = "hmac-sha1-160"
    HMAC_SHA1_96 = "hmac-sha1-96"


class ChildSaDhGroupEnum(str, Enum):
    """Enumeration for ChildSaDhGroupEnum

    Values:
      * dhe-2048
      * dhe-3072
      * dhe-4096
      * dhe-6144
      * dhe-8192
      * ecp-256
      * ecp-384
      * ecp-521
      * curve-25519
      * curve-448
    """

    DHE_2048 = "dhe-2048"
    DHE_3072 = "dhe-3072"
    DHE_4096 = "dhe-4096"
    DHE_6144 = "dhe-6144"
    DHE_8192 = "dhe-8192"
    ECP_256 = "ecp-256"
    ECP_384 = "ecp-384"
    ECP_521 = "ecp-521"
    CURVE_25519 = "curve-25519"
    CURVE_448 = "curve-448"


class SecureEntitySaProposalItem(YangBaseModel):
    """A list of protocol proposals when negotiating the secure entity SA
    with the far-end secure entity peer.
    """

    number: int = Field(
        json_schema_extra={"is_config": False}, description="The proposal number for the secure entity SA.", ge=1
    )
    encryption_algorithm: EncryptionAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The encryption algorithm for the secure entity SA.",
        default=None,
        alias="encryption-algorithm",
    )
    encryption_key_length: EncryptionKeyLengthEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The secure entity SA encryption algorithm key length.",
        default=None,
        alias="encryption-key-length",
    )
    integrity_algorithm: IntegrityAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Secure entity SA integrity algorithm advertised to the far-end secure entity peer.",
        default=None,
        alias="integrity-algorithm",
    )
    dh_group: ChildSaDhGroupEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Secure entity SA Diffie-Hellman group\nadvertised to the far-end secure entity peer.",
        default=None,
        alias="dh-group",
    )


class SecureEntityItem(YangBaseModel):
    """List of l1 encryption secure entities."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A name for the data path l1 encryption secure entity (SecY).",
        min_length=1,
        max_length=64,
    )
    supporting_entity_type: SupportingEntityTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates supporting entity type.",
        default=SupportingEntityTypeEnum.WAVELENGTH_ENCRYPTION,
        alias="supporting-entity-type",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates whether the SecY are configured and attached to any data path entity.",
        default=False,
    )
    supporting_facility: str = Field(
        json_schema_extra={"is_config": True},
        description="The optical carrier that needs data path encryption.",
        alias="supporting-facility",
    )
    remote_secure_entity: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="Refers to the far-end  secure entity's object name (XPath).\nRequired by IKEv2 - This will be used by IKEv2 as a traffic selector.",
            min_length=1,
            max_length=64,
            alias="remote-secure-entity",
        )
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A system-generated AID for the SecY.",
        min_length=1,
        max_length=64,
        default=None,
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    re_key_frequency: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The re-key frequency for the data path encryption service.",
        ge=300,
        le=86400,
        default=300,
        alias="re-key-frequency",
    )
    re_key_fail_policy: ReKeyFailPolicyEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the NE's policy and consequent action when re-keying\nthe data path security association is unsuccessful.",
        default=ReKeyFailPolicyEnum.CONTINUE_TRAFFIC,
        alias="re-key-fail-policy",
    )
    traffic_kill_offset: int | None = Field(
        json_schema_extra={"is_config": True},
        description="If the re-key fail policy is set to KILL-TRAFFIC, this attribute indicates the amount of time\nthe system waits before killing encrypted data path.\n\nCondition (when): ../re-key-fail-policy = 'kill-traffic'",
        ge=0,
        le=86400,
        default=0,
        alias="traffic-kill-offset",
    )
    esn: bool | None = Field(
        json_schema_extra={"is_config": False}, description="Extended Sequence Number (ESN) support.", default=True
    )
    secure_entity_sa_proposal: RestconfList[SecureEntitySaProposalItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="A list of protocol proposals when negotiating the secure entity SA\nwith the far-end secure entity peer.",
        default=None,
        alias="secure-entity-sa-proposal",
    )


class DataPathEncryption(YangBaseModel):
    """A top-level container for all data path encryption services and entities."""

    secure_entity: RestconfList[SecureEntityItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of l1 encryption secure entities.",
        default=None,
        alias="secure-entity",
    )


class ServicesServices(YangBaseModel):
    """Services of multiples types commissioned in this NE."""

    xcon: RestconfList[XconItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Layer 1 digital services that are currently provisioned in the system.\nThis includes pre-provisoned XCONs too.",
        default=None,
    )
    oxcon: RestconfList[OxconItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of Optical Cross Connections (OXcon).\n\nCondition (when): /ne/node-type = 'OADM'",
        default=None,
    )
    data_path_encryption: DataPathEncryption | None = Field(
        json_schema_extra={"is_config": True},
        description="A top-level container for all data path encryption services and entities.",
        default=None,
        alias="data-path-encryption",
    )


class SshAuthenticationMethodEnum(str, Enum):
    """Enumeration for SshAuthenticationMethodEnum

    Values:
      * password: Use password-based authentication for SSH access.
      * public-key: Use public key authentication for SSH access. Only supported in ADV package.
      * public-key-or-password: Use public key authentication with fallback to password-based authentication for SSH access. Only supported in ADV package. Note: This is a convenience feature and does not enhance security.
    """

    PASSWORD = "password"
    PUBLIC_KEY = "public-key"
    PUBLIC_KEY_OR_PASSWORD = "public-key-or-password"


class AaaAuthenticationMethodEnum(str, Enum):
    """Enumeration for AaaAuthenticationMethodEnum

    Values:
      * local-only: Authentication locally only
      * local-first-then-remote: Authentication locally first, if not pass, then use remote AAA server
      * remote-first-then-local: Authentication use remote AAA server first, if remote authentication failed or all servers could not be contacted, then authenticate locally
      * remote-unavailable-then-local: Authentication use remote AAA server first, if all servers could not be contacted, then authenticate locally
    """

    LOCAL_ONLY = "local-only"
    LOCAL_FIRST_THEN_REMOTE = "local-first-then-remote"
    REMOTE_FIRST_THEN_LOCAL = "remote-first-then-local"
    REMOTE_UNAVAILABLE_THEN_LOCAL = "remote-unavailable-then-local"


class AaaAuthorizationMethodEnum(str, Enum):
    """Enumeration for AaaAuthorizationMethodEnum

    Values:
      * local-only: Authorization locally only.
      * remote-if-authenticated-else-local: Local users should follow local permissions and remote users should follow the remote ones.
      * remote-unavailable-then-local: All users (local or remote) should follow remote permissions. If the permissions return unavailable, then use local ones.
    """

    LOCAL_ONLY = "local-only"
    REMOTE_IF_AUTHENTICATED_ELSE_LOCAL = "remote-if-authenticated-else-local"
    REMOTE_UNAVAILABLE_THEN_LOCAL = "remote-unavailable-then-local"


class SshStrictHostKeyCheckingEnum(str, Enum):
    """Enumeration for SshStrictHostKeyCheckingEnum

    Values:
      * strict: Only allow connection to a remote ssh/sftp/scp host if identity provided by remote host is known
      * relaxed: Allow connection to a remote ssh/sftp/scp host, regardless if identity provided by remote host is known
    """

    STRICT = "strict"
    RELAXED = "relaxed"


class SshCiphersEnum(str, Enum):
    """Enumeration for SshCiphersEnum

    Values:
      * aes128-ctr: Advanced Encryption Standard with 128-bit key in Counter mode.
      * aes192-ctr: Advanced Encryption Standard with 192-bit key in Counter mode.
      * aes256-ctr: Advanced Encryption Standard with 256-bit key in Counter mode.
      * aes128-gcm-at-openssh-com: Advanced Encryption Standard with 128-bit key in Galois/Counter mode.
      * aes256-gcm-at-openssh-com: Advanced Encryption Standard with 256-bit key in Galois/Counter mode.
      * chacha20-poly1305-at-openssh-com: ChaCha20 stream cipher and Poly1305 MAC.
      * aes128-cbc: Advanced Encryption Standard with 128-bit key in Cipher Block Chaining mode.
      * aes256-cbc: Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode.
    """

    AES128_CTR = "aes128-ctr"
    AES192_CTR = "aes192-ctr"
    AES256_CTR = "aes256-ctr"
    AES128_GCM_AT_OPENSSH_COM = "aes128-gcm-at-openssh-com"
    AES256_GCM_AT_OPENSSH_COM = "aes256-gcm-at-openssh-com"
    CHACHA20_POLY1305_AT_OPENSSH_COM = "chacha20-poly1305-at-openssh-com"
    AES128_CBC = "aes128-cbc"
    AES256_CBC = "aes256-cbc"


class SshMacsEnum(str, Enum):
    """Enumeration for SshMacsEnum

    Values:
      * hmac-sha2-256: 256-bit hash-based MAC using Secure Hash Algorithm-2.
      * hmac-sha2-512: 512-bit hash-based MAC using Secure Hash Algorithm-2.
      * hmac-sha2-256-etm-at-openssh-com: 256-bit Encrypt-then-MAC using Secure Hash Algorithm-2.
      * hmac-sha2-512-etm-at-openssh-com: 512-bit Encrypt-then-MAC using Secure Hash Algorithm-2.
      * hmac-sha1: 160-bit hash-based MAC using Secure Hash Algorithm-1.
      * hmac-sha1-96: Truncated 160-bit hash-based MAC using Secure Hash Algorithm-1.
      * hmac-sha1-etm-at-openssh-com: 160-bit Encrypt-then-MAC using Secure Hash Algorithm-1.
      * hmac-sha1-96-etm-at-openssh-com: Truncated 160-bit Encrypt-then-MAC using Secure Hash Algorithm-1.
    """

    HMAC_SHA2_256 = "hmac-sha2-256"
    HMAC_SHA2_512 = "hmac-sha2-512"
    HMAC_SHA2_256_ETM_AT_OPENSSH_COM = "hmac-sha2-256-etm-at-openssh-com"
    HMAC_SHA2_512_ETM_AT_OPENSSH_COM = "hmac-sha2-512-etm-at-openssh-com"
    HMAC_SHA1 = "hmac-sha1"
    HMAC_SHA1_96 = "hmac-sha1-96"
    HMAC_SHA1_ETM_AT_OPENSSH_COM = "hmac-sha1-etm-at-openssh-com"
    HMAC_SHA1_96_ETM_AT_OPENSSH_COM = "hmac-sha1-96-etm-at-openssh-com"


class SshKeyExchangesEnum(str, Enum):
    """Enumeration for SshKeyExchangesEnum

    Values:
      * diffie-hellman-group-exchange-sha256: Diffie-Hellman group exchange algorithm using Secure Hash Algorithm-2.
      * ecdh-sha2-nistp256: ECDH key exchange algorithm with ephemeral keys generated on the nistp256 curve using Secure Hash Algorithm-2.
      * ecdh-sha2-nistp384: ECDH key exchange algorithm with ephemeral keys generated on the nistp384 curve using Secure Hash Algorithm-2.
      * ecdh-sha2-nistp521: ECDH key exchange algorithm with ephemeral keys generated on the nistp521 curve using Secure Hash Algorithm-2.
      * diffie-hellman-group14-sha1: Diffie-Hellman group 14 key exchange algorithm using Secure Hash Algorithm-1.
      * diffie-hellman-group-exchange-sha1: Diffie-Hellman group exchange algorithm using Secure Hash Algorithm-1.
      * diffie-hellman-group14-sha256: Diffie-Hellman group 14 key exchange algorithm using Secure Hash Algorithm-2.
    """

    DIFFIE_HELLMAN_GROUP_EXCHANGE_SHA256 = "diffie-hellman-group-exchange-sha256"
    ECDH_SHA2_NISTP256 = "ecdh-sha2-nistp256"
    ECDH_SHA2_NISTP384 = "ecdh-sha2-nistp384"
    ECDH_SHA2_NISTP521 = "ecdh-sha2-nistp521"
    DIFFIE_HELLMAN_GROUP14_SHA1 = "diffie-hellman-group14-sha1"
    DIFFIE_HELLMAN_GROUP_EXCHANGE_SHA1 = "diffie-hellman-group-exchange-sha1"
    DIFFIE_HELLMAN_GROUP14_SHA256 = "diffie-hellman-group14-sha256"


class SshKeyAlgorithmEnum(str, Enum):
    """Enumeration for SshKeyAlgorithmEnum

    Values:
      * ssh-rsa: RSA key algorithm using SHA-1 hash.
      * rsa-sha2-256: RSA key algorithm using SHA-256 hash.
      * rsa-sha2-512: RSA key algorithm using SHA-512 hash.
      * ecdsa-sha2-nistp256: ECDSA key algorithm on the nistp256 curve using SHA-256 hash.
      * ecdsa-sha2-nistp384: ECDSA key algorithm on the nistp384 curve using SHA-384 hash.
      * ecdsa-sha2-nistp521: ECDSA key algorithm on the nistp521 curve using SHA-512 hash.
    """

    SSH_RSA = "ssh-rsa"
    RSA_SHA2_256 = "rsa-sha2-256"
    RSA_SHA2_512 = "rsa-sha2-512"
    ECDSA_SHA2_NISTP256 = "ecdsa-sha2-nistp256"
    ECDSA_SHA2_NISTP384 = "ecdsa-sha2-nistp384"
    ECDSA_SHA2_NISTP521 = "ecdsa-sha2-nistp521"


class CspRetrievalEncodingEnum(str, Enum):
    """Enumeration for CspRetrievalEncodingEnum

    Values:
      * disabled: Do not use any encoding. CSPs are obfuscated.
      * type7: Display CSPs in type 7 encoding, or in hash when applicable.
      * hashed-only: Display CSPs hash when applicable, otherwise they are obfuscated.
    """

    DISABLED = "disabled"
    TYPE7 = "type7"
    HASHED_ONLY = "hashed-only"


class SupportedTlsVersionEnum(str, Enum):
    """Enumeration for SupportedTlsVersionEnum

    Values:
      * 1.2-only: Use TLS version 1.2 only.
      * 1.3-only: Use TLS version 1.3 only.
      * 1.3-with-fallback-to-1.2: Try to use TLS version 1.3 but if it fails use version 1.2.
    """

    _1_2_ONLY = "1.2-only"
    _1_3_ONLY = "1.3-only"
    _1_3_WITH_FALLBACK_TO_1_2 = "1.3-with-fallback-to-1.2"


class Tls12CipherSuitesEnum(str, Enum):
    """Enumeration for Tls12CipherSuitesEnum

    Values:
      * TLS_DHE_RSA_WITH_AES_128_CBC_SHA256: Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 128-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 256.
      * TLS_DHE_RSA_WITH_AES_128_GCM_SHA256: Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 128-bit key in Galois/Counter mode, Secure Hash Algorithm 256.
      * TLS_DHE_RSA_WITH_AES_256_CBC_SHA256: Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 256.
      * TLS_DHE_RSA_WITH_AES_256_GCM_SHA384: Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 256-bit key in Galois/Counter mode, Secure Hash Algorithm 384.
      * TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256: Elliptic Curve Diffie-Hellman Ephemeral, Elliptic Curve Digital Signature Algorithm, Advanced Encryption Standard with 128-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 256.
      * TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256: Elliptic Curve Diffie-Hellman Ephemeral, Elliptic Curve Digital Signature Algorithm, Advanced Encryption Standard with 128-bit key in Galois/Counter mode, Secure Hash Algorithm 256.
      * TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384: Elliptic Curve Diffie-Hellman Ephemeral, Elliptic Curve Digital Signature Algorithm, Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 384.
      * TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384: Elliptic Curve Diffie-Hellman Ephemeral, Elliptic Curve Digital Signature Algorithm, Advanced Encryption Standard with 256-bit key in Galois/Counter mode, Secure Hash Algorithm 384.
      * TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256: Elliptic Curve Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 128-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 256.
      * TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256: Elliptic Curve Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 128-bit key in Galois/Counter mode, Secure Hash Algorithm 256.
      * TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384: Elliptic Curve Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 384.
      * TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384: Elliptic Curve Diffie-Hellman Ephemeral, Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 256-bit key in Galois/Counter mode, Secure Hash Algorithm 384.
      * TLS_RSA_WITH_AES_128_CBC_SHA256: Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 128-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 256.
      * TLS_RSA_WITH_AES_128_GCM_SHA256: Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 128-bit key in Galois/Counter mode, Secure Hash Algorithm 256.
      * TLS_RSA_WITH_AES_256_CBC_SHA256: Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode, Secure Hash Algorithm 256.
      * TLS_RSA_WITH_AES_256_GCM_SHA384: Rivest Shamir Adleman algorithm, Advanced Encryption Standard with 256-bit key in Galois/Counter mode, Secure Hash Algorithm 384.
    """

    TLS_DHE_RSA_WITH_AES_128_CBC_SHA256 = "TLS_DHE_RSA_WITH_AES_128_CBC_SHA256"
    TLS_DHE_RSA_WITH_AES_128_GCM_SHA256 = "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256"
    TLS_DHE_RSA_WITH_AES_256_CBC_SHA256 = "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256"
    TLS_DHE_RSA_WITH_AES_256_GCM_SHA384 = "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384"
    TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 = "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256"
    TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 = "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"
    TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 = "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384"
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 = "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
    TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 = "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256"
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 = "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 = "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384"
    TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    TLS_RSA_WITH_AES_128_CBC_SHA256 = "TLS_RSA_WITH_AES_128_CBC_SHA256"
    TLS_RSA_WITH_AES_128_GCM_SHA256 = "TLS_RSA_WITH_AES_128_GCM_SHA256"
    TLS_RSA_WITH_AES_256_CBC_SHA256 = "TLS_RSA_WITH_AES_256_CBC_SHA256"
    TLS_RSA_WITH_AES_256_GCM_SHA384 = "TLS_RSA_WITH_AES_256_GCM_SHA384"


class Tls13CipherSuitesEnum(str, Enum):
    """Enumeration for Tls13CipherSuitesEnum

    Values:
      * TLS_AES_128_GCM_SHA256: Advanced Encryption Standard with 128-bit key in Galois/Counter mode (Secure Hash Algorithm 256).
      * TLS_AES_256_GCM_SHA384: Advanced Encryption Standard with 256-bit key in Galois/Counter mode (Secure Hash Algorithm 384).
      * TLS_CHACHA20_POLY1305_SHA256: ChaCha stream cipher and Poly1305 authenticator (Secure Hash Algorithm 256).
      * TLS_AES_128_CCM_SHA256: Advanced Encryption Standard with 128-bit key in Counter with CBC-MAC mode (Secure Hash Algorithm 256).
      * TLS_AES_128_CCM_8_SHA256: Advanced Encryption Standard with 128-bit key in Counter with CBC-MAC mode with 8-Octet ICV (Secure Hash Algorithm 256).
    """

    TLS_AES_128_GCM_SHA256 = "TLS_AES_128_GCM_SHA256"
    TLS_AES_256_GCM_SHA384 = "TLS_AES_256_GCM_SHA384"
    TLS_CHACHA20_POLY1305_SHA256 = "TLS_CHACHA20_POLY1305_SHA256"
    TLS_AES_128_CCM_SHA256 = "TLS_AES_128_CCM_SHA256"
    TLS_AES_128_CCM_8_SHA256 = "TLS_AES_128_CCM_8_SHA256"


class TlsCurvesEnum(str, Enum):
    """Enumeration for TlsCurvesEnum

    Values:
      * secp256r1: 256-bit Elliptic-curve Diffie-Hellman using curve SECP256r1.
      * secp384r1: 384-bit Elliptic-curve Diffie-Hellman using curve SECP384r1.
      * secp521r1: 521-bit Elliptic-curve Diffie-Hellman using curve SECP521r1.
      * x25519: 256-bit Elliptic-curve Diffie-Hellman using curve 25519.
      * x448: 448-bit Elliptic-curve Diffie-Hellman using curve 448.
    """

    SECP256R1 = "secp256r1"
    SECP384R1 = "secp384r1"
    SECP521R1 = "secp521r1"
    X25519 = "x25519"
    X448 = "x448"


class SignatureHashAlgorithmTypeEnum(str, Enum):
    """Enumeration for SignatureHashAlgorithmTypeEnum

    Values:
      * sha256: Secure Hash Algorithm 2, digest size 256 bits.
      * sha384: Secure Hash Algorithm 2, digest size 384 bits.
      * sha512: Secure Hash Algorithm 2, digest size 512 bits.
      * sha1: Secure Hash Algorithm 1
    """

    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA1 = "sha1"


class SecurityPolicies(YangBaseModel):
    """Container with several flags that represent security policies of the system."""

    secure_mode: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If enabled, non-secure protocols are not supported.\nIf disabled, non-secure protocols can be used, including:\n- HTTP protocol for file transfer, REST API, or any other HTTP based application\n- FTP protocol for file transfer\n- SNMPv2c or SNMPv3 without encryption\n\nEnabling secure-mode will be rejected if any non-secure protocol is in use.",
        default=True,
        alias="secure-mode",
    )
    strict_password_check: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If enabled, ensures the strict password complexity rules. Including:\n- minimum length of 8 characters (by default, configurable via the minimum-password-length policy)\n- at least one lower case letter (a-z)\n- at least one upper case letter (A-Z)\n- at least one number (0-9)\n- at least one symbol ()\n- user name cannot be part of the password\nIf disabled, all these rules are not enforced, except:\n- minimum length is 1 character (by default, configurable via the minimum-password-length policy)\nOnce enabled, this policy only has impact on newly defined passwords.",
        default=True,
        alias="strict-password-check",
    )
    minimum_password_length: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurable minimum length for user passwords. When a password is changed, the password length will be verified according with this policy.\nNote that changing this policy will not have impact on already set passwords, only on newly set passwords.\nThe default value will depend on whether the policy strict-password-check is enabled or not (min length is 8 if enabled, 1 if disabled),\nbut the user is able to override this value by editing this policy manually.\nNote: this policy can only be enforced when the password is provided in a non-hashed way.",
        ge=1,
        le=200,
        default=8,
        alias="minimum-password-length",
    )
    ssh_authentication_method: SshAuthenticationMethodEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The method used to authenticate user for SSH access.\nNote: For two-factor authentication, use public-key method and employ PIN/password-protected hardware device (e.g.: smart card or USB token.)",
        default=SshAuthenticationMethodEnum.PASSWORD,
        alias="ssh-authentication-method",
    )
    default_user_group: RestconfList[
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))]
    ] = Field(
        json_schema_extra={"is_config": True},
        description="Default roles for users access.",
        min_length=1,
        max_length=64,
        alias="default-user-group",
    )
    enforce_password_history_check: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If enabled, ensures that a new password being set cannot match any of the previous N passwords\nfor the user. N is configurable through password-history-size.\nIf disabled, password repetition is allowed.\nOnce enabled, this policy only has impact on newly defined passwords.",
        default=True,
        alias="enforce-password-history-check",
    )
    password_history_size: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The number of passwords to store for password reuse checking.",
        ge=1,
        le=20,
        default=5,
        alias="password-history-size",
    )
    aaa_authentication_method: AaaAuthenticationMethodEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify authentication method for the user login to the NE.",
        default=AaaAuthenticationMethodEnum.LOCAL_ONLY,
        alias="aaa-authentication-method",
    )
    aaa_authorization_method: AaaAuthorizationMethodEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify authorization policy for the logged user. If the user changes this parameter, it should logout and login again to apply the rules.",
        default=AaaAuthorizationMethodEnum.LOCAL_ONLY,
        alias="aaa-authorization-method",
    )
    ssh_strict_host_key_checking: SshStrictHostKeyCheckingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify the strictness of remote ssh/sftp/scp host identity checking.",
        default=SshStrictHostKeyCheckingEnum.RELAXED,
        alias="ssh-strict-host-key-checking",
    )
    ssh_ciphers: RestconfList[SshCiphersEnum] = Field(
        json_schema_extra={"is_config": True}, description="Allowed symmetric ciphers for SSH.", alias="ssh-ciphers"
    )
    ssh_macs: RestconfList[SshMacsEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Allowed message authentication code algorithms for SSH.",
        alias="ssh-macs",
    )
    ssh_key_exchanges: RestconfList[SshKeyExchangesEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Allowed key exchange algorithms for SSH.",
        alias="ssh-key-exchanges",
    )
    ssh_host_key_algorithms: RestconfList[SshKeyAlgorithmEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Allowed host key algorithms for SSH.",
        alias="ssh-host-key-algorithms",
    )
    ssh_public_key_algorithms: RestconfList[SshKeyAlgorithmEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Allowed public key algorithms for SSH.",
        alias="ssh-public-key-algorithms",
    )
    ssh_key_aging_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This policy defines the ssh-authorized-keys aging interval. Setting the value to 0 disables ssh-authorized-keys aging.\nThis affects the expiration date of all ssh-authorized-keys. Once aging is enabled, the expiration date is calculated\nfrom current time, for previously configured keys, and from configuration time, for newly configured keys.",
        ge=0,
        le=3000,
        default=0,
        alias="ssh-key-aging-interval",
    )
    root_password: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="The password of the root user.\nNote: this attribute is obsolete and has no impact in the system - this is kept for temporary backward compatibility.",
        min_length=0,
        max_length=200,
        default=None,
        alias="root-password",
    )
    console_user_password: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="The password of the console-user. Can be provided as an alternative to the console-user-password-hashed.",
        min_length=0,
        max_length=200,
        default=None,
        alias="console-user-password",
    )
    console_user_password_hashed: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Hashed password of the console-user.\nCan be provided as an alternative to the plaintext console-user-password field.\nIt is made of three mandatory fields,\nwhere the dollar sign is the field separator. The structure is: $id$salt$hash\nOnly id 6 (SHA512) is supported. Salt size is between 2 and 16.\nreference: https://www.akkadia.org/drepper/SHA-crypt.txt",
        min_length=0,
        max_length=106,
        default=None,
        alias="console-user-password-hashed",
    )
    console_user_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="A switch to enable/disable console-user.\nThe console-user account is an emergency account that is only usable through the serial console.\nDisabling this account may put the device in a position where recovery is not possible,\nso it is recommended to keep this account enabled.",
        default=True,
        alias="console-user-enabled",
    )
    csp_symmetrical_key: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="Critical Security Parameters symmetrical key.",
        min_length=0,
        max_length=200,
        default=None,
        alias="csp-symmetrical-key",
    )
    csp_retrieval_encoding: CspRetrievalEncodingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Support to retrieve CSPs in the given encoding.",
        default=CspRetrievalEncodingEnum.DISABLED,
        alias="csp-retrieval-encoding",
    )
    max_system_sessions: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The maximum number of management sessions that the system supports.\nNote: session via serial console does not count against this maximum.",
        ge=0,
        default=None,
        alias="max-system-sessions",
    )
    max_local_users: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The maximum number of local users that can be configured in the system.",
        ge=0,
        default=None,
        alias="max-local-users",
    )
    disable_user_lockout: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This policy allows to enable/disable user lockout when multiple invalid logins are detected.\nThe number of invalid logins that trigger the lockout is configurable at the individual user level with the max-invalid-logins parameter.\nThe time the user is locked-out is also configurable at user level with the suspension-time parameter.",
        default=False,
        alias="disable-user-lockout",
    )
    db_passphrase: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-zA-Z.\\-:+=^!/*?&<>()\\[\\]{}@%$#]*)$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Passphrase used for encrypting and decrypting DB snapshots.\nFor each command associated with DB snapshots (backup, restore, etc),\nthis db-passphrase will be used, except when it is directly provided in each command.\nAutomatic DB snapshots will not be enabled until this parameter is set.",
        default=None,
        alias="db-passphrase",
    )
    supported_tls_version: SupportedTlsVersionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Transport Layer Security (TLS) supported version(s). Changing this attribute will not affect existing connections.",
        default=SupportedTlsVersionEnum._1_2_ONLY,
        alias="supported-tls-version",
    )
    tls_1_2_cipher_suites: RestconfList[Tls12CipherSuitesEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Supported TLS 1.2 cipher suites. Changing this attribute will not affect existing connections.",
        alias="tls-1.2-cipher-suites",
    )
    tls_1_3_cipher_suites: RestconfList[Tls13CipherSuitesEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Supported TLS 1.3 cipher suites. Changing this attribute will not affect existing connections.\nTLS_CHACHA20_POLY1305_SHA256 note:\nIf present and requested by the client, it will be prioritized regardless of cipher-suite order.",
        alias="tls-1.3-cipher-suites",
    )
    tls_curves: RestconfList[TlsCurvesEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Supported elliptic curve algorithms.\nThe tls-curve algorithm affects both key-exchange and authentication stages of TLS handshake.\nChanging this attribute will not affect existing connections.\nApplies to both TLS 1.2 and 1.3.\nNOTE: Restricting curves can cause interoperability issues.\nTLS 1.2 remark: if the configured curve is not sent by the client, handshake may fail.\nTLS 1.3 remark: for the Authentication stage, it is possible that the server\nselects another curve different from the certificate signing algorithm.",
        alias="tls-curves",
    )
    supported_signature_hash_algorithms: RestconfList[SignatureHashAlgorithmTypeEnum] = Field(
        json_schema_extra={"is_config": True},
        description="Supported hash algorithms for digital signatures for certificates.\nThis applies to locally-managed certificates as well as certificates received from a remote peer.\nNOTE: If algorithms are removed from this list, any installed certificates using them will become unusable\nand transition to the 'unsupported' status, potentially disabling secure-applications and services.\nIt also will prevent TLS connections to remote peers using unsupported signature hashes.\nAlso, note that SHA-1 support is limited to root CA certificates.",
        alias="supported-signature-hash-algorithms",
    )
    crl_based_revocation: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This policy allows to enable/disable CRL-based certificate revocation.",
        default=False,
        alias="crl-based-revocation",
    )
    crl_download_timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the maximum time to wait (in seconds) for automatic CRL downloads.\nNote: This timeout does not apply to manual CRL downloads.",
        ge=1,
        le=60,
        default=15,
        alias="crl-download-timeout",
    )
    ocsp_based_revocation: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This policy defines whether OCSP responders can be consulted for certificate revocation checking.",
        default=False,
        alias="ocsp-based-revocation",
    )


class ModeEnum_1(str, Enum):
    """Enumeration for ModeEnum

    Values:
      * static-only: Only system defined static authorization rules are used.
      * static+rules: Both user and system defined access-rules are used. System will try to identify a user configured access-rule first, and only if not found would the system rules be used as a fallback.
      * rules-only: Only user defined access-rules are used. System will try to identify a user configured access-rule first; if not found, the global defaults (read-default/write-default/exec-default) will be used.
    """

    STATIC_ONLY = "static-only"
    STATIC_PLUS_RULES = "static+rules"
    RULES_ONLY = "rules-only"


class ActionTypeEnum(str, Enum):
    """Enumeration for ActionTypeEnum

    Values:
      * permit
      * deny
    """

    PERMIT = "permit"
    DENY = "deny"


class AccessRuleItem(YangBaseModel):
    """Represents a single access-rule, defining access to a particular target path.
    The rule can also consider multiple filters, including:
    - just a particular path
    - a path and an attribute (or more than one attribute)
    - a path, an attribute and a value (or more than one value)
    - a module-name
    - the operation type (create/read/update/delete/execute)
    Paths can represent data-nodes, RPCs or notifications, as well as other non-YANG commands.
    If all criteria are satisfied, the rule will be applied, which means the associated access
    will be permited or denied (depending on the 'action' parameter).
    System supports a maximum of 500 access-rules, accross all access-rule-lists.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name of the access-rule-list.",
        min_length=1,
        max_length=64,
    )
    sequence_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The id of this access-rule within the current list, used for processing all rules.\nLower number ids are processed first.\nId can change over the lifetime of the access-rule-list to re-sort different entries.\nIf not provided, sequence-id will be set to the currently used latest id plus 1 (e.g. will go to the end of the list).",
        ge=1,
        default=None,
        alias="sequence-id",
    )
    module_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="YANG Module to consider when considering this rule; needs to match an available data-model file.\nBy default value '*' is used to represent 'any module name'.\nNote: this value is not validated; if a non-existing module is described here, it will imply the rule\nwill not be valid.",
        min_length=0,
        max_length=64,
        default=None,
        alias="module-name",
    )
    path: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The target object of the access rule.\nMay be:\n- XPath of a YANG data node\n- XPath of a YANG notification\n- XPath of a YANG RPC or a descendant\n- Non-YANG-based command name (gNOI, etc)\n- The default value, '*', representing all targets",
        min_length=1,
        max_length=255,
        default="*",
    )
    attribute: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="Attribute name to which this rule applies to.\nIf not provided, the rule will apply to all attributes in the provided path.\nIf multiple attributes are specified, then the rule applies to all of them.\nNote that if the rule is based on attribute-value, then this field needs to target only 1 attribute.",
        min_length=0,
        max_length=64,
        default=None,
    )
    attribute_value: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="Attribute value to which this rule applies to.\nIf not provided, it means the rule applies independently on the attribute value.\nCan only be provided if a single 'attribute' name is provided.",
        min_length=0,
        max_length=64,
        default=None,
        alias="attribute-value",
    )
    operation: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The list of operations that the rule applies to.\nThe '*' value represents all operations, and is the default value.",
        default=None,
    )
    action: ActionTypeEnum = Field(
        json_schema_extra={"is_config": True},
        description="The permit/deny action associated with this rule.\nThis field needs to be provided whenever an access rule is created.",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="A user-configurable description about this access rule.",
        min_length=0,
        max_length=256,
        default=None,
    )


class AccessRuleListItem(YangBaseModel):
    """Group of access-rules, organized by which user-groups the rules apply to.
    Access-rule-list are processed in order, as given by the sequence-id parameter.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name of the access-rule-list.",
        min_length=1,
        max_length=64,
    )
    user_group: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of user-groups that this access-rule-list applies to.\nThe default value '*' is used as a match-all representation, meaning this access-rule-list applies\nto all existing user-groups.",
        default=None,
        alias="user-group",
    )
    sequence_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The id of this access-rule-lists, used for processing all lists.\nLower number ids are processed first.\nId can change over the lifetime of the access-rule-list to re-sort different entries.\nIf not provided, sequence-id will be set to the currently used latest id plus 1 (e.g. will go to the end of the list).",
        ge=1,
        default=None,
        alias="sequence-id",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="A generic description of this access-rule-list.",
        min_length=0,
        max_length=256,
        default=None,
    )
    access_rule: RestconfList[AccessRuleItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Represents a single access-rule, defining access to a particular target path.\nThe rule can also consider multiple filters, including:\n- just a particular path\n- a path and an attribute (or more than one attribute)\n- a path, an attribute and a value (or more than one value)\n- a module-name\n- the operation type (create/read/update/delete/execute)\nPaths can represent data-nodes, RPCs or notifications, as well as other non-YANG commands.\nIf all criteria are satisfied, the rule will be applied, which means the associated access\nwill be permited or denied (depending on the 'action' parameter).\nSystem supports a maximum of 500 access-rules, accross all access-rule-lists.",
        default=None,
        alias="access-rule",
    )


class Authorization(YangBaseModel):
    """Top level container for authorizations settings."""

    mode: ModeEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="System global authorization mode - selects which kind of authorization rules are used.",
        default=ModeEnum_1.STATIC_PLUS_RULES,
    )
    read_default: ActionTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="In case only user configured access-rules are used, this policy defines what is the action to use\nif a given read operation does not match any rule.\nRead access includes ability to do get/show commands, as well as to receive notifications.\n\nCondition (when): ../mode = 'rules-only'",
        default=ActionTypeEnum.PERMIT,
        alias="read-default",
    )
    write_default: ActionTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="In case only user configured access-rules are used, this policy defines what is the action to use\nif a given write operation does not match any rule.\nWrite access includes create/update/delete commands.\n\nCondition (when): ../mode = 'rules-only'",
        default=ActionTypeEnum.DENY,
        alias="write-default",
    )
    exec_default: ActionTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="In case only user configured access-rules are used, this policy defines what is the action to use\nif a given exec operation does not match any rule.\nExec access includes invocation of RPCs and other commands.\n\nCondition (when): ../mode = 'rules-only'",
        default=ActionTypeEnum.PERMIT,
        alias="exec-default",
    )
    denied_operations: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of times since the system last restarted that an Exec request was denied.",
        ge=0,
        default=None,
        alias="denied-operations",
    )
    denied_data_writes: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of times since the system last restarted that a Write operation request was denied.",
        ge=0,
        default=None,
        alias="denied-data-writes",
    )
    denied_notifications: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of times since the system last restarted that that a notification was dropped for a subscription because\naccess to the event type was denied.",
        ge=0,
        default=None,
        alias="denied-notifications",
    )
    access_rule_list: RestconfList[AccessRuleListItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Group of access-rules, organized by which user-groups the rules apply to.\nAccess-rule-list are processed in order, as given by the sequence-id parameter.",
        default=None,
        alias="access-rule-list",
    )


class UserStatusEnum(str, Enum):
    """Enumeration for UserStatusEnum

    Values:
      * enabled: User account has password-based access to the system.
      * disabled: User account does not have password-based access to the system.
      * password-aged: User will be forced to change password upon next login.
      * lockout: User account is locked out due to unsuccessful login attempts. Note that 'lockout' only applies to password authentication for remote connections. Connections from local (i.e. directly attached) terminals including console and CRAFT port access cannot trigger 'lockout' and are not influenced by it.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"
    PASSWORD_AGED = "password-aged"
    LOCKOUT = "lockout"


class UserAaaTypeEnum(str, Enum):
    """Enumeration for UserAaaTypeEnum

    Values:
      * local: User is authenticated locally.
      * remote: User is authenticated through remote AAA server.
    """

    LOCAL = "local"
    REMOTE = "remote"


class UserItem(YangBaseModel):
    """User details. Can represent both locally configured users, as well as temporary remote users."""

    user_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="The name of the user.",
            min_length=1,
            max_length=64,
            alias="user-name",
        )
    )
    password: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="The password of the user.",
        min_length=0,
        max_length=200,
        default=None,
    )
    password_hashed: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Hashed password of the user. It is made of three mandatory fields,\nwhere the dollar sign is the field separator. The structure is: $id$salt$hash\nOnly id 6 (SHA512) is supported. Salt size is between 2 and 16.\nreference: https://www.akkadia.org/drepper/SHA-crypt.txt",
        min_length=0,
        max_length=106,
        default=None,
        alias="password-hashed",
    )
    user_group: (
        RestconfList[Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))]] | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Associated user groups for this user.",
        min_length=1,
        max_length=64,
        default=None,
        alias="user-group",
    )
    display_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The display name for this user.",
        min_length=0,
        max_length=128,
        default=None,
        alias="display-name",
    )
    max_invalid_login: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This attribute is the maximum number of consecutive and invalid login attempts\nbefore an account is suspended (lockedout). Zero disables escalation on login failure.",
        ge=0,
        default=5,
        alias="max-invalid-login",
    )
    suspension_time: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This attribute is the duration of UID suspension following consecutive invalid login attempts.\nSetting the value to 0 disables this behavior.",
        ge=0,
        le=1440,
        default=5,
        alias="suspension-time",
    )
    timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This attribute is the Session Time Out Interval. If there are no messages between the user\nand the NE over the Time Out interval, the session is logged off. Setting the value to 0 disables\nthis attribute (meaning the session will not time out).",
        ge=0,
        le=1440,
        default=60,
    )
    password_aging_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This attribute is the Password Aging Interval. Setting the value to 0 disables password aging.",
        ge=0,
        le=365,
        default=90,
        alias="password-aging-interval",
    )
    password_expiration_date: (
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
        description="This attribute shows the password expiration date.",
        default=None,
        alias="password-expiration-date",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable switch for the user, allows admins to explicitly disable users.",
        default=True,
    )
    user_status: UserStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute shows the status of the user account.\nNote that public-key authentication is not influenced by this status.",
        default=UserStatusEnum.DISABLED,
        alias="user-status",
    )
    force_password_change: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows administrator to force user to change password on next login.",
        default=False,
        alias="force-password-change",
    )
    max_sessions: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This attribute specifies the maximum number of sessions allowed for this user.",
        ge=1,
        le=20,
        default=10,
        alias="max-sessions",
    )
    last_login_date: (
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
        description="The last login date/time of the user.",
        default="1970-01-01T00:00:00Z",
        alias="last-login-date",
    )
    failed_logins: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of previous failed password-based logins. Resets to zero upon a successful login.\nNote that login failures from local (i.e. directly attached) terminals do not contribute to this count.\nThis includes CLI, NETCONF, and direct shell access from the console and CRAFT ports.\nNote also that login failures for public-key authentication do not contribute to this count.",
        ge=0,
        default=0,
        alias="failed-logins",
    )
    user_aaa_type: UserAaaTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the authentication method of the user.",
        default=UserAaaTypeEnum.LOCAL,
        alias="user-aaa-type",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class UserGroupItem(YangBaseModel):
    """List of user groups, each one with its own access permissions.
    Each user will be associated with a list of groups, and will derive its permissions from them.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Name of the group.", min_length=1, max_length=64
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Long description of the user group.",
        min_length=0,
        max_length=128,
        default=None,
    )


class SessionTypeEnum(str, Enum):
    """Enumeration for SessionTypeEnum

    Values:
      * none
      * cli
      * snmp
      * netconf
      * restconf
      * webgui
      * gnmi
      * tl1
      * gnmi-gnoi
    """

    NONE = "none"
    CLI = "cli"
    SNMP = "snmp"
    NETCONF = "netconf"
    RESTCONF = "restconf"
    WEBGUI = "webgui"
    GNMI = "gnmi"
    TL1 = "tl1"
    GNMI_GNOI = "gnmi-gnoi"


class SessionProtocolEnum(str, Enum):
    """Enumeration for SessionProtocolEnum

    Values:
      * none
      * telnet
      * telnet-raw
      * serial
      * ssh
      * ssh-raw
      * https
      * http
    """

    NONE = "none"
    TELNET = "telnet"
    TELNET_RAW = "telnet-raw"
    SERIAL = "serial"
    SSH = "ssh"
    SSH_RAW = "ssh-raw"
    HTTPS = "https"
    HTTP = "http"


class SessionItem(YangBaseModel):
    """List of currently established management layer sessions."""

    session_id: str = Field(
        json_schema_extra={"is_config": False},
        description="Specifies a unique identifier of the current session. It indicates the\nIP address and transport layer port number associated with this session.\nIf the session is initiated from the serial port, the value is 'NA'.",
        alias="session-id",
    )
    session_user: str | None = Field(
        json_schema_extra={"is_config": False},
        description="User name associated with this session.",
        default=None,
        alias="session-user",
    )
    session_type: SessionTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Session type.", default=None, alias="session-type"
    )
    session_protocol: SessionProtocolEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates which protocol has been used to establish the session.",
        default=None,
        alias="session-protocol",
    )
    created_time: (
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
        description="The timestamp the user has created this session.",
        default=None,
        alias="created-time",
    )
    local_ip_address: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Local ip address of the session",
        default=None,
        alias="local-ip-address",
    )
    dial_out_server_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Name of the dial-out-server associated with this session.",
        min_length=1,
        max_length=64,
        default=None,
        alias="dial-out-server-name",
    )


class ProtocolSupportedEnum(str, Enum):
    """Enumeration for ProtocolSupportedEnum

    Values:
      * TACACSPLUS
      * RADIUS
    """

    TACACSPLUS = "TACACSPLUS"
    RADIUS = "RADIUS"


class TransportEnum(str, Enum):
    """Enumeration for TransportEnum

    Values:
      * tcp: Applicable when the protocol is TACACS.
      * udp: Applicable when the protocol is RADIUS.
      * tls: Applicable when the protocol is RADIUS. When this transport mode is selected,    the shared secret is defaulted to 'radsec'. Refer to RFC 6614
    """

    TCP = "tcp"
    UDP = "udp"
    TLS = "tls"


class AaaServerItem(YangBaseModel):
    """Configuration of AAA servers - RADIUS or TACACS+."""

    server_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="specify the name of aaa server.",
        min_length=1,
        max_length=64,
        alias="server-name",
    )
    server_priority: int = Field(
        json_schema_extra={"is_config": True},
        description="This is used to sort the servers in the order of precedence.",
        ge=1,
        le=10,
        alias="server-priority",
    )
    protocol_supported: ProtocolSupportedEnum = Field(
        json_schema_extra={"is_config": True},
        description="specify the protocol used for AAA.",
        alias="protocol-supported",
    )
    server_address: str = Field(
        json_schema_extra={"is_config": True}, description="The IP address of AAA server.", alias="server-address"
    )
    transport: TransportEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The transport protocol used for AAA server communication.",
        default=None,
    )
    server_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="AAA server port number.\n    Default value will depend on protocol: 49 for TACACS,\n    2083 for RADIUS/TLS. Not applicable for RADIUS/UDP.",
        ge=0,
        le=65535,
        default=None,
        alias="server-port",
    )
    server_port_authentication: int | None = Field(
        json_schema_extra={"is_config": True},
        description="AAA server authentication port number.\n    Ony of relevance for protocol supported RADIUS.",
        ge=0,
        le=65535,
        default=1812,
        alias="server-port-authentication",
    )
    server_port_accounting: int | None = Field(
        json_schema_extra={"is_config": True},
        description="AAA server accounting port number.\n    Ony of relevance for protocol supported RADIUS.",
        ge=0,
        le=65535,
        default=1813,
        alias="server-port-accounting",
    )
    shared_secret: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="The shared secret of the aaa server. The shared secret will be displayed as *.",
        min_length=0,
        max_length=200,
        default="sharedkey",
        alias="shared-secret",
    )
    role_supported: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The configured roles for the AAA server.",
        default="authentication authorization accounting",
        alias="role-supported",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Enable switch for this aaa-server.", default=True
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the response timeout of Access-Request messages sent to a AAA server in seconds.",
        ge=1,
        le=90,
        default=5,
    )
    retry: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the number of attempted Access-Request messages to a single AAA server before failing authentication.",
        ge=0,
        le=5,
        default=3,
    )
    source_ip: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Source IP address used for RADIUS communications.\n    Only of relevance for protocol supported RADIUS.",
        default="auto",
        alias="source-ip",
    )
    common_password: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="Password used for RADIUS authorization after SSH public key authentication.\nIf blank, username is reused as password for RADIUS authorization.\nOnly of relevance for protocol supported RADIUS.",
        min_length=0,
        max_length=200,
        default=None,
        alias="common-password",
    )
    auth_protocol: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The list of supported authentication protocols to use; if more than one is selected, system will try one at a time in a best-effort way.\nAuthentication will be considered unsuccessful if none of the protocols work.\nOnly of relevance for protocol supported TACACSPLUS.",
        default="pap chap",
        alias="auth-protocol",
    )
    radius_options: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Extra configuration options for each radius server.",
        default=None,
        alias="radius-options",
    )


class Niap(YangBaseModel):
    """Container for NIAP (National Information Assurance Partnership) compliance configuration and status.
    NIAP is responsible for the United States implementation of Common Criteria, see niap-ccevs.org for details.
    This container allows configuration of whether NIAP compliance is expected and provides information about the current NIAP compliance status.
    """

    expected_niap_compliance: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="The user configurable expected NIAP compliance status.\nIf set to true and the actual niap-compliance is false, the NIAP-COMPLIANCE-MISMATCH alarm will be raised.",
        default=False,
        alias="expected-niap-compliance",
    )
    niap_compliance: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="The current system NIAP compliance status.",
        default=None,
        alias="niap-compliance",
    )
    non_compliance_reason: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Provides the first 10 reasons why the system is not NIAP compliant.\nList is empty if system is NIAP compliant.",
        min_length=1,
        max_length=255,
        default=None,
        alias="non-compliance-reason",
    )


class EncryptionAlgorithmEnum_1(str, Enum):
    """Enumeration for EncryptionAlgorithmEnum

    Values:
      * xts-aes-256-plain64: AES-256 encryption in XTS mode with 64-byte block size.
    """

    XTS_AES_256_PLAIN64 = "xts-aes-256-plain64"


class IntegrityAlgorithmEnum_1(str, Enum):
    """Enumeration for IntegrityAlgorithmEnum

    Values:
      * none
      * hmac-sha2-512
    """

    NONE = "none"
    HMAC_SHA2_512 = "hmac-sha2-512"


class IntegrityStatusEnum(str, Enum):
    """Enumeration for IntegrityStatusEnum

    Values:
      * disabled
      * passed-on-bootup
      * failed-on-bootup
    """

    DISABLED = "disabled"
    PASSED_ON_BOOTUP = "passed-on-bootup"
    FAILED_ON_BOOTUP = "failed-on-bootup"


class ModeEnum_2(str, Enum):
    """Enumeration for ModeEnum

    Values:
      * encryption-only
      * encryption-with-integrity
    """

    ENCRYPTION_ONLY = "encryption-only"
    ENCRYPTION_WITH_INTEGRITY = "encryption-with-integrity"


class DbProtectionScheme(YangBaseModel):
    """Container for database protection scheme."""

    encryption_algorithm: EncryptionAlgorithmEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Encryption algorithm used for database encryption.",
        default=None,
        alias="encryption-algorithm",
    )
    integrity_algorithm: IntegrityAlgorithmEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of integrity algorithm used for DB.",
        default=None,
        alias="integrity-algorithm",
    )
    integrity_status: IntegrityStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Status of integrity check.",
        default=None,
        alias="integrity-status",
    )
    mode: ModeEnum_2 | None = Field(
        json_schema_extra={"is_config": False},
        description="Current Protection Scheme of DB. Can be changed via 'db-migrate' RPC.",
        default=None,
    )


class SignatureHashSchemeEnum(str, Enum):
    """Enumeration for SignatureHashSchemeEnum

    Values:
      * SHA2_256
      * SHA2_384
      * SHA2_512
    """

    SHA2_256 = "SHA2_256"
    SHA2_384 = "SHA2_384"
    SHA2_512 = "SHA2_512"


class SignatureAlgorithmEnum(str, Enum):
    """Enumeration for SignatureAlgorithmEnum

    Values:
      * ECDSA
      * RSA
      * none
    """

    ECDSA = "ECDSA"
    RSA = "RSA"
    NONE = "none"


class IskItem(YangBaseModel):
    """Image Signing Key list."""

    name: str = Field(json_schema_extra={"is_config": False}, description="Unique representation of the object")
    CPU: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifier for member CPUs on cards starts at 0",
        ge=0,
        default=None,
    )
    key_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the key",
        min_length=0,
        max_length=64,
        default=None,
        alias="key-name",
    )
    key_serial_number: str | None = Field(
        json_schema_extra={"is_config": False}, description="Key Serial Number", default=None, alias="key-serial-number"
    )
    issuer_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the CSA (Code Signing Appliance)",
        min_length=0,
        max_length=20,
        default=None,
        alias="issuer-name",
    )
    key_length: int | None = Field(
        json_schema_extra={"is_config": False}, description="Key length in bits", ge=0, default=None, alias="key-length"
    )
    key_payload: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Key Payload (hex format)",
        default=None,
        alias="key-payload",
    )
    is_key_in_use: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates if the key is in use in this FRU",
        default=False,
        alias="is-key-in-use",
    )
    is_key_verified: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates if the key is verified in this FRU",
        default=False,
        alias="is-key-verified",
    )
    being_deleted: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="System is in the process of deletion for this ISK.",
        default=False,
        alias="being-deleted",
    )
    KRK_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the KRK (Image root key) that signed this ISK",
        default=None,
        alias="KRK-name",
    )
    signature_hash_scheme: SignatureHashSchemeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Hashing Scheme",
        default=None,
        alias="signature-hash-scheme",
    )
    signature_algorithm: SignatureAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Signature Algorithm",
        default=None,
        alias="signature-algorithm",
    )
    signature_payload: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False}, description="Signature Payload", default=None, alias="signature-payload"
    )
    signature_gen_time: (
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
        description="Signature Generation Time",
        default=None,
        alias="signature-gen-time",
    )


class Isks(YangBaseModel):
    """Container for Image Signing Keys"""

    ISK: RestconfList[IskItem] | None = Field(
        json_schema_extra={"is_config": False}, description="Image Signing Key list.", default=None
    )


class KrkItem(YangBaseModel):
    """Image Root Key list."""

    name: str = Field(json_schema_extra={"is_config": False}, description="Unique representation of the object")
    CPU: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifier for member CPUs on cards starts at 0",
        ge=0,
        default=None,
    )
    key_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the key",
        min_length=0,
        max_length=64,
        default=None,
        alias="key-name",
    )
    key_serial_number: str | None = Field(
        json_schema_extra={"is_config": False}, description="Key Serial Number", default=None, alias="key-serial-number"
    )
    issuer_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the CSA (Code Signing Appliance)",
        min_length=0,
        max_length=20,
        default=None,
        alias="issuer-name",
    )
    key_length: int | None = Field(
        json_schema_extra={"is_config": False}, description="Key length in bits", ge=0, default=None, alias="key-length"
    )
    key_payload: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Key Payload (hex format)",
        default=None,
        alias="key-payload",
    )


class Krks(YangBaseModel):
    """Container for Image Root Keys"""

    KRK: RestconfList[KrkItem] | None = Field(
        json_schema_extra={"is_config": False}, description="Image Root Key list.", default=None
    )


class ImageKeys(YangBaseModel):
    """Container for image keys"""

    ISKs: Isks | None = Field(
        json_schema_extra={"is_config": False}, description="Container for Image Signing Keys", default=None
    )
    KRKs: Krks | None = Field(
        json_schema_extra={"is_config": False}, description="Container for Image Root Keys", default=None
    )


class InstallStatusEnum(str, Enum):
    """Enumeration for InstallStatusEnum

    Values:
      * not-installed
      * installing
      * installed
      * failed
    """

    NOT_INSTALLED = "not-installed"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"


class KeyReplacementPackage(YangBaseModel):
    """Container for KRP (Key Replacement Package)"""

    KRP_name: str | None = Field(
        json_schema_extra={"is_config": False}, description="KRP name", default=None, alias="KRP-name"
    )
    KRP_version: int | None = Field(
        json_schema_extra={"is_config": False}, description="Package version", ge=0, default=None, alias="KRP-version"
    )
    key_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the key",
        min_length=0,
        max_length=64,
        default=None,
        alias="key-name",
    )
    key_serial_number: str | None = Field(
        json_schema_extra={"is_config": False}, description="Key Serial Number", default=None, alias="key-serial-number"
    )
    issuer_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the CSA (Code Signing Appliance)",
        min_length=0,
        max_length=20,
        default=None,
        alias="issuer-name",
    )
    key_length: int | None = Field(
        json_schema_extra={"is_config": False}, description="Key length in bits", ge=0, default=None, alias="key-length"
    )
    key_payload: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Key Payload (hex format)",
        default=None,
        alias="key-payload",
    )
    KRK_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the KRK (Image root key) that signed this ISK",
        default=None,
        alias="KRK-name",
    )
    signature_hash_scheme: SignatureHashSchemeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Hashing Scheme",
        default=None,
        alias="signature-hash-scheme",
    )
    signature_algorithm: SignatureAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Signature Algorithm",
        default=None,
        alias="signature-algorithm",
    )
    signature_payload: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False}, description="Signature Payload", default=None, alias="signature-payload"
    )
    signature_gen_time: (
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
        description="Signature Generation Time",
        default=None,
        alias="signature-gen-time",
    )
    install_status: InstallStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates if this KRP has been installed in the system",
        default=None,
        alias="install-status",
    )


class VersionEnum(str, Enum):
    """Enumeration for VersionEnum

    Values:
      * v3
    """

    V3 = "v3"


class StatusEnum_2(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * in-use: Certificate is either assigned to a secure-application or otherwise in use by the system. This is deprecated; new status is 'valid'. Certificate usage is now tracked in the used-by attribute.
      * unused: Certificate is currently not being used by the system nor a secure-application. Can be assigned/used. This is deprecated; new status is 'valid'. Certificate usage is now tracked in the used-by attribute.
      * revoked: Certificate has been revoked.
      * expired: Certificate is past the validity date.
      * available: Trusted certificate is in use by the system. This is deprecated; new status is 'valid'. Certificate usage is now tracked in the used-by attribute.
      * pending-import: Certificate generated by CSR, but import not yet complete.
      * invalid: Trusted certificate is invalid due to broken trust-chain (not usable by the system). This is deprecated; new status is 'untrusted'.
      * untrusted: Certificate has a broken trust-chain.
      * future: Certificate has not yet reached the validity period.
      * valid: Certificate is not revoked, is in the validity period, and has a valid trust chain.
      * unsupported: Certificate is not usable by the system due to properties violating system policies.
    """

    IN_USE = "in-use"
    UNUSED = "unused"
    REVOKED = "revoked"
    EXPIRED = "expired"
    AVAILABLE = "available"
    PENDING_IMPORT = "pending-import"
    INVALID = "invalid"
    UNTRUSTED = "untrusted"
    FUTURE = "future"
    VALID = "valid"
    UNSUPPORTED = "unsupported"


class PublicKeyLengthEnum(str, Enum):
    """Enumeration for PublicKeyLengthEnum

    Values:
      * rsa2048
      * rsa3072
      * rsa4096
      * ecdsa256
      * ecdsa384
      * ecdsa521
      * ecdsa128
    """

    RSA2048 = "rsa2048"
    RSA3072 = "rsa3072"
    RSA4096 = "rsa4096"
    ECDSA256 = "ecdsa256"
    ECDSA384 = "ecdsa384"
    ECDSA521 = "ecdsa521"
    ECDSA128 = "ecdsa128"


class PublicKeyTypeEnum(str, Enum):
    """Enumeration for PublicKeyTypeEnum

    Values:
      * rsa
      * ecdsa
      * rsassa-pss
    """

    RSA = "rsa"
    ECDSA = "ecdsa"
    RSASSA_PSS = "rsassa-pss"


class KeyUsageTypeEnum(str, Enum):
    """Enumeration for KeyUsageTypeEnum

    Values:
      * digitalSignature: Allows using public key with a digital sign mechanism.
      * nonRepudiation: Allows using public key for verifying digital signatures.
      * keyEncipherment: Allows usage with a protocol that uses encryption keys from public key.
      * dataEncipherment: Allows public key usage to encrypt user data.
      * keyAgreement: Allows deriving of a session key from the public key.
      * keyCertSign: Allows public key to verify signature of certificates.
      * cRLSign: Allows public key to verify signature of revocation information.
      * encipherOnly: For keyEncipherment, allows the public key to be use for encryption only.
      * decipherOnly: For keyEncipherment, allows the public key to be use for decryption only.
    """

    DIGITALSIGNATURE = "digitalSignature"
    NONREPUDIATION = "nonRepudiation"
    KEYENCIPHERMENT = "keyEncipherment"
    DATAENCIPHERMENT = "dataEncipherment"
    KEYAGREEMENT = "keyAgreement"
    KEYCERTSIGN = "keyCertSign"
    CRLSIGN = "cRLSign"
    ENCIPHERONLY = "encipherOnly"
    DECIPHERONLY = "decipherOnly"


class ExtendedKeyUsageTypeEnum(str, Enum):
    """Enumeration for ExtendedKeyUsageTypeEnum

    Values:
      * serverAuth: TLS WWW Server Authentication.
      * clientAuth: TLS WWW Client Authentication.
      * codeSigning: Code Signing.
      * emailProtection: E-mail Protection (S/MIME).
      * timeStamping: Trusted Timestamping.
      * OCSPSigning: OCSP Signing.
    """

    SERVERAUTH = "serverAuth"
    CLIENTAUTH = "clientAuth"
    CODESIGNING = "codeSigning"
    EMAILPROTECTION = "emailProtection"
    TIMESTAMPING = "timeStamping"
    OCSPSIGNING = "OCSPSigning"


class RevocationModeEnum(str, Enum):
    """Enumeration for RevocationModeEnum

    Values:
      * auto: Revocation status is determined based on configured CRL/CDP/OCSP policies.
      * force-revoked: Certificate is considered revoked, without consulting CRLs or OCSP responders.
      * force-unrevoked: Certificate is considered not revoked, without consulting CRLs or OCSP responders. Note that the certificate may still be invalid and unusable if it is expired or has an invalid trust-chain.
    """

    AUTO = "auto"
    FORCE_REVOKED = "force-revoked"
    FORCE_UNREVOKED = "force-unrevoked"


class TrustedCertificateItem(YangBaseModel):
    """X509v3 CA(Root and Intermediate) certificate that the system trusts."""

    id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="A unique object identifier for the certificate.",
            min_length=1,
            max_length=128,
        )
    )
    version: VersionEnum | None = Field(
        json_schema_extra={"is_config": False}, description="X509 certificate version.", default=VersionEnum.V3
    )
    serial_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Ascii hexadecimal string representing a positive (long) integer assigned by the CA.\nIt must be unique for each certificate issued by a given CA (i.e., the issuer name and\nserial number identify a unique certificate)",
        min_length=0,
        max_length=100,
        default=None,
        alias="serial-number",
    )
    subject_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The subject field identifies the entity\nassociated with the public key stored in the subject\npublic key field.",
        min_length=1,
        max_length=1024,
        default=None,
        alias="subject-name",
    )
    issuer: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The issuer name identifies the entity that has signed\nand issued the certificate. Issuers (such as a CA or\nan RA) also issue CRLs.",
        min_length=1,
        max_length=1024,
        default=None,
    )
    trust_chain: (
        RestconfList[
            Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="List of trusted certificates that constitute this certificate's trust chain.",
        min_length=1,
        max_length=128,
        default=None,
        alias="trust-chain",
    )
    valid_from: (
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
        description="The date from which the certificate is valid.",
        default=None,
        alias="valid-from",
    )
    valid_to: (
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
        description="The date after which the certificate is deemed to have expired.",
        default=None,
        alias="valid-to",
    )
    modification_time: (
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
        description="Timestamp of certificate installation/rotation.\nThe timestamp '1970-01-01T00:00:00Z' means the modification time is unknown.",
        default=None,
        alias="modification-time",
    )
    status: StatusEnum_2 | None = Field(
        json_schema_extra={"is_config": False},
        description="The current status of the X509v3 certificate.",
        default=None,
    )
    public_key_length: PublicKeyLengthEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="X509v3 certificate public key algorithm and supported key length.",
        default=None,
        alias="public-key-length",
    )
    public_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Public/private key type for X509v3 certificate.",
        default=None,
        alias="public-key-type",
    )
    signature_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Signature algorithm key type for certificate/CRL.",
        default=None,
        alias="signature-key-type",
    )
    signature_hash_algorithm: SignatureHashAlgorithmTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Hash algorithm used for signing certificate/CRL.",
        default=None,
        alias="signature-hash-algorithm",
    )
    certificate_bytes: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A custom type that encodes the entire X.509v3 certificate\nas string in PEM(base64 encoding) format:\n\n-----BEGIN CERTIFICATE-----\n...base64 encoded X509v3 certificate....\n-----END CERTIFICATE-----",
        min_length=0,
        max_length=16384,
        default=None,
        alias="certificate-bytes",
    )
    key_usage: RestconfList[KeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="Certificate's key usage purposes.",
        default=None,
        alias="key-usage",
    )
    extended_key_usage: RestconfList[ExtendedKeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="Certificate's extended key usage purposes.",
        default=None,
        alias="extended-key-usage",
    )
    revocation_mode: RevocationModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls how the revocation status of the certificate is determined.",
        default=RevocationModeEnum.AUTO,
        alias="revocation-mode",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class LocalCertificateItem(YangBaseModel):
    """X509v3 end-entity certificate that represents a one of
    various secure application identities.
    """

    id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="A unique object identifier for the certificate.",
            min_length=1,
            max_length=128,
        )
    )
    version: VersionEnum | None = Field(
        json_schema_extra={"is_config": False}, description="X509 certificate version.", default=VersionEnum.V3
    )
    serial_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Ascii hexadecimal string representing a positive (long) integer assigned by the CA.\nIt must be unique for each certificate issued by a given CA (i.e., the issuer name and\nserial number identify a unique certificate)",
        min_length=0,
        max_length=100,
        default=None,
        alias="serial-number",
    )
    subject_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The subject field identifies the entity\nassociated with the public key stored in the subject\npublic key field.",
        min_length=1,
        max_length=1024,
        default=None,
        alias="subject-name",
    )
    issuer: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The issuer name identifies the entity that has signed\nand issued the certificate. Issuers (such as a CA or\nan RA) also issue CRLs.",
        min_length=1,
        max_length=1024,
        default=None,
    )
    trust_chain: (
        RestconfList[
            Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="List of trusted certificates that constitute this certificate's trust chain.",
        min_length=1,
        max_length=128,
        default=None,
        alias="trust-chain",
    )
    valid_from: (
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
        description="The date from which the certificate is valid.",
        default=None,
        alias="valid-from",
    )
    valid_to: (
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
        description="The date after which the certificate is deemed to have expired.",
        default=None,
        alias="valid-to",
    )
    modification_time: (
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
        description="Timestamp of certificate installation/rotation.\nThe timestamp '1970-01-01T00:00:00Z' means the modification time is unknown.",
        default=None,
        alias="modification-time",
    )
    status: StatusEnum_2 | None = Field(
        json_schema_extra={"is_config": False},
        description="The current status of the X509v3 certificate.",
        default=None,
    )
    public_key_length: PublicKeyLengthEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="X509v3 certificate public key algorithm and supported key length.",
        default=None,
        alias="public-key-length",
    )
    public_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Public/private key type for X509v3 certificate.",
        default=None,
        alias="public-key-type",
    )
    signature_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Signature algorithm key type for certificate/CRL.",
        default=None,
        alias="signature-key-type",
    )
    signature_hash_algorithm: SignatureHashAlgorithmTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Hash algorithm used for signing certificate/CRL.",
        default=None,
        alias="signature-hash-algorithm",
    )
    certificate_bytes: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A custom type that encodes the entire X.509v3 certificate\nas string in PEM(base64 encoding) format:\n\n-----BEGIN CERTIFICATE-----\n...base64 encoded X509v3 certificate....\n-----END CERTIFICATE-----",
        min_length=0,
        max_length=16384,
        default=None,
        alias="certificate-bytes",
    )
    key_usage: RestconfList[KeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="Certificate's key usage purposes.",
        default=None,
        alias="key-usage",
    )
    extended_key_usage: RestconfList[ExtendedKeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="Certificate's extended key usage purposes.",
        default=None,
        alias="extended-key-usage",
    )
    revocation_mode: RevocationModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls how the revocation status of the certificate is determined.",
        default=RevocationModeEnum.AUTO,
        alias="revocation-mode",
    )
    used_by: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of foreign keys representing secure-applications, ikev2-peers, etc., presently using the\ncertificate.",
        default=None,
        alias="used-by",
    )
    self_signed: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="True if certificate is self-signed (does not have a trust chain)",
        default=False,
        alias="self-signed",
    )
    subject_alternative_names: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Contains a list of subject alternative name (X509v3 extension SAN) entries\nseparated by <SPACE><PIPE><SPACE> delimiters (e.g. 'URI:https://www.example.com | DNS:example.com').",
        min_length=0,
        max_length=4096,
        default=None,
        alias="subject-alternative-names",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class PeerCertificateItem(YangBaseModel):
    """X509v3 end-entity certificate that represents a trusted 'remote peer' certificate
    for L1 encryption secure application.
    """

    id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="A unique object identifier for the certificate.",
            min_length=1,
            max_length=128,
        )
    )
    version: VersionEnum | None = Field(
        json_schema_extra={"is_config": False}, description="X509 certificate version.", default=VersionEnum.V3
    )
    serial_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Ascii hexadecimal string representing a positive (long) integer assigned by the CA.\nIt must be unique for each certificate issued by a given CA (i.e., the issuer name and\nserial number identify a unique certificate)",
        min_length=0,
        max_length=100,
        default=None,
        alias="serial-number",
    )
    subject_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The subject field identifies the entity\nassociated with the public key stored in the subject\npublic key field.",
        min_length=1,
        max_length=1024,
        default=None,
        alias="subject-name",
    )
    issuer: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The issuer name identifies the entity that has signed\nand issued the certificate. Issuers (such as a CA or\nan RA) also issue CRLs.",
        min_length=1,
        max_length=1024,
        default=None,
    )
    trust_chain: (
        RestconfList[
            Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="List of trusted certificates that constitute this certificate's trust chain.",
        min_length=1,
        max_length=128,
        default=None,
        alias="trust-chain",
    )
    valid_from: (
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
        description="The date from which the certificate is valid.",
        default=None,
        alias="valid-from",
    )
    valid_to: (
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
        description="The date after which the certificate is deemed to have expired.",
        default=None,
        alias="valid-to",
    )
    modification_time: (
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
        description="Timestamp of certificate installation/rotation.\nThe timestamp '1970-01-01T00:00:00Z' means the modification time is unknown.",
        default=None,
        alias="modification-time",
    )
    status: StatusEnum_2 | None = Field(
        json_schema_extra={"is_config": False},
        description="The current status of the X509v3 certificate.",
        default=None,
    )
    public_key_length: PublicKeyLengthEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="X509v3 certificate public key algorithm and supported key length.",
        default=None,
        alias="public-key-length",
    )
    public_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Public/private key type for X509v3 certificate.",
        default=None,
        alias="public-key-type",
    )
    signature_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Signature algorithm key type for certificate/CRL.",
        default=None,
        alias="signature-key-type",
    )
    signature_hash_algorithm: SignatureHashAlgorithmTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Hash algorithm used for signing certificate/CRL.",
        default=None,
        alias="signature-hash-algorithm",
    )
    certificate_bytes: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A custom type that encodes the entire X.509v3 certificate\nas string in PEM(base64 encoding) format:\n\n-----BEGIN CERTIFICATE-----\n...base64 encoded X509v3 certificate....\n-----END CERTIFICATE-----",
        min_length=0,
        max_length=16384,
        default=None,
        alias="certificate-bytes",
    )
    key_usage: RestconfList[KeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="Certificate's key usage purposes.",
        default=None,
        alias="key-usage",
    )
    extended_key_usage: RestconfList[ExtendedKeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="Certificate's extended key usage purposes.",
        default=None,
        alias="extended-key-usage",
    )
    revocation_mode: RevocationModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls how the revocation status of the certificate is determined.",
        default=RevocationModeEnum.AUTO,
        alias="revocation-mode",
    )
    used_by: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of foreign keys representing secure-applications, ikev2-peers, etc., presently using the\ncertificate.",
        default=None,
        alias="used-by",
    )
    subject_alternative_names: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Contains a list of subject alternative name (X509v3 extension SAN) entries\nseparated by <SPACE><PIPE><SPACE> delimiters (e.g. 'URI:https://www.example.com | DNS:example.com').",
        min_length=0,
        max_length=4096,
        default=None,
        alias="subject-alternative-names",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class TypeEnum_3(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * server: Secure application is a server.
      * client: Secure application is a client.
    """

    SERVER = "server"
    CLIENT = "client"


class VerifyClientCertEnum(str, Enum):
    """Enumeration for VerifyClientCertEnum

    Values:
      * disabled: Client certificate not requested or validated.
      * required: Client certificate is required and validated (for TLS Mutual Authentication).
    """

    DISABLED = "disabled"
    REQUIRED = "required"


class SecureApplicationItem(YangBaseModel):
    """A secured application represents which
    uses X509v3 certificate as its digital identity
    """

    id: str = Field(
        json_schema_extra={"is_config": True},
        description="A unique object identifier for the secure application.",
        min_length=1,
        max_length=20,
    )
    type: TypeEnum_3 | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies whether secure application acts as a server or client.",
        default=TypeEnum_3.SERVER,
    )
    active_certificate_id: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of assigned certificates for this secure application.",
        min_length=0,
        max_length=128,
        default=None,
        alias="active-certificate-id",
    )
    in_use: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Active certificate for this secure application.",
        min_length=0,
        max_length=128,
        default=None,
        alias="in-use",
    )
    status: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates whether this secure application is enabled or disabled.",
        default=None,
    )
    verify_client_cert: VerifyClientCertEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls client certificate verification behavior at TLS handshake.\nFor TLS Mutual Authentication, this should be set to 'required'.\nNote that changes to this attribute will take effect for new TLS connections; it will have no\nimpact on existing connections.",
        default=VerifyClientCertEnum.DISABLED,
        alias="verify-client-cert",
    )


class SecureApplications(YangBaseModel):
    """A collection of secured applications which
    uses X509v3 certificate as its digital identity
    """

    secure_application: RestconfList[SecureApplicationItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A secured application represents which\nuses X509v3 certificate as its digital identity",
        default=None,
        alias="secure-application",
    )


class TypeEnum_4(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * manual: CRL installed via a manual download.
      * cached: CRL automatically cached from a configured CDP or certificate CDP extension.
    """

    MANUAL = "manual"
    CACHED = "cached"


class StatusEnum_3(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * valid: CRL is in the validity period, (effective-time <= current time <= next-update).
      * future: CRL has not entered the validity period (current time < effective-time). It will not be used for revocation checking.
      * expired: CRL is no longer in the validity period (current time > next-update). An updated version will be required for revocation checking. For CRLs with type='manual', it may be necessary to manually download the updated CRL.
    """

    VALID = "valid"
    FUTURE = "future"
    EXPIRED = "expired"


class CrlItem(YangBaseModel):
    """A Certificate Revocation List (CRL) used to check if a certificate has been revoked by its
    issuer.
    """

    name: str = Field(
        json_schema_extra={"is_config": False},
        description="A unique object identifier for the CRL.\nThe format is <issuer-common-name>-<n> where 'n' is an incrementing integer to\ndifferentiate multiple CRLs from the same issuing CA.",
    )
    issuer: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The issuer name identifies the entity that has signed and issued the CRL.",
        min_length=1,
        max_length=1024,
        default=None,
    )
    crl_number: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Monotonically increasing sequence number for a given CRL scope and CRL issuer.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="crl-number",
    )
    issuing_distribution_point_uri: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies the issuer's distribution point name URI(s) for the CRL.\nOnly HTTP URIs are supported.\nThis may be an empty list.",
        min_length=1,
        max_length=1024,
        default=None,
        alias="issuing-distribution-point-uri",
    )
    effective_date: (
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
        description="The issue date of the CRL.",
        default=None,
        alias="effective-date",
    )
    next_update: (
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
        description="The date by which the next CRL will be issued.",
        default=None,
        alias="next-update",
    )
    signature_key_type: PublicKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Signature algorithm key type for certificate/CRL.",
        default=None,
        alias="signature-key-type",
    )
    signature_hash_algorithm: SignatureHashAlgorithmTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Hash algorithm used for signing certificate/CRL.",
        default=None,
        alias="signature-hash-algorithm",
    )
    type: TypeEnum_4 | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies whether CRL was manually installed or automatically cached from a CDP.",
        default=None,
    )
    status: StatusEnum_3 | None = Field(
        json_schema_extra={"is_config": False}, description="The current status of the CRL.", default=None
    )
    last_used_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of last usage of this CRL for revocation checking.",
        default=None,
        alias="last-used-time",
    )
    associated_cdp: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="The configured CDP which downloaded this CRL, if applicable.",
            min_length=1,
            max_length=64,
            default=None,
            alias="associated-cdp",
        )
    )
    downloaded_from_uri: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The HTTP URI from which this CRL was auto-downloaded.\nNot applicable to manually downloaded CRLs.\n    Only of relevance when type is cached.",
        min_length=0,
        max_length=1024,
        default=None,
        alias="downloaded-from-uri",
    )


class Crls(YangBaseModel):
    """All Certificate Revocation Lists (CRLs) presently on the system.
    This includes manually downloaded CRLs as well as those automatically retrieved from a CRL
    Distribution Point (CDP).
    """

    crl: RestconfList[CrlItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="A Certificate Revocation List (CRL) used to check if a certificate has been revoked by its\nissuer.",
        default=None,
    )


class CdpItem(YangBaseModel):
    """A CRL Distribution Point (CDP) for automatic download and periodic refresh of a specified
    CRL.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique object identifier for the CDP.",
        min_length=1,
        max_length=64,
    )
    url: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:http://([^\\s/$.?#][^\\s/]*)/([^\\s]+))$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="HTTP URL of CRL. The CRL will be fetched from this location.\nThe format is 'http://<host>[:<port>]/<path_to_crl_file>' where\n    - '<host>' may be IPv4/v6 address, or DNS name of the distribution point,\n    - '<port>' is optional,\n    - '<path_to_crl_file>' is the path to the CRL file, conventionally with the .crl extension\nFor example: http://crl.example.org/pki/myCA.crl",
            min_length=0,
            max_length=1024,
        )
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables automatic download and periodic refresh of the CRL.\nEnabling will immediately trigger a CRL auto-download.\nWhen disabled, no CRL refresh/updates will be performed, but existing CRLs are\nunaffected.",
        default=False,
    )
    refresh_interval: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines when CRL should be refreshed/updated.\nIf 'use-next-update' is specified, the next refresh time is defined by the current CRL\nnext-update field.\nRefresh interval is provided using the following syntax:\n   '[xw] [xd] [xh] [xm] [xs]'\nwhere:\n   w(eeks), d(ays), h(ours), m(inutes), s(seconds).\nExamples:\n   2w        -- two weeks\n   5d 12h    -- 5 days and 12 hours\n   1h 7m 30s -- 1 hour, 7 minutes and 30 seconds",
        default="use-next-update",
        alias="refresh-interval",
    )
    next_update_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of next CRL update.",
        default=None,
        alias="next-update-time",
    )
    last_update_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of most recent CRL update.",
        default=None,
        alias="last-update-time",
    )
    last_update_result: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Result of the most recent CRL update.",
        min_length=0,
        max_length=255,
        default=None,
        alias="last-update-result",
    )


class Cdps(YangBaseModel):
    """All manually configured CRL Distribution Points (CDPs).
    Each CDP will support download and auto-refreshing of a specified CRL.
    """

    cdp: RestconfList[CdpItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A CRL Distribution Point (CDP) for automatic download and periodic refresh of a specified\nCRL.",
        default=None,
    )


class OcspServerItem(YangBaseModel):
    """A manually-configured Online Certificate Status Protocol (OCSP) responder for certificate revocation status checking."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique object identifier for the OCSP responder.",
        min_length=1,
        max_length=64,
    )
    url: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:http://([^\\s/$.?#][^\\s/]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="HTTP URL of OCSP responder.\nThe format is 'http://<host>[:<port>]' where\n    - '<host>' may be IPv4/v6 address, or DNS name of the server hosting the OCSP responder,\n    - '<port>' is the optional port number, otherwise default HTTP port is used (80)\nFor example: http://ocsp.example.org",
        min_length=0,
        max_length=1024,
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls whether this OCSP responder can be consulted for certificate revocation status.",
        default=False,
    )
    priority: int = Field(
        json_schema_extra={"is_config": True},
        description="This is used to sort the OCSP responders in order of precedence.\nLower numbered OCSP responders are consulted before higher numbered ones.",
        ge=1,
        le=10,
    )
    last_query: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp of last successful query.",
        default=None,
        alias="last-query",
    )


class OcspServers(YangBaseModel):
    """A prioritized list of Online Certificate Status Protocol (OCSP) responders to consult for certificate revocation status.
    These are employed when no usable OCSP URL is available via the certificate's Authority Information Access (AIA) extension.
    """

    ocsp_server: RestconfList[OcspServerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A manually-configured Online Certificate Status Protocol (OCSP) responder for certificate revocation status checking.",
        default=None,
        alias="ocsp-server",
    )


class CertificateRevocation(YangBaseModel):
    """All objects related to certificate revocation.
    This includes Certificate Revocation Lists (CRLs) and CRL Distribution Points (CDPs).
    """

    crls: Crls | None = Field(
        json_schema_extra={"is_config": False},
        description="All Certificate Revocation Lists (CRLs) presently on the system.\nThis includes manually downloaded CRLs as well as those automatically retrieved from a CRL\nDistribution Point (CDP).",
        default=None,
    )
    cdps: Cdps | None = Field(
        json_schema_extra={"is_config": True},
        description="All manually configured CRL Distribution Points (CDPs).\nEach CDP will support download and auto-refreshing of a specified CRL.",
        default=None,
    )
    ocsp_servers: OcspServers | None = Field(
        json_schema_extra={"is_config": True},
        description="A prioritized list of Online Certificate Status Protocol (OCSP) responders to consult for certificate revocation status.\nThese are employed when no usable OCSP URL is available via the certificate's Authority Information Access (AIA) extension.",
        default=None,
        alias="ocsp-servers",
    )


class Certificates(YangBaseModel):
    """All system managed local/trusted/peer X509v3 certificates on the system
    that were imported by download mechanism in PKCS#12 or PKCS#7 secure bundles.
    Also includes all certificate revocation related objects.
    """

    trusted_certificate: RestconfList[TrustedCertificateItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="X509v3 CA(Root and Intermediate) certificate that the system trusts.",
        default=None,
        alias="trusted-certificate",
    )
    local_certificate: RestconfList[LocalCertificateItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="X509v3 end-entity certificate that represents a one of\nvarious secure application identities.",
        default=None,
        alias="local-certificate",
    )
    peer_certificate: RestconfList[PeerCertificateItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="X509v3 end-entity certificate that represents a trusted 'remote peer' certificate\nfor L1 encryption secure application.",
        default=None,
        alias="peer-certificate",
    )
    secure_applications: SecureApplications | None = Field(
        json_schema_extra={"is_config": True},
        description="A collection of secured applications which\nuses X509v3 certificate as its digital identity",
        default=None,
        alias="secure-applications",
    )
    certificate_revocation: CertificateRevocation | None = Field(
        json_schema_extra={"is_config": True},
        description="All objects related to certificate revocation.\nThis includes Certificate Revocation Lists (CRLs) and CRL Distribution Points (CDPs).",
        default=None,
        alias="certificate-revocation",
    )


class DataPathEncryptionSanIkeIdMatchEnum(str, Enum):
    """Enumeration for DataPathEncryptionSanIkeIdMatchEnum

    Values:
      * match
      * ignore
    """

    MATCH = "match"
    IGNORE = "ignore"


class HostCardEncryptionCapabilityEnum(str, Enum):
    """Enumeration for HostCardEncryptionCapabilityEnum

    Values:
      * yes: Indicates that the host card supports encryption.
      * no: Indicates that the host card does not support encryption.
      * unknown: The host card's encryption capability is unknown.
    """

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class ScopeEnum(str, Enum):
    """Enumeration for ScopeEnum

    Values:
      * data-path-encryption: IKEv2 used in GX's data path encryption.
      * management-ipsec: IKEv2 used for C-OS control and management plane security.
    """

    DATA_PATH_ENCRYPTION = "data-path-encryption"
    MANAGEMENT_IPSEC = "management-ipsec"


class Ipv4EndpointsItem(YangBaseModel):
    """All local IPv4 end-points on which this IKEv2 instance is listening for incoming IKE negotiations."""

    ip_address: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                v,
            )
        ),
    ] = Field(json_schema_extra={"is_config": False}, alias="ip-address")
    port: int | None = Field(
        json_schema_extra={"is_config": False}, description="The IKEv2 UDP listen port.", ge=0, default=500
    )


class Ipv6EndpointsItem(YangBaseModel):
    """All local IPv6 end-points on which this IKEv2 instance is listening for incoming IKE negotiations."""

    ip_address: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                v,
            )
        ),
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
            )
        ),
    ] = Field(json_schema_extra={"is_config": False}, alias="ip-address")
    port: int | None = Field(
        json_schema_extra={"is_config": False}, description="The IKEv2 UDP listen port.", ge=0, default=500
    )


class SupportingInterfaceItem(YangBaseModel):
    """List of all local interfaces on which this local IKEv2 instance listens for incoming IKE negotiations."""

    interface: str = Field(
        json_schema_extra={"is_config": False},
        description="A reference to the IPv4/IPv6 interface.",
        min_length=1,
        max_length=64,
    )
    ipv4_endpoints: RestconfList[Ipv4EndpointsItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="All local IPv4 end-points on which this IKEv2 instance is listening for incoming IKE negotiations.",
        default=None,
        alias="ipv4-endpoints",
    )
    ipv6_endpoints: RestconfList[Ipv6EndpointsItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="All local IPv6 end-points on which this IKEv2 instance is listening for incoming IKE negotiations.",
        default=None,
        alias="ipv6-endpoints",
    )


class IkeIdentityTypeEnum(str, Enum):
    """Enumeration for IkeIdentityTypeEnum

    Values:
      * ipv4-address: Specifies the identity as an IPv4 address.
      * ipv6-address: Specifies the identity as an IPv6 address.
      * fqdn: Specifies the identity as a Fully-Qualified Domain Name (FQDN) string.
      * dnx509: Specifies the identity as an ASN.1 X.500 Distinguished Name.
      * id-key: Opaque octet stream that may be used to pass vendor-specific information for proprietary types of identification.
    """

    IPV4_ADDRESS = "ipv4-address"
    IPV6_ADDRESS = "ipv6-address"
    FQDN = "fqdn"
    DNX509 = "dnx509"
    ID_KEY = "id-key"


class AuthenticationSchemeEnum(str, Enum):
    """Enumeration for AuthenticationSchemeEnum

    Values:
      * x.509-certificate
      * pre-shared-key
    """

    X_509_CERTIFICATE = "x.509-certificate"
    PRE_SHARED_KEY = "pre-shared-key"


class PreSharedKeyTypeEnum(str, Enum):
    """Enumeration for PreSharedKeyTypeEnum

    Values:
      * ascii
      * hex
      * hash
    """

    ASCII = "ascii"
    HEX = "hex"
    HASH = "hash"


class ProtocolIdEnum(str, Enum):
    """Enumeration for ProtocolIdEnum

    Values:
      * IKE
      * ESP
    """

    IKE = "IKE"
    ESP = "ESP"


class EncryptionAlgorithmItem(YangBaseModel):
    """A list of IKE SA encryption algorithms advertised to the far-end IKE peer."""

    algorithm: EncryptionAlgorithmEnum = Field(
        json_schema_extra={"is_config": True}, description="The encryption algorithm for the IKE SA."
    )
    key_length: EncryptionKeyLengthEnum = Field(
        json_schema_extra={"is_config": True},
        description="The IKE SA encryption algorithm key length.",
        alias="key-length",
    )


class IkeSaPrfEnum(str, Enum):
    """Enumeration for IkeSaPrfEnum

    Values:
      * hmac-sha2-256
      * hmac-sha2-384
      * hmac-sha2-512
      * hmac-sha1
    """

    HMAC_SHA2_256 = "hmac-sha2-256"
    HMAC_SHA2_384 = "hmac-sha2-384"
    HMAC_SHA2_512 = "hmac-sha2-512"
    HMAC_SHA1 = "hmac-sha1"


class IkeSaProposalItem(YangBaseModel):
    """A list of protocol proposals when negotiating the IKE SA with the far-end IKE peer."""

    number: int = Field(json_schema_extra={"is_config": True}, description="The proposal number for the IKE SA.", ge=1)
    protocol_id: ProtocolIdEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The protocol ID (type) for which the IKE proposal applies to.",
        default=ProtocolIdEnum.IKE,
        alias="protocol-id",
    )
    encryption_algorithm: RestconfList[EncryptionAlgorithmItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of IKE SA encryption algorithms advertised to the far-end IKE peer.",
        default=None,
        alias="encryption-algorithm",
    )
    integrity_algorithm: RestconfList[IntegrityAlgorithmEnum] = Field(
        json_schema_extra={"is_config": True},
        description="A list of IPsec SA integrity algorithms advertised to the far-end IKE peer.",
        alias="integrity-algorithm",
    )
    dh_group: RestconfList[ChildSaDhGroupEnum] = Field(
        json_schema_extra={"is_config": True},
        description="A list of IKE SA Diffie-Hellman groups advertised to the far-end IKE peer.",
        alias="dh-group",
    )
    prf: RestconfList[IkeSaPrfEnum] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of IKE SA pseudo-random functions advertised to the far-end IKE peer.",
        default=None,
    )


class LocalSubnetItem(YangBaseModel):
    """This is a list of ranges of IPv4/IPv6
    addresses (unicast, broadcast (IPv4 only)).
    """

    prefix: str = Field(json_schema_extra={"is_config": True})


class RemoteSubnetItem(YangBaseModel):
    """This is a list of ranges of IPv4/IPv6
    addresses (unicast, broadcast (IPv4 only)).
    """

    prefix: str = Field(json_schema_extra={"is_config": True})


class LocalPortsItem(YangBaseModel):
    """A list of local ports ranges associated with this traffic selector."""

    start: int | str = Field(
        json_schema_extra={"is_config": True},
        description="The port number where the range starts or a predefined value (all, opaque).",
    )
    stop: int = Field(
        json_schema_extra={"is_config": True}, description="The port number where the range ends.", ge=0, le=65535
    )


class RemotePortsItem(YangBaseModel):
    """A list of remote ports ranges associated with this traffic selector."""

    start: int | str = Field(
        json_schema_extra={"is_config": True},
        description="The port number where the range starts or a predefined value (all, opaque).",
    )
    stop: int = Field(
        json_schema_extra={"is_config": True}, description="The port number where the range ends", ge=0, le=65535
    )


class IpsecTrafficSelectorItem(YangBaseModel):
    """A list of traffic selectors associated with an IPSec SPD entry."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique name to identify this IPsec traffic selector entry.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A system-populated access identifier for this traffic selector entry.",
        min_length=1,
        max_length=64,
        default=None,
    )
    local_subnet: RestconfList[LocalSubnetItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="This is a list of ranges of IPv4/IPv6\naddresses (unicast, broadcast (IPv4 only)).",
        default=None,
        alias="local-subnet",
    )
    remote_subnet: RestconfList[RemoteSubnetItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="This is a list of ranges of IPv4/IPv6\naddresses (unicast, broadcast (IPv4 only)).",
        default=None,
        alias="remote-subnet",
    )
    next_layer_protocol: int | str | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the inner protocol (upper layer), obtained\nfrom the IPv4 protocol or the IPv6 next header field.",
        default="any",
        alias="next-layer-protocol",
    )
    local_ports: RestconfList[LocalPortsItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of local ports ranges associated with this traffic selector.",
        default=None,
        alias="local-ports",
    )
    remote_ports: RestconfList[RemotePortsItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of remote ports ranges associated with this traffic selector.",
        default=None,
        alias="remote-ports",
    )


class ActionEnum(str, Enum):
    """Enumeration for ActionEnum

    Values:
      * protect
      * bypass
      * discard
    """

    PROTECT = "protect"
    BYPASS = "bypass"
    DISCARD = "discard"


class IpsecProtocolEnum(str, Enum):
    """Enumeration for IpsecProtocolEnum

    Values:
      * ESP
    """

    ESP = "ESP"


class ModeEnum_3(str, Enum):
    """Enumeration for ModeEnum

    Values:
      * tunnel
      * transport
    """

    TUNNEL = "tunnel"
    TRANSPORT = "transport"


class IpsecSaReKey(YangBaseModel):
    """Contains the rekeying configurations of an IPSec SPD entry."""

    frequency: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The rekeying frequency for the IPsec child\nsecurity association with the far-end peer.",
        ge=3600,
        le=86400,
        default=14400,
    )
    bytes: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="The rekeying frequency for the IPsec child\nsecurity association with the far-end peer\nbased on amount of bytes transmitted.",
        default="1073741824",
    )
    packets: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="The rekeying frequency for the IPsec child\nsecurity association with the far-end peer\nbased on amount of packets transmitted.",
        default="disabled",
    )


class EncryptionAlgorithmItem(YangBaseModel):
    """A list of IPsec SA encryption algorithms
    advertised to the far-end IKE peer.
    """

    algorithm: EncryptionAlgorithmEnum = Field(
        json_schema_extra={"is_config": True}, description="The encryption algorithm for the IPsec SA."
    )
    key_length: EncryptionKeyLengthEnum = Field(
        json_schema_extra={"is_config": True},
        description="The IPsec SA encryption algorithm key length.",
        alias="key-length",
    )


class IpsecSaProposalItem(YangBaseModel):
    """A list of protocol proposals when negotiating the IPsec SA
    for this SPD entry with the far-end IKE peer.
    """

    number: int = Field(
        json_schema_extra={"is_config": True}, description="The proposal number for the IPsec SA.", ge=1
    )
    protocol_id: ProtocolIdEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The protocol ID (type) for which the IPsec Child SA proposal applies to.",
        default=ProtocolIdEnum.ESP,
        alias="protocol-id",
    )
    encryption_algorithm: RestconfList[EncryptionAlgorithmItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of IPsec SA encryption algorithms\nadvertised to the far-end IKE peer.\n\nCondition (when): ../../ipsec-protocol = 'ESP'",
        default=None,
        alias="encryption-algorithm",
    )
    integrity_algorithm: RestconfList[IntegrityAlgorithmEnum] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of IPsec SA integrity algorithms\nadvertised to the far-end IKE peer.",
        default=None,
        alias="integrity-algorithm",
    )
    dh_group: RestconfList[ChildSaDhGroupEnum] = Field(
        json_schema_extra={"is_config": True},
        description="A list of IPsec SA Diffie-Hellman groups\nadvertised to the far-end IKE peer. NOTE:\nThe 'min-elements' is 1, which means perfect\nforward secrecy (PFS) for IPsec Child SA is\nalways enabled.",
        alias="dh-group",
    )


class IpsecSpdEntryItem(YangBaseModel):
    """A list of SPD entries associated with an IPSec IKEv2 peer."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique name to identify this SPD entry.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A system-populated access identifier for this SPD entry.",
        min_length=1,
        max_length=64,
        default=None,
    )
    priority: int = Field(
        json_schema_extra={"is_config": True},
        description="A priority value for each SPD entry. This is\nused to give precedence to the SPD entries.",
        ge=0,
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable label/description.",
        min_length=0,
        max_length=128,
        default=None,
    )
    ipsec_traffic_selector: RestconfList[IpsecTrafficSelectorItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of traffic selectors associated with an IPSec SPD entry.",
        default=None,
        alias="ipsec-traffic-selector",
    )
    action: ActionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the IPsec treatment given to the IP datagrams.",
        default=ActionEnum.PROTECT,
    )
    ipsec_protocol: IpsecProtocolEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the use of ESP or AH IPsec protocols.\n\nCondition (when): ../action = 'protect'",
        default=IpsecProtocolEnum.ESP,
        alias="ipsec-protocol",
    )
    mode: ModeEnum_3 | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates if the IPsec session should operate in\ntransport or tunnel mode.\n\nCondition (when): ../action = 'protect'",
        default=ModeEnum_3.TUNNEL,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    esn: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Extended Sequence Number (ESN) support.", default=True
    )
    ipsec_sa_re_key: IpsecSaReKey | None = Field(
        json_schema_extra={"is_config": True},
        description="Contains the rekeying configurations of an IPSec SPD entry.\n\nCondition (when): ../action = 'protect'",
        default=None,
        alias="ipsec-sa-re-key",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    ipsec_sa_proposal: RestconfList[IpsecSaProposalItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of protocol proposals when negotiating the IPsec SA\nfor this SPD entry with the far-end IKE peer.\n\nCondition (when): action = 'protect'",
        default=None,
        alias="ipsec-sa-proposal",
    )
    anti_replay_window: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the replay window size tolerance.\n\nCondition (when): ../action = 'protect'",
        default="64",
        alias="anti-replay-window",
    )
    dynamic_ts: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates whether dynamic traffic selector is enabled in this SPD entry.",
        default=EnableSwitchEnum.DISABLED,
        alias="dynamic-ts",
    )


class SecurityPolicyDatabase(YangBaseModel):
    """Represents the Security Policy Database (SPD) that
    specifies what services are to be offered to IP datagrams
    (in case of management IPsec) or to data path encryption
    facilities.
    """

    associated_secure_entity: (
        RestconfList[Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))]] | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="List of all SPD entries associated with with\nthis far-end peer for which IKE negotiates security\nassociations (keys). The SAs can either be for data path\nencryption, or IPsec.\nOnly of relevance for scope data path encryption.",
        min_length=1,
        max_length=64,
        default=None,
        alias="associated-secure-entity",
    )
    ipsec_spd_entry: RestconfList[IpsecSpdEntryItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of SPD entries associated with an IPSec IKEv2 peer.",
        default=None,
        alias="ipsec-spd-entry",
    )


class Ikev2PeerItem(YangBaseModel):
    """List of remote IKE peers associated with this local IKE instance."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique identifier for each IKE peer association.",
        min_length=1,
        max_length=64,
    )
    destination: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The IPv4/IPv6 address or the domain name of the far-end IKE peer.\n    Only of relevance for scope management ipsec and name not global.",
        default=None,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The UDP port on which the IKE session exists with the far-end IKE peer.\n    Only of relevance for scope management ipsec and name not global.",
        ge=0,
        le=65535,
        default=500,
    )
    dpd_delay: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The interval to check the liveness of a peer actively.\n    Only of relevance for scope management ipsec and name not global.",
        ge=0,
        default=30,
        alias="dpd-delay",
    )
    keying_tries: int | str | None = Field(
        json_schema_extra={"is_config": True},
        description="The number of rekeying attempts once a peer is considered dead.\n    Only of relevance for scope management ipsec and name not global.",
        default="infinite",
        alias="keying-tries",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    local_identity_type: IkeIdentityTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of local identity.",
        default=IkeIdentityTypeEnum.ID_KEY,
        alias="local-identity-type",
    )
    local_identity: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Identity of local IKE instance.",
        min_length=1,
        max_length=255,
        default=None,
        alias="local-identity",
    )
    peer_identity_type: IkeIdentityTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of peer identity.",
        default=IkeIdentityTypeEnum.ID_KEY,
        alias="peer-identity-type",
    )
    peer_identity: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Identity of remote IKE instance.",
        min_length=1,
        max_length=255,
        default=None,
        alias="peer-identity",
    )
    authentication_scheme: AuthenticationSchemeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="IKEv2 authentication mechanism with the peer.",
        default=AuthenticationSchemeEnum.X_509_CERTIFICATE,
        alias="authentication-scheme",
    )
    re_key_frequency: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The re-key frequency for the IKE security association with the far-end IKE peer.\n   Range and default values may be context-specific.",
        ge=3600,
        le=86400,
        default=28800,
        alias="re-key-frequency",
    )
    re_auth_frequency: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The re-authentication frequency for the IKE security association with the far-end IKE peer.\n   Range and default values may be context-specific",
        ge=3600,
        le=604800,
        default=43200,
        alias="re-auth-frequency",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    pre_shared_key_type: PreSharedKeyTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The type of pre-shared key scheme.\n\nCondition (when): ../authentication-scheme='pre-shared-key'",
        default=None,
        alias="pre-shared-key-type",
    )
    psk_ascii: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="Plain-text ASCII value for the PSK.\n\nCondition (when): ../pre-shared-key-type='ascii'",
        min_length=8,
        max_length=128,
        default=None,
        alias="psk-ascii",
    )
    psk_hex: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9A-Fa-f][0-9A-Fa-f])*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="Binary, hexadecimal value for the PSK.\n\nCondition (when): ../pre-shared-key-type='hex'",
            min_length=16,
            max_length=256,
            default=None,
            alias="psk-hex",
        )
    )
    psk_hash: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9A-Fa-f][0-9A-Fa-f])*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="HMAC SHA512 'Key Pad for IKEv2' with PSK (IETF RFC 7296).\n\nCondition (when): ../../../scope='data-path-encryption' and ../pre-shared-key-type='hash'",
            min_length=128,
            max_length=128,
            default=None,
            alias="psk-hash",
        )
    )
    interface: str | None = Field(
        json_schema_extra={"is_config": True},
        description="A reference to a supported IPv4/IPv6 interface.\n    Only of relevance for scope management ipsec and name not global.",
        min_length=1,
        max_length=64,
        default=None,
    )
    psk_configured_timestamp: (
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
        description="Local NE timestamp when the PSK was configured.\n\nCondition (when): ../../../scope='data-path-encryption' and  ../authentication-scheme='pre-shared-key'",
        default=None,
        alias="psk-configured-timestamp",
    )
    psk_lifetime: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Absolute time duration in days after which the PSK will expire.\n\nCondition (when): ../../../scope='data-path-encryption' and  ../authentication-scheme='pre-shared-key' and ../psk-lifetime-enable='true'",
        ge=7,
        le=180,
        default=90,
        alias="psk-lifetime",
    )
    psk_expiration_warning: int | None = Field(
        json_schema_extra={"is_config": True},
        description="An absolute time duration (in days) at which the NE provides a warning when the PSK is about to expire .\n\nCondition (when): ../../../scope='data-path-encryption' and  ../authentication-scheme='pre-shared-key' and ../psk-lifetime-enable='true'",
        ge=1,
        le=173,
        default=14,
        alias="psk-expiration-warning",
    )
    psk_lifetime_enable: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates whether PSK lifetime notification is enabled or disabled\n\nCondition (when): ../../../scope='data-path-encryption' and  ../authentication-scheme='pre-shared-key'",
        default=True,
        alias="psk-lifetime-enable",
    )
    local_certificate: (
        RestconfList[
            Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="The locally installed certificates that the local IKEv2 instance\nuses with this particular IKE peer for purposes of authentication.\nCustomers can pick one or more certificates from the list of\nlocally installed certificates to use during IKE authentication\nwith this far-end IKE peer. This attribute is a 'list' that\nallows for multiple certificates to be added → This helps in\nrotating the local certificate.\n\nCondition (when): ../../../scope != 'management-ipsec' or (../name != 'global' and ../authentication-scheme='x.509-certificate')",
        min_length=1,
        max_length=128,
        default=None,
        alias="local-certificate",
    )
    peer_certificate: (
        RestconfList[
            Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="The locally installed list of peer certificates that the\ninstance uses to authenticate the far-end IKE peer. These\ncertificates indicate the identity of this far-end peer.\nCustomers can indicate multiple certificates from the list of\nlocally installed 'peer' certificates to use during IKE\nauthentication with this far-end IKE peer. This attribute\nis a 'list' that allows for multiple certificates to be\nadded → This helps in certificate rotation and revocation.\nOnly of relevance for scope for data path encryption.",
        min_length=1,
        max_length=128,
        default=None,
        alias="peer-certificate",
    )
    last_used_local_certificate: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="A reference to the specific local entity leaf certificate\nthat was last used during the IKE authentication with the\nfar-end peer.\n\nCondition (when): ../authentication-scheme='x.509-certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="last-used-local-certificate",
    )
    last_used_peer_certificate: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="A reference to the specific peer leaf certificate\nthat was last used to authenticate the far-end IKE peer.\n\nCondition (when): ../../../scope='data-path-encryption' and ../authentication-scheme='x.509-certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="last-used-peer-certificate",
    )
    re_key_fail_policy: ReKeyFailPolicyEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the NE's policy and consequent action when\nre-keying the IKE security association is unsuccessful.\nOnly of release for scope for data path encryption.",
        default=ReKeyFailPolicyEnum.CONTINUE_TRAFFIC,
        alias="re-key-fail-policy",
    )
    re_key_traffic_kill_offset: int | None = Field(
        json_schema_extra={"is_config": True},
        description="If the re-key fail policy is set to KILL-TRAFFIC,\nthis attribute indicates the amount of time the\n   system waits before killing all encrypted data\n   security associations that are tied to this IKE SA.\n\nCondition (when): ../../../scope='data-path-encryption' and ../re-key-fail-policy='kill-traffic'",
        ge=0,
        le=86400,
        default=0,
        alias="re-key-traffic-kill-offset",
    )
    re_auth_fail_policy: ReKeyFailPolicyEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the NE's policy and consequent action when\nre-authenticating the far-end IKE peer is unsuccessful.\nOnly of relevance for scope for data path encryption.",
        default=ReKeyFailPolicyEnum.KILL_TRAFFIC,
        alias="re-auth-fail-policy",
    )
    re_auth_traffic_kill_offset: int | None = Field(
        json_schema_extra={"is_config": True},
        description="If the re-authentication fail policy is set to\nKILL-TRAFFIC, this attribute indicates the\namount of time the system waits before killing\nall Child SAs that are associated with this IKE SA.\n\nCondition (when): ../../../scope='data-path-encryption' and ../re-auth-fail-policy='kill-traffic'",
        ge=0,
        le=86400,
        default=0,
        alias="re-auth-traffic-kill-offset",
    )
    ike_sa_proposal: RestconfList[IkeSaProposalItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of protocol proposals when negotiating the IKE SA with the far-end IKE peer.",
        default=None,
        alias="ike-sa-proposal",
    )
    security_policy_database: SecurityPolicyDatabase | None = Field(
        json_schema_extra={"is_config": True},
        description="Represents the Security Policy Database (SPD) that\nspecifies what services are to be offered to IP datagrams\n(in case of management IPsec) or to data path encryption\nfacilities.",
        default=None,
        alias="security-policy-database",
    )


class PeerAuthorizationDatabase(YangBaseModel):
    """Container: peer-authorization-database"""

    ikev2_peer: RestconfList[Ikev2PeerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of remote IKE peers associated with this local IKE instance.",
        default=None,
        alias="ikev2-peer",
    )


class Ikev2LocalInstanceItem(YangBaseModel):
    """List of local IKE protocol daemon instance."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name (ID) of the local IKE protocol daemon instance.",
        min_length=1,
        max_length=64,
    )
    host_card_encryption_capability: HostCardEncryptionCapabilityEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates whether the card on which this IKEv2 local instance is\nrunning, supports the ability to do encryption.\n   Only of relevance for scope data path encryption.",
        default=HostCardEncryptionCapabilityEnum.UNKNOWN,
        alias="host-card-encryption-capability",
    )
    scope: ScopeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The scope of the IKEv2 instance for which security\nassociations (SA) are being negotiated.",
        default=None,
    )
    host_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = Field(
        json_schema_extra={"is_config": False},
        description="The reference to the service card on which this\nIKEv2 protocol instance is running.",
        min_length=1,
        max_length=64,
        default=None,
        alias="host-card",
    )
    started_time: (
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
        description="Local system timestamp when this IKEv2 instance\nwas started.",
        default=None,
        alias="started-time",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    local_address_assignment_method: OscControlEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Local IP address assignment method for IKEv2 channel.\n    Only of relevance for scope data path encryption.",
        default=OscControlEnum.AUTO,
        alias="local-address-assignment-method",
    )
    local_address: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Local IPv4 address for IKEv2 channel with prefix-length 32.",
        default="0.0.0.0",
        alias="local-address",
    )
    supporting_interface: RestconfList[SupportingInterfaceItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of all local interfaces on which this local IKEv2 instance listens for incoming IKE negotiations.",
        default=None,
        alias="supporting-interface",
    )
    peer_authorization_database: PeerAuthorizationDatabase | None = Field(
        json_schema_extra={"is_config": True}, default=None, alias="peer-authorization-database"
    )


class Ikev2(YangBaseModel):
    """Set of attributes that describe the properties of an IKEv2 protocol
    daemon/instance that runs as part of the C-OS system software.
    """

    data_path_encryption_san_ike_id_match: DataPathEncryptionSanIkeIdMatchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="A global, L1 encryption-specific policy that indicates whether the NE must\nvalidate Certificate subject alternate name to match the IKE ID (OPT-IN) or not (OPT-OUT).",
        default=DataPathEncryptionSanIkeIdMatchEnum.MATCH,
        alias="data-path-encryption-san-ike-id-match",
    )
    ikev2_local_instance: RestconfList[Ikev2LocalInstanceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of local IKE protocol daemon instance.",
        default=None,
        alias="ikev2-local-instance",
    )


class FipsStateEnum(str, Enum):
    """Enumeration for FipsStateEnum

    Values:
      * fips-pre-operational-self-test: Node is in FIPS pre-operational self test phase.
      * fips-error: Node landed into FIPS error state.
      * fips-idle: Pre-operational self test passed resulting in FIPS idle state.
    """

    FIPS_PRE_OPERATIONAL_SELF_TEST = "fips-pre-operational-self-test"
    FIPS_ERROR = "fips-error"
    FIPS_IDLE = "fips-idle"


class Fips(YangBaseModel):
    """FIPS state machine and error reporting."""

    fips_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="User set mode of FIPS. This flag is set via fips RPC.",
        default=EnableSwitchEnum.DISABLED,
        alias="fips-mode",
    )
    fips_state: FipsStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current state of FIPS service.\n\nCondition (when): ../fips-mode = 'enabled'",
        default=FipsStateEnum.FIPS_PRE_OPERATIONAL_SELF_TEST,
        alias="fips-state",
    )
    fips_error_reason: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Each entry having reason for fips error per card; if no failures exist, no entries will be seen.\n\nCondition (when): ../fips-state = 'fips-error'",
        min_length=1,
        max_length=255,
        default=None,
        alias="fips-error-reason",
    )


class Security(YangBaseModel):
    """Top level security container."""

    security_policies: SecurityPolicies | None = Field(
        json_schema_extra={"is_config": True},
        description="Container with several flags that represent security policies of the system.",
        default=None,
        alias="security-policies",
    )
    authorization: Authorization | None = Field(
        json_schema_extra={"is_config": True},
        description="Top level container for authorizations settings.",
        default=None,
    )
    user: RestconfList[UserItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="User details. Can represent both locally configured users, as well as temporary remote users.",
        default=None,
    )
    user_group: RestconfList[UserGroupItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of user groups, each one with its own access permissions.\nEach user will be associated with a list of groups, and will derive its permissions from them.",
        default=None,
        alias="user-group",
    )
    session: RestconfList[SessionItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of currently established management layer sessions.",
        default=None,
    )
    aaa_server: RestconfList[AaaServerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of AAA servers - RADIUS or TACACS+.",
        default=None,
        alias="aaa-server",
    )
    niap: Niap | None = Field(
        json_schema_extra={"is_config": True},
        description="Container for NIAP (National Information Assurance Partnership) compliance configuration and status.\nNIAP is responsible for the United States implementation of Common Criteria, see niap-ccevs.org for details.\nThis container allows configuration of whether NIAP compliance is expected and provides information about the current NIAP compliance status.",
        default=None,
    )
    db_protection_scheme: DbProtectionScheme | None = Field(
        json_schema_extra={"is_config": False},
        description="Container for database protection scheme.",
        default=None,
        alias="db-protection-scheme",
    )
    image_keys: ImageKeys | None = Field(
        json_schema_extra={"is_config": False}, description="Container for image keys", default=None, alias="image-keys"
    )
    key_replacement_package: KeyReplacementPackage | None = Field(
        json_schema_extra={"is_config": False},
        description="Container for KRP (Key Replacement Package)",
        default=None,
        alias="key-replacement-package",
    )
    certificates: Certificates | None = Field(
        json_schema_extra={"is_config": True},
        description="All system managed local/trusted/peer X509v3 certificates on the system\nthat were imported by download mechanism in PKCS#12 or PKCS#7 secure bundles.\nAlso includes all certificate revocation related objects.",
        default=None,
    )
    ikev2: Ikev2 | None = Field(
        json_schema_extra={"is_config": True},
        description="Set of attributes that describe the properties of an IKEv2 protocol\ndaemon/instance that runs as part of the C-OS system software.",
        default=None,
    )
    fips: Fips | None = Field(
        json_schema_extra={"is_config": False}, description="FIPS state machine and error reporting.", default=None
    )


class AssignmentMethodEnum(str, Enum):
    """Enumeration for AssignmentMethodEnum

    Values:
      * both: Assignment method is both manual and dhcp.
      * manual: Assignment method is manual.
      * dhcp: Assignment method is dhcp.
    """

    BOTH = "both"
    MANUAL = "manual"
    DHCP = "dhcp"


class SyslogFacilityEnum(str, Enum):
    """Enumeration for SyslogFacilityEnum

    Values:
      * kernel: Kernel messages.
      * user-level: User level messages.
      * mail-system: Mail system.
      * system-daemons: System daemons.
      * authentication: Authentication/authorization attempt messages.
      * syslog-internal: Messages generated internally by syslog.
      * line-printer: Line printer subsystem.
      * network-news: Network news subsystem.
      * uucp: UUCP subsystem.
      * clock-daemon-9: Clock daemon.
      * security: Security related events and error messages.
      * ftp-daemon: FTP daemon.
      * ntp: NTP subsystem.
      * log-audit: Log audit.
      * log-alert: Log alert.
      * clock-daemon-15: Clock daemon.
      * local0: Local use 0 (unused).
      * local1: Alarm logs.
      * local2: All commands, in a protocol agnostic format.
      * local3: All commands, in a protocol specific format (CLI, NETCONF, etc).
      * local4: Line card logs above severity level ERROR.
      * local5: Initial HW initialization and EEPROM status sysinfo log.
      * local6: Any changes to the configuration DB, both internal or externally triggered.
      * local7: All applications.
      * all: Selects all other syslog facilities.
    """

    KERNEL = "kernel"
    USER_LEVEL = "user-level"
    MAIL_SYSTEM = "mail-system"
    SYSTEM_DAEMONS = "system-daemons"
    AUTHENTICATION = "authentication"
    SYSLOG_INTERNAL = "syslog-internal"
    LINE_PRINTER = "line-printer"
    NETWORK_NEWS = "network-news"
    UUCP = "uucp"
    CLOCK_DAEMON_9 = "clock-daemon-9"
    SECURITY = "security"
    FTP_DAEMON = "ftp-daemon"
    NTP = "ntp"
    LOG_AUDIT = "log-audit"
    LOG_ALERT = "log-alert"
    CLOCK_DAEMON_15 = "clock-daemon-15"
    LOCAL0 = "local0"
    LOCAL1 = "local1"
    LOCAL2 = "local2"
    LOCAL3 = "local3"
    LOCAL4 = "local4"
    LOCAL5 = "local5"
    LOCAL6 = "local6"
    LOCAL7 = "local7"
    ALL = "all"


class MessageFormatEnum(str, Enum):
    """Enumeration for MessageFormatEnum

    Values:
      * rfc5424: <${PRI}>1 ${ISODATE} ${HOST} ${PROGRAM} ${PID} ${MSGID} ${SDATA} $MSG <45>1 2019-11-20T12:55:50+00:00 localhost syslog-ng 2392 - [meta sequenceId='1'] syslog-ng starting up; version='3.24.1'
      * rfc3164: <${PRI}> ${TIMESTAMP} ${HOSTNAME} ${TAG} $MSG <34>Nov 20 12:55:50 localhost syslog-ng[2392] syslog-ng starting up; version='3.24.1'
    """

    RFC5424 = "rfc5424"
    RFC3164 = "rfc3164"


class OriginEnum(str, Enum):
    """Enumeration for OriginEnum

    Values:
      * manual: Indicates Log-server address has been manually configured.
      * dhcp: Indicates Log-server address  has been assigned to this system by a DHCP server.
    """

    MANUAL = "manual"
    DHCP = "dhcp"


class SensitiveDataOptionsEnum(str, Enum):
    """Enumeration for SensitiveDataOptionsEnum

    Values:
      * none: Contains only logs without sensitive data.
      * both: Contains logs without and with sensitive data.
      * only: Contains only logs with sensitive data.
    """

    NONE = "none"
    BOTH = "both"
    ONLY = "only"


class SeverityEnum(str, Enum):
    """Enumeration for SeverityEnum

    Values:
      * emergency: Level 0 - System is unusable.
      * alert: Level 1 - Action must be taken immediately.
      * critical: Level 2 - Critical conditions.
      * error: Level 3 - Error conditions.
      * warning: Level 4 - Warning conditions.
      * notice: Level 5 - Normal but significant condition.
      * informational: Level 6 - Informational messages.
      * debug: Level 7 - Debug-level messages.
    """

    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFORMATIONAL = "informational"
    DEBUG = "debug"


class CompareOpEnum(str, Enum):
    """Enumeration for CompareOpEnum

    Values:
      * equals-or-higher
      * equals
      * not-equals
    """

    EQUALS_OR_HIGHER = "equals-or-higher"
    EQUALS = "equals"
    NOT_EQUALS = "not-equals"


class LogServerFacilityFilterItem(YangBaseModel):
    """Selector that allows to filter log messages based on their source facilities and severities.
    This is a filter based on source-facilities leaf-list (can only add filter to the configured
    source facilities).
    """

    name: SyslogFacilityEnum = Field(
        json_schema_extra={"is_config": True},
        description="Identifies a single syslog facility, or all of them if value is 'all'.",
    )
    severity: SeverityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The system log selected severity level for forwarding.\nThe default severity level is all levels",
        default=SeverityEnum.INFORMATIONAL,
    )
    compare_op: CompareOpEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This leaf describes the option to specify how the severity comparison is performed.\nThe default severity level is all levels",
        default=CompareOpEnum.EQUALS_OR_HIGHER,
        alias="compare-op",
    )


class LogServerItem(YangBaseModel):
    """Grouping the configuration parameters for log forwarding."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-]*)$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name for the endpoint to forwarding logs to.",
        min_length=1,
        max_length=64,
    )
    address: str = Field(
        json_schema_extra={"is_config": True},
        description="The leaf uniquely specifies the ipv4 or ipv6 address of the remote host.",
    )
    transport: TransportEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="It is the transport protocol used when forwarding logs.",
        default=TransportEnum.UDP,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="This leaf specifies the port number used to deliver messages to the remote server.",
        ge=0,
        le=65535,
        default=None,
    )
    destination_facility_override: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="When not disabled, this leaf specifies the facility used in messages delivered\nto the remote server.",
        default="disabled",
        alias="destination-facility-override",
    )
    source_facilities: RestconfList[SyslogFacilityEnum] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of syslog facilities used in this configuration.\nWill default to 'all' facilities if not provided.",
        default=None,
        alias="source-facilities",
    )
    pattern_match: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Regex pattern that all entries need to obey.",
        min_length=0,
        max_length=255,
        default=None,
        alias="pattern-match",
    )
    message_coalescence: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If true, prevent flooding of identical messages during abnormal conditions.\nIf there are multiple identical log messages, there will be one message logged fully\nand follow with 'last message repeated n times' message.",
        default=True,
        alias="message-coalescence",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Allows to toggle this syslog server.", default=True
    )
    message_format: MessageFormatEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Identifies the syslog messaging format",
        default=MessageFormatEnum.RFC5424,
        alias="message-format",
    )
    origin: OriginEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Log-server address assignment method, user can convert\nDHCP configured Log-server entry into a manual configured by changing this attribute.",
        default=OriginEnum.MANUAL,
    )
    sensitive_data: SensitiveDataOptionsEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether the local file has logs include sensitive data.",
        default=SensitiveDataOptionsEnum.NONE,
        alias="sensitive-data",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    log_server_facility_filter: RestconfList[LogServerFacilityFilterItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Selector that allows to filter log messages based on their source facilities and severities.\nThis is a filter based on source-facilities leaf-list (can only add filter to the configured\nsource facilities).",
        default=None,
        alias="log-server-facility-filter",
    )


class LogFileFacilityFilterItem(YangBaseModel):
    """Selector that allows to filter log messages based on their source facilities and severities."""

    name: SyslogFacilityEnum = Field(
        json_schema_extra={"is_config": True},
        description="Identifies a single syslog facility, or all of them if value is 'all'.",
    )
    severity: SeverityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The system log selected severity level for forwarding.\nThe default severity level is all levels",
        default=SeverityEnum.INFORMATIONAL,
    )
    compare_op: CompareOpEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This leaf describes the option to specify how the severity comparison is performed.\nThe default severity level is all levels",
        default=CompareOpEnum.EQUALS_OR_HIGHER,
        alias="compare-op",
    )


class LogFileItem(YangBaseModel):
    """Local syslog files supported by the system."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-]*)$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The file name without the .log extension.",
        min_length=1,
        max_length=128,
    )
    number_of_files: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Maximum number of log files retained.\nWhen rotating files due to max size being reached, the oldest files will be discarded\nif the total number of files is greater than number-of-files.",
        ge=1,
        le=20,
        default=10,
        alias="number-of-files",
    )
    max_file_size: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Maximum file size before rotation.",
        ge=1,
        le=30,
        default=30,
        alias="max-file-size",
    )
    source_facilities: RestconfList[SyslogFacilityEnum] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of syslog facilities used in this configuration.\nWill default to 'all' facilities if not provided.",
        default=None,
        alias="source-facilities",
    )
    pattern_match: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Regex pattern that all entries need to obey.",
        min_length=0,
        max_length=255,
        default=None,
        alias="pattern-match",
    )
    sensitive_data: SensitiveDataOptionsEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether the local file has logs include sensitive data.",
        default=SensitiveDataOptionsEnum.NONE,
        alias="sensitive-data",
    )
    log_file_facility_filter: RestconfList[LogFileFacilityFilterItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Selector that allows to filter log messages based on their source facilities and severities.",
        default=None,
        alias="log-file-facility-filter",
    )


class LogConsoleFacilityFilterItem(YangBaseModel):
    """Selector that allows to filter log messages based on their source facilities and severities."""

    name: SyslogFacilityEnum = Field(
        json_schema_extra={"is_config": True},
        description="Identifies a single syslog facility, or all of them if value is 'all'.",
    )
    severity: SeverityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The system log selected severity level for forwarding.\nThe default severity level is all levels",
        default=SeverityEnum.INFORMATIONAL,
    )
    compare_op: CompareOpEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This leaf describes the option to specify how the severity comparison is performed.\nThe default severity level is all levels",
        default=CompareOpEnum.EQUALS_OR_HIGHER,
        alias="compare-op",
    )


class LogConsole(YangBaseModel):
    """Console logging supported by the system."""

    source_facilities: RestconfList[SyslogFacilityEnum] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of syslog facilities used in this configuration.\nWill default to 'all' facilities if not provided.",
        default=None,
        alias="source-facilities",
    )
    log_console_facility_filter: RestconfList[LogConsoleFacilityFilterItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Selector that allows to filter log messages based on their source facilities and severities.",
        default=None,
        alias="log-console-facility-filter",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Switches on and off the console logging.", default=False
    )


class Syslog(YangBaseModel):
    """Central configuration for logging functionality via syslog.
    Includes control of local log files, remote logging configuration and logging in serial console.
    """

    remote_logging_switch: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If false, disable all remote logging destinations.",
        default=True,
        alias="remote-logging-switch",
    )
    log_relay: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If false, disable all remote logging from shelf controller to node controller.",
        default=False,
        alias="log-relay",
    )
    source_address: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Source address or hostname to be inserted in HOST field of log message.",
        default="localhost",
        alias="source-address",
    )
    log_file_message_coalescence: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If true, prevent flooding of identical messages during abnormal conditions.\nIf there are multiple identical log messages for log files, there will be one\nmessage logged fully and follow with 'last message repeated n times' message.",
        default=True,
        alias="log-file-message-coalescence",
    )
    niap_compliant_logging: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether the logs are NIAP compliant.",
        default=False,
        alias="niap-compliant-logging",
    )
    privacy_mode: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If true, the system becomes GDPR compliant, by obfuscating\nthe user private data in the logs",
        default=False,
        alias="privacy-mode",
    )
    assignment_method: AssignmentMethodEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The system would contain manual and dhcp configured values.\nSystem can use those onfigurations/values defined by assignment-method attributes.",
        default=AssignmentMethodEnum.BOTH,
        alias="assignment-method",
    )
    log_server: RestconfList[LogServerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Grouping the configuration parameters for log forwarding.",
        default=None,
        alias="log-server",
    )
    log_file: RestconfList[LogFileItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Local syslog files supported by the system.",
        default=None,
        alias="log-file",
    )
    log_console: LogConsole | None = Field(
        json_schema_extra={"is_config": True},
        description="Console logging supported by the system.",
        default=None,
        alias="log-console",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class PublicKeyAlgorithmEnum(str, Enum):
    """Enumeration for PublicKeyAlgorithmEnum

    Values:
      * ecdsa-sha2-nistp256
      * ecdsa-sha2-nistp384
      * ecdsa-sha2-nistp521
      * ssh-rsa2048
      * ssh-rsa3072
      * ssh-rsa4096
    """

    ECDSA_SHA2_NISTP256 = "ecdsa-sha2-nistp256"
    ECDSA_SHA2_NISTP384 = "ecdsa-sha2-nistp384"
    ECDSA_SHA2_NISTP521 = "ecdsa-sha2-nistp521"
    SSH_RSA2048 = "ssh-rsa2048"
    SSH_RSA3072 = "ssh-rsa3072"
    SSH_RSA4096 = "ssh-rsa4096"


class FingerprintAlgorithmEnum(str, Enum):
    """Enumeration for FingerprintAlgorithmEnum

    Values:
      * md5
      * sha256
    """

    MD5 = "md5"
    SHA256 = "sha256"


class SshHostKeyItem(YangBaseModel):
    """Global(for server and client side SSHv2 based apps) SSHv2 host keys.
    There needs to be one host key per supported algorithm.
    The system auto-generates a host-key in default DB and
    additional host-keys can be added/overwritten via the ssh-keygen RPC.
    """

    public_key_algorithm: PublicKeyAlgorithmEnum = Field(
        json_schema_extra={"is_config": False},
        description="The type of host key algorithm in use.",
        alias="public-key-algorithm",
    )
    public_key: str | None = Field(
        json_schema_extra={"is_config": False},
        description="SSHv2(OpenSSH Portable) host public key component encoded in PEM format:\n<key type><SPACE>...base64 encoded OpenSSH public key....<SPACE><comment>",
        min_length=0,
        max_length=2048,
        default=None,
        alias="public-key",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": False}, description="User label.", min_length=0, max_length=256, default=None
    )
    fingerprint_algorithm: FingerprintAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The type of hash algorithm in use for computing the key fingerprint",
        default=None,
        alias="fingerprint-algorithm",
    )
    fingerprint: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Fingerprint string as a sequence of pairs of hex digits.\nSSHv2 public key fingerprint examples for MD5 and SHA256 hash:\nmd5sum fingerprint => b2:9c:cd:30:b1:38:e3:d1:17:d6:73:eb:03:9a:80:83\nsha256sum fingerprint => f4:61:58:e4:90:65:c4:70:98:7f:d1:40:0a:d8:d9:79:14:e6:91:dc:b6:ed:91:8c:c0:df:d9:65:db:dd:a0:18",
        min_length=1,
        max_length=95,
        default=None,
    )


class SshKnownHostItem(YangBaseModel):
    """SSHv2 known hosts entry."""

    id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique identifier (name) for this entry.",
        min_length=1,
        max_length=64,
    )
    address: str = Field(
        json_schema_extra={"is_config": True},
        description="The hostname/IPv4/IPv6 address of the allowed/known peer host.",
    )
    public_key_algorithm: PublicKeyAlgorithmEnum = Field(
        json_schema_extra={"is_config": True},
        description="The type of host key algorithm in use.",
        alias="public-key-algorithm",
    )
    public_key: str = Field(
        json_schema_extra={"is_config": True},
        description="SSHv2(OpenSSH Portable) host public key component encoded in PEM format:\n<key type><SPACE>...base64 encoded OpenSSH public key....<SPACE><comment>",
        min_length=0,
        max_length=2048,
        alias="public-key",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class SshAuthorizedKeyItem(YangBaseModel):
    """SSHv2 authorized key.
    Each authorized key entry contains a trusted public key for SSHv2 user authentication.
    """

    user_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="User owning the authorized key. Can be local or remote user.",
            min_length=1,
            max_length=64,
            alias="user-name",
        )
    )
    key_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A unique identifier (name) for this entry.",
        min_length=1,
        max_length=64,
        alias="key-id",
    )
    key_expiration_date: (
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
        description="Expiration date for SSH authorized key.",
        default=None,
        alias="key-expiration-date",
    )
    key_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="State is 'disabled' if key is expired, 'enabled' otherwise.",
        default=EnableSwitchEnum.ENABLED,
        alias="key-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    public_key_algorithm: PublicKeyAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The type of key algorithm used. Auto-discovered based on provided public key.",
        default=None,
        alias="public-key-algorithm",
    )
    public_key: str = Field(
        json_schema_extra={"is_config": True},
        description="Base64-encoded OpenSSH public key.",
        min_length=0,
        max_length=2048,
        alias="public-key",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class Ssh(YangBaseModel):
    """Control of ssh access."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Enables direct access to shell via ssh.", default=False
    )
    sftp_support: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls whether SFTP is enabled or not.",
        default=EnableSwitchEnum.ENABLED,
        alias="sftp-support",
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Port listening for ssh login that goes directly to shell.",
        ge=1,
        default=8022,
    )
    pre_login_message: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Welcome message displayed before user login.",
        min_length=0,
        max_length=1440,
        default=None,
        alias="pre-login-message",
    )
    post_login_message: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Welcome message displayed after user login.",
        min_length=0,
        max_length=1440,
        default=None,
        alias="post-login-message",
    )
    ssh_host_key: RestconfList[SshHostKeyItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Global(for server and client side SSHv2 based apps) SSHv2 host keys.\n  There needs to be one host key per supported algorithm.\n  The system auto-generates a host-key in default DB and\n  additional host-keys can be added/overwritten via the ssh-keygen RPC.",
        default=None,
        alias="ssh-host-key",
    )
    ssh_known_host: RestconfList[SshKnownHostItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="SSHv2 known hosts entry.",
        default=None,
        alias="ssh-known-host",
    )
    ssh_authorized_key: RestconfList[SshAuthorizedKeyItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="SSHv2 authorized key.\nEach authorized key entry contains a trusted public key for SSHv2 user authentication.",
        default=None,
        alias="ssh-authorized-key",
    )


class CliAliasItem(YangBaseModel):
    """List of aliases used in CLI.
    Can only be accessed via 'alias/unalias' CLI commands.
    """

    name: str = Field(
        json_schema_extra={"is_config": True}, description="Name of the alias", min_length=1, max_length=256
    )
    value: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Value of the alias",
        min_length=1,
        max_length=1024,
        default=None,
    )


class CliSessionConfigItem(YangBaseModel):
    """Configurations associated with individual CLI sessions."""

    session_id: str = Field(
        json_schema_extra={"is_config": True}, description="The identifier of the CLI session", alias="session-id"
    )
    cli_lines: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Number of rows to be used for display. This value is automatically\ndiscovered when possible",
        ge=10,
        le=1000,
        default=40,
        alias="cli-lines",
    )
    cli_columns: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Number of columns to be used for display. This value is automatically\ndiscovered when possible",
        ge=80,
        le=4000,
        default=140,
        alias="cli-columns",
    )
    interactive_mode: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This determines if the CLI shall issue interactive prompt (e.g. for prompting\nadditional information, or for confirmation of user initiated actions).\nEnabled = CLI will prompt user (default)",
        default=None,
        alias="interactive-mode",
    )
    display_timestamp: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This determines if the current timestamp will be printed on every CLI command.",
        default=False,
        alias="display-timestamp",
    )


class Cli(YangBaseModel):
    """Configuration of the Command Line Interface (CLI) management protocol."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Enables/disables the CLI management protocol.", default=True
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The port which listens for CLI access via ssh.",
        ge=1,
        default=22,
    )
    script_dir: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Location in the filesystem where CLI scripts are stored.",
        min_length=1,
        max_length=80,
        default=None,
        alias="script-dir",
    )
    default_interactive_mode: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines whether CLI sessions have interactive-mode enabled or disabled by default.\nIndividual sessions can deviate from this global flag by configuring the interactive-mode at the cli-session-config level.\nNote: changing this parameter will not affect existing CLI sessions, only newly created sessions.",
        default=True,
        alias="default-interactive-mode",
    )
    show_alarm_columns: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="Columns to display in the output of 'show alarm' CLI command.\nPossible options are the standard alarm fields, and additionally the following values:\n- default-columns: represents the group of columns shown by default.",
        min_length=0,
        max_length=128,
        default=None,
        alias="show-alarm-columns",
    )
    cli_alias: RestconfList[CliAliasItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of aliases used in CLI.\nCan only be accessed via 'alias/unalias' CLI commands.",
        default=None,
        alias="cli-alias",
    )
    cli_session_config: RestconfList[CliSessionConfigItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Configurations associated with individual CLI sessions.",
        default=None,
        alias="cli-session-config",
    )


class SerialConsole(YangBaseModel):
    """Global configuration of all serial console ports in the system."""

    global_switch: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Allow access by serial-console. Note: each console port can override this global behavior.",
        default=EnableSwitchEnum.ENABLED,
        alias="global-switch",
    )
    global_timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Serial console inactivity timeout. Can be set to zero to disable inactivity timer.",
        ge=0,
        default=60,
        alias="global-timeout",
    )


class Netconf(YangBaseModel):
    """Configuration of the NETCONF management protocol."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables/disables the NETCONF management protocol.",
        default=True,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The port which listens for NETCONF access via ssh.",
        ge=1,
        default=830,
    )
    annotate_cli_name: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If enabled, annotates NETCONF XML output with cli names for traceability.",
        default=False,
        alias="annotate-cli-name",
    )
    static_info_in_notifs: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of YANG identifiers that are statically included in notifications.\nIf they are present in objects that are notified.\nApplicable for management protocols with support for YANG-type notifications (NETCONF, etc).\nFor example, if object user[user-name='tom'] has had the 'timeout' attribute updated,\nand the static-info-in-notifs included the 'user-status' string,\nthe associated notification would include not only the 'timeout' parameter,\nbut also the 'user-status' (despite the fact that it had not changed).",
        min_length=1,
        max_length=64,
        default=None,
        alias="static-info-in-notifs",
    )
    hello_timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the number of seconds that a session may exist\nbefore the hello PDU is received/transmitted.  A session will be\ndropped if no hello PDU is received/transmitted before this number\nof seconds elapses.",
        ge=1,
        le=3600,
        default=2,
        alias="hello-timeout",
    )


class Tl1(YangBaseModel):
    """TL1 protocol configuration"""

    tl1_over_ssh_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Decides whether TL1 protocol is accessible over SSH or not.",
        default=True,
        alias="tl1-over-ssh-enabled",
    )
    ssh_interactive_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="SSH port that gives access to interactive interface of TL1 protocol server.",
        ge=1,
        default=9095,
        alias="ssh-interactive-port",
    )
    ssh_scripting_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="SSH port that gives access to non-interactive or scripting interface of TL1 protocol server. This interface does not echo terminal characters to client.",
        ge=1,
        default=9096,
        alias="ssh-scripting-port",
    )


class Restconf(YangBaseModel):
    """Configuration of the RESTCONF management protocol."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable RESTCONF access.",
        default=True,
    )
    http_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable RESTCONF HTTP access.",
        default=False,
        alias="http-enabled",
    )
    https_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable RESTCONF HTTPS access.",
        default=True,
        alias="https-enabled",
    )
    http_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable RESTCONF HTTP port.",
        ge=1,
        default=8080,
        alias="http-port",
    )
    https_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable RESTCONF HTTPS port.",
        ge=1,
        default=8181,
        alias="https-port",
    )
    cookie_timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Timeout of a cookie based RESTCONF session.",
        ge=1,
        le=300,
        default=5,
        alias="cookie-timeout",
    )
    api_root: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Root of the RESTCONF API.",
        min_length=0,
        max_length=64,
        default=None,
        alias="api-root",
    )


class GnmiGetEncodingGranularityEnum(str, Enum):
    """Enumeration for GnmiGetEncodingGranularityEnum

    Values:
      * per-path: Put all path data on a Update message.
      * per-object: Divide the path data into multiple Update messages, one per YANG container/list entry.
    """

    PER_PATH = "per-path"
    PER_OBJECT = "per-object"


class Grpc(YangBaseModel):
    """Configuration of the gNMI/gRPC management protocol."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables/disables the gRPC management protocol.",
        default=True,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The port which listens for gNMI & gNOI access via gRPC.",
        ge=1,
        default=50051,
    )
    gnmi_get_encoding_granularity: GnmiGetEncodingGranularityEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows to configure the granularity of data in gNMI Get responses, when encoded with JSON.",
        default=GnmiGetEncodingGranularityEnum.PER_OBJECT,
        alias="gnmi-get-encoding-granularity",
    )


class CommunityStringAccessEnum(str, Enum):
    """Enumeration for CommunityStringAccessEnum

    Values:
      * read-only
    """

    READ_ONLY = "read-only"


class SnmpCommunityItem(YangBaseModel):
    """List of SNMP Community Strings.
    Note: trap-community-string is located in the snmp-target object.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Name for the community (different from the community string itself).",
        min_length=1,
        max_length=64,
    )
    community_string: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[!-~\\s]*)$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Community String.",
        min_length=1,
        max_length=32,
        alias="community-string",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable this community-string.",
        default=True,
    )
    community_string_access: CommunityStringAccessEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="SNMP access right of this community string.",
        default=CommunityStringAccessEnum.READ_ONLY,
        alias="community-string-access",
    )


class SnmpVersionEnum(str, Enum):
    """Enumeration for SnmpVersionEnum

    Values:
      * v2c
      * v3
    """

    V2C = "v2c"
    V3 = "v3"


class TargetTransportEnum(str, Enum):
    """Enumeration for TargetTransportEnum

    Values:
      * udp
    """

    UDP = "udp"


class SnmpTargetItem(YangBaseModel):
    """List of SNMP targets (trap listeners)"""

    target_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Identifies the SNMP target",
        min_length=1,
        max_length=64,
        alias="target-name",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable this snmp-target.",
        default=True,
    )
    snmp_version: SnmpVersionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="snmp version.",
        default=SnmpVersionEnum.V2C,
        alias="snmp-version",
    )
    trap_community_string: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[!-~\\s]*)$", v))] | None = Field(
        json_schema_extra={"is_config": True},
        description="Community string used for SNMP traps.\n    Only of relevance for snmpv2c.",
        min_length=1,
        max_length=32,
        default="nokia",
        alias="trap-community-string",
    )
    snmpv3_user: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-z_.][a-z0-9_\\-.]*[$]?)$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Indicate the snmpv3 user.\n    Only of relevance for snmpv3.",
        min_length=1,
        max_length=32,
        alias="snmpv3-user",
    )
    target_address: str = Field(
        json_schema_extra={"is_config": True},
        description="IP address or hostname of the SNMP target",
        alias="target-address",
    )
    target_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="UDP port number.",
        ge=0,
        le=65535,
        default=162,
        alias="target-port",
    )
    target_transport: TargetTransportEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of transport for the SNMP target",
        default=TargetTransportEnum.UDP,
        alias="target-transport",
    )


class UserSecLevelEnum(str, Enum):
    """Enumeration for UserSecLevelEnum

    Values:
      * auth-priv
      * auth-no-priv
      * no-auth-no-priv
    """

    AUTH_PRIV = "auth-priv"
    AUTH_NO_PRIV = "auth-no-priv"
    NO_AUTH_NO_PRIV = "no-auth-no-priv"


class AuthProtocolEnum(str, Enum):
    """Enumeration for AuthProtocolEnum

    Values:
      * SHA
    """

    SHA = "SHA"


class PrivProtocolEnum(str, Enum):
    """Enumeration for PrivProtocolEnum

    Values:
      * AES128
      * AES192
      * AES256
      * DES
    """

    AES128 = "AES128"
    AES192 = "AES192"
    AES256 = "AES256"
    DES = "DES"


class Snmpv3UserItem(YangBaseModel):
    """SNMPv3 user configuration."""

    snmpv3_user_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-z_.][a-z0-9_\\-.]*[$]?)$", v))] = (
        Field(
            json_schema_extra={"is_config": True},
            description="SNMPv3 user name.",
            min_length=1,
            max_length=32,
            alias="snmpv3-user-name",
        )
    )
    user_sec_level: UserSecLevelEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the SNMPv3 user security level.\nNote: when NE is in secure-mode, only auth-priv is allowed.",
        default=UserSecLevelEnum.NO_AUTH_NO_PRIV,
        alias="user-sec-level",
    )
    auth_protocol: AuthProtocolEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the authentication protocol that the SNMPv3 user being created will use.\n\nCondition (when): ../user-sec-level != 'no-auth-no-priv'",
        default=AuthProtocolEnum.SHA,
        alias="auth-protocol",
    )
    auth_passphrase: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the SNMPv3 authentication pass phrase.\n\nCondition (when): ../user-sec-level != 'no-auth-no-priv'",
        min_length=8,
        max_length=64,
        default=None,
        alias="auth-passphrase",
    )
    priv_protocol: PrivProtocolEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the privacy protocol that the SNMPv3 user being created will use.\n\nCondition (when): ../user-sec-level = 'auth-priv'",
        default=PrivProtocolEnum.AES128,
        alias="priv-protocol",
    )
    priv_passphrase: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the SNMPv3 privacy pass phrase.\n\nCondition (when): ../user-sec-level = 'auth-priv'",
        min_length=8,
        max_length=64,
        default=None,
        alias="priv-passphrase",
    )


class Snmp(YangBaseModel):
    """Configuration of the SNMP management protocol."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable global SNMP access.",
        default=True,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable port where the NE is listening for SNMP requests.",
        ge=1,
        default=161,
    )
    snmp_engine_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="SNMP EngineID of the NE.\nThe EngineID will follow the EngineID format 3 defined in RFC3411.\nThe MAC address in the Engine ID will be the first MAC address of the MAC addresses Pool of the NE.",
        min_length=0,
        max_length=256,
        default=None,
        alias="snmp-engine-id",
    )
    engine_boot_count: int | None = Field(
        json_schema_extra={"is_config": False},
        description="SNMP engine boot count.\nCounts how many times the engine has restarted.",
        ge=0,
        default=0,
        alias="engine-boot-count",
    )
    snmp_community: RestconfList[SnmpCommunityItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of SNMP Community Strings.\nNote: trap-community-string is located in the snmp-target object.",
        default=None,
        alias="snmp-community",
    )
    snmp_target: RestconfList[SnmpTargetItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of SNMP targets (trap listeners)",
        default=None,
        alias="snmp-target",
    )
    snmpv3_user: RestconfList[Snmpv3UserItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="SNMPv3 user configuration.",
        default=None,
        alias="snmpv3-user",
    )


class HttpFileServer(YangBaseModel):
    """HTTP file server configuration"""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable file server access.",
        default=True,
    )
    http_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable HTTP protocol for file server access.",
        default=False,
        alias="http-enabled",
    )
    https_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable HTTPS protocol for file server access.",
        default=True,
        alias="https-enabled",
    )
    http_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable HTTP port.",
        ge=1,
        default=8980,
        alias="http-port",
    )
    https_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable HTTPS port.",
        ge=1,
        default=8981,
        alias="https-port",
    )
    url_base: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The base URL use to redirect to the file transfer application.",
        min_length=1,
        max_length=100,
        default="/transfer",
        alias="url-base",
    )


class ProtocolEnum(str, Enum):
    """Enumeration for ProtocolEnum

    Values:
      * netconf
      * gnmi-dial-out-tunnel: Dial-Out with gRPC Tunnels.
    """

    NETCONF = "netconf"
    GNMI_DIAL_OUT_TUNNEL = "gnmi-dial-out-tunnel"


class TransportEnum_1(str, Enum):
    """Enumeration for TransportEnum

    Values:
      * ssh
      * tls
    """

    SSH = "ssh"
    TLS = "tls"


class RetryPolicyEnum(str, Enum):
    """Enumeration for RetryPolicyEnum

    Values:
      * progressive-back-off: Try to reconnect with an exponentional time interval.
      * retry-then-stop: Retry a fixed number of times with a fixed timeout interval.
      * retry-forever: Retry forever with a fixed timeout interval.
    """

    PROGRESSIVE_BACK_OFF = "progressive-back-off"
    RETRY_THEN_STOP = "retry-then-stop"
    RETRY_FOREVER = "retry-forever"


class ConnectionStateEnum(str, Enum):
    """Enumeration for ConnectionStateEnum

    Values:
      * connected: Session is currently established with 'home'.
      * connecting: Running through the retries; also used if connected, and session abruptly is terminated.
      * failed: All retries have failed, no further attempts are being done to connect to it.
      * closed: session was established, and was gracefully closed.
      * disabled: Enabled parameter is false.
    """

    CONNECTED = "connected"
    CONNECTING = "connecting"
    FAILED = "failed"
    CLOSED = "closed"
    DISABLED = "disabled"


class DialOutServerItem(YangBaseModel):
    """Dial-out server configuration and state.
    A dial-out-server configuration automatically triggers a connection against the server, with client-server functionality is inverted;
    this connection is then used to establish a normal NBI session.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Dial-out-server name.", min_length=1, max_length=64
    )
    address: str = Field(
        json_schema_extra={"is_config": True}, description="Dial-out-server IPv4/IPv6 address or hostname."
    )
    protocol: ProtocolEnum | None = Field(
        json_schema_extra={"is_config": True}, description="Dial-out-server session type.", default=ProtocolEnum.NETCONF
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True}, description="Dial-out-server session port.", ge=1, default=None
    )
    transport: TransportEnum_1 | None = Field(
        json_schema_extra={"is_config": False}, description="Dial-out-server transport protocol.", default=None
    )
    retry_policy: RetryPolicyEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Retry policy after a timeout.",
        default=RetryPolicyEnum.PROGRESSIVE_BACK_OFF,
        alias="retry-policy",
    )
    retry: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Number of retries before giving up.\n\nCondition (when): ../retry-policy = 'retry-then-stop'",
        ge=0,
        le=5,
        default=3,
    )
    timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Wait time until timeout.\n\nCondition (when): ../retry-policy != 'progressive-back-off'",
        ge=2,
        le=255,
        default=10,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    auto_connect: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If true, automatically tries to connect to this dial-out-server. Note that a server with auto-connect false can still be connected manually via the call-home RPC.",
        default=True,
        alias="auto-connect",
    )
    connection_state: ConnectionStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Connection state to the dial-out-server.",
        default=ConnectionStateEnum.DISABLED,
        alias="connection-state",
    )


class DataModelItem(YangBaseModel):
    """Available YANG Data models for loading/unloading."""

    name: str = Field(json_schema_extra={"is_config": True}, description="Model name.", min_length=0, max_length=256)
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Data model description.",
        min_length=0,
        max_length=256,
        default=None,
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows to load/unload this data model.A loaded data model means that it can be used via the management interfaces.",
        default=False,
    )
    config_cache: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Allows caching of config data for the given data-model.",
        default=False,
        alias="config-cache",
    )


class ProtocolEnum_1(str, Enum):
    """Enumeration for ProtocolEnum

    Values:
      * gnmi-openconfig: gnmi openconfig streaming.
    """

    GNMI_OPENCONFIG = "gnmi-openconfig"


class FastTelemetry(YangBaseModel):
    """Fast Telemetry provides an alternative telemetry channel that accesses the hardware directly for specific metrics.
    Please consult documentation to see what metrics are available per card type.
    """

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable fast telemetry streaming.",
        default=False,
    )
    protocol: ProtocolEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable attribute to select the desired protocol.",
        default=ProtocolEnum_1.GNMI_OPENCONFIG,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True}, description="User configurable port.", ge=1, default=57400
    )


class HighSpeedMonitoring(YangBaseModel):
    """High Speed Monitoring is a gRPC server that accesses the hardware directly to get specific mesurements."""

    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable switch to enable or disable high speed monitoring.",
        default=False,
    )
    port: int | None = Field(
        json_schema_extra={"is_config": True}, description="User configurable port.", ge=1, default=57500
    )


class NotificationTypeItem(YangBaseModel):
    """List of supported notifications."""

    name: str = Field(
        json_schema_extra={"is_config": False},
        description="Notification qualified name (prefix:name).",
        min_length=1,
        max_length=64,
    )
    namespace: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Notification namespace.",
        min_length=1,
        max_length=64,
        default=None,
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Description of the notification.",
        min_length=1,
        max_length=128,
        default=None,
    )
    scope: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the scope of the notification - which data model it applies to.",
        min_length=0,
        max_length=256,
        default=None,
    )


class NotificationStreamItem(YangBaseModel):
    """List of supported NETCONF streams, their description and other information."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": False}, description="The name of the event stream.", min_length=1, max_length=64
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Description of the event stream.",
        min_length=1,
        max_length=128,
        default=None,
    )
    supported_notifications: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Contains the list of supported notifications.",
        min_length=1,
        max_length=64,
        default=None,
        alias="supported-notifications",
    )
    state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="State of the stream (tied with the respective data-model enabled leaf).",
        default=None,
    )


class Notifications(YangBaseModel):
    """Information on supported NETCONF streams and notifications."""

    notification_type: RestconfList[NotificationTypeItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of supported notifications.",
        default=None,
        alias="notification-type",
    )
    notification_stream: RestconfList[NotificationStreamItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of supported NETCONF streams, their description and other information.",
        default=None,
        alias="notification-stream",
    )


class Protocols(YangBaseModel):
    """Container of management protocol objects."""

    ssh: Ssh | None = Field(json_schema_extra={"is_config": True}, description="Control of ssh access.", default=None)
    cli: Cli | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of the Command Line Interface (CLI) management protocol.",
        default=None,
    )
    serial_console: SerialConsole | None = Field(
        json_schema_extra={"is_config": True},
        description="Global configuration of all serial console ports in the system.",
        default=None,
        alias="serial-console",
    )
    netconf: Netconf | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of the NETCONF management protocol.",
        default=None,
    )
    tl1: Tl1 | None = Field(
        json_schema_extra={"is_config": True}, description="TL1 protocol configuration", default=None
    )
    restconf: Restconf | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of the RESTCONF management protocol.",
        default=None,
    )
    grpc: Grpc | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of the gNMI/gRPC management protocol.",
        default=None,
    )
    snmp: Snmp | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of the SNMP management protocol.",
        default=None,
    )
    http_file_server: HttpFileServer | None = Field(
        json_schema_extra={"is_config": True},
        description="HTTP file server configuration",
        default=None,
        alias="http-file-server",
    )
    dial_out_server: RestconfList[DialOutServerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Dial-out server configuration and state.\nA dial-out-server configuration automatically triggers a connection against the server, with client-server functionality is inverted;\nthis connection is then used to establish a normal NBI session.",
        default=None,
        alias="dial-out-server",
    )
    data_model: RestconfList[DataModelItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Available YANG Data models for loading/unloading.",
        default=None,
        alias="data-model",
    )
    fast_telemetry: FastTelemetry | None = Field(
        json_schema_extra={"is_config": True},
        description="Fast Telemetry provides an alternative telemetry channel that accesses the hardware directly for specific metrics.\n         Please consult documentation to see what metrics are available per card type.",
        default=None,
        alias="fast-telemetry",
    )
    high_speed_monitoring: HighSpeedMonitoring | None = Field(
        json_schema_extra={"is_config": True},
        description="High Speed Monitoring is a gRPC server that accesses the hardware directly to get specific mesurements.",
        default=None,
        alias="high-speed-monitoring",
    )
    notifications: Notifications | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on supported NETCONF streams and notifications.",
        default=None,
    )


class CommandTypeEnum(str, Enum):
    """Enumeration for CommandTypeEnum

    Values:
      * cli: CLI command.
    """

    CLI = "cli"


class TaskStatusEnum(str, Enum):
    """Enumeration for TaskStatusEnum

    Values:
      * scheduled: Task is enabled and will run when the time comes.
      * disabled: Task is disabled by user.
      * finished: Task has reached its end-time, or single occurrence task was already executed.
      * ongoing: Task is enabled and is currently running
    """

    SCHEDULED = "scheduled"
    DISABLED = "disabled"
    FINISHED = "finished"
    ONGOING = "ongoing"


class PreviousResultEnum(str, Enum):
    """Enumeration for PreviousResultEnum

    Values:
      * success
      * fail
    """

    SUCCESS = "success"
    FAIL = "fail"


class TaskItem(YangBaseModel):
    """User configurable scheduled task. Can define single occurrence or periodic commands."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Identifier of the scheduled task.",
        min_length=1,
        max_length=64,
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable switch of this task; allows user to disable a task without deleting it.",
        default=True,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.INHIBITED,
        alias="alarm-report-control",
    )
    command: str = Field(
        json_schema_extra={"is_config": True},
        description="Command that is scheduled. Content will depend on the command-type.",
        min_length=1,
        max_length=1024,
    )
    command_type: CommandTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of configured command.",
        default=CommandTypeEnum.CLI,
        alias="command-type",
    )
    frequency: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(((1000)|(0*\\d{1,3}))w)? *(((1000)|(0*\\d{1,3}))d)? *(((1000)|(0*\\d{1,3}))h)? *(((1000)|(0*\\d{1,3}))m)? *(((1000)|(0*\\d{1,3}))s)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Frequency interval for setting up a periodic scheduled task.\nIf empty (default value), represents a single-occurrence task.\nFrequency interval is provided using the following syntax:\n   '[xw] [xd] [xh] [xm] [xs]'\nwhere:\n    w(eeks), d(ays), h(ours), m(inutes), s(seconds).\nExamples:\n   2w          - two weeks\n   5d 12h      - 5 days and 12 hours\n   1h 7m 30s   - 1 hour and 7 minutes and 30 seconds",
        min_length=0,
        max_length=32,
        default=None,
    )
    number_of_runs: int | str | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines the number of times a periodic task is executed before stopping.",
        default="no-limit",
        alias="number-of-runs",
    )
    start_time: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Timestamp to start the task. For periodic tasks, this is the timestamp for the first trigger of the task.\nIf not provided, uses current time as start-time.",
        default=None,
        alias="start-time",
    )
    end_time: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Timestamp to stop the periodic task.\nNot relevant for single-occurrence tasks.",
        default="never",
        alias="end-time",
    )
    persistent: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If true, this scheduled task will persist a system restart.",
        default=True,
    )
    task_status: TaskStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current operational state of the scheduled task.",
        default=TaskStatusEnum.SCHEDULED,
        alias="task-status",
    )
    next_run: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Next run timestamp. May be 'never' for finished tasks.",
        default="never",
        alias="next-run",
    )
    remaining_runs: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Counter of how many runs are pending until task stops.",
        ge=0,
        default=0,
        alias="remaining-runs",
    )
    previous_run: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Previous task run timestamp.",
        default="never",
        alias="previous-run",
    )
    previous_result: PreviousResultEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Previous task run result.",
        default=None,
        alias="previous-result",
    )
    previous_output: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Output of the previous task run.",
        min_length=0,
        max_length=1024,
        default=None,
        alias="previous-output",
    )


class ScheduledTasks(YangBaseModel):
    """Container of individual user-configurable scheduled commands."""

    task: RestconfList[TaskItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable scheduled task. Can define single occurrence or periodic commands.",
        default=None,
    )


class ZtpStateEnum(str, Enum):
    """Enumeration for ZtpStateEnum

    Values:
      * ztp-init
      * dhcp-in-progress
      * image-download-in-progress
      * image-install-in-progress
      * custom-script-execution-in-progress
      * multi-chassis-setup-in-progress
      * configuration-apply-in-progress
      * ztp-completed
      * ztp-state-unknown
      * ztp-disabled
      * wait-before-ztp-restart
      * ztp-disable-in-progress
      * cleanup-on-ztp-completion
    """

    ZTP_INIT = "ztp-init"
    DHCP_IN_PROGRESS = "dhcp-in-progress"
    IMAGE_DOWNLOAD_IN_PROGRESS = "image-download-in-progress"
    IMAGE_INSTALL_IN_PROGRESS = "image-install-in-progress"
    CUSTOM_SCRIPT_EXECUTION_IN_PROGRESS = "custom-script-execution-in-progress"
    MULTI_CHASSIS_SETUP_IN_PROGRESS = "multi-chassis-setup-in-progress"
    CONFIGURATION_APPLY_IN_PROGRESS = "configuration-apply-in-progress"
    ZTP_COMPLETED = "ztp-completed"
    ZTP_STATE_UNKNOWN = "ztp-state-unknown"
    ZTP_DISABLED = "ztp-disabled"
    WAIT_BEFORE_ZTP_RESTART = "wait-before-ztp-restart"
    ZTP_DISABLE_IN_PROGRESS = "ztp-disable-in-progress"
    CLEANUP_ON_ZTP_COMPLETION = "cleanup-on-ztp-completion"


class ZtpCompletionStatusEnum(str, Enum):
    """Enumeration for ZtpCompletionStatusEnum

    Values:
      * not-completed
      * completed
    """

    NOT_COMPLETED = "not-completed"
    COMPLETED = "completed"


class Ztp(YangBaseModel):
    """Zero Touch Provisioning status.
    Please see RPC 'change-ztp-mode' for ZTP configuration.
    """

    ztp_mode: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="User set mode of ZTP. This flag is set via change-ztp-mode RPC that is allowed even when NBI is locked.",
        default=EnableSwitchEnum.ENABLED,
        alias="ztp-mode",
    )
    ztp_state: ZtpStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current state of ZTP service",
        default=ZtpStateEnum.ZTP_INIT,
        alias="ztp-state",
    )
    ztp_details: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Additional information on the current state",
        min_length=0,
        max_length=256,
        default=None,
        alias="ztp-details",
    )
    ztp_completion_status: ZtpCompletionStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Summarized completion status of ZTP on the node",
        default=ZtpCompletionStatusEnum.NOT_COMPLETED,
        alias="ztp-completion-status",
    )


class FtsFiletypeEnum(str, Enum):
    """Enumeration for FtsFiletypeEnum

    Values:
      * database: Database
      * swimage: SW Image
      * krp: Key replacement package (KRP)
      * script:  Scripts to download from the remote Server
      * debug-log: Debug Logs
      * pm-logs: PM Logs
      * local-certificate: Either an x509 certificate in PKCS#12 format (with password-protected private key) or PKCS#7 format.
      * trusted-certificate: x509v3 PKCS#7 trusted certificate, either Root or Intermediate CA
      * fdr-log: Flight Data Recorder(FDR) Logs
      * logs: Specific logs
      * file: Generic file
      * peer-certificate: An x509v3 certificate in PKCS#12 format (with password-protected private key)
      * crl: Certificate Revocation List (CRL) in PEM format
      * otdr-result: Otdr result
    """

    DATABASE = "database"
    SWIMAGE = "swimage"
    KRP = "krp"
    SCRIPT = "script"
    DEBUG_LOG = "debug-log"
    PM_LOGS = "pm-logs"
    LOCAL_CERTIFICATE = "local-certificate"
    TRUSTED_CERTIFICATE = "trusted-certificate"
    FDR_LOG = "fdr-log"
    LOGS = "logs"
    FILE = "file"
    PEER_CERTIFICATE = "peer-certificate"
    CRL = "crl"
    OTDR_RESULT = "otdr-result"


class OperationEnum(str, Enum):
    """Enumeration for OperationEnum

    Values:
      * upload: last operation upload.
      * download: last operation download.
    """

    UPLOAD = "upload"
    DOWNLOAD = "download"


class TransferTypeEnum(str, Enum):
    """Enumeration for TransferTypeEnum

    Values:
      * sync: last transfer type sync.
      * async: last transfer type async
    """

    SYNC = "sync"
    ASYNC = "async"


class TransferStatusItem(YangBaseModel):
    """Status of the last operation for this filetype.
    This object will only exist if at least one of the operation of that kind was done for that filetype.
    """

    filetype: FtsFiletypeEnum = Field(
        json_schema_extra={"is_config": False}, description="File transfer status per filetype."
    )
    operation: OperationEnum = Field(json_schema_extra={"is_config": False}, description="Last transfer operation.")
    last_completion_status: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Success indicates a successful operation.",
        min_length=0,
        max_length=128,
        default=None,
        alias="last-completion-status",
    )
    last_transfer: (
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
        description="Last transfer Start Timestamp.",
        default=None,
        alias="last-transfer",
    )
    last_duration: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(((1000)|(0*\\d{1,3}))w)? *(((1000)|(0*\\d{1,3}))d)? *(((1000)|(0*\\d{1,3}))h)? *(((1000)|(0*\\d{1,3}))m)? *(((1000)|(0*\\d{1,3}))s)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Last transfer duration.",
        min_length=0,
        max_length=32,
        default=None,
        alias="last-duration",
    )
    transfer_type: TransferTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Last transfer type.", default=None, alias="transfer-type"
    )
    session_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Last transfer session-id.",
        min_length=0,
        max_length=100,
        default=None,
        alias="session-id",
    )
    session_user_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Last transfer session-user-name.",
        min_length=1,
        max_length=64,
        default=None,
        alias="session-user-name",
    )
    filename: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Last transferred file URL. Filename larger than 512 chars are truncated.",
        min_length=0,
        max_length=1024,
        default=None,
    )


class Transfer(YangBaseModel):
    """Information associated with file transfer."""

    debug_log_optional_content: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of keywords associated with optional content to be selected for debug-log upload.",
        min_length=0,
        max_length=64,
        default=None,
        alias="debug-log-optional-content",
    )
    http_proxy: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:((http://)?([^\\s/$.?#][^\\s/]*))?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="Proxy server for internally-generated HTTP requests leaving the NE.\nThis includes certificate revocation-related requests, i.e.: CRL downloads and OCSP requests.\nThe format is '[http://]<host>[:<port>]' where\n    - 'http://' is optional,\n    - '<host>' may be the IPv4 address, IPv6 address, or DNS name of the proxy server,\n    - '<port>' is optional\nIf <port> is omitted, the default is 1080.\nNote: This proxy is not used for file transfers.",
        min_length=0,
        max_length=1024,
        default=None,
        alias="http-proxy",
    )
    transfer_status: RestconfList[TransferStatusItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Status of the last operation for this filetype.\nThis object will only exist if at least one of the operation of that kind was done for that filetype.",
        default=None,
        alias="transfer-status",
    )


class IfTypeEnum(str, Enum):
    """Enumeration for IfTypeEnum

    Values:
      * ethernet: For all Ethernet-like interfaces, regardless of speed, as per RFC 3635.
      * software-loopback: Software Loopback interface type.
      * point-to-point: Point to point interfaces associated with control channels.
      * ppp: RFC 1661 Point-to-Point Protocol (PPP) interface. A Link Control Protocol (LCP) for establishing and configuring the data-link connection and a family of Network Control Protocols (NCPs) for establishing and configuring different network-layer protocols will run over the interface.
      * hdlc: High-Level Data Link Control interface associated with OSCX channels.
      * oscx: Interface associated with OSCX channels.
      * osc-eth: Ethernet over HDLC Interface asscoiated with OSCX channels .
    """

    ETHERNET = "ethernet"
    SOFTWARE_LOOPBACK = "software-loopback"
    POINT_TO_POINT = "point-to-point"
    PPP = "ppp"
    HDLC = "hdlc"
    OSCX = "oscx"
    OSC_ETH = "osc-eth"


class ProtectionModeEnum(str, Enum):
    """Enumeration for ProtectionModeEnum

    Values:
      * unknown: Unknown/Transient protection state; output only.
      * protected: Protected by redundant ports.
      * unprotected: No port redundancy.
    """

    UNKNOWN = "unknown"
    PROTECTED = "protected"
    UNPROTECTED = "unprotected"


class IpAddressConfigModeEnum(str, Enum):
    """Enumeration for IpAddressConfigModeEnum

    Values:
      * static
      * dhcp
    """

    STATIC = "static"
    DHCP = "dhcp"


class OriginEnum_1(str, Enum):
    """Enumeration for OriginEnum

    Values:
      * static: Indicates that the address has been statically configured - for example, using NETCONF or a Command Line Interface.
      * dhcp: Indicates an address that has been assigned to this system by a DHCP server.
      * auto-config: Indicates an address created by autoconfiguration.
    """

    STATIC = "static"
    DHCP = "dhcp"
    AUTO_CONFIG = "auto-config"


class Ipv4AddressItem(YangBaseModel):
    """The IPv4 address on the interface."""

    ip: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                v,
            )
        ),
    ] = Field(
        json_schema_extra={"is_config": True},
        description="The IPv4 addresses on the interface. The following\naddresses are disallowed from being configured:\n1. Addresses beginning with 0 (current network)\n2. Addresses beginning with 127 (loopback addresses)\n3. Addresses beginning with 224 up to 255 (broadcast,\n       multicast and experimental addresses)",
    )
    netmask: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$",
                v,
            )
        ),
    ] = Field(
        json_schema_extra={"is_config": True},
        description="The subnet specified as a netmask for a particular address.\nOnly valid netmasks are allowed to be configured.",
    )
    origin: OriginEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="IPv4 address assignment method.",
        default=OriginEnum_1.STATIC,
    )


class Ipv6AddressItem(YangBaseModel):
    """The IPv6 address on the interface."""

    ip: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                v,
            )
        ),
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
            )
        ),
    ] = Field(json_schema_extra={"is_config": True}, description="The IPv6 address on the interface")
    prefix_length: int = Field(
        json_schema_extra={"is_config": True},
        description="The length of the subnet prefix.",
        ge=1,
        le=128,
        alias="prefix-length",
    )
    origin: OriginEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="IPv6 address assignment method.",
        default=OriginEnum_1.STATIC,
    )


class InterfaceItem(YangBaseModel):
    """The list of configured interfaces on the device."""

    if_name: str = Field(
        json_schema_extra={"is_config": True},
        description="The name of the interface.",
        min_length=1,
        max_length=64,
        alias="if-name",
    )
    if_description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="A textual description of the interface.",
        min_length=0,
        max_length=255,
        default=None,
        alias="if-description",
    )
    if_type: IfTypeEnum = Field(
        json_schema_extra={"is_config": True}, description="The type of the interface.", alias="if-type"
    )
    supporting_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference to the physical port that interface is currently mapped to.\nNot relevant for software loopback interfaces.",
        min_length=0,
        max_length=64,
        default=None,
        alias="supporting-port",
    )
    backup_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference to the physical port that supports this interface (if applicable).\nOnly relevant for ethernet interfaces.",
        min_length=0,
        max_length=64,
        default=None,
        alias="backup-port",
    )
    protection_mode: ProtectionModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Protection mode for interface.\nOnly relevant for ethernet interfaces.",
        default=ProtectionModeEnum.PROTECTED,
        alias="protection-mode",
    )
    protection_state: ProtectionModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current state of protection of interface.\nOnly relevant for ethernet interfaces.",
        default=ProtectionModeEnum.UNKNOWN,
        alias="protection-state",
    )
    vrf: str | None = Field(
        json_schema_extra={"is_config": False},
        description="VRF to which this interface is bound.",
        min_length=1,
        max_length=32,
        default=None,
    )
    ipv4_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls whether IPv4 is enabled or disabled on this\ninterface. When IPv4 is enabled, this interface is\nconnected to an IPv4 stack, and the interface can send\nand receive IPv4 packets.",
        default=True,
        alias="ipv4-enabled",
    )
    ipv4_address_assignment_method: IpAddressConfigModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="IPv4 address assignment method.\n\nCondition (when): ../ipv4-enabled = 'true'",
        default=IpAddressConfigModeEnum.STATIC,
        alias="ipv4-address-assignment-method",
    )
    ipv6_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls whether IPv6 is enabled or disabled on this\ninterface. When IPv6 is enabled, this interface is\nconnected to an IPv6 stack, and the interface can send\nand receive IPv6 packets.\nNot relevant for ppp, hdlc, oscx interfaces.",
        default=True,
        alias="ipv6-enabled",
    )
    ipv6_address_assignment_method: IpAddressConfigModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="IPv6 address assignment method.\nNot relevant for ppp, hdlc and oscx interfaces.\n\nCondition (when): ../ipv6-enabled = 'true'",
        default=IpAddressConfigModeEnum.STATIC,
        alias="ipv6-address-assignment-method",
    )
    proxy_arp_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls whether or not Proxy ARP is to be enabled on the interface.\nNot relevant for ppp, hdlc and oscx interfaces.\n\nCondition (when): ../ipv4-enabled = 'true'",
        default=False,
        alias="proxy-arp-enabled",
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.\n\nCondition (when): if-type != 'software-loopback'",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.\n\nCondition (when): if-type != 'software-loopback'",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.\n\nCondition (when): if-type != 'software-loopback'",
        default=None,
        alias="avail-state",
    )
    ipv4_address: RestconfList[Ipv4AddressItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="The IPv4 address on the interface.",
        default=None,
        alias="ipv4-address",
    )
    ipv6_address: RestconfList[Ipv6AddressItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="The IPv6 address on the interface.\n\nCondition (when): ../if-type != 'ppp' and ../if-type != 'hdlc' and\n../if-type != 'oscx'",
        default=None,
        alias="ipv6-address",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class TypeEnum_5(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * mgmt: Management VRF.
      * internal: Internal VRF.
      * scn: SCN VRF.
    """

    MGMT = "mgmt"
    INTERNAL = "internal"
    SCN = "scn"


class VrfItem(YangBaseModel):
    """Virtual Routing and Forwarding instance."""

    name: str = Field(
        json_schema_extra={"is_config": True}, description="Name of the VRF.", min_length=1, max_length=32
    )
    type: TypeEnum_5 | None = Field(json_schema_extra={"is_config": False}, description="VRF type.", default=None)
    chassis_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Associated chassis name to this VRF.",
            min_length=1,
            max_length=64,
            default=None,
            alias="chassis-name",
        )
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Description of the VRF and its intended purpose.",
        min_length=0,
        max_length=255,
        default=None,
    )


class MonitoringStateEnum(str, Enum):
    """Enumeration for MonitoringStateEnum

    Values:
      * unmonitored: static-route is not part of any ip monitoring instance.
      * ok: static-route is part of an ip monitoring instance in 'ok' state.
      * failed: static-route is part of an ip monitoring instance in 'failed' state.
    """

    UNMONITORED = "unmonitored"
    OK = "ok"
    FAILED = "failed"


class SpecialNextHopEnum(str, Enum):
    """Enumeration for SpecialNextHopEnum

    Values:
      * none: no special treatment of routes, used for all for normal routes.
      * blackhole: For the blackhole routes next-hop will not be created under route.
      * unreachable: For the unreachable routes next-hop will not be created under route.
    """

    NONE = "none"
    BLACKHOLE = "blackhole"
    UNREACHABLE = "unreachable"


class Ipv4StaticRouteItem(YangBaseModel):
    """A list of IPv4 static routes."""

    ipv4_destination_prefix: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])/(([0-9])|([1-2][0-9])|(3[0-2])))$",
                v,
            )
        ),
    ] = Field(
        json_schema_extra={"is_config": True}, description="IPv4 destination prefix.", alias="ipv4-destination-prefix"
    )
    advertised: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="When set to YES, the static route is advertised in the routing\nprotocol. For OSPF, the static route will be advertised as an\nAS external route, if OSPF is configured as an ASBR.",
        default=False,
    )
    next_hop_address: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="IPv4 address of the next-hop.",
        default=None,
        alias="next-hop-address",
    )
    vrf: str = Field(
        json_schema_extra={"is_config": True},
        description="VRF associated with this static route.",
        min_length=1,
        max_length=32,
    )
    distance: int | None = Field(
        json_schema_extra={"is_config": True}, description="distance of the next-hop.", ge=1, le=255, default=1
    )
    interface: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Interface associated with this static route.  The VRF bound\n  to this interface needs to match the static-route provided\n  vrf.",
        min_length=1,
        max_length=64,
        default=None,
    )
    monitoring_state: MonitoringStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The current state of the monitoring.",
        default=MonitoringStateEnum.UNMONITORED,
        alias="monitoring-state",
    )
    monitoring_instance: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Monitoring instance name, applicable only if this route is being monitored.",
        min_length=0,
        max_length=64,
        default=None,
        alias="monitoring-instance",
    )
    origin: OriginEnum | None = Field(
        json_schema_extra={"is_config": True}, description="Route address assignment method.", default=OriginEnum.MANUAL
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    special_next_hop: SpecialNextHopEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the special-next-hop applicable to a route.",
        default=SpecialNextHopEnum.NONE,
        alias="special-next-hop",
    )


class Ipv6StaticRouteItem(YangBaseModel):
    """A list of IPv6 static routes."""

    ipv6_destination_prefix: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(/(([0-9])|([0-9]{2})|(1[0-1][0-9])|(12[0-8]))))$",
                v,
            )
        ),
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(/.+))$", v
            )
        ),
    ] = Field(
        json_schema_extra={"is_config": True}, description="IPv6 destination prefix.", alias="ipv6-destination-prefix"
    )
    vrf: str = Field(
        json_schema_extra={"is_config": True},
        description="VRF associated with this static route.",
        min_length=1,
        max_length=32,
    )
    advertised: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="When set to YES, the static route is advertised in the routing\nprotocol. For OSPF, the static route will be advertised as an\nAS external route, if OSPF is configured as an ASBR.",
        default=False,
    )
    next_hop_address: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                    v,
                )
            ),
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="IPv6 address of the next-hop.",
        default=None,
        alias="next-hop-address",
    )
    distance: int | None = Field(
        json_schema_extra={"is_config": True}, description="distance of the next-hop.", ge=1, le=255, default=1
    )
    interface: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Interface associated with this static route.  The VRF bound\nto this interface needs to match the static-route provided\nvrf.",
        min_length=1,
        max_length=64,
        default=None,
    )
    monitoring_state: MonitoringStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The current state of the monitoring",
        default=MonitoringStateEnum.UNMONITORED,
        alias="monitoring-state",
    )
    monitoring_instance: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Monitoring Instance Name.",
        min_length=0,
        max_length=64,
        default=None,
        alias="monitoring-instance",
    )
    origin: OriginEnum | None = Field(
        json_schema_extra={"is_config": True}, description="route address assignment method.", default=OriginEnum.MANUAL
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    special_next_hop: SpecialNextHopEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the special-next-hop applicable to a route.",
        default=SpecialNextHopEnum.NONE,
        alias="special-next-hop",
    )


class VersionEnum_1(str, Enum):
    """Enumeration for VersionEnum

    Values:
      * ospfv2
      * ospfv3
    """

    OSPFV2 = "ospfv2"
    OSPFV3 = "ospfv3"


class RouterIdModeEnum(str, Enum):
    """Enumeration for RouterIdModeEnum

    Values:
      * use-loopback
      * manual
    """

    USE_LOOPBACK = "use-loopback"
    MANUAL = "manual"


class OspfAreaTypeEnum(str, Enum):
    """Enumeration for OspfAreaTypeEnum

    Values:
      * normal
    """

    NORMAL = "normal"


class OspfAreaRangeItem(YangBaseModel):
    """Summarize routes matching address/mask -
    Applicable to Area Border Routers (ABRs) only.
    """

    prefix: str = Field(json_schema_extra={"is_config": True}, description="IPv4 or IPv6 prefix")
    advertise: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Advertise or hide.", default=True
    )


class OspfIfRoutingEnum(str, Enum):
    """Enumeration for OspfIfRoutingEnum

    Values:
      * active: ACTIVE - This link is advertised and routing messages are transported over this link.
      * passive: PASSIVE - This link is advertised, routing messages are not transported over this link.
      * auto: Auto - ospf-if-routing will be automatically derived from the interface type.
    """

    ACTIVE = "active"
    PASSIVE = "passive"
    AUTO = "auto"


class OspfNetworkTypeEnum(str, Enum):
    """Enumeration for OspfNetworkTypeEnum

    Values:
      * broadcast
      * point-to-point
    """

    BROADCAST = "broadcast"
    POINT_TO_POINT = "point-to-point"


class OspfAuthAlgorithmEnum(str, Enum):
    """Enumeration for OspfAuthAlgorithmEnum

    Values:
      * none
      * HMAC_SHA_256
    """

    NONE = "none"
    HMAC_SHA_256 = "HMAC_SHA_256"


class IpsecModeEnum(str, Enum):
    """Enumeration for IpsecModeEnum

    Values:
      * transport
    """

    TRANSPORT = "transport"


class TypeEnum_6(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * ascii
      * hex
    """

    ASCII = "ascii"
    HEX = "hex"


class AuthKey(YangBaseModel):
    """Container: auth-key"""

    type: TypeEnum_6 | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates whether the integrity key is ASCII or hexadecimal encoded.",
        default=TypeEnum_6.ASCII,
    )
    key: str = Field(
        json_schema_extra={"is_config": True},
        description="The pre-shared key for OSPFv3 IPsec integrity protection.\nThe valid key length range for ascii format is 8..128 and\nfor hex format, it is 16..256.",
        min_length=8,
        max_length=256,
    )


class Ospfv3IpsecSecurityAssociationItem(YangBaseModel):
    """A list of SAs created to protect OSPFv3 traffic. NOTE that
    in ThanOS, we will always create both INBOUND and OUTBOUND
    SAs automatically (i.e., for one user-created entry, there
    will be two SAs automatically created).
    """

    spi: int = Field(
        json_schema_extra={"is_config": True},
        description="A unique security parameter index (SPI) for this SA.",
        ge=256,
        le=4294967295,
    )
    ipsec_protocol: IpsecProtocolEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the use of ESP or AH protocols.",
        default=IpsecProtocolEnum.ESP,
        alias="ipsec-protocol",
    )
    ipsec_mode: IpsecModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates IPsec mode. Only transport mode is supported in the initial releases.",
        default=IpsecModeEnum.TRANSPORT,
        alias="ipsec-mode",
    )
    integrity_algorithm: str = Field(
        json_schema_extra={"is_config": True},
        description="The cryptographic algorithm used to perform IPsec integrity protection.",
        alias="integrity-algorithm",
    )
    auth_key: AuthKey | None = Field(json_schema_extra={"is_config": True}, default=None, alias="auth-key")


class OspfInterfaceItem(YangBaseModel):
    """Configuration of interface in an ospf area."""

    ospf_if_name: str = Field(
        json_schema_extra={"is_config": True},
        description="Reference of the interface in OSPF area.",
        min_length=1,
        max_length=64,
        alias="ospf-if-name",
    )
    ospf_if_routing: OspfIfRoutingEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies if routing is enabled and if so, if Routing is passive or active.",
        default=OspfIfRoutingEnum.AUTO,
        alias="ospf-if-routing",
    )
    enable: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable/disable OSPF protocol on the interface.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        default=True,
    )
    hello_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the Hello Interval in seconds.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        ge=1,
        le=32767,
        default=10,
        alias="hello-interval",
    )
    router_dead_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the Router Dead Interval in seconds.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        ge=4,
        le=65535,
        default=40,
        alias="router-dead-interval",
    )
    retransmission_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the Retransmission Interval in seconds.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        ge=2,
        le=3600,
        default=5,
        alias="retransmission-interval",
    )
    transmit_delay: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Estimated time needed to transmit Link State Update\n(LSU) packets on the interface (seconds). LSAs have\ntheir age incremented by this amount when advertised\non the interface. A sample value would be 1 second.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        ge=1,
        le=450,
        default=1,
        alias="transmit-delay",
    )
    ospf_cost: int | None = Field(
        json_schema_extra={"is_config": True},
        description="OSPF link cost.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        ge=1,
        le=65535,
        default=10,
        alias="ospf-cost",
    )
    ospf_network_type: OspfNetworkTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="OSPF Interface Network Types.\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        default=OspfNetworkTypeEnum.BROADCAST,
        alias="ospf-network-type",
    )
    priority: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Configure OSPF router priority. On multi-access network\nthis value is for Designated Router (DR) election. The\npriority is ignored on other interface types. A router\nwith a higher priority will be preferred in the election\nand a value of 0 indicates the router is not eligible to\nbecome Designated Router or Backup Designated Router\n(BDR).\n\nCondition (when): (ospf-if-routing != 'passive') and (ospf-if-name != 'LO-MGMT')",
        ge=0,
        le=255,
        default=1,
    )
    ospf_auth_enable: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable/Disable Authentication.\n    Only of relevance for ospfv2 or ospfv3.\n\nCondition (when): ((../../version = 'ospfv2') or (../../version = 'ospfv3')) and (ospf-if-name != 'LO-MGMT')    and (ospf-if-routing != 'passive')",
        default=False,
        alias="ospf-auth-enable",
    )
    ospf_auth_algorithm: OspfAuthAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Cryptographic algorithm associated with key.\n    Only of relevance for ospfv2.\n\nCondition (when): ((../../version = 'ospfv2') or (../../version = 'ospfv3')) and (ospf-if-name != 'LO-MGMT')    and (ospf-if-routing != 'passive')",
        default=OspfAuthAlgorithmEnum.HMAC_SHA_256,
        alias="ospf-auth-algorithm",
    )
    ospf_auth_key: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Authentication key string in ASCII format.\n    Only of relevance for ospfv2.\n\nCondition (when): ((../../version = 'ospfv2') or (../../version = 'ospfv3')) and (ospf-if-name != 'LO-MGMT')    and (ospf-if-routing != 'passive')",
        min_length=0,
        max_length=256,
        default=None,
        alias="ospf-auth-key",
    )
    ospfv3_ipsec_security_association: RestconfList[Ospfv3IpsecSecurityAssociationItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of SAs created to protect OSPFv3 traffic. NOTE that\nin ThanOS, we will always create both INBOUND and OUTBOUND\nSAs automatically (i.e., for one user-created entry, there\nwill be two SAs automatically created).\n\nCondition (when): (../../../version = 'ospfv3') and (../ospf-auth-enable = 'true')",
        default=None,
        alias="ospfv3-ipsec-security-association",
    )


class OspfAreaItem(YangBaseModel):
    """Configuration of ospf area."""

    ospf_area_id: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$",
                v,
            )
        ),
    ] = Field(json_schema_extra={"is_config": True}, description="OSPF Router Area ID.", alias="ospf-area-id")
    ospf_area_type: OspfAreaTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="OSPF Router Area Type.",
        default=OspfAreaTypeEnum.NORMAL,
        alias="ospf-area-type",
    )
    ospf_area_range: RestconfList[OspfAreaRangeItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Summarize routes matching address/mask -\nApplicable to Area Border Routers (ABRs) only.",
        default=None,
        alias="ospf-area-range",
    )
    ospf_interface: RestconfList[OspfInterfaceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of interface in an ospf area.",
        default=None,
        alias="ospf-interface",
    )


class OspfInstanceItem(YangBaseModel):
    """OSPF protocol instances."""

    router_id: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="OSPF Router ID.\n\nCondition (when): ../router-id-mode = 'manual'",
        default=None,
        alias="router-id",
    )
    instance_id: int = Field(
        json_schema_extra={"is_config": True}, description="OSPF instance ID.", ge=0, le=255, alias="instance-id"
    )
    version: VersionEnum_1 | None = Field(
        json_schema_extra={"is_config": True}, description="OSPF version v2 or v3", default=VersionEnum_1.OSPFV2
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Textual description of the OSPF instance.",
        min_length=0,
        max_length=128,
        default=None,
    )
    vrf: str | None = Field(
        json_schema_extra={"is_config": False},
        description="VRF associated with this OSPF instance.",
        min_length=1,
        max_length=32,
        default=None,
    )
    router_id_mode: RouterIdModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Flag to indicate router-id is loopback IP or manual configured.",
        default=RouterIdModeEnum.USE_LOOPBACK,
        alias="router-id-mode",
    )
    ospf_area: RestconfList[OspfAreaItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Configuration of ospf area.",
        default=None,
        alias="ospf-area",
    )


class MonitoringStateEnum_1(str, Enum):
    """Enumeration for MonitoringStateEnum

    Values:
      * unknown: Initial state before ping responses are received.
      * ok: Successfully pinging the Destination IP address.
      * failed: Pinging the destination IP Address has failed beyond the configured drop-rate.
      * disabled: Monitoring instance is administratively locked. No pings are sent, routes are active.
    """

    UNKNOWN = "unknown"
    OK = "ok"
    FAILED = "failed"
    DISABLED = "disabled"


class ActionEnum_1(str, Enum):
    """Enumeration for ActionEnum

    Values:
      * none: Indicates that no action will be take on the static routes under monitoring instance.
      * withdraw: Indicates that all static routes under monitoring instance will be withdrawn.
    """

    NONE = "none"
    WITHDRAW = "withdraw"


class IpMonitoringItem(YangBaseModel):
    """Monitoring instance configuration and state. A monitoring instance allows to periodically ping certain destinations whose result takes action on configured static-routes."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Name of the monitoring instance.",
        min_length=1,
        max_length=64,
    )
    probe_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The time between two consecutive pings in seconds",
        ge=1,
        le=60,
        default=5,
        alias="probe-interval",
    )
    destination: str = Field(json_schema_extra={"is_config": True}, description="The remote host to monitor.")
    drop_rate: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The accepted drop rate of ping in 10% steps",
        ge=1,
        le=10,
        default=1,
        alias="drop-rate",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Start or Stop the monitoring of the destination by setting to true or false.",
        default=True,
    )
    monitoring_state: MonitoringStateEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="The current state of the monitoring.",
        default=MonitoringStateEnum_1.UNKNOWN,
        alias="monitoring-state",
    )
    action: ActionEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="The action to take when the monitoring goes into 'failed' state.",
        default=ActionEnum_1.WITHDRAW,
    )
    static_route: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="The list of connected static routes for this Monitoring instance.",
        default=None,
        alias="static-route",
    )
    next_hop: str = Field(
        json_schema_extra={"is_config": True},
        description="Defines the exit interface to use which can be ipv4/ipv6 source ip address or interface name or empty.\nThe monitoring instance will not be active until the exit-interface is configured.",
        alias="next-hop",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )


class AfiSafisEnum(str, Enum):
    """Enumeration for AfiSafisEnum

    Values:
      * IPV4-UNICAST
      * IPV6-UNICAST
    """

    IPV4_UNICAST = "IPV4-UNICAST"
    IPV6_UNICAST = "IPV6-UNICAST"


class SecureSessionEnum(str, Enum):
    """Enumeration for SecureSessionEnum

    Values:
      * none
      * TCP-MD5
    """

    NONE = "none"
    TCP_MD5 = "TCP-MD5"


class SessionStateEnum(str, Enum):
    """Enumeration for SessionStateEnum

    Values:
      * Idle: Idle state
      * Connect: Connect state
      * Active: Active state
      * OpenSent: OpenSent state
      * OpenConfirm: OpenConfirm state
      * Established: Established state
      * Close: Close state
    """

    IDLE = "Idle"
    CONNECT = "Connect"
    ACTIVE = "Active"
    OPENSENT = "OpenSent"
    OPENCONFIRM = "OpenConfirm"
    ESTABLISHED = "Established"
    CLOSE = "Close"


class BgpNetworkItem(YangBaseModel):
    """It advertises (injects) the specified network prefix into the BGP.
    This route must exist in the forwarding table installed by an IGP (ospf, static).
    """

    network_prefix: str = Field(
        json_schema_extra={"is_config": True},
        description="A route item (dynamic or static) in the route table (FIB)\nwill be advertised to eBGP only if there is network-prefix\nprovisioned under the bgp-network.",
        alias="network-prefix",
    )


class BgpNeighborItem(YangBaseModel):
    """List of BGP neighbors configured on the local system,
    uniquely identified by peer IPv4 address.
    """

    remote_address: str = Field(
        json_schema_extra={"is_config": True}, description="Address of the BGP peer.", alias="remote-address"
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether the BGP peer is enabled. In cases where the enabled\nleaf is set to false, the local system should not initiate\nconnections to the neighbor, and should not respond to TCP\nconnections attempts from the neighbor. If the state of the\nBGP session is ESTABLISHED at the time that this leaf is set\nto false, the BGP session should be ceased.",
        default=True,
    )
    peer_as: int = Field(
        json_schema_extra={"is_config": True}, description="AS number of the peer.", ge=0, alias="peer-as"
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="An optional textual description (intended primarily for use\nwith a peer or group.",
        min_length=0,
        max_length=128,
        default=None,
    )
    afi_safis: RestconfList[AfiSafisEnum] = Field(
        json_schema_extra={"is_config": True},
        description="List of AFI/SAFI values used for BGP configuration.",
        alias="afi-safis",
    )
    secure_session: SecureSessionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Authentication method of the session to the peer.",
        default=SecureSessionEnum.NONE,
        alias="secure-session",
    )
    password: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Password as TCP-MD5 authentication key in ASCII format.",
        min_length=0,
        max_length=80,
        default=None,
    )
    connect_retry_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Time interval in seconds between attempts to establish a\nsession with the peer.",
        ge=1,
        le=65535,
        default=120,
        alias="connect-retry-interval",
    )
    hold_time: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Time interval in seconds that a BGP session will be\nconsidered active in the absence of keepalive or other\nmessages from the peer.  The hold-time is typically set to\n3x the keepalive-interval.",
        ge=3,
        le=65535,
        default=90,
        alias="hold-time",
    )
    keepalive_interval: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Time interval in seconds between transmission of keepalive\nmessages to the neighbor.  Typically set to 1/3 the\nhold-time.",
        ge=1,
        le=21845,
        default=30,
        alias="keepalive-interval",
    )
    negotiated_hold_time: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Negotiated hold time between two BGP neighbors.",
        ge=0,
        le=65535,
        default=0,
        alias="negotiated-hold-time",
    )
    session_state: SessionStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current BGP Session state in ASCII format.",
        default=SessionStateEnum.IDLE,
        alias="session-state",
    )
    known_errors: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Current BGP Session state errors if any ASCII format.",
        min_length=0,
        max_length=256,
        default=None,
        alias="known-errors",
    )
    bgp_network: RestconfList[BgpNetworkItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="It advertises (injects) the specified network prefix into the BGP.\nThis route must exist in the forwarding table installed by an IGP (ospf, static).",
        default=None,
        alias="bgp-network",
    )


class BgpInstanceItem(YangBaseModel):
    """BGP protocol instances."""

    instance_id: int = Field(
        json_schema_extra={"is_config": True}, description="BGP instance ID.", ge=0, le=255, alias="instance-id"
    )
    description: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Textual description of the BGP instance.",
        min_length=0,
        max_length=128,
        default=None,
    )
    vrf: str | None = Field(
        json_schema_extra={"is_config": False},
        description="VRF associated with this BGP instance.",
        min_length=1,
        max_length=32,
        default=None,
    )
    local_as: int = Field(
        json_schema_extra={"is_config": True},
        description="The local autonomous system number that is to be used\nwhen establishing sessions with the remote peer or peer\ngroup.",
        ge=0,
        alias="local-as",
    )
    router_id_mode: RouterIdModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Flag to indicate router-id is from loopback interface or manually assigned.",
        default=RouterIdModeEnum.USE_LOOPBACK,
        alias="router-id-mode",
    )
    router_id: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="BGP Router ID.\n\nCondition (when): ../router-id-mode = 'manual'",
        default=None,
        alias="router-id",
    )
    bgp_neighbor: RestconfList[BgpNeighborItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of BGP neighbors configured on the local system,\nuniquely identified by peer IPv4 address.",
        default=None,
        alias="bgp-neighbor",
    )


class Bgp(YangBaseModel):
    """Container of BGP routing."""

    bgp_instance: RestconfList[BgpInstanceItem] | None = Field(
        json_schema_extra={"is_config": True}, description="BGP protocol instances.", default=None, alias="bgp-instance"
    )


class Routing(YangBaseModel):
    """Container of routing subsystem."""

    ipv4_static_route: RestconfList[Ipv4StaticRouteItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of IPv4 static routes.",
        default=None,
        alias="ipv4-static-route",
    )
    ipv6_static_route: RestconfList[Ipv6StaticRouteItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A list of IPv6 static routes.",
        default=None,
        alias="ipv6-static-route",
    )
    ospf_instance: RestconfList[OspfInstanceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="OSPF protocol instances.",
        default=None,
        alias="ospf-instance",
    )
    ip_monitoring: RestconfList[IpMonitoringItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Monitoring instance configuration and state. A monitoring instance allows to periodically ping certain destinations whose result takes action on configured static-routes.",
        default=None,
        alias="ip-monitoring",
    )
    bgp: Bgp | None = Field(
        json_schema_extra={"is_config": True}, description="Container of BGP routing.", default=None
    )


class AddressFamilyEnum(str, Enum):
    """Enumeration for AddressFamilyEnum

    Values:
      * ipv4-unicast
      * ipv6-unicast
    """

    IPV4_UNICAST = "ipv4-unicast"
    IPV6_UNICAST = "ipv6-unicast"


class NextHopItem(YangBaseModel):
    """Next-hop of a route item."""

    interface: str = Field(
        json_schema_extra={"is_config": False},
        description="Reference of the outgoing interface.",
        min_length=1,
        max_length=64,
    )
    next_hop_address: str | None = Field(
        json_schema_extra={"is_config": False},
        description="IP address of the next-hop.",
        default=None,
        alias="next-hop-address",
    )


class RouteItem(YangBaseModel):
    """A list of system routes from various source, such as dynamic protocols and static route."""

    destination_prefix: str = Field(
        json_schema_extra={"is_config": False}, description="IP destination prefix.", alias="destination-prefix"
    )
    special_next_hop: SpecialNextHopEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the special-next-hop applicable to a route.",
        default=SpecialNextHopEnum.NONE,
        alias="special-next-hop",
    )
    next_hop: RestconfList[NextHopItem] | None = Field(
        json_schema_extra={"is_config": False}, description="Next-hop of a route item.", default=None, alias="next-hop"
    )


class RibItem(YangBaseModel):
    """Each entry represents a RIB identified by the 'name'
    key. All routes in a RIB belong to the same address
    family. For each routing instance, the system will
    provide one system-controlled default RIB for each
    supported address family.
    """

    rib_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": False},
        description="The name of the RIB.",
        min_length=1,
        max_length=64,
        alias="rib-name",
    )
    vrf: str | None = Field(
        json_schema_extra={"is_config": False},
        description="VRF to which this RIB is bound.",
        min_length=1,
        max_length=32,
        default=None,
    )
    address_family: AddressFamilyEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Address family.",
        default=AddressFamilyEnum.IPV4_UNICAST,
        alias="address-family",
    )
    route: RestconfList[RouteItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="A list of system routes from various source, such as dynamic protocols and static route.",
        default=None,
    )


class TypeEnum_7(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * ipv4
      * ipv6
    """

    IPV4 = "ipv4"
    IPV6 = "ipv6"


class DirectionEnum_5(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * input
      * output
    """

    INPUT = "input"
    OUTPUT = "output"


class ActionEnum_2(str, Enum):
    """Enumeration for ActionEnum

    Values:
      * accept
      * reject
      * drop
    """

    ACCEPT = "accept"
    REJECT = "reject"
    DROP = "drop"


class ProtocolEnum_2(str, Enum):
    """Enumeration for ProtocolEnum

    Values:
      * any: Matches any protocol.
      * ah: Authentication Header.
      * comp: IP Compression
      * egp: External Gateway Protocol
      * esp: Encapsulating Security Payload
      * gre: Generic Routing Encapsulation
      * icmp: Internet Control Message Protocol
      * idrp: Inter-Domain Routing Protocol
      * igmp: Internet Group Management Protocol
      * igrp: Interior Gateway Routing Protocol
      * isis: Intermediate System-to-Intermediate System
      * ospf: Open Shortest Path First
      * rsvp: Resource Reservation Protocol
      * tcp: Transmission Control Protocol
      * udp: User Datagram Protocol
      * vrrp: Virtual Router Redundancy Protocol
    """

    ANY = "any"
    AH = "ah"
    COMP = "comp"
    EGP = "egp"
    ESP = "esp"
    GRE = "gre"
    ICMP = "icmp"
    IDRP = "idrp"
    IGMP = "igmp"
    IGRP = "igrp"
    ISIS = "isis"
    OSPF = "ospf"
    RSVP = "rsvp"
    TCP = "tcp"
    UDP = "udp"
    VRRP = "vrrp"


class AceItem(YangBaseModel):
    """Attributes pertaining to an access control entry (ACE). Every ACL can have one or more ACEs."""

    sequence_id: int = Field(
        json_schema_extra={"is_config": True},
        description="Sequence number that establishes the relative\norder of the ACE within an ACL",
        ge=1,
        le=100,
        alias="sequence-id",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Name of the IP Filter",
        min_length=0,
        max_length=256,
        default=None,
    )
    direction: DirectionEnum_5 | None = Field(
        json_schema_extra={"is_config": True},
        description="Based on the direction, this filter shall be applied\nto incoming packets, or outgoing packets. Note that Input is\nmandatory and output is an optional function.",
        default=DirectionEnum_5.INPUT,
    )
    logging_action: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Flag to indicate if logging needs to be done once the ACE rule is matched.",
        default=False,
        alias="logging-action",
    )
    source_ip_address: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the source IP of this filter. The\nvalues could be a valid IPv4/v6-address or Ipv4/v6-address/prefix.",
        default="any",
        alias="source-ip-address",
    )
    source_lower_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The lower bound on the source Layer 4 TCP/UDP port number.\nA value of zero for both indicates wildcarding.\n\nCondition (when): ../protocol != 'icmp'",
        ge=0,
        le=65535,
        default=0,
        alias="source-lower-port",
    )
    source_upper_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The upper bound on the source Layer 4 TCP/UDP port number.\nA value of zero for both indicates wildcarding.\n\nCondition (when): ../protocol != 'icmp'",
        ge=0,
        le=65535,
        default=0,
        alias="source-upper-port",
    )
    destination_ip_address: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Specifies the destination IP of this filter. The\nvalues could be a valid IPv4/v6-address or Ipv4/v6-address/prefix.",
        default="any",
        alias="destination-ip-address",
    )
    destination_lower_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The lower bound on the destination Layer 4 TCP/UDP port number.\nA value of zero for both indicates wildcarding.\n\nCondition (when): ../protocol != 'icmp'",
        ge=0,
        le=65535,
        default=0,
        alias="destination-lower-port",
    )
    destination_upper_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The upper bound on the destination Layer 4 TCP/UDP port number.\nA value of zero for both indicates wildcarding.\n\nCondition (when): ../protocol != 'icmp'",
        ge=0,
        le=65535,
        default=0,
        alias="destination-upper-port",
    )
    ttl: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="IPv4 and IPv6 packet's time-to-live (TTL) hop limit. Default TTL value 255 is max hop",
        default="any",
    )
    action: ActionEnum_2 | None = Field(
        json_schema_extra={"is_config": True},
        description="The action to be taken by the filter.",
        default=ActionEnum_2.DROP,
    )
    protocol: ProtocolEnum_2 | None = Field(
        json_schema_extra={"is_config": True},
        description="Internet Protocol number.  Refers to the protocol\npayload.  In IPv6, this field is known as 'next-header', and\nif extension headers are present, the protocol is present in\nthe 'upper-layer' header.",
        default=ProtocolEnum_2.ANY,
    )


class AclItem(YangBaseModel):
    """Set of attributes associated with every access control list (ACL). An ACL can have one or more ACEs."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Name of the ACL.", min_length=1, max_length=64
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    type: TypeEnum_7 = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the top-level type of ACL, i.e., what\nfields from the associated IPv4 or IPv6 headers this ACL matches on.",
    )
    interface: str = Field(
        json_schema_extra={"is_config": True},
        description="A reference to the interface this filter\nshall be applied to.",
        min_length=1,
        max_length=64,
    )
    ace: RestconfList[AceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Attributes pertaining to an access control entry (ACE). Every ACL can have one or more ACEs.",
        default=None,
    )


class AccessControlList(YangBaseModel):
    """Attributes and objects pertaining to ACLs."""

    acl: RestconfList[AclItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Set of attributes associated with every access control list (ACL). An ACL can have one or more ACEs.",
        default=None,
    )


class DnsServerItem(YangBaseModel):
    """DNS server configuration."""

    address: str = Field(json_schema_extra={"is_config": True}, description="DNS address.")
    origin: OriginEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="DNS address assignment method, user can convert\nDHCP configured DNS entry into a manual configured  by changing this attribute.",
        default=None,
    )


class Dns(YangBaseModel):
    """Domain Name Server configuration"""

    assignment_method: AssignmentMethodEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The system would contain manual and dhcp configured values.\nSystem can use those onfigurations/values defined by assignment-method attributes.",
        default=AssignmentMethodEnum.BOTH,
        alias="assignment-method",
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Whether DNS is enabled.", default=True
    )
    search: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([A-Za-z0-9]*\\.)+[A-Za-z0-9]+)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": True},
        description="DNS-search-suffix name, should contain atleast single dot.\n  To clear value, set to empty string.",
        min_length=0,
        max_length=64,
        default=None,
    )
    dns_server: RestconfList[DnsServerItem] | None = Field(
        json_schema_extra={"is_config": True}, description="DNS server configuration.", default=None, alias="dns-server"
    )


class XconTypeEnum(str, Enum):
    """Enumeration for XconTypeEnum

    Values:
      * L1-ETH-TO-GCC0: L1-ETH to GCC0 user channel cross-connection.
      * L1-GCC0-TO-GCC0: GCC0 to GCC0 user channel cross-connection.
      * L1-ETH-TO-OSC: L1-ETH to OSC user channel cross-connection.
      * L1-OSC-TO-OSC: OSC to OSC user channel cross-connection.
      * L1-ETH-TO-FCC1: ETH to FCC1 user channel cross-connection.
    """

    L1_ETH_TO_GCC0 = "L1-ETH-TO-GCC0"
    L1_GCC0_TO_GCC0 = "L1-GCC0-TO-GCC0"
    L1_ETH_TO_OSC = "L1-ETH-TO-OSC"
    L1_OSC_TO_OSC = "L1-OSC-TO-OSC"
    L1_ETH_TO_FCC1 = "L1-ETH-TO-FCC1"


class NwXconnectItem(YangBaseModel):
    """List of all the network cross connect services that are currently provisioned in the system."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A user configured name for the XCON.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    endpoint1: str = Field(
        json_schema_extra={"is_config": True},
        description="The end-point1 on which the network-xcon needs to be created.",
    )
    endpoint2: str = Field(
        json_schema_extra={"is_config": True},
        description="The end-point2 on which the network-xcon needs to be created.",
    )
    xcon_type: XconTypeEnum = Field(
        json_schema_extra={"is_config": True}, description="The xcon type of this object.", alias="xcon-type"
    )
    rate: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Maximum bandwidth rate of the user channel.",
        ge=0,
        default=None,
    )
    operational_rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Operational-rate of the user channel.",
        default=None,
        alias="operational-rate",
    )


class NetworkXconnect(YangBaseModel):
    """Services of multiples user cross connections commissioned in this NE."""

    nw_xconnect: RestconfList[NwXconnectItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of all the network cross connect services that are currently provisioned in the system.",
        default=None,
        alias="nw-xconnect",
    )


class NetworkingServices(YangBaseModel):
    """Top level container for network services model."""

    network_xconnect: NetworkXconnect | None = Field(
        json_schema_extra={"is_config": True},
        description="Services of multiples user cross connections commissioned in this NE.",
        default=None,
        alias="network-xconnect",
    )


class Networking(YangBaseModel):
    """Top level container for networking model."""

    interface: RestconfList[InterfaceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="The list of configured interfaces on the device.",
        default=None,
    )
    vrf: RestconfList[VrfItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Virtual Routing and Forwarding instance.", default=None
    )
    routing: Routing | None = Field(
        json_schema_extra={"is_config": True}, description="Container of routing subsystem.", default=None
    )
    rib: RestconfList[RibItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Each entry represents a RIB identified by the 'name'\nkey. All routes in a RIB belong to the same address\nfamily. For each routing instance, the system will\nprovide one system-controlled default RIB for each\nsupported address family.",
        default=None,
    )
    access_control_list: AccessControlList | None = Field(
        json_schema_extra={"is_config": True},
        description="Attributes and objects pertaining to ACLs.",
        default=None,
        alias="access-control-list",
    )
    dns: Dns | None = Field(
        json_schema_extra={"is_config": True}, description="Domain Name Server configuration", default=None
    )
    networking_services: NetworkingServices | None = Field(
        json_schema_extra={"is_config": True},
        description="Top level container for network services model.",
        default=None,
        alias="networking-services",
    )
    use_as_source: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Interface to use as source address",
        min_length=0,
        max_length=64,
        default=None,
        alias="use-as-source",
    )


class TimezoneEnum(str, Enum):
    """Enumeration for TimezoneEnum

    Values:
      * International_Date_Line_West[GMT-12:00]
      * Midway_Island-Samoa[GMT-11:00]
      * Hawaii[GMT-10:00]
      * Alaska[GMT-09:00]
      * Pacific_Time[US_and_Canada][GMT-08:00]
      * Arizona[GMT-07:00]
      * Mountain_Time[US_and_Canada][GMT-07:00]
      * CentralAmerica[GMT-06:00]
      * Central_Time[US_and_Canada][GMT-06:00]
      * Mexico_City-Tegucigalpa[GMT-06:00]
      * Saskatchewan[GMT-06:00]
      * Bagota-Lima-Quito[GMT-05:00]
      * Eastern_Time[US_and_Canada][GMT-05:00]
      * Indiana[East][GMT-05:00]
      * Caracas-La_Paz[GMT-04:30]
      * Atlantic_Time[Canada][GMT-04:00]
      * Santiago[GMT-04:00]
      * Newfoundland[GMT-03:30]
      * Brasilia[GMT-03:00]
      * Buenos_Aires-Georgetown[GMT-03:00]
      * Greenland[GMT-03:00]
      * Mid-Atlantic[GMT-02:00]
      * Azores[GMT-01:00]
      * Cape_Verde_Is.[GMT-01:00]
      * Casablanca-Monrovia[GMT]
      * Greenwich_Mean_Time:Dublin-Edinburgh-Lisbon-London[GMT]
      * Amsterdam-Copenhagen-Madrid-ParisVilnius[GMT+01:00]
      * Belgrade-Sarajevo-Skopje-Sofija-Zargreb[GMT+01:00]
      * Bratislava-Budapest-Ljublijana-Prague-Wasaw[GMT+01:00]
      * Brussels-Berlin-Bern-Rome-Stockholm-Vienna[GMT+01:00]
      * West_Central_Africa[GMT+01:00]
      * Athens-Istanbul-Minsk[GMT+02:00]
      * Bucharest[GMT+02:00]
      * Cairo[GMT+02:00]
      * Harare-Pretoria[GMT+02:00]
      * Helsinki-Riga-Tallinn[GMT+02:00]
      * Jerusalem[GMT+02:00]
      * Israel[GMT+02:00]
      * Baghdad[GMT+03:00]
      * Kuwait-Riyadh[GMT+03:00]
      * Moscow-St.Petersburg-Volgograd[GMT+03:00]
      * Nairobi[GMT+03:00]
      * Tehran[GMT+03:30]
      * Abu_Dhabi-Muscat[GMT+04:00]
      * Baku[GMT+04:00]
      * Tbilisi[GMT+04:00]
      * Kabul[GMT+04:30]
      * Ekaterinburg[GMT+05:00]
      * Islamabad-Karachi-Tashkent[GMT+05:00]
      * Mumbai-Calcutta-Chennai-New_Delhi[GMT+05:30]
      * Colombo[GMT+05:30]
      * Kathmandu[GMT+05:45]
      * Dhaka[GMT+06:00]
      * Almaty[GMT+06:00]
      * Rangoon[GMT+06:30]
      * Bangkok-Hanoi-Jakarta[GMT+07:00]
      * Beijing-Chongqing-Hong_Kong-Urumqi[GMT+08:00]
      * Perth[GMT+08:00]
      * Singapore-Kuala_Lumpur[GMT+08:00]
      * Taipei[GMT+08:00]
      * Osaka-Sapporo-Tokyo[GMT+09:00]
      * Seoul[GMT+09:00]
      * Yakutsk[GMT+09:00]
      * Adelaide[GMT+09:30]
      * Darwin[GMT+09:30]
      * Brisbane[GMT+10:00]
      * Canberra-Melbourne-Sydney[GMT+10:00]
      * Guam-Port_Moresby[GMT+10:00]
      * Hobart[GMT+10:00]
      * Vladivostok[GMT+10:00]
      * Magadan-Solomon_Is.-New_Caledonia[GMT+11:00]
      * Auckland-Wellington[GMT+12:00]
      * Fiji-Kamchatka-Marshall_Is.[GMT+12:00]
      * Eniwetok-Kwajalein[GMT+12:00]
      * Nuku_alofa[GMT+13:00]
      * Kiritimati[GMT+14:00]
      * Universal-Time-Coordinated
    """

    INTERNATIONAL_DATE_LINE_WEST_GMT_12_00 = "International_Date_Line_West[GMT-12:00]"
    MIDWAY_ISLAND_SAMOA_GMT_11_00 = "Midway_Island-Samoa[GMT-11:00]"
    HAWAII_GMT_10_00 = "Hawaii[GMT-10:00]"
    ALASKA_GMT_09_00 = "Alaska[GMT-09:00]"
    PACIFIC_TIME_US_AND_CANADA_GMT_08_00 = "Pacific_Time[US_and_Canada][GMT-08:00]"
    ARIZONA_GMT_07_00 = "Arizona[GMT-07:00]"
    MOUNTAIN_TIME_US_AND_CANADA_GMT_07_00 = "Mountain_Time[US_and_Canada][GMT-07:00]"
    CENTRALAMERICA_GMT_06_00 = "CentralAmerica[GMT-06:00]"
    CENTRAL_TIME_US_AND_CANADA_GMT_06_00 = "Central_Time[US_and_Canada][GMT-06:00]"
    MEXICO_CITY_TEGUCIGALPA_GMT_06_00 = "Mexico_City-Tegucigalpa[GMT-06:00]"
    SASKATCHEWAN_GMT_06_00 = "Saskatchewan[GMT-06:00]"
    BAGOTA_LIMA_QUITO_GMT_05_00 = "Bagota-Lima-Quito[GMT-05:00]"
    EASTERN_TIME_US_AND_CANADA_GMT_05_00 = "Eastern_Time[US_and_Canada][GMT-05:00]"
    INDIANA_EAST_GMT_05_00 = "Indiana[East][GMT-05:00]"
    CARACAS_LA_PAZ_GMT_04_30 = "Caracas-La_Paz[GMT-04:30]"
    ATLANTIC_TIME_CANADA_GMT_04_00 = "Atlantic_Time[Canada][GMT-04:00]"
    SANTIAGO_GMT_04_00 = "Santiago[GMT-04:00]"
    NEWFOUNDLAND_GMT_03_30 = "Newfoundland[GMT-03:30]"
    BRASILIA_GMT_03_00 = "Brasilia[GMT-03:00]"
    BUENOS_AIRES_GEORGETOWN_GMT_03_00 = "Buenos_Aires-Georgetown[GMT-03:00]"
    GREENLAND_GMT_03_00 = "Greenland[GMT-03:00]"
    MID_ATLANTIC_GMT_02_00 = "Mid-Atlantic[GMT-02:00]"
    AZORES_GMT_01_00 = "Azores[GMT-01:00]"
    CAPE_VERDE_IS_GMT_01_00 = "Cape_Verde_Is.[GMT-01:00]"
    CASABLANCA_MONROVIA_GMT = "Casablanca-Monrovia[GMT]"
    GREENWICH_MEAN_TIME_DUBLIN_EDINBURGH_LISBON_LONDON_GMT = "Greenwich_Mean_Time:Dublin-Edinburgh-Lisbon-London[GMT]"
    AMSTERDAM_COPENHAGEN_MADRID_PARISVILNIUS_GMT_PLUS_01_00 = "Amsterdam-Copenhagen-Madrid-ParisVilnius[GMT+01:00]"
    BELGRADE_SARAJEVO_SKOPJE_SOFIJA_ZARGREB_GMT_PLUS_01_00 = "Belgrade-Sarajevo-Skopje-Sofija-Zargreb[GMT+01:00]"
    BRATISLAVA_BUDAPEST_LJUBLIJANA_PRAGUE_WASAW_GMT_PLUS_01_00 = (
        "Bratislava-Budapest-Ljublijana-Prague-Wasaw[GMT+01:00]"
    )
    BRUSSELS_BERLIN_BERN_ROME_STOCKHOLM_VIENNA_GMT_PLUS_01_00 = "Brussels-Berlin-Bern-Rome-Stockholm-Vienna[GMT+01:00]"
    WEST_CENTRAL_AFRICA_GMT_PLUS_01_00 = "West_Central_Africa[GMT+01:00]"
    ATHENS_ISTANBUL_MINSK_GMT_PLUS_02_00 = "Athens-Istanbul-Minsk[GMT+02:00]"
    BUCHAREST_GMT_PLUS_02_00 = "Bucharest[GMT+02:00]"
    CAIRO_GMT_PLUS_02_00 = "Cairo[GMT+02:00]"
    HARARE_PRETORIA_GMT_PLUS_02_00 = "Harare-Pretoria[GMT+02:00]"
    HELSINKI_RIGA_TALLINN_GMT_PLUS_02_00 = "Helsinki-Riga-Tallinn[GMT+02:00]"
    JERUSALEM_GMT_PLUS_02_00 = "Jerusalem[GMT+02:00]"
    ISRAEL_GMT_PLUS_02_00 = "Israel[GMT+02:00]"
    BAGHDAD_GMT_PLUS_03_00 = "Baghdad[GMT+03:00]"
    KUWAIT_RIYADH_GMT_PLUS_03_00 = "Kuwait-Riyadh[GMT+03:00]"
    MOSCOW_ST_PETERSBURG_VOLGOGRAD_GMT_PLUS_03_00 = "Moscow-St.Petersburg-Volgograd[GMT+03:00]"
    NAIROBI_GMT_PLUS_03_00 = "Nairobi[GMT+03:00]"
    TEHRAN_GMT_PLUS_03_30 = "Tehran[GMT+03:30]"
    ABU_DHABI_MUSCAT_GMT_PLUS_04_00 = "Abu_Dhabi-Muscat[GMT+04:00]"
    BAKU_GMT_PLUS_04_00 = "Baku[GMT+04:00]"
    TBILISI_GMT_PLUS_04_00 = "Tbilisi[GMT+04:00]"
    KABUL_GMT_PLUS_04_30 = "Kabul[GMT+04:30]"
    EKATERINBURG_GMT_PLUS_05_00 = "Ekaterinburg[GMT+05:00]"
    ISLAMABAD_KARACHI_TASHKENT_GMT_PLUS_05_00 = "Islamabad-Karachi-Tashkent[GMT+05:00]"
    MUMBAI_CALCUTTA_CHENNAI_NEW_DELHI_GMT_PLUS_05_30 = "Mumbai-Calcutta-Chennai-New_Delhi[GMT+05:30]"
    COLOMBO_GMT_PLUS_05_30 = "Colombo[GMT+05:30]"
    KATHMANDU_GMT_PLUS_05_45 = "Kathmandu[GMT+05:45]"
    DHAKA_GMT_PLUS_06_00 = "Dhaka[GMT+06:00]"
    ALMATY_GMT_PLUS_06_00 = "Almaty[GMT+06:00]"
    RANGOON_GMT_PLUS_06_30 = "Rangoon[GMT+06:30]"
    BANGKOK_HANOI_JAKARTA_GMT_PLUS_07_00 = "Bangkok-Hanoi-Jakarta[GMT+07:00]"
    BEIJING_CHONGQING_HONG_KONG_URUMQI_GMT_PLUS_08_00 = "Beijing-Chongqing-Hong_Kong-Urumqi[GMT+08:00]"
    PERTH_GMT_PLUS_08_00 = "Perth[GMT+08:00]"
    SINGAPORE_KUALA_LUMPUR_GMT_PLUS_08_00 = "Singapore-Kuala_Lumpur[GMT+08:00]"
    TAIPEI_GMT_PLUS_08_00 = "Taipei[GMT+08:00]"
    OSAKA_SAPPORO_TOKYO_GMT_PLUS_09_00 = "Osaka-Sapporo-Tokyo[GMT+09:00]"
    SEOUL_GMT_PLUS_09_00 = "Seoul[GMT+09:00]"
    YAKUTSK_GMT_PLUS_09_00 = "Yakutsk[GMT+09:00]"
    ADELAIDE_GMT_PLUS_09_30 = "Adelaide[GMT+09:30]"
    DARWIN_GMT_PLUS_09_30 = "Darwin[GMT+09:30]"
    BRISBANE_GMT_PLUS_10_00 = "Brisbane[GMT+10:00]"
    CANBERRA_MELBOURNE_SYDNEY_GMT_PLUS_10_00 = "Canberra-Melbourne-Sydney[GMT+10:00]"
    GUAM_PORT_MORESBY_GMT_PLUS_10_00 = "Guam-Port_Moresby[GMT+10:00]"
    HOBART_GMT_PLUS_10_00 = "Hobart[GMT+10:00]"
    VLADIVOSTOK_GMT_PLUS_10_00 = "Vladivostok[GMT+10:00]"
    MAGADAN_SOLOMON_IS_NEW_CALEDONIA_GMT_PLUS_11_00 = "Magadan-Solomon_Is.-New_Caledonia[GMT+11:00]"
    AUCKLAND_WELLINGTON_GMT_PLUS_12_00 = "Auckland-Wellington[GMT+12:00]"
    FIJI_KAMCHATKA_MARSHALL_IS_GMT_PLUS_12_00 = "Fiji-Kamchatka-Marshall_Is.[GMT+12:00]"
    ENIWETOK_KWAJALEIN_GMT_PLUS_12_00 = "Eniwetok-Kwajalein[GMT+12:00]"
    NUKU_ALOFA_GMT_PLUS_13_00 = "Nuku_alofa[GMT+13:00]"
    KIRITIMATI_GMT_PLUS_14_00 = "Kiritimati[GMT+14:00]"
    UNIVERSAL_TIME_COORDINATED = "Universal-Time-Coordinated"


class TimeSourceEnum(str, Enum):
    """Enumeration for TimeSourceEnum

    Values:
      * ntp: Indicates that NE uses NTP for synchronization.
      * manual: indicates that NE uses NE internal clock for Synchronization.
    """

    NTP = "ntp"
    MANUAL = "manual"


class Clock(YangBaseModel):
    """System clock."""

    current_time: (
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
        description="Indicates the current Date and Time of this NE.",
        default=None,
        alias="current-time",
    )
    universal_time: (
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
        description="Indicates the UTC Date and Time of this NE.",
        default=None,
        alias="universal-time",
    )
    timezone: TimezoneEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Indicates the Name of the Time Zone of this NE.",
        default=TimezoneEnum.UNIVERSAL_TIME_COORDINATED,
    )
    uptime: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates how long the system has been running in days hh:mm:ss format.",
        min_length=0,
        max_length=200,
        default=None,
    )
    uptime_seconds: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates how long the system has been running, in seconds.",
        ge=0,
        default=None,
        alias="uptime-seconds",
    )
    time_source: TimeSourceEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the source of the system current time.",
        default=TimeSourceEnum.MANUAL,
        alias="time-source",
    )
    DST_active: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether daylight saving is active.",
        default=False,
        alias="DST-active",
    )
    last_time_jump: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates last system time jump in the format '<time1> to <time2>'. Time jumps of less than 10 seconds are ignored.",
        min_length=0,
        max_length=200,
        default=None,
        alias="last-time-jump",
    )


class KeyTypeEnum(str, Enum):
    """Enumeration for KeyTypeEnum

    Values:
      * sha-1: Use sha-1 hash algorithm for NTP message digest computation
      * aes-cmac: Use AES-CMAC hash algorithm for NTP message digest computation
      * sha-256: Use sha-256 hash algorithm for NTP message digest computation
      * md5: Use md5 hash algorithm for NTP message digest computation
    """

    SHA_1 = "sha-1"
    AES_CMAC = "aes-cmac"
    SHA_256 = "sha-256"
    MD5 = "md5"


class NtpKeyItem(YangBaseModel):
    """Keys to be used for NTP authentication."""

    key_id: int = Field(
        json_schema_extra={"is_config": True}, description="NTP Key-ID.", ge=1, le=65534, alias="key-id"
    )
    key_type: KeyTypeEnum = Field(
        json_schema_extra={"is_config": True},
        description="Hash algorithm for NTP message digest computation",
        alias="key-type",
    )
    key_value: str = Field(
        json_schema_extra={"is_config": True},
        description="NTP Key-value.",
        min_length=8,
        max_length=40,
        alias="key-value",
    )
    is_trusted: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Is trusted NTP key.", default=False, alias="is-trusted"
    )


class AuthStatusEnum(str, Enum):
    """Enumeration for AuthStatusEnum

    Values:
      * ok
      * yes
      * bad
      * none
    """

    OK = "ok"
    YES = "yes"
    BAD = "bad"
    NONE = "none"


class NtpServerStatus(YangBaseModel):
    """NTP server status."""

    refid: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference clock type or address for the peer.",
        min_length=0,
        max_length=32,
        default=None,
    )
    stratum: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the stratum of the remote peer.",
        ge=0,
        default=None,
    )
    type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of the peer ('l' for local reference clock, 'u' for unicast, 'm' for multicast or 'b' for broadcast)",
        min_length=0,
        max_length=10,
        default=None,
    )
    when: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates time elapsed since last packet was received in seconds.",
        ge=0,
        default=None,
    )
    poll: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the polling interval in seconds.",
        ge=0,
        default=None,
    )
    reach: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the reachability of the configured server.\nThis is an 8-bit shift register with the most recent probe in the 2^0 position.\nThe value 377 indicates that all the recent probes have been answered.",
        ge=0,
        default=None,
    )
    delay: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Delay along path to the server in milliseconds.",
        default=None,
    )
    offset: Decimal64 | None = Field(
        json_schema_extra={"is_config": False}, description="Offset of clock to the peer in milliseconds.", default=None
    )
    jitter: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Jitter along path to the server in milliseconds.",
        default=None,
    )
    auth_status: AuthStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Authentication status of NTP server",
        default=AuthStatusEnum.NONE,
        alias="auth-status",
    )
    condition: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Condition of NTP server. Some of possible values: sys.peer/reject/candidate/...",
        min_length=0,
        max_length=16,
        default=None,
    )


class NtpServerItem(YangBaseModel):
    """Configured NTP server."""

    ip_address: str = Field(
        json_schema_extra={"is_config": True},
        description="NTP Server IP address. Ipv4/Ipv6/hostname supported.",
        alias="ip-address",
    )
    origin: OriginEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="NTP address assignment method, user can convert\nDHCP configured NTP entry into a manual configured by changing this attribute.",
        default=None,
    )
    auth_key_id: str | int | None = Field(
        json_schema_extra={"is_config": True},
        description="Key ID to be used for this server.",
        default="not-applicable",
        alias="auth-key-id",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    ntp_server_status: NtpServerStatus | None = Field(
        json_schema_extra={"is_config": False},
        description="NTP server status.",
        default=None,
        alias="ntp-server-status",
    )


class Ntp(YangBaseModel):
    """Network Time Protocol Configuration."""

    ntp_enabled: bool | None = Field(
        json_schema_extra={"is_config": True}, description="Whether ntp is enabled.", default=True, alias="ntp-enabled"
    )
    ntp_auth_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether NTP authentication is enabled.",
        default=False,
        alias="ntp-auth-enabled",
    )
    ntp_active_server: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently active NTP server.",
        default=None,
        alias="ntp-active-server",
    )
    assignment_method: AssignmentMethodEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The system would contain manual and dhcp configured values.\nSystem can use those onfigurations/values defined by assignment-method attributes.",
        default=AssignmentMethodEnum.BOTH,
        alias="assignment-method",
    )
    ntp_key: RestconfList[NtpKeyItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Keys to be used for NTP authentication.",
        default=None,
        alias="ntp-key",
    )
    ntp_server: RestconfList[NtpServerItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Configured NTP server.", default=None, alias="ntp-server"
    )


class FailActionEnum(str, Enum):
    """Enumeration for FailActionEnum

    Values:
      * system-restart: Warm restart the system/card software immediately upon service failure.
      * default-action: Default policy of restarting the service, then rebooting the system if service not recovered.
      * ignore: No automatic action taken in case of service failure.
    """

    SYSTEM_RESTART = "system-restart"
    DEFAULT_ACTION = "default-action"
    IGNORE = "ignore"


class SwControlRuleItem(YangBaseModel):
    """Optional service-specific custom rules to overide default action upon service failure."""

    service_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Name of the service to be monitored.",
        min_length=1,
        max_length=64,
        alias="service-name",
    )
    fail_action: FailActionEnum = Field(
        json_schema_extra={"is_config": True},
        description="Action profile to be used in the case of service failure.",
        alias="fail-action",
    )


class StateEnum(str, Enum):
    """Enumeration for StateEnum

    Values:
      * off: Default state of a service, indicates not being monitored.
      * ok: Indicates the service is ready and functional.
      * fail: Indicates the service failed to launch/turn-up or is unresponsive.
    """

    OFF = "off"
    OK = "ok"
    FAIL = "fail"


class SwServiceItem(YangBaseModel):
    """Software service running in the system."""

    sv_name: str = Field(
        json_schema_extra={"is_config": False},
        description="A unique Id for each service instance on the NE. Contains card type, shelf, slot information.",
        alias="sv-name",
    )
    equipment: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference to the equipment on which the service is running.",
        min_length=1,
        max_length=64,
        default=None,
    )
    location: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Location where the service is running - host/container info.",
        default=None,
    )
    state: StateEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Current status of the service.", default=None
    )
    state_details: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Brief description of the service status.",
        default=None,
        alias="state-details",
    )
    cpu_usage: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Current usage of CPU by the service, in percentage. In a multi-core system, this indicates the overall usage relative to all cores.",
        ge=0,
        le=100,
        default=None,
        alias="cpu-usage",
    )
    memory_usage: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Current usage of memory by the service, in percentage.",
        ge=0,
        le=100,
        default=None,
        alias="memory-usage",
    )
    uptime: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Time since the service turned up, in days:hours:minutes.",
        default=None,
    )
    last_start_time: (
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
        description="Time of the last service start/boot.",
        default=None,
        alias="last-start-time",
    )
    reboot_count: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The number of times a service has restarted.",
        ge=0,
        default=None,
        alias="reboot-count",
    )


class StateEnum_1(str, Enum):
    """Enumeration for StateEnum

    Values:
      * off: Default state of a container, indicates it is not launched yet.
      * up: Indicates the container is up and running.
      * exited: Indicates the container has exited.
    """

    OFF = "off"
    UP = "up"
    EXITED = "exited"


class SwContainerItem(YangBaseModel):
    """List of OS-level containers."""

    container_name: str = Field(
        json_schema_extra={"is_config": False}, description="A unique Id for each container.", alias="container-name"
    )
    equipment: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reference to the equipment on which the container is running.",
        min_length=1,
        max_length=64,
        default=None,
    )
    state: StateEnum_1 | None = Field(
        json_schema_extra={"is_config": False}, description="Current status of the container.", default=None
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False}, description="Brief description of the container instance.", default=None
    )
    cpu_usage: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Current usage of CPU by the container, in percentage. In a multi-core system, this indicates the overall usage relative to all cores.",
        ge=0,
        le=100,
        default=None,
        alias="cpu-usage",
    )
    memory_usage: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Current usage of memory by the container, in percentage.",
        ge=0,
        le=100,
        default=None,
        alias="memory-usage",
    )
    uptime: str | None = Field(
        json_schema_extra={"is_config": False}, description="Time since the container started.", default=None
    )


class SwServices(YangBaseModel):
    """Information about the software services and containers on the node."""

    sw_control_rule: RestconfList[SwControlRuleItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Optional service-specific custom rules to overide default action upon service failure.",
        default=None,
        alias="sw-control-rule",
    )
    sw_service: RestconfList[SwServiceItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Software service running in the system.",
        default=None,
        alias="sw-service",
    )
    sw_container: RestconfList[SwContainerItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of OS-level containers.",
        default=None,
        alias="sw-container",
    )


class ProtocolEnum_3(str, Enum):
    """Enumeration for ProtocolEnum

    Values:
      * sftp: Represents sftp transfer protocol.
      * ftp: Represents ftp transfer protocol.
      * scp: Represents scp transfer protocol.
      * http: Represents http transfer protocol.
      * https: Represents https transfer protocol.
      * file: Represents local storage, including USB storage. Requires initial-path to be provided.
    """

    SFTP = "sftp"
    FTP = "ftp"
    SCP = "scp"
    HTTP = "http"
    HTTPS = "https"
    FILE = "file"


class FileServerItem(YangBaseModel):
    """User configurable file-server (e.g SFTP server), to be used by transfer operations (upload/download)."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Name of the server, as usable in download/upload commands.",
        min_length=1,
        max_length=64,
    )
    server_address: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Address of the file-server\n\nCondition (when): ../protocol != 'file'",
        default=None,
        alias="server-address",
    )
    server_port: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Port used for file transfer; if not provided, default will be used according with selected\nprotocol.\n\nCondition (when): ../protocol != 'file'",
        ge=0,
        default=None,
        alias="server-port",
    )
    protocol: ProtocolEnum_3 = Field(
        json_schema_extra={"is_config": True},
        description="The file transfer protocol that this server supports.\nNon-secure protocols (ftp and http) are supported conditionally on configured security policies.",
    )
    user_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User name credentials for the remote file server.\n\nCondition (when): ../protocol != 'file'",
        min_length=0,
        max_length=64,
        default=None,
        alias="user-name",
    )
    password: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Password credentials for the remote file server.\n\nCondition (when): ../protocol != 'file'",
        min_length=0,
        max_length=128,
        default=None,
    )
    initial_path: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The directory in the file server that is used as source/destination.\nIf empty, means the root directory (/) on the server is the initial path.\nMust be an absolute directory (e.g. starting with /).",
        min_length=0,
        max_length=256,
        default=None,
        alias="initial-path",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class FileServers(YangBaseModel):
    """Container of all configured file-servers."""

    file_server: RestconfList[FileServerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="User configurable file-server (e.g SFTP server), to be used by transfer operations (upload/download).",
        default=None,
        alias="file-server",
    )


class StatusEnum_4(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * idle: No upgrade status
      * upgrade-in-progress: NE upgrade in progress
      * upgrade-complete: NE upgrade complete
      * upgrade-partially-failed: NE upgrade partial complete
      * upgrade-failed: NE upgrade failed
      * validate-in-progress:  Chassis/Card validate in progress
      * validate-failed: Chassis/Card validation failed
      * validate-complete: Chassis/Card validation complete
      * apply-in-progress: Chassis/Card apply in progress
      * apply-failed: Chassis/Card apply failed
      * apply-complete: Chassis/Card apply complete
      * activate-in-progress: Chassis/Card activation in progress
      * activate-failed: Chassis/Card activation failed
      * activate-complete: Chassis/Card activation complete
      * no-communication: No communication
    """

    IDLE = "idle"
    UPGRADE_IN_PROGRESS = "upgrade-in-progress"
    UPGRADE_COMPLETE = "upgrade-complete"
    UPGRADE_PARTIALLY_FAILED = "upgrade-partially-failed"
    UPGRADE_FAILED = "upgrade-failed"
    VALIDATE_IN_PROGRESS = "validate-in-progress"
    VALIDATE_FAILED = "validate-failed"
    VALIDATE_COMPLETE = "validate-complete"
    APPLY_IN_PROGRESS = "apply-in-progress"
    APPLY_FAILED = "apply-failed"
    APPLY_COMPLETE = "apply-complete"
    ACTIVATE_IN_PROGRESS = "activate-in-progress"
    ACTIVATE_FAILED = "activate-failed"
    ACTIVATE_COMPLETE = "activate-complete"
    NO_COMMUNICATION = "no-communication"


class UpgradeStatusItem(YangBaseModel):
    """Provides information of the upgrade status for each entity in the system."""

    resource: str = Field(
        json_schema_extra={"is_config": False},
        description="The resource to which the status refers to.\n   May represent the entire ne, a chassis, or a card.\n   For ne and chassis, the results provide aggregated summaries of all cards in that scope.",
        min_length=0,
        max_length=255,
    )
    to_swload_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Target Software Load Version.",
        min_length=1,
        max_length=64,
        default=None,
        alias="to-swload-version",
    )
    status: StatusEnum_4 | None = Field(
        json_schema_extra={"is_config": False},
        description="The current upgrade status for this resource.",
        default=StatusEnum_4.IDLE,
    )
    start_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The start timestamp of the current phase of upgrade.\n   Will have value 'na' if this entity was idle since startup.",
        default=None,
        alias="start-time",
    )
    end_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The end timestamp of the current phase of upgrade.\n   Will have value 'na' if this entity has not finished any upgrade phase since startup.",
        default=None,
        alias="end-time",
    )
    step: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The identifier for the current upgrade step.",
        min_length=0,
        max_length=128,
        default=None,
    )
    step_start_time: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The timestamp at which the current upgrade step was initiated.",
        default=None,
        alias="step-start-time",
    )
    details: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Details on the current upgrade.",
        min_length=0,
        max_length=255,
        default=None,
    )


class SwloadStateEnum(str, Enum):
    """Enumeration for SwloadStateEnum

    Values:
      * active: Active software load.
      * inactive: Inactive software load.
      * installable: Installable software load.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    INSTALLABLE = "installable"


class SwloadStatusEnum(str, Enum):
    """Enumeration for SwloadStatusEnum

    Values:
      * status-unknown: Software load status unknown.
      * validate-in-progress: Software load validation in progress.
      * validate-complete: Software load validation completed.
      * validate-failed: Software load validation failed.
      * apply-in-progress: Software load apply in progress.
      * apply-complete: Software load apply completed.
      * apply-failed: Software load apply failed.
      * activate-in-progress: Software load activation in progress.
      * activate-failed: Software load activation failed.
      * activate-complete: Software load activation completed.
      * cancel-in-progress: Software load cancel in progress.
      * cancel-failed: Software load cancel failed.
      * cancel-complete: Software load cancel completed.
      * validate-timeout: Software load validate timeout.
      * apply-timeout: Software load apply timeout.
      * activate-timeout: Software load activate timeout.
      * cancel-timeout: Software load cancel timeout.
    """

    STATUS_UNKNOWN = "status-unknown"
    VALIDATE_IN_PROGRESS = "validate-in-progress"
    VALIDATE_COMPLETE = "validate-complete"
    VALIDATE_FAILED = "validate-failed"
    APPLY_IN_PROGRESS = "apply-in-progress"
    APPLY_COMPLETE = "apply-complete"
    APPLY_FAILED = "apply-failed"
    ACTIVATE_IN_PROGRESS = "activate-in-progress"
    ACTIVATE_FAILED = "activate-failed"
    ACTIVATE_COMPLETE = "activate-complete"
    CANCEL_IN_PROGRESS = "cancel-in-progress"
    CANCEL_FAILED = "cancel-failed"
    CANCEL_COMPLETE = "cancel-complete"
    VALIDATE_TIMEOUT = "validate-timeout"
    APPLY_TIMEOUT = "apply-timeout"
    ACTIVATE_TIMEOUT = "activate-timeout"
    CANCEL_TIMEOUT = "cancel-timeout"


class SwloadActivationTypeEnum(str, Enum):
    """Enumeration for SwloadActivationTypeEnum

    Values:
      * direct: No reboot type determined
      * warmstart: Update requires warm reboot
      * coldstart: Update requires cold reboot
    """

    DIRECT = "direct"
    WARMSTART = "warmstart"
    COLDSTART = "coldstart"


class StateEnum_2(str, Enum):
    """Enumeration for StateEnum

    Values:
      * installed: Software package installed
      * not-installed: Software package not installed
      * installation-failed: Software package install failed
      * unknown: Software package state unknown
    """

    INSTALLED = "installed"
    NOT_INSTALLED = "not-installed"
    INSTALLATION_FAILED = "installation-failed"
    UNKNOWN = "unknown"


class SwSubcomponentItem(YangBaseModel):
    """Software load subcomponent details"""

    state: StateEnum_2 | None = Field(
        json_schema_extra={"is_config": False}, description="Package state", default=StateEnum_2.UNKNOWN
    )
    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Package version", min_length=0, max_length=64, default=None
    )
    name: str = Field(json_schema_extra={"is_config": False}, description="Package name", min_length=1, max_length=256)
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Package information",
        min_length=0,
        max_length=512,
        default=None,
    )


class SwComponentItem(YangBaseModel):
    """Software load component details"""

    state: StateEnum_2 | None = Field(
        json_schema_extra={"is_config": False}, description="Package state", default=StateEnum_2.UNKNOWN
    )
    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Package version", min_length=0, max_length=64, default=None
    )
    name: str = Field(json_schema_extra={"is_config": False}, description="Package name", min_length=1, max_length=256)
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Package information",
        min_length=0,
        max_length=512,
        default=None,
    )
    sw_subcomponent: RestconfList[SwSubcomponentItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load subcomponent details",
        default=None,
        alias="sw-subcomponent",
    )


class PackagedFwItem(YangBaseModel):
    """Firmware version included in this software-load.
    Versions for the same firmware can be different per equipment-type.
    """

    equipment_type: str = Field(
        json_schema_extra={"is_config": False},
        description="Type of the equipment (card, etc) that will use this firmware.",
        min_length=0,
        max_length=32,
        alias="equipment-type",
    )
    fw_name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the firmware.",
        min_length=0,
        max_length=32,
        alias="fw-name",
    )
    fw_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Included version of the firmware.",
        min_length=0,
        max_length=32,
        default=None,
        alias="fw-version",
    )


class SoftwareLoadItem(YangBaseModel):
    """Information on the Software Load present in the system."""

    swload_state: SwloadStateEnum = Field(
        json_schema_extra={"is_config": False}, description="Software load state", alias="swload-state"
    )
    swload_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load version",
        min_length=1,
        max_length=64,
        default=None,
        alias="swload-version",
    )
    swload_manifest: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load manifest file.\n    Only of relevance for software load installable.",
        min_length=0,
        max_length=256,
        default=None,
        alias="swload-manifest",
    )
    swload_prepared: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load prepared.\n    Only of relevance for software load installable.",
        default=None,
        alias="swload-prepared",
    )
    swload_status: SwloadStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load current status.\n    Only of relevance for software load installable.",
        default=None,
        alias="swload-status",
    )
    swload_information: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load information",
        min_length=0,
        max_length=1024,
        default=None,
        alias="swload-information",
    )
    swload_activation_type: SwloadActivationTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load activation type\n    Only of relevance for software load state installable.",
        default=SwloadActivationTypeEnum.DIRECT,
        alias="swload-activation-type",
    )
    swload_vendor: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load vendor",
        min_length=0,
        max_length=256,
        default=None,
        alias="swload-vendor",
    )
    swload_product: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load product",
        min_length=0,
        max_length=256,
        default=None,
        alias="swload-product",
    )
    swload_label: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load label",
        min_length=0,
        max_length=256,
        default=None,
        alias="swload-label",
    )
    swload_delta_label: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load delta label;\n    Only of relevance for software load state active.",
        min_length=0,
        max_length=256,
        default=None,
        alias="swload-delta-label",
    )
    swload_pkg_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load package type\n    Only of relevance for software load state installable.",
        min_length=0,
        max_length=256,
        default=None,
        alias="swload-pkg-type",
    )
    sw_component: RestconfList[SwComponentItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load component details",
        default=None,
        alias="sw-component",
    )
    packaged_fw: RestconfList[PackagedFwItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Firmware version included in this software-load.\nVersions for the same firmware can be different per equipment-type.",
        default=None,
        alias="packaged-fw",
    )


class ManifestComponentItem(YangBaseModel):
    """packaged component details"""

    state: StateEnum_2 | None = Field(
        json_schema_extra={"is_config": False}, description="Package state", default=StateEnum_2.UNKNOWN
    )
    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Package version", min_length=0, max_length=64, default=None
    )
    name: str = Field(json_schema_extra={"is_config": False}, description="Package name", min_length=1, max_length=256)
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Package information",
        min_length=0,
        max_length=512,
        default=None,
    )


class ManifestFirmwareItem(YangBaseModel):
    """Packaged Firmware detials."""

    fw_name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the firmware.",
        min_length=0,
        max_length=32,
        alias="fw-name",
    )
    fw_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Included version of the firmware.",
        min_length=0,
        max_length=32,
        default=None,
        alias="fw-version",
    )


class FruInfoItem(YangBaseModel):
    """The packaged FRU information associated to a particular equipment-type."""

    equipment_type: str = Field(
        json_schema_extra={"is_config": False},
        description="Type of the equipment",
        min_length=0,
        max_length=32,
        alias="equipment-type",
    )
    manifest_component: RestconfList[ManifestComponentItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="packaged component details",
        default=None,
        alias="manifest-component",
    )
    manifest_firmware: RestconfList[ManifestFirmwareItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Packaged Firmware detials.",
        default=None,
        alias="manifest-firmware",
    )


class DownloadedImageItem(YangBaseModel):
    """Downloaded software image files"""

    name: str = Field(
        json_schema_extra={"is_config": False},
        description="Downloaded software image name",
        min_length=0,
        max_length=256,
    )
    signature: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False}, description="Downloaded software image file signature", default=None
    )


class ManifestItem(YangBaseModel):
    """Downloaded manifest file and it's information."""

    manifest_file: str = Field(
        json_schema_extra={"is_config": False},
        description="Manifest file",
        min_length=0,
        max_length=256,
        alias="manifest-file",
    )
    manifest_signature: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Manifest file signature",
        default=None,
        alias="manifest-signature",
    )
    fru_info: RestconfList[FruInfoItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="The packaged FRU information associated to a particular equipment-type.",
        default=None,
        alias="fru-info",
    )
    downloaded_image: RestconfList[DownloadedImageItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Downloaded software image files",
        default=None,
        alias="downloaded-image",
    )
    downloaded_on: (
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
        description="Manifest file downloaded timestamp",
        default=None,
        alias="downloaded-on",
    )
    information: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on the manifest downloaded",
        min_length=0,
        max_length=256,
        default=None,
    )


class Downloads(YangBaseModel):
    """Downloaded manifest files and associated image files."""

    manifest: RestconfList[ManifestItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Downloaded manifest file and it's information.",
        default=None,
    )


class StateEnum_3(str, Enum):
    """Enumeration for StateEnum

    Values:
      * running: Third party app running.
      * stopped: Third party app stopped.
      * failed: Third party app failed.
    """

    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class ThirdPartyAppInfoItem(YangBaseModel):
    """List of 3rd party applications available per location."""

    app_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": False},
        description="Third party app name.",
        min_length=1,
        max_length=64,
        alias="app-name",
    )
    version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app version.",
        min_length=0,
        max_length=64,
        default=None,
    )
    state: StateEnum_3 | None = Field(
        json_schema_extra={"is_config": False}, description="Third party app state.", default=StateEnum_3.RUNNING
    )
    information: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app information.",
        min_length=0,
        max_length=1024,
        default=None,
    )


class SoftwareLocationItem(YangBaseModel):
    """Software load information associated to each of the equipment."""

    location_id: str = Field(
        json_schema_extra={"is_config": False},
        description="Location of the equipment",
        min_length=0,
        max_length=64,
        alias="location-id",
    )
    software_load: RestconfList[SoftwareLoadItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on the Software Load present in the system.",
        default=None,
        alias="software-load",
    )
    third_party_app_info: RestconfList[ThirdPartyAppInfoItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of 3rd party applications available per location.",
        default=None,
        alias="third-party-app-info",
    )


class ThirdPartyAppItem(YangBaseModel):
    """List of 3rd party applications."""

    app_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Third party app name.",
        min_length=1,
        max_length=64,
        alias="app-name",
    )
    version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app version.",
        min_length=0,
        max_length=64,
        default=None,
    )
    state: StateEnum_3 | None = Field(
        json_schema_extra={"is_config": False}, description="Third party app state.", default=StateEnum_3.RUNNING
    )
    information: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app information.",
        min_length=0,
        max_length=1024,
        default=None,
    )
    vendor: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app vendor.",
        min_length=0,
        max_length=64,
        default=None,
    )
    product: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app product.",
        min_length=0,
        max_length=256,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Third party app label.",
        min_length=0,
        max_length=256,
        default=None,
    )
    enable: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Third-party-app enabled state. If enabled, app is started(app is enabled also upon system restart). If disabled, app is stopped.",
        default=True,
    )


class FileStatusEnum(str, Enum):
    """Enumeration for FileStatusEnum

    Values:
      * valid: fw file is present and is valid (crc matches).
      * invalid: fw file is present but is invalid (crc doesn't match).
      * missing: fw file is not present.
    """

    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"


class ThirdPartyFwItem(YangBaseModel):
    """List of 3rd party fw files available to be used to upgrade 3rd party equipment."""

    fw_name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the firmware.",
        min_length=0,
        max_length=64,
        alias="fw-name",
    )
    file_status: FileStatusEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Firmware file status.", default=None, alias="file-status"
    )
    path: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Path for the firmware image.",
        min_length=0,
        max_length=255,
        default=None,
    )
    version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Firmware version.",
        min_length=0,
        max_length=64,
        default=None,
    )
    crc: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Cyclic redundancy check (CRC) of the firmware image, used to validate the file when present.",
        min_length=0,
        max_length=64,
        default=None,
    )
    vendor: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The vendor of the firmware.",
        min_length=0,
        max_length=64,
        default=None,
    )
    part_number: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="The part-number of the firmware.",
        min_length=0,
        max_length=64,
        default=None,
        alias="part-number",
    )
    nsa_upgrade_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Versions from where the upgrade is non service affecting (nsa).",
        min_length=0,
        max_length=255,
        default=None,
        alias="nsa-upgrade-version",
    )
    present_in_eqpt: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of resources that contain this version.",
        default=None,
        alias="present-in-eqpt",
    )
    applicable_eqpt: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of resources that this firmware can be applied apply.",
        default=None,
        alias="applicable-eqpt",
    )


class SwManagement(YangBaseModel):
    """Software management information."""

    upgrade_status: RestconfList[UpgradeStatusItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Provides information of the upgrade status for each entity in the system.",
        default=None,
        alias="upgrade-status",
    )
    software_load: RestconfList[SoftwareLoadItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Information on the Software Load present in the system.",
        default=None,
        alias="software-load",
    )
    downloads: Downloads | None = Field(
        json_schema_extra={"is_config": False},
        description="Downloaded manifest files and associated image files.",
        default=None,
    )
    software_location: RestconfList[SoftwareLocationItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Software load information associated to each of the equipment.",
        default=None,
        alias="software-location",
    )
    third_party_app: RestconfList[ThirdPartyAppItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of 3rd party applications.",
        default=None,
        alias="third-party-app",
    )
    third_party_fw: RestconfList[ThirdPartyFwItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of 3rd party fw files available to be used to upgrade 3rd party equipment.",
        default=None,
        alias="third-party-fw",
    )


class DatabaseTypeEnum(str, Enum):
    """Enumeration for DatabaseTypeEnum

    Values:
      * active
      * onehour
      * oneday
      * oneweek
      * temp
      * manual
      * rollback
    """

    ACTIVE = "active"
    ONEHOUR = "onehour"
    ONEDAY = "oneday"
    ONEWEEK = "oneweek"
    TEMP = "temp"
    MANUAL = "manual"
    ROLLBACK = "rollback"


class DatabaseStateEnum(str, Enum):
    """Enumeration for DatabaseStateEnum

    Values:
      * active
      * inactive
    """

    ACTIVE = "active"
    INACTIVE = "inactive"


class DatabaseItem(YangBaseModel):
    """The list of the databases in the system."""

    database_type: DatabaseTypeEnum = Field(
        json_schema_extra={"is_config": False}, description="Database identifier.", alias="database-type"
    )
    database_state: DatabaseStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the state of the database.",
        default=None,
        alias="database-state",
    )
    database_version: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the database version.",
        min_length=0,
        max_length=20,
        default=None,
        alias="database-version",
    )
    database_vendor: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Vendor information of the database.",
        min_length=0,
        max_length=32,
        default=None,
        alias="database-vendor",
    )
    database_product: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the network element family this database belongs to.",
        min_length=0,
        max_length=32,
        default=None,
        alias="database-product",
    )
    ne_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="User assigned name for this NE as present in this database.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-name",
    )
    node_controller_serial_number: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Serial number of the node controller.",
        min_length=0,
        max_length=32,
        default=None,
        alias="node-controller-serial-number",
    )
    loopback_ipv4: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="loopback ipv4 address.",
        default=None,
        alias="loopback-ipv4",
    )
    loopback_ipv6: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                    v,
                )
            ),
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="loopback ipv6 address.",
        default=None,
        alias="loopback-ipv6",
    )
    backup_time: (
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
        description="Indicates the database snapshot backup time.",
        default=None,
        alias="backup-time",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Database description",
        min_length=0,
        max_length=128,
        default=None,
    )


class SessionTypeEnum_1(str, Enum):
    """Enumeration for SessionTypeEnum

    Values:
      * gnmi-dial-in: GNMI dial-in session type.
      * gnmi-dial-out-tunnel: GNMI dial-out via tunnel session type.
      * gnmi-dial-out-reverse-rpc: GNMI dial-out via reverse RPC session type.
    """

    GNMI_DIAL_IN = "gnmi-dial-in"
    GNMI_DIAL_OUT_TUNNEL = "gnmi-dial-out-tunnel"
    GNMI_DIAL_OUT_REVERSE_RPC = "gnmi-dial-out-reverse-rpc"


class SessionProtocolEnum_1(str, Enum):
    """Enumeration for SessionProtocolEnum

    Values:
      * gnmi: GNMI protocol session.
    """

    GNMI = "gnmi"


class EncodingEnum(str, Enum):
    """Enumeration for EncodingEnum

    Values:
      * json
      * bytes
      * proto
      * ascii
      * json-ietf
    """

    JSON = "json"
    BYTES = "bytes"
    PROTO = "proto"
    ASCII = "ascii"
    JSON_IETF = "json-ietf"


class TransferModeEnum(str, Enum):
    """Enumeration for TransferModeEnum

    Values:
      * stream: Values streamed by the target.
      * once: Values sent once-off by the target.
      * poll: Values sent in response to a poll request.
    """

    STREAM = "stream"
    ONCE = "once"
    POLL = "poll"


class SubscriptionPathModeEnum(str, Enum):
    """Enumeration for SubscriptionPathModeEnum

    Values:
      * target-defined: Subcription updates are sent according with system definition.
      * on-change: Subscription updates are sent when there are changes.
      * sample: Subscription updates are sent periodically.
    """

    TARGET_DEFINED = "target-defined"
    ON_CHANGE = "on-change"
    SAMPLE = "sample"


class SubscriptionPathItem(YangBaseModel):
    """List of single subscriptions paths keyed by
    subscription-path-name.
    """

    subscription_path_name: str = Field(
        json_schema_extra={"is_config": False},
        description="Name of the single subscription path in the subscription list.",
        min_length=0,
        max_length=64,
        alias="subscription-path-name",
    )
    subscription_path: str = Field(
        json_schema_extra={"is_config": False},
        description="Specifies a path in the data model path corresponding to\nthe data in the message",
        min_length=1,
        max_length=520,
        alias="subscription-path",
    )
    subscription_path_origin: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies the schema tree in order to disambiguate the path.",
        min_length=0,
        max_length=64,
        default=None,
        alias="subscription-path-origin",
    )
    subscription_path_mode: SubscriptionPathModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Specify how the device should return the values of the subscription-path",
        default=SubscriptionPathModeEnum.TARGET_DEFINED,
        alias="subscription-path-mode",
    )
    sample_interval: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Time in milliseconds between the device's sample of a\ntelemetry data source. For example, setting this to 2000\nwould require the local device to collect the telemetry\ndata every 2000 milliseconds. There can be latency or jitter\nin transmitting the data, but the sample must occur at\nthe specified interval.\nThe timestamp must reflect the actual time when the data\nwas sampled, not simply the previous sample timestamp +\nsample-interval.\nSet to 0 when optional. On the case of stream 'target-defined'\nit is automatically adjusted from 0 to 10 seconds.",
        ge=0,
        le=18446744073709551615,
        default=0,
        alias="sample-interval",
    )
    heartbeat_interval: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum time interval in milliseconds that may pass\nbetween updates from a device to a telemetry collector.\nIf this interval expires, but there is no updated data to\nsend (such as if suppress_updates has been configured), the\ndevice must send a telemetry message to the collector.\nSet to 0 when optional. On the case of stream 'target-defined',\nif 'sample-interval' is not provided and heartbeat is lower than\n10 seconds, the heartbeat-interval is automatically adjusted to 20 seconds.",
        ge=0,
        le=18446744073709551615,
        default=0,
        alias="heartbeat-interval",
    )
    suppress_redundant: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Boolean flag to control suppression of redundant\ntelemetry updates to the collector platform. If this flag is\nset to TRUE, then the collector will only send an update at\nthe configured interval if a subscribed data value has\nchanged. Otherwise, the device will not send an update to\nthe collector until expiration of the heartbeat interval.",
        default=True,
        alias="suppress-redundant",
    )


class CurrentSubscriptionItem(YangBaseModel):
    """List representation of telemetry subscriptions that
    are configured in the system, otherwise known
    as current telemetry subscriptions.
    """

    subscription_name: str = Field(
        json_schema_extra={"is_config": False},
        description="User configured identifier of the telemetry\nsubscription. This value is used primarily for\nsubscriptions configured locally on the network\nelement. For dial-in subscription this name is\nconfigured by the NBI.",
        min_length=1,
        max_length=128,
        alias="subscription-name",
    )
    related_session_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifier of the telemetry subscription\nsession.",
        min_length=1,
        max_length=128,
        default=None,
        alias="related-session-id",
    )
    related_dial_out_server: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Identifier of the subscrition dial-out\nserver address. Only applicable to\ndial-out based subscriptions.",
        min_length=1,
        max_length=64,
        default=None,
        alias="related-dial-out-server",
    )
    session_type: SessionTypeEnum_1 = Field(
        json_schema_extra={"is_config": False},
        description="Identifier of the type of subscription session.",
        alias="session-type",
    )
    session_protocol: SessionProtocolEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Selection of the transport protocol for the telemetry\nstream.",
        default=SessionProtocolEnum_1.GNMI,
        alias="session-protocol",
    )
    encoding: EncodingEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies the data encoding scheme to be used for data\nsent to and from the target device.  The encoding may\nbe specified for all data, or optionally on a per-RPC\nbasis if supported by the target.",
        default=EncodingEnum.JSON_IETF,
    )
    transfer_mode: TransferModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Specifies the data transfer mode to the target device.",
        default=TransferModeEnum.STREAM,
        alias="transfer-mode",
    )
    updates_only: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="A Boolean flag allowing to only send updates to the current state,\nwhen set to true the device will not send the initial current value,\nrather only changes to the initial value.",
        default=False,
        alias="updates-only",
    )
    user_access: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Username in order to resolve paths according to user access.",
        default=None,
        alias="user-access",
    )
    subscription_path: RestconfList[SubscriptionPathItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of single subscriptions paths keyed by\nsubscription-path-name.",
        default=None,
        alias="subscription-path",
    )


class Subscriptions(YangBaseModel):
    """This container holds information for both persistent
    and dynamic telemetry subscriptions.
    """

    current_subscription: RestconfList[CurrentSubscriptionItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List representation of telemetry subscriptions that\nare configured in the system, otherwise known\nas current telemetry subscriptions.",
        default=None,
        alias="current-subscription",
    )


class Telemetry(YangBaseModel):
    """Top level configuration and state for the
    device telemetry system.
    """

    subscriptions: Subscriptions | None = Field(
        json_schema_extra={"is_config": True},
        description="This container holds information for both persistent\nand dynamic telemetry subscriptions.",
        default=None,
    )


class RestoreFromChassisStorageEnum(str, Enum):
    """Enumeration for RestoreFromChassisStorageEnum

    Values:
      * disabled: Chassis storage is not used for restoration in this NE.
      * auto-restore: SW and DB are stored on the chassis storage and restored in recovery mode. A manual clear recovery-mode command is then necessary. It allows the user to validate the restored system before affecting the HW.
      * auto-in-service: SW and DB are stored on the chassis storage and restored in recovery mode. On successful restore, the NC will automatically leave recovery mode.
    """

    DISABLED = "disabled"
    AUTO_RESTORE = "auto-restore"
    AUTO_IN_SERVICE = "auto-in-service"


class RestoreStatusEnum(str, Enum):
    """Enumeration for RestoreStatusEnum

    Values:
      * init: Provisioning service is starting.
      * image-install-in-progress: Installing backup image.
      * db-restore-in-progress: Restoring database.
      * check-completed: Provisioning service completed provisioning.
      * failed: Provisioning failed, requires manual provisioning.
      * disabled: Provisioning service is disabled, no backups are being performed.
      * wait-for-upgrade: Waiting for system reboot after image upgrade.
      * wait-for-db-restore: Waiting for system reboot after database restore.
    """

    INIT = "init"
    IMAGE_INSTALL_IN_PROGRESS = "image-install-in-progress"
    DB_RESTORE_IN_PROGRESS = "db-restore-in-progress"
    CHECK_COMPLETED = "check-completed"
    FAILED = "failed"
    DISABLED = "disabled"
    WAIT_FOR_UPGRADE = "wait-for-upgrade"
    WAIT_FOR_DB_RESTORE = "wait-for-db-restore"


class BackupStatusEnum(str, Enum):
    """Enumeration for BackupStatusEnum

    Values:
      * successful: Provisioning service is enabled, backups are being performed successfully.
      * failed: Provisioning service is enabled, a backup failed.
      * in-progress: Backup is in progress.
      * unknown: Backup is in an unknown status.
    """

    SUCCESSFUL = "successful"
    FAILED = "failed"
    IN_PROGRESS = "in-progress"
    UNKNOWN = "unknown"


class Recovery(YangBaseModel):
    """Status and configuration of system recovery from chassis storage."""

    restore_from_chassis_storage: RestoreFromChassisStorageEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="This attribute is only relevant when a chassis storage is available.\nIt allows the operator to control how the system behaves in such cases.\nWhen no chassis storage is available, this attribute has no effect.",
        default=RestoreFromChassisStorageEnum.AUTO_IN_SERVICE,
        alias="restore-from-chassis-storage",
    )
    restore_status: RestoreStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current state of the restoration.",
        default=RestoreStatusEnum.INIT,
        alias="restore-status",
    )
    backup_status: BackupStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Current state of the last backup.",
        default=BackupStatusEnum.UNKNOWN,
        alias="backup-status",
    )
    last_backup: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp with the last backup performed.",
        default="never",
        alias="last-backup",
    )
    next_backup: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp with the next backup performed.",
        default="never",
        alias="next-backup",
    )


class TemplateItem(YangBaseModel):
    """A single template entry, allowing an individual rule for defining a default value for a given IOA attribute.
    A template entry is defined by an object+attribute pair, and then the value to be used as that attribute's default.
    Additionally, a template may be conditional, where the default is only applied if the conditional criteria is obeyed.
    Multiple template entries may coexist for the same object+attribute pair with different conditions.
    Templates are automatically applied whenever an attribute value is defaulted, as long as the template belongs to the
    enabled template-group.
    It is also possible to force apply the templates using the 'apply-template' RPC.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name of the template entry within the template-group.",
        min_length=1,
        max_length=64,
    )
    sequence_id: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The id of this template entry, used to define the order in which templates are processed.\nLower number ids are processed first.\nId can change over the lifetime of the template entry to re-sort different entries.\nIf not provided, sequence-id will be set to the currently used latest id plus 1 (e.g. will go to the end of the list).",
        ge=1,
        default=None,
        alias="sequence-id",
    )
    object: str = Field(
        json_schema_extra={"is_config": True},
        description="Object name that this template entry applies to.\nNeeds to match an existing config true IOA object name (representing a container or a list).\nNote: currently, IOA object names are globally identifiable (e.g. the same name is not used\nmore than once in the IOA hierarchy); as such, the name of the object is sufficient to\nglobally identify it (instead of having to provide an XPath of the object.",
        min_length=1,
        max_length=128,
    )
    attribute: str = Field(
        json_schema_extra={"is_config": True},
        description="Attribute name that this template entry applies to.\nNeeds to match a config true attribute in the provided object.",
        min_length=1,
        max_length=128,
    )
    value: str = Field(
        json_schema_extra={"is_config": True},
        description="Attribute value to be used by this template entry.\nNeeds to match a valid value of the selected attribute.\nNote: even though the value is provided as a string, this may represent any YANG type.\nUpon being configured, the template value will be checked against the target attribute data type.\nUpon being applied, this value will be checked for validity against the attribute preconditions,\nand the template will not be applied if it violates any precondition (just like a normal 'set' would).",
        min_length=1,
        max_length=128,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    condition: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": True},
        description="Optional criteria for this template entry to be applied.\nTemplate is applied if object+attribute match, and the condition is obeyed.\nCondition matches the format '<criteria>=<value>', where <criteria> may be:\n- card-type -  matching one of the supported card-types\n- card-subtype - matching one of the supported card-subtypes\n- service-type - matching a trib-ptp service-type parameter\n- port-type - matching a the port-type parameter of the port\n- AID - matching a custom AID\nBeing a leaf-list, multiple conditions can be provided; the condition is considered as\napplicable if all criteria are satisfied (AND logic).\nEach criteria can only be provided once.\nUpon configuration, the <value> part of the condition will be validated, and invalid values will be\nrejected (for example, 'card-type=ABC' would be rejected, if 'ABC' was an invalid supported card type).\n\nIf multiple template entries exist for the same object+attribute, the entries are processed\nbased on their sequence-id and condition criteria, and the first entry that satisfies the\ncriteria is selected; if no condition is provided, the template is consider unconditional;\nif all considered template entries don't satisfy their conditions, then no custom template is\napplied (e.g. normal system defined default value is used).\n\nDisclaimer: conditions will be accepted even if they do not apply to the selected object - it is\nup to the user to consider which conditions are relevant.\nFor example, using an AID filter to an entity that does not have that concept would mean the condition\nwould never be observed - effectively meaning the template would never be applied.",
        min_length=0,
        max_length=128,
        default=None,
    )


class TemplateGroupItem(YangBaseModel):
    """Represents a configuration template-group, containing a list of template entries.
    Using this feature, a user can configure what are the default values for configurable attributes in the IOA model.
    Multiple template-groups may coexist, but only one can be enabled at a time (based on the 'enabled' attribute).
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="The name of the template-group.",
        min_length=1,
        max_length=64,
    )
    enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Whether this template-group is enabled or not.\nNote: only one template-group can be enabled at a time.\nDefault is 'true' if there is no other template-group enabled, otherwise 'false'.",
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    template: RestconfList[TemplateItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="A single template entry, allowing an individual rule for defining a default value for a given IOA attribute.\nA template entry is defined by an object+attribute pair, and then the value to be used as that attribute's default.\nAdditionally, a template may be conditional, where the default is only applied if the conditional criteria is obeyed.\nMultiple template entries may coexist for the same object+attribute pair with different conditions.\nTemplates are automatically applied whenever an attribute value is defaulted, as long as the template belongs to the\nenabled template-group.\nIt is also possible to force apply the templates using the 'apply-template' RPC.",
        default=None,
    )


class Templates(YangBaseModel):
    """Top level container containing all supported template types."""

    template_group: RestconfList[TemplateGroupItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Represents a configuration template-group, containing a list of template entries.\nUsing this feature, a user can configure what are the default values for configurable attributes in the IOA model.\nMultiple template-groups may coexist, but only one can be enabled at a time (based on the 'enabled' attribute).",
        default=None,
        alias="template-group",
    )


class SystemPolicies(YangBaseModel):
    """Object keeping generic system policies."""

    commit_tracking: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables the commit-repository feature.\nWith this feature enabled, all configuration changes done via running or candidate datastores are stored as\ncommit-records, which can then be visualized, compared and rolled back.",
        default=EnableSwitchEnum.DISABLED,
        alias="commit-tracking",
    )


class SystemSystem(YangBaseModel):
    """System Configuration container"""

    security: Security | None = Field(
        json_schema_extra={"is_config": True}, description="Top level security container.", default=None
    )
    syslog: Syslog | None = Field(
        json_schema_extra={"is_config": True},
        description="Central configuration for logging functionality via syslog.\nIncludes control of local log files, remote logging configuration and logging in serial console.",
        default=None,
    )
    protocols: Protocols | None = Field(
        json_schema_extra={"is_config": True}, description="Container of management protocol objects.", default=None
    )
    scheduled_tasks: ScheduledTasks | None = Field(
        json_schema_extra={"is_config": True},
        description="Container of individual user-configurable scheduled commands.",
        default=None,
        alias="scheduled-tasks",
    )
    ztp: Ztp | None = Field(
        json_schema_extra={"is_config": False},
        description="Zero Touch Provisioning status.\nPlease see RPC 'change-ztp-mode' for ZTP configuration.",
        default=None,
    )
    transfer: Transfer | None = Field(
        json_schema_extra={"is_config": True}, description="Information associated with file transfer.", default=None
    )
    networking: Networking | None = Field(
        json_schema_extra={"is_config": True}, description="Top level container for networking model.", default=None
    )
    clock: Clock | None = Field(json_schema_extra={"is_config": True}, description="System clock.", default=None)
    ntp: Ntp | None = Field(
        json_schema_extra={"is_config": True}, description="Network Time Protocol Configuration.", default=None
    )
    sw_services: SwServices | None = Field(
        json_schema_extra={"is_config": True},
        description="Information about the software services and containers on the node.",
        default=None,
        alias="sw-services",
    )
    file_servers: FileServers | None = Field(
        json_schema_extra={"is_config": True},
        description="Container of all configured file-servers.",
        default=None,
        alias="file-servers",
    )
    sw_management: SwManagement | None = Field(
        json_schema_extra={"is_config": True},
        description="Software management information.",
        default=None,
        alias="sw-management",
    )
    database: RestconfList[DatabaseItem] | None = Field(
        json_schema_extra={"is_config": False}, description="The list of the databases in the system.", default=None
    )
    telemetry: Telemetry | None = Field(
        json_schema_extra={"is_config": True},
        description="Top level configuration and state for the\ndevice telemetry system.",
        default=None,
    )
    recovery: Recovery | None = Field(
        json_schema_extra={"is_config": True},
        description="Status and configuration of system recovery from chassis storage.",
        default=None,
    )
    templates: Templates | None = Field(
        json_schema_extra={"is_config": True},
        description="Top level container containing all supported template types.",
        default=None,
    )
    system_policies: SystemPolicies | None = Field(
        json_schema_extra={"is_config": True},
        description="Object keeping generic system policies.",
        default=None,
        alias="system-policies",
    )


class FunctionEnum(str, Enum):
    """Enumeration for FunctionEnum

    Values:
      * pa: Pre-amplifier.
      * ba: Booster (booster-amplifier).
      * inline: Inline amplifier (ILA node-types).
      * add: Add amplifier.
      * drop: Drop amplifier.
      * backward-raman: Raman amplifier.
      * edfa-tof: Erbium-Doped Fiber Amplifier/Tunable Optical Filter.
      * ase-idler-source: ASE Idler source.
      * idler: ASE Idler service (within an RD card).
    """

    PA = "pa"
    BA = "ba"
    INLINE = "inline"
    ADD = "add"
    DROP = "drop"
    BACKWARD_RAMAN = "backward-raman"
    EDFA_TOF = "edfa-tof"
    ASE_IDLER_SOURCE = "ase-idler-source"
    IDLER = "idler"


class ControlModeEnum(str, Enum):
    """Enumeration for ControlModeEnum

    Values:
      * auto-max-pw: Automatic Maximum Power.
      * manual: Manual gain.
    """

    AUTO_MAX_PW = "auto-max-pw"
    MANUAL = "manual"


class AmpControlSupportEnum(str, Enum):
    """Enumeration for AmpControlSupportEnum

    Values:
      * auto: Manual and auto-max-pw 'control-mode' supported.
      * manual-only: Only manual 'control-mode' supported.
    """

    AUTO = "auto"
    MANUAL_ONLY = "manual-only"


class AmplifierModeEnum(str, Enum):
    """Enumeration for AmplifierModeEnum

    Values:
      * constant-power: Contant Power
      * constant-gain: Constant Gain
    """

    CONSTANT_POWER = "constant-power"
    CONSTANT_GAIN = "constant-gain"


class BandOfTransmissionEnum(str, Enum):
    """Enumeration for BandOfTransmissionEnum

    Values:
      * c-band-4.85THz: Standard C-band (4.85 THz)
      * c-band-6.1THz: SuperC-band (6.1 THz)
      * l-band-4.85THz: Standard L-band (4.85 THz)
    """

    C_BAND_4_85THZ = "c-band-4.85THz"
    C_BAND_6_1THZ = "c-band-6.1THz"
    L_BAND_4_85THZ = "l-band-4.85THz"


class GainRangeTypeEnum(str, Enum):
    """Enumeration for GainRangeTypeEnum

    Values:
      * standard: standard gain
      * low: low gain
      * high: high gain
    """

    STANDARD = "standard"
    LOW = "low"
    HIGH = "high"


class AmplifierTypeEnum(str, Enum):
    """Enumeration for AmplifierTypeEnum

    Values:
      * fixed-gain-EDFA: Fixed Gain EDFA
      * variable-gain-EDFA: Variable Gain EDFA
    """

    FIXED_GAIN_EDFA = "fixed-gain-EDFA"
    VARIABLE_GAIN_EDFA = "variable-gain-EDFA"


class VoaControlModeEnum(str, Enum):
    """Enumeration for VoaControlModeEnum

    Values:
      * manual: Manual target attenuation.
      * constant-power: Constant Power.
    """

    MANUAL = "manual"
    CONSTANT_POWER = "constant-power"


class TiltControlModeEnum(str, Enum):
    """Enumeration for TiltControlModeEnum

    Values:
      * manual: User manually controls amplifier tilt
      * auto: System implicitly control amplifier tilt per configured fiber parameters
      * auto-planned: System implicitly controls amplifier tilt per planning tool configured parameters
    """

    MANUAL = "manual"
    AUTO = "auto"
    AUTO_PLANNED = "auto-planned"


class SupportedGainRangeItem(YangBaseModel):
    """Supported gain range(s), min. and max. gain"""

    gain_range_type: GainRangeTypeEnum = Field(
        json_schema_extra={"is_config": False}, description="Type of Gain Range", alias="gain-range-type"
    )
    gain_range_min: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The minimum settable gain-target for this type of range ('standard'/ 'low'/ 'high').",
        default=None,
        alias="gain-range-min",
    )
    gain_range_max: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The maximum settable gain-target for this type of range ('standard'/ 'low'/ 'high').",
        default=None,
        alias="gain-range-max",
    )


class AmplifierItem(YangBaseModel):
    """Amplifier container."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Non-configurable name: derived from chass/slot and degree.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_input_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Rx (input) Port that hold this object",
        default=None,
        alias="supporting-input-port",
    )
    supporting_output_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Tx (output) Port that hold this object",
        default=None,
        alias="supporting-output-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    function: FunctionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Which NE function the ne-function object works as.",
        default=None,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    partner_amplifier: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The partner amplifier for PAx/ BAX instalments.\nAt cards with dual-band, by convention, this is always not-applicable.",
        default="not-applicable",
        alias="partner-amplifier",
    )
    amplifier_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The enable switch of amplifier(s)\nIn cards with dual-band, this attribute is relevant at the C-band related amplifier.",
        default=None,
        alias="amplifier-enable",
    )
    forced_shutdown: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="For cards with dual-band, one amplifier be forced to be shutdown by setting this attribute to 'yes'.",
        default=False,
        alias="forced-shutdown",
    )
    control_mode: ControlModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of control-mode.",
        default=ControlModeEnum.AUTO_MAX_PW,
        alias="control-mode",
    )
    amp_control_support: AmpControlSupportEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether 'control-mode' can be configured as 'auto-max-pw' or not.",
        default=AmpControlSupportEnum.AUTO,
        alias="amp-control-support",
    )
    amplifier_mode: AmplifierModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The amplifier operating mode of the amplifier (gain or power control).",
        default=AmplifierModeEnum.CONSTANT_GAIN,
        alias="amplifier-mode",
    )
    pump_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The state of the pump.",
        default=EnableSwitchEnum.DISABLED,
        alias="pump-state",
    )
    actual_transmission_band: BandOfTransmissionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Currently assigned transmission band. If amplifier is not at a degree, it will be 4.85 THz by convention.",
        default=BandOfTransmissionEnum.C_BAND_4_85THZ,
        alias="actual-transmission-band",
    )
    gain_range_control: OscControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Automatic or Manual Gain Range configuration.",
        default=OscControlEnum.AUTO,
        alias="gain-range-control",
    )
    span_loss_control: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Span Loss Control configuration.\n    Only of relevance for inline amplifier(s) and preamp(s).",
        default=EnableSwitchEnum.ENABLED,
        alias="span-loss-control",
    )
    gain_range_target: GainRangeTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Gain Range Target\n\nCondition (when): ../gain-range-control = 'manual'",
        default=GainRangeTypeEnum.STANDARD,
        alias="gain-range-target",
    )
    gain_range_actual: GainRangeTypeEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Actual Gain Range", default=None, alias="gain-range-actual"
    )
    gain_target: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="For manual control mode: setting gain to the amplifier for constant-gain mode.",
        default=0.0,
        alias="gain-target",
    )
    gain_operating: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Operating gain of the amplifier that is the actually configured gain on the amplifier.\nWhen card is plugged out, or EDFA disabled, gain-operating is 0.0.",
        default=0.0,
        alias="gain-operating",
    )
    optimum_edfa_gain: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="System reports the optimum EDFA gain the required equipped EDFA has.\nBy convention system reports 0 dB when card is not required equipped.",
        default=None,
        alias="optimum-edfa-gain",
    )
    gain_adjustment: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Gain range adjustment:\nFor auto control mode: gain offset defined by the user.\nThe value is used for adjustment of gain when the amplifier is in automatic control mode, the automatically calculated gain will include offset of this attribute.\nOnly supported on amplifiers with 'function' = 'pa' or 'inline'.\n\nCondition (when): ../control-mode != 'manual'",
        default=0,
        alias="gain-adjustment",
    )
    amplifier_type: AmplifierTypeEnum = Field(
        json_schema_extra={"is_config": False}, description="Type of the amplifier HW.", alias="amplifier-type"
    )
    output_power_mon: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Monitored aggregate signal output power.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="output-power-mon",
    )
    output_power_mon_with_ase: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Monitored aggregate total output power including both signal and ASE.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="output-power-mon-with-ase",
    )
    input_power_mon: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Monitored aggregate input power.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="input-power-mon",
    )
    output_voa_attenuation: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="For control-mode = 'manual': target VOA attenuation at output of the amplifier (line padding VOA).",
        ge=0,
        le=30,
        default=0,
        alias="output-voa-attenuation",
    )
    voa_control_mode: VoaControlModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of voa-control-mode.",
        default=VoaControlModeEnum.CONSTANT_POWER,
        alias="voa-control-mode",
    )
    output_voa_actual: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual VOA output.",
        default="not-applicable",
        alias="output-voa-actual",
    )
    power_before_output_voa: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Measured optical power before output VOA.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="power-before-output-voa",
    )
    interstage_support: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="'true' if interstage port is supported in this amplifier.",
        default=False,
        alias="interstage-support",
    )
    interstage_loss: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Amplifier interstage loss.\n   Only of relevance when amplifier has an interstage port.",
        default=0,
        alias="interstage-loss",
    )
    tilt_control_mode: TiltControlModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Specify the tilt control mode. Defines whether amplifier tilt is automatically set by system or configured manually by the user",
        default=TiltControlModeEnum.AUTO,
        alias="tilt-control-mode",
    )
    tilt_target: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="For manual control mode: target tilt, to be configured on the amplifier.\n\nCondition (when): ../tilt-control-mode = 'manual'",
        ge=-5,
        le=5,
        default=0,
        alias="tilt-target",
    )
    tilt_adjustment: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Used to offset the target tilt when tilt-control-mode = 'auto' / 'auto-planned'\n\nCondition (when): ../tilt-control-mode != 'manual'",
        ge=-5,
        le=5,
        default=0,
        alias="tilt-adjustment",
    )
    tilt_actual: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Actual setting of tilt on the amplifier.\nSpectrum Tilt (measured by the EDFA): 0 means both no tilt, or amplifier not available.",
        default=0,
        alias="tilt-actual",
    )
    raman_signal_gain: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Raman Gain of C-Band (signal)\n- if there is a fiber-connection from/to Raman, the API raman-signal-gain at amplifier needs to be appropriately configured autonomously;\n- if there is no fiber-connection from/to Raman, user reads out the amplifier-raman.raman-signal-gain and should configure it on the amplifier.",
        default=None,
        alias="raman-signal-gain",
    )
    raman_osc_gain: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Raman Gain OSC (see raman-signal-gain).",
        default=None,
        alias="raman-osc-gain",
    )
    olos_shutdown_soak_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="On input OLOS, system will soak for the specified time (in msecs) and if the fault still persists, it will go on to do the consequent action (shutdown).",
        ge=0,
        le=2000,
        default=0,
        alias="olos-shutdown-soak-timer",
    )
    supported_gain_range: RestconfList[SupportedGainRangeItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported gain range(s), min. and max. gain",
        default=None,
        alias="supported-gain-range",
    )
    olos_shutdown_disable: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="If it is set to be true, on input OLOS, it will not do the consequent action (shutdown).",
        default=False,
        alias="olos-shutdown-disable",
    )


class ControlModeEnum_1(str, Enum):
    """Enumeration for ControlModeEnum

    Values:
      * auto: Automatic gain control.
      * manual: Manual gain control
      * auto-planned: Auto-planned
    """

    AUTO = "auto"
    MANUAL = "manual"
    AUTO_PLANNED = "auto-planned"


class RamanStateEnum(str, Enum):
    """Enumeration for RamanStateEnum

    Values:
      * not-specified: Not Applicable/ Not specified.
      * disabled: Disabled local and remote Raman.
      * disabled-from-remote: Disabled locally because of remote Raman disabled.
      * enabled: Local Raman enabled, operating with remote Raman.
    """

    NOT_SPECIFIED = "not-specified"
    DISABLED = "disabled"
    DISABLED_FROM_REMOTE = "disabled-from-remote"
    ENABLED = "enabled"


class AmplifierEnableEnum(str, Enum):
    """Enumeration for AmplifierEnableEnum

    Values:
      * disable-local-and-remote: Fully disable local and remote Raman.
      * disable-local: Local Raman manually disabled.
      * enabled: Enable local and remote Raman to operate.
    """

    DISABLE_LOCAL_AND_REMOTE = "disable-local-and-remote"
    DISABLE_LOCAL = "disable-local"
    ENABLED = "enabled"


class PumpPowerItem(YangBaseModel):
    """Target Pump Power, as configured by the user, for each pump.
    If control-mode = auto, value(s) configured are irrelevant.
    """

    pump_id: int = Field(
        json_schema_extra={"is_config": True},
        description="'pump-id' is an integer identifying the number of the pump.",
        ge=0,
        alias="pump-id",
    )
    target_pump_power: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="Raman Pump Power required.\n\nCondition (when): ../../control-mode = 'manual'",
        default=None,
        alias="target-pump-power",
    )
    configured_pump_power: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="The pump power configured in the hardware.\nValue can be derived automatically, if control-mode is auto, or otherwise via the target-pump-power.",
        default=None,
        alias="configured-pump-power",
    )
    min_target_pump_power: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Minimum target pump power.",
        default=None,
        alias="min-target-pump-power",
    )
    max_target_pump_power: str | float | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum target pump power.",
        default=None,
        alias="max-target-pump-power",
    )
    actual_pump_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual values which are currently measured in each pump.",
        ge=-99.0,
        le=99.0,
        default=-99,
        alias="actual-pump-power",
    )


class AmplifierRamanItem(YangBaseModel):
    """Amplifier Raman container."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Non-configurable name: derived from chass/slot and degree.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_input_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Rx (input) Port that hold this object",
        default=None,
        alias="supporting-input-port",
    )
    supporting_output_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Tx (output) Port that hold this object",
        default=None,
        alias="supporting-output-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    function: FunctionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Which NE function the ne-function object works as.",
        default=None,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    control_mode: ControlModeEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="Control Mode for this Raman Amplifier.",
        default=ControlModeEnum_1.AUTO,
        alias="control-mode",
    )
    raman_state: RamanStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The state of the Raman Pump.",
        default=RamanStateEnum.DISABLED,
        alias="raman-state",
    )
    amplifier_enable: AmplifierEnableEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable switch for this Raman.\nUser configuration of Local Raman, and optionally control remote Raman card.",
        default=AmplifierEnableEnum.DISABLE_LOCAL_AND_REMOTE,
        alias="amplifier-enable",
    )
    connected_amplifier: str | int | None = Field(
        json_schema_extra={"is_config": False},
        description="SYSTEM reports the degree that corresponds to the amplifier where Raman is fiber connected to.\nIf Raman is not fiber connected, then SYSTEM returns 'not-specified'.",
        default="not-specified",
        alias="connected-amplifier",
    )
    connected_amp_edfa_optimum_gain: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Connected EDFA Optimum Gain; 0 means no known optimum gain, in case of disaggregated Raman.",
        ge=0.0,
        le=55.0,
        default=0,
        alias="connected-amp-edfa-optimum-gain",
    )
    total_pump_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Operating Total Pump Power.",
        ge=-99.0,
        le=99.0,
        default=None,
        alias="total-pump-power",
    )
    number_of_pumps: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of pumps for the required-equipped card.",
        ge=0,
        default=None,
        alias="number-of-pumps",
    )
    target_raman_gain: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Target Raman Gain, configurable in case control-mode = manual.\nIn case control-mode = auto, this is then ignored.",
        default=None,
        alias="target-raman-gain",
    )
    actual_raman_signal_gain: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="PCL output to express the gain for the raman signal",
        default=None,
        alias="actual-raman-signal-gain",
    )
    actual_raman_osc_gain: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="PCL output to express the gain for the raman OSC",
        default=None,
        alias="actual-raman-osc-gain",
    )
    pump_power: RestconfList[PumpPowerItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Target Pump Power, as configured by the user, for each pump.\nIf control-mode = auto, value(s) configured are irrelevant.",
        default=None,
        alias="pump-power",
    )


class AmplifierModeEnum_1(str, Enum):
    """Enumeration for AmplifierModeEnum

    Values:
      * constant-power: Constant Power
    """

    CONSTANT_POWER = "constant-power"


class AmplifierTofItem(YangBaseModel):
    """Amplifier/Tunable Optical Filter container."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Non-configurable name: derived from chass/slot and degree.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_input_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Rx (input) Port that hold this object",
        default=None,
        alias="supporting-input-port",
    )
    supporting_output_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Tx (output) Port that hold this object",
        default=None,
        alias="supporting-output-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    function: FunctionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Which NE function the ne-function object works as.",
        default=None,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    frequency: str | int | None = Field(
        json_schema_extra={"is_config": True}, description="The laser frequency for amplifier-tof.", default=None
    )
    amplifier_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable switch for this amplifier-tof.",
        default=EnableSwitchEnum.DISABLED,
        alias="amplifier-enable",
    )
    amplifier_mode: AmplifierModeEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="The operating mode of the amplifier-tof.",
        default=AmplifierModeEnum_1.CONSTANT_POWER,
        alias="amplifier-mode",
    )


class ConnectionPortsItem(YangBaseModel):
    """Port associated with degree: One if bi-directional; two if uni-directional.
    Min. and max. elements in the list is 1 in R6.0
    """

    index: int = Field(
        json_schema_extra={"is_config": False},
        description="Always 1 in GX (since dwdm-line ports are bi-directional).",
        ge=1,
        le=2,
    )
    port_name: str = Field(
        json_schema_extra={"is_config": False},
        description="The dwdm-line port of RDxx or ILAx card.\nAs a consequence, OMS of the corresponding dwdm-port is created.",
        alias="port-name",
    )


class ModulesDegreeItem(YangBaseModel):
    """List of cards/ subcards/ modules involved in degree: modules listed here must be listed as 'possibleDegrees'."""

    index: int = Field(
        json_schema_extra={"is_config": True},
        description="Card with index 1 should be the card/ subcard/ module with DWDM line interface.\nCard with index 2 is only applicable to BAXOFP2, when card-mode = 'degree'.\nIndex 2 cannot be used for PAx nor RD cards.",
        ge=1,
        le=2,
    )
    supported_card: str = Field(
        json_schema_extra={"is_config": True},
        description="Instance of card or subcard that belongs to degree.",
        alias="supported-card",
    )


class DegreeItem(YangBaseModel):
    """List of NE Degrees."""

    degree_number: int = Field(
        json_schema_extra={"is_config": True},
        description="Degree number should be greater than zero and not greater than max-degrees.",
        ge=1,
        le=64,
        alias="degree-number",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    is_foadm: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="True if there is no WSS component at the Degree and PAx assigned to the degree appropriately.",
        default=False,
        alias="is-foadm",
    )
    wss_less: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="True if there is no WSS component in the Degree.",
        default=True,
        alias="wss-less",
    )
    slot_width_granularity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Width of a slot (measured in GHz).\n\nCondition (when): ../wss-less = 'false'",
        ge=0,
        default=6250,
        alias="slot-width-granularity",
    )
    center_freq_granularity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Granularity of allowed center frequencies.\nThe base frequency for this computation is 193.1 THz (G.694.1).\n\nCondition (when): ../wss-less = 'false'",
        ge=0,
        default=3125,
        alias="center-freq-granularity",
    )
    min_slots: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Minimum number of slots permitted to be joined together to form a media channel.\nMust be less than or equal to the max-slots.\n\nCondition (when): ../wss-less = 'false'",
        ge=0,
        default=8,
        alias="min-slots",
    )
    max_slots: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum number of slots permitted to be joined together to form a media channel.\nMust be greater than or equal to the min-slots.\n\nCondition (when): ../wss-less = 'false'",
        ge=0,
        default=32,
        alias="max-slots",
    )
    bands_supported: RestconfList[TransmissionBandEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of bands supported by a degree, with dependence on supported cards.",
        default=None,
        alias="bands-supported",
    )
    connection_ports: RestconfList[ConnectionPortsItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Port associated with degree: One if bi-directional; two if uni-directional.\nMin. and max. elements in the list is 1 in R6.0",
        default=None,
        alias="connection-ports",
    )
    modules_degree: RestconfList[ModulesDegreeItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of cards/ subcards/ modules involved in degree: modules listed here must be listed as 'possibleDegrees'.",
        default=None,
        alias="modules-degree",
    )


class DirectionItem(YangBaseModel):
    """List of NE direction(s)."""

    index: int = Field(json_schema_extra={"is_config": True}, description="Direction index.", ge=1, le=16)
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    direction_number: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Direction is 1 or 2 depending on port.",
        ge=1,
        le=2,
        default=1,
        alias="direction-number",
    )
    direction_card: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Card Instance that belongs to this direction (index).",
        default=None,
        alias="direction-card",
    )
    direction_port: str = Field(
        json_schema_extra={"is_config": True},
        description="Instance of the card's port hosting this direction (index).",
        alias="direction-port",
    )


class WavelengthDuplicationEnum(str, Enum):
    """Enumeration for WavelengthDuplicationEnum

    Values:
      * one-per-adg: No duplication of frequencies in the ADG
      * one-per-degree: CDC: duplication of frequencies allowed in the ADG, but only one at the Degree
    """

    ONE_PER_ADG = "one-per-adg"
    ONE_PER_DEGREE = "one-per-degree"


class ModulesAdgItem(YangBaseModel):
    """List of cards/ subcards/ modules involved in ADG, for informational purposes."""

    index: int = Field(
        json_schema_extra={"is_config": True},
        description="Card with index 1 should be the card/ subcard/ module fibered to the Degree(s).",
        ge=1,
        le=16,
    )
    supported_card: str = Field(
        json_schema_extra={"is_config": True}, description="Instance of the card for the ADG.", alias="supported-card"
    )
    ocm_monitoring: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="'true' if monitoring is provided by the Degree, or CD-AD structure; 'false' otherwise.",
        default=True,
        alias="ocm-monitoring",
    )


class AdgItem(YangBaseModel):
    """List of ADGs - Add/ Drop Group(s)"""

    adg_number: int = Field(
        json_schema_extra={"is_config": True},
        description="ADG identifier as a number.",
        ge=1,
        le=110,
        alias="adg-number",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    max_add_drop_ports: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The max number of ports available for a given ADG.",
        ge=0,
        default=None,
        alias="max-add-drop-ports",
    )
    wavelength_duplication: WavelengthDuplicationEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether the SRG can handle duplicate wavelengths and if so to what extent.",
        default=None,
        alias="wavelength-duplication",
    )
    bands_supported: RestconfList[TransmissionBandEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of bands supported by an ADG, with dependence on supported cards.",
        default=None,
        alias="bands-supported",
    )
    modules_adg: RestconfList[ModulesAdgItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of cards/ subcards/ modules involved in ADG, for informational purposes.",
        default=None,
        alias="modules-adg",
    )


class AseIdlerStateEnum(str, Enum):
    """Enumeration for AseIdlerStateEnum

    Values:
      * ase-enabled: ASE Idler filling is enabled and complete.
      * ase-partially-enabled: ASE Idler filling is not complete but partially done.
      * ase-faulted: ASE Idler source is faulted or degraded.
      * ase-disabled: ASE Idler filling not started or disabled.
    """

    ASE_ENABLED = "ase-enabled"
    ASE_PARTIALLY_ENABLED = "ase-partially-enabled"
    ASE_FAULTED = "ase-faulted"
    ASE_DISABLED = "ase-disabled"


class AseIdlerServiceItem(YangBaseModel):
    """ASE Idler specific attributes."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Name of ase-idler-service.", min_length=1, max_length=64
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds thiS.",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    function: FunctionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Which NE function the ne-function object works as.",
        default=None,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    ase_idler_state: AseIdlerStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="ASE Idler state.",
        default=AseIdlerStateEnum.ASE_DISABLED,
        alias="ase-idler-state",
    )
    ase_idler_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="ASE Idler enabled: system will autofill the\nempty part of the spectrum and failed channels with ASE Idler signal.",
        default=EnableSwitchEnum.DISABLED,
        alias="ase-idler-enable",
    )


class AseIdlerSourceItem(YangBaseModel):
    """Amplifier ASE container."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Non-configurable name: derived from chass/slot and degree.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_input_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Rx (input) Port that hold this object",
        default=None,
        alias="supporting-input-port",
    )
    supporting_output_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Tx (output) Port that hold this object",
        default=None,
        alias="supporting-output-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    function: FunctionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Which NE function the ne-function object works as.",
        default=None,
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    pump_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="ASE Idler source enabling.",
        default=EnableSwitchEnum.DISABLED,
        alias="pump-enable",
    )
    pump_state: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The state of the ASE Idler pump.",
        default=EnableSwitchEnum.DISABLED,
        alias="pump-state",
    )
    target_output_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="ASE pump output power required (if manually configured).",
        ge=-55.0,
        le=55.0,
        default=13,
        alias="target-output-power",
    )


class OtdrStateEnum(str, Enum):
    """Enumeration for OtdrStateEnum

    Values:
      * not-available: Status is not available.
      * idle: Idle status.
      * measuring: Measurement is ongoing.
      * finished: Measurement has completed.
      * fail: Measurement has failed.
    """

    NOT_AVAILABLE = "not-available"
    IDLE = "idle"
    MEASURING = "measuring"
    FINISHED = "finished"
    FAIL = "fail"


class OtdrLaserStateEnum(str, Enum):
    """Enumeration for OtdrLaserStateEnum

    Values:
      * not-available: Status is not available.
      * enabled: Indicates laser of OTDR is on.
      * disabled: Indicates if laser of OTDR is off.
    """

    NOT_AVAILABLE = "not-available"
    ENABLED = "enabled"
    DISABLED = "disabled"


class OtdrItem(YangBaseModel):
    """Otdr-eqpt container containing attrbutes suppoting OTDR eqpt per card."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Non-configurable name: derived from chass/slot and degree.",
        min_length=1,
        max_length=64,
    )
    supporting_card: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": False},
            description="Card that holds this",
            min_length=1,
            max_length=64,
            default=None,
            alias="supporting-card",
        )
    )
    supporting_input_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Rx (input) Port that hold this object",
        default=None,
        alias="supporting-input-port",
    )
    supporting_output_port: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Tx (output) Port that hold this object",
        default=None,
        alias="supporting-output-port",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    admin_state: AdminStateEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrative state of the managed object.",
        default=AdminStateEnum.UNLOCK,
        alias="admin-state",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    otdr_state: OtdrStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicating the current status of the OTDR.This status change shall trigger change notification.",
        default=OtdrStateEnum.NOT_AVAILABLE,
        alias="otdr-state",
    )
    otdr_measurement_time: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicating the time remaining in current measurement running.",
        ge=0,
        default=0,
        alias="otdr-measurement-time",
    )
    otdr_error: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Error message produced when the measurement ends with error.",
        min_length=0,
        max_length=64,
        default=None,
        alias="otdr-error",
    )
    otdr_laser_state: OtdrLaserStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicating the current status of the OTDR laser.",
        default=OtdrLaserStateEnum.NOT_AVAILABLE,
        alias="otdr-laser-state",
    )
    otdr_measurement_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="0 indicates that the card is not measuring any port and non-zero indicates the OTDR port number where a measurement is currently taking place.",
        min_length=0,
        max_length=64,
        default="0",
        alias="otdr-measurement-port",
    )


class NeFunction(YangBaseModel):
    """NE generic functions"""

    amplifier: RestconfList[AmplifierItem] | None = Field(
        json_schema_extra={"is_config": True}, description="Amplifier container.", default=None
    )
    amplifier_raman: RestconfList[AmplifierRamanItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Amplifier Raman container.",
        default=None,
        alias="amplifier-raman",
    )
    amplifier_tof: RestconfList[AmplifierTofItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Amplifier/Tunable Optical Filter container.",
        default=None,
        alias="amplifier-tof",
    )
    degree: RestconfList[DegreeItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of NE Degrees.\n\nCondition (when): /ne/node-type='OADM'",
        default=None,
    )
    direction: RestconfList[DirectionItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of NE direction(s).\n\nCondition (when): /ne/node-type='ILA'",
        default=None,
    )
    adg: RestconfList[AdgItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of ADGs - Add/ Drop Group(s)\n\nCondition (when): /ne/node-type='OADM'",
        default=None,
    )
    ase_idler_service: RestconfList[AseIdlerServiceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="ASE Idler specific attributes.",
        default=None,
        alias="ase-idler-service",
    )
    ase_idler_source: RestconfList[AseIdlerSourceItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Amplifier ASE container.",
        default=None,
        alias="ase-idler-source",
    )
    otdr: RestconfList[OtdrItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Otdr-eqpt container containing attrbutes suppoting OTDR eqpt per card.",
        default=None,
    )


class AddressFamilyEnum_1(str, Enum):
    """Enumeration for AddressFamilyEnum

    Values:
      * ipV4: IP version 4
      * ipV6: IP version 6
      * nsap: NSAP
      * hdlc: HDLC (8-bit multidrop)
      * bbn1822: BBN 1822
      * all802: 802 (includes all 802 media plus Ethernet 'canonical format')
      * e163: E.163
      * e164: E.164 (SMDS, FrameRelay, ATM)
      * f69: F.69 (Telex)
      * x121: X.121 (X.25, Frame Relay)
      * ipx: IPX (Internetwork Packet Exchange)
      * appletalk: Appletalk
      * decnetIV: DECnet IV
      * banyanVines: Banyan Vines
      * e164withNsap: E.164 with NSAP format subaddress
      * dns: DNS (Domain Name System)
      * distinguishedName: Distinguished Name (per X.500)
      * asNumber: Autonomous System Number
      * xtpOverIpv4: XTP over IP version 4
      * xtpOverIpv6: XTP over IP version 6
      * xtpNativeModeXTP: XTP native mode XTP
      * fibreChannelWWPN: Fibre Channel World-Wide Port Name
      * fibreChannelWWNN: Fibre Channel World-Wide Node Name
      * gwid: Gateway Identifier
      * l2vpn: AFI for L2VPN information
      * mplsTpSectionEndpointIdentifier: MPLS-TP Section Endpoint Identifier
      * mplsTpLspEndpointIdentifier: MPLS-TP LSP Endpoint Identifier
      * mplsTpPseudowireEndpointIdentifier: MPLS-TP Pseudowire Endpoint Identifier
      * eigrpCommonServiceFamily: EIGRP Common Service Family
      * eigrpIpv4ServiceFamily: EIGRP IPv4 Service Family
      * eigrpIpv6ServiceFamily: EIGRP IPv6 Service Family
      * lispCanonicalAddressFormat: LISP Canonical Address Format (LCAF)
      * bgpLs: BGP-LS
      * 48BitMac: 48-bit MAC
      * 64BitMac: 64-bit MAC
    """

    IPV4 = "ipV4"
    IPV6 = "ipV6"
    NSAP = "nsap"
    HDLC = "hdlc"
    BBN1822 = "bbn1822"
    ALL802 = "all802"
    E163 = "e163"
    E164 = "e164"
    F69 = "f69"
    X121 = "x121"
    IPX = "ipx"
    APPLETALK = "appletalk"
    DECNETIV = "decnetIV"
    BANYANVINES = "banyanVines"
    E164WITHNSAP = "e164withNsap"
    DNS = "dns"
    DISTINGUISHEDNAME = "distinguishedName"
    ASNUMBER = "asNumber"
    XTPOVERIPV4 = "xtpOverIpv4"
    XTPOVERIPV6 = "xtpOverIpv6"
    XTPNATIVEMODEXTP = "xtpNativeModeXTP"
    FIBRECHANNELWWPN = "fibreChannelWWPN"
    FIBRECHANNELWWNN = "fibreChannelWWNN"
    GWID = "gwid"
    L2VPN = "l2vpn"
    MPLSTPSECTIONENDPOINTIDENTIFIER = "mplsTpSectionEndpointIdentifier"
    MPLSTPLSPENDPOINTIDENTIFIER = "mplsTpLspEndpointIdentifier"
    MPLSTPPSEUDOWIREENDPOINTIDENTIFIER = "mplsTpPseudowireEndpointIdentifier"
    EIGRPCOMMONSERVICEFAMILY = "eigrpCommonServiceFamily"
    EIGRPIPV4SERVICEFAMILY = "eigrpIpv4ServiceFamily"
    EIGRPIPV6SERVICEFAMILY = "eigrpIpv6ServiceFamily"
    LISPCANONICALADDRESSFORMAT = "lispCanonicalAddressFormat"
    BGPLS = "bgpLs"
    _48BITMAC = "48BitMac"
    _64BITMAC = "64BitMac"


class IfSubtypeEnum(str, Enum):
    """Enumeration for IfSubtypeEnum

    Values:
      * unknown: Interface is not known
      * if-index: Interface identifier based on the ifIndex MIB object.
      * system-port-number: Interface identifier based on the system port numbering convetion.
    """

    UNKNOWN = "unknown"
    IF_INDEX = "if-index"
    SYSTEM_PORT_NUMBER = "system-port-number"


class ManagementAddressLocalItem(YangBaseModel):
    """Management address information about a particular chassis
    component.  There may be multiple management addresses
    configured on the remote system identified by a particular
    index whose information is received on the local system.
    Each management address should have distinct 'management address
    type' (subtype) and 'management address' (address).
    """

    address_subtype: AddressFamilyEnum_1 = Field(
        json_schema_extra={"is_config": False},
        description="The type of management address identifier encoding used in the associated 'address' attribute.",
        alias="address-subtype",
    )
    address: str = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the management address component associated with the remote system.  The purpose\nof this address is to contact the management entity.",
        min_length=0,
        max_length=64,
    )
    if_subtype: IfSubtypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the basis of a particular type of\ninterface associated with the management address.",
        default=None,
        alias="if-subtype",
    )
    if_id: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The integer value used to identify the interface number regarding the management address component associated with\nthe remote system.",
        ge=0,
        default=None,
        alias="if-id",
    )
    address_oid: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The Object Identifier (OID) value used to identify the type of hardware component or protocol entity associated with the\nmanagement address advertised by the remote system agent.",
        min_length=0,
        max_length=128,
        default=None,
        alias="address-oid",
    )


class ChassisIdSubtypeEnum(str, Enum):
    """Enumeration for ChassisIdSubtypeEnum

    Values:
      * reserved: Represents another subtype, not covered by the other options. When reserved subtype is used, the chassis-id is displayed as a hex string.
      * chassis-component: Represents a chassis identifier based on the value of entPhysicalAlias object (defined in IETF RFC 2737) for a chassis component (i.e., an entPhysicalClass value of 'chassis(3)')
      * interface-alias: Represents a chassis identifier based on the value of ifAlias object (defined in IETF RFC 2863) for an interface on the containing chassis.
      * port-component: Represents a chassis identifier based on the value of entPhysicalAlias object (defined in IETF RFC 2737) for a port or backplane component (i.e., entPhysicalClass value of 'port(10)' or 'backplane(4)'), within the containing chassis.
      * mac-address: Represents a chassis identifier based on the value of a unicast source address (encoded in network byte order and IEEE 802.3 canonical bit order), of a port on the containing chassis as defined in IEEE Std 802-2001.
      * network-address: Represents a chassis identifier based on a network address, associated with a particular chassis.  The encoded address is actually composed of two fields. The first field is a single octet, representing the IANA AddressFamilyNumbers value for the specific address type, and the second field is the network address value.
      * interface-name: Represents a chassis identifier based on the value of ifName object (defined in IETF RFC 2863) for an interface on the containing chassis.
      * local: Represents a chassis identifier based on a locally defined value.
    """

    RESERVED = "reserved"
    CHASSIS_COMPONENT = "chassis-component"
    INTERFACE_ALIAS = "interface-alias"
    PORT_COMPONENT = "port-component"
    MAC_ADDRESS = "mac-address"
    NETWORK_ADDRESS = "network-address"
    INTERFACE_NAME = "interface-name"
    LOCAL = "local"


class PortIdSubtypeEnum(str, Enum):
    """Enumeration for PortIdSubtypeEnum

    Values:
      * reserved: Represents another subtype, not covered by the other options. When reserved subtype is used, the port-id is displayed as a hex string.
      * interface-alias: Means that the port-id string identifies a particular instance of the ifAlias object (defined in IETF RFC 2863).  If the particular ifAlias object does not contain any values, another port identifier type should be used.
      * port-component: Means that the port-id string identifies a particular instance of the entPhysicalAlias object (defined in IETF RFC 2737) for a port or backplane component.
      * mac-address: Means that the port-id string identifies a particular unicast source address (encoded in network byte order and IEEE 802.3 canonical bit order) associated with the port (IEEE Std 802-2001).
      * network-address: Means that the port-id string identifies a network address associated with the port. The first octet contains the IANA AddressFamilyNumbers enumeration value for the specific address type, and octets 2 through N contain the networkAddress address value in network byte order.
      * interface-name: Means that the port-id string identifies a  particular instance of the ifName object (defined in IETF RFC 2863). If the particular ifName object does not contain any values, another port identifier type should be used.
      * agent-circuit-id: Means that the port-id string identifies an agent-local identifier of the circuit (defined in RFC 3046).
      * local: Means that the port-id string identifies a locally assigned port ID
    """

    RESERVED = "reserved"
    INTERFACE_ALIAS = "interface-alias"
    PORT_COMPONENT = "port-component"
    MAC_ADDRESS = "mac-address"
    NETWORK_ADDRESS = "network-address"
    INTERFACE_NAME = "interface-name"
    AGENT_CIRCUIT_ID = "agent-circuit-id"
    LOCAL = "local"


class LldpLocalInfoItem(YangBaseModel):
    """LLDP local system information sent on lldp-port."""

    lldp_port: str = Field(
        json_schema_extra={"is_config": False}, description="Local port on which lldp is enabled.", alias="lldp-port"
    )
    management_address_local: RestconfList[ManagementAddressLocalItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Management address information about a particular chassis\ncomponent.  There may be multiple management addresses\nconfigured on the remote system identified by a particular\nindex whose information is received on the local system.\nEach management address should have distinct 'management address\ntype' (subtype) and 'management address' (address).",
        default=None,
        alias="management-address-local",
    )
    chassis_id_subtype: ChassisIdSubtypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the format of the chassis-id string.",
        default=None,
        alias="chassis-id-subtype",
    )
    chassis_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute identifies the chassis component withing the LLDP remote system..\nThis value needs to be interpreted according with the associated chassis-id-subtype, which identifies\nthe format of this value.",
        min_length=0,
        max_length=255,
        default=None,
        alias="chassis-id",
    )
    port_id_subtype: PortIdSubtypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the format of the port-id string.",
        default=None,
        alias="port-id-subtype",
    )
    port_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute identifies the port within the LLDP remote system chassis.\nThis value needs to be interpreted according with the associated port-id-subtype, which identifies\nthe format of this value.",
        min_length=0,
        max_length=255,
        default=None,
        alias="port-id",
    )
    port_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the description of the given port associated with the remote system.",
        min_length=0,
        max_length=255,
        default=None,
        alias="port-description",
    )
    system_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the system name of the remote system.",
        min_length=0,
        max_length=255,
        default=None,
        alias="system-name",
    )
    system_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the system description of the remote system.",
        min_length=0,
        max_length=255,
        default=None,
        alias="system-description",
    )
    supported_capabilities: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the remote system supported capabilities.",
        default=None,
        alias="supported-capabilities",
    )
    enabled_capabilities: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the remote system enabled capabilities.",
        default=None,
        alias="enabled-capabilities",
    )


class ManagementAddressItem(YangBaseModel):
    """Management address information about a particular chassis
    component.  There may be multiple management addresses
    configured on the remote system identified by a particular
    index whose information is received on the local system.
    Each management address should have distinct 'management address
    type' (subtype) and 'management address' (address).
    """

    address_subtype: AddressFamilyEnum_1 = Field(
        json_schema_extra={"is_config": False},
        description="The type of management address identifier encoding used in the associated 'address' attribute.",
        alias="address-subtype",
    )
    address: str = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the management address component associated with the remote system.  The purpose\nof this address is to contact the management entity.",
        min_length=0,
        max_length=64,
    )
    if_subtype: IfSubtypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the basis of a particular type of\ninterface associated with the management address.",
        default=None,
        alias="if-subtype",
    )
    if_id: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The integer value used to identify the interface number regarding the management address component associated with\nthe remote system.",
        ge=0,
        default=None,
        alias="if-id",
    )
    address_oid: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The Object Identifier (OID) value used to identify the type of hardware component or protocol entity associated with the\nmanagement address advertised by the remote system agent.",
        min_length=0,
        max_length=128,
        default=None,
        alias="address-oid",
    )


class CustomTlvItem(YangBaseModel):
    """List of Organizational Specific TLVs (Type-Lengh-Value) parameters."""

    oui: str = Field(
        json_schema_extra={"is_config": False},
        description="The Organization Unique Identifier (OUI) of this TLV. Hexadecimal representation of the 24 bit identier.",
        min_length=0,
        max_length=6,
    )
    subtype: int = Field(
        json_schema_extra={"is_config": False},
        description="The sub-type identifier of the TLV in the scope of the OUI.",
        ge=0,
    )
    value: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The value of the TLV.",
        min_length=0,
        max_length=507,
        default=None,
    )


class LldpNeighborItem(YangBaseModel):
    """LLDP remote system discovered by lldp-port.
    This information is kept indefinitely, until the port is decomissioned, or the
    data is manually cleared by user.
    """

    lldp_port: str = Field(
        json_schema_extra={"is_config": False},
        description="Local port that is connected to this LLDP neighbor.",
        alias="lldp-port",
    )
    direction: DirectionEnum_2 = Field(
        json_schema_extra={"is_config": False}, description="Direction in which the neighbor was detected."
    )
    ttl: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Remote system info Time-To-Live (TTL); the number of seconds until information expires.\nIf the remote system deosn't provide a ttl value, this parameter is set to the global hold-on-timer.",
        ge=0,
        default=None,
    )
    last_update: (
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
        description="Timestamp with the last time this neighbor info was updated.",
        default=None,
        alias="last-update",
    )
    age: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of seconds since discovery.",
        ge=0,
        le=18446744073709551615,
        default=None,
    )
    chassis_id_subtype: ChassisIdSubtypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the format of the chassis-id string.",
        default=None,
        alias="chassis-id-subtype",
    )
    chassis_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute identifies the chassis component withing the LLDP remote system..\nThis value needs to be interpreted according with the associated chassis-id-subtype, which identifies\nthe format of this value.",
        min_length=0,
        max_length=255,
        default=None,
        alias="chassis-id",
    )
    port_id_subtype: PortIdSubtypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the format of the port-id string.",
        default=None,
        alias="port-id-subtype",
    )
    port_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute identifies the port within the LLDP remote system chassis.\nThis value needs to be interpreted according with the associated port-id-subtype, which identifies\nthe format of this value.",
        min_length=0,
        max_length=255,
        default=None,
        alias="port-id",
    )
    port_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the description of the given port associated with the remote system.",
        min_length=0,
        max_length=255,
        default=None,
        alias="port-description",
    )
    system_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the system name of the remote system.",
        min_length=0,
        max_length=255,
        default=None,
        alias="system-name",
    )
    system_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The string value used to identify the system description of the remote system.",
        min_length=0,
        max_length=255,
        default=None,
        alias="system-description",
    )
    supported_capabilities: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the remote system supported capabilities.",
        default=None,
        alias="supported-capabilities",
    )
    enabled_capabilities: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This attribute describes the remote system enabled capabilities.",
        default=None,
        alias="enabled-capabilities",
    )
    management_address: RestconfList[ManagementAddressItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Management address information about a particular chassis\ncomponent.  There may be multiple management addresses\nconfigured on the remote system identified by a particular\nindex whose information is received on the local system.\nEach management address should have distinct 'management address\ntype' (subtype) and 'management address' (address).",
        default=None,
        alias="management-address",
    )
    custom_tlv: RestconfList[CustomTlvItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of Organizational Specific TLVs (Type-Lengh-Value) parameters.",
        default=None,
        alias="custom-tlv",
    )


class LldpPortStatisticsItem(YangBaseModel):
    """LLDP frame reception statistics for a particular port and direction.

    All counter values in a particular entry shall be maintained on a continuing basis and shall not be deleted
    upon expiration of TTL timing counters associated with the LLDP neighbor information.

    All statistical counters associated with a particular port on the local LLDP agent become frozen whenever the
    lldp-admin-status is disabled for the same port.
    """

    lldp_port: str = Field(
        json_schema_extra={"is_config": False},
        description="Local port that is associated with the LLDP agent.",
        alias="lldp-port",
    )
    direction: DirectionEnum_2 = Field(
        json_schema_extra={"is_config": False}, description="Direction associated with lldp statistics."
    )
    last_change_time: (
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
        description="The timestamp associated with the last time this port received LLDP updates.",
        default="0000-01-01T00:00:00Z",
        alias="last-change-time",
    )
    last_clear_time: (
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
        description="The timestamp associated with the last time this port was cleared.",
        default="0000-01-01T00:00:00Z",
        alias="last-clear-time",
    )
    total_ageouts: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="A count of the times that a neighbor’s information\nis deleted from the lldp-neighbor list due to TTL timer\nexpiration.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="total-ageouts",
    )
    total_discarded_frames: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="A count of all LLDPDUs received and then discarded.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="total-discarded-frames",
    )
    error_frames: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="A count of all LLDPDUs received at the port with one or more\ndetectable errors.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="error-frames",
    )
    total_frames_in: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="A count of all LLDP frames received at the port.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="total-frames-in",
    )
    total_frames_out: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="A count of all LLDP frames transmitted through the port.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="total-frames-out",
    )
    total_discarded_tlvs: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="A count of all TLVs received at the port and discarded for any\nreason.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="total-discarded-tlvs",
    )
    total_unrecognized_tlvs: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="This counter provides a count of all TLVs not recognized by\nthe receiving LLDP local agent.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="total-unrecognized-tlvs",
    )


class Lldp(YangBaseModel):
    """Global LLDP configuration."""

    hold_on_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Time to keep neighbor information, in case neighbor does not have an explicit Time-To-Live (TTL) TLV.",
        ge=0,
        default=900,
        alias="hold-on-timer",
    )
    lldp_local_info: RestconfList[LldpLocalInfoItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="LLDP local system information sent on lldp-port.",
        default=None,
        alias="lldp-local-info",
    )
    lldp_neighbor: RestconfList[LldpNeighborItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="LLDP remote system discovered by lldp-port.\nThis information is kept indefinitely, until the port is decomissioned, or the\ndata is manually cleared by user.",
        default=None,
        alias="lldp-neighbor",
    )
    lldp_port_statistics: RestconfList[LldpPortStatisticsItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="LLDP frame reception statistics for a particular port and direction.\n\nAll counter values in a particular entry shall be maintained on a continuing basis and shall not be deleted\nupon expiration of TTL timing counters associated with the LLDP neighbor information.\n\nAll statistical counters associated with a particular port on the local LLDP agent become frozen whenever the\nlldp-admin-status is disabled for the same port.",
        default=None,
        alias="lldp-port-statistics",
    )


class CarrierNeighborItem(YangBaseModel):
    """Neighbor node discovered by the local-carrier via ICDP.
    This information is kept indefinitely, until the carrier is deleted, or the
    data is manually cleared by user.
    """

    local_carrier: str = Field(
        json_schema_extra={"is_config": False},
        description="Local carrier instance that has discovered this neighbor node.\nEach carrier can discover up to one node.\nIt is possible for multiple collocated carriers to discover the same\nnode multiple times (each time connected to a different remote carrier).",
        alias="local-carrier",
    )
    last_update: (
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
        description="Timestamp with the last time this neighbor info was updated.",
        default=None,
        alias="last-update",
    )
    age: Uint64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of seconds since discovery.",
        ge=0,
        le=18446744073709551615,
        default=None,
    )
    local_carrier_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="AID of local carrier.",
        min_length=1,
        max_length=32,
        default=None,
        alias="local-carrier-id",
    )
    ne_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Id of the remote network element.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-id",
    )
    ne_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Neighbor ne-name.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-name",
    )
    ne_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of the remote network element.",
        min_length=0,
        max_length=64,
        default=None,
        alias="ne-type",
    )
    remote_carrier_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="AID of the remote carrier connected to the local carrier.\nImplies a specific remote port id.",
        min_length=0,
        max_length=64,
        default=None,
        alias="remote-carrier-id",
    )
    ipv4_loopback_address: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="IPv4 loopback address of the neighbor; may be empty if not configured.",
        default=None,
        alias="ipv4-loopback-address",
    )
    ipv6_loopback_address: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                    v,
                )
            ),
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="IPv6 loopback address of the neighbor; may be empty if not configured.",
        default=None,
        alias="ipv6-loopback-address",
    )


class Icdp(YangBaseModel):
    """Contains ICDP (Intelligent Carrier Discovery Protocol) data.
    This is a proprietary mechanism that allows Network Elements to
    auto-discover their neighbors using carrier OFEC-GCC over L1 line interfaces.
    """

    global_switch: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="Global switch for ICDP.\nIf disabled, inhibits further discovery using ICDP; however, existing data will be kept.",
        default=True,
        alias="global-switch",
    )
    carrier_neighbor: RestconfList[CarrierNeighborItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Neighbor node discovered by the local-carrier via ICDP.\nThis information is kept indefinitely, until the carrier is deleted, or the\ndata is manually cleared by user.",
        default=None,
        alias="carrier-neighbor",
    )


class ConnectionStatusEnum(str, Enum):
    """Enumeration for ConnectionStatusEnum

    Values:
      * connected: Remote NE is connected.
      * not-connected: Remote NE is not connected.
      * mismatch: Mismatch between provisioned Node Name with discovered node name.
      * unknown: Remote NE is unknown.
    """

    CONNECTED = "connected"
    NOT_CONNECTED = "not-connected"
    MISMATCH = "mismatch"
    UNKNOWN = "unknown"


class InciNeighborItem(YangBaseModel):
    """List of provisioned INCI Neighbors."""

    neighbor_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Node-ID of provisioned neighbor.",
        min_length=1,
        max_length=64,
        alias="neighbor-id",
    )
    neighbor_address: str = Field(
        json_schema_extra={"is_config": True},
        description="IP address of the provisioned remote neighbor NE.",
        alias="neighbor-address",
    )
    neighbor_port: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Port number used for communication with GX NE.",
        ge=0,
        default=8800,
        alias="neighbor-port",
    )
    connection_status: ConnectionStatusEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Connection status with this Neighbor.",
        default=ConnectionStatusEnum.NOT_CONNECTED,
        alias="connection-status",
    )
    configured_node_name: str = Field(
        json_schema_extra={"is_config": True},
        description="User provisioned name of remote NE. Used to compare against the discovered-node-name.",
        min_length=0,
        max_length=128,
        alias="configured-node-name",
    )
    discovered_node_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of remote NE as sent by the remote NE.",
        min_length=0,
        max_length=128,
        default=None,
        alias="discovered-node-name",
    )
    discovered_node_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Node ID of remote node as received from remote node.",
        min_length=0,
        max_length=128,
        default=None,
        alias="discovered-node-id",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )


class Inci(YangBaseModel):
    """INCI is Inter-NE Communication Interface, Information related to Inter NE inter-op feature."""

    inci_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This is a NE level switch to control the INCI feature.",
        default=False,
        alias="inci-enabled",
    )
    inci_neighbor: RestconfList[InciNeighborItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of provisioned INCI Neighbors.",
        default=None,
        alias="inci-neighbor",
    )


class CableIdStateEnum(str, Enum):
    """Enumeration for CableIdStateEnum

    Values:
      * idle: cable-id verification is not running.
      * running-incl-switching: cable-id verification is running for both active and protected paths.
      * running-no-switching: cable-id verification is running only for active path.
    """

    IDLE = "idle"
    RUNNING_INCL_SWITCHING = "running-incl-switching"
    RUNNING_NO_SWITCHING = "running-no-switching"


class CableIdStatus(YangBaseModel):
    """Container for cable-id status."""

    cable_id_state: CableIdStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the cable-id state.",
        default=CableIdStateEnum.IDLE,
        alias="cable-id-state",
    )
    test_progress: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the cable-id test progress.",
        min_length=0,
        max_length=255,
        default="Not applicable",
        alias="test-progress",
    )


class CableIdTestResultEnum(str, Enum):
    """Enumeration for CableIdTestResultEnum

    Values:
      * not-verified: cable-id verification is not initiated.
      * pass: cable-id verification passed.
      * fail: cable-id verification failed.
      * suspected: cable-id verification results are suspected.
    """

    NOT_VERIFIED = "not-verified"
    PASS = "pass"
    FAIL = "fail"
    SUSPECTED = "suspected"


class CurrentStateEnum(str, Enum):
    """Enumeration for CurrentStateEnum

    Values:
      * idle: cable-id verification is not running.
      * pending-to-run: cable-id verification is pending to run.
      * running-incl-switching: cable-id verification is running for both active and protected paths.
      * running-no-switching: cable-id verification is running only for active path.
    """

    IDLE = "idle"
    PENDING_TO_RUN = "pending-to-run"
    RUNNING_INCL_SWITCHING = "running-incl-switching"
    RUNNING_NO_SWITCHING = "running-no-switching"


class LastTestQualifierEnum(str, Enum):
    """Enumeration for LastTestQualifierEnum

    Values:
      * up-to-date: Up to date, when cable-id test completed.
      * out-dated: Out dated, when there is any fault on fiber.
    """

    UP_TO_DATE = "up-to-date"
    OUT_DATED = "out-dated"


class SupportingFiberConnection(YangBaseModel):
    """Container for Supported fiber connection path."""

    fiber_connection_list: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported fiber connection path.",
        default=None,
        alias="fiber-connection-list",
    )


class CableIdPathItem(YangBaseModel):
    """Display cable path status."""

    name: str = Field(
        json_schema_extra={"is_config": False}, description="cable-id result name.", min_length=0, max_length=255
    )
    card_type_a: str | None = Field(
        json_schema_extra={"is_config": False}, description="card type of end A", default=None, alias="card-type-a"
    )
    port_a: str | None = Field(
        json_schema_extra={"is_config": False}, description="port instance of end A", default=None, alias="port-a"
    )
    card_type_z: str | None = Field(
        json_schema_extra={"is_config": False}, description="card type of end Z", default=None, alias="card-type-z"
    )
    port_z: str | None = Field(
        json_schema_extra={"is_config": False}, description="port instance of end Z", default=None, alias="port-z"
    )
    port_a_to_port_z_path_status: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the protection path status for endpoints A-Z.",
        default=EnableSwitchEnum.DISABLED,
        alias="port-a-to-port-z-path-status",
    )
    port_z_to_port_a_path_status: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the protection path status for endpoints A-Z.",
        default=EnableSwitchEnum.DISABLED,
        alias="port-z-to-port-a-path-status",
    )
    port_a_to_port_z_last_test_status: CableIdTestResultEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the cable id test results for endpoints A-Z.",
        default=None,
        alias="port-a-to-port-z-last-test-status",
    )
    port_z_to_port_a_last_test_status: CableIdTestResultEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the cable id test results for endpoints A-Z.",
        default=None,
        alias="port-z-to-port-a-last-test-status",
    )
    current_state: CurrentStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display the cable-id state.",
        default=CurrentStateEnum.IDLE,
        alias="current-state",
    )
    last_test_qualifier: LastTestQualifierEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Display last test status.",
        default=LastTestQualifierEnum.UP_TO_DATE,
        alias="last-test-qualifier",
    )
    last_test_timestamp: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Timestamp for the last cable-id verification for the port pair.",
        default=None,
        alias="last-test-timestamp",
    )
    additional_info: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Additional information.",
        min_length=0,
        max_length=1024,
        default=None,
        alias="additional-info",
    )
    supporting_fiber_connection: SupportingFiberConnection | None = Field(
        json_schema_extra={"is_config": False},
        description="Container for Supported fiber connection path.",
        default=None,
        alias="supporting-fiber-connection",
    )


class CableId(YangBaseModel):
    """cable-id container, with cable-id path, progress and the test results.."""

    cable_id_status: CableIdStatus | None = Field(
        json_schema_extra={"is_config": False},
        description="Container for cable-id status.",
        default=None,
        alias="cable-id-status",
    )
    cable_id_path: RestconfList[CableIdPathItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Display cable path status.",
        default=None,
        alias="cable-id-path",
    )


class FiberConnectionItem(YangBaseModel):
    """Fiber Connection list - connecting two ports of L0 cards, or line-port of Transponders/ Muxponders."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="User defined name for the fiber-connection.",
        min_length=1,
        max_length=64,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    src_port: str = Field(json_schema_extra={"is_config": True}, description="Source Port instance.", alias="src-port")
    dst_port: str = Field(
        json_schema_extra={"is_config": True}, description="Destination Port instance.", alias="dst-port"
    )
    fiber_connection_type: DirectionEnum_4 | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of the fiber connection - one-way or two-way.",
        default=DirectionEnum_4.TWO_WAY,
        alias="fiber-connection-type",
    )


class ScopeEnum_1(str, Enum):
    """Enumeration for ScopeEnum

    Values:
      * general-purpose: Indicates the general use of external-fiber-connection to represent connectivity between two ports on the same NE or across NEs
      * cable-id: Indicates that the external-fiber-connection configuration is additionally used by cable-id functionality
    """

    GENERAL_PURPOSE = "general-purpose"
    CABLE_ID = "cable-id"


class ExternalFiberConnectionItem(YangBaseModel):
    """External Fiber Connection name - connecting two ports of L0 cards in different NEs."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="User defined name for the fiber-connection.",
        min_length=1,
        max_length=64,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    scope: ScopeEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="Represents the scope of the external-fiber-connection - general-purpose use or extended for use by cable-id functionality",
        default=ScopeEnum_1.GENERAL_PURPOSE,
    )
    src_node_id: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Should be logically the same as 'ne-name', although there is no SYSTEM business logic to correct this.",
        min_length=1,
        max_length=256,
        default=None,
        alias="src-node-id",
    )
    src_card_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="Card identification.",
            min_length=1,
            max_length=64,
            default=None,
            alias="src-card-name",
        )
    )
    src_port_name: str = Field(
        json_schema_extra={"is_config": True},
        description="Port identification, as used by managers.",
        min_length=1,
        max_length=128,
        alias="src-port-name",
    )
    dst_node_id: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Should be logically the same as 'ne-name', although there is no SYSTEM business logic to correct this.",
        min_length=1,
        max_length=256,
        default=None,
        alias="dst-node-id",
    )
    dst_card_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": True},
            description="Card identification.",
            min_length=1,
            max_length=64,
            default=None,
            alias="dst-card-name",
        )
    )
    dst_port_name: str = Field(
        json_schema_extra={"is_config": True},
        description="Port identification, as used by managers.",
        min_length=1,
        max_length=128,
        alias="dst-port-name",
    )
    fiber_connection_type: DirectionEnum_4 | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of the fiber connection - one-way or two-way.",
        default=DirectionEnum_4.TWO_WAY,
        alias="fiber-connection-type",
    )


class LaunchConditionEnum(str, Enum):
    """Enumeration for LaunchConditionEnum

    Values:
      * flat-tx
      * pfib
    """

    FLAT_TX = "flat-tx"
    PFIB = "pfib"


class SubmarineLinkItem(YangBaseModel):
    """Submarine link topology including Branching Units (BU) and subsea link parameters."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="User defined name for the subsea link topology.",
        min_length=1,
        max_length=64,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    src_node_id: str = Field(
        json_schema_extra={"is_config": True},
        description="Should be logically the same as 'ne-name', although this is not enforced. Note that in a subsea topology the same src-node-id can connect to multiple dst-node-ids indicating the presence of intervening BUs.",
        min_length=1,
        max_length=256,
        alias="src-node-id",
    )
    src_card_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Card identification.",
        min_length=0,
        max_length=64,
        default=None,
        alias="src-card-name",
    )
    src_port_name: str = Field(
        json_schema_extra={"is_config": True},
        description="Port identification, as used by managers.",
        min_length=1,
        max_length=128,
        alias="src-port-name",
    )
    dst_node_id: str = Field(
        json_schema_extra={"is_config": True},
        description="Should be logically the same as 'ne-name', although this is not enforced.",
        min_length=1,
        max_length=256,
        alias="dst-node-id",
    )
    dst_card_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Card identification.",
        min_length=0,
        max_length=64,
        default=None,
        alias="dst-card-name",
    )
    dst_port_name: str = Field(
        json_schema_extra={"is_config": True},
        description="Port identification, as used by managers.",
        min_length=1,
        max_length=128,
        alias="dst-port-name",
    )
    fiber_connection_type: DirectionEnum_4 | None = Field(
        json_schema_extra={"is_config": True},
        description="Type of the fiber connection - one-way or two-way.",
        default=DirectionEnum_4.TWO_WAY,
        alias="fiber-connection-type",
    )
    link_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The name of the submarine link.",
        min_length=0,
        max_length=256,
        default=None,
        alias="link-name",
    )
    fiber_pair_id: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The fiber pair identifier associated with the link.",
        min_length=0,
        max_length=128,
        default=None,
        alias="fiber-pair-id",
    )
    fiber_length: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines the fiber length of the associated fiber pair ID. This does not include the length of the branch segments.",
        ge=0,
        le=25000,
        default=0,
        alias="fiber-length",
    )
    segment_list: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines the list of fiber segments that constitute the link.",
        min_length=0,
        max_length=512,
        default=None,
        alias="segment-list",
    )
    bu_segment_index: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines the index of the segment location associated to the BU.",
        ge=0,
        default=None,
        alias="bu-segment-index",
    )
    rx_fiber_type: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The Rx fiber type on the DWDM Line for the link.",
        min_length=0,
        max_length=128,
        default=None,
        alias="rx-fiber-type",
    )
    tx_fiber_type: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The Tx fiber type on the DWDM Line for the link.",
        min_length=0,
        max_length=128,
        default=None,
        alias="tx-fiber-type",
    )
    gsnr: Decimal64 | None = Field(
        json_schema_extra={"is_config": True}, description="Expected GSNR for the link.", default=None
    )
    degree_target_tx_power: str | float = Field(
        json_schema_extra={"is_config": True},
        description="The target Tx power for the degree.",
        alias="degree-target-tx-power",
    )
    degree_expected_rx_power: str | float | None = Field(
        json_schema_extra={"is_config": True},
        description="The target Rx power for the degree.",
        default=None,
        alias="degree-expected-rx-power",
    )
    commissioning_snr_margin: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="SNR margin at the time of commissioning.",
        default=None,
        alias="commissioning-snr-margin",
    )
    launch_condition: LaunchConditionEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Defines the launch option for the Tx pre-emphasis.",
        default=LaunchConditionEnum.PFIB,
        alias="launch-condition",
    )
    allocated_spectrum_list: RestconfList[Annotated[int, Field(ge=0)]] | None = Field(
        json_schema_extra={"is_config": True},
        description="Allocated spectrum blocks for the link configured as a set of start frequency, end frequency pairs.",
        default=None,
        alias="allocated-spectrum-list",
    )


class SrcChassisStateEnum(str, Enum):
    """Enumeration for SrcChassisStateEnum

    Values:
      * node-controller: Means this chassis is the Node Controller chassis.
      * provisioned: Means this chassis is provisioned as a sub-chassis.
      * unprovisioned: Means this chassis is detected but not provisioned.
    """

    NODE_CONTROLLER = "node-controller"
    PROVISIONED = "provisioned"
    UNPROVISIONED = "unprovisioned"


class NctConnectionItem(YangBaseModel):
    """NCT connectivity information, providing existing links between NCT ports in a multi-chassis NE.
    These links are dynamically filled in by the system, allowing to derive and display the NCT topology.
    All connections defined here are bidirectional; source and destination are therefore interchangeable.
    """

    src_port: str = Field(
        json_schema_extra={"is_config": False},
        description="The source port of the connection. Must be an NCT port.\nIf the port belongs to a commissioned chassis, it will be the AID of the port.\nIf the port belongs to an unprovisioned chassis, it will have the format\n   '<chassis-serial-number>-<slot>-NCT-<id>'",
        min_length=1,
        max_length=64,
        alias="src-port",
    )
    dst_port: str = Field(
        json_schema_extra={"is_config": False},
        description="The destination port of the connection. Must be an NCT port.\nIf the port belongs to a commissioned chassis, it will be the AID of the port.\nIf the port belongs to an unprovisioned chassis, it will have the format\n   '<chassis-serial-number>-<slot>-NCT-<id>'",
        min_length=1,
        max_length=64,
        alias="dst-port",
    )
    src_chassis: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The identifier of the chassis where the source port is located.\nIf it is a commissioned chassis, it will be the AID of the chassis.\nIf it is an unprovisioned chassis, it will have the chassis serial number.",
        min_length=1,
        max_length=64,
        default=None,
        alias="src-chassis",
    )
    dst_chassis: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The identifier of the chassis where the destination port is located.\nIf it is a commissioned chassis, it will be the AID of the chassis.\nIf it is an unprovisioned chassis, it will have the chassis serial number.",
        min_length=1,
        max_length=64,
        default=None,
        alias="dst-chassis",
    )
    src_chassis_state: SrcChassisStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The state of the src-chassis.",
        default=None,
        alias="src-chassis-state",
    )
    dst_chassis_state: SrcChassisStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The state of the dst-chassis.",
        default=None,
        alias="dst-chassis-state",
    )


class Links(YangBaseModel):
    """Links container within Topology."""

    fiber_connection: RestconfList[FiberConnectionItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Fiber Connection list - connecting two ports of L0 cards, or line-port of Transponders/ Muxponders.",
        default=None,
        alias="fiber-connection",
    )
    external_fiber_connection: RestconfList[ExternalFiberConnectionItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="External Fiber Connection name - connecting two ports of L0 cards in different NEs.",
        default=None,
        alias="external-fiber-connection",
    )
    submarine_link: RestconfList[SubmarineLinkItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Submarine link topology including Branching Units (BU) and subsea link parameters.",
        default=None,
        alias="submarine-link",
    )
    nct_connection: RestconfList[NctConnectionItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="NCT connectivity information, providing existing links between NCT ports in a multi-chassis NE.\nThese links are dynamically filled in by the system, allowing to derive and display the NCT topology.\nAll connections defined here are bidirectional; source and destination are therefore interchangeable.",
        default=None,
        alias="nct-connection",
    )


class AutodNeighborItem(YangBaseModel):
    """List of discovered neighbors."""

    local_port_id: str = Field(
        json_schema_extra={"is_config": False},
        description="The local port associated with the discovered neighbor.",
        alias="local-port-id",
    )
    discovered_ne_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Contains the ne-id parameter of the discovered neighbor.",
        min_length=0,
        max_length=255,
        default=None,
        alias="discovered-ne-id",
    )
    discovered_port_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="AID of the line port of the discovered neighbor.",
        min_length=0,
        max_length=64,
        default=None,
        alias="discovered-port-id",
    )


class AutoDiscovery(YangBaseModel):
    """The auto-discovery container contains discovered info from TXPDR and supports clear-topology RPCs to remove objects."""

    autoD_neighbor: RestconfList[AutodNeighborItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of discovered neighbors.",
        default=None,
        alias="autoD-neighbor",
    )


class NeighborAdjacencyStateEnum(str, Enum):
    """Enumeration for NeighborAdjacencyStateEnum

    Values:
      * blackout
      * discovery
      * holding
      * unknown
    """

    BLACKOUT = "blackout"
    DISCOVERY = "discovery"
    HOLDING = "holding"
    UNKNOWN = "unknown"


class InterfaceNeighborItem(YangBaseModel):
    """List of provisioned  Neighbors."""

    local_interface: str = Field(
        json_schema_extra={"is_config": True}, description="Name of the interface neighbor.", alias="local-interface"
    )
    associated_comm_channel: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Associated communication channel of provisioned neighbor.",
        default=None,
        alias="associated-comm-channel",
    )
    discovery_cycle_time: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Periodicity at which sndp discover messages will be sent.",
        ge=30,
        le=300,
        default=30,
        alias="discovery-cycle-time",
    )
    discovery_timeout: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Time after which discovery is considered as failed; when this timeout occurs, neighbor-adjacency state will transition to blackout.",
        ge=300,
        le=1800,
        default=300,
        alias="discovery-timeout",
    )
    discovery_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="It is a switch to enable or disable  discovery on the local interface.",
        default=True,
        alias="discovery-enabled",
    )
    neighbor_adjacency_state: NeighborAdjacencyStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates protocol state.",
        default=NeighborAdjacencyStateEnum.UNKNOWN,
        alias="neighbor-adjacency-state",
    )
    neighbor_ne_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates discovered neighbor ne ID.",
        min_length=0,
        max_length=255,
        default=None,
        alias="neighbor-ne-id",
    )
    neighbor_ne_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates discovered neighbor ne name.",
        min_length=0,
        max_length=255,
        default=None,
        alias="neighbor-ne-name",
    )
    neighbor_interface_name: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates discovered neighbor interface name.",
        min_length=0,
        max_length=128,
        default=None,
        alias="neighbor-interface-name",
    )
    neighbor_router_id: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Indicates discovered neighbor router ID.",
        default=None,
        alias="neighbor-router-id",
    )
    neighbor_ipv4_address: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Indicates discovered neighbor ipv4 address.",
        default=None,
        alias="neighbor-ipv4-address",
    )
    neighbor_ipv6_address: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                    v,
                )
            ),
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": False},
        description="Indicates discoverd neighbor ipv6 address.",
        default=None,
        alias="neighbor-ipv6-address",
    )
    last_change_time: (
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
        description="Provide a timestamp indicating when the interface neighbor information was last updated.",
        default=None,
        alias="last-change-time",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of interface-neighbor object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )


class Sndp(YangBaseModel):
    """Simple Neighbor Discovery Protocol container within Topology."""

    sndp_enabled: bool | None = Field(
        json_schema_extra={"is_config": True},
        description="This is a switch to control the sndp feature.",
        default=True,
        alias="sndp-enabled",
    )
    interface_neighbor: RestconfList[InterfaceNeighborItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="List of provisioned  Neighbors.",
        default=None,
        alias="interface-neighbor",
    )


class Topology(YangBaseModel):
    """Topology information related with this NE."""

    lldp: Lldp | None = Field(
        json_schema_extra={"is_config": True}, description="Global LLDP configuration.", default=None
    )
    icdp: Icdp | None = Field(
        json_schema_extra={"is_config": True},
        description="Contains ICDP (Intelligent Carrier Discovery Protocol) data.\nThis is a proprietary mechanism that allows Network Elements to\nauto-discover their neighbors using carrier OFEC-GCC over L1 line interfaces.",
        default=None,
    )
    inci: Inci | None = Field(
        json_schema_extra={"is_config": True},
        description="INCI is Inter-NE Communication Interface, Information related to Inter NE inter-op feature.",
        default=None,
    )
    cable_id: CableId | None = Field(
        json_schema_extra={"is_config": False},
        description="cable-id container, with cable-id path, progress and the test results..",
        default=None,
        alias="cable-id",
    )
    links: Links | None = Field(
        json_schema_extra={"is_config": True}, description="Links container within Topology.", default=None
    )
    auto_discovery: AutoDiscovery | None = Field(
        json_schema_extra={"is_config": False},
        description="The auto-discovery container contains discovered info from TXPDR and supports clear-topology RPCs to remove objects.",
        default=None,
        alias="auto-discovery",
    )
    sndp: Sndp | None = Field(
        json_schema_extra={"is_config": True},
        description="Simple Neighbor Discovery Protocol container within Topology.",
        default=None,
    )


class ApplicationDescriptionItem(YangBaseModel):
    """Detailed description of application ID"""

    application: str = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport application ID this mode is optimized for.",
        min_length=1,
        max_length=15,
    )
    application_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Detailed description of application ID",
        min_length=0,
        max_length=1024,
        default=None,
        alias="application-description",
    )


class Gadt(YangBaseModel):
    """Golden Application Description Table - provides human readable details for carrier-mode applications."""

    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Table version.", min_length=0, max_length=5, default=None
    )
    application_description: RestconfList[ApplicationDescriptionItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Detailed description of application ID",
        default=None,
        alias="application-description",
    )


class DustFilterReplacementEnum(str, Enum):
    """Enumeration for DustFilterReplacementEnum

    Values:
      * not-applicable: No dust filter.
      * optional-dust-filter: Optional dust-filter and replacement.
      * dust-filter-regularly-replaced: Dust filter should be regularly replaced.
    """

    NOT_APPLICABLE = "not-applicable"
    OPTIONAL_DUST_FILTER = "optional-dust-filter"
    DUST_FILTER_REGULARLY_REPLACED = "dust-filter-regularly-replaced"


class SlotLocationEnum(str, Enum):
    """Enumeration for SlotLocationEnum

    Values:
      * front
      * rear
    """

    FRONT = "front"
    REAR = "rear"


class ConfigurationModeEnum(str, Enum):
    """Enumeration for ConfigurationModeEnum

    Values:
      * system-configured: Means system automaticaly configures the card in slot (or tom in this port), and user cannot make changes to that.
      * user-configured: Means that user can provision or unprovision cards in this slot (or toms in this port).
    """

    SYSTEM_CONFIGURED = "system-configured"
    USER_CONFIGURED = "user-configured"


class RequiresBlankWhenEmptyEnum(str, Enum):
    """Enumeration for RequiresBlankWhenEmptyEnum

    Values:
      * not-applicable
      * optional
      * required
    """

    NOT_APPLICABLE = "not-applicable"
    OPTIONAL = "optional"
    REQUIRED = "required"


class SupportedSlotItem(YangBaseModel):
    """Capability for each slot. The supported-slots can be within each supported-chassis or supported-card."""

    slot_name: str = Field(json_schema_extra={"is_config": False}, description="Name of the slot.", alias="slot-name")
    slot_location: SlotLocationEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Physical location of the slot in the chassis",
        default=None,
        alias="slot-location",
    )
    slot_vertical_position: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Position of the slot vertically in the chassis, counting\nfrom the top of the chassis/card, in RUs.\nExample: position 3 means third RU starting from the top of the chassis/card.",
        ge=0,
        default=None,
        alias="slot-vertical-position",
    )
    slot_horizontal_position: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Position of the slot horizontally in the chassis/card within the current RU, counting\nfrom the left of the chassis/card.\nFor back slots, the position is counted also from the left, from a point of view facing\nthe rear of the chassis/card.",
        ge=0,
        default=None,
        alias="slot-horizontal-position",
    )
    possible_card_types: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of possible card types in this slot.",
        default=None,
        alias="possible-card-types",
    )
    configuration_mode: ConfigurationModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Configuration mode for the cards in this slot (or toms in this port).",
        default=ConfigurationModeEnum.USER_CONFIGURED,
        alias="configuration-mode",
    )
    auto_provision_capable: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this slot supports card auto-provisioning.",
        default=None,
        alias="auto-provision-capable",
    )
    default_card: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Card that exists in this slot by default.",
        default=None,
        alias="default-card",
    )
    requires_blank_when_empty: RequiresBlankWhenEmptyEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this slot requires a BLANK filler card when empty.",
        default=None,
        alias="requires-blank-when-empty",
    )
    reset_power: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Reset power consumption for this card, at 55ºC",
        default=None,
        alias="reset-power",
    )
    virtual_slot: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Describes whether this slot is virtual.",
        default=False,
        alias="virtual-slot",
    )
    leds: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of LEDs available in the slot.",
        min_length=1,
        max_length=20,
        default=None,
    )


class SupportedChassisItem(YangBaseModel):
    """Capability information for supported chassis."""

    chassis_type: str = Field(
        json_schema_extra={"is_config": False}, description="Chassis type name.", alias="chassis-type"
    )
    supported_subtype: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported chassis subtypes; may be empty if chassis doesn't support subtypes.",
        default=None,
        alias="supported-subtype",
    )
    default_subtype: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Default subtype Supported by chassis.",
        default=None,
        alias="default-subtype",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Human readable description for this chassis-type.",
        min_length=0,
        max_length=255,
        default=None,
    )
    controller_redundancy_supported: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this chassis supports controller redundancy or not.",
        default=None,
        alias="controller-redundancy-supported",
    )
    power_control_supported: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this chassis supports power control, i.e. the ability to evaluate\nthe power supply currently provided by the PEMs against the configured equipment.\nA chassis that has power control support may put some cards into low power mode\nwhen not enough power is enabled, as well as raising alarms when power protection fail.",
        default=None,
        alias="power-control-supported",
    )
    fan_adjustment_on_altitude: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether FAN(s) rotation are automatically adjusting based on the configured altitude.",
        default=False,
        alias="fan-adjustment-on-altitude",
    )
    dust_filter_replacement: DustFilterReplacementEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Chassis characteristics related with dust filter (and its replacement).",
        default=DustFilterReplacementEnum.OPTIONAL_DUST_FILTER,
        alias="dust-filter-replacement",
    )
    depth: int | None = Field(
        json_schema_extra={"is_config": False}, description="Chassis depth in millimeters.", ge=0, default=None
    )
    height: int | None = Field(
        json_schema_extra={"is_config": False}, description="Chassis height in RUs (Rack Units).", ge=0, default=None
    )
    number_of_front_slots: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of equipment holder slots in the front plate on the chassis.",
        ge=0,
        default=None,
        alias="number-of-front-slots",
    )
    number_of_rear_slots: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of equipment holder slots in the back plate on the chassis.",
        ge=0,
        default=None,
        alias="number-of-rear-slots",
    )
    leds: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of LEDs available in the chassis.",
        min_length=1,
        max_length=20,
        default=None,
    )
    supported_subchassis_type: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of chassis-types that this chassis supports as sub-chassis.\nIf empty, means this chassis-type does not support multi-chassis feature.",
        default=None,
        alias="supported-subchassis-type",
    )
    supported_slot: RestconfList[SupportedSlotItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capability for each slot. The supported-slots can be within each supported-chassis or supported-card.",
        default=None,
        alias="supported-slot",
    )
    supported_features: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported features; may be empty if no features are not supported.",
        min_length=0,
        max_length=64,
        default=None,
        alias="supported-features",
    )


class CardWidthEnum(str, Enum):
    """Enumeration for CardWidthEnum

    Values:
      * na: Not Applicable.
      * single-slot: Single slot width.
      * double-slot: Double slot width.
      * half-slot: Half slot width.
      * triple-slot: three slot width.
    """

    NA = "na"
    SINGLE_SLOT = "single-slot"
    DOUBLE_SLOT = "double-slot"
    HALF_SLOT = "half-slot"
    TRIPLE_SLOT = "triple-slot"


class SupportedPowerProfileItem(YangBaseModel):
    """Supported power profile for this card-type.
    Different power profiles can be supported to reflect different scenarios when using this card.
    User is able to define, per card instance, which profile is in effect.
    This will have impact on the power estimation for the system.
    """

    name: str = Field(json_schema_extra={"is_config": False}, description="Profile name.")
    profile_description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Description of the profile.",
        min_length=0,
        max_length=255,
        default=None,
        alias="profile-description",
    )
    power_draw: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Power draw of associated equipment when not in low-power.",
        default=None,
        alias="power-draw",
    )
    default: bool | None = Field(
        json_schema_extra={"is_config": False}, description="Whether is the default value or not.", default=None
    )


class ConsolePortSupportEnum(str, Enum):
    """Enumeration for ConsolePortSupportEnum

    Values:
      * no: Card-type does not have a serial console port.
      * yes-with-auto-sensing-baud-rate: Card-type has a serial console port, supporting auto-sensing of baud-rate.
      * yes-with-fixed-baud-rate: Card-type has a serial console port, supporting manually configured baud-rate.
    """

    NO = "no"
    YES_WITH_AUTO_SENSING_BAUD_RATE = "yes-with-auto-sensing-baud-rate"
    YES_WITH_FIXED_BAUD_RATE = "yes-with-fixed-baud-rate"


class PresentEnum(str, Enum):
    """Enumeration for PresentEnum

    Values:
      * always: This port is always present for this card type.
      * in-node-controller-only: This port is only present if this card is instanciated in a node controller chassis. Will not be instanciated for sub-chassis cards.
    """

    ALWAYS = "always"
    IN_NODE_CONTROLLER_ONLY = "in-node-controller-only"


class SupportedTomItem(YangBaseModel):
    """Capability information for supported TOM (Transceiver Optical Module) in the scope
    of this particular card.
    """

    tom_type: str = Field(json_schema_extra={"is_config": False}, description="TOM type name.", alias="tom-type")
    tom_subtype_group: str = Field(
        json_schema_extra={"is_config": False},
        description="TOM subtype group.",
        min_length=0,
        max_length=32,
        alias="tom-subtype-group",
    )
    supported_subtype: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported subtypes for this TOM type in this particular card/port.",
        default=None,
        alias="supported-subtype",
    )
    supported_phy_modes: RestconfList[PhyModeEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="The phy-mode that are supported in this TOM for this card.",
        default=None,
        alias="supported-phy-modes",
    )
    default_phy_mode: PhyModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The phy-mode that is used by default in this TOM for this card.",
        default=None,
        alias="default-phy-mode",
    )


class SupportedPortItem(YangBaseModel):
    """Capabilities for each port in each supported card."""

    port_name: str = Field(json_schema_extra={"is_config": False}, description="The port name.", alias="port-name")
    port_type: PortTypeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The port type. Each port type supports different features and services.",
        default=None,
        alias="port-type",
    )
    direction: DirectionEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Direction of the port.",
        default=DirectionEnum.NOT_APPLICABLE,
    )
    configuration_mode: ConfigurationModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Configuration mode for the cards in this slot (or toms in this port).",
        default=ConfigurationModeEnum.USER_CONFIGURED,
        alias="configuration-mode",
    )
    faceplate_label: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Label on the hardware faceplate.",
        min_length=0,
        max_length=36,
        default=None,
        alias="faceplate-label",
    )
    leds: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of LEDs available for each port of this card.",
        min_length=1,
        max_length=20,
        default=None,
    )
    present: PresentEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Provides information regarding when is this port present (e.g. instanciated as a managed object).\nThe majority of ports are statically available for each card type, but some\nare only available in specific scenarios, described here.",
        default=PresentEnum.ALWAYS,
    )
    default_tom: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Tom that exists in this port by default.",
        default="none",
        alias="default-tom",
    )
    parent_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Name of the parent port. Only applicable for sub-ports.",
        min_length=0,
        max_length=32,
        default=None,
        alias="parent-port",
    )
    subport_list: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of sub-ports associated with this port.\nOnly applicable when this port is a parent port.",
        min_length=1,
        max_length=30,
        default=None,
        alias="subport-list",
    )
    allows_auto_migration: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates if TOMs that are plugged on this port type are auto migrated according with the equipment-policies tom-auto-migration flag.",
        default=True,
        alias="allows-auto-migration",
    )
    supported_tom: RestconfList[SupportedTomItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capability information for supported TOM (Transceiver Optical Module) in the scope\nof this particular card.",
        default=None,
        alias="supported-tom",
    )


class SubtypeConstraintItem(YangBaseModel):
    """List of subtype constraints."""

    subtype: str = Field(
        json_schema_extra={"is_config": False},
        description="Card Subtype. Represents a group of related PONs for a card type to which these constraints applies.",
        min_length=1,
        max_length=20,
    )
    min_capacity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The minimum capacity supported by this subtype.",
        default=None,
        alias="min-capacity",
    )
    max_capacity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The maximum capacity supported by this subtype. -1 means there is no maximum capacity constraint.",
        default=None,
        alias="max-capacity",
    )
    supported_applications: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of applications supported by this subtype. If this list is empty, then this constraint is not applicable.",
        min_length=1,
        max_length=15,
        default=None,
        alias="supported-applications",
    )
    unsupported_applications: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of applications not supported by this subtype. If this list is empty, then this constraint is not applicable.",
        min_length=1,
        max_length=15,
        default=None,
        alias="unsupported-applications",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Subtype description.",
        min_length=0,
        max_length=255,
        default=None,
    )


class Gsct(YangBaseModel):
    """Golden Subtype Constraint Table - contains additional restrictions on supported
    carrier modes (defined by gcmt), based on card subtype.
    """

    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Table version.", min_length=0, max_length=5, default=None
    )
    subtype_constraint: RestconfList[SubtypeConstraintItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of subtype constraints.",
        default=None,
        alias="subtype-constraint",
    )


class StatusEnum_5(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * supported
      * candidate
      * experimental
      * deprecated
      * diagnostic
    """

    SUPPORTED = "supported"
    CANDIDATE = "candidate"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
    DIAGNOSTIC = "diagnostic"


class GoldenCarrierModeItem(YangBaseModel):
    """List of golden carrier modes."""

    carrier_mode: str = Field(
        json_schema_extra={"is_config": False},
        description="An acronymized code (handle) that is indicative of the optical carrier line mode (4-tuple) combination.\nThe format is as follows:\n   <Capacity><ClientMode>.<Baud Rate><Application ID>\nExamples:\n   - 600E.84P\n   - 100X.73U\n   - 325M.66P",
        min_length=0,
        max_length=15,
        alias="carrier-mode",
    )
    actual_carrier_mode: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The actual carrier-mode.",
        min_length=0,
        max_length=15,
        default=None,
        alias="actual-carrier-mode",
    )
    capacity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The net capacity of the optical carrier.",
        ge=0,
        default=None,
    )
    client_mode: ClientModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="This indicates digital client modes of the signal\nthat is mapped into, and transported by the carriers within this\nsuperchannel.",
        default=None,
        alias="client-mode",
    )
    baud_rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="The modulated symbol rate.",
        default=None,
        alias="baud-rate",
    )
    application: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport application ID this mode is optimized for.",
        min_length=1,
        max_length=15,
        default=None,
    )
    sop_tracking_mode: SopTrackingModeEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The optical transport SOP tracking mode this mode is optimized for.",
        default=SopTrackingModeEnum.NORMAL,
        alias="sop-tracking-mode",
    )
    compatibility_id: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies the compatible carrier modes that can be applied simultaneously",
        ge=0,
        default=None,
        alias="compatibility-id",
    )
    status: StatusEnum_5 | None = Field(
        json_schema_extra={"is_config": False}, description="Describes carrier mode release status.", default=None
    )
    supported_subtypes: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Subtypes that each carrier mode supports.",
        min_length=0,
        max_length=32,
        default=None,
        alias="supported-subtypes",
    )


class Gcmt(YangBaseModel):
    """Golden Carrier Mode Table - provides list of supported carrier modes in this card.
    Applicable for cards that support configurable optical carriers (transponders).
    To be used as reference, and in pre-provisioning scenarios.
    Once card is physically present, its discovered supported modes will be used instead of these.
    """

    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Table version.", min_length=0, max_length=5, default=None
    )
    golden_carrier_mode: RestconfList[GoldenCarrierModeItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of golden carrier modes.",
        default=None,
        alias="golden-carrier-mode",
    )


class GoldenAdvancedParameterItem(YangBaseModel):
    """A set of all optical carrier advanced parameters discovered from the equipment."""

    name: str = Field(
        json_schema_extra={"is_config": False},
        description="The name of the advanced parameter.",
        min_length=0,
        max_length=256,
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="A human readable description of this advanced parameter.",
        min_length=0,
        max_length=256,
        default=None,
    )
    type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Indicates the data type of the advanced parameter.",
        min_length=0,
        max_length=255,
        default=None,
    )
    supported_values: str | None = Field(
        json_schema_extra={"is_config": False},
        description="This list indicates the possible values that this parameter can take as input. It is a list of ranges.\n   E.g.'1-4, 10-14' indicating two ranges from 1 to 4 and 10 to 14. Or it could be a list of discrete\n   numbers like '10, 20, 30, 40'. Spaces are optional.",
        min_length=0,
        max_length=256,
        default=None,
        alias="supported-values",
    )
    direction: DirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Advanced parameter is applicable to the specified direction.",
        default=None,
    )
    multiplicity: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies number of values user need to enter for this advanced parameter.\n   Same range or allowed-values will apply for each entry.",
        ge=0,
        default=None,
    )
    configuration_impact: ConfigurationImpactEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies the configuration steps to apply the change.",
        default=None,
        alias="configuration-impact",
    )
    service_impact: ServiceImpactEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Identifies if applying this parameter change causes service impact. If it is service impacting, user must perform admin lock/maintenance/ToDO operation.",
        default=None,
        alias="service-impact",
    )


class Gapt(YangBaseModel):
    """Golden Advanced Parameters Table - provides a list of known advanced parameters that this card supports."""

    version: str | None = Field(
        json_schema_extra={"is_config": False}, description="Table version.", min_length=0, max_length=5, default=None
    )
    golden_advanced_parameter: RestconfList[GoldenAdvancedParameterItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="A set of all optical carrier advanced parameters discovered from the equipment.",
        default=None,
        alias="golden-advanced-parameter",
    )
    applicable_resource_type: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="The managed resource type(s) that are applicable for this particular advanced parameter.",
        default=None,
        alias="applicable-resource-type",
    )


class SupportedCardItem(YangBaseModel):
    """Capability information for supported card."""

    card_type: str = Field(json_schema_extra={"is_config": False}, description="Card type name.", alias="card-type")
    node_type_compatibility: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Node Type Compatibility refers to supported NE Node-type for a sled card.\n    Only of relevance for line-card(s) and carrier-card(s).",
        default=None,
        alias="node-type-compatibility",
    )
    sw_support_revision: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Software revision currently installed.",
        ge=0,
        default=0,
        alias="sw-support-revision",
    )
    supported_subtype: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported card subtypes; may be empty if card doesn't support subtypes.",
        default=None,
        alias="supported-subtype",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Human readable description for this card-type.",
        min_length=0,
        max_length=255,
        default=None,
    )
    default_card_mode: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The default card-mode, for cards whose supported-card-mode is not empty.\nOnly relevant if card has the concept of card-mode.",
        min_length=0,
        max_length=20,
        default=None,
        alias="default-card-mode",
    )
    supported_card_mode: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported card-modes; may be empty if card does not support any card-mode.",
        min_length=0,
        max_length=20,
        default=None,
        alias="supported-card-mode",
    )
    card_width: CardWidthEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Number of slots this card occupies; not-applicable for RU equipment.",
        default=None,
        alias="card-width",
    )
    card_height: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Card height in RUs.",
        ge=0,
        default=None,
        alias="card-height",
    )
    is_field_replaceable: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this card-type is a field replaceable unit (FRU).",
        default=None,
        alias="is-field-replaceable",
    )
    category: CategoryEnum | None = Field(
        json_schema_extra={"is_config": False}, description="Card category.", default=None
    )
    grid_mode_support: SupportedBandAndGridEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="grid-mode capabilities.\n    Only of relevance for line-card(s).",
        default=SupportedBandAndGridEnum.GENERAL_C_BAND,
        alias="grid-mode-support",
    )
    max_power_draw: Decimal64 | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum power draw for this card.",
        default=None,
        alias="max-power-draw",
    )
    supported_power_profile: RestconfList[SupportedPowerProfileItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported power profile for this card-type.\nDifferent power profiles can be supported to reflect different scenarios when using this card.\nUser is able to define, per card instance, which profile is in effect.\nThis will have impact on the power estimation for the system.",
        default=None,
        alias="supported-power-profile",
    )
    leds: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of LEDs available in the card.",
        min_length=1,
        max_length=20,
        default=None,
    )
    location_led_support: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this card-type support location-led operation.",
        default=None,
        alias="location-led-support",
    )
    console_port_support: ConsolePortSupportEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this card-type supports a serial console port, with or without auto-sensing capabilities.",
        default=ConsolePortSupportEnum.NO,
        alias="console-port-support",
    )
    default_console_baud_rate: ConsoleBaudRateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="For cards with fixed baud-rate, defines the default baud-rate.",
        default=None,
        alias="default-console-baud-rate",
    )
    support_serdes_config: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="If true, it means this card-type allows user to configure 3rd Party TOM SerDes values. If false, the card has no need for such customization.",
        default=False,
        alias="support-serdes-config",
    )
    supported_bands: RestconfList[TransmissionBandEnum] | None = Field(
        json_schema_extra={"is_config": False},
        description="List of bands supported by the card.",
        default=None,
        alias="supported-bands",
    )
    supported_port: RestconfList[SupportedPortItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capabilities for each port in each supported card.",
        default=None,
        alias="supported-port",
    )
    gsct: Gsct | None = Field(
        json_schema_extra={"is_config": False},
        description="Golden Subtype Constraint Table - contains additional restrictions on supported\ncarrier modes (defined by gcmt), based on card subtype.",
        default=None,
    )
    supported_slot: RestconfList[SupportedSlotItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capability for each slot. The supported-slots can be within each supported-chassis or supported-card.",
        default=None,
        alias="supported-slot",
    )
    supported_features: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": False},
        description="Supported features; may be empty if no features are not supported.",
        min_length=0,
        max_length=64,
        default=None,
        alias="supported-features",
    )
    gcmt: Gcmt | None = Field(
        json_schema_extra={"is_config": False},
        description="Golden Carrier Mode Table - provides list of supported carrier modes in this card.\nApplicable for cards that support configurable optical carriers (transponders).\nTo be used as reference, and in pre-provisioning scenarios.\nOnce card is physically present, its discovered supported modes will be used instead of these.",
        default=None,
    )
    gapt: Gapt | None = Field(
        json_schema_extra={"is_config": False},
        description="Golden Advanced Parameters Table - provides a list of known advanced parameters that this card supports.",
        default=None,
    )


class TomTypeItem(YangBaseModel):
    """Capability information for supported TOM (Transceiver Optical Module)."""

    tom_type: str = Field(json_schema_extra={"is_config": False}, description="TOM type name.", alias="tom-type")
    data_rate: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The approximate data-rate for this TOM type.",
        ge=0,
        default=None,
        alias="data-rate",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Human readable description for this TOM type.",
        min_length=0,
        max_length=255,
        default=None,
    )
    support_third_party_toms: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Whether this TOM type accepts third party TOMs in addition to officially supported Nokia TOMs.",
        default=None,
        alias="support-third-party-toms",
    )
    generic_subtype: str | None = Field(
        json_schema_extra={"is_config": False},
        description="3rd party subtype for this TOM.\nAvailable when support 3rd party toms is enable.",
        default=None,
        alias="generic-subtype",
    )


class EquipmentCapabilities(YangBaseModel):
    """Top level container for all equipment capabilities."""

    gadt: Gadt | None = Field(
        json_schema_extra={"is_config": False},
        description="Golden Application Description Table - provides human readable details for carrier-mode applications.",
        default=None,
    )
    supported_chassis: RestconfList[SupportedChassisItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capability information for supported chassis.",
        default=None,
        alias="supported-chassis",
    )
    supported_card: RestconfList[SupportedCardItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capability information for supported card.",
        default=None,
        alias="supported-card",
    )
    tom_type: RestconfList[TomTypeItem] | None = Field(
        json_schema_extra={"is_config": False},
        description="Capability information for supported TOM (Transceiver Optical Module).",
        default=None,
        alias="tom-type",
    )


class OadmCapabilities(YangBaseModel):
    """OADM capabilities"""

    max_degrees: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum number of degrees.",
        ge=0,
        default=None,
        alias="max-degrees",
    )
    max_adgs: int | None = Field(
        json_schema_extra={"is_config": False},
        description="Maximum number of ADGs (Add/ Drop Group(s))",
        ge=0,
        default=None,
        alias="max-adgs",
    )


class L0Capabilities(YangBaseModel):
    """Layer 0 Capabilities."""

    oadm_capabilities: OadmCapabilities | None = Field(
        json_schema_extra={"is_config": False}, description="OADM capabilities", default=None, alias="oadm-capabilities"
    )


class SystemCapabilities(YangBaseModel):
    """Top level container for all capability information.
    This data is read-only, and expected to be informative to the user
    regarding what are the system capabilities.
    This information is static and independent on current configuration.
    Capabilities can be updated only:
    - with SW upgrade
    - with a dedicated capabilities file update (for specific cases only)
    """

    equipment_capabilities: EquipmentCapabilities | None = Field(
        json_schema_extra={"is_config": False},
        description="Top level container for all equipment capabilities.",
        default=None,
        alias="equipment-capabilities",
    )
    l0_capabilities: L0Capabilities | None = Field(
        json_schema_extra={"is_config": False},
        description="Layer 0 Capabilities.",
        default=None,
        alias="l0-capabilities",
    )


class PgStateEnum(str, Enum):
    """Enumeration for PgStateEnum

    Values:
      * no-request: No request.
      * do-not-revert: Do not revert.
      * manual-to-working: Manual to working.
      * manual-to-protection: Manual to protection.
      * forced-to-working: Force to working.
      * forced-to-protection: Force to protection.
      * protection-lockout: Lockout of protection.
      * sf-on-working: Signal fail on working.
      * sf-on-protection: Signal fail on protection.
      * sd-on-working: Signal degrade on working.
      * sd-on-protection: Signal degrade on protection.
      * wait-to-restore: Wait to restore.
      * frozen: state machine is frozen.
      * unavailable: Unavailable.
    """

    NO_REQUEST = "no-request"
    DO_NOT_REVERT = "do-not-revert"
    MANUAL_TO_WORKING = "manual-to-working"
    MANUAL_TO_PROTECTION = "manual-to-protection"
    FORCED_TO_WORKING = "forced-to-working"
    FORCED_TO_PROTECTION = "forced-to-protection"
    PROTECTION_LOCKOUT = "protection-lockout"
    SF_ON_WORKING = "sf-on-working"
    SF_ON_PROTECTION = "sf-on-protection"
    SD_ON_WORKING = "sd-on-working"
    SD_ON_PROTECTION = "sd-on-protection"
    WAIT_TO_RESTORE = "wait-to-restore"
    FROZEN = "frozen"
    UNAVAILABLE = "unavailable"


class PgRequestEnum(str, Enum):
    """Enumeration for PgRequestEnum

    Values:
      * clear
      * manual-to-working
      * manual-to-protection
      * forced-to-working
      * forced-to-protection
      * protection-lockout
    """

    CLEAR = "clear"
    MANUAL_TO_WORKING = "manual-to-working"
    MANUAL_TO_PROTECTION = "manual-to-protection"
    FORCED_TO_WORKING = "forced-to-working"
    FORCED_TO_PROTECTION = "forced-to-protection"
    PROTECTION_LOCKOUT = "protection-lockout"


class PgControlRequestEnum(str, Enum):
    """Enumeration for PgControlRequestEnum

    Values:
      * freeze
      * clear-freeze
    """

    FREEZE = "freeze"
    CLEAR_FREEZE = "clear-freeze"


class SwitchingModeEnum(str, Enum):
    """Enumeration for SwitchingModeEnum

    Values:
      * unidirectional
    """

    UNIDIRECTIONAL = "unidirectional"


class ReversionModeEnum(str, Enum):
    """Enumeration for ReversionModeEnum

    Values:
      * revertive
      * non-revertive
    """

    REVERTIVE = "revertive"
    NON_REVERTIVE = "non-revertive"


class LastSwitchTriggerEnum(str, Enum):
    """Enumeration for LastSwitchTriggerEnum

    Values:
      * clear
      * manual-to-working
      * manual-to-protection
      * forced-to-working
      * forced-to-protection
      * lockout
      * sf-on-working
      * sf-on-protection
      * sd-on-working
      * sd-on-protection
      * wtr-timer-expiration
    """

    CLEAR = "clear"
    MANUAL_TO_WORKING = "manual-to-working"
    MANUAL_TO_PROTECTION = "manual-to-protection"
    FORCED_TO_WORKING = "forced-to-working"
    FORCED_TO_PROTECTION = "forced-to-protection"
    LOCKOUT = "lockout"
    SF_ON_WORKING = "sf-on-working"
    SF_ON_PROTECTION = "sf-on-protection"
    SD_ON_WORKING = "sd-on-working"
    SD_ON_PROTECTION = "sd-on-protection"
    WTR_TIMER_EXPIRATION = "wtr-timer-expiration"


class SwitchFailureReasonEnum(str, Enum):
    """Enumeration for SwitchFailureReasonEnum

    Values:
      * none
      * request-timer-expiry
      * switch-status-failed
    """

    NONE = "none"
    REQUEST_TIMER_EXPIRY = "request-timer-expiry"
    SWITCH_STATUS_FAILED = "switch-status-failed"


class StateEnum_4(str, Enum):
    """Enumeration for StateEnum

    Values:
      * active
      * standby
      * unavailable
      * unknown
    """

    ACTIVE = "active"
    STANDBY = "standby"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class RoleEnum_1(str, Enum):
    """Enumeration for RoleEnum

    Values:
      * working
      * protection
    """

    WORKING = "working"
    PROTECTION = "protection"


class ProtectionUnitItem(YangBaseModel):
    """Protection unit that identifier protection entitiy"""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True}, description="Protection unit name", min_length=1, max_length=64
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    transport_entity: str | None = Field(
        json_schema_extra={"is_config": False},
        description="The transport entity associated with this protection unit.",
        default=None,
        alias="transport-entity",
    )
    state: StateEnum_4 | None = Field(
        json_schema_extra={"is_config": False}, description="Protection unit state", default=StateEnum_4.UNKNOWN
    )
    role: RoleEnum_1 | None = Field(
        json_schema_extra={"is_config": False}, description="Protection unit role", default=None
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )


class ProtectionGroupItem(YangBaseModel):
    """Protection Group associates two Protection Units that are redundant to each other, one said Working, the other Protection Unit.
    Each Protection Group entity forms a YPG.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="A user configured name for the protection group.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    protection_type: ProtectionTypeEnum = Field(
        json_schema_extra={"is_config": True},
        description="Represents the protection type this PG has.",
        alias="protection-type",
    )
    pg_state: PgStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Protection group state",
        default=PgStateEnum.UNAVAILABLE,
        alias="pg-state",
    )
    pg_request: PgRequestEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="The management of protection switching action.",
        default=PgRequestEnum.CLEAR,
        alias="pg-request",
    )
    pg_control_request: PgControlRequestEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="local command of protection.",
        default=PgControlRequestEnum.CLEAR_FREEZE,
        alias="pg-control-request",
    )
    switching_mode: SwitchingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Protection switching mode.",
        default=SwitchingModeEnum.UNIDIRECTIONAL,
        alias="switching-mode",
    )
    reversion_mode: ReversionModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable or disable automatic reversion protection status after wtr-time delay.",
        default=ReversionModeEnum.NON_REVERTIVE,
        alias="reversion-mode",
    )
    hold_off_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Switching trigger soaking time before switching, measured and set in 1-millisecond steps.",
        ge=0,
        le=10000,
        default=0,
        alias="hold-off-timer",
    )
    wtr_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Trigger clearance soaking time before reverting to the working protection unit, measured and set in 1-second steps. Only applicable in revertive mode.\n\nCondition (when): ../reversion-mode = 'revertive'",
        ge=60,
        le=720,
        default=300,
        alias="wtr-timer",
    )
    remaining_wtr: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The remaining time in the WTR timer, in seconds. Only applicable in Revertive mode.\n\nCondition (when): ../reversion-mode = 'revertive'",
        ge=0,
        le=720,
        default=None,
        alias="remaining-wtr",
    )
    last_switch_trigger: LastSwitchTriggerEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Last switch trigger.",
        default=LastSwitchTriggerEnum.CLEAR,
        alias="last-switch-trigger",
    )
    working_pu: str = Field(
        json_schema_extra={"is_config": True},
        description="The working unit associated with the protection group.",
        min_length=1,
        max_length=32,
        alias="working-pu",
    )
    protection_pu: str = Field(
        json_schema_extra={"is_config": True},
        description="The protection unit associated with the protection group.",
        min_length=1,
        max_length=32,
        alias="protection-pu",
    )
    reliable_cp: str = Field(
        json_schema_extra={"is_config": True},
        description="The reliable connection point associated with the protection group.\n    Only of relevance for protection type snc-n.",
        min_length=1,
        max_length=32,
        alias="reliable-cp",
    )
    client_side_olos_trigger: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Considers a local client-side RX OLOS defect as a trigger for switch-over.\n    Only of relevance for protection type y-cable.",
        default=EnableSwitchEnum.DISABLED,
        alias="client-side-olos-trigger",
    )
    client_side_sd_trigger: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Considers a local client-side RX SD defect as a trigger for switch-over.\n    Only of relevance for protection type y-cable.",
        default=EnableSwitchEnum.DISABLED,
        alias="client-side-sd-trigger",
    )
    network_side_csf_trigger: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Considers a network-side ingress CSF defect as a trigger for switch-over.",
        default=EnableSwitchEnum.DISABLED,
        alias="network-side-csf-trigger",
    )
    network_side_sd_trigger: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Considers a network-side ingress SD defect as a trigger for switch-over.\n    Only of relevance for protection type snc-n.",
        default=EnableSwitchEnum.DISABLED,
        alias="network-side-sd-trigger",
    )
    switch_failure_reason: SwitchFailureReasonEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="switch failure reason.",
        default=SwitchFailureReasonEnum.NONE,
        alias="switch-failure-reason",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    protection_unit: RestconfList[ProtectionUnitItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Protection unit that identifier protection entitiy",
        default=None,
        alias="protection-unit",
    )


class ProtectionTypeEnum_1(str, Enum):
    """Enumeration for ProtectionTypeEnum

    Values:
      * not-applicable: No protection.
      * oms: OMS protection type.
      * och-cs: Optical Channel/ Carrier Tributary Protection (without PT).
      * och-ls: Optical Line-side Channel Protection (with PT).
      * multi-channel: multi channel protection
    """

    NOT_APPLICABLE = "not-applicable"
    OMS = "oms"
    OCH_CS = "och-cs"
    OCH_LS = "och-ls"
    MULTI_CHANNEL = "multi-channel"


class WorkingOrProtectingLegEnum(str, Enum):
    """Enumeration for WorkingOrProtectingLegEnum

    Values:
      * working
      * protection
    """

    WORKING = "working"
    PROTECTION = "protection"


class SwitchRoleEnum(str, Enum):
    """Enumeration for SwitchRoleEnum

    Values:
      * standalone: Regular protection (2-path protection or any other).
      * cascaded-outer: OPSM is deployed in cascaded configuration (3-path protection) as outer instance.
      * cascaded-inner: OPSM is deployed in cascaded configuration (3-path protection) as inner instance.
    """

    STANDALONE = "standalone"
    CASCADED_OUTER = "cascaded-outer"
    CASCADED_INNER = "cascaded-inner"


class LastRequestEnum(str, Enum):
    """Enumeration for LastRequestEnum

    Values:
      * not-applicable: Not Applicable
      * clear: Clear
      * manual-to-working: Manual to Working
      * manual-to-protection: Manual to Protection
      * forced-to-working: Forced to Working
      * forced-to-protection: Forced to Protection
      * protection-lockout: Protection Lockout
    """

    NOT_APPLICABLE = "not-applicable"
    CLEAR = "clear"
    MANUAL_TO_WORKING = "manual-to-working"
    MANUAL_TO_PROTECTION = "manual-to-protection"
    FORCED_TO_WORKING = "forced-to-working"
    FORCED_TO_PROTECTION = "forced-to-protection"
    PROTECTION_LOCKOUT = "protection-lockout"


class LastSwitchTriggerEnum_1(str, Enum):
    """Enumeration for LastSwitchTriggerEnum

    Values:
      * not-applicable: Not Applicable
      * clear: Clear
      * manual-to-working: Manual switch to Working
      * manual-to-protection: Manual switch to Protection
      * forced-to-working: Forced switch to Working
      * forced-to-protection: Forced switch to Protection
      * lockout: Lockout
      * sf-on-working: Signal Fail on Working
      * sf-on-protection: Signal Fail on Protection
      * sd-on-working: Signal Degrade on Working
      * sd-on-protection: Signal Degrade on Protection
      * wtr: Wait to Restore
    """

    NOT_APPLICABLE = "not-applicable"
    CLEAR = "clear"
    MANUAL_TO_WORKING = "manual-to-working"
    MANUAL_TO_PROTECTION = "manual-to-protection"
    FORCED_TO_WORKING = "forced-to-working"
    FORCED_TO_PROTECTION = "forced-to-protection"
    LOCKOUT = "lockout"
    SF_ON_WORKING = "sf-on-working"
    SF_ON_PROTECTION = "sf-on-protection"
    SD_ON_WORKING = "sd-on-working"
    SD_ON_PROTECTION = "sd-on-protection"
    WTR = "wtr"


class WavelengthBandEnum(str, Enum):
    """Enumeration for WavelengthBandEnum

    Values:
      * o-band: O Band.
      * c-band: C Band.
    """

    O_BAND = "o-band"
    C_BAND = "c-band"


class OpticalSwitchItem(YangBaseModel):
    """optical-switch 'Protection Group' (PG)"""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": True},
        description="Fixed name, this is autonomously created by the system.",
        min_length=1,
        max_length=64,
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    supporting_card: str | None = Field(
        json_schema_extra={"is_config": False}, description="Protection card.", default=None, alias="supporting-card"
    )
    supporting_working_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Working port.",
        default=None,
        alias="supporting-working-port",
    )
    supporting_protection_port: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Protection port.",
        default=None,
        alias="supporting-protection-port",
    )
    protection_type: ProtectionTypeEnum_1 | None = Field(
        json_schema_extra={"is_config": True},
        description="Represents the protection type for this PG.",
        default=None,
        alias="protection-type",
    )
    pg_state: PgStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Protection group state",
        default=PgStateEnum.NO_REQUEST,
        alias="pg-state",
    )
    active_path: WorkingOrProtectingLegEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Protection active path (working/ protection).",
        default=WorkingOrProtectingLegEnum.WORKING,
        alias="active-path",
    )
    switch_role: SwitchRoleEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Indication for the cascading/ non-cascading OPSM switch role of the optical-switch.",
        default=SwitchRoleEnum.STANDALONE,
        alias="switch-role",
    )
    switching_mode: SwitchingModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Protection switching mode.",
        default=SwitchingModeEnum.UNIDIRECTIONAL,
        alias="switching-mode",
    )
    reversion_mode: ReversionModeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enable or disable automatic reversion protection status after wtr-time delay.",
        default=ReversionModeEnum.NON_REVERTIVE,
        alias="reversion-mode",
    )
    hold_off_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Switching trigger soaking time before switching, measured and set in 1-millisecond steps.",
        ge=0,
        le=10000,
        default=0,
        alias="hold-off-timer",
    )
    wtr_timer: int | None = Field(
        json_schema_extra={"is_config": True},
        description="Wait to Restore Timer: clearance soaking time before reverting to the working leg. Only applicable in revertive mode.\n\nCondition (when): ../reversion-mode = 'revertive'",
        ge=0,
        le=3600,
        default=300,
        alias="wtr-timer",
    )
    last_request: LastRequestEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="Last user request.",
        default=LastRequestEnum.NOT_APPLICABLE,
        alias="last-request",
    )
    last_switch_trigger: LastSwitchTriggerEnum_1 | None = Field(
        json_schema_extra={"is_config": False},
        description="Last switch trigger.",
        default=LastSwitchTriggerEnum_1.NOT_APPLICABLE,
        alias="last-switch-trigger",
    )
    och_center_frequency: int | None = Field(
        json_schema_extra={"is_config": True},
        description="The frequency of Optical Protection switch, which will decide the pilot tone modulated on the channel.",
        ge=0,
        default=0,
        alias="och-center-frequency",
    )
    working_switch_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The switching threshold of the working port which indicates the optical power threshold of signal degrade.",
        ge=-55.0,
        le=55.0,
        default=-18.0,
        alias="working-switch-threshold",
    )
    protection_switch_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The switching threshold of the protection port which indicates the optical power threshold of signal degrade.",
        ge=-55.0,
        le=55.0,
        default=-18.0,
        alias="protection-switch-threshold",
    )
    working_path_degree: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The degree number of the working path degree.  The value of zero denotes that the working path degree is not associated yet.",
        ge=0,
        default=0,
        alias="working-path-degree",
    )
    protection_path_degree: int | None = Field(
        json_schema_extra={"is_config": False},
        description="The degree number of the protection path degree.",
        ge=0,
        default=0,
        alias="protection-path-degree",
    )
    switch_threshold_enable: EnableSwitchEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Enables protection switching based on SD threshold configured for Working and Protection Paths.",
        default=EnableSwitchEnum.DISABLED,
        alias="switch-threshold-enable",
    )
    working_los_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The switching threshold of the working port, power level below it will lead to loss of signal.",
        ge=-55.0,
        le=55.0,
        default=-23.0,
        alias="working-los-threshold",
    )
    protection_los_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The switching threshold of the protection port, power level below it will lead to loss of signal.",
        ge=-55.0,
        le=55.0,
        default=-23.0,
        alias="protection-los-threshold",
    )
    facility_los_threshold: Decimal64 | None = Field(
        json_schema_extra={"is_config": True},
        description="The threshold of the facility port, power level below it will lead to loss of signal.",
        ge=-55.0,
        le=55.0,
        default=-30.0,
        alias="facility-los-threshold",
    )
    wavelength_band: WavelengthBandEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Wavelength band o-band(1310), c-band(1550) are used for internal PD calibration and IL test.",
        default=WavelengthBandEnum.C_BAND,
        alias="wavelength-band",
    )


class Protection(YangBaseModel):
    """The top-level protection root node under which all other protection entities are present."""

    protection_group: RestconfList[ProtectionGroupItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="Protection Group associates two Protection Units that are redundant to each other, one said Working, the other Protection Unit.\nEach Protection Group entity forms a YPG.",
        default=None,
        alias="protection-group",
    )
    optical_switch: RestconfList[OpticalSwitchItem] | None = Field(
        json_schema_extra={"is_config": True},
        description="optical-switch 'Protection Group' (PG)",
        default=None,
        alias="optical-switch",
    )


class Ne(YangBaseModel):
    """Top level entity of the model, represents the entire Network Element."""

    ne_id: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Unique identifier of the NE defined by the system.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-id",
    )
    ne_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="User assigned name for this NE.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-name",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": True}, description="User label.", min_length=0, max_length=256, default=None
    )
    ne_type: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Type of the NE.",
        min_length=0,
        max_length=64,
        default=None,
        alias="ne-type",
    )
    node_type: NodeTypeEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Node Type refers to the main function NE agent operates.",
        default=NodeTypeEnum.OADM,
        alias="node-type",
    )
    l0_mode_op: L0ModeOpEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Operation mode for Power Control and services.",
        default=L0ModeOpEnum.STANDARD,
        alias="l0-mode-op",
    )
    ne_vendor: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Vendor name of the NE.",
        min_length=0,
        max_length=64,
        default=None,
        alias="ne-vendor",
    )
    ne_site: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Name or CLLI of the site where this NE is located.",
        min_length=0,
        max_length=64,
        default=None,
        alias="ne-site",
    )
    ne_location: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Name of the location of this particular NE.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-location",
    )
    ne_sub_location: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Name of the secondary location of this particular NE.",
        min_length=0,
        max_length=256,
        default=None,
        alias="ne-sub-location",
    )
    clli: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Common Language Location Identifier (CLLI) is a 20-character standardized geographic\nidentifier that uniquely identifies the functional category of the equipment.",
        min_length=0,
        max_length=20,
        default=None,
    )
    node_controller_chassis_name: str | None = Field(
        json_schema_extra={"is_config": True},
        description="Configures the name of the node-controller chassis; only takes effect after\nthe database is cleared. Needs to be a number between 1 and 254.",
        min_length=0,
        max_length=64,
        default=None,
        alias="node-controller-chassis-name",
    )
    altitude: int | None = Field(json_schema_extra={"is_config": True}, description="Altitude of the NE.", default=None)
    latitude: Decimal64 | None = Field(
        json_schema_extra={"is_config": True}, description="Latitude of the NE.", ge=-90, le=90, default=None
    )
    longitude: Decimal64 | None = Field(
        json_schema_extra={"is_config": True}, description="Longitude of the NE.", ge=-180, le=180, default=None
    )
    equipment_discovery_ready: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Represents the equipment discovery state for the Node Controller chassis.\nIt will remain as 'false' until all equipment was discovered during startup.\nEquipment added after startup will not contribute to the update of this state.",
        default=False,
        alias="equipment-discovery-ready",
    )
    alarm_report_ready: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="Represents the alarm monitoring state for the entire NE.\nIt is 'true' if the alarm-report-ready flag of all chassis instances is 'true'.\nIt is 'false' otherwise.",
        default=False,
        alias="alarm-report-ready",
    )
    contact: str | None = Field(
        json_schema_extra={"is_config": True},
        description="The administrator contact information for the system.",
        min_length=0,
        max_length=128,
        default=None,
    )
    recover_mode: bool | None = Field(
        json_schema_extra={"is_config": False},
        description="A system is in recover-mode to represent an error state that requires manual intervention.\nSeveral specific sanity checks are done during system startup, and if any of them fail\nthe system will enter recover-mode.\n\nWhile in recover mode, the following happens:\n- the reason for the recover mode can be visualized in the ne recover-mode-reason attribute\n- a system-wide alarm RECOVER-MODE is raised\n- CLI sessions get an extra banner at login reminding the user the current system state\n- connection to existing line cards is severed, effectively keeping previous hardware configuration untouched\n- new configurations are accepted, but will not take effect until the recover mode is cleared\n\nRecover mode can be resolved in multiple ways:\n- simply confirming that current configuration is the desired one\n- restoring a valid Database backup\nIn all cases, the recover mode requires an explicit command to be cleared.\n\nUse command 'clear recover-mode' to confirm current configuration and return to normal system operation.\n\n(!) Warning: clearing the recover mode may have traffic impact; please confirm settings before this action.",
        default=True,
        alias="recover-mode",
    )
    original_recover_mode_reason: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Original reason for recover mode.\nDisplays the original recover mode reason, available only when current reason has changed.",
        min_length=0,
        max_length=256,
        default=None,
        alias="original-recover-mode-reason",
    )
    recover_mode_reason: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Reason for recover mode.\nAvailable only when ne is in recover mode.",
        min_length=0,
        max_length=256,
        default=None,
        alias="recover-mode-reason",
    )
    oper_state: OperStateEnum | None = Field(
        json_schema_extra={"is_config": False},
        description="The operational state of this object.",
        default=OperStateEnum.DISABLED,
        alias="oper-state",
    )
    avail_state: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Availability state of an entity.",
        default=None,
        alias="avail-state",
    )
    alarm_report_control: AlarmReportControlEnum | None = Field(
        json_schema_extra={"is_config": True},
        description="Controls the reporting of alarms for this particular object.",
        default=AlarmReportControlEnum.ALLOWED,
        alias="alarm-report-control",
    )
    equipment: Equipment | None = Field(
        json_schema_extra={"is_config": True},
        description="Container for all equipment related resources.",
        default=None,
    )
    facilities: Facilities | None = Field(
        json_schema_extra={"is_config": True},
        description="The top-level facility root node under which all other facilities are present.",
        default=None,
    )
    services: ServicesServices | None = Field(
        json_schema_extra={"is_config": True},
        description="Services of multiples types commissioned in this NE.",
        default=None,
    )
    system: SystemSystem | None = Field(
        json_schema_extra={"is_config": True}, description="System Configuration container", default=None
    )
    ne_function: NeFunction | None = Field(
        json_schema_extra={"is_config": True}, description="NE generic functions", default=None, alias="ne-function"
    )
    topology: Topology | None = Field(
        json_schema_extra={"is_config": True}, description="Topology information related with this NE.", default=None
    )
    system_capabilities: SystemCapabilities | None = Field(
        json_schema_extra={"is_config": False},
        description="Top level container for all capability information.\nThis data is read-only, and expected to be informative to the user\nregarding what are the system capabilities.\nThis information is static and independent on current configuration.\nCapabilities can be updated only:\n- with SW upgrade\n- with a dedicated capabilities file update (for specific cases only)",
        default=None,
        alias="system-capabilities",
    )
    protection: Protection | None = Field(
        json_schema_extra={"is_config": True},
        description="The top-level protection root node under which all other protection entities are present.",
        default=None,
    )


class IoaNetworkElementData(YangBaseModel):
    """Root data model for ioa-network-element"""

    ne: Ne | None = Field(
        json_schema_extra={"is_config": True},
        description="Top level entity of the model, represents the entire Network Element.",
        default=None,
        alias="ioa-network-element:ne",
    )


class ChangedBy(YangBaseModel):
    """Information regarding the agent that caused this change."""

    # Choice: server-or-user
    # Case: server
    server: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If present, the change was caused by the server.",
        default=None,
    )
    # Case: by-user
    user_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="User name that made the change",
        default=None,
        alias="user-name",
    )
    session_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Session ID that made the change",
        default=None,
        alias="session-id",
    )
    message_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Message ID that matches the request",
        default=None,
        alias="message-id",
    )
    request_info: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Metadata from the request that is propagated to the notifications.",
        default=None,
        alias="request-info",
    )


class DbChangeNotification(YangBaseModel):
    """Generated when the system detects that the <running> configuration datastore has changed.
    Contains both state and config changes.
    """

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
    changed_by: ChangedBy | None = Field(
        json_schema_extra={"is_config": None},
        description="Information regarding the agent that caused this change.",
        default=None,
        alias="changed-by",
    )
    change: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="Copy of the running datastore subset and state data that changed.\nThe following metadata is used in this content:\n- 'operation' attribute, used for containers and lists. May have values 'create' and 'delete',\nrepresenting that this node was created or deleted.\n- 'old-value' attribute, used for leaf and leaf-lists. Will contain the previous value of the\nattribute it refers to.\nThese two metadata attributes are qualified with the same namespace as the datastore itself, and\nare defined according with RFC7952.\n\nXML Example:\n<object operation='create'>\n...\n</object>\n<attribute old-value='x'>y</attribute>",
        default=None,
    )


class AuditNotification(YangBaseModel):
    """Contains configuration commands performed by users.
    Only sent for  successful commands that have impact on system configuration.
    """

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
    user_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="User name that made the change",
        default=None,
        alias="user-name",
    )
    session_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Session ID that made the change",
        default=None,
        alias="session-id",
    )
    session_type: SessionTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of the session that made the change.",
        default=None,
        alias="session-type",
    )
    message_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Message ID that associated with the request",
        default=None,
        alias="message-id",
    )
    commit_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Commit ID associated with the request",
        default=None,
        alias="commit-id",
    )
    request_info: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Metadata from the request that is propagated to the notifications.",
        default=None,
        alias="request-info",
    )
    command: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="Copy of the inputted command, using an abstract XML representation.\nEffectively, contains the command as if it was converted to NETCONF XML.",
        default=None,
    )
    original_command: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Contains original command, if applicable (e.g. for CLI commands).",
        default=None,
        alias="original-command",
    )
