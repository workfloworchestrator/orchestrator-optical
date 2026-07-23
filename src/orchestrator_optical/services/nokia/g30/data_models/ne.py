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

class EnableSwitchEnum(str, Enum):
    """Enumeration for EnableSwitchEnum
    
    Values:
      * enabled
      * disabled
    """

    ENABLED = "enabled"
    DISABLED = "disabled"

class SeverityLevelEnum(str, Enum):
    """Enumeration for SeverityLevelEnum
    
    Values:
      * not-applicable
      * critical
      * major
      * minor
      * not-alarmed
      * not-reported
      * cleared
    """

    NOT_APPLICABLE = "not-applicable"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    NOT_ALARMED = "not-alarmed"
    NOT_REPORTED = "not-reported"
    CLEARED = "cleared"

class AdminStatusEnum(str, Enum):
    """Enumeration for AdminStatusEnum
    
    Values:
      * up:  The resource is administratively permitted to perform services for its users. This is independent of its inherent operability, i.e. whether it is capable of providing service. 
      * down:  The resource is administratively prohibited from performing services for its users. The resource currently does not provide any service. 
      * up-no-alm:  The resource is administratively permitted to perform services for its users without alarm reported. This is independent of its inherent operability, i.e. whether it is capable of providing service. All alarm reported on this entity will be suppressed. 
    """

    UP = "up"
    DOWN = "down"
    UP_NO_ALM = "up-no-alm"

class OperStatusEnum(str, Enum):
    """Enumeration for OperStatusEnum
    
    Values:
      * up:  The resource is partially or fully operable and available for use. 
      * down:  The resource is totally inoperable and unable to provide service. 
    """

    UP = "up"
    DOWN = "down"

class EquipmentTypeEnum(str, Enum):
    """Enumeration for EquipmentTypeEnum
    
    Values:
      * empty: Empty slot/subslot.
      * Filled: Filled with not managed module.
      * Reserved: Occupied by a module on other slot/subslot.
      * Unrecognized: Unknown module present on the slot/subslot
      * not-applicable: Not applicable.
      * FAN: Fan card for system cooling.
      * PSU: Power supply unit card.
      * CHM1: Coherent Module of type I.
      * CHM2: Coherent Module of type II.
      * BFM: Blank Filler Module.
      * XTM2: 10G Muxponder Transport Module of type II
      * CHM1G: Coherent Module type I of Green version.
      * CHM1LH: Coherent Module type I of Long Haul
      * CHM2LH: Coherent Module type II of Long Haul
      * UTM2: Universal Transponder Muxponder
      * QSFP: Quad small form factor Pluggable.
      * CFP2: C form factor 2 pluggable
      * SFP+: small form factor Pluggable Plus
      * SFP: Small form-factor pluggable
      * CFP2-DCO: CFP2 - Digital Coherent Optics Module
      * OCC2: Optical carrier card of type II.
      * OMD96: Optical multiplex/demultiplex module for 96 channels.
      * PAOSCOFP2: Pre-amplifier OFP2 with OSC.
      * PABAOFP2: Pre-amplifier, booster amplfier OFP2.
      * PAIROFP2: Hight Power intermediate reach pre-amplifier OFP2 with OSC.
      * PALROFP2: High power long reach pre-amplifier OFP2 with OSC.
      * PAEROFP2: High power extended reach pre-amplifier OFP2 with OSC.
      * BAHOFP2: High power booster amplifier OFP2.
      * OMD48-S: Optical multiplex/demultiplex module for 48 channels of standard grid.
      * OMD48-O: Optical multiplex/demultiplex module for 48 channels of off grid.
      * TDCMOFP2: Tunable Dispersion Compensation Module OFP2.
      * BAUOFP2: Ultra-high power booster amplifier OFP2.
      * PAULROFP2: Ultra-high power long reach pre-amplifier OFP2.
      * OMD8B1OFP2: Optical multiplex/demultiplex OFP2 for 8 channels of band 1.
      * OMD8B2OFP2: Optical multiplex/demultiplex OFP2 for 8 channels of band 2.
      * OPSOFP2: Optical Protection Switch Module OFP2.
      * OTDROFP2: Optical Time Domain Reflectometer OFP2.
      * OCMOFP2: Optical Channel Monitor OFP2.
      * OPSPTOFP2: Optical Protection Switch Module OFP2 with Pilot Tone.
      * CHM2T: Coherent Module of Tera bps, 2-slot width.
      * FRCU: Replaceable Controller Unit.
      * CAD8OFP2: Optical Colorless Add Drop OFP2 for 8 channels.
      * CAD8EOFP2: Optical Colorless Add Drop OFP2 for 8 channels with expandable port.
      * OMD64: Optical multiplex/demultiplex module for 64 channels.
      * WS04SOFP2: 1x4 Wavelength Selector OFP2 with single WSS.
      * CAD16AOFP2: Colorless add/drop 1x16 fan out OFP2 with amplifier.
      * BAXOFP2: Booster amplifier OFP2 with extended gain range.
      * RD09SM: 1x9 degree Wavelength Selector with signal WSS, double amplfier and OSC
      * OMD48E: Optical multiplex/demultiplex module for 48 channels of Enclosured
      * DGE2M2OFP2: 2 channel Dynamic Gain Equalization with 2 channel Optical Channel Monitor OFP2
      * PBMTPP: Patch panel from MTP port to LC port
      * OMD64S: Optical multiplex/demultiplex module for 64 channels with shifted frequency by 12.5 GHz.
      * VIR-SIM: Virtual system interface module, Only wokring for the environment need report system IO port
    """

    EMPTY = "empty"
    FILLED = "Filled"
    RESERVED = "Reserved"
    UNRECOGNIZED = "Unrecognized"
    NOT_APPLICABLE = "not-applicable"
    FAN = "FAN"
    PSU = "PSU"
    CHM1 = "CHM1"
    CHM2 = "CHM2"
    BFM = "BFM"
    XTM2 = "XTM2"
    CHM1G = "CHM1G"
    CHM1LH = "CHM1LH"
    CHM2LH = "CHM2LH"
    UTM2 = "UTM2"
    QSFP = "QSFP"
    CFP2 = "CFP2"
    SFP_PLUS = "SFP+"
    SFP = "SFP"
    CFP2_DCO = "CFP2-DCO"
    OCC2 = "OCC2"
    OMD96 = "OMD96"
    PAOSCOFP2 = "PAOSCOFP2"
    PABAOFP2 = "PABAOFP2"
    PAIROFP2 = "PAIROFP2"
    PALROFP2 = "PALROFP2"
    PAEROFP2 = "PAEROFP2"
    BAHOFP2 = "BAHOFP2"
    OMD48_S = "OMD48-S"
    OMD48_O = "OMD48-O"
    TDCMOFP2 = "TDCMOFP2"
    BAUOFP2 = "BAUOFP2"
    PAULROFP2 = "PAULROFP2"
    OMD8B1OFP2 = "OMD8B1OFP2"
    OMD8B2OFP2 = "OMD8B2OFP2"
    OPSOFP2 = "OPSOFP2"
    OTDROFP2 = "OTDROFP2"
    OCMOFP2 = "OCMOFP2"
    OPSPTOFP2 = "OPSPTOFP2"
    CHM2T = "CHM2T"
    FRCU = "FRCU"
    CAD8OFP2 = "CAD8OFP2"
    CAD8EOFP2 = "CAD8EOFP2"
    OMD64 = "OMD64"
    WS04SOFP2 = "WS04SOFP2"
    CAD16AOFP2 = "CAD16AOFP2"
    BAXOFP2 = "BAXOFP2"
    RD09SM = "RD09SM"
    OMD48E = "OMD48E"
    DGE2M2OFP2 = "DGE2M2OFP2"
    PBMTPP = "PBMTPP"
    OMD64S = "OMD64S"
    VIR_SIM = "VIR-SIM"

class CardSubTypeEnum(str, Enum):
    """Enumeration for CardSubTypeEnum
    
    Values:
      * not-applicable: not-applicable.
      * MT: CHM2T DCI/Metro.
      * LH: CHM2T Long Haul .
      * SM: CHM2T Super Metro.
      * SMX: CHM2T XR Super Metro.
      * MTX: CHM2T XR Metro.
    """

    NOT_APPLICABLE = "not-applicable"
    MT = "MT"
    LH = "LH"
    SM = "SM"
    SMX = "SMX"
    MTX = "MTX"

class CardTypeEnum(str, Enum):
    """Enumeration for CardTypeEnum
    
    Values:
      * FAN: Fan card for system cooling.
      * PSU: Power supply unit card.
      * CHM1: Coherent Module of type I.
      * CHM2: Coherent Module of type II.
      * XTM2: 10G Muxponder Transport Module of type II
      * CHM1G: Coherent Module type I of Green version.
      * CHM1LH: Coherent Module type I of Long Haul
      * CHM2LH: Coherent Module type II of Long Haul
      * UTM2: Universal Transponder Muxponder
      * OCC2: Optical carrier card of type II.
      * OMD96: Optical multiplex/demultiplex module for 96 channels.
      * PAOSCOFP2: Pre-amplifier OFP2 with OSC.
      * PABAOFP2: Pre-amplifier, booster amplifier OFP2.
      * PAIROFP2: High Power intermediate reach pre-amplifier OFP2 with OSC.
      * PALROFP2: High power long reach pre-amplifier OFP2 with OSC.
      * PAEROFP2: High power extended reach pre-amplifier OFP2 with OSC.
      * BAHOFP2: High power booster amplifier OFP2.
      * OMD48-S: Optical multiplex/demultiplex module for 48 channels of standard grid.
      * OMD48-O: Optical multiplex/demultiplex module for 48 channels of off grid.
      * TDCMOFP2: Tunable Dispersion Compensation Module OFP2.
      * BAUOFP2: Ultra-high power booster amplifier OFP2.
      * PAULROFP2: Ultra-high power long reach pre-amplifier OFP2.
      * OMD8B1OFP2: Optical multiplex/demultiplex OFP2 for 8 channels of band 1.
      * OMD8B2OFP2: Optical multiplex/demultiplex OFP2 for 8 channels of band 2.
      * OPSOFP2: Optical Protection Switch Module OFP2.
      * OTDROFP2: Optical Time Domain Reflectometer OFP2.
      * OCMOFP2: Optical Channel Monitor OFP2.
      * OPSPTOFP2: Optical Protection Switch Module OFP2 with Pilot Tone.
      * CHM2T: Coherent Module of Tera bps, 2-slot width.
      * FRCU: Replaceable Controller Unit.
      * CAD8OFP2: Optical Colorless Add Drop OFP2 for 8 channels.
      * CAD8EOFP2: Optical Colorless Add Drop OFP2 for 8 channels with expandable port.
      * OMD64: Optical multiplex/demultiplex module for 64 channels.
      * WS04SOFP2: 1x4 Wavelength Selector OFP2 with single WSS.
      * CAD16AOFP2: Colorless add/drop 1x16 fan out OFP2 with amplifier.
      * BAXOFP2: Booster amplifier OFP2 with extended gain range.
      * RD09SM: 1x9 degree Wavelength Selector with signal WSS, double amplfier and OSC
      * OMD48E: Optical multiplex/demultiplex module for 48 channels of Enclosured
      * DGE2M2OFP2: 2 channel Dynamic Gain Equalization with 2 channel Optical Channel Monitor OFP2
      * PBMTPP: Patch panel from MTP port to LC port
      * OMD64S: Optical multiplex/demultiplex module for 64 channels with shifted frequency by 12.5 GHz.
      * VIR-SIM: Virtual system interface module, Only wokring for the environment need report system IO port
    """

    FAN = "FAN"
    PSU = "PSU"
    CHM1 = "CHM1"
    CHM2 = "CHM2"
    XTM2 = "XTM2"
    CHM1G = "CHM1G"
    CHM1LH = "CHM1LH"
    CHM2LH = "CHM2LH"
    UTM2 = "UTM2"
    OCC2 = "OCC2"
    OMD96 = "OMD96"
    PAOSCOFP2 = "PAOSCOFP2"
    PABAOFP2 = "PABAOFP2"
    PAIROFP2 = "PAIROFP2"
    PALROFP2 = "PALROFP2"
    PAEROFP2 = "PAEROFP2"
    BAHOFP2 = "BAHOFP2"
    OMD48_S = "OMD48-S"
    OMD48_O = "OMD48-O"
    TDCMOFP2 = "TDCMOFP2"
    BAUOFP2 = "BAUOFP2"
    PAULROFP2 = "PAULROFP2"
    OMD8B1OFP2 = "OMD8B1OFP2"
    OMD8B2OFP2 = "OMD8B2OFP2"
    OPSOFP2 = "OPSOFP2"
    OTDROFP2 = "OTDROFP2"
    OCMOFP2 = "OCMOFP2"
    OPSPTOFP2 = "OPSPTOFP2"
    CHM2T = "CHM2T"
    FRCU = "FRCU"
    CAD8OFP2 = "CAD8OFP2"
    CAD8EOFP2 = "CAD8EOFP2"
    OMD64 = "OMD64"
    WS04SOFP2 = "WS04SOFP2"
    CAD16AOFP2 = "CAD16AOFP2"
    BAXOFP2 = "BAXOFP2"
    RD09SM = "RD09SM"
    OMD48E = "OMD48E"
    DGE2M2OFP2 = "DGE2M2OFP2"
    PBMTPP = "PBMTPP"
    OMD64S = "OMD64S"
    VIR_SIM = "VIR-SIM"

class CardModeEnum(str, Enum):
    """Enumeration for CardModeEnum
    
    Values:
      * not-applicable: Not applicable to the entity.
      * normal: Specify the card to be normal operation mode.
      * regen: Specify the card to be regeneration operation mode.
      * mix-function: Specify the card to be mix function mode
      * grey-muxponder: 100G grey muxponder mode on port 3 and 4 for UTM2
    """

    NOT_APPLICABLE = "not-applicable"
    NORMAL = "normal"
    REGEN = "regen"
    MIX_FUNCTION = "mix-function"
    GREY_MUXPONDER = "grey-muxponder"

class YesNoEnum(str, Enum):
    """Enumeration for YesNoEnum
    
    Values:
      * yes: Yes
      * no: No
    """

    YES = "yes"
    NO = "no"

class SwitchingTypeEnum(str, Enum):
    """Enumeration for SwitchingTypeEnum
    
    Values:
      * otn
      * tdm
      * optical
      * packet
      * optical-router
      * amplifier
      * omd
      * cad
      * not-applicable
      * otn-transponder
    """

    OTN = "otn"
    TDM = "tdm"
    OPTICAL = "optical"
    PACKET = "packet"
    OPTICAL_ROUTER = "optical-router"
    AMPLIFIER = "amplifier"
    OMD = "omd"
    CAD = "cad"
    NOT_APPLICABLE = "not-applicable"
    OTN_TRANSPONDER = "otn-transponder"

class TemperatureDetailsItem(YangBaseModel):
    """The detailed information of temperature in each monitoring-point of current module"""

    monitoring_point: str = Field(json_schema_extra={"is_config": False}, description="The point of temperature monitoring. It could be the sensor or chip internal.", alias="monitoring-point")
    temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Temperature at the monitoring point.", default=None)
    temperature_range_low: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The lowest temperature threshold of this monitoring point in working mode.", default=None, alias="temperature-range-low")
    temperature_range_high: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The highest temperature threshold of this monitoring point in working mode.", default=None, alias="temperature-range-high")

class PerCoreUtilizationItem(YangBaseModel):
    """Each CPU core's utilization"""

    core_index: int = Field(json_schema_extra={"is_config": False}, description="The index of the CPU core", ge=0, alias="core-index")
    utilization: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The utilization of current CPU core", ge=0, le=100.0, default=None)

class CpuState(YangBaseModel):
    """The module with CPU's utilization states"""

    cpu_total_utilization: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The total CPUs' utilization", ge=0, le=100.0, default=None, alias="cpu-total-utilization")
    per_core_utilization: RestconfList[PerCoreUtilizationItem] | None = Field(json_schema_extra={"is_config": False}, description="Each CPU core's utilization", default=None, alias="per-core-utilization")

class MemoryState(YangBaseModel):
    """For module that have associated memory, these values
    report information about available and utilized memory
    """

    available: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="The available memory physically installed, or logically allocated to the module.", ge=0, le=18446744073709551615, default=None)
    utilized: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="The memory currently in use by processes running on the module, not considering reserved memory that is not available for use.", ge=0, le=18446744073709551615, default=None)

class OtdrStateEnum(str, Enum):
    """Enumeration for OtdrStateEnum
    
    Values:
      * not-available: Status is not available
      * idle: Idle status
      * measuring: Measurement is ongoing.
      * finished: Measurement has completed
      * fail: Measurement has failed
    """

    NOT_AVAILABLE = "not-available"
    IDLE = "idle"
    MEASURING = "measuring"
    FINISHED = "finished"
    FAIL = "fail"

class OtdrLaserStatusEnum(str, Enum):
    """Enumeration for OtdrLaserStatusEnum
    
    Values:
      * not-available: Status is not available.
      * enabled: Laser enabled.
      * disabled: Laser disabled.
    """

    NOT_AVAILABLE = "not-available"
    ENABLED = "enabled"
    DISABLED = "disabled"

class Otdr(YangBaseModel):
    """Container of OTDR."""

    otdr_state: OtdrStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the current status of the OTDR.", default=OtdrStateEnum.NOT_AVAILABLE, alias="otdr-state")
    otdr_measurement_time: int | None = Field(json_schema_extra={"is_config": False}, description="Indicating the time remaining in current measurement running.", ge=0, default=0, alias="otdr-measurement-time")
    otdr_error: str | None = Field(json_schema_extra={"is_config": False}, description="Error message produced when the measurement ends with error.", min_length=0, max_length=64, default=None, alias="otdr-error")
    otdr_laser_status: OtdrLaserStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the current status of the OTDR laser.", default=OtdrLaserStatusEnum.NOT_AVAILABLE, alias="otdr-laser-status")
    otdr_measurement_port: int | None = Field(json_schema_extra={"is_config": False}, description="0 indicates that the card is not measuring any port;\nnon-zero indicates the OTDR port number where a measurement is currently taking place.", ge=0, default=0, alias="otdr-measurement-port")
    otdr_file_name: str | None = Field(json_schema_extra={"is_config": True}, description="Indicating the file name of the current OTDR test result.", min_length=0, max_length=256, default=None)
    otdr_file_prefix: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9][a-zA-Z0-9\\-_\\.]*)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Indicating the file name prefix of the current OTDR test result.", min_length=0, max_length=64, default=None, alias="otdr-file-prefix")

class PluggableTypeEnum(str, Enum):
    """Enumeration for PluggableTypeEnum
    
    Values:
      * non-pluggable: The port is not pluggable.
      * QSFP: Quad Small Form-factor Pluggable.
      * CFP2: C form-factor pluggable of type 2.
      * SFP+: Enhanced small form-factor pluggable.
      * SFP: Small form-factor pluggable
      * CFP2-DCO: CFP2 - Digital Coherent Optics Module
    """

    NON_PLUGGABLE = "non-pluggable"
    QSFP = "QSFP"
    CFP2 = "CFP2"
    SFP_PLUS = "SFP+"
    SFP = "SFP"
    CFP2_DCO = "CFP2-DCO"

class OpticalPowerLaneItem(YangBaseModel):
    """List: optical-power-lane"""

    lane_id: int = Field(json_schema_extra={"is_config": False}, description="The physical lane index for optical pluggable", ge=0, alias="lane-id")
    rx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Received optical power", default=None, alias="rx-optical-power")
    tx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power", default=None, alias="tx-optical-power")

class TypeOfDirectionEnum(str, Enum):
    """Enumeration for TypeOfDirectionEnum
    
    Values:
      * not-applicable: Not applicable or unknown.
      * tx: Tx direction.
      * rx: Rx direction.
      * rxtx: Both Rx and Tx directions.
    """

    NOT_APPLICABLE = "not-applicable"
    TX = "tx"
    RX = "rx"
    RXTX = "rxtx"

class PortTypeEnum(str, Enum):
    """Enumeration for PortTypeEnum
    
    Values:
      * client: Client port on Transponder.
      * line: Line port on Transponder.
      * client-subport: Client subport on Transponder.
      * optical: Optical port on optical module.
      * otdr: OTDR port on optical module.
      * optical-nomon: Optical port without monitor on optical module.
      * ocm: Port on OCM.
      * osc: Port for OSC
      * mgmt-eth: management Ethernet port
    """

    CLIENT = "client"
    LINE = "line"
    CLIENT_SUBPORT = "client-subport"
    OPTICAL = "optical"
    OTDR = "otdr"
    OPTICAL_NOMON = "optical-nomon"
    OCM = "ocm"
    OSC = "osc"
    MGMT_ETH = "mgmt-eth"

class PortModeEnum(str, Enum):
    """Enumeration for PortModeEnum
    
    Values:
      * not-applicable: No service mode
      * 10GBE: IEEE802.3ae 10 gigabits per second LAN Ethernet signal
      * 40GBE: IEEE802.3ae 40 gigabits per second Ethernet signal
      * 100GBE: IEEE802.3ae 100 gigabits per second Ethernet signal
      * subport: The logical port for break down channel signal type
      * QPSK_100G: 100G rate class och-os signal with DP-QPSK modulation format
      * 8QAM_300G: 150G rate class otsi signal with DP-8QAM modulation format
      * 16QAM_200G: 200G rate class och-os signal with DP-16QAM modulation format
      * FC16G: 16 gigabits per second rates Fiber Channel signal
      * FC8G: 8 gigabits per second rates Fiber Channel signal
      * OTU4: ITUT G.709 112 gigabits per second Optical channel Transport Unit
      * OTU2: ITUT G.709 10.70 gigabits per second Optical channel Transport Unit
      * OTU2e: ITUT G.709 11.09 gigabits per second Optical channel Transport Unit
      * OC192: 9.95 gigabits per second SONET signal
      * STM64: 9.95 gigabits per second SDH signal
      * OCHOS_OTU2: 10G rate class och-os signal with NRZ modulation format
      * OCHOS_OTU2e: 11G rate class och-os signal with NRZ modulation format
      * 8QAM_200G: 200G rate class och-os signal with DP-8QAM modulation format
      * 10GWAN_SONET: IEEE802.3ae 10 gigabits per second WAN Ethernet signal with SOENT overhead
      * 10GWAN_SDH: IEEE802.3ae 10 gigabits per second WAN Ethernet signal with SDH overhead
      * 64QAM_600G: 600G rate class och-os signal with DP-64QAM modulation format
      * 400GBE: IEEE802.3ae 400 gigabits per second Ethernet signal
      * SPQPSK_100G: 100G rate class och-os signal with DP-SPQPSK modulation format
      * SPQPSK_QPSK_100G: 100G rate class och-os signal with DP-SPQPSK-QPSK modulation format
      * QPSK_200G: 200G rate class och-os signal with DP-QPSK modulation format
      * SP16QAM_200G: 200G rate class och-os signal with DP-SP16QAM modulation format
      * 32QAM_200G: 200G rate class och-os signal with DP-32QAM modulation format
      * QPSK_SP16QAM_200G: 200G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * 16QAM_300G: 300G rate class och-os signal with DP-16QAM modulation format
      * SP16QAM_300G: 300G rate class och-os signal with DP-SP16QAM modulation format
      * 32QAM_300G: 300G rate class och-os signal with DP-32QAM modulation format
      * 64QAM_300G: 300G rate class och-os signal with DP-64QAM modulation format
      * SP16QAM_16QAM_300G: 300G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 16QAM_400G: 400G rate class och-os signal with DP-16QAM modulation format
      * 32QAM_400G: 400G rate class och-os signal with DP-32QAM modulation format
      * 64QAM_400G: 400G rate class och-os signal with DP-64QAM modulation format
      * 16QAM_32QAM_400G: 400G rate class och-os signal with DP-16QAM-32QAM modulation format
      * 32QAM_500G: 500G rate class och-os signal with DP-32QAM modulation format
      * 64QAM_500G: 500G rate class och-os signal with DP-64QAM modulation format
      * 32QAM_64QAM_500G: 500G rate class och-os signal with DP-32QAM-64QAM modulation format
      * OTU4_TRANSPARENT: ITUT G.709 112 gigabits per second Optical channel Transport Unit with transparent mode
      * QPSK_100G_TRANSPARENT: 100G rate class och-os signal with DP-QPSK modulation format and transparent mode
      * SP16QAM_16QAM_200G: 200G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 32QAM_64QAM_600G: 600G rate class och-os signal with DP-32QAM-64QAM modulation format
      * 1GBE: IEEE802.3ae 1 gigabits per second LAN Ethernet signal
      * OC48: 2.5 gigabits per second SONET signal
      * STM16: 2.5 gigabits per second SDH signal
      * SP16QAM_300G_C: couple 2*150G rate class och-os signal with DP-SP16QAM modulation format
      * QPSK_SP16QAM_300G_C: couple 2*150G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * 16QAM_32QAM_500G_C: couple 2*250G rate class och-os signal with DP-16QAM-32QAM modulation format
      * 16QAM_500G_C: couple 2*250G rate class och-os signal with DP-16QAM modulation format
      * SP16QAM_500G_C: couple 2*250G rate class och-os signal with DP-SP16QAM modulation format
      * QPSK_SP16QAM_500G_C: couple 2*250G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * 32QAM_64QAM_700G_C: couple 2*350G rate class och-os signal with DP-32QAM-64QAM modulation format
      * 16QAM_700G_C: couple 2*350G rate class och-os signal with DP-16QAM modulation format
      * SP16QAM_16QAM_700G_C: couple 2*350G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 32QAM_900G_C: couple 2*450G rate class och-os signal with DP-32QAM modulation format
      * 16QAM_32QAM_900G_C: couple 2*450G rate class och-os signal with DP-16QAM-32QAM modulation format
      * 32QAM_64QAM_1100G_C: couple 2*550G rate class och-os signal with DP-32QAM-64QAM modulation format
      * SPQPSK_QPSK_200G: 200G rate class och-os signal with DP-SPQPSK-QPSK modulation format
      * QPSK_SP16QAM_300G: 300G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * SP16QAM_16QAM_400G: 400G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 16QAM_32QAM_500G: 500G rate class och-os signal with DP-16QAM-32QAM modulation format
      * FC1G: 1 gigabits per second rates Fiber Channel signal
      * FC4G: 4 gigabits per second rates Fiber Channel signal
    """

    NOT_APPLICABLE = "not-applicable"
    _10GBE = "10GBE"
    _40GBE = "40GBE"
    _100GBE = "100GBE"
    SUBPORT = "subport"
    QPSK_100G = "QPSK_100G"
    _8QAM_300G = "8QAM_300G"
    _16QAM_200G = "16QAM_200G"
    FC16G = "FC16G"
    FC8G = "FC8G"
    OTU4 = "OTU4"
    OTU2 = "OTU2"
    OTU2E = "OTU2e"
    OC192 = "OC192"
    STM64 = "STM64"
    OCHOS_OTU2 = "OCHOS_OTU2"
    OCHOS_OTU2E = "OCHOS_OTU2e"
    _8QAM_200G = "8QAM_200G"
    _10GWAN_SONET = "10GWAN_SONET"
    _10GWAN_SDH = "10GWAN_SDH"
    _64QAM_600G = "64QAM_600G"
    _400GBE = "400GBE"
    SPQPSK_100G = "SPQPSK_100G"
    SPQPSK_QPSK_100G = "SPQPSK_QPSK_100G"
    QPSK_200G = "QPSK_200G"
    SP16QAM_200G = "SP16QAM_200G"
    _32QAM_200G = "32QAM_200G"
    QPSK_SP16QAM_200G = "QPSK_SP16QAM_200G"
    _16QAM_300G = "16QAM_300G"
    SP16QAM_300G = "SP16QAM_300G"
    _32QAM_300G = "32QAM_300G"
    _64QAM_300G = "64QAM_300G"
    SP16QAM_16QAM_300G = "SP16QAM_16QAM_300G"
    _16QAM_400G = "16QAM_400G"
    _32QAM_400G = "32QAM_400G"
    _64QAM_400G = "64QAM_400G"
    _16QAM_32QAM_400G = "16QAM_32QAM_400G"
    _32QAM_500G = "32QAM_500G"
    _64QAM_500G = "64QAM_500G"
    _32QAM_64QAM_500G = "32QAM_64QAM_500G"
    OTU4_TRANSPARENT = "OTU4_TRANSPARENT"
    QPSK_100G_TRANSPARENT = "QPSK_100G_TRANSPARENT"
    SP16QAM_16QAM_200G = "SP16QAM_16QAM_200G"
    _32QAM_64QAM_600G = "32QAM_64QAM_600G"
    _1GBE = "1GBE"
    OC48 = "OC48"
    STM16 = "STM16"
    SP16QAM_300G_C = "SP16QAM_300G_C"
    QPSK_SP16QAM_300G_C = "QPSK_SP16QAM_300G_C"
    _16QAM_32QAM_500G_C = "16QAM_32QAM_500G_C"
    _16QAM_500G_C = "16QAM_500G_C"
    SP16QAM_500G_C = "SP16QAM_500G_C"
    QPSK_SP16QAM_500G_C = "QPSK_SP16QAM_500G_C"
    _32QAM_64QAM_700G_C = "32QAM_64QAM_700G_C"
    _16QAM_700G_C = "16QAM_700G_C"
    SP16QAM_16QAM_700G_C = "SP16QAM_16QAM_700G_C"
    _32QAM_900G_C = "32QAM_900G_C"
    _16QAM_32QAM_900G_C = "16QAM_32QAM_900G_C"
    _32QAM_64QAM_1100G_C = "32QAM_64QAM_1100G_C"
    SPQPSK_QPSK_200G = "SPQPSK_QPSK_200G"
    QPSK_SP16QAM_300G = "QPSK_SP16QAM_300G"
    SP16QAM_16QAM_400G = "SP16QAM_16QAM_400G"
    _16QAM_32QAM_500G = "16QAM_32QAM_500G"
    FC1G = "FC1G"
    FC4G = "FC4G"

class ArcConfigEnum(str, Enum):
    """Enumeration for ArcConfigEnum
    
    Values:
      * alm: Alarm is reported
      * nalm-qi: Not Alarmed - Qualified Inhibit
      * nalm: Not Alarmed
    """

    ALM = "alm"
    NALM_QI = "nalm-qi"
    NALM = "nalm"

class ArcSubStateEnum(str, Enum):
    """Enumeration for ArcSubStateEnum
    
    Values:
      * not-applicable
      * nalm-cd: Alarm is not reported - hold off counting down
      * nalm-nr: Alarm is not reported - Not ready
    """

    NOT_APPLICABLE = "not-applicable"
    NALM_CD = "nalm-cd"
    NALM_NR = "nalm-nr"

class EthFecEnum(str, Enum):
    """Enumeration for EthFecEnum
    
    Values:
      * enabled: FEC is enabled
      * disabled: FEC is disabled
      * auto: System will automatically decide FEC type of the ethernet interface.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"
    AUTO = "auto"

class MappingModeEnum(str, Enum):
    """Enumeration for MappingModeEnum
    
    Values:
      * not-applicable: No mapping
      * GMP: Generic Mapping Procedure
      * GFP-F: Generic Framing Procedure - Framed
      * 40GBMP-ODU2E: Bit-synchronous Mapping Procedure for 40G in 4xODU2e
      * PREAMBLE: Generic Framing Procedure – Framed with Preamble Transparency
      * BMP-FixedStuff: Bit-synchronous Mapping Procedure with Fixed Stuff
      * BMP: Bit-synchronous Mapping Procedure
      * AMP: Asynchronous Mapping Procedure
      * TTT_GMP: Timing Transparent Transcoding Generic Mapping Procedure 
    """

    NOT_APPLICABLE = "not-applicable"
    GMP = "GMP"
    GFP_F = "GFP-F"
    _40GBMP_ODU2E = "40GBMP-ODU2E"
    PREAMBLE = "PREAMBLE"
    BMP_FIXEDSTUFF = "BMP-FixedStuff"
    BMP = "BMP"
    AMP = "AMP"
    TTT_GMP = "TTT_GMP"

class LoopbackTypeEnum(str, Enum):
    """Enumeration for LoopbackTypeEnum
    
    Values:
      * none
      * terminal
      * facility
    """

    NONE = "none"
    TERMINAL = "terminal"
    FACILITY = "facility"

class TestSignalTypeEnum(str, Enum):
    """Enumeration for TestSignalTypeEnum
    
    Values:
      * NONE: Testing signal type is not specified
      * PRBS: Testing signal type - pseudorandom binary sequence
      * IDLE: Testing signal type - idle signal of PCS layer
    """

    NONE = "NONE"
    PRBS = "PRBS"
    IDLE = "IDLE"

class TestSignalConfigEnum(str, Enum):
    """Enumeration for TestSignalConfigEnum
    
    Values:
      * NONE: Testing signal disabled
      * RXTX: Enable testing signals at both Rx and Tx directions
    """

    NONE = "NONE"
    RXTX = "RXTX"

class PrbsSyncEnum(str, Enum):
    """Enumeration for PrbsSyncEnum
    
    Values:
      * not-applicable
      * in-sync
      * out-sync
      * err-sync
    """

    NOT_APPLICABLE = "not-applicable"
    IN_SYNC = "in-sync"
    OUT_SYNC = "out-sync"
    ERR_SYNC = "err-sync"

class TestSignalFacilityStatus(YangBaseModel):
    """Test signal status for current facility."""

    prbs_sync: PrbsSyncEnum | None = Field(json_schema_extra={"is_config": False}, description="The test result of PRBS Synchronization", default=PrbsSyncEnum.NOT_APPLICABLE, alias="prbs-sync")
    test_time_duration: int | None = Field(json_schema_extra={"is_config": False}, description="The time duration of signal test", ge=0, default=None, alias="test-time-duration")
    prbs_bit_error_count: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="The counting of bit error by PRBS Synchronization", ge=0, le=18446744073709551615, default=None, alias="prbs-bit-error-count")

class ManagedByEnum(str, Enum):
    """Enumeration for ManagedByEnum
    
    Values:
      * system
      * user
    """

    SYSTEM = "system"
    USER = "user"

class LldpStatusIfEnum(str, Enum):
    """Enumeration for LldpStatusIfEnum
    
    Values:
      * not-applicable
      * rxonly
      * txandrx
      * disabled
    """

    NOT_APPLICABLE = "not-applicable"
    RXONLY = "rxonly"
    TXANDRX = "txandrx"
    DISABLED = "disabled"

class RemoteChassisIdSubtypeEnum(str, Enum):
    """Enumeration for RemoteChassisIdSubtypeEnum
    
    Values:
      * chassisComponent
      * interfaceAlias
      * portComponent
      * macAddress
      * networkAddress
      * interfaceName
      * local
    """

    CHASSISCOMPONENT = "chassisComponent"
    INTERFACEALIAS = "interfaceAlias"
    PORTCOMPONENT = "portComponent"
    MACADDRESS = "macAddress"
    NETWORKADDRESS = "networkAddress"
    INTERFACENAME = "interfaceName"
    LOCAL = "local"

class RemotePortIdSubtypeEnum(str, Enum):
    """Enumeration for RemotePortIdSubtypeEnum
    
    Values:
      * interfaceAlias
      * portComponent
      * macAddress
      * networkAddress
      * interfaceName
      * agentCircuitId
      * local
    """

    INTERFACEALIAS = "interfaceAlias"
    PORTCOMPONENT = "portComponent"
    MACADDRESS = "macAddress"
    NETWORKADDRESS = "networkAddress"
    INTERFACENAME = "interfaceName"
    AGENTCIRCUITID = "agentCircuitId"
    LOCAL = "local"

class AddressFamilyEnum(str, Enum):
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

class RemoteManAddressesItem(YangBaseModel):
    """List of management addresses of LLDP neighbor.
    man:managment, remote management addresses
    """

    remote_man_addr_subtype: int = Field(json_schema_extra={"is_config": False}, description="The type of management address identifier encoding used in\nthe associated 'lldpLocManagmentAddr' object.", ge=0, alias="remote-man-addr-subtype")
    remote_man_addr: str = Field(json_schema_extra={"is_config": False}, description="The string value used to identify the management address\ncomponent associated with the remote system.  The purpose\nof this address is to contact the management entity.\nman: management\naddr: address", min_length=0, max_length=62, alias="remote-man-addr")
    remote_man_addr_if_subtype: int | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the basis of a particular type of\ninterface associated with the management address.\n\nThe enumeration 'unknown(1)' represents the case where the\ninterface is not known.\n\nThe enumeration 'ifIndex(2)' represents interface identifier\nbased on the ifIndex MIB object.\n\nThe enumeration 'systemPortNumber(3)' represents interface\nidentifier based on the system port numbering convention.\nman: management\naddr: address", ge=0, default=None, alias="remote-man-addr-if-subtype")
    remote_man_addr_if_id: int | None = Field(json_schema_extra={"is_config": False}, description="The integer value used to identify the interface number\nregarding the management address component associated with\nthe remote system.\nman: management\naddr: address", ge=0, default=None, alias="remote-man-addr-if-id")
    remote_man_addr_oid: str | None = Field(json_schema_extra={"is_config": False}, description="The OID value used to identify the type of hardware component\nor protocol entity associated with the management address\nadvertised by the remote system agent.\nman: management\naddr: address\noid: object identifier", min_length=0, max_length=128, default=None, alias="remote-man-addr-oid")
    or_remote_man_addr_subtype: AddressFamilyEnum | None = Field(json_schema_extra={"is_config": False}, description="remote neighbour Management Address Subtype Enumeration", default=None, alias="or-remote-man-addr-subtype")

class LldpRemoteSystemItem(YangBaseModel):
    """List of LLDP neighbors."""

    lldp_remote_index: int = Field(json_schema_extra={"is_config": True}, description="This attribute represents an arbitrary local integer value used\nby this agent to identify a particular connection instance,\nunique only for the indicated remote system.", ge=0, alias="lldp-remote-index")
    remote_chassis_id_subtype: RemoteChassisIdSubtypeEnum | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the source of a chassis identifier.\n\nThe enumeration 'chassisComponent(1)' represents a chassis\nidentifier based on the value of entPhysicalAlias object\n(defined in IETF RFC 2737) for a chassis component (i.e.,\nan entPhysicalClass value of 'chassis(3)').\n\nThe enumeration 'interfaceAlias(2)' represents a chassis\nidentifier based on the value of ifAlias object (defined in\nIETF RFC 2863) for an interface on the containing chassis.\n\nThe enumeration 'portComponent(3)' represents a chassis\nidentifier based on the value of entPhysicalAlias object\n(defined in IETF RFC 2737) for a port or backplane\ncomponent (i.e., entPhysicalClass value of 'port(10)' or\n'backplane(4)'), within the containing chassis.\n\nThe enumeration 'macAddress(4)' represents a chassis\nidentifier based on the value of a unicast source address\n(encoded in network byte order and IEEE 802.3 canonical bit\norder), of a port on the containing chassis as defined in\nIEEE Std 802-2001.\n\nThe enumeration 'networkAddress(5)' represents a chassis\nidentifier based on a network address, associated with\na particular chassis.  The encoded address is actually\ncomposed of two fields.  The first field is a single octet,\nrepresenting the IANA AddressFamilyNumbers value for the\nspecific address type, and the second field is the network\naddress value.\n\nThe enumeration 'interfaceName(6)' represents a chassis\nidentifier based on the value of ifName object (defined in\nIETF RFC 2863) for an interface on the containing chassis.\n\nThe enumeration 'local(7)' represents a chassis identifier\nbased on a locally defined value.", default=None, alias="remote-chassis-id-subtype")
    remote_chassis_id: str | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the format of a chassis identifier string.\nObjects of this type are always used with an associated\nLldpChassisIdSubtype object, which identifies the format of\nthe particular LldpChassisId object instance.\n\nIf the associated LldpChassisIdSubtype object has a value of\n'chassisComponent(1)', then the octet string identifies\na particular instance of the entPhysicalAlias object\n(defined in IETF RFC 2737) for a chassis component (i.e.,\nan entPhysicalClass value of 'chassis(3)').\n\nIf the associated LldpChassisIdSubtype object has a value\nof 'interfaceAlias(2)', then the octet string identifies\na particular instance of the ifAlias object (defined in\nIETF RFC 2863) for an interface on the containing chassis.\nIf the particular ifAlias object does not contain any values,\nanother chassis identifier type should be used.\n\nIf the associated LldpChassisIdSubtype object has a value\nof 'portComponent(3)', then the octet string identifies a\nparticular instance of the entPhysicalAlias object (defined\nin IETF RFC 2737) for a port or backplane component within\nthe containing chassis.\n\nIf the associated LldpChassisIdSubtype object has a value of\n'macAddress(4)', then this string identifies a particular\nunicast source address (encoded in network byte order and\nIEEE 802.3 canonical bit order), of a port on the containing\nchassis as defined in IEEE Std 802-2001.\n\nIf the associated LldpChassisIdSubtype object has a value of\n'networkAddress(5)', then this string identifies a particular\nnetwork address, encoded in network byte order, associated\nwith one or more ports on the containing chassis.  The first\noctet contains the IANA Address Family Numbers enumeration\nvalue for the specific address type, and octets 2 through\nN contain the network address value in network byte order.\n\nIf the associated LldpChassisIdSubtype object has a value\nof 'interfaceName(6)', then the octet string identifies\na particular instance of the ifName object (defined in\nIETF RFC 2863) for an interface on the containing chassis.\nIf the particular ifName object does not contain any values,\nanother chassis identifier type should be used.\n\nIf the associated LldpChassisIdSubtype object has a value of\n'local(7)', then this string identifies a locally assigned\nChassis ID.", min_length=0, max_length=255, default=None, alias="remote-chassis-id")
    remote_port_id_subtype: RemotePortIdSubtypeEnum | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the format of a port identifier string.\nObjects of this type are always used with an associated\nLldpPortIdSubtype object, which identifies the format of the\nparticular LldpPortId object instance.\n\nIf the associated LldpPortIdSubtype object has a value of\n'interfaceAlias(1)', then the octet string identifies a\nparticular instance of the ifAlias object (defined in IETF\nRFC 2863).  If the particular ifAlias object does not contain\nany values, another port identifier type should be used.\n\nIf the associated LldpPortIdSubtype object has a value of\n'portComponent(2)', then the octet string identifies a\nparticular instance of the entPhysicalAlias object (defined\nin IETF RFC 2737) for a port or backplane component.\n\nIf the associated LldpPortIdSubtype object has a value of\n'macAddress(3)', then this string identifies a particular\nunicast source address (encoded in network byte order\nand IEEE 802.3 canonical bit order) associated with the port\n(IEEE Std 802-2001).\n\nIf the associated LldpPortIdSubtype object has a value of\n'networkAddress(4)', then this string identifies a network\naddress associated with the port.  The first octet contains\nthe IANA AddressFamilyNumbers enumeration value for the\nspecific address type, and octets 2 through N contain the\nnetworkAddress address value in network byte order.\n\nIf the associated LldpPortIdSubtype object has a value of\n'interfaceName(5)', then the octet string identifies a\nparticular instance of the ifName object (defined in IETF\nRFC 2863).  If the particular ifName object does not contain\nany values, another port identifier type should be used.\n\nIf the associated LldpPortIdSubtype object has a value of\n'agentCircuitId(6)', then this string identifies an agent-local\nidentifier of the circuit (defined in RFC 3046).\n\nIf the associated LldpPortIdSubtype object has a value of\n'local(7)', then this string identifies a locally\nassigned port ID.", default=None, alias="remote-port-id-subtype")
    remote_port_id: str | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the format of a port identifier string.\nObjects of this type are always used with an associated\nLldpPortIdSubtype object, which identifies the format of the\nparticular LldpPortId object instance.\n\nIf the associated LldpPortIdSubtype object has a value of\n'interfaceAlias(1)', then the octet string identifies a\nparticular instance of the ifAlias object (defined in IETF\nRFC 2863).  If the particular ifAlias object does not contain\nany values, another port identifier type should be used.\n\nIf the associated LldpPortIdSubtype object has a value of\n'portComponent(2)', then the octet string identifies a\nparticular instance of the entPhysicalAlias object (defined\nin IETF RFC 2737) for a port or backplane component.\n\nIf the associated LldpPortIdSubtype object has a value of\n'macAddress(3)', then this string identifies a particular\nunicast source address (encoded in network byte order\nand IEEE 802.3 canonical bit order) associated with the port\n(IEEE Std 802-2001).\n\nIf the associated LldpPortIdSubtype object has a value of\n'networkAddress(4)', then this string identifies a network\naddress associated with the port.  The first octet contains\nthe IANA AddressFamilyNumbers enumeration value for the\nspecific address type, and octets 2 through N contain the\nnetworkAddress address value in network byte order.\n\nIf the associated LldpPortIdSubtype object has a value of\n'interfaceName(5)', then the octet string identifies a\nparticular instance of the ifName object (defined in IETF\nRFC 2863).  If the particular ifName object does not contain\nany values, another port identifier type should be used.\n\nIf the associated LldpPortIdSubtype object has a value of\n'agentCircuitId(6)', then this string identifies an agent-local\nidentifier of the circuit (defined in RFC 3046).\n\nIf the associated LldpPortIdSubtype object has a value of\n'local(7)', then this string identifies a locally\nassigned port ID.", min_length=0, max_length=255, default=None, alias="remote-port-id")
    remote_port_desc: str | None = Field(json_schema_extra={"is_config": False}, description="The string value used to identify the description of\nthe given port associated with the remote system.", min_length=0, max_length=255, default=None, alias="remote-port-desc")
    remote_sys_name: str | None = Field(json_schema_extra={"is_config": False}, description="The string value used to identify the system name of the\nremote system.\nsys-name: system name", min_length=0, max_length=255, default=None, alias="remote-sys-name")
    remote_sys_desc: str | None = Field(json_schema_extra={"is_config": False}, description="The string value used to identify the system description\nof the remote system.\nsys-desc: system description", min_length=0, max_length=255, default=None, alias="remote-sys-desc")
    remote_sys_cap_supported: str | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the system capabilities.\nThe bit 'other(0)' indicates that the system has capabilities\nother than those listed below.\nThe bit 'repeater(1)' indicates that the system has repeater\ncapability.\nThe bit 'bridge(2)' indicates that the system has bridge\ncapability.\nThe bit 'wlanAccessPoint(3)' indicates that the system has\nWLAN access point capability.\nThe bit 'router(4)' indicates that the system has router\ncapability.\nThe bit 'telephone(5)' indicates that the system has telephone\ncapability.\nThe bit 'docsisCableDevice(6)' indicates that the system has\nDOCSIS Cable Device capability (IETF RFC 2669 & 2670).\nThe bit 'stationOnly(7)' indicates that the system has only\nstation capability and nothing else.\nThe bit 'cVLANComponent(8)' indicates that the system has\nC-VLAN component functionality.\nThe bit 'sVLANComponent(9)' indicates that the system  has\nS-VLAN component functionality.\nThe bit 'twoPortMACRelay(10)' indicates that the system has\nTwo-port MAC Relay (TPMR) functionality.\nsys-cap-supported: supported system capability", default=None, alias="remote-sys-cap-supported")
    remote_sys_cap_enabled: str | None = Field(json_schema_extra={"is_config": False}, description="This attribute describes the system capabilities.\nThe bit 'other(0)' indicates that the system has capabilities\nother than those listed below.\nThe bit 'repeater(1)' indicates that the system has repeater\ncapability.\nThe bit 'bridge(2)' indicates that the system has bridge\ncapability.\nThe bit 'wlanAccessPoint(3)' indicates that the system has\nWLAN access point capability.\nThe bit 'router(4)' indicates that the system has router\ncapability.\nThe bit 'telephone(5)' indicates that the system has telephone\ncapability.\nThe bit 'docsisCableDevice(6)' indicates that the system has\nDOCSIS Cable Device capability (IETF RFC 2669 & 2670).\nThe bit 'stationOnly(7)' indicates that the system has only\nstation capability and nothing else.\nThe bit 'cVLANComponent(8)' indicates that the system has\nC-VLAN component functionality.\nThe bit 'sVLANComponent(9)' indicates that the system  has\nS-VLAN component functionality.\nThe bit 'twoPortMACRelay(10)' indicates that the system has\nTwo-port MAC Relay (TPMR) functionality.", default=None, alias="remote-sys-cap-enabled")
    management_address: str | None = Field(json_schema_extra={"is_config": False}, description="The last reported remote management address", default=None, alias="management-address")
    management_address_type: int | None = Field(json_schema_extra={"is_config": False}, description="The last reported remote management address type", ge=0, default=None, alias="management-address-type")
    remote_man_addresses: RestconfList[RemoteManAddressesItem] | None = Field(json_schema_extra={"is_config": False}, description="List of management addresses of LLDP neighbor.\nman:managment, remote management addresses", default=None, alias="remote-man-addresses")

class BitErrorRatePreFec(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for bit error rate before fec, corresponding to pm parameter BER-FEC"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class BitErrorRatePostFec(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for bit error rate post fec, corresponding to pm parameter BER-POST-FEC"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class InUtilization(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for RX utilization, corresponding to pm parameter Utilization"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, le=100, default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, le=100, default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, le=100, default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, le=100, default=None)

class OutUtilization(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for TX utilization, corresponding to pm parameter Utilization"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, le=100, default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, le=100, default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, le=100, default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, le=100, default=None)

class InBackgroundBlockErrorRate(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value corresponding to ingress pm parameter BBER"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutBackgroundBlockErrorRate(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value corresponding to egress pm parameter BBER"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class InSeverelyErroredSecondsRate(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value corresponding to ingress pm parameter SESR"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutSeverelyErroredSecondsRate(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value corresponding to egress pm parameter SESR"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    loss_of_signal_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for signal loss, corresponding to pm parameter loss", ge=0, le=18446744073709551615, default=None, alias="loss-of-signal-seconds")
    bit_error_fec: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics bits counting for error bit forward error correction, corresponding to pm parameter BE-FEC\n\nCondition (when): (../../port-mode = '100GBE') or (../../port-mode = '400GBE')", ge=0, le=18446744073709551615, default=None, alias="bit-error-fec")
    uncorrected_block_error_fec: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics blocks counting for uncorrected block error forward error correction, corresponding to pm parameter UBE-FEC\n\nCondition (when): (../../port-mode = '100GBE') or (../../port-mode = '400GBE')", ge=0, le=18446744073709551615, default=None, alias="uncorrected-block-error-fec")
    in_symbol_errors: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics Times counting for input signal symbol errors, corresponding to pm parameter SE", ge=0, le=18446744073709551615, default=None, alias="in-symbol-errors")
    in_drop_events: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input signal drop events, corresponding to pm parameter DropEvents", ge=0, le=18446744073709551615, default=None, alias="in-drop-events")
    in_octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input signal octets, corresponding to pm parameter Octets", ge=0, le=18446744073709551615, default=None, alias="in-octets")
    in_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input signal packets, corresponding to pm parameter Pkts", ge=0, le=18446744073709551615, default=None, alias="in-packets")
    in_broadcast_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input broadcast packets, corresponding to pm parameter BroadcastPkts", ge=0, le=18446744073709551615, default=None, alias="in-broadcast-packets")
    in_multicast_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input multicast packets, corresponding to pm parameter MulticastPkts", ge=0, le=18446744073709551615, default=None, alias="in-multicast-packets")
    in_crc_align_errors: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input CRC error packets, corresponding to pm parameter CRCAlignErrors", ge=0, le=18446744073709551615, default=None, alias="in-crc-align-errors")
    in_undersize_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input undersize packets, corresponding to pm parameter UndersizePkts", ge=0, le=18446744073709551615, default=None, alias="in-undersize-packets")
    in_oversize_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input oversize packets, corresponding to pm parameter OversizePkts", ge=0, le=18446744073709551615, default=None, alias="in-oversize-packets")
    in_fragments: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input fragment packets, corresponding to pm parameter Fragments", ge=0, le=18446744073709551615, default=None, alias="in-fragments")
    in_jabbers: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input jabber packets, corresponding to pm parameter Jabbers", ge=0, le=18446744073709551615, default=None, alias="in-jabbers")
    in_packets_64octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input 64 octets packets, corresponding to pm parameter Pkts64Octets", ge=0, le=18446744073709551615, default=None, alias="in-packets-64octets")
    in_packets_65to127octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input 65 to 127 octets packets, corresponding to pm parameter Pkts65to127Octets", ge=0, le=18446744073709551615, default=None, alias="in-packets-65to127octets")
    in_packets_128to255octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input 128 to 255 octets packets, corresponding to pm parameter Pkts128to255Octets", ge=0, le=18446744073709551615, default=None, alias="in-packets-128to255octets")
    in_packets_256to511octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input 256 to 511 octets packets, corresponding to pm parameter Pkts256to511Octets", ge=0, le=18446744073709551615, default=None, alias="in-packets-256to511octets")
    in_packets_512to1023octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input 512 to 1023 octets packets, corresponding to pm parameter Pkts512to1023Octets", ge=0, le=18446744073709551615, default=None, alias="in-packets-512to1023octets")
    in_packets_1024to1518octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for input 1024 to 1518 octets packets, corresponding to pm parameter Pkts1024to1518Octets", ge=0, le=18446744073709551615, default=None, alias="in-packets-1024to1518octets")
    out_symbol_errors: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics Times counting for output signal symbol errors, corresponding to pm parameter SE", ge=0, le=18446744073709551615, default=None, alias="out-symbol-errors")
    out_drop_events: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output signal drop events, corresponding to pm parameter DropEvents", ge=0, le=18446744073709551615, default=None, alias="out-drop-events")
    out_octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output signal octets, corresponding to pm parameter Octets", ge=0, le=18446744073709551615, default=None, alias="out-octets")
    out_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output signal packets, corresponding to pm parameter Pkts", ge=0, le=18446744073709551615, default=None, alias="out-packets")
    out_broadcast_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output broadcast packets, corresponding to pm parameter BroadcastPkts", ge=0, le=18446744073709551615, default=None, alias="out-broadcast-packets")
    out_multicast_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output multicast packets, corresponding to pm parameter MulticastPkts", ge=0, le=18446744073709551615, default=None, alias="out-multicast-packets")
    out_crc_align_errors: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output CRC error packets, corresponding to pm parameter CRCAlignErrors", ge=0, le=18446744073709551615, default=None, alias="out-crc-align-errors")
    out_undersize_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output undersize packets, corresponding to pm parameter UndersizePkts", ge=0, le=18446744073709551615, default=None, alias="out-undersize-packets")
    out_oversize_packets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output oversize packets, corresponding to pm parameter OversizePkts", ge=0, le=18446744073709551615, default=None, alias="out-oversize-packets")
    out_fragments: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output fragment packets, corresponding to pm parameter Fragments", ge=0, le=18446744073709551615, default=None, alias="out-fragments")
    out_jabbers: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output jabber packets, corresponding to pm parameter Jabbers", ge=0, le=18446744073709551615, default=None, alias="out-jabbers")
    out_packets_64octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output 64 octets packets, corresponding to pm parameter Pkts64Octets", ge=0, le=18446744073709551615, default=None, alias="out-packets-64octets")
    out_packets_65to127octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output 65 to 127 octets packets, corresponding to pm parameter Pkts65to127Octets", ge=0, le=18446744073709551615, default=None, alias="out-packets-65to127octets")
    out_packets_128to255octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output 128 to 255 octets packets, corresponding to pm parameter Pkts128to255Octets", ge=0, le=18446744073709551615, default=None, alias="out-packets-128to255octets")
    out_packets_256to511octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output 256 to 511 octets packets, corresponding to pm parameter Pkts256to511Octets", ge=0, le=18446744073709551615, default=None, alias="out-packets-256to511octets")
    out_packets_512to1023octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output 512 to 1023 octets packets, corresponding to pm parameter Pkts512to1023Octets", ge=0, le=18446744073709551615, default=None, alias="out-packets-512to1023octets")
    out_packets_1024to1518octets: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for output 1024 to 1518 octets packets, corresponding to pm parameter Pkts1024to1518Octets", ge=0, le=18446744073709551615, default=None, alias="out-packets-1024to1518octets")
    bit_error_rate_pre_fec: BitErrorRatePreFec | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for bit error rate before fec, corresponding to pm parameter BER-FEC", default=None, alias="bit-error-rate-pre-fec")
    bit_error_rate_post_fec: BitErrorRatePostFec | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for bit error rate post fec, corresponding to pm parameter BER-POST-FEC", default=None, alias="bit-error-rate-post-fec")
    in_utilization: InUtilization | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX utilization, corresponding to pm parameter Utilization", default=None, alias="in-utilization")
    out_utilization: OutUtilization | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX utilization, corresponding to pm parameter Utilization", default=None, alias="out-utilization")
    in_coding_violation: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics bits counting for ingress coding violation, corresponding to pm parameter CV\n\nCondition (when): ../../port-type = 'osc'", ge=0, le=18446744073709551615, default=None, alias="in-coding-violation")
    errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for errored signal, corresponding to pm parameter ES\n\nCondition (when): ../../port-type = 'osc'", ge=0, le=18446744073709551615, default=None, alias="errored-seconds")
    severely_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for severely errored signal, corresponding to pm parameter SES\n\nCondition (when): ../../port-type = 'osc'", ge=0, le=18446744073709551615, default=None, alias="severely-errored-seconds")
    unavailable_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for unavailable signal, corresponding to pm parameter UAS\n\nCondition (when): ../../port-type = 'osc'", ge=0, le=18446744073709551615, default=None, alias="unavailable-seconds")
    in_background_block_error: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for ingress errored blocks, corresponding to pm parameter BBE\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", ge=0, le=18446744073709551615, default=None, alias="in-background-block-error")
    out_background_block_error: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for egress errored blocks, corresponding to pm parameter BBE\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", ge=0, le=18446744073709551615, default=None, alias="out-background-block-error")
    in_background_block_error_rate: InBackgroundBlockErrorRate | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value corresponding to ingress pm parameter BBER\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", default=None, alias="in-background-block-error-rate")
    out_background_block_error_rate: OutBackgroundBlockErrorRate | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value corresponding to egress pm parameter BBER\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", default=None, alias="out-background-block-error-rate")
    in_severely_errored_seconds_rate: InSeverelyErroredSecondsRate | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value corresponding to ingress pm parameter SESR\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", default=None, alias="in-severely-errored-seconds-rate")
    out_severely_errored_seconds_rate: OutSeverelyErroredSecondsRate | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value corresponding to egress pm parameter SESR\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", default=None, alias="out-severely-errored-seconds-rate")
    in_errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for errored blocks, corresponding to pm parameter EB ingress\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", ge=0, le=18446744073709551615, default=None, alias="in-errored-blocks")
    out_errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for errored blocks, corresponding to pm parameter EB egress\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", ge=0, le=18446744073709551615, default=None, alias="out-errored-blocks")
    in_bip_errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for ingress BIP errored blocks, corresponding to pm parameter BE\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", ge=0, le=18446744073709551615, default=None, alias="in-bip-errored-blocks")
    out_bip_errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for egress BIP errored blocks, corresponding to pm parameter BE\n\nCondition (when): ../../port-mode = ('1GBE', '10GBE', '40GBE', '100GBE')", ge=0, le=18446744073709551615, default=None, alias="out-bip-errored-blocks")

class UpiValueEnum(str, Enum):
    """Enumeration for UpiValueEnum
    
    Values:
      * not-applicable
      * G709
      * Gsupp43
    """

    NOT_APPLICABLE = "not-applicable"
    G709 = "G709"
    GSUPP43 = "Gsupp43"

class OduTypeEnum(str, Enum):
    """Enumeration for OduTypeEnum
    
    Values:
      * unused
      * odu0
      * odu1
      * odu2
      * odu2e
      * odu3
      * odu3e
      * odu4
      * oduflex
      * oduc2
      * oduc3
      * oduc4
      * oduc5
      * oduc6
      * oduc7
      * oduc9
      * oduc11
    """

    UNUSED = "unused"
    ODU0 = "odu0"
    ODU1 = "odu1"
    ODU2 = "odu2"
    ODU2E = "odu2e"
    ODU3 = "odu3"
    ODU3E = "odu3e"
    ODU4 = "odu4"
    ODUFLEX = "oduflex"
    ODUC2 = "oduc2"
    ODUC3 = "oduc3"
    ODUC4 = "oduc4"
    ODUC5 = "oduc5"
    ODUC6 = "oduc6"
    ODUC7 = "oduc7"
    ODUC9 = "oduc9"
    ODUC11 = "oduc11"

class OpuConfigActualEnum(str, Enum):
    """Enumeration for OpuConfigActualEnum
    
    Values:
      * not-applicable
      * intact
      * client
      * mux
    """

    NOT_APPLICABLE = "not-applicable"
    INTACT = "intact"
    CLIENT = "client"
    MUX = "mux"

class ClientSignalTypeEnum(str, Enum):
    """Enumeration for ClientSignalTypeEnum
    
    Values:
      * not-applicable
      * FC8G
      * FC16G
      * FC4G
    """

    NOT_APPLICABLE = "not-applicable"
    FC8G = "FC8G"
    FC16G = "FC16G"
    FC4G = "FC4G"

class OduTerminationModeEnum(str, Enum):
    """Enumeration for OduTerminationModeEnum
    
    Values:
      * terminated
      * non-terminated
    """

    TERMINATED = "terminated"
    NON_TERMINATED = "non-terminated"

class OduAlarmFunctionEnum(str, Enum):
    """Enumeration for OduAlarmFunctionEnum
    
    Values:
      * no-function
      * TTP
      * CTP
      * TTP-CTP
    """

    NO_FUNCTION = "no-function"
    TTP = "TTP"
    CTP = "CTP"
    TTP_CTP = "TTP-CTP"

class TimModeEnum(str, Enum):
    """Enumeration for TimModeEnum
    
    Values:
      * NONE: No TTI match checking
      * SAPI: Comparing SAPI only
      * DAPI: Comparing DAPI only
      * OPER: Comparing Operator Specific only
      * SAPI_DAPI: Comparing SAPI + DAPI
      * SAPI_OPER: Comparing SAPI + OPER
      * DAPI_OPER: Comparing DAPI + OPER
      * SAPI_DAPI_OPER: Comparing SAPI + DAPI + OPER
    """

    NONE = "NONE"
    SAPI = "SAPI"
    DAPI = "DAPI"
    OPER = "OPER"
    SAPI_DAPI = "SAPI_DAPI"
    SAPI_OPER = "SAPI_OPER"
    DAPI_OPER = "DAPI_OPER"
    SAPI_DAPI_OPER = "SAPI_DAPI_OPER"

class EncryptionEnableEnum(str, Enum):
    """Enumeration for EncryptionEnableEnum
    
    Values:
      * enabled
      * disabled
      * enabled-non-revertive
    """

    ENABLED = "enabled"
    DISABLED = "disabled"
    ENABLED_NON_REVERTIVE = "enabled-non-revertive"

class BlockCipherModeEnum(str, Enum):
    """Enumeration for BlockCipherModeEnum
    
    Values:
      * CTR
      * GCM
    """

    CTR = "CTR"
    GCM = "GCM"

class EncryptionTerminationDirectionEnum(str, Enum):
    """Enumeration for EncryptionTerminationDirectionEnum
    
    Values:
      * physical-port: The ODU encryption terminates encrypted service coming from physical port of the odu entity
      * cross-connection: The ODU encryption terminates encrypted service coming from odu cross connection associated with the odu entity
    """

    PHYSICAL_PORT = "physical-port"
    CROSS_CONNECTION = "cross-connection"

class OduEncryption(YangBaseModel):
    """Encryption function for the ODU channel."""

    encryption_enable: EncryptionEnableEnum | None = Field(json_schema_extra={"is_config": True}, description="Setting AES-256 encryption on OTN", default=EncryptionEnableEnum.DISABLED, alias="encryption-enable")
    block_cipher_mode: BlockCipherModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies the block cipher mode of operation.", default=None, alias="block-cipher-mode")
    encryption_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The encryption key rotation interval (in minutes)", ge=10, le=1440, default=30, alias="encryption-interval")
    time_to_next_key: int | None = Field(json_schema_extra={"is_config": False}, description="The time left to rotate the ODU encryption key.", ge=0, default=0, alias="time-to-next-key")
    encryption_tx_status: str | None = Field(json_schema_extra={"is_config": False}, description="The encryption status at transmit side of the ODU,\nwhich reflects the status of both encryption data and communication sessions.", default=None, alias="encryption-tx-status")
    encryption_rx_status: str | None = Field(json_schema_extra={"is_config": False}, description="The encryption status at receive side of the ODU,\nwhich reflects the status of both encryption data and communication sessions.", default=None, alias="encryption-rx-status")
    odu_key_sync_session: str | None = Field(json_schema_extra={"is_config": True}, description="Indicate the associated session for the ODU channel to synchronize keys.", default="none", alias="odu-key-sync-session")
    encryption_tx_channel_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([A-Za-z0-9_\\-][A-Za-z0-9_\\-\\+]*)|(\\+loc:([A-Za-z0-9]{1,})\\+rmt:([A-Za-z0-9]{1,})))?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Specify channel identifier of the encrypted ODU, which shall be unique within the NE.", min_length=0, max_length=32, default=None, alias="encryption-tx-channel-id")
    encryption_termination_direction: EncryptionTerminationDirectionEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the encryption termination direction.", default=EncryptionTerminationDirectionEnum.PHYSICAL_PORT, alias="encryption-termination-direction")

class OduDelay(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for measured odu signal delay, corresponding to pm parameter DELAY"""

    instant: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, le=18446744073709551615, default=None)
    avg: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, le=18446744073709551615, default=None)
    min: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, le=18446744073709551615, default=None)
    max: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, le=18446744073709551615, default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for errored blocks, corresponding to pm parameter EB", ge=0, le=18446744073709551615, default=None, alias="errored-blocks")
    farend_errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for farend error blocks, corresponding to pm parameter FEB", ge=0, le=18446744073709551615, default=None, alias="farend-errored-blocks")
    errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for errored signal, corresponding to pm parameter ES", ge=0, le=18446744073709551615, default=None, alias="errored-seconds")
    severely_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for severely errored signal, corresponding to pm parameter SES", ge=0, le=18446744073709551615, default=None, alias="severely-errored-seconds")
    unavailable_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for unavailable signal, corresponding to pm parameter UAS", ge=0, le=18446744073709551615, default=None, alias="unavailable-seconds")
    odu_delay: OduDelay | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for measured odu signal delay, corresponding to pm parameter DELAY", default=None, alias="odu-delay")
    encryption_fail_rx: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Failed Encryption Frames of Receive side, corresponding to pm parameter Encryption-fail-rx\n\nCondition (when): ../odu-encryption", ge=0, le=18446744073709551615, default=None, alias="encryption-fail-rx")

class TestSignalStatus(YangBaseModel):
    """Test signal status on ODU"""

    prbs_sync: PrbsSyncEnum | None = Field(json_schema_extra={"is_config": False}, description="The test result of PRBS Synchronization", default=PrbsSyncEnum.NOT_APPLICABLE, alias="prbs-sync")
    test_time_duration: int | None = Field(json_schema_extra={"is_config": False}, description="The time duration of signal test", ge=0, default=None, alias="test-time-duration")
    prbs_bit_error_count: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="The counting of bit error by PRBS Synchronization", ge=0, le=18446744073709551615, default=None, alias="prbs-bit-error-count")

class OduItem(YangBaseModel):
    """List: odu"""

    odutype_L1: OduTypeEnum = Field(json_schema_extra={"is_config": True}, description="Level 1 ODU type", alias="odutype-L1")
    oduid_L1: int = Field(json_schema_extra={"is_config": True}, description="Identifier of level 1 ODU", ge=0, alias="oduid-L1")
    odutype_L2: OduTypeEnum = Field(json_schema_extra={"is_config": True}, description="Level 2 ODU type", alias="odutype-L2")
    oduid_L2: int = Field(json_schema_extra={"is_config": True}, description="Identifier of level 2 ODU", ge=0, alias="oduid-L2")
    odutype_L3: OduTypeEnum = Field(json_schema_extra={"is_config": True}, description="Level 3 ODU type", alias="odutype-L3")
    oduid_L3: int = Field(json_schema_extra={"is_config": True}, description="Identifier of level 3 ODU", ge=0, alias="oduid-L3")
    odutype_L4: OduTypeEnum = Field(json_schema_extra={"is_config": True}, description="Level 4 ODU type", alias="odutype-L4")
    oduid_L4: int = Field(json_schema_extra={"is_config": True}, description="Identifier of level 4 ODU", ge=0, alias="oduid-L4")
    odu_type: OduTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes the type of odu", default=None, alias="odu-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    trib_slot: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]+(\\.\\.[0-9]+)?)(,([0-9]+(\\.\\.[0-9]+)?))*)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Tributary slots of ODU, range 1 to 80", min_length=0, max_length=255, default=None, alias="trib-slot")
    rx_payload_type: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x[0-9a-fA-F]{2})?)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Received payload-type of ODU", default=None, alias="rx-payload-type")
    tx_payload_type: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(0x[0-9a-fA-F]{2})?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Transmitter payload-type of ODU", default=None, alias="tx-payload-type")
    nim_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of nim function", default=EnableSwitchEnum.ENABLED, alias="nim-enable")
    delay_measurement_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of delay-measurement function", default=EnableSwitchEnum.DISABLED, alias="delay-measurement-enable")
    opu_config_actual: OpuConfigActualEnum | None = Field(json_schema_extra={"is_config": False}, description="The actual opu configuration type", default=OpuConfigActualEnum.NOT_APPLICABLE, alias="opu-config-actual")
    client_signal_type: ClientSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The ODUflex rate for special signal type", default=ClientSignalTypeEnum.NOT_APPLICABLE, alias="client-signal-type")
    odu_termination_mode: OduTerminationModeEnum | None = Field(json_schema_extra={"is_config": False}, description="Termination mode for ODU. It works for trace label, nim , Delay Measurement and test signal function validation", default=OduTerminationModeEnum.TERMINATED, alias="odu-termination-mode")
    odu_alarm_function: OduAlarmFunctionEnum | None = Field(json_schema_extra={"is_config": True}, description="The alarm transfer rang for openconfig and openroadm model", default=OduAlarmFunctionEnum.TTP_CTP, alias="odu-alarm-function")
    msim_config: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies msim alarm reporting or not when msi value received not followed G.709 definition\n\nCondition (when): ../odu-type = 'ODU4'", default=EnableSwitchEnum.ENABLED, alias="msim-config")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=None, alias="degrade-threshold")
    odu_encryption: OduEncryption | None = Field(json_schema_extra={"is_config": True}, description="Encryption function for the ODU channel.", default=None, alias="odu-encryption")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    test_signal_status: TestSignalStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status on ODU", default=None, alias="test-signal-status")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")

class Eth10g(YangBaseModel):
    """Represents the 10GBE object.
    """

    eth_fec_type: EthFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC working type of etyn port.", default=EthFecEnum.AUTO, alias="eth-fec-type")
    eth_fec_type_state: EthFecEnum | None = Field(json_schema_extra={"is_config": False}, description="The FEC working state of etyn port.", default=EthFecEnum.DISABLED, alias="eth-fec-type-state")
    transmit_interpacketgap: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the minimum transmit IPG value.", ge=8, le=12, default=8, alias="transmit-interpacketgap")
    gfp_payload_fcs: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enabled: GFP payload FCS will be used, Ethernet frame FCS will be removed;\nDisabled: GFP payload FCS will not be inserted, Ethernet frame FCS will be used.", default=EnableSwitchEnum.DISABLED, alias="gfp-payload-fcs")
    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    lldp_status_if: LldpStatusIfEnum | None = Field(json_schema_extra={"is_config": True}, description="Port level lldp control.\nValue of 'rxonly', then the LLDP agent will receive lldp,\nwhen lldp-status-ne is also enabled.\n\nValue of 'disabled', then LLDP agent will not filter and\nreceive LLDP frames on this port.  If there is remote systems\ninformation which is received on this port and stored in\nthe system before the lldp-status   becomes disabled,\nthen the information will naturally age out.\n\nNote: txOnly and txAndRx modes are not supported in Transponder module.", default=LldpStatusIfEnum.DISABLED, alias="lldp-status-if")
    lldp_remote_system: RestconfList[LldpRemoteSystemItem] | None = Field(json_schema_extra={"is_config": True}, description="List of LLDP neighbors.", default=None, alias="lldp-remote-system")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    upi_value: UpiValueEnum | None = Field(json_schema_extra={"is_config": True}, description="The value of ODU2 upi in PREAMBLE mapping mode.", default=UpiValueEnum.NOT_APPLICABLE, alias="upi-value")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Eth40g(YangBaseModel):
    """Represents the 40GBE object.
    """

    eth_fec_type: EthFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC working type of etyn port.", default=EthFecEnum.AUTO, alias="eth-fec-type")
    eth_fec_type_state: EthFecEnum | None = Field(json_schema_extra={"is_config": False}, description="The FEC working state of etyn port.", default=EthFecEnum.DISABLED, alias="eth-fec-type-state")
    transmit_interpacketgap: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the minimum transmit IPG value.", ge=8, le=12, default=8, alias="transmit-interpacketgap")
    gfp_payload_fcs: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enabled: GFP payload FCS will be used, Ethernet frame FCS will be removed;\nDisabled: GFP payload FCS will not be inserted, Ethernet frame FCS will be used.", default=EnableSwitchEnum.DISABLED, alias="gfp-payload-fcs")
    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    lldp_status_if: LldpStatusIfEnum | None = Field(json_schema_extra={"is_config": True}, description="Port level lldp control.\nValue of 'rxonly', then the LLDP agent will receive lldp,\nwhen lldp-status-ne is also enabled.\n\nValue of 'disabled', then LLDP agent will not filter and\nreceive LLDP frames on this port.  If there is remote systems\ninformation which is received on this port and stored in\nthe system before the lldp-status   becomes disabled,\nthen the information will naturally age out.\n\nNote: txOnly and txAndRx modes are not supported in Transponder module.", default=LldpStatusIfEnum.DISABLED, alias="lldp-status-if")
    lldp_remote_system: RestconfList[LldpRemoteSystemItem] | None = Field(json_schema_extra={"is_config": True}, description="List of LLDP neighbors.", default=None, alias="lldp-remote-system")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Eth100g(YangBaseModel):
    """Represents the 100GBE object."""

    eth_fec_type: EthFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC working type of etyn port.", default=EthFecEnum.AUTO, alias="eth-fec-type")
    eth_fec_type_state: EthFecEnum | None = Field(json_schema_extra={"is_config": False}, description="The FEC working state of etyn port.", default=EthFecEnum.DISABLED, alias="eth-fec-type-state")
    transmit_interpacketgap: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the minimum transmit IPG value.", ge=8, le=12, default=8, alias="transmit-interpacketgap")
    gfp_payload_fcs: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enabled: GFP payload FCS will be used, Ethernet frame FCS will be removed;\nDisabled: GFP payload FCS will not be inserted, Ethernet frame FCS will be used.", default=EnableSwitchEnum.DISABLED, alias="gfp-payload-fcs")
    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    lldp_status_if: LldpStatusIfEnum | None = Field(json_schema_extra={"is_config": True}, description="Port level lldp control.\nValue of 'rxonly', then the LLDP agent will receive lldp,\nwhen lldp-status-ne is also enabled.\n\nValue of 'disabled', then LLDP agent will not filter and\nreceive LLDP frames on this port.  If there is remote systems\ninformation which is received on this port and stored in\nthe system before the lldp-status   becomes disabled,\nthen the information will naturally age out.\n\nNote: txOnly and txAndRx modes are not supported in Transponder module.", default=LldpStatusIfEnum.DISABLED, alias="lldp-status-if")
    lldp_remote_system: RestconfList[LldpRemoteSystemItem] | None = Field(json_schema_extra={"is_config": True}, description="List of LLDP neighbors.", default=None, alias="lldp-remote-system")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Eth400g(YangBaseModel):
    """Represents the 400GBE object."""

    eth_fec_type: EthFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC working type of etyn port.", default=EthFecEnum.AUTO, alias="eth-fec-type")
    eth_fec_type_state: EthFecEnum | None = Field(json_schema_extra={"is_config": False}, description="The FEC working state of etyn port.", default=EthFecEnum.DISABLED, alias="eth-fec-type-state")
    transmit_interpacketgap: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the minimum transmit IPG value.", ge=8, le=12, default=8, alias="transmit-interpacketgap")
    gfp_payload_fcs: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enabled: GFP payload FCS will be used, Ethernet frame FCS will be removed;\nDisabled: GFP payload FCS will not be inserted, Ethernet frame FCS will be used.", default=EnableSwitchEnum.DISABLED, alias="gfp-payload-fcs")
    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    lldp_status_if: LldpStatusIfEnum | None = Field(json_schema_extra={"is_config": True}, description="Port level lldp control.\nValue of 'rxonly', then the LLDP agent will receive lldp,\nwhen lldp-status-ne is also enabled.\n\nValue of 'disabled', then LLDP agent will not filter and\nreceive LLDP frames on this port.  If there is remote systems\ninformation which is received on this port and stored in\nthe system before the lldp-status   becomes disabled,\nthen the information will naturally age out.\n\nNote: txOnly and txAndRx modes are not supported in Transponder module.", default=LldpStatusIfEnum.DISABLED, alias="lldp-status-if")
    lldp_remote_system: RestconfList[LldpRemoteSystemItem] | None = Field(json_schema_extra={"is_config": True}, description="List of LLDP neighbors.", default=None, alias="lldp-remote-system")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class OtukFecEnum(str, Enum):
    """Enumeration for OtukFecEnum
    
    Values:
      * SDFEC15: Soft-decision Forward Error Correction with 15 percentage redundancy ratio.
      * SDFEC25: Soft-decision Forward Error Correction with 25 percentage redundancy ratio.
      * G709: Forward Error Correction in compliance with ITU-T G.709.
      * I4: Forward Error Correction in compliance with ITU-T G.975.1 I.4.
      * I7: Forward Error Correction in compliance with ITU-T G.975.1 I.7.
      * noFEC: Forward Error Correction processing disabled.
      * STAIRCASE7: Forward Error Correction of staircase in compliance with ITU-T G.709.2 Annex A.
      * SDFEC15ND: Soft-decision Forward Error Correction of type ND with 15 percentage redundancy ratio.
      * SDFEC27ND: Soft-decision Forward Error Correction of type ND with 27 percentage redundancy ratio.
      * SDFEC15ND2: Soft-decision Forward Error Correction of type ND2 with 15 percentage redundancy ratio.
      * TRANSPARENT: Forward Error Correction is unspecified and transparently passing through.
      * UFEC7: Forward Error Correction of Inphi proprietary hard-decision(HD), 7% overhead (OH) staircase FEC.
    """

    SDFEC15 = "SDFEC15"
    SDFEC25 = "SDFEC25"
    G709 = "G709"
    I4 = "I4"
    I7 = "I7"
    NOFEC = "noFEC"
    STAIRCASE7 = "STAIRCASE7"
    SDFEC15ND = "SDFEC15ND"
    SDFEC27ND = "SDFEC27ND"
    SDFEC15ND2 = "SDFEC15ND2"
    TRANSPARENT = "TRANSPARENT"
    UFEC7 = "UFEC7"

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    loss_of_signal_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for signal loss, corresponding to pm parameter loss\n\nCondition (when): ancestor::port/port-type = 'client'", ge=0, le=18446744073709551615, default=None, alias="loss-of-signal-seconds")
    bit_error_fec: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics bits counting for error bit forward error correction, corresponding to pm parameter BE-FEC\n\nCondition (when): (ancestor::port/port-type = 'client') and (../../port-mode != 'OTU4_TRANSPARENT')", ge=0, le=18446744073709551615, default=None, alias="bit-error-fec")
    uncorrected_block_error_fec: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics blocks counting for uncorrected block error forward error correction, corresponding to pm parameter UBE-FEC\n\nCondition (when): (ancestor::port/port-type = 'client') and (../../port-mode != 'OTU4_TRANSPARENT')", ge=0, le=18446744073709551615, default=None, alias="uncorrected-block-error-fec")
    errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for errored blocks, corresponding to pm parameter EB", ge=0, le=18446744073709551615, default=None, alias="errored-blocks")
    errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for errored signal, corresponding to pm parameter ES", ge=0, le=18446744073709551615, default=None, alias="errored-seconds")
    severely_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for severely errored signal, corresponding to pm parameter SES", ge=0, le=18446744073709551615, default=None, alias="severely-errored-seconds")
    unavailable_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for unavailable signal, corresponding to pm parameter UAS", ge=0, le=18446744073709551615, default=None, alias="unavailable-seconds")
    bit_error_rate_pre_fec: BitErrorRatePreFec | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for bit error rate before fec, corresponding to pm parameter BER-FEC", default=None, alias="bit-error-rate-pre-fec")
    bit_error_rate_post_fec: BitErrorRatePostFec | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for bit error rate post fec, corresponding to pm parameter BER-POST-FEC", default=None, alias="bit-error-rate-post-fec")
    farend_errored_blocks: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for farend error blocks, corresponding to pm parameter FEB", ge=0, le=18446744073709551615, default=None, alias="farend-errored-blocks")
    incoming_alignment_errored_seconds: int | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for incoming alignment error seconds, corresponding to pm parameter IAE", ge=0, default=None, alias="incoming-alignment-errored-seconds")
    backward_incoming_alignment_errored_seconds: int | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for backward incoming alignment error seconds, corresponding to pm parameter BIAE", ge=0, default=None, alias="backward-incoming-alignment-errored-seconds")

class Otu4(YangBaseModel):
    """Represents the otu4 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=128459, alias="degrade-threshold")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.\n\nCondition (when): ancestor::port/port-type = 'client'", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.\n\nCondition (when): ancestor::port/port-type = 'client'", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.\n\nCondition (when): ancestor::port/port-type = 'client'", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.\n\nCondition (when): ancestor::port/port-type = 'client'", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS\n\nCondition (when): ancestor::port/port-type = 'client'", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.\n\nCondition (when): ancestor::port/port-type = 'client'", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function\n\nCondition (when): ancestor::port/port-type = 'client'", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otu2(YangBaseModel):
    """Represents the otu2 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=12304, alias="degrade-threshold")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.\n\nCondition (when): (ancestor::port/port-type = 'client-subport') or (ancestor::port/port-type = 'client')", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function\n\nCondition (when): (ancestor::port/port-type = 'client-subport') or (ancestor::port/port-type = 'client')", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.\n\nCondition (when): (ancestor::port/port-type = 'client')", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.\n\nCondition (when): (ancestor::port/port-type = 'client')", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.\n\nCondition (when): (ancestor::port/port-type = 'client')", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.\n\nCondition (when): (ancestor::port/port-type = 'client')", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS\n\nCondition (when): (ancestor::port/port-type = 'client')", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otu2e(YangBaseModel):
    """Represents the otu2e object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=12748, alias="degrade-threshold")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.\n\nCondition (when): (ancestor::port/port-type = 'client-subport') or (ancestor::port/port-type = 'client')", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function\n\nCondition (when): (ancestor::port/port-type = 'client-subport') or (ancestor::port/port-type = 'client')", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.\n\nCondition (when): (ancestor::port/port-type = 'client')", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.\n\nCondition (when): (ancestor::port/port-type = 'client')", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.\n\nCondition (when): (ancestor::port/port-type = 'client')", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.\n\nCondition (when): (ancestor::port/port-type = 'client')", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS\n\nCondition (when): (ancestor::port/port-type = 'client')", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class AisTypeEnum(str, Enum):
    """Enumeration for AisTypeEnum
    
    Values:
      * Generic-AIS
      * MS-AIS
      * AIS-L
    """

    GENERIC_AIS = "Generic-AIS"
    MS_AIS = "MS-AIS"
    AIS_L = "AIS-L"

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    loss_of_signal_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for signal loss, corresponding to pm parameter loss", ge=0, le=18446744073709551615, default=None, alias="loss-of-signal-seconds")
    in_coding_violation: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics bits counting for ingress coding violation, corresponding to pm parameter CV", ge=0, le=18446744073709551615, default=None, alias="in-coding-violation")
    in_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for RX errored signal, corresponding to pm parameter ES", ge=0, le=18446744073709551615, default=None, alias="in-errored-seconds")
    in_severely_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for RX severely errored signal, corresponding to pm parameter SES", ge=0, le=18446744073709551615, default=None, alias="in-severely-errored-seconds")
    in_unavailable_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for RX unavailable signal, corresponding to pm parameter UAS", ge=0, le=18446744073709551615, default=None, alias="in-unavailable-seconds")
    in_severely_errored_frame_second: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for ingress signal frame severely errored, corresponding to pm parameter SEFS", ge=0, le=18446744073709551615, default=None, alias="in-severely-errored-frame-second")

class Oc192(YangBaseModel):
    """Represents the OC192 object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    exp_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="exp-trc")
    tx_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter trc(trail trace identification)\n\nCondition (when): ancestor::card/switching-type = 'tdm'", min_length=0, max_length=15, default=None, alias="tx-trc")
    rx_trc: str | None = Field(json_schema_extra={"is_config": False}, description="The received trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="rx-trc")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function\n\nCondition (when): ancestor::card/switching-type = 'tdm'", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    tim_monitor: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of tim defect monitor mode", default=EnableSwitchEnum.DISABLED, alias="tim-monitor")
    ais_type: AisTypeEnum | None = Field(json_schema_extra={"is_config": True}, default=AisTypeEnum.GENERIC_AIS, alias="ais-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Oc48(YangBaseModel):
    """Represents the OC48 object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    exp_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="exp-trc")
    tx_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter trc(trail trace identification)\n\nCondition (when): ancestor::card/switching-type = 'tdm'", min_length=0, max_length=15, default=None, alias="tx-trc")
    rx_trc: str | None = Field(json_schema_extra={"is_config": False}, description="The received trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="rx-trc")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function\n\nCondition (when): ancestor::card/switching-type = 'tdm'", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    tim_monitor: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of tim defect monitor mode", default=EnableSwitchEnum.DISABLED, alias="tim-monitor")
    ais_type: AisTypeEnum | None = Field(json_schema_extra={"is_config": True}, default=AisTypeEnum.GENERIC_AIS, alias="ais-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    loss_of_signal_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for signal loss, corresponding to pm parameter loss", ge=0, le=18446744073709551615, default=None, alias="loss-of-signal-seconds")
    in_background_block_error: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting for ingress errored blocks, corresponding to pm parameter BBE", ge=0, le=18446744073709551615, default=None, alias="in-background-block-error")
    in_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for RX errored signal, corresponding to pm parameter ES", ge=0, le=18446744073709551615, default=None, alias="in-errored-seconds")
    in_severely_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for RX severely errored signal, corresponding to pm parameter SES", ge=0, le=18446744073709551615, default=None, alias="in-severely-errored-seconds")
    in_unavailable_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for RX unavailable signal, corresponding to pm parameter UAS", ge=0, le=18446744073709551615, default=None, alias="in-unavailable-seconds")
    in_out_of_frame_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for ingress signal lose of frame, corresponding to pm parameter OFS", ge=0, le=18446744073709551615, default=None, alias="in-out-of-frame-seconds")

class Stm64(YangBaseModel):
    """Represents the STM64 object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    exp_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="exp-trc")
    tx_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter trc(trail trace identification)\n\nCondition (when): ancestor::card/switching-type = 'tdm'", min_length=0, max_length=15, default=None, alias="tx-trc")
    rx_trc: str | None = Field(json_schema_extra={"is_config": False}, description="The received trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="rx-trc")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function\n\nCondition (when): ancestor::card/switching-type = 'tdm'", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    tim_monitor: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of tim defect monitor mode", default=EnableSwitchEnum.DISABLED, alias="tim-monitor")
    ais_type: AisTypeEnum | None = Field(json_schema_extra={"is_config": True}, default=AisTypeEnum.GENERIC_AIS, alias="ais-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Stm16(YangBaseModel):
    """Represents the STM16 object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    exp_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="exp-trc")
    tx_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter trc(trail trace identification)\n\nCondition (when): ancestor::card/switching-type = 'tdm'", min_length=0, max_length=15, default=None, alias="tx-trc")
    rx_trc: str | None = Field(json_schema_extra={"is_config": False}, description="The received trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="rx-trc")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function\n\nCondition (when): ancestor::card/switching-type = 'tdm'", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    tim_monitor: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of tim defect monitor mode", default=EnableSwitchEnum.DISABLED, alias="tim-monitor")
    ais_type: AisTypeEnum | None = Field(json_schema_extra={"is_config": True}, default=AisTypeEnum.GENERIC_AIS, alias="ais-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Wan10gSonet(YangBaseModel):
    """Represents the 10GWAN_SONET object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    exp_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="exp-trc")
    tx_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter trc(trail trace identification)\n\nCondition (when): ancestor::card/switching-type = 'tdm'", min_length=0, max_length=15, default=None, alias="tx-trc")
    rx_trc: str | None = Field(json_schema_extra={"is_config": False}, description="The received trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="rx-trc")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function\n\nCondition (when): ancestor::card/switching-type = 'tdm'", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    tim_monitor: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of tim defect monitor mode", default=EnableSwitchEnum.DISABLED, alias="tim-monitor")
    ais_type: AisTypeEnum | None = Field(json_schema_extra={"is_config": True}, default=AisTypeEnum.GENERIC_AIS, alias="ais-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Wan10gSdh(YangBaseModel):
    """Represents the 10GWAN_SDH object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    exp_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="exp-trc")
    tx_trc: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter trc(trail trace identification)\n\nCondition (when): ancestor::card/switching-type = 'tdm'", min_length=0, max_length=15, default=None, alias="tx-trc")
    rx_trc: str | None = Field(json_schema_extra={"is_config": False}, description="The received trc(trail trace identification)", min_length=0, max_length=15, default=None, alias="rx-trc")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function\n\nCondition (when): ancestor::card/switching-type = 'tdm'", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    tim_monitor: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of tim defect monitor mode", default=EnableSwitchEnum.DISABLED, alias="tim-monitor")
    ais_type: AisTypeEnum | None = Field(json_schema_extra={"is_config": True}, default=AisTypeEnum.GENERIC_AIS, alias="ais-type")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    loss_of_signal_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for signal loss, corresponding to pm parameter loss", ge=0, le=18446744073709551615, default=None, alias="loss-of-signal-seconds")
    in_symbol_errors: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics Times counting for signal symbol errors, corresponding to pm parameter SE", ge=0, le=18446744073709551615, default=None, alias="in-symbol-errors")

class Fc1g(YangBaseModel):
    """Represents the FC1G object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Fc4g(YangBaseModel):
    """Represents the FC4G object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Fc8g(YangBaseModel):
    """Represents the FC8G object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Fc16g(YangBaseModel):
    """Represents the FC16G object.
    """

    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class InOpticalPower(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutOpticalPower(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")
    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")

class Otuc2(YangBaseModel):
    """Represents the otuc2 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=259085, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otuc3(YangBaseModel):
    """Represents the otuc3 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=388627, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otuc6(YangBaseModel):
    """Represents the otuc6 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=777255, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class SubportItem(YangBaseModel):
    """List: subport"""

    subport_id: int = Field(json_schema_extra={"is_config": True}, description="The identifier is defined to uniquely identify the subport.", ge=0, alias="subport-id")
    port_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The name of the port.", min_length=1, max_length=32, default="unspecified", alias="port-name")
    port_type: PortTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="The type of port. Needs to be provided upon Port creation", default=PortTypeEnum.OPTICAL_NOMON, alias="port-type")
    port_mode: PortModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The working mode of port.\nFor client side:\nCHM1: applicable to port 3 to 6; possible values are: 100GBE, not-applicable.\nDefault is 100GBE when card created.\n\nCHM2: applicable to port 3 to 11; possible values are: 40GBE, subport, not-applicable;\napplicable to subport 1 to 4; possible values are: 10GBE, not-applicable.\nDefault is not-applicable.\n       \nFor Line side:\nCHM1/CHM2: possible values are: QPSK_100G, 16QAM_200G, 8QAM_300G.\nDefault is 16QAM_200G.\n\nnon applicable : there shall not be service created on the port or subport\nsubport: the port shall create four subports under the port to support 4x10G.\n40GBE: 40GBE service shall be created on the port with default mapping GMP.\n10GBE: 10GBE service shall be created on the subport with default mapping BMP with fixed stuff.\n100GBE: 100GBE service shall be created on the subport with default mapping GMP.\nQPSK_100G: 100G OTU4 service with DP-QPSK coherent modulation format shall be created on the port.\n16QAM_200G: 200G OTUC2 service with DP-16QAM coherent modulation format shall be created on the port.\n8QAM_300G: 300G OTUC3 service with DP-8QAM coherent modulation format shall be created on the coupled two line ports.\n\nNote 4x10G is to create subport managed objects under the port. Each subport can support a 10G service.\n       \nRestrictions:\nChanging Port mode shall be allowed only if the impacted port or subport object is administratively down.\nChanging a 'subport' port mode of a port to be other value shall only be allowed only if port-modes of all the subports under the port are 'not-applicable'.\nIf there is explicitly cross-connection is created associated with the ODU of the port, change port mode of the port shall be denied.\nIf the port mode is a coupled port mode, e.g. 8QAM_300G, port mode can only be edited on the lower number of port within the coupled ports. The other port (or ports if more than two) will have read-only port mode value same as this lowest number port.\nWhen port/subport is set to admin down, laser will be shutdown, ingress side will insert proper maintenance signal.\n\nCondition (when): (../port-type = 'line') or (../port-type = 'client') or (../port-type = 'client-subport')", default=PortModeEnum.NOT_APPLICABLE, alias="port-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    connected_to: str | None = Field(json_schema_extra={"is_config": True}, description="Indicate neighbour port/facility entity to which the current port/facility is connected to.", min_length=0, max_length=128, default=None, alias="connected-to")
    external_connectivity: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the port is connected externally or not.", default=YesNoEnum.NO, alias="external-connectivity")
    arc_config: ArcConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The configurable mode of the Alarm Report Control (ARC).\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default=ArcConfigEnum.NALM_QI, alias="arc-config")
    arc_state: ArcConfigEnum | None = Field(json_schema_extra={"is_config": False}, description="The current mode of the Alarm Report Control (ARC).\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default=ArcConfigEnum.NALM_QI, alias="arc-state")
    arc_sub_state: ArcSubStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Additional information about the Alarm Report Control (ARC) when the main state is in the NALM-QI state\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default=ArcSubStateEnum.NALM_NR, alias="arc-sub-state")
    arc_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The holdoff timer value in minutes of the ARC.\nRange is 0 - 10080 minutes\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", ge=0, le=10080, default=1440, alias="arc-timer")
    arc_remaining_time: str | None = Field(json_schema_extra={"is_config": False}, description="The remaining timer value (format: xxd-xxh:xxm:xxs) before the alarm is reported.\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default="00d-00h:00m:00s", alias="arc-remaining-time")
    eth10g: Eth10g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 10GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    eth40g: Eth40g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 40GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    eth100g: Eth100g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 100GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    eth400g: Eth400g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 400GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otu4: Otu4 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu4 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otu2: Otu2 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu2 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otu2e: Otu2e | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu2e object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    oc192: Oc192 | None = Field(json_schema_extra={"is_config": True}, description="Represents the OC192 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    oc48: Oc48 | None = Field(json_schema_extra={"is_config": True}, description="Represents the OC48 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    stm64: Stm64 | None = Field(json_schema_extra={"is_config": True}, description="Represents the STM64 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    stm16: Stm16 | None = Field(json_schema_extra={"is_config": True}, description="Represents the STM16 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    wan10g_sonet: Wan10gSonet | None = Field(json_schema_extra={"is_config": True}, description="Represents the 10GWAN_SONET object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None, alias="wan10g-sonet")
    wan10g_sdh: Wan10gSdh | None = Field(json_schema_extra={"is_config": True}, description="Represents the 10GWAN_SDH object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None, alias="wan10g-sdh")
    fc1g: Fc1g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC1G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    fc4g: Fc4g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC4G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    fc8g: Fc8g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC8G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    fc16g: Fc16g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC16G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    tx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'mgmt-eth')", default=None, alias="tx-optical-power")
    rx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Received optical power\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'mgmt-eth')", default=None, alias="rx-optical-power")
    direction_type: TypeOfDirectionEnum | None = Field(json_schema_extra={"is_config": False}, description="Supported direction of the optical port.\n\nCondition (when): (port-type = 'optical') or (port-type = 'otdr') or (port-type = 'optical-nomon') or (port-type = 'ocm')", default=None, alias="direction-type")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, description="Condition (when): port-type = 'client-subport'", default=None)
    otuc2: Otuc2 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc2 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'mgmt-eth')", default=None)
    otuc3: Otuc3 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc3 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'mgmt-eth')", default=None)
    otuc6: Otuc6 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc6 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'mgmt-eth')", default=None)

class PluggableFormFactorEnum(str, Enum):
    """Enumeration for PluggableFormFactorEnum
    
    Values:
      * Not-applicable: Not applicable
      * Unrecognized: Type not recognized
      * QSFP+: Quad Small Form-factor Pluggable 10Gb/s.
      * QSFP28: Quad Small Form-factor Pluggable 28Gb/s.
      * CFP2-ACO: CFP2 - Analog Coherent Optics Module.
      * SFP+: Enhanced small form-factor pluggable
      * SFP: Small form-factor pluggable
      * XFP: 10 Gigabit Small Form Factor Pluggable
      * QSFP-DD: QSFP double density pluggable
      * CFP2-DCO: CFP2 - Digital Coherent Optics Module.
    """

    NOT_APPLICABLE = "Not-applicable"
    UNRECOGNIZED = "Unrecognized"
    QSFP_PLUS = "QSFP+"
    QSFP28 = "QSFP28"
    CFP2_ACO = "CFP2-ACO"
    SFP_PLUS = "SFP+"
    SFP = "SFP"
    XFP = "XFP"
    QSFP_DD = "QSFP-DD"
    CFP2_DCO = "CFP2-DCO"

class LaserSourceEnum(str, Enum):
    """Enumeration for LaserSourceEnum
    
    Values:
      * tx-lo-shared
      * tx-lo-independent
      * not-available
    """

    TX_LO_SHARED = "tx-lo-shared"
    TX_LO_INDEPENDENT = "tx-lo-independent"
    NOT_AVAILABLE = "not-available"

class UpgradeStatusEnum(str, Enum):
    """Enumeration for UpgradeStatusEnum
    
    Values:
      * unknown
      * idle
      * in_progress
      * success
      * failed
    """

    UNKNOWN = "unknown"
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"

class ChannelStatesItem(YangBaseModel):
    """List: channel-states"""

    channel_id: int = Field(json_schema_extra={"is_config": False}, description="multi channel pluggable's channel id", ge=0, alias="channel-id")
    laser_bias_current: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The current applied by the system to the transmit laser to\nachieve the output power. The current is expressed in mA\nwith up to two decimal precision. Just supply the instant value", default=None, alias="laser-bias-current")

class DiagnosticParameterEnum(str, Enum):
    """Enumeration for DiagnosticParameterEnum
    
    Values:
      * temperature
      * voltage
      * laser-bias
      * lane-rx-power
      * lane-tx-power
    """

    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"
    LASER_BIAS = "laser-bias"
    LANE_RX_POWER = "lane-rx-power"
    LANE_TX_POWER = "lane-tx-power"

class ParameterUnitsEnum(str, Enum):
    """Enumeration for ParameterUnitsEnum
    
    Values:
      * celsius
      * V
      * mA
      * dBm
    """

    CELSIUS = "celsius"
    V = "V"
    MA = "mA"
    DBM = "dBm"

class DiagnosticAlarmThresholdsItem(YangBaseModel):
    """List: diagnostic-alarm-thresholds"""

    diagnostic_parameter: DiagnosticParameterEnum = Field(json_schema_extra={"is_config": False}, description="The diagnostic parameter for pluggable\nwhich support alarm by threshold", alias="diagnostic-parameter")
    parameter_units: ParameterUnitsEnum | None = Field(json_schema_extra={"is_config": False}, default=None, alias="parameter-units")
    high_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The high alarm threshold of this parameter", default=None, alias="high-threshold")
    low_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The low alarm threshold of this parameter", default=None, alias="low-threshold")

class SignalValEnum(str, Enum):
    """Enumeration for SignalValEnum
    
    Values:
      * n/a: The setting value is not available
      * true: The setting value is true
      * false: The setting value is false
    """

    N_A = "n/a"
    TRUE = "true"
    FALSE = "false"

class RxOutputAmplitudeControlEnum(str, Enum):
    """Enumeration for RxOutputAmplitudeControlEnum
    
    Values:
      * n/a: The setting value is not available
      * 100-400mV: Corresponding to code value 0000
      * 300-600mV: Corresponding to code value 0001
      * 400-800mV: Corresponding to code value 0010
      * 600-1200mV: Corresponding to code value 0011
      * not-defined: The setting is valid but not defined in the range above.
    """

    N_A = "n/a"
    _100_400MV = "100-400mV"
    _300_600MV = "300-600mV"
    _400_800MV = "400-800mV"
    _600_1200MV = "600-1200mV"
    NOT_DEFINED = "not-defined"

class QsfpSignalIntegrityLaneItem(YangBaseModel):
    """List of qspf lane signal integrity."""

    lane_id: int = Field(json_schema_extra={"is_config": False}, description="Id of pluggable lane.", ge=0, alias="lane-id")
    tx_input_eq_fixed_manual_control: str | float | None = Field(json_schema_extra={"is_config": False}, description="Fixed manual equalization value of Tx side input for the lane.", default="n/a", alias="tx-input-eq-fixed-manual-control")
    tx_input_eq_adaptive_control: SignalValEnum | None = Field(json_schema_extra={"is_config": False}, description="Adaptive equalization control of Tx side input for Tx 1-4.", default=None, alias="tx-input-eq-adaptive-control")
    rx_output_eq_precursor_control: str | float | None = Field(json_schema_extra={"is_config": False}, description="Rx side output pre-cursor equalization values for Rx 1-4.", default="n/a", alias="rx-output-eq-precursor-control")
    rx_output_eq_postcursor_control: str | float | None = Field(json_schema_extra={"is_config": False}, description="Rx side output post-cursor equalization values for Rx 1-4.", default="n/a", alias="rx-output-eq-postcursor-control")
    rx_output_amplitude_control: RxOutputAmplitudeControlEnum | None = Field(json_schema_extra={"is_config": False}, description="Rx side output amplitude values for Rx 1-4.", default=RxOutputAmplitudeControlEnum.N_A, alias="rx-output-amplitude-control")

class QsfpSignalIntegrity(YangBaseModel):
    """Container for QSFP or QSFPxx signal integrity parameters defined in SFF-8636 ."""

    tx_input_eq_fixed_manual_control_impl: SignalValEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates implementation status of Tx side input fixed manual equalization control.", default=None, alias="tx-input-eq-fixed-manual-control-impl")
    rx_output_eq_precursor_control_impl: SignalValEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates implementation status of Rx side output pre-cursor equalization control.", default=None, alias="rx-output-eq-precursor-control-impl")
    rx_output_eq_postcursor_control_impl: SignalValEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates implementation status of Rx side output post-cursor equalization control.", default=None, alias="rx-output-eq-postcursor-control-impl")
    rx_output_amplitude_control_impl: SignalValEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates implementation status of Rx side output amplitude control.", default=None, alias="rx-output-amplitude-control-impl")
    qsfp_signal_integrity_lane: RestconfList[QsfpSignalIntegrityLaneItem] | None = Field(json_schema_extra={"is_config": False}, description="List of qspf lane signal integrity.", default=None, alias="qsfp-signal-integrity-lane")

class Pluggable(YangBaseModel):
    """Represents the Pluggable object"""

    required_type: PluggableTypeEnum = Field(json_schema_extra={"is_config": True}, description="The attribute indicates the equipment type to identify the module.\nNeeds to be re-defined in the project specific model.", alias="required-type")
    form_factor: PluggableFormFactorEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the exact form factor of the pluggable.", default=PluggableFormFactorEnum.UNRECOGNIZED, alias="form-factor")
    interface_type: str | None = Field(json_schema_extra={"is_config": False}, description="Indicating interface type of the pluggable.", min_length=0, max_length=64, default="", alias="interface-type")
    laser_source: LaserSourceEnum | None = Field(json_schema_extra={"is_config": False}, description="The type of laser frequency. Only tx-lo-independent type support och-os rx-frequency working\n\nCondition (when): ../required-type = 'CFP2'", default=LaserSourceEnum.NOT_AVAILABLE, alias="laser-source")
    hw_version: str | None = Field(json_schema_extra={"is_config": False}, description="The attribute Identifies the Hardware Version of the module that populates the slot.", min_length=0, max_length=20, default=None, alias="hw-version")
    vendor: str | None = Field(json_schema_extra={"is_config": False}, description="Vendor information.", min_length=0, max_length=64, default=None)
    serial_number: str | None = Field(json_schema_extra={"is_config": False}, description="This is the value of serial number stored in EEPROM of the equipment.", min_length=0, max_length=18, default=None, alias="serial-number")
    fw_version: str | None = Field(json_schema_extra={"is_config": False}, description="Current Firmware (FW) version on the equipment.", min_length=0, max_length=20, default=None, alias="fw-version")
    upgrade_status: UpgradeStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Successful or Failed", default=UpgradeStatusEnum.IDLE, alias="upgrade-status")
    upgrade_fail_reasons: str | None = Field(json_schema_extra={"is_config": False}, description="3rd party pluggle upgrade fail reason.", min_length=0, max_length=50, default=None, alias="upgrade-fail-reasons")
    part_number: str | None = Field(json_schema_extra={"is_config": False}, description="Identifies the Part Number of the equipment.", min_length=0, max_length=18, default=None, alias="part-number")
    clei: str | None = Field(json_schema_extra={"is_config": False}, description="Identifies the CLEI code number of the equipment.\nThe CLEI code is a 10-character code that identifies\ncommunications equipment. It describes product type, features,\nsource document, and associated drawings and vintages.", min_length=0, max_length=18, default=None)
    voltage: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The current voltage applied by the module. The current is\nexpressed in V with up to two decimal precision. Just\nsupply the instant value.", default=None)
    channel_states: RestconfList[ChannelStatesItem] | None = Field(json_schema_extra={"is_config": False}, default=None, alias="channel-states")
    diagnostic_alarm_thresholds: RestconfList[DiagnosticAlarmThresholdsItem] | None = Field(json_schema_extra={"is_config": False}, default=None, alias="diagnostic-alarm-thresholds")
    equipment_name: str | None = Field(json_schema_extra={"is_config": True}, description="The attribute indicates an additional field to identify the module.", min_length=0, max_length=64, default=None, alias="equipment-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Temperature at the monitoring point.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=None)
    qsfp_signal_integrity: QsfpSignalIntegrity | None = Field(json_schema_extra={"is_config": False}, description="Container for QSFP or QSFPxx signal integrity parameters defined in SFF-8636 .", default=None, alias="qsfp-signal-integrity")

class ModulationFormatEnum(str, Enum):
    """Enumeration for ModulationFormatEnum
    
    Values:
      * not-applicable
      * DP-QPSK
      * DP-16QAM
      * DP-8QAM
      * NRZ
      * DP-64QAM
      * DP-SP16QAM
      * DP-QPSK-SP16QAM
      * DP-SP16QAM-16QAM
      * DP-16QAM-32QAM
      * DP-32QAM-64QAM
      * DP-32QAM
      * DP-SPQPSK
      * DP-SPQPSK-QPSK
    """

    NOT_APPLICABLE = "not-applicable"
    DP_QPSK = "DP-QPSK"
    DP_16QAM = "DP-16QAM"
    DP_8QAM = "DP-8QAM"
    NRZ = "NRZ"
    DP_64QAM = "DP-64QAM"
    DP_SP16QAM = "DP-SP16QAM"
    DP_QPSK_SP16QAM = "DP-QPSK-SP16QAM"
    DP_SP16QAM_16QAM = "DP-SP16QAM-16QAM"
    DP_16QAM_32QAM = "DP-16QAM-32QAM"
    DP_32QAM_64QAM = "DP-32QAM-64QAM"
    DP_32QAM = "DP-32QAM"
    DP_SPQPSK = "DP-SPQPSK"
    DP_SPQPSK_QPSK = "DP-SPQPSK-QPSK"

class LineEncodingEnum(str, Enum):
    """Enumeration for LineEncodingEnum
    
    Values:
      * non-differential
      * differential
    """

    NON_DIFFERENTIAL = "non-differential"
    DIFFERENTIAL = "differential"

class RateClassEnum(str, Enum):
    """Enumeration for RateClassEnum
    
    Values:
      * 10G
      * 11G
      * 100G
      * 150G
      * 200G
      * 300G
      * 400G
      * 500G
      * 600G
      * 250G
      * 350G
      * 450G
      * 550G
    """

    _10G = "10G"
    _11G = "11G"
    _100G = "100G"
    _150G = "150G"
    _200G = "200G"
    _300G = "300G"
    _400G = "400G"
    _500G = "500G"
    _600G = "600G"
    _250G = "250G"
    _350G = "350G"
    _450G = "450G"
    _550G = "550G"

class CdCompensationModeEnum(str, Enum):
    """Enumeration for CdCompensationModeEnum
    
    Values:
      * auto: CD auto search by system
      * manual: CD manual setting by user
    """

    AUTO = "auto"
    MANUAL = "manual"

class DifferentialGroupDelay(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for differential group delay, corresponding to pm parameter DGD"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, default=None)

class ChromaticDispersion(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for chromatic dispersion, corresponding to pm parameter CD"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Osnr(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for osnr, corresponding to pm parameter OSNR"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class QFactor(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for q-factor, corresponding to pm parameter Q-factor"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class PolarizationDependentLoss(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for polarization dependent loss, corresponding to pm parameter PDL"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class InOpticalFrequency(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for RX optical frequency, corresponding to pm parameter OFT"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, default=None)

class OutOpticalFrequency(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for TX optical frequency, corresponding to pm parameter OFR"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, default=None)

class SopChangeRate(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for SOP change rate, corresponding to pm parameter SOP"""

    instant: int | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", ge=0, default=None)
    avg: int | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", ge=0, default=None)
    min: int | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", ge=0, default=None)
    max: int | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", ge=0, default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    loss_of_signal_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for signal loss, corresponding to pm parameter loss", ge=0, le=18446744073709551615, default=None, alias="loss-of-signal-seconds")
    bit_error_fec: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics bits counting for error bit forward error correction, corresponding to pm parameter BE-FEC\n\nCondition (when): ../../port-mode != 'QPSK_100G_TRANSPARENT'", ge=0, le=18446744073709551615, default=None, alias="bit-error-fec")
    uncorrected_block_error_fec: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics blocks counting for uncorrected block error forward error correction, corresponding to pm parameter UBE-FEC\n\nCondition (when): ../../port-mode != 'QPSK_100G_TRANSPARENT'", ge=0, le=18446744073709551615, default=None, alias="uncorrected-block-error-fec")
    differential_group_delay: DifferentialGroupDelay | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for differential group delay, corresponding to pm parameter DGD", default=None, alias="differential-group-delay")
    chromatic_dispersion: ChromaticDispersion | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for chromatic dispersion, corresponding to pm parameter CD", default=None, alias="chromatic-dispersion")
    osnr: Osnr | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for osnr, corresponding to pm parameter OSNR", default=None)
    q_factor: QFactor | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for q-factor, corresponding to pm parameter Q-factor", default=None, alias="q-factor")
    polarization_dependent_loss: PolarizationDependentLoss | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for polarization dependent loss, corresponding to pm parameter PDL", default=None, alias="polarization-dependent-loss")
    in_optical_frequency: InOpticalFrequency | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical frequency, corresponding to pm parameter OFT", default=None, alias="in-optical-frequency")
    out_optical_frequency: OutOpticalFrequency | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical frequency, corresponding to pm parameter OFR", default=None, alias="out-optical-frequency")
    sop_change_rate: SopChangeRate | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for SOP change rate, corresponding to pm parameter SOP", default=None, alias="sop-change-rate")
    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")
    bit_error_rate_pre_fec: BitErrorRatePreFec | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for bit error rate before fec, corresponding to pm parameter BER-FEC", default=None, alias="bit-error-rate-pre-fec")
    bit_error_rate_post_fec: BitErrorRatePostFec | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for bit error rate post fec, corresponding to pm parameter BER-POST-FEC", default=None, alias="bit-error-rate-post-fec")

class Otuc4(YangBaseModel):
    """Represents the otuc6 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=518170, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otuc5(YangBaseModel):
    """Represents the otuc5 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=647712, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otuc7(YangBaseModel):
    """Represents the otuc7 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=906797, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otuc9(YangBaseModel):
    """Represents the otuc9 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=1165881, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class Otuc11(YangBaseModel):
    """Represents the otuc11 object"""

    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of client OTUk.\n\nCondition (when): (ancestor::port/port-type = 'client') or (ancestor::port/port-type = 'client-subport')", default=OtukFecEnum.G709, alias="fec-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    exp_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-sapi")
    exp_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="exp-dapi")
    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_sapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-sapi")
    tx_dapi: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="tx-dapi")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    tim_defect_mode: TimModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The tim defect selection mode", default=TimModeEnum.NONE, alias="tim-defect-mode")
    tim_act: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of inserting AIS by tim function", default=EnableSwitchEnum.DISABLED, alias="tim-act")
    rx_sapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received sapi(Source Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-sapi")
    rx_dapi: str | None = Field(json_schema_extra={"is_config": False}, description="The received dapi(Destination Access Point Identifier)", min_length=0, max_length=15, default=None, alias="rx-dapi")
    rx_operator: str | None = Field(json_schema_extra={"is_config": False}, description="The received operator TTI", min_length=0, max_length=32, default=None, alias="rx-operator")
    port_bandwidth: int | None = Field(json_schema_extra={"is_config": True}, description="port cost bandwidth in chip side, for the capacity validation in card like chm2", ge=0, default=0, alias="port-bandwidth")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    degrade_interval: int | None = Field(json_schema_extra={"is_config": True}, description="The consecutive number of 1s intervals with the number of detected block errors exceeding the block error threshold for each of those seconds for the purposes of SDBER detection.", ge=2, le=10, default=7, alias="degrade-interval")
    degrade_threshold: int | None = Field(json_schema_extra={"is_config": True}, description="The threshold number of block errors at which a 1s interval will be considered degraded for the purposes of SDBER detection.", ge=1, le=2590845, default=1424967, alias="degrade-threshold")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class OchOs(YangBaseModel):
    """Represents the och-os MO"""

    modulation_format: ModulationFormatEnum = Field(json_schema_extra={"is_config": True}, description="Currently och-os modulation format", alias="modulation-format")
    line_encoding: LineEncodingEnum | None = Field(json_schema_extra={"is_config": False}, description="Currently line-encoding mode", default=LineEncodingEnum.NON_DIFFERENTIAL, alias="line-encoding")
    rate_class: RateClassEnum = Field(json_schema_extra={"is_config": True}, description="Carried OTN signal basic rate class", alias="rate-class")
    frequency: int | None = Field(json_schema_extra={"is_config": True}, description="The laser frequency. For tx-lo-independent laser-type, it set the tx laser frequency only.", le=196111250, ge=0, default=0)
    actual_frequency: int | None = Field(json_schema_extra={"is_config": False}, description="The actual laser frequency.\nIf rx-frequency is 0, it reflects both Rx and Tx frequency for coherent interface.", ge=0, default=0, alias="actual-frequency")
    rx_frequency: int | None = Field(json_schema_extra={"is_config": True}, description="The rx laser frequency. Special for 0 means it is same as tx laser frequency.\n\nCondition (when): ../../possible-pluggable-types != 'SFP+'", le=196111250, ge=0, default=0, alias="rx-frequency")
    actual_rx_frequency: int | None = Field(json_schema_extra={"is_config": False}, description="The actual rx laser frequency for coherent interface with separating Lo laser from Tx.\n0 means Lo and Tx share the same laser where 'frequency' attriute will indicate both Tx and Rx.\n\nCondition (when): ../../possible-pluggable-types != 'SFP+'", ge=0, default=0, alias="actual-rx-frequency")
    laser_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of output laser.", default=EnableSwitchEnum.DISABLED, alias="laser-enable")
    required_tx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="This is to support adjustable optical power of Line side.", default=1.0, alias="required-tx-optical-power")
    actual_tx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="This is the actual transmitting optical power of Line side.", default=-99.0, alias="actual-tx-optical-power")
    fec_type: OtukFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC type of och-os", default=OtukFecEnum.SDFEC25, alias="fec-type")
    rx_attenuation: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="This is to support configurable optical attenuation at receiver side which is based on the hardware capability on the port.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=0.0, alias="rx-attenuation")
    tx_filter_roll_off: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Transmitter filter roll off factor.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", ge=0.01, le=1.0, default=None, alias="tx-filter-roll-off")
    preemphasis: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Preemphasis of transmitted signal.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=EnableSwitchEnum.ENABLED)
    preemphasis_value: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Preemphasis of transmitted signal.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=1.0, alias="preemphasis-value")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    DGD: int | None = Field(json_schema_extra={"is_config": False}, description="Value of Differential Group Delay\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", ge=0, default=None)
    CD: int | None = Field(json_schema_extra={"is_config": False}, description="Value of Chromatic Dispersion\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=None)
    OSNR: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Current value of OSNR.\nThe result could be OSNR value with dB\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=None)
    Q_factor: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Current value of Q-factor\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=None, alias="Q-factor")
    pre_fec_ber: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Current value of PreFEC Bit Error Ratio.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=-99.0, alias="pre-fec-ber")
    cd_range_low: int | None = Field(json_schema_extra={"is_config": True}, description="low value of chromatic dispersion search range.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=-45000, alias="cd-range-low")
    cd_range_high: int | None = Field(json_schema_extra={"is_config": True}, description="high value of chromatic dispersion search range.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=45000, alias="cd-range-high")
    cd_compensation_mode: CdCompensationModeEnum | None = Field(json_schema_extra={"is_config": True}, description="chromatic dispersion compensation value source mode\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=CdCompensationModeEnum.AUTO, alias="cd-compensation-mode")
    cd_compensation_value: int | None = Field(json_schema_extra={"is_config": True}, description="manual chromatic dispersion compensation value\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=None, alias="cd-compensation-value")
    fast_sop_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if enable fast SOP (state of polarization) change tracking; if enabled, the interface\nwill tolerate very fast SOP and transient.\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", default=EnableSwitchEnum.DISABLED, alias="fast-sop-mode")
    BICHM: int | None = Field(json_schema_extra={"is_config": True}, description="The BICHM (bit interleaved coded hybrid modulation) incremental step in 1/128 bits/symbol added to base modulation bits/symbol for the hybrid modes modulation-format.\n0: Base modulation format bits/symbol;\n1: 1/128 bits/symbol added to base modulation format bits/symbol;\n...\n127: 127/128 bits/symbol added to base modulation format bits/symbol\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", ge=0, le=127, default=64)
    SOP_vector: str | None = Field(json_schema_extra={"is_config": False}, description="The RX SOP (State Of Polarization) Stokes Vector S1 S2 S3\nS1: the degree of linearly polarized light aligned to horizontal (X) axis\nS2: the degree of linearly polarized light aligned to +45 degree axis\nS3: the degree of righthand circularly polarized light\n\nCondition (when): ../possible-pluggable-types != 'SFP+'", min_length=0, max_length=18, default=None, alias="SOP-vector")
    propagate_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="When the attribute value is set to yes, the transmit laser will\nbe shutdown if the whole service of the direction has signal failure,\nthe function mainly used in regeneration node to propagate signal failure as LOS.\n\nCondition (when): ancestor::card/card-mode =  'regen'", default=YesNoEnum.NO, alias="propagate-shutdown")
    propagate_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of propagate shutdown.\n\nCondition (when): ancestor::card/card-mode =  'regen'", ge=0, le=2000, default=0, alias="propagate-shutdown-holdoff-timer")
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    otuc2: Otuc2 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc2 object", default=None)
    otuc3: Otuc3 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc3 object", default=None)
    otuc4: Otuc4 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc6 object", default=None)
    otuc5: Otuc5 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc5 object", default=None)
    otuc6: Otuc6 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc6 object", default=None)
    otuc7: Otuc7 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc7 object", default=None)
    otuc9: Otuc9 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc9 object", default=None)
    otuc11: Otuc11 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otuc11 object", default=None)
    otu4: Otu4 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu4 object", default=None)
    otu2: Otu2 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu2 object", default=None)
    otu2e: Otu2e | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu2e object", default=None)

class OtdrMeasurementSpeedEnum(str, Enum):
    """Enumeration for OtdrMeasurementSpeedEnum
    
    Values:
      * fast: Fast speed.
      * medium: Medium speed.
      * slow: Slow speed.
      * precision: Very slow speed for precise result.
      * auto: indicates that the measurement speed shall be selected automatically.
      * high-precision: The slowest speed for high precise result.
    """

    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    PRECISION = "precision"
    AUTO = "auto"
    HIGH_PRECISION = "high-precision"

class OtdrFiberTypeEnum(str, Enum):
    """Enumeration for OtdrFiberTypeEnum
    
    Values:
      * Unknown
      * SSMF
      * LEAF
      * TWRS
      * TWC
      * Allwave
      * DSF
      * LS
      * PureSilica
      * TWReach
      * VistaCor
      * Teralight
      * DrakaLL
      * TWPlus
      * TWMinus
      * PSLC
      * auto
    """

    UNKNOWN = "Unknown"
    SSMF = "SSMF"
    LEAF = "LEAF"
    TWRS = "TWRS"
    TWC = "TWC"
    ALLWAVE = "Allwave"
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
    AUTO = "auto"

class OtdrPort(YangBaseModel):
    """Containing attributes of OTDR port."""

    otdr_range: str | float | None = Field(json_schema_extra={"is_config": True}, description="OTDR measurement range.", default="auto", alias="otdr-range")
    otdr_pulse_width: str | int | None = Field(json_schema_extra={"is_config": True}, description="Indicates pulse width to be used in otdr measurement.", default="auto", alias="otdr-pulse-width")
    otdr_measurement_speed: OtdrMeasurementSpeedEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicating OTDR measurement speed.", default=OtdrMeasurementSpeedEnum.AUTO, alias="otdr-measurement-speed")
    otdr_ior: str | float | None = Field(json_schema_extra={"is_config": True}, description="Specifies the group index of refraction (IOR) of the fiber to be measured.", default="auto", alias="otdr-ior")
    otdr_fiber_type: OtdrFiberTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicating fiber type to be measured.", default=OtdrFiberTypeEnum.AUTO, alias="otdr-fiber-type")
    otdr_resolution: str | float | None = Field(json_schema_extra={"is_config": True}, description="Specifies the OTDR data sampling resolution.", default="auto", alias="otdr-resolution")
    otdr_last_measurement: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Indicates the last otdr measurement date and time on the port.", default="0000-01-01T00:00:00.00Z", alias="otdr-last-measurement")
    launching_fiber_length: str | float | None = Field(json_schema_extra={"is_config": True}, description="The launching fiber length information for SOR to filter the launching fiber path data", default="0", alias="launching-fiber-length")

class GridTypeEnum(str, Enum):
    """Enumeration for GridTypeEnum
    
    Values:
      * not-applicable: Grid is not defined.
      * fixed_50G_96ch: 50GHz fixed grid with 96 channels in C-band.
      * fixed_100G_48ch: 100GHz fixed grid with 48 channels in C-band.
      * fixed_75G_64ch: 75GHz fixed grid with 64 channels in C-band.
      * flexible: Flexible grid.
      * fixed_75G_64ch_OIF: OIF 75GHz fixed grid with 64 channels in C-band.
    """

    NOT_APPLICABLE = "not-applicable"
    FIXED_50G_96CH = "fixed_50G_96ch"
    FIXED_100G_48CH = "fixed_100G_48ch"
    FIXED_75G_64CH = "fixed_75G_64ch"
    FLEXIBLE = "flexible"
    FIXED_75G_64CH_OIF = "fixed_75G_64ch_OIF"

class ChannelBaudRateEnum(str, Enum):
    """Enumeration for ChannelBaudRateEnum
    
    Values:
      * low: 39GHz threshold with 1dB bandwidth
      * high: 66GHz threshold with 1dB bandwidth
      * user-defined
    """

    LOW = "low"
    HIGH = "high"
    USER_DEFINED = "user-defined"

class MonitoredChannelsItem(YangBaseModel):
    """List of monitored channels"""

    frequency_index: int = Field(json_schema_extra={"is_config": False}, description="Nominal center frequency as index with unit of MHz.", le=196111250, ge=0, alias="frequency-index")
    channel_id: int | None = Field(json_schema_extra={"is_config": False}, description="the optical och index.", ge=0, default=None, alias="channel-id")
    monitored_center_frequency: int | None = Field(json_schema_extra={"is_config": False}, description="Monitored channel center frequency.", le=196111250, ge=0, default=None, alias="monitored-center-frequency")
    monitored_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Monitored channel optical power.", default=None, alias="monitored-optical-power")
    monitored_width: str | int | None = Field(json_schema_extra={"is_config": False}, description="Monitored frequency width with unit MHz.", default="not-available", alias="monitored-width")

class OcmPort(YangBaseModel):
    """Containing attributes of OCM port."""

    ocm_port_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enable or disable the function of ocm port measurement.", default=None, alias="ocm-port-enable")
    grid_mode: GridTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates Grid type of the OMS.", default=GridTypeEnum.NOT_APPLICABLE, alias="grid-mode")
    grid_offset: int | None = Field(json_schema_extra={"is_config": True}, description="Indicates channel frequency offset to standard grid.", default=0, alias="grid-offset")
    optical_power_offset: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The offset to calibrate Optical power of monitored channels, resulted value = monitored value + offset.", default=None, alias="optical-power-offset")
    channel_baud_rate: ChannelBaudRateEnum | None = Field(json_schema_extra={"is_config": True}, description="The baud rate selection for monitored optical channel", default=None, alias="channel-baud-rate")
    ppa_1dB_BW: int | None = Field(json_schema_extra={"is_config": True}, description="The channel baud rate with 1dB bandwidth working for user-defined channel-baud-rate", ge=0, default=None, alias="ppa-1dB-BW")
    monitored_channels: RestconfList[MonitoredChannelsItem] | None = Field(json_schema_extra={"is_config": False}, description="List of monitored channels", default=None, alias="monitored-channels")

class InOpticalPowerLaneHigh(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for highest value of RX lane optical power, corresponding to pm parameter OPR-lane-high"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class InOpticalPowerLaneLow(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for lowest value of RX lane optical power, corresponding to pm parameter OPR-lane-low"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class InOpticalPowerLaneTotal(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for total value of RX lane optical power, corresponding to pm parameter OPR-lane-total"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutOpticalPowerLaneHigh(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for highest value of TX lane optical power, corresponding to pm parameter OPR-lane-high"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutOpticalPowerLaneLow(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for lowest value of TX lane optical power, corresponding to pm parameter OPR-lane-low"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutOpticalPowerLaneTotal(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for total value of TX lane optical power, corresponding to pm parameter OPR-lane-total"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    in_optical_power_lane_high: InOpticalPowerLaneHigh | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for highest value of RX lane optical power, corresponding to pm parameter OPR-lane-high", default=None, alias="in-optical-power-lane-high")
    in_optical_power_lane_low: InOpticalPowerLaneLow | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for lowest value of RX lane optical power, corresponding to pm parameter OPR-lane-low", default=None, alias="in-optical-power-lane-low")
    in_optical_power_lane_total: InOpticalPowerLaneTotal | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for total value of RX lane optical power, corresponding to pm parameter OPR-lane-total", default=None, alias="in-optical-power-lane-total")
    out_optical_power_lane_high: OutOpticalPowerLaneHigh | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for highest value of TX lane optical power, corresponding to pm parameter OPR-lane-high", default=None, alias="out-optical-power-lane-high")
    out_optical_power_lane_low: OutOpticalPowerLaneLow | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for lowest value of TX lane optical power, corresponding to pm parameter OPR-lane-low", default=None, alias="out-optical-power-lane-low")
    out_optical_power_lane_total: OutOpticalPowerLaneTotal | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for total value of TX lane optical power, corresponding to pm parameter OPR-lane-total", default=None, alias="out-optical-power-lane-total")
    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")

class DuplexEnum(str, Enum):
    """Enumeration for DuplexEnum
    
    Values:
      * half: half duplex
      * full: full duplex
    """

    HALF = "half"
    FULL = "full"

class AutoNegotiationEnum(str, Enum):
    """Enumeration for AutoNegotiationEnum
    
    Values:
      * enabled: Auto Negotiation enabled
      * disabled: Auto Negotiation disabled
    """

    ENABLED = "enabled"
    DISABLED = "disabled"

class Eth1g(YangBaseModel):
    """Container: eth1g"""

    eth_fec_type: EthFecEnum | None = Field(json_schema_extra={"is_config": True}, description="The FEC working type of etyn port.", default=EthFecEnum.AUTO, alias="eth-fec-type")
    eth_fec_type_state: EthFecEnum | None = Field(json_schema_extra={"is_config": False}, description="The FEC working state of etyn port.", default=EthFecEnum.DISABLED, alias="eth-fec-type-state")
    transmit_interpacketgap: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the minimum transmit IPG value.", ge=8, le=12, default=8, alias="transmit-interpacketgap")
    gfp_payload_fcs: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enabled: GFP payload FCS will be used, Ethernet frame FCS will be removed;\nDisabled: GFP payload FCS will not be inserted, Ethernet frame FCS will be used.", default=EnableSwitchEnum.DISABLED, alias="gfp-payload-fcs")
    mapping_mode: MappingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The mapping mode of client port packets into ODUk.", default=MappingModeEnum.NOT_APPLICABLE, alias="mapping-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    client_shutdown: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of client-shutdown.", default=YesNoEnum.NO, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of client shutdown or replacement siganl at egress direction.", ge=0, le=2000, default=0, alias="client-shutdown-holdoff-timer")
    holdoff_signal: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify if specific signal will be sent out during hold off time\nwhich avoid downstream equipment consequent action in the duration.", default=YesNoEnum.NO, alias="holdoff-signal")
    near_end_als: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of near end ALS.", default=YesNoEnum.NO, alias="near-end-als")
    als_degrade_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The switching of defect BERSD-ODU trig ALS", default=EnableSwitchEnum.DISABLED, alias="als-degrade-mode")
    loopback_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of loopback function.", default=EnableSwitchEnum.DISABLED, alias="loopback-enable")
    loopback_type: LoopbackTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of loopback function", default=LoopbackTypeEnum.NONE, alias="loopback-type")
    test_signal_type: TestSignalTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The type mode of test signal.", default=TestSignalTypeEnum.NONE, alias="test-signal-type")
    test_signal_enable: TestSignalConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The enable switching of test signal function", default=TestSignalConfigEnum.NONE, alias="test-signal-enable")
    test_signal_facility_status: TestSignalFacilityStatus | None = Field(json_schema_extra={"is_config": False}, description="Test signal status for current facility.", default=None, alias="test-signal-facility-status")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    index: str | None = Field(json_schema_extra={"is_config": True}, description="Index of the current logical client channel to tributary mapping", default=None)
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    connected_interface: str | None = Field(json_schema_extra={"is_config": True}, default="none", alias="connected-interface")
    lldp_status_if: LldpStatusIfEnum | None = Field(json_schema_extra={"is_config": True}, description="Port level lldp control.\nValue of 'rxonly', then the LLDP agent will receive lldp,\nwhen lldp-status-ne is also enabled.\n\nValue of 'disabled', then LLDP agent will not filter and\nreceive LLDP frames on this port.  If there is remote systems\ninformation which is received on this port and stored in\nthe system before the lldp-status   becomes disabled,\nthen the information will naturally age out.\n\nNote: txOnly and txAndRx modes are not supported in Transponder module.", default=LldpStatusIfEnum.DISABLED, alias="lldp-status-if")
    lldp_remote_system: RestconfList[LldpRemoteSystemItem] | None = Field(json_schema_extra={"is_config": True}, description="List of LLDP neighbors.", default=None, alias="lldp-remote-system")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    mac_address: str | None = Field(json_schema_extra={"is_config": True}, description="The MAC address of the port for L2CP", default=None, alias="mac-address")
    speed: int | None = Field(json_schema_extra={"is_config": True}, description="Set speed of the interface, unit mbps.\nThis is for ETH facility.", ge=0, default=1000)
    duplex: DuplexEnum | None = Field(json_schema_extra={"is_config": True}, description="Set duplex selections.", default=DuplexEnum.FULL)
    mtu: int | None = Field(json_schema_extra={"is_config": True}, description="Set Maximum Frame Size.", ge=1280, le=1500, default=1500)
    auto_negotiation: AutoNegotiationEnum | None = Field(json_schema_extra={"is_config": True}, description="Set Auto Negotiation: Enabled/Disabled.", default=AutoNegotiationEnum.ENABLED, alias="auto-negotiation")
    curr_speed: str | None = Field(json_schema_extra={"is_config": False}, description="speed (UNKNOWN/AUTO/10/100/1000/10000) corresponding to the interface", default=None, alias="curr-speed")
    curr_duplex: str | None = Field(json_schema_extra={"is_config": False}, description="duplex (HALF/FULL) corresponding to the interface", default=None, alias="curr-duplex")
    odu: RestconfList[OduItem] | None = Field(json_schema_extra={"is_config": True}, description="Condition (when): (../port-type != 'osc') and (../port-type != 'mgmt-eth')", default=None)

class PortItem(YangBaseModel):
    """List: port"""

    port_id: int = Field(json_schema_extra={"is_config": True}, description="The identifier is defined to uniquely identify the port.", ge=0, alias="port-id")
    possible_pluggable_types: RestconfList[PluggableTypeEnum] | None = Field(json_schema_extra={"is_config": False}, description="Defined all the pluggable types which can be equipped on the port.\nNeeds to be re-defined in the project specific model.\n\nCondition (when): (../port-type != 'optical') and (../port-type != 'otdr') and (../port-type != 'optical-nomon') and (../port-type != 'ocm') and (../port-type != 'mgmt-eth')", default=None, alias="possible-pluggable-types")
    actual_pluggable_type: EquipmentTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Pluggable type for each port according to the actually equipping.\nNeeds to be re-defined in the project specific model.\n\nCondition (when): (../port-type != 'optical') and (../port-type != 'ocm') and (../port-type != 'optical-nomon') and (../port-type != 'otdr') and (../port-type != 'mgmt-eth')", default=EquipmentTypeEnum.EMPTY, alias="actual-pluggable-type")
    defect_optical_loss: bool | None = Field(json_schema_extra={"is_config": False}, description="defect optical loss for the partner ports", default=None, alias="defect-optical-loss")
    rx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Received optical power\n\nCondition (when): (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'mgmt-eth') and (direction-type != 'tx')", default=None, alias="rx-optical-power")
    tx_optical_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power\n\nCondition (when): (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'mgmt-eth') and (direction-type != 'rx')", default=None, alias="tx-optical-power")
    rx_optical_power_selected_channel: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Optical power of the selected channel on coherent receiver,\nwhich will be different from the rx-optical-power when multiple channels input simultaneously.\n\nCondition (when): (port-type = 'line') and (possible-pluggable-types != 'SFP+')", default=None, alias="rx-optical-power-selected-channel")
    optical_power_lane: RestconfList[OpticalPowerLaneItem] | None = Field(json_schema_extra={"is_config": False}, description="Condition (when): (port-type = 'client') and (possible-pluggable-types != 'SFP+')", default=None, alias="optical-power-lane")
    direction_type: TypeOfDirectionEnum | None = Field(json_schema_extra={"is_config": False}, description="Supported direction of the optical port.\n\nCondition (when): (port-type = 'optical') or (port-type = 'otdr') or (port-type = 'optical-nomon') or (port-type = 'ocm')", default=None, alias="direction-type")
    subport: RestconfList[SubportItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    pluggable: Pluggable | None = Field(json_schema_extra={"is_config": True}, description="Represents the Pluggable object\n\nCondition (when): (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'optical') and (port-type != 'mgmt-eth')", default=None)
    och_os: OchOs | None = Field(json_schema_extra={"is_config": True}, description="Represents the och-os MO\n\nCondition (when): (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm') and (port-type != 'optical') and (port-type != 'mgmt-eth')", default=None, alias="och-os")
    port_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The name of the port.", min_length=1, max_length=32, default="unspecified", alias="port-name")
    port_type: PortTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="The type of port. Needs to be provided upon Port creation", default=PortTypeEnum.OPTICAL_NOMON, alias="port-type")
    port_mode: PortModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The working mode of port.\nFor client side:\nCHM1: applicable to port 3 to 6; possible values are: 100GBE, not-applicable.\nDefault is 100GBE when card created.\n\nCHM2: applicable to port 3 to 11; possible values are: 40GBE, subport, not-applicable;\napplicable to subport 1 to 4; possible values are: 10GBE, not-applicable.\nDefault is not-applicable.\n       \nFor Line side:\nCHM1/CHM2: possible values are: QPSK_100G, 16QAM_200G, 8QAM_300G.\nDefault is 16QAM_200G.\n\nnon applicable : there shall not be service created on the port or subport\nsubport: the port shall create four subports under the port to support 4x10G.\n40GBE: 40GBE service shall be created on the port with default mapping GMP.\n10GBE: 10GBE service shall be created on the subport with default mapping BMP with fixed stuff.\n100GBE: 100GBE service shall be created on the subport with default mapping GMP.\nQPSK_100G: 100G OTU4 service with DP-QPSK coherent modulation format shall be created on the port.\n16QAM_200G: 200G OTUC2 service with DP-16QAM coherent modulation format shall be created on the port.\n8QAM_300G: 300G OTUC3 service with DP-8QAM coherent modulation format shall be created on the coupled two line ports.\n\nNote 4x10G is to create subport managed objects under the port. Each subport can support a 10G service.\n       \nRestrictions:\nChanging Port mode shall be allowed only if the impacted port or subport object is administratively down.\nChanging a 'subport' port mode of a port to be other value shall only be allowed only if port-modes of all the subports under the port are 'not-applicable'.\nIf there is explicitly cross-connection is created associated with the ODU of the port, change port mode of the port shall be denied.\nIf the port mode is a coupled port mode, e.g. 8QAM_300G, port mode can only be edited on the lower number of port within the coupled ports. The other port (or ports if more than two) will have read-only port mode value same as this lowest number port.\nWhen port/subport is set to admin down, laser will be shutdown, ingress side will insert proper maintenance signal.\n\nCondition (when): (../port-type = 'line') or (../port-type = 'client') or (../port-type = 'client-subport')", default=PortModeEnum.NOT_APPLICABLE, alias="port-mode")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    connected_to: str | None = Field(json_schema_extra={"is_config": True}, description="Indicate neighbour port/facility entity to which the current port/facility is connected to.", min_length=0, max_length=128, default=None, alias="connected-to")
    external_connectivity: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the port is connected externally or not.", default=YesNoEnum.NO, alias="external-connectivity")
    arc_config: ArcConfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The configurable mode of the Alarm Report Control (ARC).\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default=ArcConfigEnum.NALM_QI, alias="arc-config")
    arc_state: ArcConfigEnum | None = Field(json_schema_extra={"is_config": False}, description="The current mode of the Alarm Report Control (ARC).\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default=ArcConfigEnum.NALM_QI, alias="arc-state")
    arc_sub_state: ArcSubStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Additional information about the Alarm Report Control (ARC) when the main state is in the NALM-QI state\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default=ArcSubStateEnum.NALM_NR, alias="arc-sub-state")
    arc_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The holdoff timer value in minutes of the ARC.\nRange is 0 - 10080 minutes\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", ge=0, le=10080, default=1440, alias="arc-timer")
    arc_remaining_time: str | None = Field(json_schema_extra={"is_config": False}, description="The remaining timer value (format: xxd-xxh:xxm:xxs) before the alarm is reported.\n\nCondition (when): (port-type = 'client') or (port-type = 'client-subport')", default="00d-00h:00m:00s", alias="arc-remaining-time")
    eth10g: Eth10g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 10GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    eth40g: Eth40g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 40GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    eth100g: Eth100g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 100GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    eth400g: Eth400g | None = Field(json_schema_extra={"is_config": True}, description="Represents the 400GBE object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otu4: Otu4 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu4 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otu2: Otu2 | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu2 object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otu2e: Otu2e | None = Field(json_schema_extra={"is_config": True}, description="Represents the otu2e object\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    oc192: Oc192 | None = Field(json_schema_extra={"is_config": True}, description="Represents the OC192 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    oc48: Oc48 | None = Field(json_schema_extra={"is_config": True}, description="Represents the OC48 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    stm64: Stm64 | None = Field(json_schema_extra={"is_config": True}, description="Represents the STM64 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    stm16: Stm16 | None = Field(json_schema_extra={"is_config": True}, description="Represents the STM16 object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    wan10g_sonet: Wan10gSonet | None = Field(json_schema_extra={"is_config": True}, description="Represents the 10GWAN_SONET object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None, alias="wan10g-sonet")
    wan10g_sdh: Wan10gSdh | None = Field(json_schema_extra={"is_config": True}, description="Represents the 10GWAN_SDH object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None, alias="wan10g-sdh")
    fc1g: Fc1g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC1G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    fc4g: Fc4g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC4G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    fc8g: Fc8g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC8G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    fc16g: Fc16g | None = Field(json_schema_extra={"is_config": True}, description="Represents the FC16G object.\n\nCondition (when): (port-type != 'optical') and (port-type != 'otdr') and (port-type != 'optical-nomon') and (port-type != 'ocm')", default=None)
    otdr_port: OtdrPort | None = Field(json_schema_extra={"is_config": True}, description="Containing attributes of OTDR port.", default=None, alias="otdr-port")
    ocm_port: OcmPort | None = Field(json_schema_extra={"is_config": True}, description="Containing attributes of OCM port.\n\nCondition (when): ../port-type = 'ocm'", default=None, alias="ocm-port")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)
    eth1g: Eth1g | None = Field(json_schema_extra={"is_config": True}, default=None)

class ControlModeEnum(str, Enum):
    """Enumeration for ControlModeEnum
    
    Values:
      * manual
      * auto
      * auto-max-pw
    """

    MANUAL = "manual"
    AUTO = "auto"
    AUTO_MAX_PW = "auto-max-pw"

class AmplifierModeEnum(str, Enum):
    """Enumeration for AmplifierModeEnum
    
    Values:
      * constant-power
      * constant-gain
    """

    CONSTANT_POWER = "constant-power"
    CONSTANT_GAIN = "constant-gain"

class GainRangeControlEnum(str, Enum):
    """Enumeration for GainRangeControlEnum
    
    Values:
      * manual
      * auto
    """

    MANUAL = "manual"
    AUTO = "auto"

class GainRangeTypeEnum(str, Enum):
    """Enumeration for GainRangeTypeEnum
    
    Values:
      * standard: Single range amplifier working range
      * low: The low range for multi working range
      * high: The high range for multi working range
      * not-available: amplifier working range is unknown
    """

    STANDARD = "standard"
    LOW = "low"
    HIGH = "high"
    NOT_AVAILABLE = "not-available"

class SupportedGainRangeItem(YangBaseModel):
    """List: supported-gain-range"""

    range_type: GainRangeTypeEnum = Field(json_schema_extra={"is_config": False}, description="The type of gain range for manually setting", alias="range-type")
    gain_range_min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The minimum of settable gain for this range type", default=None, alias="gain-range-min")
    gain_range_max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The maxmum of settable gain for this range type", default=None, alias="gain-range-max")

class AmplifierTypeEnum(str, Enum):
    """Enumeration for AmplifierTypeEnum
    
    Values:
      * fixed-gain-EDFA
      * variable-gain-EDFA
    """

    FIXED_GAIN_EDFA = "fixed-gain-EDFA"
    VARIABLE_GAIN_EDFA = "variable-gain-EDFA"

class TiltControlModeEnum(str, Enum):
    """Enumeration for TiltControlModeEnum
    
    Values:
      * manual: Manually control amplifier tilt.
      * auto: System implicitly control amplifier tilt per configured fiber parameters.
      * auto-planned: System implicitly control amplifier tilt per planning tool configured parameters.
    """

    MANUAL = "manual"
    AUTO = "auto"
    AUTO_PLANNED = "auto-planned"

class AmplifierItem(YangBaseModel):
    """The list of optical amplifier on an equipment."""

    amplifier_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="User-defined name assigned to identify a specific amplifier in the device", min_length=1, max_length=32, alias="amplifier-name")
    supporting_input_port: str | None = Field(json_schema_extra={"is_config": True}, description="Identifier of the supporting input port.", default=None, alias="supporting-input-port")
    supporting_output_port: str | None = Field(json_schema_extra={"is_config": True}, description="Identifier of the supporting output port.", default=None, alias="supporting-output-port")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    amplifier_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Configuration for enable or disable the amplifier.", default=EnableSwitchEnum.DISABLED, alias="amplifier-enable")
    pump_status: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": False}, description="The amplifier's pump working status, enable or disable", default=EnableSwitchEnum.DISABLED, alias="pump-status")
    input_los_shutdown: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enable or disable the function of automatic shutdown per input LOS.", default=EnableSwitchEnum.ENABLED, alias="input-los-shutdown")
    control_mode: ControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Control mode of the amplifier.", default=None, alias="control-mode")
    amplifier_mode: AmplifierModeEnum | None = Field(json_schema_extra={"is_config": False}, description="The operating mode of the amplifier", default=AmplifierModeEnum.CONSTANT_GAIN, alias="amplifier-mode")
    gain_range_control: GainRangeControlEnum | None = Field(json_schema_extra={"is_config": True}, description="The gain range working mode for multi gain range supported amplifier", default=GainRangeControlEnum.AUTO, alias="gain-range-control")
    target_gain_range: GainRangeTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The gain-range selected one for manual gain-range-mode", default=GainRangeTypeEnum.STANDARD, alias="target-gain-range")
    working_gain_range: GainRangeTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="The current working gain range", default=GainRangeTypeEnum.NOT_AVAILABLE, alias="working-gain-range")
    supported_gain_range: RestconfList[SupportedGainRangeItem] | None = Field(json_schema_extra={"is_config": False}, default=None, alias="supported-gain-range")
    amplifier_type: AmplifierTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Type of the amplifier.", default=AmplifierTypeEnum.VARIABLE_GAIN_EDFA, alias="amplifier-type")
    target_gain: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Setting gain to the amplifier for constant-gain mode in manual control mode.", default=None, alias="target-gain")
    operating_gain: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Operating gain of the amplifier, which is the actually configured gain on the amplifier.", default=None, alias="operating-gain")
    gain_adjustment: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The value is used for adjustment of gain when the amplifier in automatic control mode,\nthe automatically caculated gain will include offset of this attribute.", default=0.0, alias="gain-adjustment")
    output_power_mon: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Monitored aggregation signal output power.", default=None, alias="output-power-mon")
    output_power_mon_with_ase: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Monitored aggregation total output power including both signal and ASE.", default=None, alias="output-power-mon-with-ase")
    input_power_mon: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Monitored aggregation input power.", default=None, alias="input-power-mon")
    output_voa: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Configurable optical attenuation at output of the amplifier.\n\nCondition (when): amplifier-name = 'ba'", default=0.0, alias="output-voa")
    actual_output_voa: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Working optical attenuation at output of the amplifier.\n\nCondition (when): amplifier-name = 'ba'", default=0.0, alias="actual-output-voa")
    power_before_output_voa: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Monitored optical power after output VOA.\n\nCondition (when): amplifier-name = 'ba'", default=None, alias="power-before-output-voa")
    tilt_control_mode: TiltControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify gain tilt control modes.", default=None, alias="tilt-control-mode")
    gain_tilt: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Specify gain tilt of the amplifier.", default=0.0, alias="gain-tilt")
    actual_gain_tilt: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Actually setting of gain tilt on the amplifier.", default=0.0, alias="actual-gain-tilt")
    partner_amp: str | None = Field(json_schema_extra={"is_config": False}, description="The partner amplifier for in line amplifier working mode.", default="not-available", alias="partner-amp")
    egress_average_channel_power: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Based upon the total max power across the 4.8 THz passband.\nDefined as optional for ODL support, but shall be considered as mandatory and provided\nby the controller when the control-mode is set to gainLoss for amplifier setting", default=None, alias="egress-average-channel-power")

class TdcItem(YangBaseModel):
    """The list of optical tdc on an equipment."""

    tdc_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="User-defined name assigned to identify a specific tdc in the device", min_length=1, max_length=32, alias="tdc-name")
    supporting_input_port: str | None = Field(json_schema_extra={"is_config": True}, description="Identifier of the supporting input port.", default=None, alias="supporting-input-port")
    supporting_output_port: str | None = Field(json_schema_extra={"is_config": True}, description="Identifier of the supporting output port.", default=None, alias="supporting-output-port")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    tdc_mode: GainRangeControlEnum | None = Field(json_schema_extra={"is_config": True}, description="Control mode of the tunable dispersion compensation; Manual: CD value will be decided per configured CD value;\nAuto: system will automatically decide the CD value per measured chromatic dispersion in the span.", default=GainRangeControlEnum.AUTO, alias="tdc-mode")
    reference_frequency: int | None = Field(json_schema_extra={"is_config": True}, description="Indicating the reference wavelength of the TDC.", le=196111250, ge=0, default=None, alias="reference-frequency")
    actual_reference_frequency: int | None = Field(json_schema_extra={"is_config": False}, description="Indicating the actual reference wavelength of the TDC.", ge=0, default=None, alias="actual-reference-frequency")
    frequency_range_min: int | None = Field(json_schema_extra={"is_config": False}, description="The minimum of supported wavelength.", ge=0, default=None, alias="frequency-range-min")
    frequency_range_max: int | None = Field(json_schema_extra={"is_config": False}, description="The maximum of supported wavelength.", ge=0, default=None, alias="frequency-range-max")
    chromatic_dispersion: int | None = Field(json_schema_extra={"is_config": True}, description="The setting value of Chromatic Dispersion.", default=0, alias="chromatic-dispersion")
    chromatic_dispersion_adjustment: int | None = Field(json_schema_extra={"is_config": True}, description="The value will be used to adjust target chromatic dispersion by adding the value with auto decided dispersion in auto tdc mode.", default=None, alias="chromatic-dispersion-adjustment")
    actual_chromatic_dispersion: int | None = Field(json_schema_extra={"is_config": False}, description="The actual value of Chromatic Dispersion.", default=None, alias="actual-chromatic-dispersion")
    cd_range_min: int | None = Field(json_schema_extra={"is_config": False}, description="The minimum of supported chromatic dispersion.", default=None, alias="cd-range-min")
    cd_range_max: int | None = Field(json_schema_extra={"is_config": False}, description="The maximum of supported chromatic dispersion.", default=None, alias="cd-range-max")

class ProtectionStatusEnum(str, Enum):
    """Enumeration for ProtectionStatusEnum
    
    Values:
      * not-applicable: Not applicable.
      * manual-switch-to-protection: Manual switch to protection.
      * manual-switch-to-working: Manual switch to working.
      * force-switch-to-protection: Force switch to protection.
      * force-switch-to-working: Force switch to working.
      * lockout-of-protection: Lockout of protection.
      * signal-failure-on-working: Signal failure on working.
      * signal-failure-on-protection: Signal failure on protection.
      * signal-degrade-on-working: Signal degrade on working.
      * signal-degrade-on-protection: Signal degrade on protection.
      * do-not-revert: Do not revert.
      * no-request: No request.
      * wait-to-restore: Wait to restore.
    """

    NOT_APPLICABLE = "not-applicable"
    MANUAL_SWITCH_TO_PROTECTION = "manual-switch-to-protection"
    MANUAL_SWITCH_TO_WORKING = "manual-switch-to-working"
    FORCE_SWITCH_TO_PROTECTION = "force-switch-to-protection"
    FORCE_SWITCH_TO_WORKING = "force-switch-to-working"
    LOCKOUT_OF_PROTECTION = "lockout-of-protection"
    SIGNAL_FAILURE_ON_WORKING = "signal-failure-on-working"
    SIGNAL_FAILURE_ON_PROTECTION = "signal-failure-on-protection"
    SIGNAL_DEGRADE_ON_WORKING = "signal-degrade-on-working"
    SIGNAL_DEGRADE_ON_PROTECTION = "signal-degrade-on-protection"
    DO_NOT_REVERT = "do-not-revert"
    NO_REQUEST = "no-request"
    WAIT_TO_RESTORE = "wait-to-restore"

class ActivePathEnum(str, Enum):
    """Enumeration for ActivePathEnum
    
    Values:
      * working
      * protection
      * unknown
    """

    WORKING = "working"
    PROTECTION = "protection"
    UNKNOWN = "unknown"

class WavelengthBandEnum(str, Enum):
    """Enumeration for WavelengthBandEnum
    
    Values:
      * 1550
      * 1310
    """

    _1550 = "1550"
    _1310 = "1310"

class OpsItem(YangBaseModel):
    """The list of optical protection switch (ops) on an equipment."""

    ops_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name assigned to identify a specific ops in the device", min_length=1, max_length=32, alias="ops-name")
    working_entity: str | None = Field(json_schema_extra={"is_config": False}, description="Identifier of the working port of the OPS.", default=None, alias="working-entity")
    protection_entity: str | None = Field(json_schema_extra={"is_config": False}, description="Identifier of the protection port of the OPS", default=None, alias="protection-entity")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    protection_status: ProtectionStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the status of the protection switch.", default=None, alias="protection-status")
    active_path: ActivePathEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the active port of the protection switch.", default=ActivePathEnum.UNKNOWN, alias="active-path")
    revertive: YesNoEnum | None = Field(json_schema_extra={"is_config": True}, description="Revertive behavior of the aps.\nIf True, then automatically revert after protection switch\nonce the fault is restored.", default=YesNoEnum.NO)
    wait_to_restore: int | None = Field(json_schema_extra={"is_config": True}, description="Wait To Restore, valid values: 0-3600 seconds. A value of zero will switch back immediately,\nafter expiration of the timer, the working is restored and a norequest state is transmitted.", ge=0, le=3600, default=300, alias="wait-to-restore")
    working_switch_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The switching threshold of the working port which indicates the optical power threshold of signal degrade.", default=-18.0, alias="working-switch-threshold")
    protection_switch_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The switching threshold of the protection port which indicates the optical power threshold of signal degrade.", default=-18.0, alias="protection-switch-threshold")
    working_los_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The switching threshold of the working port, power level below it will lead to loss of signal.", default=-23.0, alias="working-los-threshold")
    protection_los_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The switching threshold of the protection port, power level below it will lead to loss of signal.", default=-23.0, alias="protection-los-threshold")
    holdoff_timer: int | None = Field(json_schema_extra={"is_config": True}, description="The hold off time of the protection switch.", ge=0, le=1000, default=0, alias="holdoff-timer")
    wavelength_band: WavelengthBandEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies the band of the signal going through the optical protection switch unit.", default=WavelengthBandEnum._1550, alias="wavelength-band")
    ops_frequency: int | None = Field(json_schema_extra={"is_config": True}, description="The frequency of optical protection frequency, which will decide the pilot tone modulated on the channel.", le=196111250, ge=0, default=0, alias="ops-frequency")
    working_protection_relative_threshold: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Specify the threshold of power difference between working path and protection path;\nSetting to value 0 to disable the power difference as switch criteria;\nSetting to non-zero value indicates the value of power difference between two paths will trigger protection switch.", default=0, alias="working-protection-relative-threshold")
    relative_threshold_hysteresis: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Specify relative threshold hysteresis for clearance of relative threshold crossing failure.", default=2.0, alias="relative-threshold-hysteresis")
    relative_threshold_offset: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Specify relative threshold offset for protection switch per power difference between working and protection,\nthe offset is the value of (working power - protection power), the offset value will be excluded from power\ndifference before comparing to relative threshold threshold and its hysteresis.", default=0.0, alias="relative-threshold-offset")

class ModuleTemperature(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for module temperature, corresponding to pm parameter T-module"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    module_temperature: ModuleTemperature | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for module temperature, corresponding to pm parameter T-module", default=None, alias="module-temperature")

class Subcard(YangBaseModel):
    """Subcard is a container carried by a subslot."""

    required_type: CardTypeEnum = Field(json_schema_extra={"is_config": True}, description="The attribute indicates the equipment type to identify the module.\nNeeds to be re-defined in the project specific model.", alias="required-type")
    required_subtype: CardSubTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute indicates the equipment sub type to identify the module, which is only appied to CHM2T currently.", default=CardSubTypeEnum.NOT_APPLICABLE, alias="required-subtype")
    equipment_name: str | None = Field(json_schema_extra={"is_config": True}, description="The attribute indicates an additional field to identify the module.", min_length=0, max_length=64, default=None, alias="equipment-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    switching_type: SwitchingTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="The traffic switching type of card.\n\nCondition (when): (../required-type != 'FAN') and (../required-type != 'PSU') and (../required-type != 'FRCU') and (../required-type != 'VIR-SIM')", default=SwitchingTypeEnum.OTN, alias="switching-type")
    temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Temperature at the monitoring point.", default=None)
    otdr: Otdr | None = Field(json_schema_extra={"is_config": True}, description="Container of OTDR.", default=None)
    port: RestconfList[PortItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    amplifier: RestconfList[AmplifierItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of optical amplifier on an equipment.", default=None)
    tdc: RestconfList[TdcItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of optical tdc on an equipment.", default=None)
    ops: RestconfList[OpsItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of optical protection switch (ops) on an equipment.", default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class SubslotItem(YangBaseModel):
    """List: subslot"""

    subslot_id: int = Field(json_schema_extra={"is_config": True}, description="Identifier of the subslot.", ge=0, alias="subslot-id")
    actual_card_type: EquipmentTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Equipment type for each slot/subslot according to the actually equipping.\nNeeds to be re-defined in the project specific model.", default=EquipmentTypeEnum.EMPTY, alias="actual-card-type")
    actual_card_subtype: CardSubTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Equipment sub-type for each slot according to the actually equipping.\n\nCondition (when): ../actual-card-type = 'CHM2T'", default=CardSubTypeEnum.NOT_APPLICABLE, alias="actual-card-subtype")
    possible_card_types: RestconfList[CardTypeEnum] | None = Field(json_schema_extra={"is_config": False}, description="Defined all the equipment types which can be installed on the slot/subslot.", default=None, alias="possible-card-types")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    subcard: Subcard | None = Field(json_schema_extra={"is_config": True}, description="Subcard is a container carried by a subslot.", default=None)

class Card(YangBaseModel):
    """Card is a container carried by a slot."""

    required_type: CardTypeEnum = Field(json_schema_extra={"is_config": True}, description="The attribute indicates the equipment type to identify the module.\nNeeds to be re-defined in the project specific model.", alias="required-type")
    required_subtype: CardSubTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute indicates the equipment sub type to identify the module, which is only appied to CHM2T currently.", default=CardSubTypeEnum.NOT_APPLICABLE, alias="required-subtype")
    equipment_name: str | None = Field(json_schema_extra={"is_config": True}, description="The attribute indicates an additional field to identify the module.", min_length=0, max_length=64, default=None, alias="equipment-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    card_mode: CardModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify the card mode, e.g. normal or regen.", default=CardModeEnum.NORMAL, alias="card-mode")
    fan_speed_rate: int | None = Field(json_schema_extra={"is_config": False}, description="The fan speed of percentage.\n\nCondition (when): ../required-type = 'FAN'", ge=0, le=100, default=None, alias="fan-speed-rate")
    latch_open: YesNoEnum | None = Field(json_schema_extra={"is_config": False}, description="The latch is opened or closed.", default=YesNoEnum.NO, alias="latch-open")
    switching_type: SwitchingTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="The traffic switching type of card.\n\nCondition (when): (../required-type != 'FAN') and (../required-type != 'PSU') and (../required-type != 'FRCU') and (../required-type != 'VIR-SIM')", default=SwitchingTypeEnum.OTN, alias="switching-type")
    temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Temperature at the monitoring point.", default=None)
    temperature_details: RestconfList[TemperatureDetailsItem] | None = Field(json_schema_extra={"is_config": False}, description="The detailed information of temperature in each monitoring-point of current module", default=None, alias="temperature-details")
    cpu_state: CpuState | None = Field(json_schema_extra={"is_config": False}, description="The module with CPU's utilization states", default=None, alias="cpu-state")
    memory_state: MemoryState | None = Field(json_schema_extra={"is_config": False}, description="For module that have associated memory, these values\nreport information about available and utilized memory", default=None, alias="memory-state")
    subslot: RestconfList[SubslotItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    port: RestconfList[PortItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    amplifier: RestconfList[AmplifierItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of optical amplifier on an equipment.", default=None)
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class SlotItem(YangBaseModel):
    """List: slot"""

    slot_id: int = Field(json_schema_extra={"is_config": True}, description="Identifier of the slot. It shall be an integer number and assigned implicitly by the system.", ge=0, alias="slot-id")
    reserved: bool | None = Field(json_schema_extra={"is_config": True}, description="Describes whether this slot is reserved by a required card.\nThis is true for both cards in current slot, or in adjancent slots.", default=False)
    actual_card_type: EquipmentTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Equipment type for each slot/subslot according to the actually equipping.\nNeeds to be re-defined in the project specific model.", default=EquipmentTypeEnum.EMPTY, alias="actual-card-type")
    actual_card_subtype: CardSubTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Equipment sub-type for each slot according to the actually equipping.\n\nCondition (when): ../actual-card-type = 'CHM2T'", default=CardSubTypeEnum.NOT_APPLICABLE, alias="actual-card-subtype")
    possible_card_types: RestconfList[CardTypeEnum] | None = Field(json_schema_extra={"is_config": False}, description="Defined all the equipment types which can be installed on the slot/subslot.", default=None, alias="possible-card-types")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    card: Card | None = Field(json_schema_extra={"is_config": True}, description="Card is a container carried by a slot.", default=None)

class InletTemperature(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for inlet temperature, corresponding to pm parameter T-inlet"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class OutletTemperature(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for outlet temperature, corresponding to pm parameter T-outlet"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")
    inlet_temperature: InletTemperature | None = Field(json_schema_extra={"is_config": True}, description="statistics value: average, minimum, maximum and instant value for inlet temperature, corresponding to pm parameter T-inlet", default=None, alias="inlet-temperature")
    outlet_temperature: OutletTemperature | None = Field(json_schema_extra={"is_config": True}, description="statistics value: average, minimum, maximum and instant value for outlet temperature, corresponding to pm parameter T-outlet", default=None, alias="outlet-temperature")

class ShelfItem(YangBaseModel):
    """List: shelf"""

    shelf_id: int = Field(json_schema_extra={"is_config": True}, description="Identifier of the shelf.\nIt shall be an integer number and assigned implicitly by the system or setting through coder on the shelf.", ge=1, alias="shelf-id")
    shelf_type: str | None = Field(json_schema_extra={"is_config": True}, description="Type of the shelf.", min_length=0, max_length=64, default=None, alias="shelf-type")
    shelf_serial_number: str | None = Field(json_schema_extra={"is_config": False}, description="Serial number of the shelf.", min_length=0, max_length=64, default=None, alias="shelf-serial-number")
    shelf_location: str | None = Field(json_schema_extra={"is_config": True}, description="Name of the location of this particular shelf.", min_length=0, max_length=64, default=None, alias="shelf-location")
    shelf_mac_address: str | None = Field(json_schema_extra={"is_config": True}, description="The MAC address of the shelf", default=None, alias="shelf-mac-address")
    shelf_linklocal_ip_address: str | None = Field(json_schema_extra={"is_config": True}, description="The link local IP address of the shelf, which is used during the shelf topology establishment phase", default=None, alias="shelf-linklocal-ip-address")
    shelf_ip_address: str | None = Field(json_schema_extra={"is_config": True}, description="The IP address of the shelf, which is assigned by the main shelf", default=None, alias="shelf-ip-address")
    flush_l2_addr_table: int | None = Field(json_schema_extra={"is_config": True}, description="Flush the L2 MAC address table of the shelf", ge=0, default=0)
    unknown_pluggable_report: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute will enable/disable the alarm reporting for unknown pluggables present on the NE.", default=EnableSwitchEnum.ENABLED, alias="unknown-pluggable-report")
    los_alarm_soak_time: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="enable or disable the function of los-alarm-soak-time. By default it's enabled, which means LOS detection still have soak time.", default=EnableSwitchEnum.ENABLED, alias="los-alarm-soak-time")
    highest_alarm_severity: SeverityLevelEnum | None = Field(json_schema_extra={"is_config": True}, description="The highest severity of any active alarm on any object under this shelf (or ne if this is the main shelf).\nThis is used to configure the FAULT LED of the shelf.", default=SeverityLevelEnum.NOT_ALARMED, alias="highest-alarm-severity")
    inlet_temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="shelf inlet temperature", default=None, alias="inlet-temperature")
    outlet_temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="shelf outlet temperature", default=None, alias="outlet-temperature")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    slot: RestconfList[SlotItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    temperature_details: RestconfList[TemperatureDetailsItem] | None = Field(json_schema_extra={"is_config": False}, description="The detailed information of temperature in each monitoring-point of current module", default=None, alias="temperature-details")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": True}, default=None)

class EquipmentTypeEnum_1(str, Enum):
    """Enumeration for EquipmentTypeEnum
    
    Values:
      * shelf
      * slot
      * card
      * port
      * pluggable
      * subslot
      * subcard
    """

    SHELF = "shelf"
    SLOT = "slot"
    CARD = "card"
    PORT = "port"
    PLUGGABLE = "pluggable"
    SUBSLOT = "subslot"
    SUBCARD = "subcard"

class InventoryItem(YangBaseModel):
    """List: inventory"""

    equipment_type: EquipmentTypeEnum_1 = Field(json_schema_extra={"is_config": False}, description="The equipment type that the inventory data refers to", alias="equipment-type")
    shelf_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the shelf.", ge=1, alias="shelf-id")
    slot_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the slot.", ge=0, alias="slot-id")
    subslot_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the subslot.", ge=0, alias="subslot-id")
    port_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the port.", ge=0, alias="port-id")
    equipment_version: str | None = Field(json_schema_extra={"is_config": False}, description="The attribute Identifies the Hardware Version of the module that populates the slot.", min_length=0, max_length=20, default=None, alias="equipment-version")
    module_type: str | None = Field(json_schema_extra={"is_config": False}, description="This is the value of module type stored in EEPROM of the equipment.", min_length=0, max_length=18, default=None, alias="module-type")
    vendor: str | None = Field(json_schema_extra={"is_config": False}, description="Vendor information.", min_length=0, max_length=64, default=None)
    serial_number: str | None = Field(json_schema_extra={"is_config": False}, description="This is the value of serial number stored in EEPROM of the equipment.", min_length=0, max_length=20, default=None, alias="serial-number")
    manufacturer_number: str | None = Field(json_schema_extra={"is_config": False}, description="This is the value of manufacturer number stored in EEPROM of the equipment.", min_length=0, max_length=18, default=None, alias="manufacturer-number")
    fw_version: str | None = Field(json_schema_extra={"is_config": False}, description="Current Firmware (FW) version on the equipment.", min_length=0, max_length=20, default=None, alias="fw-version")
    part_number: str | None = Field(json_schema_extra={"is_config": False}, description="Identifies the Part Number of the equipment.", min_length=0, max_length=18, default=None, alias="part-number")
    clei: str | None = Field(json_schema_extra={"is_config": False}, description="Identifies the CLEI code number of the equipment.\nThe CLEI code is a 10-character code that identifies\ncommunications equipment. It describes product type, features,\nsource document, and associated drawings and vintages.\nCLEI codes have 4 data elements:\n- Characters 1 to 4: Define family or subfamily of product.\n- Characters 5 to 7: Define features.\n- Character 8: Manufacturer and System ID.\n- Characters 9 and 10: Identifies version, issue, and release #.", min_length=0, max_length=18, default=None)
    interface_type: str | None = Field(json_schema_extra={"is_config": False}, description="Indicating interface type of the pluggable.", min_length=0, max_length=64, default="", alias="interface-type")
    manufacture_date: str | None = Field(json_schema_extra={"is_config": False}, description="The equipment manufacture date get from equipment.\nformat is mm/dd/yyyy. When there is no date information show nothing\n\nCondition (when): (../equipment-type = 'shelf') or (../equipment-type = 'card') or (../equipment-type = 'subcard') or (../equipment-type = 'pluggable')", default="", alias="manufacture-date")

class InventoryData(YangBaseModel):
    """Simple container for the inventory list"""

    inventory: RestconfList[InventoryItem] | None = Field(json_schema_extra={"is_config": False}, default=None)

class LedStatusEnum(str, Enum):
    """Enumeration for LedStatusEnum
    
    Values:
      * not-available
      * off
      * blink
      * red
      * red-blink
      * green
      * green-blink
      * amber
      * amber-blink
    """

    NOT_AVAILABLE = "not-available"
    OFF = "off"
    BLINK = "blink"
    RED = "red"
    RED_BLINK = "red-blink"
    GREEN = "green"
    GREEN_BLINK = "green-blink"
    AMBER = "amber"
    AMBER_BLINK = "amber-blink"

class LedItem(YangBaseModel):
    """Attributes related with LED
    Applicable to Shelf, FAN, PSU, CHM1, CHM2, CHM1G, OCC2 in DCI.
    """

    equipment_type: str = Field(json_schema_extra={"is_config": False}, description="The attribute indicates the equipment type to identify the module.\nfor example, if the card is CHM1, 'CHM1' shall be used.\nDCI supporting LEDs:\nCHM1, CHM2, SHELF, FAN", min_length=0, max_length=16, alias="equipment-type")
    shelf_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the shelf.", ge=1, alias="shelf-id")
    slot_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the slot.", ge=0, alias="slot-id")
    subslot_id: int = Field(json_schema_extra={"is_config": False}, description="Identifier of the subslot.", ge=0, alias="subslot-id")
    led_name: str = Field(json_schema_extra={"is_config": False}, description="The functional name of LED.\nDCI NE:\nlocation_led\nport(n)_led   (CHM1: n = 1 to 6, CHM2 n = 1 to 12, e.g. Port12)\nactive_led\npower_led\nfault_led\nstatus_led\nsubslot(n)_led", min_length=0, max_length=16, alias="led-name")
    led_status: LedStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Current LED status.\nDCI NE:\nFor Location_LED: OFF, BLINK\nFor others:\nred, red-blink,green,green-blink,amber,amber-blink,off,notAvailable", default=LedStatusEnum.NOT_AVAILABLE, alias="led-status")

class Leds(YangBaseModel):
    """Simple container for the led list."""

    led: RestconfList[LedItem] | None = Field(json_schema_extra={"is_config": False}, description="Attributes related with LED\nApplicable to Shelf, FAN, PSU, CHM1, CHM2, CHM1G, OCC2 in DCI.", default=None)

class RoadmTargetPowerModeEnum(str, Enum):
    """Enumeration for RoadmTargetPowerModeEnum
    
    Values:
      * psd: power control by target psd
      * power: power control by target power
    """

    PSD = "psd"
    POWER = "power"

class SpanLossCorrectionModeEnum(str, Enum):
    """Enumeration for SpanLossCorrectionModeEnum
    
    Values:
      * slow: span-loss-correction-rate is 0.1 dB/s
      * fast: span-loss-correction-rate is 20 dB/s
    """

    SLOW = "slow"
    FAST = "fast"

class CrsItem(YangBaseModel):
    """Cross connection table.
    """

    src_tp: str = Field(json_schema_extra={"is_config": True}, description="Source tp of cross connection.", alias="src-tp")
    dst_tp: str = Field(json_schema_extra={"is_config": True}, description="Destination tp of cross connection.", alias="dst-tp")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection.", min_length=0, max_length=128, default=None, alias="service-label")
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")

class FiberConnectionTypeEnum(str, Enum):
    """Enumeration for FiberConnectionTypeEnum
    
    Values:
      * two-way: Two-way indicates the connection is bidirectional.
      * one-way: One-way indicates the connection is unidirectional, when two unidirectional connections are created for the same two ports, it is the same as one bidirectional connection.
    """

    TWO_WAY = "two-way"
    ONE_WAY = "one-way"

class FiberConnectionItem(YangBaseModel):
    """Fiber connection table which will be user managed and be explicitly provisioned by user.
    Fiber Connection indicates the physical fiber connection between physical ports or subports.
    """

    src_port: str = Field(json_schema_extra={"is_config": True}, description="Source port of fiber connection.", alias="src-port")
    dst_port: str = Field(json_schema_extra={"is_config": True}, description="Destination port of fiber connection.", alias="dst-port")
    fiber_connection_type: FiberConnectionTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates fiber connection type.", default=FiberConnectionTypeEnum.TWO_WAY, alias="fiber-connection-type")
    fiber_label: str | None = Field(json_schema_extra={"is_config": True}, description="Label of fiber connection.", min_length=0, max_length=255, default=None, alias="fiber-label")
    fix_attenuation_dst: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="external fixed attenuator's attenuation from src-port to dst-port", default=None, alias="fix-attenuation-dst")
    fix_attenuation_src: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="external attenuator's attenuation from dst-port to src-port", default=None, alias="fix-attenuation-src")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")

class InternalLinkItem(YangBaseModel):
    """List: internal-link"""

    internal_link_name: str = Field(json_schema_extra={"is_config": False}, min_length=1, max_length=255, alias="internal-link-name")
    src_port: str = Field(json_schema_extra={"is_config": False}, alias="src-port")
    dst_port: str = Field(json_schema_extra={"is_config": False}, alias="dst-port")

class FiberTypeEnum(str, Enum):
    """Enumeration for FiberTypeEnum
    
    Values:
      * SSMF
      * LEAF
      * TWRS
      * TWC
      * Allwave
      * DSF
      * LS
      * PureSilica
      * TWReach
      * VistaCor
      * Teralight
      * DrakaLL
      * TWPlus
      * TWMinus
      * PSLC
      * OLEAF
      * NZ-DSF
      * ULL
    """

    SSMF = "SSMF"
    LEAF = "LEAF"
    TWRS = "TWRS"
    TWC = "TWC"
    ALLWAVE = "Allwave"
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
    OLEAF = "OLEAF"
    NZ_DSF = "NZ-DSF"
    ULL = "ULL"

class TargetPowerSettingEnum(str, Enum):
    """Enumeration for TargetPowerSettingEnum
    
    Values:
      * manual: Users configures target values for oxcon.
      * auto: System calculates target values for oxcon.
    """

    MANUAL = "manual"
    AUTO = "auto"

class OtsDiagnostics(YangBaseModel):
    """Container: ots-diagnostics"""

    exp_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The expected operator TTI", min_length=0, max_length=32, default=None, alias="exp-operator")
    tx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The transmitter operator TTI", min_length=0, max_length=32, default=None, alias="tx-operator")
    rx_operator: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The received operation specific bytes as an ASCII string; will not be available if bytes cannot be encoded as a printable string.", min_length=0, max_length=32, default=None, alias="rx-operator")
    tim_mon: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates if a Neighbor Mismatch TTI Operator-Specific field based (NMOPER) alarm is reported or not.", default=EnableSwitchEnum.DISABLED, alias="tim-mon")
    shelf_id: int | None = Field(json_schema_extra={"is_config": True}, description="Identifier of the shelf.\nIt shall be an integer number and assigned implicitly by the system or setting through coder on the shelf.", ge=1, default=None, alias="shelf-id")

class OtsItem(YangBaseModel):
    """Represents the Optical Transmission Section (OTS) interface entity"""

    ots_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the ots optical interface.", min_length=1, max_length=32, alias="ots-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    supporting_rx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Rx port for the optical interface.", default=None, alias="supporting-rx-port")
    supporting_tx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Tx port for the optical interface.", default=None, alias="supporting-tx-port")
    measured_span_loss_receive: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The received measured span loss excluding offset.", default=99, alias="measured-span-loss-receive")
    measured_span_loss_transmit: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The transmit measured span loss excluding offset.", default=99, alias="measured-span-loss-transmit")
    fiber_spectral_attenuation_tilt: str | float | None = Field(json_schema_extra={"is_config": True}, description="Specifies the Fiber Spectral Attenuation Tilt.", default="unspecified", alias="fiber-spectral-attenuation-tilt")
    raman_tilt_coefficient: str | float | None = Field(json_schema_extra={"is_config": True}, description="Specifies the Fiber Spectral Attenuation Tilt.", default="unspecified", alias="raman-tilt-coefficient")
    fiber_type: FiberTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicating fiber type of the OTS span.", default=FiberTypeEnum.SSMF, alias="fiber-type")
    external_tx_attenuation: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="External padding attenuation at transmitting direction.", default=None, alias="external-tx-attenuation")
    fiber_length_tx: str | float | None = Field(json_schema_extra={"is_config": True}, description="Specify the fiber length of transmitting direction.", default="auto", alias="fiber-length-tx")
    fiber_length_tx_derived: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Derived fiber length of transmitting direction.", default=None, alias="fiber-length-tx-derived")
    fiber_length_rx: str | float | None = Field(json_schema_extra={"is_config": True}, description="Specify the fiber length of received direction.", default="auto", alias="fiber-length-rx")
    fiber_length_rx_derived: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Derived fiber length of recieved direction.", default=None, alias="fiber-length-rx-derived")
    span_degrade_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="switching for span degrade shutdown function", default=EnableSwitchEnum.DISABLED, alias="span-degrade-enable")
    span_degrade_loss: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The degrade threhsold for recieved span loss", default=28, alias="span-degrade-loss")
    span_degrade_hysteresis: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The hysteresis of optical revocery threshold of recieved", default=2, alias="span-degrade-hysteresis")
    span_loss_receive: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Span loss on the receiver side. Set by the controller and used by device to set AMP gain.", default=None, alias="span-loss-receive")
    span_loss_transmit: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Span loss on the transmitter side. Set by the controller and used by device to configure MSA compliant channel launch power", default=None, alias="span-loss-transmit")
    ingress_span_loss_aging_margin: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Span-loss margin used to set optical amplifier gain and output-voa.\nDay one attenuation of the link, at initial commissioning may increase across wdm link life.\nspan-loss-aging-margin defines the maximum additional loss the wdm link may experience in addition\nto initial loss without requiring a new design (new amplifier settings).", default=0, alias="ingress-span-loss-aging-margin")
    eol_max_load_pIn: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="End Of Life Total input power at maximum load used for amplifier control.\nCalculated during the design, this value shall be used by the amplifier device\nfor the setting so that the reasonable margin is kept to reach this value\nat the end of life of the wdm link, considering span-loss aging margins are reached", default=None, alias="eol-max-load-pIn")
    target_power_setting: TargetPowerSettingEnum | None = Field(json_schema_extra={"is_config": True}, description="Allows automatic configuration of target values for oxcon.", default=TargetPowerSettingEnum.AUTO, alias="target-power-setting")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    ots_diagnostics: OtsDiagnostics | None = Field(json_schema_extra={"is_config": True}, default=None, alias="ots-diagnostics")

class ChannelWorkingModeEnum(str, Enum):
    """Enumeration for ChannelWorkingModeEnum
    
    Values:
      * no-monitor: working without channel monitor function
      * monitor: working with channel monitor function
      * power-control: working with per-channel power-control
    """

    NO_MONITOR = "no-monitor"
    MONITOR = "monitor"
    POWER_CONTROL = "power-control"

class AttControlModeEnum(str, Enum):
    """Enumeration for AttControlModeEnum
    
    Values:
      * not-applicable: Not applicable.
      * auto: Automatic attenuation control mode in which system will decide the attenuation value.
      * manual: Manual attenuation control mode in which target attenuation will be used.
      * gainLoss: Automatic attenuation control mode based on input gainLoss
      * off: Turn off attenuation control in which attenuation will stop at the value last control.
      * power: Automatic attenuation control mode based on target output power
    """

    NOT_APPLICABLE = "not-applicable"
    AUTO = "auto"
    MANUAL = "manual"
    GAINLOSS = "gainLoss"
    OFF = "off"
    POWER = "power"

class OpticalReturnLoss(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for return loss, corresponding to pm parameter ORL"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")
    optical_return_loss: OpticalReturnLoss | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for return loss, corresponding to pm parameter ORL", default=None, alias="optical-return-loss")
    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")

class OmsItem(YangBaseModel):
    """Represents the optical multiplex section (OMS) interface MO"""

    oms_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the oms optical interface.", min_length=1, max_length=32, alias="oms-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    oms_working_mode: ChannelWorkingModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The oms working mode for FOADM scenario\n\nCondition (when): deref(../supporting-rx-port)/../switching-type = 'amplifier'", default=ChannelWorkingModeEnum.NO_MONITOR, alias="oms-working-mode")
    supporting_rx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Rx port for the optical interface.", default=None, alias="supporting-rx-port")
    supporting_tx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Tx port for the optical interface.", default=None, alias="supporting-tx-port")
    parent_ots_interface: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting OTS interface.", default=None, alias="parent-ots-interface")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    rx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Received optical power", default="not-available", alias="rx-optical-power")
    tx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power", default="not-available", alias="tx-optical-power")
    grid_mode: GridTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates Grid type of the OMS.", default=GridTypeEnum.NOT_APPLICABLE, alias="grid-mode")
    grid_offset: int | None = Field(json_schema_extra={"is_config": True}, description="Indicates channel frequency offset to standard grid.", default=0, alias="grid-offset")
    input_channel_attenuation_control_mode: AttControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify attenuation control mode of the channel which applicable to all channels of the oms.", default=None, alias="input-channel-attenuation-control-mode")
    output_channel_attenuation_control_mode: AttControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify attenuation control mode of the channel which applicable to all channels of the oms.", default=AttControlModeEnum.AUTO, alias="output-channel-attenuation-control-mode")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class OscModeEnum(str, Enum):
    """Enumeration for OscModeEnum
    
    Values:
      * not-applicable: OSC mode information is unavailable.
      * 155M52: OSC format of OC-3.
      * 1GBE: 1GBE ethernet type OSC
    """

    NOT_APPLICABLE = "not-applicable"
    _155M52 = "155M52"
    _1GBE = "1GBE"

class DelayMeasurementDistance(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for delay measurement distance, corresponding to pm parameter DM-Distance"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class RoundTripDelay(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for round trip delay, corresponding to pm parameter RTD"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class RtdBaseline(YangBaseModel):
    """statistics value: average, minimum, maximum and instant value for round trip delay baseline, corresponding to pm parameter RTD-Baseline"""

    instant: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the instant value of statistics counter", default=None)
    avg: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the average value of statistics counter", default=None)
    min: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the minimum value of statistics counter", default=None)
    max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the maximum value of statistics counter", default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")
    delay_measurement_distance: DelayMeasurementDistance | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for delay measurement distance, corresponding to pm parameter DM-Distance", default=None, alias="delay-measurement-distance")
    round_trip_delay: RoundTripDelay | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for round trip delay, corresponding to pm parameter RTD", default=None, alias="round-trip-delay")
    rtd_baseline: RtdBaseline | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for round trip delay baseline, corresponding to pm parameter RTD-Baseline", default=None, alias="rtd-baseline")
    in_coding_violation: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics bits counting for ingress coding violation, corresponding to pm parameter CV\n\nCondition (when): deref(../supporting-rx-port)/../required-type = 'RD09SM'", ge=0, le=18446744073709551615, default=None, alias="in-coding-violation")
    errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for errored signal, corresponding to pm parameter ES\n\nCondition (when): deref(../supporting-rx-port)/../required-type = 'RD09SM'", ge=0, le=18446744073709551615, default=None, alias="errored-seconds")
    severely_errored_seconds: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for severely errored signal, corresponding to pm parameter SES\n\nCondition (when): deref(../supporting-rx-port)/../required-type = 'RD09SM'", ge=0, le=18446744073709551615, default=None, alias="severely-errored-seconds")
    in_severely_errored_frame_second: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics seconds counting for ingress signal frame severely errored, corresponding to pm parameter SEFS\n\nCondition (when): deref(../supporting-rx-port)/../required-type = 'RD09SM'", ge=0, le=18446744073709551615, default=None, alias="in-severely-errored-frame-second")
    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")

class OscItem(YangBaseModel):
    """Represents the Optical Supervision Channel (OSC) MO"""

    osc_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the osc optical interface.", min_length=1, max_length=32, alias="osc-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    supporting_rx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Rx port for the optical interface.", default=None, alias="supporting-rx-port")
    supporting_tx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Tx port for the optical interface.", default=None, alias="supporting-tx-port")
    parent_ots_interface: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting OTS insterface.", default="unassigned", alias="parent-ots-interface")
    osc_laser_on: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="enable or disable OSC", default=EnableSwitchEnum.ENABLED, alias="osc-laser-on")
    osc_mode: OscModeEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the current OSC mode.", default=OscModeEnum._155M52, alias="osc-mode")
    osc_wavelength: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Indicates the wavelength band of the OSC channel.", ge=950.0, le=1700.0, default=1510, alias="osc-wavelength")
    osc_data_communication: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Configuration for enable or disable data communication network support of the OSC.", default=EnableSwitchEnum.ENABLED, alias="osc-data-communication")
    rtd_measurement: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Configuration for enable or disable round trip delay measurement via the OSC.", default=EnableSwitchEnum.ENABLED, alias="rtd-measurement")
    rtd_interval: Uint64 | None = Field(json_schema_extra={"is_config": True}, description="The time interval of the measurement message sent.", ge=1, le=600, default=5, alias="rtd-interval")
    rtd_tx_msg: Uint64 | None = Field(json_schema_extra={"is_config": True}, description="The number of measurement messages to be sent, fixed as 1.", ge=0, le=18446744073709551615, default=1, alias="rtd-tx-msg")
    rtd_est_baseline: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics of estimated length of the measured OSC span in kilometers to be stored in the baseline file", default=None, alias="rtd-est-baseline")
    rtd_min_distance: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics of minimum measureable distance which can be measured using OSC RTD", default=None, alias="rtd-min-distance")
    rtd_tx: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting of the transmit messages sent", ge=0, le=18446744073709551615, default=None, alias="rtd-tx")
    rtd_rx: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="the statistics counting of the reply messages received", ge=0, le=18446744073709551615, default=None, alias="rtd-rx")
    rx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Received optical power", default="not-available", alias="rx-optical-power")
    tx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power", default="not-available", alias="tx-optical-power")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class Statistics(YangBaseModel):
    """Container: statistics"""

    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")
    protection_switch_duration: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Protection Switch Duration, corresponding to pm parameter PSD", ge=0, le=18446744073709551615, default=None, alias="protection-switch-duration")
    protection_switch_count: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Protection Switch Count, corresponding to pm parameter PSC", ge=0, le=18446744073709551615, default=None, alias="protection-switch-count")
    loss_tx: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Loss of Signal Seconds of Transmit side, corresponding to pm parameter LOSS-TX", ge=0, le=18446744073709551615, default=None, alias="loss-tx")
    loss_rx: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Loss of Signal Seconds of Receive side, corresponding to pm parameter LOSS-RX", ge=0, le=18446744073709551615, default=None, alias="loss-rx")
    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")

class GoptItem(YangBaseModel):
    """Represents the Generic Optical Section Interface (GOPT) MO"""

    gopt_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the gopt optical interface.", min_length=1, max_length=32, alias="gopt-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    supporting_rx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Rx port for the optical interface.", default=None, alias="supporting-rx-port")
    supporting_tx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Tx port for the optical interface.", default=None, alias="supporting-tx-port")
    rx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Received optical power", default="not-available", alias="rx-optical-power")
    tx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power", default="not-available", alias="tx-optical-power")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class OchInput(YangBaseModel):
    """Container: och-input"""

    input_channel_attenuation_control_mode: AttControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify attenuation control mode of the channel.", default=AttControlModeEnum.NOT_APPLICABLE, alias="input-channel-attenuation-control-mode")
    actual_attenuation: str | float | None = Field(json_schema_extra={"is_config": False}, description="Actually setting attenuation.", default="not-available", alias="actual-attenuation")
    target_attenuation: str | float | None = Field(json_schema_extra={"is_config": True}, description="Actually setting attenuation.", default="6", alias="target-attenuation")
    intended_attenuation: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="the attenuation value for pcl output", default=200.0, alias="intended-attenuation")

class OchOutput(YangBaseModel):
    """Container: och-output"""

    output_channel_attenuation_control_mode: AttControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify attenuation control mode of the channel.", default=AttControlModeEnum.NOT_APPLICABLE, alias="output-channel-attenuation-control-mode")
    actual_attenuation: str | float | None = Field(json_schema_extra={"is_config": False}, description="Actually setting attenuation.", default="not-available", alias="actual-attenuation")
    target_attenuation: str | float | None = Field(json_schema_extra={"is_config": True}, description="Actually setting attenuation.", default="6", alias="target-attenuation")
    intended_attenuation: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="the attenuation value for pcl output", default=200.0, alias="intended-attenuation")

class OchOpticalAttenuation(YangBaseModel):
    """Container for channel attenuation attributes used for function of per channel attenuation control, e.g. on DGE"""

    och_input: OchInput | None = Field(json_schema_extra={"is_config": True}, default=None, alias="och-input")
    och_output: OchOutput | None = Field(json_schema_extra={"is_config": True}, default=None, alias="och-output")

class OchItem(YangBaseModel):
    """Represents the Optical Channel (OCH) MO"""

    och_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the och optical interface.", min_length=1, max_length=32, alias="och-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    supporting_rx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Rx port for the optical interface.", default=None, alias="supporting-rx-port")
    supporting_tx_port: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting Tx port for the optical interface.", default=None, alias="supporting-tx-port")
    parent_entity: str | None = Field(json_schema_extra={"is_config": True}, description="Supporting OMS interface.", default="none", alias="parent-entity")
    och_frequency: int | None = Field(json_schema_extra={"is_config": True}, description="Frequency of the channel with unit MHz.", le=196125000, ge=0, default=None, alias="och-frequency")
    och_wavelength: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Wavelength of the channel with unit nm.", default=None, alias="och-wavelength")
    input_power_typical: str | float | None = Field(json_schema_extra={"is_config": True}, description="Typical input power required for reliable channel detection.", default="not-specified", alias="input-power-typical")
    och_width: int | None = Field(json_schema_extra={"is_config": True}, description="Channel frequency width.", ge=15000, le=200000, default=50000, alias="och-width")
    och_working_mode: ChannelWorkingModeEnum | None = Field(json_schema_extra={"is_config": False}, description="och power control function mode\n\nCondition (when): name(deref(../parent-entity)) = 'oms'", default=ChannelWorkingModeEnum.NO_MONITOR, alias="och-working-mode")
    rx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Received optical power", default="not-available", alias="rx-optical-power")
    tx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power", default="not-available", alias="tx-optical-power")
    och_optical_attenuation: OchOpticalAttenuation | None = Field(json_schema_extra={"is_config": True}, description="Container for channel attenuation attributes used for function of per channel attenuation control, e.g. on DGE", default=None, alias="och-optical-attenuation")

class McItem(YangBaseModel):
    """Represents the  Media Channel (MC) MO"""

    mc_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the mc optical interface.", min_length=1, max_length=32, alias="mc-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    parent_entity: str = Field(json_schema_extra={"is_config": True}, description="Specify supporting parent entity.", alias="parent-entity")
    lower_frequency: int = Field(json_schema_extra={"is_config": True}, description="Minimal frequency of the mc with unit MHz.", ge=0, alias="lower-frequency")
    upper_frequency: int = Field(json_schema_extra={"is_config": True}, description="Max frequency of the mc with unit MHz.", ge=0, alias="upper-frequency")
    center_frequency: int | None = Field(json_schema_extra={"is_config": False}, description="Center frequency of the media channel (mc) with unit MHz.", ge=0, default=None, alias="center-frequency")
    slot_width: int | None = Field(json_schema_extra={"is_config": False}, description="Slot width of the media channel (mc) with unit MHz.", ge=0, default=None, alias="slot-width")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")

class NmcInput(YangBaseModel):
    """Container: nmc-input"""

    input_channel_attenuation_control_mode: AttControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify attenuation control mode of the channel.", default=AttControlModeEnum.NOT_APPLICABLE, alias="input-channel-attenuation-control-mode")
    actual_attenuation: str | float | None = Field(json_schema_extra={"is_config": False}, description="Actually setting attenuation.", default="not-available", alias="actual-attenuation")
    target_attenuation: str | float | None = Field(json_schema_extra={"is_config": True}, description="Actually setting attenuation.", default="max", alias="target-attenuation")
    intended_attenuation: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="the attenuation value for pcl output", default=200.0, alias="intended-attenuation")

class NmcOutput(YangBaseModel):
    """Container: nmc-output"""

    output_channel_attenuation_control_mode: AttControlModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify attenuation control mode of the channel.", default=AttControlModeEnum.NOT_APPLICABLE, alias="output-channel-attenuation-control-mode")
    actual_attenuation: str | float | None = Field(json_schema_extra={"is_config": False}, description="Actually setting attenuation.", default="not-available", alias="actual-attenuation")
    target_attenuation: str | float | None = Field(json_schema_extra={"is_config": True}, description="Actually setting attenuation.", default="max", alias="target-attenuation")
    intended_attenuation: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="the attenuation value for pcl output", default=200.0, alias="intended-attenuation")

class NmcOpticalAttenuation(YangBaseModel):
    """Container for channel attenuation attributes used for function of per channel attenuation control, e.g. on WSS"""

    nmc_input: NmcInput | None = Field(json_schema_extra={"is_config": True}, default=None, alias="nmc-input")
    nmc_output: NmcOutput | None = Field(json_schema_extra={"is_config": True}, default=None, alias="nmc-output")

class Statistics(YangBaseModel):
    """Container: statistics"""

    loss_tx: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Loss of Signal Seconds of Transmit side, corresponding to pm parameter LOSS-TX", ge=0, le=18446744073709551615, default=None, alias="loss-tx")
    in_optical_power: InOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for RX optical power, corresponding to pm parameter OPT", default=None, alias="in-optical-power")
    out_optical_power: OutOpticalPower | None = Field(json_schema_extra={"is_config": False}, description="statistics value: average, minimum, maximum and instant value for TX optical power, corresponding to pm parameter OPR", default=None, alias="out-optical-power")
    last_clear: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The start time of statistics monitor", default="0000-01-01T00:00:00.000Z", alias="last-clear")

class NmcItem(YangBaseModel):
    """Represents the Network Media Channel (NMC) MO"""

    nmc_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name is defined to uniquely identify the nmc optical interface.", min_length=1, max_length=32, alias="nmc-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    parent_entity: str = Field(json_schema_extra={"is_config": True}, description="Specify supporting parent entity.", alias="parent-entity")
    center_frequency: int = Field(json_schema_extra={"is_config": True}, description="Center frequency of the network media channel (nmc) with unit MHz.", ge=184600000, le=196150000, alias="center-frequency")
    width: int = Field(json_schema_extra={"is_config": True}, description="Network media channel frequency width with unit MHz.", ge=15000, le=200000)
    actual_center_frequency: str | int | None = Field(json_schema_extra={"is_config": False}, description="Actual center frequency of the network media channel (nmc) with unit MHz.", default="not-available", alias="actual-center-frequency")
    actual_width: str | int | None = Field(json_schema_extra={"is_config": False}, description="Actual network media channel frequency width with unit MHz.", default="not-available", alias="actual-width")
    actual_psd: str | float | None = Field(json_schema_extra={"is_config": False}, description="Actual input power spectral density expressed in nanowatts per megahertz, nW/GHz.", default="not-available", alias="actual-psd")
    actual_output_psd: str | float | None = Field(json_schema_extra={"is_config": False}, description="Actual output power spectral density expressed in nanowatts per megahertz, nW/GHz.", default="not-available", alias="actual-output-psd")
    input_psd_max: str | float | None = Field(json_schema_extra={"is_config": True}, description="the maximum valid input signal psd\n\nCondition (when): ../../../roadm-target-power-mode = 'psd'", default="not-available", alias="input-psd-max")
    input_psd_min: str | float | None = Field(json_schema_extra={"is_config": True}, description="the minimum valid input signal psd\n\nCondition (when): ../../../roadm-target-power-mode = 'psd'", default="not-available", alias="input-psd-min")
    input_power_max: str | float | None = Field(json_schema_extra={"is_config": True}, description="the maximum valid input signal power\n\nCondition (when): ../../../roadm-target-power-mode = 'power'", default="not-available", alias="input-power-max")
    input_power_min: str | float | None = Field(json_schema_extra={"is_config": True}, description="the minimum valid input signal power\n\nCondition (when): ../../../roadm-target-power-mode = 'power'", default="not-available", alias="input-power-min")
    peer_nmc: str | None = Field(json_schema_extra={"is_config": True}, description="hmo for covert nmc record the peer nmc in OCRS", default=None, alias="peer-nmc")
    rx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Received optical power", default="not-available", alias="rx-optical-power")
    tx_optical_power: str | float | None = Field(json_schema_extra={"is_config": False}, description="Transmitted optical power", default="not-available", alias="tx-optical-power")
    managed_by: ManagedByEnum | None = Field(json_schema_extra={"is_config": False}, description="Describes whether this CRS was system created or not.\nA system created CRS implies a HW cross connection, that is not\nmanageable by the user.", default=ManagedByEnum.USER, alias="managed-by")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection related facility.", min_length=0, max_length=128, default="", alias="service-label")
    nmc_optical_attenuation: NmcOpticalAttenuation | None = Field(json_schema_extra={"is_config": True}, description="Container for channel attenuation attributes used for function of per channel attenuation control, e.g. on WSS", default=None, alias="nmc-optical-attenuation")
    statistics: Statistics | None = Field(json_schema_extra={"is_config": False}, default=None)

class OpticalInterfaces(YangBaseModel):
    """Represents the optical-interface MO"""

    ots: RestconfList[OtsItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the Optical Transmission Section (OTS) interface entity", default=None)
    oms: RestconfList[OmsItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the optical multiplex section (OMS) interface MO", default=None)
    osc: RestconfList[OscItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the Optical Supervision Channel (OSC) MO", default=None)
    gopt: RestconfList[GoptItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the Generic Optical Section Interface (GOPT) MO", default=None)
    och: RestconfList[OchItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the Optical Channel (OCH) MO", default=None)
    mc: RestconfList[McItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the  Media Channel (MC) MO", default=None)
    nmc: RestconfList[NmcItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents the Network Media Channel (NMC) MO", default=None)

class OcrsItem(YangBaseModel):
    """Cross connection table.
    """

    src_if: str = Field(json_schema_extra={"is_config": True}, description="Source tp of cross connection.", alias="src-if")
    dst_if: str = Field(json_schema_extra={"is_config": True}, description="Destination tp of optical cross connection.", alias="dst-if")
    optical_connection_type: FiberConnectionTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the cross connection type.", default=FiberConnectionTypeEnum.ONE_WAY, alias="optical-connection-type")
    target_psd_dst: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Destination interface power spectral density expressed in nanowatts per\nmegahertz, nW/GHz.  These units allow the value to often\nbe greater than 1.0.  It also avoids dealing with zero values\nfor 0dBm.  For example, a 40GHz wide channel\nwith 0dBm power would be:\n0dBm = 1mW = 10^6nW\n0dBm/40GHz = 10^6nW/40GHz = 1000000/40 = 25000\n\nCondition (when): ../../roadm-target-power-mode = 'psd'", default=None, alias="target-psd-dst")
    target_psd_src: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Source interface power spectral density expressed in nanowatts per\ngigahertz, nW/GHz.  These units allow the value to often\nbe greater than 1.0.  It also avoids dealing with zero values\nfor 0dBm.  For example, a 40GHz wide channel\nwith 0dBm power would be:\n0dBm = 1mW = 10^6nW\n0dBm/40GHz = 10^6nW/40GHz = 1000000/40 = 25000\n\nCondition (when): (../optical-connection-type = 'two-way') and (../../roadm-target-power-mode = 'psd')", default=None, alias="target-psd-src")
    target_output_power_dst: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The destination interface target power\n\nCondition (when): ../../roadm-target-power-mode = 'power'", default=None, alias="target-output-power-dst")
    target_output_power_src: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="The source interface target power\n\nCondition (when): ../../roadm-target-power-mode = 'power'", default=None, alias="target-output-power-src")
    target_actual_output_power_dst: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The destination interface target power\n\nCondition (when): ../../roadm-target-power-mode = 'power'", default=None, alias="target-actual-output-power-dst")
    target_actual_output_power_src: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The source interface target power\n\nCondition (when): ../../roadm-target-power-mode = 'power'", default=None, alias="target-actual-output-power-src")
    target_actual_psd_dst: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Destination interface power spectral density expressed in nanowatts per\nmegahertz, nW/GHz.  These units allow the value to often\nbe greater than 1.0.  It also avoids dealing with zero values\nfor 0dBm.  For example, a 40GHz wide channel\nwith 0dBm power would be:\n0dBm = 1mW = 10^6nW\n0dBm/40GHz = 10^6nW/40GHz = 1000000/40 = 25000\n\nCondition (when): ../../roadm-target-power-mode = 'psd'", default=None, alias="target-actual-psd-dst")
    target_actual_psd_src: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Source interface power spectral density expressed in nanowatts per\ngigahertz, nW/GHz.  These units allow the value to often\nbe greater than 1.0.  It also avoids dealing with zero values\nfor 0dBm.  For example, a 40GHz wide channel\nwith 0dBm power would be:\n0dBm = 1mW = 10^6nW\n0dBm/40GHz = 10^6nW/40GHz = 1000000/40 = 25000\n\nCondition (when): (../optical-connection-type = 'two-way') and (../../roadm-target-power-mode = 'psd')", default=None, alias="target-actual-psd-src")
    service_label: str | None = Field(json_schema_extra={"is_config": True}, description="Path/service name of cross-connection.", min_length=0, max_length=128, default=None, alias="service-label")
    stage_dst: str | None = Field(json_schema_extra={"is_config": True}, description="record the stage of ocrs for dst.", min_length=0, max_length=32, default="not-applicable", alias="stage-dst")
    stage_src: str | None = Field(json_schema_extra={"is_config": True}, description="record the stage of ocrs for dst.", min_length=0, max_length=32, default="not-applicable", alias="stage-src")
    actual_psd_dst: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="hmo", default=0, alias="actual-psd-dst")
    actual_psd_src: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="hmo", default=0, alias="actual-psd-src")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")

class ModulesItem(YangBaseModel):
    """list for Cards associated with a degree"""

    index: int = Field(json_schema_extra={"is_config": True}, ge=0)
    supported_card: str = Field(json_schema_extra={"is_config": True}, alias="supported-card")

class ConnectionPortsItem(YangBaseModel):
    """Port associated with degree: One if bi-directional; two if uni-directional"""

    index: int = Field(json_schema_extra={"is_config": True}, ge=0)
    supported_port: str = Field(json_schema_extra={"is_config": True}, alias="supported-port")

class AssociatedOtdrPort(YangBaseModel):
    """otdr port associated with degree."""

    supported_port: str | None = Field(json_schema_extra={"is_config": True}, default=None, alias="supported-port")

class McCapabilities(YangBaseModel):
    """Capabilities of the media channel on a degree or SRG.  This is used to validate mc-ttp provisioning on degrees and SRGs."""

    slot_width_granularity: str | int | None = Field(json_schema_extra={"is_config": False}, description="Width of a slot measured in MHz.", default="50000", alias="slot-width-granularity")
    center_freq_granularity: str | int | None = Field(json_schema_extra={"is_config": False}, description="Granularity of allowed center frequencies.  The base frequency for this computation is 193100000 MHz (G.694.1)", default="50000", alias="center-freq-granularity")
    min_slots: int | None = Field(json_schema_extra={"is_config": False}, description="Minimum number of slots permitted to be joined together to form a media channel.  Must be less than or equal to the max-slots", ge=0, default=1, alias="min-slots")
    max_slots: int | None = Field(json_schema_extra={"is_config": False}, description="Maximum number of slots permitted to be joined together to form a media channel.  Must be greater than or equal to the min-slots", ge=0, default=1, alias="max-slots")

class DegreeItem(YangBaseModel):
    """List: degree"""

    degree_number: int = Field(json_schema_extra={"is_config": True}, ge=0, alias="degree-number")
    max_channels: int = Field(json_schema_extra={"is_config": False}, description="maximum number of DWDM channels", ge=0, alias="max-channels")
    group_status: str | None = Field(json_schema_extra={"is_config": False}, description="The group status for ROADM", default=None, alias="group-status")
    modules: RestconfList[ModulesItem] | None = Field(json_schema_extra={"is_config": True}, description="list for Cards associated with a degree", default=None)
    connection_ports: RestconfList[ConnectionPortsItem] | None = Field(json_schema_extra={"is_config": True}, description="Port associated with degree: One if bi-directional; two if uni-directional", default=None, alias="connection-ports")
    associated_otdr_port: AssociatedOtdrPort | None = Field(json_schema_extra={"is_config": True}, description="otdr port associated with degree.", default=None, alias="associated-otdr-port")
    mc_capabilities: McCapabilities | None = Field(json_schema_extra={"is_config": False}, description="Capabilities of the media channel on a degree or SRG.  This is used to validate mc-ttp provisioning on degrees and SRGs.", default=None, alias="mc-capabilities")

class WavelengthDuplicationEnum(str, Enum):
    """Enumeration for WavelengthDuplicationEnum
    
    Values:
      * one-per-srg: The SRG cannot handle wavelength duplication. Attempting to provision a connection on this SRG that uses the same wavelength as an existing service will result in failure.
      * one-per-degree: The SRG can handle wavelength duplication, but only one per degree. Attempting to provision a connection on this SRG that uses the same wavelength as an existing service will succeed, so long as the connections are not using the same degree.
    """

    ONE_PER_SRG = "one-per-srg"
    ONE_PER_DEGREE = "one-per-degree"

class GridCapabilityEnum(str, Enum):
    """Enumeration for GridCapabilityEnum
    
    Values:
      * colorless
      * colored
    """

    COLORLESS = "colorless"
    COLORED = "colored"

class ModulesItem(YangBaseModel):
    """list for Cards associated with an add/drop group and srg"""

    index: int = Field(json_schema_extra={"is_config": True}, ge=0)
    supported_card: str = Field(json_schema_extra={"is_config": True}, alias="supported-card")

class SharedRiskGroupItem(YangBaseModel):
    """List: shared-risk-group"""

    max_add_drop_ports: int = Field(json_schema_extra={"is_config": False}, description="The max number of ports available for a given srg", ge=0, alias="max-add-drop-ports")
    current_provisioned_add_drop_ports: int = Field(json_schema_extra={"is_config": False}, description="The number of ports currently provisioned for a given srg.", ge=0, alias="current-provisioned-add-drop-ports")
    srg_number: int = Field(json_schema_extra={"is_config": True}, ge=0, alias="srg-number")
    wavelength_duplication: WavelengthDuplicationEnum | None = Field(json_schema_extra={"is_config": False}, description="Whether the SRG can handle duplicate wavelengths and if so to what extent.", default=WavelengthDuplicationEnum.ONE_PER_SRG, alias="wavelength-duplication")
    grid_capability: GridCapabilityEnum | None = Field(json_schema_extra={"is_config": True}, description="The srg grid capability selected by request", default=GridCapabilityEnum.COLORLESS, alias="grid-capability")
    group_status: str | None = Field(json_schema_extra={"is_config": False}, description="The group status for ROADM", default=None, alias="group-status")
    modules: RestconfList[ModulesItem] | None = Field(json_schema_extra={"is_config": True}, description="list for Cards associated with an add/drop group and srg", default=None)
    mc_capabilities: McCapabilities | None = Field(json_schema_extra={"is_config": False}, description="Capabilities of the media channel on a degree or SRG.  This is used to validate mc-ttp provisioning on degrees and SRGs.", default=None, alias="mc-capabilities")

class Services(YangBaseModel):
    """Container: services"""

    roadm_target_power_mode: RoadmTargetPowerModeEnum | None = Field(json_schema_extra={"is_config": True}, description="The optical power control mode of ocrs", default=RoadmTargetPowerModeEnum.POWER, alias="roadm-target-power-mode")
    span_loss_correction_mode: SpanLossCorrectionModeEnum | None = Field(json_schema_extra={"is_config": True}, description="for user to weight between fast span loss control versus safeguarding from accidental traffic impact when OSC fiber maintenance is conducted but the recommended procedure is not followed.", default=SpanLossCorrectionModeEnum.FAST, alias="span-loss-correction-mode")
    CRS: RestconfList[CrsItem] | None = Field(json_schema_extra={"is_config": True}, description="Cross connection table.", default=None)
    fiber_connection: RestconfList[FiberConnectionItem] | None = Field(json_schema_extra={"is_config": True}, description="Fiber connection table which will be user managed and be explicitly provisioned by user.\nFiber Connection indicates the physical fiber connection between physical ports or subports.", default=None, alias="fiber-connection")
    internal_link: RestconfList[InternalLinkItem] | None = Field(json_schema_extra={"is_config": False}, default=None, alias="internal-link")
    optical_interfaces: OpticalInterfaces | None = Field(json_schema_extra={"is_config": True}, description="Represents the optical-interface MO", default=None, alias="optical-interfaces")
    OCRS: RestconfList[OcrsItem] | None = Field(json_schema_extra={"is_config": True}, description="Cross connection table.", default=None)
    degree: RestconfList[DegreeItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    shared_risk_group: RestconfList[SharedRiskGroupItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="shared-risk-group")

class ConditionTypeEnum(str, Enum):
    """Enumeration for ConditionTypeEnum
    
    Values:
      * IDP: ID Prom Failure
      * RUP-DEG: Replaceable Unit Problem - Degrade
      * RUP-FAIL: Replaceable Unit Problem - Failed
      * MEA-HWVM: Mismatch of Equipment - Hardware version Mismatch
      * MEA: Mismatch of Equipment, Equipment not support on this slot or this configuration type
      * PWRA: Power Feed A problem
      * PWRB: Power Feed B problem
      * RUP-MISS: Replaceable Unit Missing
      * SBANR: Software Boot Abnormal
      * SDF: Software Download Failure
      * THERMAL: Thermal Problem
      * SDCARDMISS: SD Card Missing
      * SDCARDFAIL: SD Card Failure
      * MGMTRST: Database Down or Corruption
      * PROGFLT: Software fault or failure
      * NTPPU: NTP Sever Unreachable
      * LINKDOWN: Link Down
      * LOS: Loss Of Signal
      * LOL: Loss of Lock
      * LOF-OTU: Loss Of Frame - OTU
      * LOM-OTU: Loss of Multiframe - OTU
      * TIM-OTU: Trace identifier Mismatch on OTU
      * BDI-OTU: Backward Defect Indication - OTU
      * BERSD-OTU: Bit Error Rate Signal Degrade - OTU
      * AIS-OTU: Alarm Indication Signal - OTU
      * BERSD-ODU: Bit Error Rate Signal Degrade - ODU
      * LCK-ODU: Locked
      * OCI-ODU: Open Connection Indication
      * AIS-ODU: Alarm Indication Signal - ODU
      * BDI-ODU: Backward Defect Indication - ODU
      * TIM-ODU: Trace identifier Mismatch on ODU
      * PLM-ODU: Payload Label Mismatch - ODU
      * LOOMFI: Loss of OPU MultiFrame Identifier
      * MSIM: Multiplex Structure Identifier Mismatch
      * LOFLOM: Loss of Frame and Loss of Multiframe
      * CSF-OPU: Client Signal Fail - Optical Payload Unit
      * LOSYNC: Loss of Synchronization
      * LF: Local Fault
      * RF: Remote Fault
      * CSF-LOS-GFP: Client Signal Failure - Loss of Signal
      * CSF-LOSYNC-GFP: Client Signal Failure - Loss of Synchronization
      * CSF-FDI-GFP: Client Signal Failure - Local fault
      * CSF-RDI-GFP: Client Signal Failure - Remote Defect Indication
      * LOFD-GFP: Loss Of Frame Delineation
      * PLM-GFP: Payload Label Mismatch - ODU
      * LPBKFACILITY: Loopback, Facility
      * LPBKFTERM: Loopback, Terminal
      * CONTCOM: Control Communications Failure
      * LATCH-OPEN: Latch status is open
      * LOF: Loss of Frame
      * AIS-L: Alarm Indication Signal -Line
      * MS-AIS: Alarm indication signal - Multiplex Section
      * TIM-R: Trace identifier Mismatch - Regen Section
      * RS-TIM: Trace identifier Mismatch - Regenerator Section
      * RFI-L: Remote Failure Indication - Line
      * MS-RFI: Remote Failure Indication - Multiplex Section
      * CABS: Connection Absent
      * OOG: Out of Gain
      * CONNECT-FAIL: Connection failed
      * ENCRYPT-FAIL: Encryption failed
      * KEYEX-FAIL: Key exchange failed
      * BDI: Backward Defect Indication
      * BDI-O: Backward Defect Indication - Overhead
      * AUTOSHUTOFF: Optical amplifier automatically shutoff
      * FIBRCONN-MISS: Fiber Connection is Missing
      * BDI-P: Backward Defect Indication - Payload
      * LOS-MSA: Loss of Signal - Middle Stage Access
      * PROTNA: Protection Not Available
      * SWITCH-THRES: Switching Threshold Crossed
      * LOSYNC-CD: Loss of Synchronization - Chromatic Dispersion Measurement
      * UPDATE-PSK-FAIL: Updating an existing psk-map failed
      * ENC-TRAFFIC-SQUELCH: Encryption Traffic Squelched
      * OPTPWR-DIFF-HIGH: Optical Power Difference High
      * PT-FAIL: Pilot Tone is Failed
      * PT-DEG: Pilot Tone is Degraded
      * PSK-MISMATCH: PSK mismatch detected
      * VOATC: VOA Threshold Crossing
      * SPAN-DEG: Span Degrade
      * LOA: Loss of Lock
      * TOPO-MISM: Topology Mismatch.
      * FIPS-SELFTEST-FAIL: FIPS Self-Test Failure.
      * LOS-OPR: Loss of Optical Power Received
      * DEG-OPR: Degraded of Optical Power Received
      * HORL: High Reflection/ Low Optical Return Loss
      * AUTOSHUTOFF-DIS: Optical amplifier automatically shutoff disabled
      * OLF: Optical line failure
      * SW-MISM: The active software version in subshelf different from main shelf
      * POWER-TOO-HIGH: If the NMC power is below the minimum or above the maximum values of the configured range, raise the alarm. The exact same range is used as for the RCD checks, which is defined without tolerance with respect to min and max border.
      * POWER-TOO-LOW: If the NMC power is below the minimum or above the maximum values of the configured range, raise the alarm. The exact same range is used as for the RCD checks, which is defined without tolerance with respect to min and max border.
      * FDI: Forward Defect Indication
      * FW-INSTAL-FAIL: 3rd party firmware install fail
      * TIM-OTS: Trace identifier Mismatch on OTS
      * MEMORY-LOW: Chassis free memory is low
      * T-SE: Symbol Error During Carrier
      * T-DROPEVENTS: Drop Events
      * T-OCTETS: Octets
      * T-PKTS: Packets
      * T-BROADCASTPKTS: Broadcast Packets
      * T-MULTICASTPKTS: Multicast Packets
      * T-CRCALIGNERRORS: CRC Alignment Errors
      * T-UNDERSIZEPKTS: Undersize Packets
      * T-OVERSIZEPKTS: Oversize Packets
      * T-FRAGMENTS: Fragments
      * T-JABBERS: Jabbers
      * T-PKTS64OCTETS: Packets with 64 octets in length 
      * T-PKTS65TO127OCTETS: Packets with between 65 and 127 octets in length inclusive
      * T-PKTS128TO255OCTETS: Packets with between 128 and 255 octets in length inclusive
      * T-PKTS256TO511OCTETS: Packets with between 256 and 511 octets in length inclusive
      * T-PKTS512TO1023OCTETS: Packets with between 512 and 1023 octets in length inclusive
      * T-PKTS1024TO1518OCTETS: Packets with between 1024 and 1518 octets in length inclusive
      * T-UTIL-HT: Utilization
      * T-BE-FEC: Bit Error Forward Error Correction
      * T-UBE-FEC: Uncorrectable Block Error Forward Error Correction
      * T-BER-FEC-HT: Bit Error Rate before Forward Error Correction - High Threshold
      * T-EB-OTU: Error Block Count - Optical Transport Unit
      * T-ES-OTU: Errored Second - Optical Transport Unit
      * T-SES-OTU: Severely Errored Second - Optical Transport Unit
      * T-UAS-OTU: Unavailable Second - Optical Transport Unit 
      * T-EB-ODU: Error Block Count - Optical Data Unit
      * T-ES-ODU: Errored Second - Optical Data Unit
      * T-SES-ODU: Severely Errored Second - Optical Data Unit
      * T-UAS-ODU: Unavailable Second - Optical Data Unit
      * T-DELAY-ODU-HT: Delay measurement - Optical Data Unit - High Threshold
      * T-DELAY-ODU-LT: Delay measurement - Optical Data Unit - Low Threshold
      * T-DGD-HT: Differential Group Delay - High Threshold
      * T-CD-LT: Chromatic Dispersion - Low Threshold
      * T-CD-HT: Chromatic Dispersion - High Threshold
      * T-OSNR-LT: Optical Signal to Noise Ratio - Low Threshold
      * T-LOSS: Loss of Signal Seconds count
      * T-OPR-HT: Optical Power Received level - High Threshold
      * T-OPR-LT: Optical Power Received level - Low Threshold
      * T-QFACTOR-LT: Quality factor - Low Threshold
      * T-OPT-HT: Optical Power Transmitted level - High Threshold
      * T-OPT-LT: Optical Power Transmitted level - Low Threshold
      * T-PDL-HT: Polarization Dependent Loss - High Threshold
      * T-OFT-HT: Optical Frequency Transmitted level - High Threshold
      * T-OFT-LT: Optical Frequency Transmitted level - Low Threshold
      * T-OFR-HT: Optical Frequency Received level - High Threshold
      * T-OFR-LT: Optical Frequency Received level - Low Threshold
      * T-CV-S: Coding Violation - SONET Section
      * T-ES-S: Errored Second - SONET Section
      * T-SES-S: Severely Errored Seconds - SONET Section
      * T-UAS-S: Unavailable Second - SONET Section
      * T-SEFS: Severely Errored Frame Second - SONET
      * T-BBE-RS: Background Block Error - RS
      * T-ES-RS: Errored Second - SDH RS
      * T-SES-RS: Severely Errored Seconds - SDH RS
      * T-UAS-RS: Unavailable Second - SDH RS
      * T-OFS: Out of Frame Seconds - SDH
      * T-OPR-LANE-HT: Optical Power Received level, lane - High Threshold
      * T-OPR-LANE-LT: Optical Power Received level, lane - Low Threshold
      * T-OPR-TOTAL-HT: Optical Power Received level, aggregation - High Threshold
      * T-OPR-TOTAL-LT: Optical Power Received level, aggregation - Low Threshold
      * T-OPT-LANE-HT: Optical Power Transmitted level, lane - High Threshold
      * T-OPT-LANE-LT: Optical Power Transmitted level, lane - Low Threshold
      * T-OPT-TOTAL-HT: Optical Power Transmitted level, total - High Threshold
      * T-OPT-TOTAL-LT: Optical Power Transmitted level, aggregation - Low Threshold
      * T-LOSS-Tx: Loss of Signal Seconds count - Transmit
      * T-LOSS-Rx: Loss of Signal Seconds count - Receive
      * T-PTFS: Pilot Tone Failed Seconds count
      * T-ORL-HT: Optical Return Loss - High Threshold
      * T-CV-PCS: Coding Violation - Ethernet PCS
      * T-ES-PCS: Errored Second - Ethernet PCS
      * T-SES-PCS: Severely Errored Seconds - Ethernet PCS
      * T-UAS-PCS: Unavailable Second - Ethernet PCS
      * T-CBE-FEC: Corrected Block Error Forward Error Correction
      * T-FEB: Farend Error Block counter, Backward Error Indicator
      * T-IAE: Incoming Alignment Error
      * T-BIAE: Backward Incoming Alignment Error
      * T-BE: BIP error
      * T-PktsERR: Errored Packets
      * T-DM-Distance-HT: RDT Delay Measurement Distance - High Threshold
      * T-DM-Distance-LT: RDT Delay Measurement Distance - Low Threshold
      * INIT: Initialization
      * SWUPG-COMPLD: Software Upgrade completed
      * SWUPG-FAIL: Software Upgrade has failed
      * SWUPG-ROLLBACK: Software Upgrade roll back
      * UPG-COMPLD: Module has completed software upgrade
      * UPG-FAIL: Module has failed software upgrade
      * INTRUSION: Unknown account attempt
      * USERLOCK: User suspended
      * SWUPG-IP: Software Upgrade In-Progress
      * ZTC-FAIL: Zero Touch Commissioning Failed
      * ZTC-COMPLETE: Zero Touch Commissioning Complete Successfully
      * DBACT-FAIL: Database Activation Failed
      * INACTIVE: User Inactive
      * RESTART: System restart
      * FSTOPROT: Force switch to protect
      * FSTOWKG: Force switch to working
      * LOCKOUT: Lockout of protection
      * MANTOPROT: Manual switch to protect
      * MANTOWKG: Manual switch to working
      * NOREQ: No Request
      * SDONPROT: Signal degrade on protect
      * SDONWKG: Signal degrade on working
      * SFONPROT: Signal fail on protect
      * SFONWKG: Signal fail on working
      * WKSWPR: Working Switch to Protect
      * PRSWWK: Protect Switch to Working
      * WTR: Wait to Restore
      * DNR: Do Not Revert
      * AUTHN-FAILED: Authentication failed
      * LOGIN-FAILED: Login failed
      * CANDIDATE-PSK-MISMATCH: The candidate psk mismatched with peer NE
      * UPDATE-PSK-COMPLD: Updating an existing psk-map completed
      * CANDIDATE-PSK-AUTHENTICATED: The candidate psk has been authenticated with peer NE
      * UPDATE-PSK-REQ-RCV: Update psk-map request received
      * PULLOUT-TRIGGERED: Pull-out is triggered
      * FIPS-SELFTEST-PASSED: FIPS Self-Test Passed
      * FW-CRASH: Firmware Crash
      * POWER-ARRAY-QUITE-AREA: power array quite area
    """

    IDP = "IDP"
    RUP_DEG = "RUP-DEG"
    RUP_FAIL = "RUP-FAIL"
    MEA_HWVM = "MEA-HWVM"
    MEA = "MEA"
    PWRA = "PWRA"
    PWRB = "PWRB"
    RUP_MISS = "RUP-MISS"
    SBANR = "SBANR"
    SDF = "SDF"
    THERMAL = "THERMAL"
    SDCARDMISS = "SDCARDMISS"
    SDCARDFAIL = "SDCARDFAIL"
    MGMTRST = "MGMTRST"
    PROGFLT = "PROGFLT"
    NTPPU = "NTPPU"
    LINKDOWN = "LINKDOWN"
    LOS = "LOS"
    LOL = "LOL"
    LOF_OTU = "LOF-OTU"
    LOM_OTU = "LOM-OTU"
    TIM_OTU = "TIM-OTU"
    BDI_OTU = "BDI-OTU"
    BERSD_OTU = "BERSD-OTU"
    AIS_OTU = "AIS-OTU"
    BERSD_ODU = "BERSD-ODU"
    LCK_ODU = "LCK-ODU"
    OCI_ODU = "OCI-ODU"
    AIS_ODU = "AIS-ODU"
    BDI_ODU = "BDI-ODU"
    TIM_ODU = "TIM-ODU"
    PLM_ODU = "PLM-ODU"
    LOOMFI = "LOOMFI"
    MSIM = "MSIM"
    LOFLOM = "LOFLOM"
    CSF_OPU = "CSF-OPU"
    LOSYNC = "LOSYNC"
    LF = "LF"
    RF = "RF"
    CSF_LOS_GFP = "CSF-LOS-GFP"
    CSF_LOSYNC_GFP = "CSF-LOSYNC-GFP"
    CSF_FDI_GFP = "CSF-FDI-GFP"
    CSF_RDI_GFP = "CSF-RDI-GFP"
    LOFD_GFP = "LOFD-GFP"
    PLM_GFP = "PLM-GFP"
    LPBKFACILITY = "LPBKFACILITY"
    LPBKFTERM = "LPBKFTERM"
    CONTCOM = "CONTCOM"
    LATCH_OPEN = "LATCH-OPEN"
    LOF = "LOF"
    AIS_L = "AIS-L"
    MS_AIS = "MS-AIS"
    TIM_R = "TIM-R"
    RS_TIM = "RS-TIM"
    RFI_L = "RFI-L"
    MS_RFI = "MS-RFI"
    CABS = "CABS"
    OOG = "OOG"
    CONNECT_FAIL = "CONNECT-FAIL"
    ENCRYPT_FAIL = "ENCRYPT-FAIL"
    KEYEX_FAIL = "KEYEX-FAIL"
    BDI = "BDI"
    BDI_O = "BDI-O"
    AUTOSHUTOFF = "AUTOSHUTOFF"
    FIBRCONN_MISS = "FIBRCONN-MISS"
    BDI_P = "BDI-P"
    LOS_MSA = "LOS-MSA"
    PROTNA = "PROTNA"
    SWITCH_THRES = "SWITCH-THRES"
    LOSYNC_CD = "LOSYNC-CD"
    UPDATE_PSK_FAIL = "UPDATE-PSK-FAIL"
    ENC_TRAFFIC_SQUELCH = "ENC-TRAFFIC-SQUELCH"
    OPTPWR_DIFF_HIGH = "OPTPWR-DIFF-HIGH"
    PT_FAIL = "PT-FAIL"
    PT_DEG = "PT-DEG"
    PSK_MISMATCH = "PSK-MISMATCH"
    VOATC = "VOATC"
    SPAN_DEG = "SPAN-DEG"
    LOA = "LOA"
    TOPO_MISM = "TOPO-MISM"
    FIPS_SELFTEST_FAIL = "FIPS-SELFTEST-FAIL"
    LOS_OPR = "LOS-OPR"
    DEG_OPR = "DEG-OPR"
    HORL = "HORL"
    AUTOSHUTOFF_DIS = "AUTOSHUTOFF-DIS"
    OLF = "OLF"
    SW_MISM = "SW-MISM"
    POWER_TOO_HIGH = "POWER-TOO-HIGH"
    POWER_TOO_LOW = "POWER-TOO-LOW"
    FDI = "FDI"
    FW_INSTAL_FAIL = "FW-INSTAL-FAIL"
    TIM_OTS = "TIM-OTS"
    MEMORY_LOW = "MEMORY-LOW"
    T_SE = "T-SE"
    T_DROPEVENTS = "T-DROPEVENTS"
    T_OCTETS = "T-OCTETS"
    T_PKTS = "T-PKTS"
    T_BROADCASTPKTS = "T-BROADCASTPKTS"
    T_MULTICASTPKTS = "T-MULTICASTPKTS"
    T_CRCALIGNERRORS = "T-CRCALIGNERRORS"
    T_UNDERSIZEPKTS = "T-UNDERSIZEPKTS"
    T_OVERSIZEPKTS = "T-OVERSIZEPKTS"
    T_FRAGMENTS = "T-FRAGMENTS"
    T_JABBERS = "T-JABBERS"
    T_PKTS64OCTETS = "T-PKTS64OCTETS"
    T_PKTS65TO127OCTETS = "T-PKTS65TO127OCTETS"
    T_PKTS128TO255OCTETS = "T-PKTS128TO255OCTETS"
    T_PKTS256TO511OCTETS = "T-PKTS256TO511OCTETS"
    T_PKTS512TO1023OCTETS = "T-PKTS512TO1023OCTETS"
    T_PKTS1024TO1518OCTETS = "T-PKTS1024TO1518OCTETS"
    T_UTIL_HT = "T-UTIL-HT"
    T_BE_FEC = "T-BE-FEC"
    T_UBE_FEC = "T-UBE-FEC"
    T_BER_FEC_HT = "T-BER-FEC-HT"
    T_EB_OTU = "T-EB-OTU"
    T_ES_OTU = "T-ES-OTU"
    T_SES_OTU = "T-SES-OTU"
    T_UAS_OTU = "T-UAS-OTU"
    T_EB_ODU = "T-EB-ODU"
    T_ES_ODU = "T-ES-ODU"
    T_SES_ODU = "T-SES-ODU"
    T_UAS_ODU = "T-UAS-ODU"
    T_DELAY_ODU_HT = "T-DELAY-ODU-HT"
    T_DELAY_ODU_LT = "T-DELAY-ODU-LT"
    T_DGD_HT = "T-DGD-HT"
    T_CD_LT = "T-CD-LT"
    T_CD_HT = "T-CD-HT"
    T_OSNR_LT = "T-OSNR-LT"
    T_LOSS = "T-LOSS"
    T_OPR_HT = "T-OPR-HT"
    T_OPR_LT = "T-OPR-LT"
    T_QFACTOR_LT = "T-QFACTOR-LT"
    T_OPT_HT = "T-OPT-HT"
    T_OPT_LT = "T-OPT-LT"
    T_PDL_HT = "T-PDL-HT"
    T_OFT_HT = "T-OFT-HT"
    T_OFT_LT = "T-OFT-LT"
    T_OFR_HT = "T-OFR-HT"
    T_OFR_LT = "T-OFR-LT"
    T_CV_S = "T-CV-S"
    T_ES_S = "T-ES-S"
    T_SES_S = "T-SES-S"
    T_UAS_S = "T-UAS-S"
    T_SEFS = "T-SEFS"
    T_BBE_RS = "T-BBE-RS"
    T_ES_RS = "T-ES-RS"
    T_SES_RS = "T-SES-RS"
    T_UAS_RS = "T-UAS-RS"
    T_OFS = "T-OFS"
    T_OPR_LANE_HT = "T-OPR-LANE-HT"
    T_OPR_LANE_LT = "T-OPR-LANE-LT"
    T_OPR_TOTAL_HT = "T-OPR-TOTAL-HT"
    T_OPR_TOTAL_LT = "T-OPR-TOTAL-LT"
    T_OPT_LANE_HT = "T-OPT-LANE-HT"
    T_OPT_LANE_LT = "T-OPT-LANE-LT"
    T_OPT_TOTAL_HT = "T-OPT-TOTAL-HT"
    T_OPT_TOTAL_LT = "T-OPT-TOTAL-LT"
    T_LOSS_TX = "T-LOSS-Tx"
    T_LOSS_RX = "T-LOSS-Rx"
    T_PTFS = "T-PTFS"
    T_ORL_HT = "T-ORL-HT"
    T_CV_PCS = "T-CV-PCS"
    T_ES_PCS = "T-ES-PCS"
    T_SES_PCS = "T-SES-PCS"
    T_UAS_PCS = "T-UAS-PCS"
    T_CBE_FEC = "T-CBE-FEC"
    T_FEB = "T-FEB"
    T_IAE = "T-IAE"
    T_BIAE = "T-BIAE"
    T_BE = "T-BE"
    T_PKTSERR = "T-PktsERR"
    T_DM_DISTANCE_HT = "T-DM-Distance-HT"
    T_DM_DISTANCE_LT = "T-DM-Distance-LT"
    INIT = "INIT"
    SWUPG_COMPLD = "SWUPG-COMPLD"
    SWUPG_FAIL = "SWUPG-FAIL"
    SWUPG_ROLLBACK = "SWUPG-ROLLBACK"
    UPG_COMPLD = "UPG-COMPLD"
    UPG_FAIL = "UPG-FAIL"
    INTRUSION = "INTRUSION"
    USERLOCK = "USERLOCK"
    SWUPG_IP = "SWUPG-IP"
    ZTC_FAIL = "ZTC-FAIL"
    ZTC_COMPLETE = "ZTC-COMPLETE"
    DBACT_FAIL = "DBACT-FAIL"
    INACTIVE = "INACTIVE"
    RESTART = "RESTART"
    FSTOPROT = "FSTOPROT"
    FSTOWKG = "FSTOWKG"
    LOCKOUT = "LOCKOUT"
    MANTOPROT = "MANTOPROT"
    MANTOWKG = "MANTOWKG"
    NOREQ = "NOREQ"
    SDONPROT = "SDONPROT"
    SDONWKG = "SDONWKG"
    SFONPROT = "SFONPROT"
    SFONWKG = "SFONWKG"
    WKSWPR = "WKSWPR"
    PRSWWK = "PRSWWK"
    WTR = "WTR"
    DNR = "DNR"
    AUTHN_FAILED = "AUTHN-FAILED"
    LOGIN_FAILED = "LOGIN-FAILED"
    CANDIDATE_PSK_MISMATCH = "CANDIDATE-PSK-MISMATCH"
    UPDATE_PSK_COMPLD = "UPDATE-PSK-COMPLD"
    CANDIDATE_PSK_AUTHENTICATED = "CANDIDATE-PSK-AUTHENTICATED"
    UPDATE_PSK_REQ_RCV = "UPDATE-PSK-REQ-RCV"
    PULLOUT_TRIGGERED = "PULLOUT-TRIGGERED"
    FIPS_SELFTEST_PASSED = "FIPS-SELFTEST-PASSED"
    FW_CRASH = "FW-CRASH"
    POWER_ARRAY_QUITE_AREA = "POWER-ARRAY-QUITE-AREA"

class EntityTypeFmEnum(str, Enum):
    """Enumeration for EntityTypeFmEnum
    
    Values:
      * 10GBE
      * 40GBE
      * 100GBE
      * OCH-OS
      * OTU4
      * OTUC2
      * OTUC3
      * ODUC2
      * ODUC3
      * ODU4
      * ODU3
      * ODU2E
      * ODU2
      * SHELF
      * SLOT
      * PORT
      * FAN
      * CHM1
      * CHM2
      * BFM
      * MGTETH
      * NTPPEER
      * DB
      * SW
      * LOG
      * SECURITY
      * PSU
      * CFP2
      * QSFP
      * TIME
      * USER
      * ZTC
      * PPP
      * FC8G
      * FC16G
      * ODUflex
      * OTU2
      * OTU2e
      * OC192
      * STM64
      * OMS
      * GOPT
      * PAOSCOFP2
      * PABAOFP2
      * PAIROFP2
      * PALROFP2
      * PAEROFP2
      * BAHOFP2
      * SUBSLOT
      * OCC2
      * OMD96
      * AMPLIFIER
      * OMD48-S
      * OMD48-O
      * CHM1G
      * TDCMOFP2
      * BAUOFP2
      * PAULROFP2
      * OSC
      * OTS
      * SFP+
      * XTM2
      * OMD8B1OFP2
      * OMD8B2OFP2
      * OPSOFP2
      * OPS
      * CHM1LH
      * CHM2LH
      * 10GWAN-SONET
      * 10GWAN-SDH
      * OTDROFP2
      * OCMOFP2
      * OCH
      * OTUC6
      * ODUC6
      * OTUC5
      * ODUC5
      * OTUC4
      * ODUC4
      * CHM2T
      * OPSPTOFP2
      * FRCU
      * CAD8OFP2
      * CAD8EOFP2
      * OMD64
      * 400GBE
      * WS04SOFP2
      * CAD16AOFP2
      * BAXOFP2
      * NMC
      * 1GBE
      * OC48
      * STM16
      * UTM2
      * RD09SM
      * OMD48E
      * OTUC7
      * ODUC7
      * OTUC9
      * ODUC9
      * OTUC11
      * ODUC11
      * ODU0
      * ODU1
      * DGE2M2OFP2
      * PBMTPP
      * CFP2-DCO
      * SUBPORT
      * SFP
      * IPSEC
      * FC1G
      * FC4G
      * OMD64S
    """

    _10GBE = "10GBE"
    _40GBE = "40GBE"
    _100GBE = "100GBE"
    OCH_OS = "OCH-OS"
    OTU4 = "OTU4"
    OTUC2 = "OTUC2"
    OTUC3 = "OTUC3"
    ODUC2 = "ODUC2"
    ODUC3 = "ODUC3"
    ODU4 = "ODU4"
    ODU3 = "ODU3"
    ODU2E = "ODU2E"
    ODU2 = "ODU2"
    SHELF = "SHELF"
    SLOT = "SLOT"
    PORT = "PORT"
    FAN = "FAN"
    CHM1 = "CHM1"
    CHM2 = "CHM2"
    BFM = "BFM"
    MGTETH = "MGTETH"
    NTPPEER = "NTPPEER"
    DB = "DB"
    SW = "SW"
    LOG = "LOG"
    SECURITY = "SECURITY"
    PSU = "PSU"
    CFP2 = "CFP2"
    QSFP = "QSFP"
    TIME = "TIME"
    USER = "USER"
    ZTC = "ZTC"
    PPP = "PPP"
    FC8G = "FC8G"
    FC16G = "FC16G"
    ODUFLEX = "ODUflex"
    OTU2 = "OTU2"
    OTU2E = "OTU2e"
    OC192 = "OC192"
    STM64 = "STM64"
    OMS = "OMS"
    GOPT = "GOPT"
    PAOSCOFP2 = "PAOSCOFP2"
    PABAOFP2 = "PABAOFP2"
    PAIROFP2 = "PAIROFP2"
    PALROFP2 = "PALROFP2"
    PAEROFP2 = "PAEROFP2"
    BAHOFP2 = "BAHOFP2"
    SUBSLOT = "SUBSLOT"
    OCC2 = "OCC2"
    OMD96 = "OMD96"
    AMPLIFIER = "AMPLIFIER"
    OMD48_S = "OMD48-S"
    OMD48_O = "OMD48-O"
    CHM1G = "CHM1G"
    TDCMOFP2 = "TDCMOFP2"
    BAUOFP2 = "BAUOFP2"
    PAULROFP2 = "PAULROFP2"
    OSC = "OSC"
    OTS = "OTS"
    SFP_PLUS = "SFP+"
    XTM2 = "XTM2"
    OMD8B1OFP2 = "OMD8B1OFP2"
    OMD8B2OFP2 = "OMD8B2OFP2"
    OPSOFP2 = "OPSOFP2"
    OPS = "OPS"
    CHM1LH = "CHM1LH"
    CHM2LH = "CHM2LH"
    _10GWAN_SONET = "10GWAN-SONET"
    _10GWAN_SDH = "10GWAN-SDH"
    OTDROFP2 = "OTDROFP2"
    OCMOFP2 = "OCMOFP2"
    OCH = "OCH"
    OTUC6 = "OTUC6"
    ODUC6 = "ODUC6"
    OTUC5 = "OTUC5"
    ODUC5 = "ODUC5"
    OTUC4 = "OTUC4"
    ODUC4 = "ODUC4"
    CHM2T = "CHM2T"
    OPSPTOFP2 = "OPSPTOFP2"
    FRCU = "FRCU"
    CAD8OFP2 = "CAD8OFP2"
    CAD8EOFP2 = "CAD8EOFP2"
    OMD64 = "OMD64"
    _400GBE = "400GBE"
    WS04SOFP2 = "WS04SOFP2"
    CAD16AOFP2 = "CAD16AOFP2"
    BAXOFP2 = "BAXOFP2"
    NMC = "NMC"
    _1GBE = "1GBE"
    OC48 = "OC48"
    STM16 = "STM16"
    UTM2 = "UTM2"
    RD09SM = "RD09SM"
    OMD48E = "OMD48E"
    OTUC7 = "OTUC7"
    ODUC7 = "ODUC7"
    OTUC9 = "OTUC9"
    ODUC9 = "ODUC9"
    OTUC11 = "OTUC11"
    ODUC11 = "ODUC11"
    ODU0 = "ODU0"
    ODU1 = "ODU1"
    DGE2M2OFP2 = "DGE2M2OFP2"
    PBMTPP = "PBMTPP"
    CFP2_DCO = "CFP2-DCO"
    SUBPORT = "SUBPORT"
    SFP = "SFP"
    IPSEC = "IPSEC"
    FC1G = "FC1G"
    FC4G = "FC4G"
    OMD64S = "OMD64S"

class ManagementTimePeriodEnum(str, Enum):
    """Enumeration for ManagementTimePeriodEnum
    
    Values:
      * not-applicable
      * 15min
      * 24h
      * all
      * 1min
      * 1h
    """

    NOT_APPLICABLE = "not-applicable"
    _15MIN = "15min"
    _24H = "24h"
    ALL = "all"
    _1MIN = "1min"
    _1H = "1h"

class AlarmProfileEntryItem(YangBaseModel):
    """The list includes alarm/event entries of an alarm-profile."""

    condition_type: ConditionTypeEnum = Field(json_schema_extra={"is_config": True}, description="Identifies the current standing conditions which cause conditions and/or events.", alias="condition-type")
    fm_entity_type: EntityTypeFmEnum = Field(json_schema_extra={"is_config": True}, description="Indicates the entity type the condition associated, which provides additional information for the object instance having the condition.\nentity type is not exactly same as MO. Entity type have smaller granularity referring to\ndifferent service functions, e.g. 100GBase-R, 40GBase-R, 100GBase-R, ODU4, ODU2, ODU3, OTU4, OTUC2...\nSeparate functions will have different entity types so that profile can be set differently for different\nservice function which is more corresponding to user application.", alias="fm-entity-type")
    time_period: ManagementTimePeriodEnum = Field(json_schema_extra={"is_config": True}, description="Indicates the time-period increments during which PM data is collected.", alias="time-period")
    severity_level_sa: SeverityLevelEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the notification code (severity level) associated with the condition type of service affecting.", default=None, alias="severity-level-sa")
    severity_level_nsa: SeverityLevelEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the notification code (severity level) associated with the condition type of non-service affecting.", default=None, alias="severity-level-nsa")

class AlarmProfileItem(YangBaseModel):
    """Alarm profile defines the severity profile of alarm and event."""

    alarm_profile_id: int = Field(json_schema_extra={"is_config": True}, description="alarm profile identifier which uniquely specify alarm profile.\nalarm profile 1 is supported firstly and applicable to all entities implicitly.", ge=1, le=255, alias="alarm-profile-id")
    alarm_profile_entry: RestconfList[AlarmProfileEntryItem] | None = Field(json_schema_extra={"is_config": True}, description="The list includes alarm/event entries of an alarm-profile.", default=None, alias="alarm-profile-entry")

class ManagementLocationEnum(str, Enum):
    """Enumeration for ManagementLocationEnum
    
    Values:
      * near-end
      * far-end
      * not-applicable
    """

    NEAR_END = "near-end"
    FAR_END = "far-end"
    NOT_APPLICABLE = "not-applicable"

class ManagementDirectionEnum(str, Enum):
    """Enumeration for ManagementDirectionEnum
    
    Values:
      * not-applicable
      * ingress
      * egress
    """

    NOT_APPLICABLE = "not-applicable"
    INGRESS = "ingress"
    EGRESS = "egress"

class ServiceAffectFmEnum(str, Enum):
    """Enumeration for ServiceAffectFmEnum
    
    Values:
      * SA: service-affecting
      * NSA: non-service-affecting
    """

    SA = "SA"
    NSA = "NSA"

class StandingConditionItem(YangBaseModel):
    """The list includes active standing alarms."""

    fm_entity: str = Field(json_schema_extra={"is_config": False}, description="The management object instance which the alarm or condition is reported against.", alias="fm-entity")
    condition_type: ConditionTypeEnum = Field(json_schema_extra={"is_config": False}, description="Identifies the current standing conditions which cause alarms and/or events.", alias="condition-type")
    location: ManagementLocationEnum = Field(json_schema_extra={"is_config": False}, description="Indicates if the alarm or event location is near end or far end.")
    direction: ManagementDirectionEnum = Field(json_schema_extra={"is_config": False}, description="Specifies the direction of an event/occurrence in the system, Ingress, Egress, NA.")
    time_period: ManagementTimePeriodEnum = Field(json_schema_extra={"is_config": False}, description="Indicates the time-period increments during which PM data is collected.", alias="time-period")
    service_affect: ServiceAffectFmEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates if an alarm is service affecting or non-service affecting.\nNSA indicates non-service affecting.\nSA indicates service affecting.", default=None, alias="service-affect")
    severity_level: SeverityLevelEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the notification code (severity level) associated with the alarm type of service affecting.", default=None, alias="severity-level")
    occurrence_date_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Indicates the occurrence date and time of the alarm by the month of the year, the day of the month, hour of the day, the minute of the hour, and the second of the minute.", default=None, alias="occurrence-date-time")
    condition_description: str | None = Field(json_schema_extra={"is_config": False}, description="Describes the condition that caused the alarm.", min_length=0, max_length=255, default=None, alias="condition-description")
    fm_entity_type: EntityTypeFmEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the entity type the condition associated, which provides additional information for the object instance having the condition.\nentity type is not exactly same as MO. Entity type have smaller granularity referring to\ndifferent service functions, e.g. 100GBase-R, 40GBase-R, 100GBase-R, ODU4, ODU2, ODU3, OTU4, OTUC2...\nSeparate functions will have different entity types so that profile can be set differently for different\nservice function which is more corresponding to user application.", default=None, alias="fm-entity-type")
    alarm_id: str | None = Field(json_schema_extra={"is_config": False}, description="A system assigned unique identified to the alarm.", min_length=0, max_length=128, default=None, alias="alarm-id")

class Fault(YangBaseModel):
    """fault management MO, always exist"""

    alarm_profile: RestconfList[AlarmProfileItem] | None = Field(json_schema_extra={"is_config": True}, description="Alarm profile defines the severity profile of alarm and event.", default=None, alias="alarm-profile")
    standing_condition: RestconfList[StandingConditionItem] | None = Field(json_schema_extra={"is_config": False}, description="The list includes active standing alarms.", default=None, alias="standing-condition")

class PmpTypeEnum(str, Enum):
    """Enumeration for PmpTypeEnum
    
    Values:
      * not-applicable: not applicable
      * odu-nend-egress: PM point of ODU at near end and egress
      * odu-nend-ingress: PM point of ODU at near end and ingress
      * otu-nend-ingress: PM point of OTU at near end and ingress
      * delay-measurement-odu: delay measurement PM point of ODU
      * coherent-optical-interface: PM point of coherent optical interface
      * optical-power: PM point of optical power
      * loss: PM point of LOS seconds
      * ethernet-nend-ingress: PM point of Ethernet at near end and ingress
      * ethernet-nend-egress: PM point of Ethernet at near end and egress
      * fec: PM point of FEC
      * fc-nend-ingress: PM point of FC at near end and ingress
      * sonet-s-nend-ingress: PM point of OCn at near end and ingress
      * sdh-rs-nend-ingress: PM point of STMn at near end and egress
      * sonet-s-nend-egress: PM point of OCn at near end and ingress
      * sdh-rs-nend-egress: PM point of STMn at near end and egress
      * shelf-temperature: PM point of shelf temperature
      * equipment-temperature: PM point of equipment temperature
      * optical-power-lane: PM point of optical power with multiple lanes
      * protection-switch: PM point of protection switch
      * loss-txrx: PM point of LOS seconds - Rx and Tx
      * optical-power-ingress: PM point of received optical power
      * optical-power-egress: PM point of transmitted optical power
      * odu-encryption: PM point of ODU encryption
      * pilot-tone: PM point of pilot tone
      * loss-tx: PM point of LOS seconds - TX only
      * return-loss: PM point of optical return loss
      * pcs-nend-ingress: PM point of Ethernet PSC layer at near end and ingress
      * mac-nend-ingress: IEEE PM point of Ethernet MAC layer at near end and ingress
      * mac-nend-egress: IEEE PM point of Ethernet MAC layer at near end and egress
      * ethernet-error-ingress: IEEE PM point of Ethernet MAC layer ERROR at near end and ingress
      * ethernet-error-egress: IEEE PM point of Ethernet MAC layer ERROR at near end and egress
      * rtd-osc: PM point of Round Trip Delay Measurement over OSC
      * oc3-osc: PM point of OC3 OSC digital pm
      * all: ALL
    """

    NOT_APPLICABLE = "not-applicable"
    ODU_NEND_EGRESS = "odu-nend-egress"
    ODU_NEND_INGRESS = "odu-nend-ingress"
    OTU_NEND_INGRESS = "otu-nend-ingress"
    DELAY_MEASUREMENT_ODU = "delay-measurement-odu"
    COHERENT_OPTICAL_INTERFACE = "coherent-optical-interface"
    OPTICAL_POWER = "optical-power"
    LOSS = "loss"
    ETHERNET_NEND_INGRESS = "ethernet-nend-ingress"
    ETHERNET_NEND_EGRESS = "ethernet-nend-egress"
    FEC = "fec"
    FC_NEND_INGRESS = "fc-nend-ingress"
    SONET_S_NEND_INGRESS = "sonet-s-nend-ingress"
    SDH_RS_NEND_INGRESS = "sdh-rs-nend-ingress"
    SONET_S_NEND_EGRESS = "sonet-s-nend-egress"
    SDH_RS_NEND_EGRESS = "sdh-rs-nend-egress"
    SHELF_TEMPERATURE = "shelf-temperature"
    EQUIPMENT_TEMPERATURE = "equipment-temperature"
    OPTICAL_POWER_LANE = "optical-power-lane"
    PROTECTION_SWITCH = "protection-switch"
    LOSS_TXRX = "loss-txrx"
    OPTICAL_POWER_INGRESS = "optical-power-ingress"
    OPTICAL_POWER_EGRESS = "optical-power-egress"
    ODU_ENCRYPTION = "odu-encryption"
    PILOT_TONE = "pilot-tone"
    LOSS_TX = "loss-tx"
    RETURN_LOSS = "return-loss"
    PCS_NEND_INGRESS = "pcs-nend-ingress"
    MAC_NEND_INGRESS = "mac-nend-ingress"
    MAC_NEND_EGRESS = "mac-nend-egress"
    ETHERNET_ERROR_INGRESS = "ethernet-error-ingress"
    ETHERNET_ERROR_EGRESS = "ethernet-error-egress"
    RTD_OSC = "rtd-osc"
    OC3_OSC = "oc3-osc"
    ALL = "all"

class PmParameterEnum(str, Enum):
    """Enumeration for PmParameterEnum
    
    Values:
      * all: all pm-parameters
      * EB: Errored Block
      * ES: Errored Seconds
      * SES: Severely Errored Seconds
      * UAS: Unavailable Seconds
      * DELAY: Value of Delay Measurement time on ODU
      * DELAY-max: Max value of Delay Measurement time on ODU
      * DELAY-min: Min value of Delay Measurement time on ODU
      * DGD: Value of Differential Group Delay
      * DGD-max: Maximum of Differential Group Delay
      * DGD-min: Minimum of Differential Group Delay
      * CD: Value of Chromatic Dispersion
      * CD-max: Maximum of Chromatic Dispersion
      * CD-min: Minimum of Chromatic Dispersion
      * OSNR:  Current value of OSNR, The result could be OSNR value in dB
      * OSNR-max: Maximum of OSNR. The result could be OSNR value in dB
      * OSNR-min: Minimum of OSNR. The result could be OSNR value in dB
      * Q-factor: Current value of Q-factor
      * Q-factor-max: Maximum of Q-factor
      * Q-factor-min: Minimum of Q-factor
      * OPR: Current Value of OPR    Optical Power Received
      * OPR-max: Maximum of OPR Optical Power Received
      * OPR-min: Minimum of OPR Optical Power Receive
      * LOSS: Loss of Signal Seconds
      * SE: SymbolErrors
      * DropEvents: DropEvents
      * Octets: Octets
      * Pkts: Pkts
      * BroadcastPkts: BroadcastPkts
      * MulticastPkts: MulticastPkts
      * CRCAlignErrors: CRCAlignErrors
      * UndersizePkts: UndersizePkts
      * OversizePkts: OversizePkts
      * Fragments: Fragmentsments
      * Jabbers: Jabbers
      * Pkts64Octets: Pkts64Octets
      * Pkts65to127Octets: Pkts65to127Octets
      * Pkts128to255Octets: Pkts128to255Octets
      * Pkts256to511Octets: Pkts256to511Octets
      * Pkts512to1023Octets: Pkts512to1023Octets
      * Pkts1024to1518Octets: Pkts1024to1518Octets
      * Utilization: Utilization
      * Utilization-max: Maximum of Utilization
      * Utilization-min: Minimum of Utilization
      * BE-FEC: Bit Error Forward Error Correction
      * UBE-FEC: Uncorrected Block Error Forward Error Correction
      * BER-FEC: Bit Error Rate before Forward Error Correction
      * BER-FEC-max: Maximum of Bit Error Rate before Forward Error Correction
      * BER-FEC-min: Minimum of Bit Error Rate before Forward Error Correction
      * OPT: Current Value of OPT    Optical Power Transmitted
      * OPT-max: Maximum of OPT Optical Power Transmitted
      * OPT-min: Minimum of OPT Optical Power Transmitted
      * PDL: Current value of Polarization Dependent Loss
      * PDL-max: Maximum of Polarization Dependent Loss
      * PDL-min: Minimum of Polarization Dependent Loss
      * OFT: Current Value of OFT Optical Frequency Transmitted
      * OFT-max: Maximum of OFT Optical Frequency Transmitted
      * OFT-min: Minimum of OFT Optical Frequency Transmitted
      * OFR: Current Value of OFR Optical Frequency Received
      * OFR-max: Maximum of OFR Optical Frequency Received
      * OFR-min: Minimum of OFR Optical Frequency Received
      * BBE: Background Block Error
      * OFS: Out of Frame Seconds
      * CV: Coding Violation
      * SEFS: Severely Errored Frame Second
      * OPR-lane-high: Current Value of the highest lane Optical Power received for multiple lanes
      * OPR-lane-high-max: Maximum of the highest lane Optical Power received for multiple lanes
      * OPR-lane-high-min: Minimum of the highest lane Optical Power received for multiple lanes
      * OPR-lane-low: Current Value of the lowest lane Optical Power received for multiple lanes
      * OPR-lane-low-max: Maximum of the lowest lane Optical Power received for multiple lanes
      * OPR-lane-low-min: Minimum of the lowest lane Optical Power received for multiple lanes
      * OPR-total: Current Value of total Optical Power received for multiple lanes
      * OPR-total-max: Maximum of total Optical Power received for multiple lanes
      * OPR-total-min: Minimum of total Optical Power received for multiple lanes
      * OPT-lane-high: Current Value of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-high-max: Maximum of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-high-min: Minimum of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low: Current Value of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low-max: Maximum of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low-min: Minimum of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-total: Current Value of total Optical Power transmitted for multiple lanes
      * OPT-total-max: Maximum of total Optical Power transmitted for multiple lanes
      * OPT-total-min: Minimum of total Optical Power transmitted for multiple lanes
      * Tmodule: The module temperature
      * Tinlet: The inlet temperature
      * Toutlet: The outlet temperature
      * Tmodule-max: Maximum of the module temperature
      * Tmodule-min: Minimum of the module temperature
      * Tinlet-max: Maximum of the inlet temperature
      * Tinlet-min: Minimum of the inlet temperature
      * Toutlet-max: Maximum of the outlet temperature
      * Toutlet-min: Minimum of the outlet temperature
      * BER-POST-FEC: Bit Error Rate Post Forward Error Correction
      * BER-POST-FEC-max: Maximum of Bit Error Rate Post Forward Error Correction
      * BER-POST-FEC-min: Minimum of Bit Error Rate Post Forward Error Correction
      * PSD: Protection Switch Duration
      * PSC: Protection Switch Count
      * LOSS-Tx: Loss of Signal Seconds of Transmit side
      * LOSS-Rx: Loss of Signal Seconds of Receive side
      * Encryption-fail-rx: Encryption frame fail.
      * PTFS: Pilot Tone Failed Seconds
      * ORL: Optical return loss
      * ORL-max: Maximum of Optical return loss
      * ORL-min: Minimum of Optical return loss
      * ORL-avg: Average of Optical return loss
      * DELAY-avg: Average value of Delay Measurement time on ODU
      * DGD-avg: Average of Differential Group Delay
      * CD-avg: Average of Chromatic Dispersion
      * OSNR-avg: Average of OSNR. The result could be OSNR value in dB
      * Q-factor-avg: Average of Q-factor
      * OPR-avg: Average of OPR Optical Power Receive
      * OPT-avg: Average of OPT Optical Power Transmitted
      * BER-FEC-avg: Average of Bit Error Rate before Forward Error Correction
      * BER-POST-FEC-avg: Average of Bit Error Rate Post Forward Error Correction
      * PDL-avg: Average of Polarization Dependent Loss
      * OFT-avg: Average of OFT Optical Frequency Transmitted
      * OFR-avg: Average of OFR Optical Frequency Received
      * OPR-lane-high-avg: Average of the highest lane Optical Power received for multiple lanes
      * OPR-lane-low-avg: Average of the lowest lane Optical Power received for multiple lanes
      * OPR-total-avg: Average of total Optical Power received for multiple lanes
      * OPT-lane-high-avg: Average of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low-avg: Average of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-total-avg: Average of total Optical Power transmitted for multiple lanes
      * Tmodule-avg: Average of the module temperature
      * Tinlet-avg: Average of the inlet temperature
      * Toutlet-avg: Average of the outlet temperature
      * Utilization-avg: Average of Utilization
      * DELAY-frame: Value of Delay Measurement frame on ODU
      * DELAY-frame-max: Max value of Delay Measurement frame on ODU
      * DELAY-frame-min: Min value of Delay Measurement frame on ODU
      * DELAY-frame-avg: Average value of Delay Measurement frame on ODU
      * CBE-FEC: Corrected Block Error Forward Error Correction
      * FEB: Farend Error Block counter, Backward Error Indicator
      * IAE: Incoming Alignment Error seconds
      * BIAE: Backward Incoming Alignment Error seconds
      * BE: BIP error
      * PktsERR: Errored Packets
      * BBER: Background Block Error Rate
      * BBER-max: Max value of Background Block Error Rate
      * BBER-min: Min value of Background Block Error Rate
      * BBER-avg: AVG value of Background Block Error Rate
      * SESR: Severely Errored Seconds Rate
      * SESR-max: Max value of Severely Errored Seconds Rate
      * SESR-min: Min value of Severely Errored Seconds Rate
      * SESR-avg: Avg value of Severely Errored Seconds Rate
      * SOP: SOP Change Rate
      * SOP_max: Max value of SOP Change Rate
      * SOP_min: Min value of SOP Change Rate
      * SOP_avg: Avg value of SOP Change Rate
      * DM-Distance: Delay Measurement Distance
      * DM-Distance-max: Max value of RTD Delay Measurement Distance
      * DM-Distance-min: Min value of RTD Delay Measurement Distance
      * DM-Distance-avg: Avg value of RTD Delay Measurement Distance
      * RTD: Round Trip Delay
      * RTD-max: Max value of Round Trip Delay
      * RTD-min: Min value of Round Trip Delay
      * RTD-avg: Avg value of Round Trip Delay
      * RTD-Baseline: Round Trip Delay Baseline
      * RTD-Baseline-max: Max value of Round Trip Delay Baseline
      * RTD-Baseline-min: Min value of Round Trip Delay Baseline
      * RTD-Baseline-avg: Avg value of Round Trip Delay Baseline
    """

    ALL = "all"
    EB = "EB"
    ES = "ES"
    SES = "SES"
    UAS = "UAS"
    DELAY = "DELAY"
    DELAY_MAX = "DELAY-max"
    DELAY_MIN = "DELAY-min"
    DGD = "DGD"
    DGD_MAX = "DGD-max"
    DGD_MIN = "DGD-min"
    CD = "CD"
    CD_MAX = "CD-max"
    CD_MIN = "CD-min"
    OSNR = "OSNR"
    OSNR_MAX = "OSNR-max"
    OSNR_MIN = "OSNR-min"
    Q_FACTOR = "Q-factor"
    Q_FACTOR_MAX = "Q-factor-max"
    Q_FACTOR_MIN = "Q-factor-min"
    OPR = "OPR"
    OPR_MAX = "OPR-max"
    OPR_MIN = "OPR-min"
    LOSS = "LOSS"
    SE = "SE"
    DROPEVENTS = "DropEvents"
    OCTETS = "Octets"
    PKTS = "Pkts"
    BROADCASTPKTS = "BroadcastPkts"
    MULTICASTPKTS = "MulticastPkts"
    CRCALIGNERRORS = "CRCAlignErrors"
    UNDERSIZEPKTS = "UndersizePkts"
    OVERSIZEPKTS = "OversizePkts"
    FRAGMENTS = "Fragments"
    JABBERS = "Jabbers"
    PKTS64OCTETS = "Pkts64Octets"
    PKTS65TO127OCTETS = "Pkts65to127Octets"
    PKTS128TO255OCTETS = "Pkts128to255Octets"
    PKTS256TO511OCTETS = "Pkts256to511Octets"
    PKTS512TO1023OCTETS = "Pkts512to1023Octets"
    PKTS1024TO1518OCTETS = "Pkts1024to1518Octets"
    UTILIZATION = "Utilization"
    UTILIZATION_MAX = "Utilization-max"
    UTILIZATION_MIN = "Utilization-min"
    BE_FEC = "BE-FEC"
    UBE_FEC = "UBE-FEC"
    BER_FEC = "BER-FEC"
    BER_FEC_MAX = "BER-FEC-max"
    BER_FEC_MIN = "BER-FEC-min"
    OPT = "OPT"
    OPT_MAX = "OPT-max"
    OPT_MIN = "OPT-min"
    PDL = "PDL"
    PDL_MAX = "PDL-max"
    PDL_MIN = "PDL-min"
    OFT = "OFT"
    OFT_MAX = "OFT-max"
    OFT_MIN = "OFT-min"
    OFR = "OFR"
    OFR_MAX = "OFR-max"
    OFR_MIN = "OFR-min"
    BBE = "BBE"
    OFS = "OFS"
    CV = "CV"
    SEFS = "SEFS"
    OPR_LANE_HIGH = "OPR-lane-high"
    OPR_LANE_HIGH_MAX = "OPR-lane-high-max"
    OPR_LANE_HIGH_MIN = "OPR-lane-high-min"
    OPR_LANE_LOW = "OPR-lane-low"
    OPR_LANE_LOW_MAX = "OPR-lane-low-max"
    OPR_LANE_LOW_MIN = "OPR-lane-low-min"
    OPR_TOTAL = "OPR-total"
    OPR_TOTAL_MAX = "OPR-total-max"
    OPR_TOTAL_MIN = "OPR-total-min"
    OPT_LANE_HIGH = "OPT-lane-high"
    OPT_LANE_HIGH_MAX = "OPT-lane-high-max"
    OPT_LANE_HIGH_MIN = "OPT-lane-high-min"
    OPT_LANE_LOW = "OPT-lane-low"
    OPT_LANE_LOW_MAX = "OPT-lane-low-max"
    OPT_LANE_LOW_MIN = "OPT-lane-low-min"
    OPT_TOTAL = "OPT-total"
    OPT_TOTAL_MAX = "OPT-total-max"
    OPT_TOTAL_MIN = "OPT-total-min"
    TMODULE = "Tmodule"
    TINLET = "Tinlet"
    TOUTLET = "Toutlet"
    TMODULE_MAX = "Tmodule-max"
    TMODULE_MIN = "Tmodule-min"
    TINLET_MAX = "Tinlet-max"
    TINLET_MIN = "Tinlet-min"
    TOUTLET_MAX = "Toutlet-max"
    TOUTLET_MIN = "Toutlet-min"
    BER_POST_FEC = "BER-POST-FEC"
    BER_POST_FEC_MAX = "BER-POST-FEC-max"
    BER_POST_FEC_MIN = "BER-POST-FEC-min"
    PSD = "PSD"
    PSC = "PSC"
    LOSS_TX = "LOSS-Tx"
    LOSS_RX = "LOSS-Rx"
    ENCRYPTION_FAIL_RX = "Encryption-fail-rx"
    PTFS = "PTFS"
    ORL = "ORL"
    ORL_MAX = "ORL-max"
    ORL_MIN = "ORL-min"
    ORL_AVG = "ORL-avg"
    DELAY_AVG = "DELAY-avg"
    DGD_AVG = "DGD-avg"
    CD_AVG = "CD-avg"
    OSNR_AVG = "OSNR-avg"
    Q_FACTOR_AVG = "Q-factor-avg"
    OPR_AVG = "OPR-avg"
    OPT_AVG = "OPT-avg"
    BER_FEC_AVG = "BER-FEC-avg"
    BER_POST_FEC_AVG = "BER-POST-FEC-avg"
    PDL_AVG = "PDL-avg"
    OFT_AVG = "OFT-avg"
    OFR_AVG = "OFR-avg"
    OPR_LANE_HIGH_AVG = "OPR-lane-high-avg"
    OPR_LANE_LOW_AVG = "OPR-lane-low-avg"
    OPR_TOTAL_AVG = "OPR-total-avg"
    OPT_LANE_HIGH_AVG = "OPT-lane-high-avg"
    OPT_LANE_LOW_AVG = "OPT-lane-low-avg"
    OPT_TOTAL_AVG = "OPT-total-avg"
    TMODULE_AVG = "Tmodule-avg"
    TINLET_AVG = "Tinlet-avg"
    TOUTLET_AVG = "Toutlet-avg"
    UTILIZATION_AVG = "Utilization-avg"
    DELAY_FRAME = "DELAY-frame"
    DELAY_FRAME_MAX = "DELAY-frame-max"
    DELAY_FRAME_MIN = "DELAY-frame-min"
    DELAY_FRAME_AVG = "DELAY-frame-avg"
    CBE_FEC = "CBE-FEC"
    FEB = "FEB"
    IAE = "IAE"
    BIAE = "BIAE"
    BE = "BE"
    PKTSERR = "PktsERR"
    BBER = "BBER"
    BBER_MAX = "BBER-max"
    BBER_MIN = "BBER-min"
    BBER_AVG = "BBER-avg"
    SESR = "SESR"
    SESR_MAX = "SESR-max"
    SESR_MIN = "SESR-min"
    SESR_AVG = "SESR-avg"
    SOP = "SOP"
    SOP_MAX = "SOP_max"
    SOP_MIN = "SOP_min"
    SOP_AVG = "SOP_avg"
    DM_DISTANCE = "DM-Distance"
    DM_DISTANCE_MAX = "DM-Distance-max"
    DM_DISTANCE_MIN = "DM-Distance-min"
    DM_DISTANCE_AVG = "DM-Distance-avg"
    RTD = "RTD"
    RTD_MAX = "RTD-max"
    RTD_MIN = "RTD-min"
    RTD_AVG = "RTD-avg"
    RTD_BASELINE = "RTD-Baseline"
    RTD_BASELINE_MAX = "RTD-Baseline-max"
    RTD_BASELINE_MIN = "RTD-Baseline-min"
    RTD_BASELINE_AVG = "RTD-Baseline-avg"

class UnitOfValueEnum(str, Enum):
    """Enumeration for UnitOfValueEnum
    
    Values:
      * not-applicable
      * dBm
      * Microseconds
      * ps
      * ps/nm
      * dB
      * Seconds
      * Packets
      * Events
      * Octets
      * Bits
      * Bits/s
      * Blocks
      * Times
      * Percentage
      * Bit-ratio
      * MHz
      * Celsius
      * Frames
      * rads/s
      * Kilometers
    """

    NOT_APPLICABLE = "not-applicable"
    DBM = "dBm"
    MICROSECONDS = "Microseconds"
    PS = "ps"
    PS_NM = "ps/nm"
    DB = "dB"
    SECONDS = "Seconds"
    PACKETS = "Packets"
    EVENTS = "Events"
    OCTETS = "Octets"
    BITS = "Bits"
    BITS_S = "Bits/s"
    BLOCKS = "Blocks"
    TIMES = "Times"
    PERCENTAGE = "Percentage"
    BIT_RATIO = "Bit-ratio"
    MHZ = "MHz"
    CELSIUS = "Celsius"
    FRAMES = "Frames"
    RADS_S = "rads/s"
    KILOMETERS = "Kilometers"

class PmThresholdsValueItem(YangBaseModel):
    """The list of entries of performance monitoring threshold value."""

    pm_parameter: PmParameterEnum = Field(json_schema_extra={"is_config": True}, description="Performance Monitoring parameter, which could be a counter or gauge parameter, the later support current, max and min values.", alias="pm-parameter")
    pm_high_threshold: str | None = Field(json_schema_extra={"is_config": True}, description="Specifies the desired high threshold value of the selected performance monitoring parameter.", min_length=1, max_length=32, default=None, alias="pm-high-threshold")
    pm_low_threshold: str | None = Field(json_schema_extra={"is_config": True}, description="Specifies the desired low threshold value of the selected performance monitoring parameter.", min_length=1, max_length=32, default=None, alias="pm-low-threshold")
    pm_unit: UnitOfValueEnum | None = Field(json_schema_extra={"is_config": False}, description="The unit of the performance monitoring value.", default=None, alias="pm-unit")

class PmThresholds(YangBaseModel):
    """Containing the pm thresholds corresponding to each performance monitoring parameter."""

    pm_thresholds_value: RestconfList[PmThresholdsValueItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of entries of performance monitoring threshold value.", default=None, alias="pm-thresholds-value")

class PmPointItem(YangBaseModel):
    """The list of performance monitoring points associated with the monitored management object."""

    pm_entity: str = Field(json_schema_extra={"is_config": True}, description="Specifies the management object instance the performance monitoring data are collected for.", alias="pm-entity")
    pmp_type: PmpTypeEnum = Field(json_schema_extra={"is_config": True}, description="Specifies the type of performance monitoring point.", alias="pmp-type")
    pm_time_period: ManagementTimePeriodEnum = Field(json_schema_extra={"is_config": True}, description="Specifies the time-period increments during which PM data are collected.", alias="pm-time-period")
    supervision_switch: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enable/disable counting for all performance monitoring parameters of the given PMP.", default=EnableSwitchEnum.DISABLED, alias="supervision-switch")
    thresholding_switch: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enable/disable the TCA processing and reporting for all performance monitoring parameters of the given PM point.", default=EnableSwitchEnum.DISABLED, alias="thresholding-switch")
    history_recording: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Enable/disable the history data storage for all performance monitoring parameters of the given PM point.", default=EnableSwitchEnum.ENABLED, alias="history-recording")
    pm_thresholds: PmThresholds | None = Field(json_schema_extra={"is_config": True}, description="Containing the pm thresholds corresponding to each performance monitoring parameter.", default=None, alias="pm-thresholds")

class Performance(YangBaseModel):
    """Container for all PM-Points and for PM related attributes"""

    pmdaystart: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the hour of starting collecting 1-DAY monitoring parameters.\nTo reset the NE clock to the default value of 00:00 hours, the parameter should contain the value 0.", ge=0, le=23, default=0)
    statistics_enable: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The global switch for all system statistics data collection.", default=EnableSwitchEnum.ENABLED, alias="statistics-enable")
    pm_point: RestconfList[PmPointItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of performance monitoring points associated with the monitored management object.", default=None, alias="pm-point")

class ShelfPowerConsumptionItem(YangBaseModel):
    """List: shelf-power-consumption"""

    shelf_entity: str = Field(json_schema_extra={"is_config": True}, alias="shelf-entity")
    magic: int = Field(json_schema_extra={"is_config": True}, ge=0)
    power_consumption_current: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Current power consumption of the system.", default=None, alias="power-consumption-current")
    power_consumption_estimated_max: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Derived maximal power consumption around room temperature.", default=None, alias="power-consumption-estimated-max")

class PowerConsumption(YangBaseModel):
    """The shelf base power consumption"""

    shelf_power_consumption: RestconfList[ShelfPowerConsumptionItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="shelf-power-consumption")

class SourceEnum(str, Enum):
    """Enumeration for SourceEnum
    
    Values:
      * static
      * dhcp
    """

    STATIC = "static"
    DHCP = "dhcp"

class L2Dcn(YangBaseModel):
    """Container: l2-dcn"""

    ip_address: str = Field(json_schema_extra={"is_config": True}, description="IP Address of device", alias="ip-address")
    prefix_length: int = Field(json_schema_extra={"is_config": True}, description="The length of the subnet prefix", ge=0, le=128, alias="prefix-length")
    default_gateway: str | None = Field(json_schema_extra={"is_config": True}, description="Default Gateway", default=None, alias="default-gateway")
    source: SourceEnum | None = Field(json_schema_extra={"is_config": False}, default=None)
    current_ip_address: str | None = Field(json_schema_extra={"is_config": False}, description="Current IP Address of device", default=None, alias="current-ip-address")
    current_prefix_length: int | None = Field(json_schema_extra={"is_config": False}, description="The current length of the subnet prefix", ge=0, le=128, default=None, alias="current-prefix-length")
    current_default_gateway: str | None = Field(json_schema_extra={"is_config": False}, description="Current Default Gateway", default=None, alias="current-default-gateway")
    mac_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})$", v))] | None = Field(json_schema_extra={"is_config": False}, description="MAC Address of device", default=None, alias="mac-address")

class SourceAddressSelectModeEnum(str, Enum):
    """Enumeration for SourceAddressSelectModeEnum
    
    Values:
      * loopback-prefer: Select the numerically lowest address configured on loopback interfaces if one exists
      * link-prefer: Select the address configured on the outgoing interface
    """

    LOOPBACK_PREFER = "loopback-prefer"
    LINK_PREFER = "link-prefer"

class IfTypeEnum(str, Enum):
    """Enumeration for IfTypeEnum
    
    Values:
      * other
      * ethernetCsmacd: For all Ethernet-like interfaces, regardless of speed, as per RFC 3635.
      * ppp
      * softwareLoopback
      * lapd
      * oscx
    """

    OTHER = "other"
    ETHERNETCSMACD = "ethernetCsmacd"
    PPP = "ppp"
    SOFTWARELOOPBACK = "softwareLoopback"
    LAPD = "lapd"
    OSCX = "oscx"

class DuplexModeEnum(str, Enum):
    """Enumeration for DuplexModeEnum
    
    Values:
      * NA
      * full
      * half
    """

    NA = "NA"
    FULL = "full"
    HALF = "half"

class EthernetRateEnum(str, Enum):
    """Enumeration for EthernetRateEnum
    
    Values:
      * NA
      * 10
      * 100
      * 1000
      * max-rate
    """

    NA = "NA"
    _10 = "10"
    _100 = "100"
    _1000 = "1000"
    MAX_RATE = "max-rate"

class FlowControlEnum(str, Enum):
    """Enumeration for FlowControlEnum
    
    Values:
      * NA: not available
      * off: No pause frames are supported
      * tx-rx: Symmetric flow (transmit and receive)
      * tx: Transmit direction only
      * rx: Receive direction only
    """

    NA = "NA"
    OFF = "off"
    TX_RX = "tx-rx"
    TX = "tx"
    RX = "rx"

class Ethernet(YangBaseModel):
    """The Ethernet attributes of an Ethernet interface."""

    auto_negotiation: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Auto negotiation mode.", default=EnableSwitchEnum.ENABLED, alias="auto-negotiation")
    duplex_mode: DuplexModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Duplex Mode; only valid if auto negotiation is disabled.", default=DuplexModeEnum.FULL, alias="duplex-mode")
    operational_duplex_mode: DuplexModeEnum | None = Field(json_schema_extra={"is_config": False}, description="Operational duplex mode.", default=DuplexModeEnum.NA, alias="operational-duplex-mode")
    ethernet_rate: EthernetRateEnum | None = Field(json_schema_extra={"is_config": True}, description="Required Ethernet Rate; only valid if auto negotiation is disabled.", default=EthernetRateEnum.MAX_RATE, alias="ethernet-rate")
    operational_ethernet_rate: EthernetRateEnum | None = Field(json_schema_extra={"is_config": False}, description="Operation ethernet rate.", default=EthernetRateEnum.NA, alias="operational-ethernet-rate")
    flow_control: FlowControlEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies the type of flow control to be supported.", default=FlowControlEnum.TX_RX, alias="flow-control")
    operational_flow_control: FlowControlEnum | None = Field(json_schema_extra={"is_config": False}, description="Operational flow control.", default=FlowControlEnum.NA, alias="operational-flow-control")
    mac_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})$", v))] | None = Field(json_schema_extra={"is_config": False}, description="MAC Address of the port.", default="00:00:00:00:00:00", alias="mac-address")
    eth_port_id: int | None = Field(json_schema_extra={"is_config": True}, description="The port ID in ethernet driver.", ge=0, default=0, alias="eth-port-id")
    eth_resource_ref: str = Field(json_schema_extra={"is_config": True}, description="Reference of the lower layer resource associated with this interface.", alias="eth-resource-ref")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")

class PppTypeEnum(str, Enum):
    """Enumeration for PppTypeEnum
    
    Values:
      * gcc0
    """

    GCC0 = "gcc0"

class Ppp(YangBaseModel):
    """Container: ppp"""

    ppp_type: PppTypeEnum = Field(json_schema_extra={"is_config": True}, description="Specifies the link type associated with the ppp.", alias="ppp-type")
    negotiated_ppp_mru: int | None = Field(json_schema_extra={"is_config": False}, description="The PPP MRU after nogotiation with peer.", ge=64, le=1500, default=1500, alias="negotiated-ppp-mru")
    peer_ip_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The IP address on the peer node.", default="0.0.0.0", alias="peer-ip-address")
    ppp_pf_ref: str = Field(json_schema_extra={"is_config": True}, description="Reference of the ppp profile.", alias="ppp-pf-ref")
    ppp_resource_ref: str = Field(json_schema_extra={"is_config": True}, description="Reference of the lower layer resource associated with this interface.", alias="ppp-resource-ref")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")

class OriginEnum(str, Enum):
    """Enumeration for OriginEnum
    
    Values:
      * other: None of the following.
      * static: Indicates that the address has been statically configured - for example, using NETCONF or a Command Line Interface.
      * dhcp: Indicates an address that has been assigned to this system by a DHCP server.
      * link-layer: Indicates an address created by IPv6 stateless autoconfiguration that embeds a link-layer address in its interface identifier.
      * random: Indicates an address chosen by the system at random, e.g., an IPv4 address within 169.254/16, an RFC 4941 temporary address, or an RFC 7217 semantically opaque address.
    """

    OTHER = "other"
    STATIC = "static"
    DHCP = "dhcp"
    LINK_LAYER = "link-layer"
    RANDOM = "random"

class IpAddress(YangBaseModel):
    """The IP address on the interface."""

    ip: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] = Field(json_schema_extra={"is_config": True}, description="The IP address on the interface.")
    origin: OriginEnum | None = Field(json_schema_extra={"is_config": False}, description="The origin of this address.", default=OriginEnum.STATIC)
    prefix_length: int = Field(json_schema_extra={"is_config": True}, description="The length of the subnet prefix.", ge=0, le=128, alias="prefix-length")

class IpUnnumbered(YangBaseModel):
    """The IP unnumbered configurations."""

    unnum_enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="Indicates that the interface is unnumbered. By default the interface is numbered, i.e., expected to have an IP address configuration.", default=False, alias="unnum-enabled")
    parent_interface: str = Field(json_schema_extra={"is_config": True}, description="Reference of the parent interface of the unnumbered interface.", alias="parent-interface")

class Ipv4(YangBaseModel):
    """Parameters for the IPv4 address family."""

    ipv4_forwarding: bool | None = Field(json_schema_extra={"is_config": True}, description="Controls IPv4 packet forwarding of datagrams received by,\nbut not addressed to, this interface.  IPv4 routers\nforward datagrams.  IPv4 hosts do not (except those\nsource-routed via the host).", default=True, alias="ipv4-forwarding")
    proxy_arp: bool | None = Field(json_schema_extra={"is_config": True}, description="Proxy ARP switch on an ethernetCsmacd interface.\n\nCondition (when): ../../if-type = 'ethernetCsmacd'", default=False, alias="proxy-arp")
    mtu: int | None = Field(json_schema_extra={"is_config": True}, description="The size, in octets, of the largest IPv4 packet that the\ninterface will send and receive.\n\nThe server may restrict the allowed values for this leaf,\ndepending on the interface's type.\n\nAll interfaces except LOOPBACK range 68..1500, octets.\n\nIf this leaf is not configured, the operationally used MTU\ndepends on the interface's type.", ge=68, default=1500)
    ipv4_address_assignment_method: SourceEnum | None = Field(json_schema_extra={"is_config": True}, description="IPv4 address assignment method.", default=None, alias="ipv4-address-assignment-method")
    ip_address: IpAddress | None = Field(json_schema_extra={"is_config": True}, description="The IP address on the interface.", default=None, alias="ip-address")
    ip_unnumbered: IpUnnumbered | None = Field(json_schema_extra={"is_config": True}, description="The IP unnumbered configurations.", default=None, alias="ip-unnumbered")

class Ipv6AddressAssignmentMethodEnum(str, Enum):
    """Enumeration for Ipv6AddressAssignmentMethodEnum
    
    Values:
      * static
      * autoconfig
    """

    STATIC = "static"
    AUTOCONFIG = "autoconfig"

class Ipv6AddressItem(YangBaseModel):
    """The IP address on the interface.
    index=1 ipv6 address,
    index=2 ipv6 link-local address, read-only
    """

    index: int = Field(json_schema_extra={"is_config": True}, description="an uint16 index.", ge=0)
    ip: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$", v)), AfterValidator(lambda v: check_pattern("^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v))] = Field(json_schema_extra={"is_config": True}, description="The IP address on the interface.")
    origin: OriginEnum | None = Field(json_schema_extra={"is_config": False}, description="The origin of this address.", default=OriginEnum.STATIC)
    prefix_length: int = Field(json_schema_extra={"is_config": True}, description="The length of the subnet prefix.", ge=0, le=128, alias="prefix-length")

class Ipv6(YangBaseModel):
    """Parameters for the IPv6 address family."""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="Controls whether IPv6 is enabled or disabled on this\ninterface.  When IPv6 is enabled, this interface is\nconnected to an IPv6 stack, and the interface can send\nand receive IPv6 packets.", default=False)
    ipv6_forwarding: bool | None = Field(json_schema_extra={"is_config": False}, description="Controls IPv6 packet forwarding of datagrams received by,\nbut not addressed to, this interface.  IPv6 routers\nforward datagrams.  IPv6 hosts do not (except those\nsource-routed via the host).", default=False, alias="ipv6-forwarding")
    mtu: int | None = Field(json_schema_extra={"is_config": True}, description="The size, in octets, of the largest IPv6 packet that the\ninterface will send and receive.\n\nThe server may restrict the allowed values for this leaf,\ndepending on the interface's type.\n\nIf this leaf is not configured, the operationally used MTU\ndepends on the interface's type.", ge=1280, default=1500)
    ipv6_address_assignment_method: Ipv6AddressAssignmentMethodEnum | None = Field(json_schema_extra={"is_config": True}, description="IPv6 address assignment method.", default=Ipv6AddressAssignmentMethodEnum.AUTOCONFIG, alias="ipv6-address-assignment-method")
    ipv6_address: RestconfList[Ipv6AddressItem] | None = Field(json_schema_extra={"is_config": True}, description="The IP address on the interface.\nindex=1 ipv6 address,\nindex=2 ipv6 link-local address, read-only", default=None, alias="ipv6-address")

class OscxChannelEnum(str, Enum):
    """Enumeration for OscxChannelEnum
    
    Values:
      * 1
      * 2
    """

    _1 = "1"
    _2 = "2"

class Oscx(YangBaseModel):
    """OSCX (Optical Supervisory Channel Extended) interface"""

    oscx_channel: OscxChannelEnum = Field(json_schema_extra={"is_config": True}, description="Specifies the OSCX channel within the Optical Supervisory Channel.", alias="oscx-channel")
    oscx_resource_ref: str = Field(json_schema_extra={"is_config": True}, description="Reference of the lower layer resource associated with this interface.", alias="oscx-resource-ref")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")

class InterfaceItem(YangBaseModel):
    """The list of configured interfaces on the device."""

    if_name: str = Field(json_schema_extra={"is_config": True}, description="The name of the interface.", min_length=1, max_length=64, alias="if-name")
    if_description: str | None = Field(json_schema_extra={"is_config": True}, description="A textual description of the interface.", min_length=0, max_length=255, default=None, alias="if-description")
    if_type: IfTypeEnum = Field(json_schema_extra={"is_config": True}, description="The type of the interface. Refer to http://www.iana.org/assignments/smi-numbers", alias="if-type")
    vlan_dev_name: str | None = Field(json_schema_extra={"is_config": True}, description="The VLAN device name.", min_length=0, max_length=20, default=None, alias="vlan-dev-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.DOWN, alias="oper-status")
    avail_status: str | None = Field(json_schema_extra={"is_config": False}, description="Provided to qualify the operational, usage and/or administrative status attributes.\nThe value shall be a bits, management interface shall show the string with space separator ' ' per yang definition.\n\nFollowing available status indication shall be supported:\nFailed,Mismatch,LowerLayerDown,NotPresent,Shutdown,Degraded,Idle,Busy,\nHibernation,In-Test,Loopback,SoftwareUpgrade,Initializing,Unknown,Incomplete\n\nExample: an ODU can be failed without cross connection, the available status is 'Failed Idle'.\n\nProvided to qualify the operational, usage and/or administrative state attributes. The value of each\nstatus attribute may denote the presence of one or more particular conditions applicable to the resource.", default=None, alias="avail-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    ethernet: Ethernet | None = Field(json_schema_extra={"is_config": True}, description="The Ethernet attributes of an Ethernet interface.\n\nCondition (when): ../if-type = 'ethernetCsmacd'", default=None)
    ppp: Ppp | None = Field(json_schema_extra={"is_config": True}, description="Condition (when): ../if-type = 'ppp'", default=None)
    ipv4: Ipv4 | None = Field(json_schema_extra={"is_config": True}, description="Parameters for the IPv4 address family.", default=None)
    ipv6: Ipv6 | None = Field(json_schema_extra={"is_config": True}, description="Parameters for the IPv6 address family.", default=None)
    oscx: Oscx | None = Field(json_schema_extra={"is_config": True}, description="OSCX (Optical Supervisory Channel Extended) interface\n\nCondition (when): ../if-type = 'oscx'", default=None)

class RtpTypeEnum(str, Enum):
    """Enumeration for RtpTypeEnum
    
    Values:
      * direct: Routing pseudo-protocol that provides routes to directly connected networks.
      * static: Static routing pseudo-protocol.
      * ospfv2: OSPFv2 routing protocol
      * ebgp: eBGP routing protocol
    """

    DIRECT = "direct"
    STATIC = "static"
    OSPFV2 = "ospfv2"
    EBGP = "ebgp"

class NextHopItem(YangBaseModel):
    """Configuration of static next-hop."""

    index: str = Field(json_schema_extra={"is_config": True}, description="An user-specified identifier utilised to uniquely reference the next-hop entry in the next-hop list. The value of this index has no semantic meaning other than for referencing the entry.", min_length=1, max_length=128)
    outgoing_interface: str = Field(json_schema_extra={"is_config": True}, description="Reference of the outgoing interface.", alias="outgoing-interface")
    next_hop_address: str | None = Field(json_schema_extra={"is_config": True}, description="IP address of the next-hop.", default=None, alias="next-hop-address")
    metric: int | None = Field(json_schema_extra={"is_config": True}, description="metric of the next-hop.", ge=0, default=0)

class StaticRouteItem(YangBaseModel):
    """A list of static routes."""

    destination_prefix: str = Field(json_schema_extra={"is_config": True}, description="IP destination prefix.", alias="destination-prefix")
    description: str | None = Field(json_schema_extra={"is_config": True}, description="Textual description of the static route.", min_length=0, max_length=128, default=None)
    advertised: bool | None = Field(json_schema_extra={"is_config": True}, description="When set to YES, the static route is advertised in the routing\nprotocol. For OSPF, the static route will be advertised as an\nAS external route, if OSPF is configured as an ASBR.", default=False)
    next_hop: RestconfList[NextHopItem] | None = Field(json_schema_extra={"is_config": True}, description="Configuration of static next-hop.", default=None, alias="next-hop")

class OspfAreaTypeEnum(str, Enum):
    """Enumeration for OspfAreaTypeEnum
    
    Values:
      * normal
      * stub
    """

    NORMAL = "normal"
    STUB = "stub"

class OspfIfRoutingEnum(str, Enum):
    """Enumeration for OspfIfRoutingEnum
    
    Values:
      * active
      * passive
    """

    ACTIVE = "active"
    PASSIVE = "passive"

class OspfNetworkTypeEnum(str, Enum):
    """Enumeration for OspfNetworkTypeEnum
    
    Values:
      * broadcast
      * point-to-point
      * point-to-multipoint
    """

    BROADCAST = "broadcast"
    POINT_TO_POINT = "point-to-point"
    POINT_TO_MULTIPOINT = "point-to-multipoint"

class OspfAdjStatusEnum(str, Enum):
    """Enumeration for OspfAdjStatusEnum
    
    Values:
      * down
      * init
      * attempt
      * two-way
      * exstart
      * exchange
      * loading
      * full
    """

    DOWN = "down"
    INIT = "init"
    ATTEMPT = "attempt"
    TWO_WAY = "two-way"
    EXSTART = "exstart"
    EXCHANGE = "exchange"
    LOADING = "loading"
    FULL = "full"

class OspfAdjacencyItem(YangBaseModel):
    """attributes of OSPF adjacency."""

    ospf_neighbor_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] = Field(json_schema_extra={"is_config": False}, description="neighbor IP address of the OSPF adjacency.", alias="ospf-neighbor-address")
    neighbor_router_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$", v))] = Field(json_schema_extra={"is_config": False}, description="OSPF neighbor Router ID.", alias="neighbor-router-id")
    ospf_adj_status: OspfAdjStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="OSPF adjacency status.", default=None, alias="ospf-adj-status")

class OspfInterfaceItem(YangBaseModel):
    """Configuration of interface in an ospf area."""

    ospf_if_name: str = Field(json_schema_extra={"is_config": True}, description="Reference of the interface in OSPF area.", min_length=1, max_length=64, alias="ospf-if-name")
    ospf_linkpf: str = Field(json_schema_extra={"is_config": True}, description="Reference of the ospf link profile associated with the interface.", min_length=1, max_length=128, alias="ospf-linkpf")
    dr_priority: int | None = Field(json_schema_extra={"is_config": True}, description="The local system's priority to become the designated router", ge=0, default=1, alias="dr-priority")
    ospf_cost: int | None = Field(json_schema_extra={"is_config": True}, description="OSPF link cost.", ge=0, le=65535, default=None, alias="ospf-cost")
    ospf_if_routing: OspfIfRoutingEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies if Routing is enabled and if so, if Routing is passive or active.\nACTIVE - This link is advertised and routing messages are transported over this link.\nPASSIVE - This link is advertised, routing messages are not transported over this link.", default=OspfIfRoutingEnum.ACTIVE, alias="ospf-if-routing")
    ospf_network_type: OspfNetworkTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="OSPF Interface Network Types.", default=None, alias="ospf-network-type")
    ospf_host_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="host IP address for p2p unnumbered interface.", default=None, alias="ospf-host-address")
    ospf_adjacency: RestconfList[OspfAdjacencyItem] | None = Field(json_schema_extra={"is_config": False}, description="attributes of OSPF adjacency.", default=None, alias="ospf-adjacency")

class OspfAreaItem(YangBaseModel):
    """Configuration of ospf area."""

    ospf_area_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$", v))] = Field(json_schema_extra={"is_config": True}, description="OSPF Router Area ID.", alias="ospf-area-id")
    ospf_area_type: OspfAreaTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="OSPF Router Area Type.", default=OspfAreaTypeEnum.NORMAL, alias="ospf-area-type")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    ospf_interface: RestconfList[OspfInterfaceItem] | None = Field(json_schema_extra={"is_config": True}, description="Configuration of interface in an ospf area.", default=None, alias="ospf-interface")

class Ospf(YangBaseModel):
    """OSPF protocol."""

    router_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$", v))] = Field(json_schema_extra={"is_config": True}, description="OSPF Router ID.", alias="router-id")
    description: str | None = Field(json_schema_extra={"is_config": True}, description="Textual description of the OSPF instance.", min_length=0, max_length=128, default=None)
    ospf_asbr: bool | None = Field(json_schema_extra={"is_config": True}, description="OSPF Autonomous System Boundary Router.", default=True, alias="ospf-asbr")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.DOWN, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    ospf_area: RestconfList[OspfAreaItem] | None = Field(json_schema_extra={"is_config": True}, description="Configuration of ospf area.", default=None, alias="ospf-area")

class PeerTypeEnum(str, Enum):
    """Enumeration for PeerTypeEnum
    
    Values:
      * INTERNAL: internal (iBGP) peer
      * EXTERNAL: external (eBGP) peer
    """

    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"

class SessionStateEnum(str, Enum):
    """Enumeration for SessionStateEnum
    
    Values:
      * IDLE: neighbor is down, and in the Idle state of the FSM
      * CONNECT: neighbor is down, and the session is waiting for the underlying transport session to be established
      * ACTIVE: neighbor is down, and the local system is awaiting a connection from the remote peer
      * OPENSENT: neighbor is in the process of being established.  The local system has sent an OPEN message
      * OPENCONFIRM: neighbor is in the process of being established.  The local system is awaiting a NOTIFICATION or KEEPALIVE message
      * ESTABLISHED: neighbor is up - the BGP session with the peer is established
    """

    IDLE = "IDLE"
    CONNECT = "CONNECT"
    ACTIVE = "ACTIVE"
    OPENSENT = "OPENSENT"
    OPENCONFIRM = "OPENCONFIRM"
    ESTABLISHED = "ESTABLISHED"

class BgpNeighborTimers(YangBaseModel):
    """Timers related to a BGP neighbor"""

    connect_retry: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Time interval in seconds between attempts to establish a\nsession with the peer.", ge=1, le=65535, default=30, alias="connect-retry")
    hold_time: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Time interval in seconds that a BGP session will be\nconsidered active in the absence of keepalive or other\nmessages from the peer.  The hold-time is typically set to\n3x the keepalive-interval.", ge=0, le=65535, default=90, alias="hold-time")
    keepalive_interval: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Time interval in seconds between transmission of keepalive\nmessages to the neighbor.  Typically set to 1/3 the\nhold-time.", ge=0, le=65535, default=30, alias="keepalive-interval")
    minimum_advertisement_interval: Decimal64 | None = Field(json_schema_extra={"is_config": True}, description="Minimum time which must elapse between subsequent UPDATE\nmessages relating to a common set of NLRI being transmitted\nto a peer. This timer is referred to as\nMinRouteAdvertisementIntervalTimer by RFC 4721 and serves to\nreduce the number of UPDATE messages transmitted when a\nparticular set of NLRI exhibit instability.", ge=0, le=600, default=30, alias="minimum-advertisement-interval")
    negotiated_hold_time: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="The negotiated hold-time for the BGP session", default=None, alias="negotiated-hold-time")

class BgpNeighborTransport(YangBaseModel):
    """Transport session parameters for the BGP neighbor"""

    local_address: str | None = Field(json_schema_extra={"is_config": False}, description="Set the local IP (either IPv4 or IPv6) address to use for\nthe session when sending BGP update messages.  This may be\nexpressed as either an IP address or reference to the name\nof an interface.", default=None, alias="local-address")
    local_port: int | None = Field(json_schema_extra={"is_config": False}, description="Local TCP port being used for the TCP session supporting\nthe BGP session", ge=0, le=65535, default=None, alias="local-port")
    remote_address: str | None = Field(json_schema_extra={"is_config": False}, description="Remote address to which the BGP session has been\nestablished", default=None, alias="remote-address")
    remote_port: int | None = Field(json_schema_extra={"is_config": False}, description="Remote port being used by the peer for the TCP session\nsupporting the BGP session", ge=0, le=65535, default=None, alias="remote-port")

class BgpNeighborItem(YangBaseModel):
    """List of BGP neighbors configured on the local system,
    uniquely identified by peer IPv[46] address
    """

    neighbor_address: str = Field(json_schema_extra={"is_config": True}, description="Address of the BGP peer, either in IPv4 or IPv6", alias="neighbor-address")
    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="Whether the BGP peer is enabled. In cases where the enabled\nleaf is set to false, the local system should not initiate\nconnections to the neighbor, and should not respond to TCP\nconnections attempts from the neighbor. If the state of the\nBGP session is ESTABLISHED at the time that this leaf is set\nto false, the BGP session should be ceased.", default=True)
    peer_as: int = Field(json_schema_extra={"is_config": True}, description="AS number of the peer.", ge=0, alias="peer-as")
    peer_type: PeerTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Explicitly designate the peer or peer group as internal\n(iBGP) or external (eBGP).", default=None, alias="peer-type")
    description: str | None = Field(json_schema_extra={"is_config": True}, description="An optional textual description (intended primarily for use\nwith a peer or group", min_length=0, max_length=128, default=None)
    session_state: SessionStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Operational state of the BGP peer", default=SessionStateEnum.IDLE, alias="session-state")
    established_transitions: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Number of transitions to the Established state for the\nneighbor session.  This value is analogous to the\nbgpPeerFsmEstablishedTransitions object from the standard\nBGP-4 MIB", ge=0, le=18446744073709551615, default=None, alias="established-transitions")
    supported_capabilities: RestconfList[str] | None = Field(json_schema_extra={"is_config": False}, description="BGP capabilities negotiated as supported with the peer", default=None, alias="supported-capabilities")
    bgp_neighbor_timers: BgpNeighborTimers | None = Field(json_schema_extra={"is_config": True}, description="Timers related to a BGP neighbor", default=None, alias="bgp-neighbor-timers")
    bgp_neighbor_transport: BgpNeighborTransport | None = Field(json_schema_extra={"is_config": True}, description="Transport session parameters for the BGP neighbor", default=None, alias="bgp-neighbor-transport")

class Bgp(YangBaseModel):
    """Top-level configuration for the BGP router"""

    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.DOWN, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.UP, alias="oper-status")
    alias_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/,\\.]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="User defined alias for this entity. Must be an alphanumeric string with dash or underscore", min_length=0, max_length=256, default=None, alias="alias-name")
    as_: int = Field(json_schema_extra={"is_config": True}, description="Local autonomous system number of the router.  Uses\nthe 32-bit as-number type from the model in RFC 6991.", ge=0, alias="as")
    router_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Router id of the router - an unsigned 32-bit integer\nexpressed in dotted quad notation.", default=None, alias="router-id")
    bgp_neighbor: RestconfList[BgpNeighborItem] | None = Field(json_schema_extra={"is_config": True}, description="List of BGP neighbors configured on the local system,\nuniquely identified by peer IPv[46] address", default=None, alias="bgp-neighbor")

class RoutingProtocolItem(YangBaseModel):
    """Routing protocol instance."""

    rtp_type: RtpTypeEnum = Field(json_schema_extra={"is_config": True}, description="The type of the routing protocol instance.", alias="rtp-type")
    rtp_name: str = Field(json_schema_extra={"is_config": True}, description="The name of the routing protocol instance.\n\nFor system-controlled instances this name is\npersistent, i.e., it SHOULD NOT change across\nreboots.", min_length=1, max_length=128, alias="rtp-name")
    description: str | None = Field(json_schema_extra={"is_config": True}, description="Textual description of the routing protocol instance.", min_length=0, max_length=128, default=None)
    static_route: RestconfList[StaticRouteItem] | None = Field(json_schema_extra={"is_config": True}, description="A list of static routes.\n\nCondition (when): ../rtp-type = 'static'", default=None, alias="static-route")
    ospf: Ospf | None = Field(json_schema_extra={"is_config": True}, description="OSPF protocol.\n\nCondition (when): ../rtp-type = 'ospfv2'", default=None)
    bgp: Bgp | None = Field(json_schema_extra={"is_config": True}, description="Top-level configuration for the BGP router\n\nCondition (when): ../rtp-type = 'ebgp'", default=None)

class AddressFamilyEnum_1(str, Enum):
    """Enumeration for AddressFamilyEnum
    
    Values:
      * ipv4
      * ipv4-unicast
      * ipv6
    """

    IPV4 = "ipv4"
    IPV4_UNICAST = "ipv4-unicast"
    IPV6 = "ipv6"

class SourceProtocolEnum(str, Enum):
    """Enumeration for SourceProtocolEnum
    
    Values:
      * direct: Routing pseudo-protocol that provides routes to directly connected networks.
      * static: Static routing pseudo-protocol.
      * ospfv2: OSPFv2 routing protocol
      * bgp: BGP routing protocol
      * ipcp: Ipcp protocol.
    """

    DIRECT = "direct"
    STATIC = "static"
    OSPFV2 = "ospfv2"
    BGP = "bgp"
    IPCP = "ipcp"

class NextHop(YangBaseModel):
    """Configuration of next-hop."""

    outgoing_interface: str = Field(json_schema_extra={"is_config": False}, description="Reference of the outgoing interface.", alias="outgoing-interface")
    next_hop_address: str | None = Field(json_schema_extra={"is_config": False}, description="IPv4 address of the next-hop.", default=None, alias="next-hop-address")
    source_address: str | None = Field(json_schema_extra={"is_config": False}, description="source address of packet out chosen by kernel if the source address has not been chosen by applcation.", default=None, alias="source-address")

class RouteItem(YangBaseModel):
    """A list of static routes."""

    source_protocol: SourceProtocolEnum = Field(json_schema_extra={"is_config": False}, description="Type of the routing protocol from which the route originated.", alias="source-protocol")
    destination_prefix: str = Field(json_schema_extra={"is_config": False}, description="IP destination prefix.", alias="destination-prefix")
    description: str | None = Field(json_schema_extra={"is_config": False}, description="Textual description of the route.", min_length=0, max_length=128, default=None)
    route_preference: int | None = Field(json_schema_extra={"is_config": False}, description="This route attribute, also known as administrative\ndistance, allows for selecting the preferred route\namong routes with the same destination prefix. A\nsmaller value means a more preferred route.", ge=0, default=None, alias="route-preference")
    route_active: bool | None = Field(json_schema_extra={"is_config": False}, description="Indicates that the route is preferred among all routes in the same RIB that have the same destination prefix.", default=None, alias="route-active")
    next_hop: NextHop | None = Field(json_schema_extra={"is_config": False}, description="Configuration of next-hop.", default=None, alias="next-hop")

class HmoRouteItem(YangBaseModel):
    """A list of routes from static/ospfv2/bgp."""

    source_protocol: SourceProtocolEnum = Field(json_schema_extra={"is_config": False}, description="Type of the routing protocol from which the route originated.", alias="source-protocol")
    destination_prefix: str = Field(json_schema_extra={"is_config": False}, description="IP destination prefix.", alias="destination-prefix")
    next_hop: NextHop | None = Field(json_schema_extra={"is_config": False}, description="Configuration of next-hop.", default=None, alias="next-hop")

class RibItem(YangBaseModel):
    """Each entry represents a RIB identified by the 'name'
    key. All routes in a RIB MUST belong to the same address
    family.

    For each routing instance, an implementation SHOULD
    provide one system-controlled default RIB for each
    supported address family.
    """

    rib_name: str = Field(json_schema_extra={"is_config": False}, description="The name of the RIB.", min_length=1, max_length=128, alias="rib-name")
    address_family: AddressFamilyEnum_1 = Field(json_schema_extra={"is_config": False}, description="Address family.", alias="address-family")
    default_rib: bool | None = Field(json_schema_extra={"is_config": False}, description="This flag has the value of 'true' if and only if the\nRIB is the default RIB for the given address family.\n\nA default RIB always receives direct routes. By\ndefault it also receives routes from all routing\nprotocols.", default=True, alias="default-rib")
    rib_description: str | None = Field(json_schema_extra={"is_config": False}, description="Textual description of the RIB.", min_length=0, max_length=128, default=None, alias="rib-description")
    route: RestconfList[RouteItem] | None = Field(json_schema_extra={"is_config": False}, description="A list of static routes.\n\nCondition (when): (../address-family = 'ipv6') or (../address-family = 'ipv4')", default=None)
    hmo_route: RestconfList[HmoRouteItem] | None = Field(json_schema_extra={"is_config": False}, description="A list of routes from static/ospfv2/bgp.", default=None, alias="hmo-route")

class OriginEnum_1(str, Enum):
    """Enumeration for OriginEnum
    
    Values:
      * other: None of the following.
      * static: Indicates that the mapping has been statically configured - for example, using NETCONF or a Command Line Interface.
      * dynamic: Indicates that the mapping has been dynamically resolved using, e.g., IPv4 ARP or the IPv6 Neighbor Discovery protocol.
    """

    OTHER = "other"
    STATIC = "static"
    DYNAMIC = "dynamic"

class NeighborItem(YangBaseModel):
    """A list of mappings from IP addresses to link-layer addresses."""

    ip: str = Field(json_schema_extra={"is_config": True}, description="The IP address of the neighbor node.")
    link_layer_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The link-layer address of the neighbor node.", default=None, alias="link-layer-address")
    origin: OriginEnum_1 | None = Field(json_schema_extra={"is_config": True}, description="The origin of this neighbor entry.", default=None)
    outgoing_interface: str | None = Field(json_schema_extra={"is_config": True}, description="Interface to the neighbor node.", default=None, alias="outgoing-interface")
    vlan_dev_name: str | None = Field(json_schema_extra={"is_config": True}, description="The VLAN device name.", min_length=0, max_length=20, default=None, alias="vlan-dev-name")

class NeighborsItem(YangBaseModel):
    """List: neighbors"""

    address_family: str = Field(json_schema_extra={"is_config": True}, description="The address-family of the neighbor.", alias="address-family")
    neighbor: RestconfList[NeighborItem] | None = Field(json_schema_extra={"is_config": True}, description="A list of mappings from IP addresses to link-layer addresses.", default=None)

class Routing(YangBaseModel):
    """Container of routing protocols and ribs."""

    routing_protocol: RestconfList[RoutingProtocolItem] | None = Field(json_schema_extra={"is_config": True}, description="Routing protocol instance.", default=None, alias="routing-protocol")
    rib: RestconfList[RibItem] = Field(json_schema_extra={"is_config": False}, description="Each entry represents a RIB identified by the 'name'\nkey. All routes in a RIB MUST belong to the same address\nfamily.\n\nFor each routing instance, an implementation SHOULD\nprovide one system-controlled default RIB for each\nsupported address family.")
    neighbors: RestconfList[NeighborsItem] | None = Field(json_schema_extra={"is_config": True}, default=None)

class PppFcsLengthEnum(str, Enum):
    """Enumeration for PppFcsLengthEnum
    
    Values:
      * 16
      * 32
    """

    _16 = "16"
    _32 = "32"

class PppProfileItem(YangBaseModel):
    """Profile for the point-to-point interface."""

    ppp_pf_name: str = Field(json_schema_extra={"is_config": True}, description="The name of the point-to-point protocol profile.", min_length=1, max_length=63, alias="ppp-pf-name")
    ppp_fcs_length: PppFcsLengthEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies whether the frame check sequence is a 16-bit or 32-bit value.", default=PppFcsLengthEnum._16, alias="ppp-fcs-length")
    ppp_mru: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the maximum number of octets in the Information and Padding fields.", ge=64, le=1500, default=1500, alias="ppp-mru")
    ppp_restart_timer: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the restart timer of the PPP protocol in seconds.", ge=1, le=10, default=3, alias="ppp-restart-timer")
    ppp_max_failure: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the maximum failure value of the PPP protocol profile.", ge=2, le=10, default=5, alias="ppp-max-failure")

class OspfLinkProfileItem(YangBaseModel):
    """Profile for the OSPF protocol link."""

    ospf_linkpf_name: str = Field(json_schema_extra={"is_config": True}, description="The name of the OSPF protocol link profile.", min_length=1, max_length=128, alias="ospf-linkpf-name")
    hello_interval: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the Hello Interval in seconds.", ge=1, le=255, default=10, alias="hello-interval")
    router_dead_interval: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the Router Dead Interval in seconds.", ge=4, le=1024, default=40, alias="router-dead-interval")
    retransmission_interval: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the Retransmission Interval in seconds.", ge=1, le=255, default=5, alias="retransmission-interval")

class Profiles(YangBaseModel):
    """Container of all the profiles used by networking, e.g. ppp-profile, ospf-if-profile."""

    ppp_profile: RestconfList[PppProfileItem] | None = Field(json_schema_extra={"is_config": True}, description="Profile for the point-to-point interface.", default=None, alias="ppp-profile")
    ospf_link_profile: RestconfList[OspfLinkProfileItem] | None = Field(json_schema_extra={"is_config": True}, description="Profile for the OSPF protocol link.", default=None, alias="ospf-link-profile")

class AuthMethodEnum(str, Enum):
    """Enumeration for AuthMethodEnum
    
    Values:
      * pre-shared: Select pre-shared key as the authentication method.
    """

    PRE_SHARED = "pre-shared"

class PreShared(YangBaseModel):
    """Shared secret value for PSK."""

    secret: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] = Field(json_schema_extra={"is_config": True}, description="Pre-shared secret value.")

class PeerAuthentication(YangBaseModel):
    """This container allows the Security
    Controller to configure the
    authentication method (pre-shared key,
    eap, digitial-signature, null) that
    will use a particular peer and the
    credentials, which will depend on the
    selected authentication method.
    """

    auth_method: AuthMethodEnum | None = Field(json_schema_extra={"is_config": True}, description="Type of authentication method.", default=AuthMethodEnum.PRE_SHARED, alias="auth-method")
    pre_shared: PreShared | None = Field(json_schema_extra={"is_config": True}, description="Shared secret value for PSK.\n\nCondition (when): ../auth-method = 'pre-shared'", default=None, alias="pre-shared")

class PadEntryItem(YangBaseModel):
    """Peer Authorization Database (PAD) entry."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_/]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="PAD unique name to identify this\nentry.", min_length=1, max_length=128)
    peer_authentication: PeerAuthentication | None = Field(json_schema_extra={"is_config": True}, description="This container allows the Security\nController to configure the\nauthentication method (pre-shared key,\neap, digitial-signature, null) that\nwill use a particular peer and the\ncredentials, which will depend on the\nselected authentication method.", default=None, alias="peer-authentication")
    # Choice: identity
    # Case: ipv4-address
    ipv4_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Specifies the identity as a\nsingle four (4) octet.", default=None, alias="ipv4-address")
    # Case: ipv6-address
    ipv6_address: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$", v)), AfterValidator(lambda v: check_pattern("^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Specifies the identity as a\nsingle sixteen (16) octet IPv6\naddress. An example is\n2001:DB8:0:0:8:800:200C:417A.", default=None, alias="ipv6-address")

class Pad(YangBaseModel):
    """Configuration of Peer Authorization Database
    (PAD). The PAD contains information about IKE
    peer (local and remote).
    """

    pad_entry: RestconfList[PadEntryItem] | None = Field(json_schema_extra={"is_config": True}, description="Peer Authorization Database (PAD) entry.", default=None, alias="pad-entry")

class IkeVersionEnum(str, Enum):
    """Enumeration for IkeVersionEnum
    
    Values:
      * ikev2: IKEv2 authentication protocol. It is the only defined right now. An enum is used for further extensibility.
    """

    IKEV2 = "ikev2"

class IkeSaLifetime(YangBaseModel):
    """IKE SA lifetime soft. Two lifetime values
    can be configured: either rekey time of the
    IKE SA or reauth time of the IKE SA. When
    the rekey lifetime expires a rekey of the
    IKE SA starts. When reauth lifetime
    expires a IKE SA reauthentication starts.
    """

    rekey_time: int | None = Field(json_schema_extra={"is_config": True}, description="Time in seconds between each IKE SA\nrekey.The value 0 means infinite.", ge=0, default=86400, alias="rekey-time")
    reauth_time: int | None = Field(json_schema_extra={"is_config": True}, description="Time in seconds between each IKE SA\nreauthentication. The value 0 means\ninfinite.", ge=0, default=86400, alias="reauth-time")

class IntegrityAlgorithmTypeEnum(str, Enum):
    """Enumeration for IntegrityAlgorithmTypeEnum
    
    Values:
      * SHA2_256
      * SHA2_384
      * SHA2_512
    """

    SHA2_256 = "SHA2_256"
    SHA2_384 = "SHA2_384"
    SHA2_512 = "SHA2_512"

class EncryptionAlgorithmTypeEnum(str, Enum):
    """Enumeration for EncryptionAlgorithmTypeEnum
    
    Values:
      * AES_CBC_128
      * AES_CBC_192
      * AES_CBC_256
      * AES_CTR_128
      * AES_CTR_192
      * AES_CTR_256
      * AES_GCM_16_128
      * AES_GCM_16_192
      * AES_GCM_16_256
    """

    AES_CBC_128 = "AES_CBC_128"
    AES_CBC_192 = "AES_CBC_192"
    AES_CBC_256 = "AES_CBC_256"
    AES_CTR_128 = "AES_CTR_128"
    AES_CTR_192 = "AES_CTR_192"
    AES_CTR_256 = "AES_CTR_256"
    AES_GCM_16_128 = "AES_GCM_16_128"
    AES_GCM_16_192 = "AES_GCM_16_192"
    AES_GCM_16_256 = "AES_GCM_16_256"

class LocalPortsItem(YangBaseModel):
    """List of local ports. When the inner
    protocol is ICMP this 16 bit value represents
    code and type.
    """

    start: int = Field(json_schema_extra={"is_config": True}, description="Start port number.", ge=0, le=65535)
    end: int = Field(json_schema_extra={"is_config": True}, description="End port number.", ge=0, le=65535)

class RemotePortsItem(YangBaseModel):
    """List of remote ports. When the upper layer
    protocol is ICMP this 16 bit value represents
    code and type.
    """

    start: int = Field(json_schema_extra={"is_config": True}, description="Start port number.", ge=0, le=65535)
    end: int = Field(json_schema_extra={"is_config": True}, description="End port number.", ge=0, le=65535)

class TrafficSelector(YangBaseModel):
    """Packets are selected for
    processing actions based on the IP and inner
    protocol header information, selectors,
    matched against entries in the SPD.
    """

    local_subnet: str = Field(json_schema_extra={"is_config": True}, description="Local IP address subnet.", alias="local-subnet")
    remote_subnet: str = Field(json_schema_extra={"is_config": True}, description="Remote IP address subnet.", alias="remote-subnet")
    inner_protocol: int | str | None = Field(json_schema_extra={"is_config": True}, description="Inner Protocol that is going to be\nprotected with IPsec.", default="any", alias="inner-protocol")
    local_ports: RestconfList[LocalPortsItem] | None = Field(json_schema_extra={"is_config": True}, description="List of local ports. When the inner\nprotocol is ICMP this 16 bit value represents\ncode and type.", default=None, alias="local-ports")
    remote_ports: RestconfList[RemotePortsItem] | None = Field(json_schema_extra={"is_config": True}, description="List of remote ports. When the upper layer\nprotocol is ICMP this 16 bit value represents\ncode and type.", default=None, alias="remote-ports")

class ActionEnum(str, Enum):
    """Enumeration for ActionEnum
    
    Values:
      * protect: PROTECT the traffic with IPsec.
      * bypass: BYPASS the traffic. The packet is forwarded without IPsec protection.
      * discard: DISCARD the traffic. The IP packet is discarded.
    """

    PROTECT = "protect"
    BYPASS = "bypass"
    DISCARD = "discard"

class ModeEnum(str, Enum):
    """Enumeration for ModeEnum
    
    Values:
      * transport: IPsec transport mode.
      * tunnel: IPsec tunnel mode.
    """

    TRANSPORT = "transport"
    TUNNEL = "tunnel"

class ProtocolParametersEnum(str, Enum):
    """Enumeration for ProtocolParametersEnum
    
    Values:
      * esp: IPsec ESP protocol.
    """

    ESP = "esp"

class EspAlgorithms(YangBaseModel):
    """Configuration of Encapsulating
    Security Payload (ESP) parameters and
    algorithms.
    """

    integrity: RestconfList[IntegrityAlgorithmTypeEnum] = Field(json_schema_extra={"is_config": True}, description="Configuration of ESP authentication\nbased on the specified integrity\nalgorithm. With AEAD algorithms,\nthe integrity node is not\nused.")
    encryption: RestconfList[EncryptionAlgorithmTypeEnum] = Field(json_schema_extra={"is_config": True}, description="Configuration of ESP encryption algorithms.")

class IpsecSaCfg(YangBaseModel):
    """IPsec SA configuration included in the SPD
    entry.
    """

    mode: ModeEnum | None = Field(json_schema_extra={"is_config": True}, description="IPsec SA has to be processed in\ntransport or tunnel mode.", default=ModeEnum.TRANSPORT)
    protocol_parameters: ProtocolParametersEnum | None = Field(json_schema_extra={"is_config": True}, description="Security protocol of the IPsec SA:\nOnly ESP is supported but it could be\nextended in the future.", default=ProtocolParametersEnum.ESP, alias="protocol-parameters")
    esp_algorithms: EspAlgorithms | None = Field(json_schema_extra={"is_config": True}, description="Configuration of Encapsulating\nSecurity Payload (ESP) parameters and\nalgorithms.\n\nCondition (when): ../protocol-parameters = 'esp'", default=None, alias="esp-algorithms")

class ProcessingInfo(YangBaseModel):
    """SPD processing. If the required processing
    action is protect, it contains the required
    information to process the packet.
    """

    action: ActionEnum | None = Field(json_schema_extra={"is_config": True}, description="If bypass or discard, container ipsec-sa-cfg is empty.", default=ActionEnum.PROTECT)
    ipsec_sa_cfg: IpsecSaCfg | None = Field(json_schema_extra={"is_config": True}, description="IPsec SA configuration included in the SPD\nentry.\n\nCondition (when): ../action = 'protect'", default=None, alias="ipsec-sa-cfg")

class IpsecPolicyConfig(YangBaseModel):
    """This container carries the
    configuration of a IPsec policy.
    """

    traffic_selector: TrafficSelector | None = Field(json_schema_extra={"is_config": True}, description="Packets are selected for\nprocessing actions based on the IP and inner\nprotocol header information, selectors,\nmatched against entries in the SPD.", default=None, alias="traffic-selector")
    processing_info: ProcessingInfo | None = Field(json_schema_extra={"is_config": True}, description="SPD processing. If the required processing\naction is protect, it contains the required\ninformation to process the packet.", default=None, alias="processing-info")

class SpdEntryItem(YangBaseModel):
    """List of entries which will constitute
    the representation of the SPD. Since we
    have IKE in this case, it is only
    required to send a IPsec policy from
    this NE where 'local' is this NE and
    'remote' the other NE. The IKE
    implementation will install IPsec
    policies in the NE in both
    directions (inbound and outbound) and
    their corresponding IPsec SAs based on
    the information in this SPD entry.
    """

    spd_entry_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_/]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="SPD entry unique name to identify\nthe IPsec policy.", min_length=1, max_length=128, alias="spd-entry-name")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.DOWN, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.DOWN, alias="oper-status")
    ipsec_policy_config: IpsecPolicyConfig | None = Field(json_schema_extra={"is_config": True}, description="This container carries the\nconfiguration of a IPsec policy.", default=None, alias="ipsec-policy-config")

class Spd(YangBaseModel):
    """Configuration of the Security Policy
    Database (SPD). This main information is
    placed in the grouping
    ipsec-policy-grouping.
    """

    spd_entry: RestconfList[SpdEntryItem] | None = Field(json_schema_extra={"is_config": True}, description="List of entries which will constitute\nthe representation of the SPD. Since we\nhave IKE in this case, it is only\nrequired to send a IPsec policy from\nthis NE where 'local' is this NE and\n'remote' the other NE. The IKE\nimplementation will install IPsec\npolicies in the NE in both\ndirections (inbound and outbound) and\ntheir corresponding IPsec SAs based on\nthe information in this SPD entry.", default=None, alias="spd-entry")

class ChildSaLifetime(YangBaseModel):
    """IPsec SA lifetime soft."""

    time: int | None = Field(json_schema_extra={"is_config": True}, description="Time in seconds since the IPsec SA was added.\nFor example, if this value is 180 seconds it\nmeans the IPsec SA expires in 180 seconds since\nit was added. The value 0 implies infinite.", ge=0, default=28800)
    bytes: int | None = Field(json_schema_extra={"is_config": True}, description="If the IPsec SA processes the number of bytes\nexpressed in this leaf, the IPsec SA expires and\nshould be rekeyed. The value 0 implies\ninfinite.", ge=0, default=0)

class ChildSaInfo(YangBaseModel):
    """Specific information for IPsec SAs
    SAs. It includes PFS group and IPsec SAs
    rekey lifetimes.
    """

    pfs_groups: RestconfList[Annotated[int, Field(ge=14), Field(le=21)]] = Field(json_schema_extra={"is_config": True}, description="perfect forward secrecy group numbers.", alias="pfs-groups")
    child_sa_lifetime: ChildSaLifetime | None = Field(json_schema_extra={"is_config": True}, description="IPsec SA lifetime soft.", default=None, alias="child-sa-lifetime")

class IkeState(YangBaseModel):
    """IKE state data for a particular
    connection.
    """

    initiator: bool | None = Field(json_schema_extra={"is_config": False}, description="It is acting as initiator for this\nconnection.", default=None)
    initiator_ikesa_spi: str | None = Field(json_schema_extra={"is_config": False}, description="Initiator's IKE SA SPI.", default=None, alias="initiator-ikesa-spi")
    responder_ikesa_spi: str | None = Field(json_schema_extra={"is_config": False}, description="Responder's IKE SA SPI.", default=None, alias="responder-ikesa-spi")
    established: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Seconds since this IKE SA has been\nestablished.", ge=0, le=18446744073709551615, default=None)
    current_rekey_time: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Seconds before IKE SA must be rekeyed.", ge=0, le=18446744073709551615, default=None, alias="current-rekey-time")
    current_reauth_time: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Seconds before IKE SA must be\nre-authenticated.", ge=0, le=18446744073709551615, default=None, alias="current-reauth-time")

class ConnEntryItem(YangBaseModel):
    """IKE peer connection information. This list
    contains the IKE connection for this peer
    with other peers. This will be translated in
    real time by IKE Security Associations
    established with these nodes.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_/]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="Identifier for this connection\nentry.", min_length=1, max_length=128)
    ike_version: IkeVersionEnum | None = Field(json_schema_extra={"is_config": True}, description="IKE version. Only version 2 is supported\nso far.", default=IkeVersionEnum.IKEV2, alias="ike-version")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.DOWN, alias="admin-status")
    oper_status: OperStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="The operational state specifies whether or not a resource is able to provide service.\nThe operational state shall be visible to the operator. The user cannot modify the operational state. It provides a simple mechanism for the operator to decide whether a resource is operational or not, therefore this parameter has a read-only nature.\nThe operational state is closely coupled with the alarm status of a resource, i.e. state transitions are triggered internally by the NE software. It can have one of the following values:\nDown: The resource is totally inoperable and unable to provide service to the user(s)\nUp: The resource is partially or fully operable and available for use.", default=OperStatusEnum.DOWN, alias="oper-status")
    ike_sa_lifetime: IkeSaLifetime | None = Field(json_schema_extra={"is_config": True}, description="IKE SA lifetime soft. Two lifetime values\ncan be configured: either rekey time of the\nIKE SA or reauth time of the IKE SA. When\nthe rekey lifetime expires a rekey of the\nIKE SA starts. When reauth lifetime\nexpires a IKE SA reauthentication starts.", default=None, alias="ike-sa-lifetime")
    authalg: RestconfList[IntegrityAlgorithmTypeEnum] = Field(json_schema_extra={"is_config": True}, description="Authentication algorithm for establishing the IKE SA.")
    encalg: RestconfList[EncryptionAlgorithmTypeEnum] = Field(json_schema_extra={"is_config": True}, description="Encryption algorithm for the IKE SAs.")
    dh_group: int | None = Field(json_schema_extra={"is_config": True}, description="Group number for Diffie-Hellman Exponentiation used during IKE_SA_INIT for the IKE SA key exchange.", ge=14, le=21, default=14, alias="dh-group")
    local_address: str = Field(json_schema_extra={"is_config": True}, description="local address.", alias="local-address")
    local_pad_entry_ref: str = Field(json_schema_extra={"is_config": True}, description="Local peer authentication information.\nThis node points to a specific entry in\nthe PAD where the authorization\ninformation about this particular local\npeer is stored. It MUST match a\npad-entry-name.", alias="local-pad-entry-ref")
    remote_address: str = Field(json_schema_extra={"is_config": True}, description="remote address.", alias="remote-address")
    remote_pad_entry_ref: str = Field(json_schema_extra={"is_config": True}, description="Remote peer authentication information.\nThis node points to a specific entry in\nthe PAD where the authorization\ninformation about this particular\nremote peer is stored. It MUST match a\npad-entry-name.", alias="remote-pad-entry-ref")
    spd: Spd | None = Field(json_schema_extra={"is_config": True}, description="Configuration of the Security Policy\nDatabase (SPD). This main information is\nplaced in the grouping\nipsec-policy-grouping.", default=None)
    child_sa_info: ChildSaInfo | None = Field(json_schema_extra={"is_config": True}, description="Specific information for IPsec SAs\nSAs. It includes PFS group and IPsec SAs\nrekey lifetimes.", default=None, alias="child-sa-info")
    ike_state: IkeState | None = Field(json_schema_extra={"is_config": False}, description="IKE state data for a particular\nconnection.", default=None, alias="ike-state")

class Ipsec(YangBaseModel):
    """IPsec configuration. It includes PAD parameters,
    IKE and Ipsec connections information and state data.
    """

    pad: Pad | None = Field(json_schema_extra={"is_config": True}, description="Configuration of Peer Authorization Database\n(PAD). The PAD contains information about IKE\npeer (local and remote).", default=None)
    conn_entry: RestconfList[ConnEntryItem] | None = Field(json_schema_extra={"is_config": True}, description="IKE peer connection information. This list\ncontains the IKE connection for this peer\nwith other peers. This will be translated in\nreal time by IKE Security Associations\nestablished with these nodes.", default=None, alias="conn-entry")

class AclTypeEnum(str, Enum):
    """Enumeration for AclTypeEnum
    
    Values:
      * ipv4-acl-type: An ACL that matches on fields from the IPv4 header (e.g., IPv4 destination address) and Layer 4 headers (e.g., TCP destination port).  An ACL of type ipv4 does not contain matches on fields in the Ethernet header or the IPv6 header.
      * ipv6-acl-type: An ACL that matches on fields from the IPv6 header (e.g., IPv6 destination address) and Layer 4 headers (e.g., TCP destination port).  An ACL of type ipv6 does not contain matches on fields in the Ethernet header or the IPv4 header.
    """

    IPV4_ACL_TYPE = "ipv4-acl-type"
    IPV6_ACL_TYPE = "ipv6-acl-type"

class AclIpv4(YangBaseModel):
    """Rule set that matches IPv4 headers."""

    source_ipv4_network: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])/(([0-9])|([1-2][0-9])|(3[0-2])))$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Source IPv4 address prefix.", default=None, alias="source-ipv4-network")
    protocol: int | None = Field(json_schema_extra={"is_config": True}, description="Internet Protocol number.\nRefers to the protocol of the payload.", ge=0, default=None)

class AclIpv6(YangBaseModel):
    """Rule set that matches IPv6 headers."""

    source_ipv6_network: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(/(([0-9])|([0-9]{2})|(1[0-1][0-9])|(12[0-8]))))$", v)), AfterValidator(lambda v: check_pattern("^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(/.+))$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Source IPv6 address prefix.", default=None, alias="source-ipv6-network")
    protocol: int | None = Field(json_schema_extra={"is_config": True}, description="Internet Protocol number.  Refers to the protocol of the\npayload.  In IPv6, this field is known as 'next-header',\nand if extension headers are present, the protocol is\npresent in the 'upper-layer' header.", ge=0, default=None)

class AclTcp(YangBaseModel):
    """Rule set that matches TCP headers."""

    destination_lower_port: int | None = Field(json_schema_extra={"is_config": True}, description="Lower boundary for a port.\n\nValidation Constraints (must):\n- . <= ../destination-upper-port (Error: The destination-lower-port must be less than or equal to\nthe destination-upper-port.)", ge=0, le=65535, default=None, alias="destination-lower-port")
    destination_upper_port: int = Field(json_schema_extra={"is_config": True}, description="Upper boundary for a port.", ge=0, le=65535, alias="destination-upper-port")

class AclUdp(YangBaseModel):
    """Rule set that matches UDP headers."""

    destination_lower_port: int | None = Field(json_schema_extra={"is_config": True}, description="Lower boundary for a port.\n\nValidation Constraints (must):\n- . <= ../destination-upper-port (Error: The destination-lower-port must be less than or equal to\nthe destination-upper-port.)", ge=0, le=65535, default=None, alias="destination-lower-port")
    destination_upper_port: int = Field(json_schema_extra={"is_config": True}, description="Upper boundary for a port.", ge=0, le=65535, alias="destination-upper-port")

class AclSnmpcommunity(YangBaseModel):
    """Rule set that matches SnmpCommunity headers."""

    community: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="String representing a ACL SNMP community string.", min_length=1, max_length=128, default=None)

class Matches(YangBaseModel):
    """The rules in this set determine what fields will be
    matched upon before any action is taken on them.
    The rules are selected based on the feature set
    defined by the server and the acl-type defined.
    If no matches are defined in a particular container,
    then any packet will match that container.  If no
    matches are specified at all in an ACE, then any
    packet will match the ACE.
    """

    acl_ipv4: AclIpv4 | None = Field(json_schema_extra={"is_config": True}, description="Rule set that matches IPv4 headers.\n\nCondition (when): ../../../acl-type = 'ipv4-acl-type'", default=None, alias="acl-ipv4")
    acl_ipv6: AclIpv6 | None = Field(json_schema_extra={"is_config": True}, description="Rule set that matches IPv6 headers.\n\nCondition (when): ../../../acl-type = 'ipv6-acl-type'", default=None, alias="acl-ipv6")
    acl_tcp: AclTcp | None = Field(json_schema_extra={"is_config": True}, description="Rule set that matches TCP headers.", default=None, alias="acl-tcp")
    acl_udp: AclUdp | None = Field(json_schema_extra={"is_config": True}, description="Rule set that matches UDP headers.", default=None, alias="acl-udp")
    acl_snmpcommunity: AclSnmpcommunity | None = Field(json_schema_extra={"is_config": True}, description="Rule set that matches SnmpCommunity headers.", default=None, alias="acl-snmpcommunity")

class ForwardingActionEnum(str, Enum):
    """Enumeration for ForwardingActionEnum
    
    Values:
      * accept: Accept the packet.
      * drop: Drop packet without sending any ICMP error message.
    """

    ACCEPT = "accept"
    DROP = "drop"

class AceItem(YangBaseModel):
    """List of ACEs."""

    sequence_id: int = Field(json_schema_extra={"is_config": True}, description="Sequence number that establishes the relative\norder of the ACE within an ACL", ge=1, alias="sequence-id")
    label: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="A unique name identifying this ACE.", min_length=1, max_length=128, default=None)
    matches: Matches | None = Field(json_schema_extra={"is_config": True}, description="The rules in this set determine what fields will be\nmatched upon before any action is taken on them.\nThe rules are selected based on the feature set\ndefined by the server and the acl-type defined.\nIf no matches are defined in a particular container,\nthen any packet will match that container.  If no\nmatches are specified at all in an ACE, then any\npacket will match the ACE.", default=None)
    forwarding_action: ForwardingActionEnum = Field(json_schema_extra={"is_config": True}, description="Specifies the forwarding action per ace entry.", alias="forwarding-action")

class AclItem(YangBaseModel):
    """An ACL is an ordered list of ACEs.  Each ACE has a
    list of match criteria and a list of actions.
    """

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="The name of the access list.", min_length=1, max_length=128)
    acl_type: AclTypeEnum = Field(json_schema_extra={"is_config": True}, description="Type of ACL.  Indicates the primary intended\ntype of match criteria (e.g., Ethernet, IPv4, IPv6, mixed,\netc.) used in the list instance.", alias="acl-type")
    ace: RestconfList[AceItem] | None = Field(json_schema_extra={"is_config": True}, description="List of ACEs.", default=None)

class ServiceEnum(str, Enum):
    """Enumeration for ServiceEnum
    
    Values:
      * legacy-all: Deprecated: all local services that terminated on the NE, such as cli, netconf, webgui, snmp.
      * ssh: ssh service.
      * cli: cli service.
      * snmp: snmp service.
      * netconf: netconf service.
      * restconf: restconf service.
      * webgui: webgui service.
      * grpc: grpc service.
      * all: All local services that terminated on the NE, such as cli, netconf, webgui, snmp.
    """

    LEGACY_ALL = "legacy-all"
    SSH = "ssh"
    CLI = "cli"
    SNMP = "snmp"
    NETCONF = "netconf"
    RESTCONF = "restconf"
    WEBGUI = "webgui"
    GRPC = "grpc"
    ALL = "all"

class AclSetItem(YangBaseModel):
    """List of ACLs on local service."""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="Reference to the ACL name applied on the local network services.", min_length=1, max_length=128)

class AclLocalServiceItem(YangBaseModel):
    """The ACL attachment point of all the local network services."""

    service: ServiceEnum = Field(json_schema_extra={"is_config": True})
    acl_set: RestconfList[AclSetItem] | None = Field(json_schema_extra={"is_config": True}, description="List of ACLs on local service.", default=None, alias="acl-set")

class AclAttachmentPoints(YangBaseModel):
    """Enclosing container for the list of
    attachment points on which ACLs are set.
    """

    acl_local_service: RestconfList[AclLocalServiceItem] | None = Field(json_schema_extra={"is_config": True}, description="The ACL attachment point of all the local network services.", default=None, alias="acl-local-service")

class DnsServerItem(YangBaseModel):
    """DNS server configuration."""

    address: str = Field(json_schema_extra={"is_config": True}, description="DNS address.")

class Dns(YangBaseModel):
    """Domain Name Server configuration"""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="Whether DNS is enabled.", default=True)
    search: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\s*(([A-Za-z0-9_\\-]*\\.)+[A-Za-z0-9_\\-]*\\s*)*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="A list of DNS-search-suffix names can be provided. The separator is space.\nEach domain name should contain at least a single dot.\nTo clear value, set to empty string.", min_length=0, max_length=128, default=None)
    dns_server: RestconfList[DnsServerItem] | None = Field(json_schema_extra={"is_config": True}, description="DNS server configuration.", default=None, alias="dns-server")

class Networking(YangBaseModel):
    """Container: networking"""

    source_address_select_mode: SourceAddressSelectModeEnum | None = Field(json_schema_extra={"is_config": True}, description="Select the source address for route next-hop entry.", default=SourceAddressSelectModeEnum.LINK_PREFER, alias="source-address-select-mode")
    reserved_subnet: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])/(([0-9])|([1-2][0-9])|(3[0-2])))$", v))] | None = Field(json_schema_extra={"is_config": True}, description="reserved subnet for internal use, prefix-length should be 24.", default="192.168.199.0/24", alias="reserved-subnet")
    interface: RestconfList[InterfaceItem] | None = Field(json_schema_extra={"is_config": True}, description="The list of configured interfaces on the device.", default=None)
    routing: Routing | None = Field(json_schema_extra={"is_config": True}, description="Container of routing protocols and ribs.", default=None)
    profiles: Profiles | None = Field(json_schema_extra={"is_config": True}, description="Container of all the profiles used by networking, e.g. ppp-profile, ospf-if-profile.", default=None)
    ipsec: Ipsec | None = Field(json_schema_extra={"is_config": True}, description="IPsec configuration. It includes PAD parameters,\nIKE and Ipsec connections information and state data.", default=None)
    acl: RestconfList[AclItem] | None = Field(json_schema_extra={"is_config": True}, description="An ACL is an ordered list of ACEs.  Each ACE has a\nlist of match criteria and a list of actions.", default=None)
    acl_attachment_points: AclAttachmentPoints | None = Field(json_schema_extra={"is_config": True}, description="Enclosing container for the list of\nattachment points on which ACLs are set.", default=None, alias="acl-attachment-points")
    dns: Dns | None = Field(json_schema_extra={"is_config": True}, description="Domain Name Server configuration", default=None)

class AaaAuthenticationMethodEnum(str, Enum):
    """Enumeration for AaaAuthenticationMethodEnum
    
    Values:
      * local-only: authentication locally only
      * local-first-then-remote: authentication locally first, if not pass, then use remote AAA server
      * remote-first-then-local: authentication use remote AAA server first, if remote authentication failed or all servers could not be contacted, then authentiate locally
      * remote-unavailable-then-local: authentication use remote AAA server first, if all servers could not be contacted, then authentiate locally
    """

    LOCAL_ONLY = "local-only"
    LOCAL_FIRST_THEN_REMOTE = "local-first-then-remote"
    REMOTE_FIRST_THEN_LOCAL = "remote-first-then-local"
    REMOTE_UNAVAILABLE_THEN_LOCAL = "remote-unavailable-then-local"

class AaaAuthorizationMethodEnum(str, Enum):
    """Enumeration for AaaAuthorizationMethodEnum
    
    Values:
      * local-only: Authorization is local for all users.
      * remote-if-authenticated-then-local: Local users should follow local permissions and remote users should follow the remote ones. If the AAA servers are unavailable, local authorization is done.
      * remote-unavailable-then-local: All users (local or remote) should follow remote permissions. If the AAA servers are unavailable, local authorization is done.
    """

    LOCAL_ONLY = "local-only"
    REMOTE_IF_AUTHENTICATED_THEN_LOCAL = "remote-if-authenticated-then-local"
    REMOTE_UNAVAILABLE_THEN_LOCAL = "remote-unavailable-then-local"

class GrpcDialOutAuthenticationEnum(str, Enum):
    """Enumeration for GrpcDialOutAuthenticationEnum
    
    Values:
      * none
      * tls-uni-auth
      * tls-mutual-auth
    """

    NONE = "none"
    TLS_UNI_AUTH = "tls-uni-auth"
    TLS_MUTUAL_AUTH = "tls-mutual-auth"

class RestconfHttpsAuthenticationEnum(str, Enum):
    """Enumeration for RestconfHttpsAuthenticationEnum
    
    Values:
      * tls-uni-auth
      * tls-mutual-auth
    """

    TLS_UNI_AUTH = "tls-uni-auth"
    TLS_MUTUAL_AUTH = "tls-mutual-auth"

class CspRetrievalEncodingEnum(str, Enum):
    """Enumeration for CspRetrievalEncodingEnum
    
    Values:
      * disabled: Do not use any encoding. CSPs are obfuscated.
      * type7: Display CSPs in type 7 encoding, or in hash when applicable.
    """

    DISABLED = "disabled"
    TYPE7 = "type7"

class PasswordEncryptMethodEnum(str, Enum):
    """Enumeration for PasswordEncryptMethodEnum
    
    Values:
      * none
      * aes
      * md5aes
      * md5
    """

    NONE = "none"
    AES = "aes"
    MD5AES = "md5aes"
    MD5 = "md5"

class AuthorizedKeyItem(YangBaseModel):
    """List: authorized-key"""

    name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\./]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="name of authorized key.", min_length=1, max_length=64)
    public_key: str | None = Field(json_schema_extra={"is_config": True}, description="one of the authorized public keys of the user.", min_length=0, max_length=3000, default=None, alias="public-key")

class UserClassEnum(str, Enum):
    """Enumeration for UserClassEnum
    
    Values:
      * crypto-officer
      * administration
      * configuration
      * operation
      * supervision
    """

    CRYPTO_OFFICER = "crypto-officer"
    ADMINISTRATION = "administration"
    CONFIGURATION = "configuration"
    OPERATION = "operation"
    SUPERVISION = "supervision"

class UserStatusEnum(str, Enum):
    """Enumeration for UserStatusEnum
    
    Values:
      * enabled
      * disabled
      * password-aged
      * lockout
    """

    ENABLED = "enabled"
    DISABLED = "disabled"
    PASSWORD_AGED = "password-aged"
    LOCKOUT = "lockout"

class UserAaaTypeEnum(str, Enum):
    """Enumeration for UserAaaTypeEnum
    
    Values:
      * local: user is authenticated locally.
      * remote: user is authenticated through remote AAA server.
    """

    LOCAL = "local"
    REMOTE = "remote"

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
      * MD5
      * SHA
    """

    MD5 = "MD5"
    SHA = "SHA"

class PrivProtocolEnum(str, Enum):
    """Enumeration for PrivProtocolEnum
    
    Values:
      * DES
      * AES
    """

    DES = "DES"
    AES = "AES"

class Snmpv3(YangBaseModel):
    """SNMPv3 configuration for user"""

    user_sec_level: UserSecLevelEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies the SNMPv3 user security level.", default=UserSecLevelEnum.NO_AUTH_NO_PRIV, alias="user-sec-level")
    auth_protocol: AuthProtocolEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies the authentication protocol that the SNMPv3 user being created will use.\n\nCondition (when): (../user-sec-level = 'auth-priv') or (../user-sec-level = 'auth-no-priv')", default=AuthProtocolEnum.SHA, alias="auth-protocol")
    auth_passphrase: str | None = Field(json_schema_extra={"is_config": True}, description="Specifies the SNMPv3 authentication pass phrase.\n\nCondition (when): (../user-sec-level = 'auth-priv') or (../user-sec-level = 'auth-no-priv')", min_length=8, max_length=64, default=None, alias="auth-passphrase")
    priv_protocol: PrivProtocolEnum | None = Field(json_schema_extra={"is_config": True}, description="Specifies the privacy protocol that the SNMPv3 user being created will use.\n\nCondition (when): ../user-sec-level = 'auth-priv'", default=PrivProtocolEnum.AES, alias="priv-protocol")
    priv_passphrase: str | None = Field(json_schema_extra={"is_config": True}, description="Specifies the SNMPv3 privacy pass phrase.\n\nCondition (when): ../user-sec-level = 'auth-priv'", min_length=8, max_length=64, default=None, alias="priv-passphrase")

class UserItem(YangBaseModel):
    """List: user"""

    user_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] = Field(json_schema_extra={"is_config": True}, description="User name.", min_length=1, max_length=32, alias="user-name")
    password: str | None = Field(json_schema_extra={"is_config": True}, description="The password of the user.", min_length=0, max_length=128, default=None)
    password_hashed: str | None = Field(json_schema_extra={"is_config": True}, description="Hashed password of the user. It is made of three mandatory fields,\nwhere the dollar sign is the field separator. The structure is: $id$salt$encrypted\nOnly id 6 (SHA512) is supported. Salt minimum size is 2.\nreference: https://www.man7.org/linux/man-pages/man3/crypt.3.html", min_length=0, max_length=106, default=None, alias="password-hashed")
    password_encrypt_method: PasswordEncryptMethodEnum | None = Field(json_schema_extra={"is_config": True}, description="The password encrypt method of the user.", default=PasswordEncryptMethodEnum.AES, alias="password-encrypt-method")
    authorized_key: RestconfList[AuthorizedKeyItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="authorized-key")
    user_class: UserClassEnum | None = Field(json_schema_extra={"is_config": True}, description="The access class for the user.", default=UserClassEnum.SUPERVISION, alias="user-class")
    max_invalid_login: int | None = Field(json_schema_extra={"is_config": True}, description="This attribute is the maximum number of consecutive and invalid login attempts\nbefore an account is suspended (lockedout).\n\nCondition (when): ../user-aaa-type = 'local'", ge=0, le=9, default=3, alias="max-invalid-login")
    suspension_time: int | None = Field(json_schema_extra={"is_config": True}, description="This attribute is the duration of UID suspension following consecutive invalid login attempts.\nSetting the value to 0 disables this attribute.\n\nCondition (when): ../user-aaa-type = 'local'", ge=0, le=300, default=60, alias="suspension-time")
    timeout: int | None = Field(json_schema_extra={"is_config": True}, description="This attribute is the Session Time Out Interval. If there are no messages between the user\nand the NE over the Time Out interval, the session is logged off. Setting the value to 0 disables\nthis attribute (meaning the session will not time out).", ge=0, le=300, default=30)
    password_aging_interval: int | None = Field(json_schema_extra={"is_config": True}, description="This attribute is the Password Aging Interval. Setting the value to 0 disables this attribute.\n\nCondition (when): ../user-aaa-type = 'local'", ge=0, le=365, default=0, alias="password-aging-interval")
    password_expiration_date: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="This attribute shows the password expiration date.\n\nCondition (when): ../user-aaa-type = 'local'", default=None, alias="password-expiration-date")
    previous_passwords: RestconfList[str] | None = Field(json_schema_extra={"is_config": False}, description="Hash of previous passwords.", min_length=0, max_length=255, default=None, alias="previous-passwords")
    user_admin_status: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute allows administrators to modify the user administration status.", default=EnableSwitchEnum.ENABLED, alias="user-admin-status")
    user_status: UserStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="This attribute shows the user status.\nUser with status 'enabled' will have access to the system.\nUser with status 'disabled' not have access to the system.\nUser with status 'password-aged' will have access to the system but will be forced to change his password on first-time login.\nUser with status 'lockout' means the account is locked out due to unsuccessful login attempts.", default=UserStatusEnum.DISABLED, alias="user-status")
    max_sessions: int | None = Field(json_schema_extra={"is_config": True}, description="This attribute specifies the maximum number of sessions allowed for this user.", ge=1, le=20, default=6, alias="max-sessions")
    last_login_date: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The last login date/time of the user.", default="1970-01-01T00:00:00Z", alias="last-login-date")
    user_aaa_type: UserAaaTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the authentication method of the user.", default=UserAaaTypeEnum.LOCAL, alias="user-aaa-type")
    snmpv3: Snmpv3 | None = Field(json_schema_extra={"is_config": True}, description="SNMPv3 configuration for user", default=None)

class SessionTypeEnum(str, Enum):
    """Enumeration for SessionTypeEnum
    
    Values:
      * cli
      * snmp
      * netconf
      * restconf
      * webgui
      * gnmi
    """

    CLI = "cli"
    SNMP = "snmp"
    NETCONF = "netconf"
    RESTCONF = "restconf"
    WEBGUI = "webgui"
    GNMI = "gnmi"

class SessionModeEnum(str, Enum):
    """Enumeration for SessionModeEnum
    
    Values:
      * server
      * client
    """

    SERVER = "server"
    CLIENT = "client"

class SessionProtocolEnum(str, Enum):
    """Enumeration for SessionProtocolEnum
    
    Values:
      * telnet
      * telnet-raw
      * serial
      * ssh
      * ssh-raw
      * https
      * http
    """

    TELNET = "telnet"
    TELNET_RAW = "telnet-raw"
    SERIAL = "serial"
    SSH = "ssh"
    SSH_RAW = "ssh-raw"
    HTTPS = "https"
    HTTP = "http"

class CliConfig(YangBaseModel):
    """Container: cli-config"""

    cli_lines: int | None = Field(json_schema_extra={"is_config": True}, description="Number of rows to be used for display. This value is automatically\ndiscovered when possible", ge=10, le=1000, default=40, alias="cli-lines")
    cli_columns: int | None = Field(json_schema_extra={"is_config": True}, description="Number of columns to be used for display. This value is automatically\ndiscovered when possible", ge=80, le=4000, default=140, alias="cli-columns")
    max_history_size: int | None = Field(json_schema_extra={"is_config": True}, description="Command history maximum size for the current session", ge=0, default=500, alias="max-history-size")
    interactive_mode: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="This determines if the CLI shall issue interactive prompt (e.g. for prompting\nadditional information, or for confirmation of user initiated actions).\nEnabled = CLI will prompt user (default)\nDisabled = CLI will suppress any prompt to the user\nThis parameter is set per CLI session and is not persistent.", default=EnableSwitchEnum.ENABLED, alias="interactive-mode")
    commit_mode: GainRangeControlEnum | None = Field(json_schema_extra={"is_config": True}, description="Determines if the configuration changes shall be manually committed or automatically committed.\nThis setting is effective or the current CLI session only.", default=GainRangeControlEnum.AUTO, alias="commit-mode")

class SessionItem(YangBaseModel):
    """List: session"""

    session_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9A-Fa-f.:]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="Specifies a unique identifier of the current session. It indicates the\nIP address and transport layer port number associated with this session.\nIf the session is initiated from the serial port, the value is 'NA'.", min_length=0, max_length=45, alias="session-id")
    session_user: str | None = Field(json_schema_extra={"is_config": False}, description="Points to a user instance.\n\nCondition (when): ../session-mode = 'server'", default=None, alias="session-user")
    session_type: SessionTypeEnum = Field(json_schema_extra={"is_config": False}, description="Session type.", alias="session-type")
    session_mode: SessionModeEnum | None = Field(json_schema_extra={"is_config": False}, description="the device role in session connection", default=SessionModeEnum.SERVER, alias="session-mode")
    session_protocol: SessionProtocolEnum = Field(json_schema_extra={"is_config": False}, description="Indicates which protocol has been used to establish the session.", alias="session-protocol")
    created_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] = Field(json_schema_extra={"is_config": False}, description="The timestamp the user has created this session.", alias="created-time")
    cli_config: CliConfig | None = Field(json_schema_extra={"is_config": True}, description="Condition (when): ../session-type = 'cli'", default=None, alias="cli-config")

class ProtocolSupportedEnum(str, Enum):
    """Enumeration for ProtocolSupportedEnum
    
    Values:
      * TACACSPLUS
      * RADIUS
    """

    TACACSPLUS = "TACACSPLUS"
    RADIUS = "RADIUS"

class AaaServerItem(YangBaseModel):
    """List: aaa-server"""

    server_name: str = Field(json_schema_extra={"is_config": True}, description="specify the name of aaa server.", min_length=1, max_length=32, alias="server-name")
    server_priority: int = Field(json_schema_extra={"is_config": True}, description="This is used to sort the servers in the order of precedence.", ge=1, le=10, alias="server-priority")
    protocol_supported: ProtocolSupportedEnum = Field(json_schema_extra={"is_config": True}, description="specify the protocol used for AAA.", alias="protocol-supported")
    server_ip: str = Field(json_schema_extra={"is_config": True}, description="The IP address of AAA server.", alias="server-ip")
    server_port: int | None = Field(json_schema_extra={"is_config": True}, description="AAA server port number.\n\nCondition (when): ../protocol-supported = 'TACACSPLUS'", ge=0, le=65535, default=49, alias="server-port")
    server_port_authentication: int | None = Field(json_schema_extra={"is_config": True}, description="AAA server authentication port number.\n\nCondition (when): ../protocol-supported = 'RADIUS'", ge=0, le=65535, default=1812, alias="server-port-authentication")
    server_port_accounting: int | None = Field(json_schema_extra={"is_config": True}, description="AAA server accounting port number.\n\nCondition (when): ../protocol-supported = 'RADIUS'", ge=0, le=65535, default=1813, alias="server-port-accounting")
    shared_secret: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The shared secret of the aaa server. The shared secret will be displayed as *.", min_length=0, max_length=100, default="sharedkey", alias="shared-secret")
    role_supported: str | None = Field(json_schema_extra={"is_config": True}, description="specify the role of the server for AAA.", default="authentication authorization accounting", alias="role-supported")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.UP, alias="admin-status")
    time_out: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the response timeout of Access-Request messages sent to a AAA server in seconds.", ge=1, le=60, default=5, alias="time-out")
    retry: int | None = Field(json_schema_extra={"is_config": True}, description="Specifies the number of attempted Access-Request messages to a single AAA server before failing authentication.", ge=0, le=10, default=3)
    source_ip: str | None = Field(json_schema_extra={"is_config": True}, description="Source IP address used for RADIUS communications.\n\nCondition (when): ../protocol-supported = 'RADIUS'", default="auto", alias="source-ip")

class AuthTypeEnum(str, Enum):
    """Enumeration for AuthTypeEnum
    
    Values:
      * tls-certificate
      * proprietary-psk
    """

    TLS_CERTIFICATE = "tls-certificate"
    PROPRIETARY_PSK = "proprietary-psk"

class SessionStatusEnum(str, Enum):
    """Enumeration for SessionStatusEnum
    
    Values:
      * unknown: unknown.
      * disabled: TLS session is setup, successfully connected with remote end.
      * connecting: Remote server is not reachable.
      * incomplete: Authentication failed.
      * connected: Failed to setup the key sync session.
      * unreachable: Configuration is not completed.
      * failed-auth: It is a transient status when the session is in the process connecting remote end.
      * failed: TLS session is management disabled, e.g. admin down.
    """

    UNKNOWN = "unknown"
    DISABLED = "disabled"
    CONNECTING = "connecting"
    INCOMPLETE = "incomplete"
    CONNECTED = "connected"
    UNREACHABLE = "unreachable"
    FAILED_AUTH = "failed-auth"
    FAILED = "failed"

class KeySyncSessionItem(YangBaseModel):
    """TLS session to synchronize ODU encryption key."""

    key_sync_session_id: int = Field(json_schema_extra={"is_config": True}, description="Specifies a unique identifier of the key synchronization session.", ge=1, le=65535, alias="key-sync-session-id")
    admin_status: AdminStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition\nagainst using the resource. The administrative state can be modified by the user, and operates independently of the operability and usage of the resource.", default=AdminStatusEnum.DOWN, alias="admin-status")
    auth_type: AuthTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicating the authentication type of the key sync session.", default=AuthTypeEnum.PROPRIETARY_PSK, alias="auth-type")
    local_certificate: str | None = Field(json_schema_extra={"is_config": True}, description="Previously installed certificate that authenticates the NE.", default="none", alias="local-certificate")
    session_status: SessionStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the status of key sync session.", default=None, alias="session-status")
    remote_ip: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] = Field(json_schema_extra={"is_config": True}, description="The IP address of remote session server.", alias="remote-ip")
    remote_port: int | None = Field(json_schema_extra={"is_config": True}, description="The port number of remote session server.", ge=0, le=65535, default=8443, alias="remote-port")
    local_ip: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The source IP address of a manual session.", default=None, alias="local-ip")
    local_port: int | None = Field(json_schema_extra={"is_config": False}, description="The source port number of a manual session.", ge=0, le=65535, default=None, alias="local-port")
    source_address_from: str | None = Field(json_schema_extra={"is_config": True}, description="specifies the interface of the source IP address of the outgoing packets.\n\nCondition (when): ../key-sync-session-type = 'manual'", default="auto", alias="source-address-from")
    connected_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="The timestamp the user has created this session.", default=None, alias="connected-time")
    key_sync_session_type: CdCompensationModeEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicating the type of key sync session,\n'manual' is for the session user configured, and 'auto' is for the session automatically created by system.", default=CdCompensationModeEnum.MANUAL, alias="key-sync-session-type")

class PskStatusEnum(str, Enum):
    """Enumeration for PskStatusEnum
    
    Values:
      * init
      * sync
      * fail
      * authenticate
    """

    INIT = "init"
    SYNC = "sync"
    FAIL = "fail"
    AUTHENTICATE = "authenticate"

class PskMapItem(YangBaseModel):
    """List: psk-map"""

    psk_identity: str = Field(json_schema_extra={"is_config": True}, description="The PSK identity encoded as a UTF-8 string. For\ndetails how certain common PSK identity formats can\nbe encoded in UTF-8, see section 5.1. of RFC 4279.", min_length=1, max_length=64, alias="psk-identity")
    key: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The key associated with the PSK identity", default=None)
    psk_info: str | None = Field(json_schema_extra={"is_config": True}, description="The label of the psk-map.", min_length=0, max_length=255, default="", alias="psk-info")
    psk_status: PskStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Status of the psk-map. psk-map can be updated only if psk-status is in init or sync status; the previous psk-map updating can be cancelled only if psk-satus is updating; psk-map cannot be updated and previous psk-map updating cannot be cancelled if psk-status is candidate-key-authenticate.", default=PskStatusEnum.INIT, alias="psk-status")
    warning_timer: int | None = Field(json_schema_extra={"is_config": True}, description="Warning Time before psk-map updating completes.", ge=1, le=240, default=5, alias="warning-timer")
    critical_timer: int | None = Field(json_schema_extra={"is_config": True}, description="Critical time before psk-map updating completes.", ge=1, le=480, default=30, alias="critical-timer")
    traffic_off_timer: int | None = Field(json_schema_extra={"is_config": True}, description="Traffic off time before psk-map updating completes.", ge=1, le=1440, default=1440, alias="traffic-off-timer")
    effective_timestamp: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Indicates the Time of new psk starts to take effect.", default=None, alias="effective-timestamp")
    hmo_psk_update: int | None = Field(json_schema_extra={"is_config": True}, description="hmo for psk-update software.", ge=0, default=0, alias="hmo-psk-update")
    ne_restart_cnt: int | None = Field(json_schema_extra={"is_config": True}, description="hmo for ne restart count during psk-update.", ge=0, default=0, alias="ne-restart-cnt")
    candidate_key: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The candidate key associated with the PSK identity", default=None, alias="candidate-key")

class PskMaps(YangBaseModel):
    """During authentication, PSK identity is used to
    look up an entry in the psk-map list. If such
    an entry is found, and the pre-shared keys match,
    then the client is authenticated. If the server
    cannot find an entry in the psk-map list, or if
    the pre-shared keys do not match, then the server
    terminates the connection.
    """

    psk_map: RestconfList[PskMapItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="psk-map")

class AlgorithmIdentifierEnum(str, Enum):
    """Enumeration for AlgorithmIdentifierEnum
    
    Values:
      * rsa1024
      * rsa2048
      * rsa3072
      * rsa4096
      * rsa7680
      * rsa15360
      * secp192r1
      * secp256r1
      * secp384r1
      * secp521r1
    """

    RSA1024 = "rsa1024"
    RSA2048 = "rsa2048"
    RSA3072 = "rsa3072"
    RSA4096 = "rsa4096"
    RSA7680 = "rsa7680"
    RSA15360 = "rsa15360"
    SECP192R1 = "secp192r1"
    SECP256R1 = "secp256r1"
    SECP384R1 = "secp384r1"
    SECP521R1 = "secp521r1"

class VersionEnum(str, Enum):
    """Enumeration for VersionEnum
    
    Values:
      * x509v1
      * x509v2
      * x509v3
    """

    X509V1 = "x509v1"
    X509V2 = "x509v2"
    X509V3 = "x509v3"

class CertificateChainItem(YangBaseModel):
    """certificate chain."""

    certificate_chain_level: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] = Field(json_schema_extra={"is_config": False}, description="certificate chain level.", min_length=1, max_length=128, alias="certificate-chain-level")
    version: VersionEnum | None = Field(json_schema_extra={"is_config": False}, description="version of the certificate.", default=VersionEnum.X509V1)
    serial_number: str | None = Field(json_schema_extra={"is_config": False}, description="serial number of the certificate.", min_length=0, max_length=128, default=None, alias="serial-number")
    signature_algorithm: str | None = Field(json_schema_extra={"is_config": False}, description="signature algorithm of the certificate.", min_length=0, max_length=128, default=None, alias="signature-algorithm")
    issuer: str | None = Field(json_schema_extra={"is_config": False}, description="issuer of the certificate.", min_length=0, max_length=255, default=None)
    valid_from: str | None = Field(json_schema_extra={"is_config": False}, description="valid-from date and time of the certificate.", min_length=0, max_length=128, default=None, alias="valid-from")
    valid_to: str | None = Field(json_schema_extra={"is_config": False}, description="valid-to date and time of the certificate.", min_length=0, max_length=128, default=None, alias="valid-to")
    subject: str | None = Field(json_schema_extra={"is_config": False}, description="subject of the certificate.", min_length=0, max_length=255, default=None)
    public_key_algorithm: str | None = Field(json_schema_extra={"is_config": False}, description="public-key-algorithm of the certificate.", min_length=0, max_length=128, default=None, alias="public-key-algorithm")
    subject_alt_name: str | None = Field(json_schema_extra={"is_config": False}, description="Subject Alternative Names of the certificate.", min_length=0, max_length=2000, default=None, alias="subject-alt-name")

class CertificateItem(YangBaseModel):
    """A certificate for this private key."""

    certificate_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] = Field(json_schema_extra={"is_config": False}, description="An arbitrary name for the certificate.  The name\nmust be a unique across all keys, not just within\nthis key.", min_length=1, max_length=128, alias="certificate-name")
    certificate_content: str | None = Field(json_schema_extra={"is_config": False}, description="certificate.", min_length=0, max_length=50000, default=None, alias="certificate-content")
    version: VersionEnum | None = Field(json_schema_extra={"is_config": False}, description="version of the certificate.", default=VersionEnum.X509V1)
    serial_number: str | None = Field(json_schema_extra={"is_config": False}, description="serial number of the certificate.", min_length=0, max_length=128, default=None, alias="serial-number")
    signature_algorithm: str | None = Field(json_schema_extra={"is_config": False}, description="signature algorithm of the certificate.", min_length=0, max_length=128, default=None, alias="signature-algorithm")
    issuer: str | None = Field(json_schema_extra={"is_config": False}, description="issuer of the certificate.", min_length=0, max_length=255, default=None)
    valid_from: str | None = Field(json_schema_extra={"is_config": False}, description="valid-from date and time of the certificate.", min_length=0, max_length=128, default=None, alias="valid-from")
    valid_to: str | None = Field(json_schema_extra={"is_config": False}, description="valid-to date and time of the certificate.", min_length=0, max_length=128, default=None, alias="valid-to")
    subject: str | None = Field(json_schema_extra={"is_config": False}, description="subject of the certificate.", min_length=0, max_length=255, default=None)
    public_key_algorithm: str | None = Field(json_schema_extra={"is_config": False}, description="public-key-algorithm of the certificate.", min_length=0, max_length=128, default=None, alias="public-key-algorithm")
    subject_alt_name: str | None = Field(json_schema_extra={"is_config": False}, description="Subject Alternative Names of the certificate.", min_length=0, max_length=2000, default=None, alias="subject-alt-name")
    certificate_chain: RestconfList[CertificateChainItem] | None = Field(json_schema_extra={"is_config": False}, description="certificate chain.", default=None, alias="certificate-chain")

class KeyItem(YangBaseModel):
    """A key maintained by the keystore."""

    key_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="An arbitrary name for the key.", min_length=1, max_length=128, alias="key-name")
    key_content: str | None = Field(json_schema_extra={"is_config": False}, description="private key.", min_length=0, max_length=8000, default=None, alias="key-content")
    algorithm_identifier: AlgorithmIdentifierEnum = Field(json_schema_extra={"is_config": True}, description="Identifies which algorithm is to be used with the key.\nThis value determines how the 'private-key' and 'public-key' fields are interpreted.", alias="algorithm-identifier")
    public_key: str | None = Field(json_schema_extra={"is_config": False}, description="A binary string that contains the value of the public key.\nThe interpretation of the content is defined in the registration of the key algorithm.\nFor example, a DSA key is an INTEGER, an RSA key is represented as RSAPublicKey as defined in [RFC3447], and an Elliptic Curve Cryptography (ECC) key is represented using the 'publicKey' described in [RFC5915]", min_length=0, max_length=3000, default=None, alias="public-key")
    certificate: RestconfList[CertificateItem] | None = Field(json_schema_extra={"is_config": False}, description="A certificate for this private key.", default=None)

class TrustedCertificateItem(YangBaseModel):
    """A trusted certificate for a specific use.
    Note, this 'certificate' is a list in order to encode any associated intermediate certificates.
    """

    trusted_certificate_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] = Field(json_schema_extra={"is_config": False}, description="An arbitrary name for this trusted certificate.\nMust be unique across all lists of trusted certificates (not just this list) so that a leafref to it from another module can resolve to unique values.", min_length=1, max_length=128, alias="trusted-certificate-name")
    certificate_content: str | None = Field(json_schema_extra={"is_config": False}, description="certificate.", min_length=0, max_length=25000, default=None, alias="certificate-content")
    version: VersionEnum | None = Field(json_schema_extra={"is_config": False}, description="version of the certificate.", default=VersionEnum.X509V1)
    serial_number: str | None = Field(json_schema_extra={"is_config": False}, description="serial number of the certificate.", min_length=0, max_length=128, default=None, alias="serial-number")
    signature_algorithm: str | None = Field(json_schema_extra={"is_config": False}, description="signature algorithm of the certificate.", min_length=0, max_length=128, default=None, alias="signature-algorithm")
    issuer: str | None = Field(json_schema_extra={"is_config": False}, description="issuer of the certificate.", min_length=0, max_length=255, default=None)
    valid_from: str | None = Field(json_schema_extra={"is_config": False}, description="valid-from date and time of the certificate.", min_length=0, max_length=128, default=None, alias="valid-from")
    valid_to: str | None = Field(json_schema_extra={"is_config": False}, description="valid-to date and time of the certificate.", min_length=0, max_length=128, default=None, alias="valid-to")
    subject: str | None = Field(json_schema_extra={"is_config": False}, description="subject of the certificate.", min_length=0, max_length=255, default=None)
    public_key_algorithm: str | None = Field(json_schema_extra={"is_config": False}, description="public-key-algorithm of the certificate.", min_length=0, max_length=128, default=None, alias="public-key-algorithm")
    subject_alt_name: str | None = Field(json_schema_extra={"is_config": False}, description="Subject Alternative Names of the certificate.", min_length=0, max_length=2000, default=None, alias="subject-alt-name")

class TrustedCertificateGroupItem(YangBaseModel):
    """A list of trusted certificates.
    These certificates can be used by a server to authenticate clients, or by clients to authenticate servers.
    The certificates may be endpoint specific or for certificate authorities, to authenticate many clients at once.
    Each list of certificates SHOULD be specific to a purpose, as the list as a whole may be referenced by other modules.
    For instance, a NETCONF server model might point to a list of certificates to use when authenticating client certificates.
    """

    trusted_certificate_group_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] = Field(json_schema_extra={"is_config": False}, description="An arbitrary name for this list of trusted certificates.", min_length=1, max_length=128, alias="trusted-certificate-group-name")
    trusted_certificate: RestconfList[TrustedCertificateItem] | None = Field(json_schema_extra={"is_config": False}, description="A trusted certificate for a specific use.\nNote, this 'certificate' is a list in order to encode any associated intermediate certificates.", default=None, alias="trusted-certificate")

class Keystore(YangBaseModel):
    """The keystore contains both active material (e.g., private keys and passwords) and passive material (e.g., trust anchors).
    The active material can be used to support either a server (e.g.,a TLS/SSH server's private keys) or a client (a private key used for TLS/SSH client-certificate based authentication, or a password used for SSH/HTTP-client authentication).
    The passive material can be used to support either a server (e.g., client certificates to trust) or clients (e.g., server certificates to trust).
    """

    key: RestconfList[KeyItem] | None = Field(json_schema_extra={"is_config": True}, description="A key maintained by the keystore.", default=None)
    trusted_certificate_group: RestconfList[TrustedCertificateGroupItem] | None = Field(json_schema_extra={"is_config": False}, description="A list of trusted certificates.\nThese certificates can be used by a server to authenticate clients, or by clients to authenticate servers.\nThe certificates may be endpoint specific or for certificate authorities, to authenticate many clients at once.\nEach list of certificates SHOULD be specific to a purpose, as the list as a whole may be referenced by other modules.\nFor instance, a NETCONF server model might point to a list of certificates to use when authenticating client certificates.", default=None, alias="trusted-certificate-group")

class Security(YangBaseModel):
    """Container: security"""

    ssh_public_key: RestconfList[str] | None = Field(json_schema_extra={"is_config": False}, description="The system's public key for use with SSH or SFTP.", min_length=0, max_length=3000, default=None, alias="ssh-public-key")
    ssh_private_key: RestconfList[str] | None = Field(json_schema_extra={"is_config": False}, description="The system's private key for use with SSH or SFTP.", min_length=0, max_length=8000, default=None, alias="ssh-private-key")
    ssh_public_key_fingerprint: RestconfList[str] | None = Field(json_schema_extra={"is_config": False}, description="The fingerprint of the system's public key.", min_length=0, max_length=256, default=None, alias="ssh-public-key-fingerprint")
    ssh_sha1_support: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Defines if ssh-sha1 is enabled for SSH. This applies to sha-1 hash and HMAC.", default=EnableSwitchEnum.ENABLED, alias="ssh-sha1-support")
    pre_login_message: str | None = Field(json_schema_extra={"is_config": True}, description="Welcome message displayed before user login", min_length=0, max_length=1440, default="****************************************** Warning ******************************************\n\nThis system is restricted to authorized users for business purposes. Unauthorized access is a\nviolation of the law. This service may be monitored for administrative and security reasons.\nBy proceeding, you consent to this monitoring.\n\n*********************************************************************************************\n", alias="pre-login-message")
    warning_message: str | None = Field(json_schema_extra={"is_config": True}, description="Welcome message displayed after user login", min_length=0, max_length=1440, default="****************************************** Warning ******************************************\n\nThis system is restricted to authorized users for business purposes. Unauthorized access is a\nviolation of the law. This service may be monitored for administrative and security reasons.\nBy proceeding, you consent to this monitoring.\n\n*********************************************************************************************\n", alias="warning-message")
    aaa_authentication_method: AaaAuthenticationMethodEnum | None = Field(json_schema_extra={"is_config": True}, description="specify authentication method for the user login to the NE.", default=AaaAuthenticationMethodEnum.LOCAL_ONLY, alias="aaa-authentication-method")
    aaa_authorization_method: AaaAuthorizationMethodEnum | None = Field(json_schema_extra={"is_config": True}, description="Specify per-command authorization policy for new sessions. If the user changes this parameter, it should\nlogout and login again to apply the rules. Note that per-command remote authorization is only supported\nin TACACS+ servers. So if there is a mix of RADIUS and TACACS+ servers configured, only the TACACS+ servers\nare queried for per-command authorization, regardless of which server authenticated the user.\nCurrently only CLI supports remote authorization.\nNote that when remote authorization is done, the pre-conditions related to authorization, i.e. related to\nuser class permissions, are skipped.", default=AaaAuthorizationMethodEnum.LOCAL_ONLY, alias="aaa-authorization-method")
    remote_accounting: bool | None = Field(json_schema_extra={"is_config": True}, description="This hidden flag is true if and only if there is a TACACS+ server with accounting role that is enabled.\nWhenever the flag is true, commands are logged in the AAA servers.\nThe flag is used just to optimize performance - MF sends the request to SMF to do accounting only when an\naccounting server is configured.", default=False, alias="remote-accounting")
    httpscert: str | None = Field(json_schema_extra={"is_config": False}, description="system internal data.", min_length=0, max_length=10000, default=None)
    httpscert_private_key: str | None = Field(json_schema_extra={"is_config": False}, description="system internal data.", min_length=0, max_length=8000, default=None, alias="httpscert-private-key")
    system_fips: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="specifies whether the system security is operating in compliance with FIPS.", default=EnableSwitchEnum.DISABLED, alias="system-fips")
    http_support: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Defines whether unsecure HTTP protocol is allowed; includes file transfer, or any other application that uses HTTP", default=EnableSwitchEnum.DISABLED, alias="http-support")
    strict_password_check: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Defines whether system password follow strict checking", default=EnableSwitchEnum.ENABLED, alias="strict-password-check")
    grpc_local_certificate: str | None = Field(json_schema_extra={"is_config": True}, description="Certificate for gRPC dial-in server and dial-out client.", default="none", alias="grpc-local-certificate")
    grpc_dial_out_trusted_certgrp: str | None = Field(json_schema_extra={"is_config": True}, description="trusted certificate group for gRPC dial-out client.", default="none", alias="grpc-dial-out-trusted-certgrp")
    grpc_dial_in_trusted_certgrp: str | None = Field(json_schema_extra={"is_config": True}, description="trusted certificate group for gRPC dial-in server.", default="none", alias="grpc-dial-in-trusted-certgrp")
    grpc_dial_out_authentication: GrpcDialOutAuthenticationEnum | None = Field(json_schema_extra={"is_config": True}, default=GrpcDialOutAuthenticationEnum.NONE, alias="grpc-dial-out-authentication")
    grpc_dial_in_authentication: GrpcDialOutAuthenticationEnum | None = Field(json_schema_extra={"is_config": True}, default=GrpcDialOutAuthenticationEnum.NONE, alias="grpc-dial-in-authentication")
    https_local_certificate: str | None = Field(json_schema_extra={"is_config": True}, description="Certificate for both WebGUI https server and RESTCONF https server.", default="none", alias="https-local-certificate")
    restconf_https_trusted_certgrp: str | None = Field(json_schema_extra={"is_config": True}, description="Certificate group for RESTCONF https server.", default="none", alias="restconf-https-trusted-certgrp")
    restconf_https_authentication: RestconfHttpsAuthenticationEnum | None = Field(json_schema_extra={"is_config": True}, description="Update TLS auth for RESTCONF\n\nCondition (when): /ne/system/restconf/rest-https-support = 'enabled'", default=RestconfHttpsAuthenticationEnum.TLS_UNI_AUTH, alias="restconf-https-authentication")
    csp_symmetrical_key: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Critical Security Parameters symmetrical key.", min_length=1, max_length=32, default=None, alias="csp-symmetrical-key")
    csp_retrieval_encoding: CspRetrievalEncodingEnum | None = Field(json_schema_extra={"is_config": True}, description="Support to retrieve CSPs in the given encoding.", default=CspRetrievalEncodingEnum.DISABLED, alias="csp-retrieval-encoding")
    user: RestconfList[UserItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    session: RestconfList[SessionItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    aaa_server: RestconfList[AaaServerItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="aaa-server")
    key_sync_session: RestconfList[KeySyncSessionItem] | None = Field(json_schema_extra={"is_config": True}, description="TLS session to synchronize ODU encryption key.", default=None, alias="key-sync-session")
    psk_maps: PskMaps | None = Field(json_schema_extra={"is_config": True}, description="During authentication, PSK identity is used to\nlook up an entry in the psk-map list. If such\nan entry is found, and the pre-shared keys match,\nthen the client is authenticated. If the server\ncannot find an entry in the psk-map list, or if\nthe pre-shared keys do not match, then the server\nterminates the connection.", default=None, alias="psk-maps")
    keystore: Keystore | None = Field(json_schema_extra={"is_config": True}, description="The keystore contains both active material (e.g., private keys and passwords) and passive material (e.g., trust anchors).\nThe active material can be used to support either a server (e.g.,a TLS/SSH server's private keys) or a client (a private key used for TLS/SSH client-certificate based authentication, or a password used for SSH/HTTP-client authentication).\nThe passive material can be used to support either a server (e.g., client certificates to trust) or clients (e.g., server certificates to trust).", default=None)

class SwloadStateEnum(str, Enum):
    """Enumeration for SwloadStateEnum
    
    Values:
      * Active
      * Inactive
    """

    ACTIVE = "Active"
    INACTIVE = "Inactive"

class DatabaseItem(YangBaseModel):
    """The list of the databases in the system."""

    database_id: int = Field(json_schema_extra={"is_config": False}, description="database identifier which is uniquely identify specific database.", ge=1, le=10, alias="database-id")
    database_state: SwloadStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the state of the database.", default=None, alias="database-state")
    database_version: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the database version.", min_length=0, max_length=20, default=None, alias="database-version")
    database_vendor: str | None = Field(json_schema_extra={"is_config": False}, description="Vendor information of the database.", min_length=0, max_length=32, default=None, alias="database-vendor")
    database_product: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the network element family this database belongs to.", min_length=0, max_length=32, default=None, alias="database-product")
    backup_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))?)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Indicates the database last backup time.", default="", alias="backup-time")

class FwVersionMapItem(YangBaseModel):
    """The firmware information of the upgradable devices included in the software load."""

    device_name: str = Field(json_schema_extra={"is_config": False}, description="Indicates the name of the device.", min_length=0, max_length=64, alias="device-name")
    device_fw_version: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the version of the firmware.", min_length=0, max_length=64, default=None, alias="device-fw-version")

class SoftwareloadItem(YangBaseModel):
    """The list of the software loads in the system."""

    swload_id: int = Field(json_schema_extra={"is_config": False}, description="software load identifier which is uniquely identify specific software load.", ge=1, le=10, alias="swload-id")
    swload_state: SwloadStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the state of the software load.", default=None, alias="swload-state")
    swload_version: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the software version of the software load.", min_length=0, max_length=20, default=None, alias="swload-version")
    swload_vendor: str | None = Field(json_schema_extra={"is_config": False}, description="Vendor information of the software load.", min_length=0, max_length=32, default=None, alias="swload-vendor")
    swload_product: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the network element family this software belongs to.", min_length=0, max_length=32, default=None, alias="swload-product")
    swload_label: str | None = Field(json_schema_extra={"is_config": False}, description="The label of the software load including summary information.", min_length=0, max_length=1024, default=None, alias="swload-label")
    database: RestconfList[DatabaseItem] | None = Field(json_schema_extra={"is_config": False}, description="The list of the databases in the system.", default=None)
    fw_version_map: RestconfList[FwVersionMapItem] | None = Field(json_schema_extra={"is_config": False}, description="The firmware information of the upgradable devices included in the software load.", default=None, alias="fw-version-map")

class FwStateEnum(str, Enum):
    """Enumeration for FwStateEnum
    
    Values:
      * not-available
      * current
      * not-current
    """

    NOT_AVAILABLE = "not-available"
    CURRENT = "current"
    NOT_CURRENT = "not-current"

class CurrentFwVersionItem(YangBaseModel):
    """The firmware information of the upgradable devices included in the software load."""

    equipment_entity: str = Field(json_schema_extra={"is_config": False}, description="Indicates the entity of the equipment carrying the device.", alias="equipment-entity")
    fw_equipment_type: EquipmentTypeEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates the type of the equipment carrying the device.", default=None, alias="fw-equipment-type")
    device_name: str = Field(json_schema_extra={"is_config": False}, description="Indicates the name of the device.", min_length=0, max_length=64, alias="device-name")
    device_fw_version: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the version of the firmware.", min_length=0, max_length=64, default=None, alias="device-fw-version")
    fw_state: FwStateEnum | None = Field(json_schema_extra={"is_config": False}, description="Indicates firmware state of the device.\nCurrent: indicates the loaded firmware is the version of current software load.\nNot-current: indicates the loaded firmware is not the version of current software load.", default=FwStateEnum.NOT_AVAILABLE, alias="fw-state")
    system_fw_version: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the version of the firmware in system appication.", min_length=0, max_length=64, default=None, alias="system-fw-version")

class ThirdPartyFwItem(YangBaseModel):
    """List of 3rd party fw files available to be used to upgrade 3rd party equipment."""

    fw_name: str = Field(json_schema_extra={"is_config": False}, description="Name of the firmware.", min_length=0, max_length=255, alias="fw-name")

class TypeEnum(str, Enum):
    """Enumeration for TypeEnum
    
    Values:
      * normal: Normal rollback-point; is automatically deleted upon activation
      * backup: Backup rollback-point; is kept even after activation
    """

    NORMAL = "normal"
    BACKUP = "backup"

class RollbackPointItem(YangBaseModel):
    """Represents a rollback point stored in the system.
    A rollback point represents the system configuration of a specific point in time, that the user may create with the
    'create-rollback-point' command, visualize with the 'diff' command' and rollback to with the 'rollback' command.
    The system is able to store up to 10 rollback-points, rolling over old instances as new ones are created.
    The incremental IDs of 1..10 are automatically generated by the system whenever the rollback-point is created.
    Rollback points can be deleted as any normal object.
    A special 'backup' rollback-point can also be created with ID 0; unlike normal rollback-points, this instance will
    be kept even after activation with the 'rollback' RPC.
    """

    rollback_point_id: int = Field(json_schema_extra={"is_config": True}, description="Integer ID of the rollback-point. Generated dynamically whenever a rollback-point is created, with range 1 to 100", ge=0, le=10, alias="rollback-point-id")
    creation_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Timestamp when this rollback-point was created", default=None, alias="creation-time")
    creation_trigger: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Describes the author user-name of this rollback-point", min_length=1, max_length=32, default=None, alias="creation-trigger")
    type: TypeEnum | None = Field(json_schema_extra={"is_config": False}, description="The type of the rollback-point", default=TypeEnum.NORMAL)
    description: str | None = Field(json_schema_extra={"is_config": True}, description="User defined description of this rollback-point", min_length=0, max_length=200, default=None)

class SwManagement(YangBaseModel):
    """The container includes management objects of software, for example, software load, database."""

    softwareload: RestconfList[SoftwareloadItem] | None = Field(json_schema_extra={"is_config": False}, description="The list of the software loads in the system.", default=None)
    current_fw_version: RestconfList[CurrentFwVersionItem] | None = Field(json_schema_extra={"is_config": False}, description="The firmware information of the upgradable devices included in the software load.", default=None, alias="current-fw-version")
    third_party_fw: RestconfList[ThirdPartyFwItem] | None = Field(json_schema_extra={"is_config": False}, description="List of 3rd party fw files available to be used to upgrade 3rd party equipment.", default=None, alias="third-party-fw")
    rollback_point: RestconfList[RollbackPointItem] | None = Field(json_schema_extra={"is_config": True}, description="Represents a rollback point stored in the system.\nA rollback point represents the system configuration of a specific point in time, that the user may create with the\n'create-rollback-point' command, visualize with the 'diff' command' and rollback to with the 'rollback' command.\nThe system is able to store up to 10 rollback-points, rolling over old instances as new ones are created.\nThe incremental IDs of 1..10 are automatically generated by the system whenever the rollback-point is created.\nRollback points can be deleted as any normal object.\nA special 'backup' rollback-point can also be created with ID 0; unlike normal rollback-points, this instance will\nbe kept even after activation with the 'rollback' RPC.", default=None, alias="rollback-point")

class LogServerTransportEnum(str, Enum):
    """Enumeration for LogServerTransportEnum
    
    Values:
      * tcp
      * udp
    """

    TCP = "tcp"
    UDP = "udp"

class LogSelectorFacilityEnum(str, Enum):
    """Enumeration for LogSelectorFacilityEnum
    
    Values:
      * security
      * alarm
      * event
      * configuration
      * crypto-configuration
      * crypto-security
      * crypto-event
      * crypto-alarm
    """

    SECURITY = "security"
    ALARM = "alarm"
    EVENT = "event"
    CONFIGURATION = "configuration"
    CRYPTO_CONFIGURATION = "crypto-configuration"
    CRYPTO_SECURITY = "crypto-security"
    CRYPTO_EVENT = "crypto-event"
    CRYPTO_ALARM = "crypto-alarm"

class LogSelectorSeverityEnum(str, Enum):
    """Enumeration for LogSelectorSeverityEnum
    
    Values:
      * emergency
      * alert
      * critical
      * error
      * warning
      * notice
      * informational
      * debug
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

class LogFacilityItem(YangBaseModel):
    """List: log-facility"""

    log_selector_facility: LogSelectorFacilityEnum = Field(json_schema_extra={"is_config": True}, description="The leaf uniquely identifies a syslog facility for forwarding.", alias="log-selector-facility")
    log_selector_severity: LogSelectorSeverityEnum | None = Field(json_schema_extra={"is_config": True}, description="The system log selected severity level for forwarding", default=LogSelectorSeverityEnum.DEBUG, alias="log-selector-severity")
    compare_op: CompareOpEnum | None = Field(json_schema_extra={"is_config": True}, description="This leaf describes the option to specify how the severity comparison is performed.", default=CompareOpEnum.EQUALS_OR_HIGHER, alias="compare-op")
    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="The current operational state of the facility.", default=True)

class LogForwardingSelector(YangBaseModel):
    """This container describes the log selector parameters for syslog."""

    log_facility: RestconfList[LogFacilityItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="log-facility")

class LogServerItem(YangBaseModel):
    """Grouping the configuration parameters for log forwarding."""

    log_server_name: str = Field(json_schema_extra={"is_config": True}, description="The name for the endpoint to forwarding logs to.", min_length=1, max_length=64, alias="log-server-name")
    log_server_ip_address: str = Field(json_schema_extra={"is_config": True}, description="The leaf uniquely specifies the ipv4 address of the remote host.", alias="log-server-ip-address")
    log_server_transport: LogServerTransportEnum | None = Field(json_schema_extra={"is_config": True}, description="It is the transport protocol used when forwarding logs.", default=LogServerTransportEnum.UDP, alias="log-server-transport")
    log_server_port: int | None = Field(json_schema_extra={"is_config": True}, description="This leaf specifies the port number used to deliver messages to the remote server.", ge=0, le=65535, default=514, alias="log-server-port")
    log_forwarding_selector: LogForwardingSelector | None = Field(json_schema_extra={"is_config": True}, description="This container describes the log selector parameters for syslog.", default=None, alias="log-forwarding-selector")
    destination_facility_type: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Switching of the function destination-facility", default=EnableSwitchEnum.DISABLED, alias="destination-facility-type")
    destination_facility: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9]|1[0-9]|2[0-3])?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="This leaf specifies the facility used in messages delivered to the remote server.", default="23", alias="destination-facility")

class SensorPathItem(YangBaseModel):
    """List of paths in the model which together
    comprise a sensor grouping. Filters for each path
    to exclude items are also provided.
    """

    index: str = Field(json_schema_extra={"is_config": True}, description="index for sensor-path", min_length=1, max_length=320)
    model_path: str = Field(json_schema_extra={"is_config": True}, description="Path to a section of operational state of interest\n(the sensor).", alias="model-path")
    exclude_filter: str | None = Field(json_schema_extra={"is_config": True}, description="Filter to exclude certain values out of the state\nvalues", default=None, alias="exclude-filter")

class SensorPaths(YangBaseModel):
    """Top level container to hold a set of sensor
    paths grouped together
    """

    sensor_path: RestconfList[SensorPathItem] | None = Field(json_schema_extra={"is_config": True}, description="List of paths in the model which together\ncomprise a sensor grouping. Filters for each path\nto exclude items are also provided.", default=None, alias="sensor-path")

class SensorGroupItem(YangBaseModel):
    """List of telemetry sensory groups on the local
    system, where a sensor grouping represents a resuable
    grouping of multiple paths and exclude filters.
    """

    sensor_group_id: str = Field(json_schema_extra={"is_config": True}, description="Name or identifier for the sensor group itself.\nWill be referenced by other configuration specifying a\nsensor group", min_length=1, max_length=128, alias="sensor-group-id")
    sensor_paths: SensorPaths | None = Field(json_schema_extra={"is_config": True}, description="Top level container to hold a set of sensor\npaths grouped together", default=None, alias="sensor-paths")

class SensorGroups(YangBaseModel):
    """Top level container for sensor-groups."""

    sensor_group: RestconfList[SensorGroupItem] | None = Field(json_schema_extra={"is_config": True}, description="List of telemetry sensory groups on the local\nsystem, where a sensor grouping represents a resuable\ngrouping of multiple paths and exclude filters.", default=None, alias="sensor-group")

class DestinationItem(YangBaseModel):
    """List of telemetry stream destinations"""

    destination_address: str = Field(json_schema_extra={"is_config": True}, description="IP address of the telemetry stream destination", alias="destination-address")
    destination_port: int = Field(json_schema_extra={"is_config": True}, description="Protocol (udp or tcp) port number for the telemetry\nstream destination", ge=0, le=65535, alias="destination-port")

class Destinations(YangBaseModel):
    """The destination container lists the destination
    information such as IP address and port of the
    telemetry messages from the network element.
    """

    destination: RestconfList[DestinationItem] | None = Field(json_schema_extra={"is_config": True}, description="List of telemetry stream destinations", default=None)

class DestinationGroupItem(YangBaseModel):
    """List of destination-groups. Destination groups allow the
    reuse of common telemetry destinations across the
    telemetry configuration. An operator references a
    set of destinations via the configurable
    destination-group-identifier.
    A destination group may contain one or more telemetry
    destinations
    """

    group_id: str = Field(json_schema_extra={"is_config": True}, description="Unique identifier for the destination group", min_length=1, max_length=128, alias="group-id")
    destinations: Destinations | None = Field(json_schema_extra={"is_config": True}, description="The destination container lists the destination\ninformation such as IP address and port of the\ntelemetry messages from the network element.", default=None)

class DestinationGroups(YangBaseModel):
    """Top level container for destination group configuration
    and state.
    """

    destination_group: RestconfList[DestinationGroupItem] | None = Field(json_schema_extra={"is_config": True}, description="List of destination-groups. Destination groups allow the\nreuse of common telemetry destinations across the\ntelemetry configuration. An operator references a\nset of destinations via the configurable\ndestination-group-identifier.\nA destination group may contain one or more telemetry\ndestinations", default=None, alias="destination-group")

class StreamingDataModelEnum(str, Enum):
    """Enumeration for StreamingDataModelEnum
    
    Values:
      * Auto: The stream data base on sensor path model
      * Device-model: The stream data base on device model
      * Openconfig: The stream data base on openconfig model
      * OpenROADM: The stream data base on openroadm model
    """

    AUTO = "Auto"
    DEVICE_MODEL = "Device-model"
    OPENCONFIG = "Openconfig"
    OPENROADM = "OpenROADM"

class ProtocolEnum(str, Enum):
    """Enumeration for ProtocolEnum
    
    Values:
      * SSH
      * GRPC
      * JSON_RPC
      * WEBSOCKET_RPC
    """

    SSH = "SSH"
    GRPC = "GRPC"
    JSON_RPC = "JSON_RPC"
    WEBSOCKET_RPC = "WEBSOCKET_RPC"

class EncodingEnum(str, Enum):
    """Enumeration for EncodingEnum
    
    Values:
      * XML
      * JSON_IETF
      * PROTO3
    """

    XML = "XML"
    JSON_IETF = "JSON_IETF"
    PROTO3 = "PROTO3"

class SensorProfileItem(YangBaseModel):
    """List of telemetry sensor groups used
    in the subscription
    """

    sensor_group: str = Field(json_schema_extra={"is_config": True}, description="Reference to the sensor group which is used in the profile", alias="sensor-group")
    sample_interval: Uint64 | None = Field(json_schema_extra={"is_config": True}, description="Time in milliseconds between the device's sample of a\ntelemetry data source. For example, setting this to 2000\nwould require the local device to collect the telemetry\ndata every 2000 milliseconds. There can be latency or jitter\nin transmitting the data, but the sample must occur at\nthe specified interval.\nThe timestamp must reflect the actual time when the data\nwas sampled, not simply the previous sample timestamp +\nsample-interval.\nIf sample-interval is set to 0, the telemetry sensor\nbecomes event based. The sensor must then emit data upon\nevery change of the underlying data source.", le=3600000, ge=0, default=10000, alias="sample-interval")
    heartbeat_interval: Uint64 | None = Field(json_schema_extra={"is_config": True}, description="Maximum time interval in milliseconds that may pass\nbetween updates from a device to a telemetry collector.\nIf this interval expires, but there is no updated data to\nsend (such as if suppress_updates has been configured), the\ndevice must send a telemetry message to the collector.", le=7200000, ge=0, default=20000, alias="heartbeat-interval")
    suppress_redundant: bool | None = Field(json_schema_extra={"is_config": True}, description="Boolean flag to control suppression of redundant\ntelemetry updates to the collector platform. If this flag is\nset to TRUE, then the collector will only send an update at\nthe configured interval if a subscribed data value has\nchanged. Otherwise, the device will not send an update to\nthe collector until expiration of the heartbeat interval.", default=True, alias="suppress-redundant")

class SensorProfiles(YangBaseModel):
    """A sensor profile is a set of sensor groups or
    individual sensor paths which are associated with a
    telemetry subscription. This is the source of the
    telemetry data for the subscription to send to the
    defined collectors.
    """

    sensor_profile: RestconfList[SensorProfileItem] | None = Field(json_schema_extra={"is_config": True}, description="List of telemetry sensor groups used\nin the subscription", default=None, alias="sensor-profile")

class DestinationProfileItem(YangBaseModel):
    """Identifier of the previously defined destination
    group
    """

    group_id: str = Field(json_schema_extra={"is_config": True}, description="The destination group id references a reusable\ngroup of destination addresses and ports for\nthe telemetry stream.", alias="group-id")

class DestinationProfiles(YangBaseModel):
    """A subscription may specify destination addresses.
    If the subscription supplies destination addresses,
    the network element will be the initiator of the
    telemetry streaming, sending it to the destination(s)
    specified.
    If the destination set is omitted, the subscription
    preconfigures certain elements such as paths and
    sample intervals under a specified subscription ID.
    In this case, the network element will NOT initiate an
    outbound connection for telemetry, but will wait for
    an inbound connection from a network management
    system.
    It is expected that the network management system
    connecting to the network element will reference
    the preconfigured subscription ID when initiating
    a subscription.
    """

    destination_profile: RestconfList[DestinationProfileItem] | None = Field(json_schema_extra={"is_config": True}, description="Identifier of the previously defined destination\ngroup", default=None, alias="destination-profile")

class DialOutSubscriptionItem(YangBaseModel):
    """List of telemetry subscriptions. A telemetry
    subscription consists of a set of collection
    destinations, stream attributes, and associated paths to
    state information in the model (sensor data)
    """

    start_streaming_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The time of the subscription first streaming data packet send out.\nIf the time is default value the packet will send immediately after subscription setting completed.\nIf the time is passed the packet will send out at the next integral multiple of sample interval since the start-streaming-time.\nIf the time is not yet the first packet will be sent out at the start-streaming-time", default="0000-01-01T00:00:00.000Z", alias="start-streaming-time")
    streaming_data_model: StreamingDataModelEnum | None = Field(json_schema_extra={"is_config": True}, description="The stream out data based on selected model", default=StreamingDataModelEnum.DEVICE_MODEL, alias="streaming-data-model")
    subscription_name: str = Field(json_schema_extra={"is_config": True}, description="User configured identifier of the telemetry\nsubscription. This value is used primarily for\nsubscriptions configured locally on the network\nelement.", min_length=1, max_length=128, alias="subscription-name")
    subscription_id: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="System generated identifer of the telemetry\nsubscription.", ge=0, le=18446744073709551615, default=None, alias="subscription-id")
    local_source_address: str | None = Field(json_schema_extra={"is_config": True}, description="The IP address which will be the source of packets from\nthe device to a telemetry collector destination.", default="auto", alias="local-source-address")
    originated_qos_marking: int | None = Field(json_schema_extra={"is_config": True}, description="DSCP marking of packets generated by the telemetry\nsubsystem on the network device.", ge=0, le=63, default=0, alias="originated-qos-marking")
    protocol: ProtocolEnum | None = Field(json_schema_extra={"is_config": True}, description="Selection of the transport protocol for the telemetry\nstream.", default=ProtocolEnum.GRPC)
    encoding: EncodingEnum | None = Field(json_schema_extra={"is_config": True}, description="Selection of the specific encoding or RPC framework\nfor telemetry messages to and from the network element.", default=EncodingEnum.JSON_IETF)
    sensor_profiles: SensorProfiles | None = Field(json_schema_extra={"is_config": True}, description="A sensor profile is a set of sensor groups or\nindividual sensor paths which are associated with a\ntelemetry subscription. This is the source of the\ntelemetry data for the subscription to send to the\ndefined collectors.", default=None, alias="sensor-profiles")
    destination_profiles: DestinationProfiles | None = Field(json_schema_extra={"is_config": True}, description="A subscription may specify destination addresses.\nIf the subscription supplies destination addresses,\nthe network element will be the initiator of the\ntelemetry streaming, sending it to the destination(s)\nspecified.\nIf the destination set is omitted, the subscription\npreconfigures certain elements such as paths and\nsample intervals under a specified subscription ID.\nIn this case, the network element will NOT initiate an\noutbound connection for telemetry, but will wait for\nan inbound connection from a network management\nsystem.\nIt is expected that the network management system\nconnecting to the network element will reference\nthe preconfigured subscription ID when initiating\na subscription.", default=None, alias="destination-profiles")

class Persistent(YangBaseModel):
    """This container holds information relating to persistent
    telemetry subscriptions. A persistent telemetry
    subscription is configued locally on the device through
    configuration, and is persistent across device restarts or
    other redundancy changes.
    """

    dial_out_subscription: RestconfList[DialOutSubscriptionItem] | None = Field(json_schema_extra={"is_config": True}, description="List of telemetry subscriptions. A telemetry\nsubscription consists of a set of collection\ndestinations, stream attributes, and associated paths to\nstate information in the model (sensor data)", default=None, alias="dial-out-subscription")

class StateDialInSubscription(YangBaseModel):
    """State information relating to dynamic telemetry
    subscriptions.
    """

    subscription_id: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="System generated identifer of the telemetry\nsubscription.", ge=0, le=18446744073709551615, default=None, alias="subscription-id")
    destination_address: str | None = Field(json_schema_extra={"is_config": False}, description="IP address of the telemetry stream destination", default=None, alias="destination-address")
    destination_port: int = Field(json_schema_extra={"is_config": False}, description="Protocol (udp or tcp) port number for the telemetry\nstream destination", ge=0, le=65535, alias="destination-port")
    sample_interval: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Time in milliseconds between the device's sample of a\ntelemetry data source. For example, setting this to 2000\nwould require the local device to collect the telemetry\ndata every 2000 milliseconds. There can be latency or jitter\nin transmitting the data, but the sample must occur at\nthe specified interval.\nThe timestamp must reflect the actual time when the data\nwas sampled, not simply the previous sample timestamp +\nsample-interval.\nIf sample-interval is set to 0, the telemetry sensor\nbecomes event based. The sensor must then emit data upon\nevery change of the underlying data source.", le=3600000, ge=0, default=10000, alias="sample-interval")
    heartbeat_interval: Uint64 | None = Field(json_schema_extra={"is_config": False}, description="Maximum time interval in milliseconds that may pass\nbetween updates from a device to a telemetry collector.\nIf this interval expires, but there is no updated data to\nsend (such as if suppress_updates has been configured), the\ndevice must send a telemetry message to the collector.", le=7200000, ge=0, default=20000, alias="heartbeat-interval")
    suppress_redundant: bool | None = Field(json_schema_extra={"is_config": False}, description="Boolean flag to control suppression of redundant\ntelemetry updates to the collector platform. If this flag is\nset to TRUE, then the collector will only send an update at\nthe configured interval if a subscribed data value has\nchanged. Otherwise, the device will not send an update to\nthe collector until expiration of the heartbeat interval.", default=True, alias="suppress-redundant")
    protocol: ProtocolEnum | None = Field(json_schema_extra={"is_config": False}, description="Selection of the transport protocol for the telemetry\nstream.", default=ProtocolEnum.GRPC)
    encoding: EncodingEnum | None = Field(json_schema_extra={"is_config": False}, description="Selection of the specific encoding or RPC framework\nfor telemetry messages to and from the network element.", default=EncodingEnum.JSON_IETF)

class PathState(YangBaseModel):
    """State information for a dynamic subscription
    paths of interest
    """

    model_path: str = Field(json_schema_extra={"is_config": False}, description="Path to a section of operational state of interest\n(the sensor).", alias="model-path")
    exclude_filter: str | None = Field(json_schema_extra={"is_config": False}, description="Filter to exclude certain values out of the state\nvalues", default=None, alias="exclude-filter")

class DialInSensorPathItem(YangBaseModel):
    """List of paths in the model which together
    comprise a sensor grouping. Filters for each path
    to exclude items are also provided.
    """

    path: str = Field(json_schema_extra={"is_config": False}, description="Reference to the path of interest", min_length=0, max_length=320)
    path_state: PathState | None = Field(json_schema_extra={"is_config": False}, description="State information for a dynamic subscription\npaths of interest", default=None, alias="path-state")

class DialInSensorPaths(YangBaseModel):
    """Top level container to hold a set of sensor
    paths grouped together
    """

    dial_in_sensor_path: RestconfList[DialInSensorPathItem] | None = Field(json_schema_extra={"is_config": False}, description="List of paths in the model which together\ncomprise a sensor grouping. Filters for each path\nto exclude items are also provided.", default=None, alias="dial-in-sensor-path")

class DialInSubscriptionItem(YangBaseModel):
    """List representation of telemetry subscriptions that
    are configured via an inline RPC, otherwise known
    as dynamic telemetry subscriptions.
    """

    subscription_id: Uint64 = Field(json_schema_extra={"is_config": False}, description="Reference to the identifier of the subscription\nitself. The id will be the handle to refer to the\nsubscription once created", ge=0, le=18446744073709551615, alias="subscription-id")
    state_dial_in_subscription: StateDialInSubscription | None = Field(json_schema_extra={"is_config": False}, description="State information relating to dynamic telemetry\nsubscriptions.", default=None, alias="state-dial-in-subscription")
    dial_in_sensor_paths: DialInSensorPaths | None = Field(json_schema_extra={"is_config": False}, description="Top level container to hold a set of sensor\npaths grouped together", default=None, alias="dial-in-sensor-paths")

class Dynamic(YangBaseModel):
    """This container holds information relating to dynamic
    telemetry subscriptions. A dynamic subscription is
    typically configured through an RPC channel, and does not
    persist across device restarts, or if the RPC channel is
    reset or otherwise torn down.
    """

    dial_in_subscription: RestconfList[DialInSubscriptionItem] | None = Field(json_schema_extra={"is_config": False}, description="List representation of telemetry subscriptions that\nare configured via an inline RPC, otherwise known\nas dynamic telemetry subscriptions.", default=None, alias="dial-in-subscription")

class Subscriptions(YangBaseModel):
    """This container holds information for both persistent
    and dynamic telemetry subscriptions.
    """

    persistent: Persistent | None = Field(json_schema_extra={"is_config": True}, description="This container holds information relating to persistent\ntelemetry subscriptions. A persistent telemetry\nsubscription is configued locally on the device through\nconfiguration, and is persistent across device restarts or\nother redundancy changes.", default=None)
    dynamic: Dynamic | None = Field(json_schema_extra={"is_config": True}, description="This container holds information relating to dynamic\ntelemetry subscriptions. A dynamic subscription is\ntypically configured through an RPC channel, and does not\npersist across device restarts, or if the RPC channel is\nreset or otherwise torn down.", default=None)

class TelemetrySystem(YangBaseModel):
    """Top level configuration and state for the
    device telemetry system.
    """

    sensor_groups: SensorGroups | None = Field(json_schema_extra={"is_config": True}, description="Top level container for sensor-groups.", default=None, alias="sensor-groups")
    destination_groups: DestinationGroups | None = Field(json_schema_extra={"is_config": True}, description="Top level container for destination group configuration\nand state.", default=None, alias="destination-groups")
    subscriptions: Subscriptions | None = Field(json_schema_extra={"is_config": True}, description="This container holds information for both persistent\nand dynamic telemetry subscriptions.", default=None)

class FileManagement(YangBaseModel):
    """Container includes management of log files, for example log-forwarding"""

    log_server: RestconfList[LogServerItem] | None = Field(json_schema_extra={"is_config": True}, description="Grouping the configuration parameters for log forwarding.", default=None, alias="log-server")
    telemetry_system: TelemetrySystem | None = Field(json_schema_extra={"is_config": True}, description="Top level configuration and state for the\ndevice telemetry system.", default=None, alias="telemetry-system")

class Lldp(YangBaseModel):
    """Container for LLDP config and status."""

    lldp_status_ne: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Global lldp control on NE level.\nValue of 'enabled', then the LLDP agent will receive,\nbut it will not transmit LLDP frames on all ports with port level lldp\nnot disabled of the NE.\n\nValue of 'disabled', then LLDP agent will not filter and\nreceive LLDP frames on all ports of the NE.  If there is remote systems\ninformation which is received on ports supporting LLDP and stored in\nthe system before the lldp-status becomes disabled, then the information\nwill naturally age out.", default=EnableSwitchEnum.ENABLED, alias="lldp-status-ne")
    msgTxInterval: int | None = Field(json_schema_extra={"is_config": True}, description="LLDP frame Retransmit Interval in seconds", ge=5, le=32768, default=30)
    msgTxHoldMultiplier: int | None = Field(json_schema_extra={"is_config": True}, description="TTL value for the TLVs transmitter over wire in seconds", ge=2, le=10, default=4)

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
    BRATISLAVA_BUDAPEST_LJUBLIJANA_PRAGUE_WASAW_GMT_PLUS_01_00 = "Bratislava-Budapest-Ljublijana-Prague-Wasaw[GMT+01:00]"
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

class TimeSourceStateEnum(str, Enum):
    """Enumeration for TimeSourceStateEnum
    
    Values:
      * External: Indicates that NE uses NTP for synchronization.
      * FreeRun: indicates that NE uses NE internal clock for Synchronization.
    """

    EXTERNAL = "External"
    FREERUN = "FreeRun"

class NtpAssociationTypeEnum(str, Enum):
    """Enumeration for NtpAssociationTypeEnum
    
    Values:
      * ntp-server: ntp server.
      * ntp-peer: ntp peer.
    """

    NTP_SERVER = "ntp-server"
    NTP_PEER = "ntp-peer"

class NtpAssociationStatus(YangBaseModel):
    """Container: ntp-association-status"""

    ntp_association_refid: str | None = Field(json_schema_extra={"is_config": False}, description="Reference clock type or address for the peer.", min_length=0, max_length=16, default=None, alias="ntp-association-refid")
    ntp_stratum: int | None = Field(json_schema_extra={"is_config": False}, description="This attribute indicates the stratum of local clock. A value of 0, indicates that Stratum in Unspecified.", ge=0, default=None, alias="ntp-stratum")
    ntp_polling_interval: int | None = Field(json_schema_extra={"is_config": False}, description="NTP polling interval. This is an integer number indicating the HOST polling interval between transmitted messages, in seconds.", ge=0, default=None, alias="ntp-polling-interval")
    ntp_precision: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="This is an unsigned floating-point number indicating the precision of the various clocks, in milliseconds.", default=None, alias="ntp-precision")
    ntp_association_offset: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Indicates the offset between the local clock and the superior reference clock.", default=None, alias="ntp-association-offset")
    ntp_association_reach: int | None = Field(json_schema_extra={"is_config": False}, description="Indicates the reachability of the configured server or peer.", ge=0, default=None, alias="ntp-association-reach")
    ntp_association_delay: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Indicates the delay between the local clock and the superior reference clock, in milliseconds.", default=None, alias="ntp-association-delay")
    ntp_association_dispersion: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Indicates the dispersion between the local clock and the peer clock, in milliseconds.", default=None, alias="ntp-association-dispersion")

class NtpAssociationItem(YangBaseModel):
    """List: ntp-association"""

    ntp_association_source: str = Field(json_schema_extra={"is_config": True}, description="Indicates the ntp-association-source.", alias="ntp-association-source")
    ntp_association_type: NtpAssociationTypeEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the ntp association type.", default=NtpAssociationTypeEnum.NTP_SERVER, alias="ntp-association-type")
    preferred_ntp_association: bool | None = Field(json_schema_extra={"is_config": True}, description="Indicates if this is preferred.", default=None, alias="preferred-ntp-association")
    ntp_admin_state: OperStatusEnum | None = Field(json_schema_extra={"is_config": True}, description="The administrative state specifies the permission to use or prohibition against using the resource.", default=OperStatusEnum.UP, alias="ntp-admin-state")
    ntp_association_status: NtpAssociationStatus | None = Field(json_schema_extra={"is_config": False}, default=None, alias="ntp-association-status")

class Ntp(YangBaseModel):
    """NTP (Network Time Protocol) system configuration and state"""

    ntp_enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="Indicates if NTP is enabled.", default=True, alias="ntp-enabled")
    current_time_source: str | None = Field(json_schema_extra={"is_config": False}, description="Indicates the current time source.", default="0.0.0.0", alias="current-time-source")
    ntp_association: RestconfList[NtpAssociationItem] | None = Field(json_schema_extra={"is_config": True}, default=None, alias="ntp-association")

class TimeManager(YangBaseModel):
    """Container: time-manager"""

    timezone: TimezoneEnum | None = Field(json_schema_extra={"is_config": True}, description="Indicates the Name of the Time Zone of this NE.", default=TimezoneEnum.GREENWICH_MEAN_TIME_DUBLIN_EDINBURGH_LISBON_LONDON_GMT)
    current_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Indicates the current Date and Time of this NE.", default=None, alias="current-time")
    last_start_time: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v))] | None = Field(json_schema_extra={"is_config": False}, description="Indicate the time of last system boot.", default=None, alias="last-start-time")
    up_time: str | None = Field(json_schema_extra={"is_config": False}, description="Indicate how long the system has been running.", default=None, alias="up-time")
    time_source_state: TimeSourceStateEnum = Field(json_schema_extra={"is_config": False}, description="Indicates the state of the time source.", alias="time-source-state")
    ntp: Ntp | None = Field(json_schema_extra={"is_config": True}, description="NTP (Network Time Protocol) system configuration and state", default=None)

class ZtcStatusEnum(str, Enum):
    """Enumeration for ZtcStatusEnum
    
    Values:
      * disabled
      * ready
      * ongoing
      * failed
      * done
      * incomplete
    """

    DISABLED = "disabled"
    READY = "ready"
    ONGOING = "ongoing"
    FAILED = "failed"
    DONE = "done"
    INCOMPLETE = "incomplete"

class Ztc(YangBaseModel):
    """Container: ztc"""

    ztc_enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="enable/disable Zero Touch commissioning.", default=True, alias="ztc-enabled")
    ztc_status: ZtcStatusEnum | None = Field(json_schema_extra={"is_config": False}, description="Shows the ZTC process status:\ndisabled - ZTC will not be attempted because it was disabled via configuration\nready - ZTC will be attempted when able to communicate with external ZTC server\nongoing - ZTC is ongoing\nfailed - some problems occurred during ZTC\ndone - ZTC completed successfully\nincomplete - ZTC incomplete.", default=ZtcStatusEnum.READY, alias="ztc-status")
    ztc_avail_status: str | None = Field(json_schema_extra={"is_config": False}, default=None, alias="ztc-avail-status")
    ztc_proxy: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute will enable/disable the ztc proxy function for the subtending NEs.", default=EnableSwitchEnum.ENABLED, alias="ztc-proxy")
    dhcp_server: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="The IPv4 address of the DHCP server for the DHCP relay agent when the ztc-proxy is enabled.", default=None, alias="dhcp-server")
    ztc_if_name: str | None = Field(json_schema_extra={"is_config": False}, description="The interface name ztc is working on.", default=None, alias="ztc-if-name")

class BaudRateEnum(str, Enum):
    """Enumeration for BaudRateEnum
    
    Values:
      * 9600
      * 19200
      * 38400
      * 57600
      * 115200
    """

    _9600 = "9600"
    _19200 = "19200"
    _38400 = "38400"
    _57600 = "57600"
    _115200 = "115200"

class Console(YangBaseModel):
    """Represents the console ports available in the system"""

    baud_rate: BaudRateEnum | None = Field(json_schema_extra={"is_config": True}, description="The baud rate of console port", default=BaudRateEnum._9600, alias="baud-rate")
    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable the console port", default=True)

class Ssh(YangBaseModel):
    """Represents the ssh server that allows Linux shell access to the user"""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable shell access via SSH", default=False)
    ssh_port: int | None = Field(json_schema_extra={"is_config": False}, description="The port that is listening for Linux shell ssh access", ge=0, default=8022, alias="ssh-port")
    timeout: int | None = Field(json_schema_extra={"is_config": True}, description="Set the idle timeout in seconds on terminal connections to the system for console port and ssh debug port.Setting the value to 0 disables this attribute (meaning the session will not time out).", ge=0, default=0)

class CommunityStringAccessEnum(str, Enum):
    """Enumeration for CommunityStringAccessEnum
    
    Values:
      * read-only
    """

    READ_ONLY = "read-only"

class SnmpCommunityItem(YangBaseModel):
    """List of SNMP Community Strings. Please note that the trap-community-string is located in the snmp-target MO."""

    community_string: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[!-~\\s]*)$", v))] = Field(json_schema_extra={"is_config": True}, description="Community String.", min_length=1, max_length=32, alias="community-string")
    community_string_access: CommunityStringAccessEnum | None = Field(json_schema_extra={"is_config": True}, description="snmp access right of this community string.", default=CommunityStringAccessEnum.READ_ONLY, alias="community-string-access")

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

    snmp_version: SnmpVersionEnum | None = Field(json_schema_extra={"is_config": True}, description="snmp version.", default=SnmpVersionEnum.V2C, alias="snmp-version")
    snmpv3_user: str | None = Field(json_schema_extra={"is_config": True}, description="Indicate the snmpv3 user.\n\nCondition (when): ../snmp-version = 'v3'", default=None, alias="snmpv3-user")
    target_name: str = Field(json_schema_extra={"is_config": True}, description="Identifies the SNMP target", min_length=1, max_length=32, alias="target-name")
    target_ip: str = Field(json_schema_extra={"is_config": True}, description="IP address of the SNMP target", alias="target-ip")
    target_port: int | None = Field(json_schema_extra={"is_config": True}, description="UDP port number.", ge=0, le=65535, default=162, alias="target-port")
    target_transport: TargetTransportEnum | None = Field(json_schema_extra={"is_config": True}, description="Type of transport for the SNMP target", default=TargetTransportEnum.UDP, alias="target-transport")
    trap_community_string: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[!-~\\s]*)$", v))] | None = Field(json_schema_extra={"is_config": True}, description="Community string used for SNMP traps\n\nCondition (when): ../snmp-version = 'v2c'", min_length=1, max_length=32, default="groove", alias="trap-community-string")

class Snmp(YangBaseModel):
    """Container with SNMP related configurations"""

    snmp_engine_id: str | None = Field(json_schema_extra={"is_config": False}, description="snmp EngineID of the NE. The EngineID will follow the EngineID format 3 defined in RFC3411. The MAC address in the Engine ID will be the first MAC address of the MAC addresses Pool of the NE.", min_length=0, max_length=256, default=None, alias="snmp-engine-id")
    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable global SNMP access", default=True)
    snmp_contact_info: str | None = Field(json_schema_extra={"is_config": True}, description="SNMP contact info of the NE. Default value is device info. Allow user defined value", min_length=1, max_length=512, default="https://www.infinera.com", alias="snmp-contact-info")
    snmp_community: RestconfList[SnmpCommunityItem] | None = Field(json_schema_extra={"is_config": True}, description="List of SNMP Community Strings. Please note that the trap-community-string is located in the snmp-target MO.", default=None, alias="snmp-community")
    snmp_target: RestconfList[SnmpTargetItem] | None = Field(json_schema_extra={"is_config": True}, description="List of SNMP targets (trap listeners)", default=None, alias="snmp-target")

class Restconf(YangBaseModel):
    """RESTCONF related configurations.

    RESTCONF is a HTTP based protocol that provides an interface for accessing
    YANG data models.
    """

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable RESTCONF access", default=True)
    rest_http_support: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Defines if the HTTP port (8080) is enabled for RESTCONF", default=EnableSwitchEnum.DISABLED, alias="rest-http-support")
    rest_https_support: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Defines if the HTTPS port (8181) is enabled for RESTCONF", default=EnableSwitchEnum.ENABLED, alias="rest-https-support")
    rest_session_timeout: int | None = Field(json_schema_extra={"is_config": True}, description="Timeout of a cookie based RESTCONF session.\nThe cookie expiration date is reset every time there is activity on the session.", ge=1, le=300, default=5, alias="rest-session-timeout")

class CliAliasItem(YangBaseModel):
    """List of aliases used in CLI.
    Can only be accessed via 'alias/unalias' CLI commands.
    """

    name: str = Field(json_schema_extra={"is_config": True}, description="Name of the alias", min_length=1, max_length=256)
    value: str | None = Field(json_schema_extra={"is_config": True}, description="Value of the alias", min_length=1, max_length=1024, default=None)

class CliScriptItem(YangBaseModel):
    """List of available CLI scripts.
    Scripts can be executed with the 'run' command
    """

    script_name: str = Field(json_schema_extra={"is_config": True}, description="File name of the CLI script", min_length=0, max_length=128, alias="script-name")
    description: str | None = Field(json_schema_extra={"is_config": True}, description="Description of the CLI script", min_length=0, max_length=256, default=None)

class Cli(YangBaseModel):
    """CLI related configurations"""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable CLI access", default=True)
    cli_alias: RestconfList[CliAliasItem] | None = Field(json_schema_extra={"is_config": True}, description="List of aliases used in CLI.\nCan only be accessed via 'alias/unalias' CLI commands.", default=None, alias="cli-alias")
    cli_script: RestconfList[CliScriptItem] | None = Field(json_schema_extra={"is_config": True}, description="List of available CLI scripts.\nScripts can be executed with the 'run' command", default=None, alias="cli-script")

class Netconf(YangBaseModel):
    """NETCONF related configurations"""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable NETCONF access", default=True)
    annotate_cli_name: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="If enabled, annotates NETCONF XML output with cli names for traceability.", default=EnableSwitchEnum.DISABLED, alias="annotate-cli-name")

class Grpc(YangBaseModel):
    """gRPC/gNMI related configurations"""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable gRPC/gNMI access", default=True)

class Webgui(YangBaseModel):
    """WebGUI related configurations"""

    enabled: bool | None = Field(json_schema_extra={"is_config": True}, description="User configurable switch to enable or disable webgui access", default=True)

class OpenconfigEnum(str, Enum):
    """Enumeration for OpenconfigEnum
    
    Values:
      * enhanced
      * false
      * standard
    """

    ENHANCED = "enhanced"
    FALSE = "false"
    STANDARD = "standard"

class ModelSelection(YangBaseModel):
    """Configuration of enabled YANG models"""

    openroadm: bool | None = Field(json_schema_extra={"is_config": True}, description="The openroadm support or not", default=False)
    openconfig: OpenconfigEnum | None = Field(json_schema_extra={"is_config": True}, description="The openconfig working mode", default=OpenconfigEnum.FALSE)

class ResultEnum(str, Enum):
    """Enumeration for ResultEnum
    
    Values:
      * successful
      * failed
      * unknown
    """

    SUCCESSFUL = "successful"
    FAILED = "failed"
    UNKNOWN = "unknown"

class DeleteFile(YangBaseModel):
    """Container: delete-file"""

    file_name: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=255, default=None, alias="file-name")
    result: ResultEnum | None = Field(json_schema_extra={"is_config": True}, default=None)
    result_msg: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=255, default=None, alias="result-msg")

class ShowFile(YangBaseModel):
    """Container: show-file"""

    file_name: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=255, default=None, alias="file-name")
    result: ResultEnum | None = Field(json_schema_extra={"is_config": True}, default=None)
    result_msg: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=511, default=None, alias="result-msg")

class ActionEnum_1(str, Enum):
    """Enumeration for ActionEnum
    
    Values:
      * upload
      * download
    """

    UPLOAD = "upload"
    DOWNLOAD = "download"

class FileTransfer(YangBaseModel):
    """Container: file-transfer"""

    action: ActionEnum_1 | None = Field(json_schema_extra={"is_config": True}, default=None)
    local_file_path: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=255, default=None, alias="local-file-path")
    remote_file_path: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=255, default=None, alias="remote-file-path")
    result: ResultEnum | None = Field(json_schema_extra={"is_config": True}, default=None)
    result_msg: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=511, default=None, alias="result-msg")
    exe_result: ResultEnum | None = Field(json_schema_extra={"is_config": True}, default=None, alias="exe-result")
    exe_result_msg: str | None = Field(json_schema_extra={"is_config": True}, min_length=0, max_length=511, default=None, alias="exe-result-msg")

class MultishelfFileManagementItem(YangBaseModel):
    """multishelf-file-management YANG models"""

    shelf_id: int = Field(json_schema_extra={"is_config": True}, ge=1, alias="shelf-id")
    delete_file: DeleteFile | None = Field(json_schema_extra={"is_config": True}, default=None, alias="delete-file")
    show_file: ShowFile | None = Field(json_schema_extra={"is_config": True}, default=None, alias="show-file")
    file_transfer: FileTransfer | None = Field(json_schema_extra={"is_config": True}, default=None, alias="file-transfer")

class StatusEnum(str, Enum):
    """Enumeration for StatusEnum
    
    Values:
      * Successful
      * Failed
    """

    SUCCESSFUL = "Successful"
    FAILED = "Failed"

class StageStateEnum(str, Enum):
    """Enumeration for StageStateEnum
    
    Values:
      * default
      * staging
      * staged
    """

    DEFAULT = "default"
    STAGING = "staging"
    STAGED = "staged"

class SwStageNotification(YangBaseModel):
    """Container: sw-stage-notification"""

    status: StatusEnum = Field(json_schema_extra={"is_config": True}, description="Successful or Failed")
    status_message: str | None = Field(json_schema_extra={"is_config": True}, description="Gives a more detailed status", min_length=0, max_length=256, default=None, alias="status-message")
    stage_state: StageStateEnum | None = Field(json_schema_extra={"is_config": True}, default=None, alias="stage-state")

class ActivateNotificationTypeEnum(str, Enum):
    """Enumeration for ActivateNotificationTypeEnum
    
    Values:
      * activate
      * commit
      * cancel
    """

    ACTIVATE = "activate"
    COMMIT = "commit"
    CANCEL = "cancel"

class ActivateStateEnum(str, Enum):
    """Enumeration for ActivateStateEnum
    
    Values:
      * default
      * before-reset
      * after-reset
    """

    DEFAULT = "default"
    BEFORE_RESET = "before-reset"
    AFTER_RESET = "after-reset"

class UpgradeResultEnum(str, Enum):
    """Enumeration for UpgradeResultEnum
    
    Values:
      * default
      * successful
      * failed
      * rollback
    """

    DEFAULT = "default"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ROLLBACK = "rollback"

class SwActivateNotification(YangBaseModel):
    """Container: sw-activate-notification"""

    activate_notification_type: ActivateNotificationTypeEnum = Field(json_schema_extra={"is_config": True}, description="Successful or Failed", alias="activate-notification-type")
    status: StatusEnum = Field(json_schema_extra={"is_config": True}, description="Successful or Failed")
    status_message: str | None = Field(json_schema_extra={"is_config": True}, description="Gives a more detailed status", min_length=0, max_length=256, default=None, alias="status-message")
    activate_state: ActivateStateEnum | None = Field(json_schema_extra={"is_config": True}, default=None, alias="activate-state")
    upgrade_result: UpgradeResultEnum | None = Field(json_schema_extra={"is_config": True}, default=None, alias="upgrade-result")

class MultishelfSwManagementItem(YangBaseModel):
    """multishelf-sw-management YANG models"""

    shelf_id: int = Field(json_schema_extra={"is_config": True}, ge=1, alias="shelf-id")
    sw_stage_notification: SwStageNotification | None = Field(json_schema_extra={"is_config": True}, default=None, alias="sw-stage-notification")
    sw_activate_notification: SwActivateNotification | None = Field(json_schema_extra={"is_config": True}, default=None, alias="sw-activate-notification")

class ShelfStatusEnum(str, Enum):
    """Enumeration for ShelfStatusEnum
    
    Values:
      * offline
      * online
      * ShelfIdAllocating
      * WaitDbReady
      * idle
      * SwUpgrade
      * KeepSilent
    """

    OFFLINE = "offline"
    ONLINE = "online"
    SHELFIDALLOCATING = "ShelfIdAllocating"
    WAITDBREADY = "WaitDbReady"
    IDLE = "idle"
    SWUPGRADE = "SwUpgrade"
    KEEPSILENT = "KeepSilent"

class MultishelfDiscoveryItem(YangBaseModel):
    """List: multishelf-discovery"""

    shelf_serial_number: str = Field(json_schema_extra={"is_config": False}, description="IP Address of device", min_length=0, max_length=64, alias="shelf-serial-number")
    shelf_mac_address: str | None = Field(json_schema_extra={"is_config": False}, description="The MAC address of the shelf", default=None, alias="shelf-mac-address")
    shelf_status: ShelfStatusEnum | None = Field(json_schema_extra={"is_config": False}, default=None, alias="shelf-status")
    shelf_id: int | None = Field(json_schema_extra={"is_config": False}, description="Identifier of the shelf after assigned by the system.", ge=1, default=None, alias="shelf-id")
    part_number: str | None = Field(json_schema_extra={"is_config": False}, description="The MAC address of the shelf", default=None, alias="part-number")
    shelf_linklocal_ip_address: str | None = Field(json_schema_extra={"is_config": False}, description="The link local IP address of the shelf, which is used during the shelf topology establishment phase", default=None, alias="shelf-linklocal-ip-address")
    supplementary_information: str | None = Field(json_schema_extra={"is_config": False}, description="supplementary infomation of the shelf", default=None, alias="supplementary-information")

class Capabilities(YangBaseModel):
    """System capabilities for each function"""

    max_degrees: int | None = Field(json_schema_extra={"is_config": False}, description="Max. number of degrees supported by device", ge=0, default=None, alias="max-degrees")
    max_srgs: int | None = Field(json_schema_extra={"is_config": False}, description="Max. number of SRGs in an add/drop group", ge=0, default=None, alias="max-srgs")

class SystemSystem(YangBaseModel):
    """Container with the part of the model with is related with the whole System"""

    unknown_pluggable_report: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute will enable/disable the alarm reporting for unknown pluggables present on the NE.", default=EnableSwitchEnum.ENABLED, alias="unknown-pluggable-report")
    factory_reset_button: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute will enable/disable factory reset button function on the NE.", default=EnableSwitchEnum.ENABLED, alias="factory-reset-button")
    auto_service_creation: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="Controls the system behavior regarding auto-creation of services for L1 modules based on port-mode.\nOnly applicable to muxponders (not for transponders).", default=EnableSwitchEnum.ENABLED, alias="auto-service-creation")
    multi_shelf: EnableSwitchEnum | None = Field(json_schema_extra={"is_config": True}, description="The attribute will enable/disable multi-shelf function on the NE.", default=EnableSwitchEnum.DISABLED, alias="multi-shelf")
    power_consumption: PowerConsumption | None = Field(json_schema_extra={"is_config": True}, description="The shelf base power consumption", default=None, alias="power-consumption")
    l2_dcn: L2Dcn | None = Field(json_schema_extra={"is_config": True}, default=None, alias="l2-dcn")
    networking: Networking | None = Field(json_schema_extra={"is_config": True}, default=None)
    security: Security | None = Field(json_schema_extra={"is_config": True}, default=None)
    sw_management: SwManagement | None = Field(json_schema_extra={"is_config": True}, description="The container includes management objects of software, for example, software load, database.", default=None, alias="sw-management")
    file_management: FileManagement | None = Field(json_schema_extra={"is_config": True}, description="Container includes management of log files, for example log-forwarding", default=None, alias="file-management")
    lldp: Lldp | None = Field(json_schema_extra={"is_config": True}, description="Container for LLDP config and status.", default=None)
    time_manager: TimeManager | None = Field(json_schema_extra={"is_config": True}, default=None, alias="time-manager")
    ztc: Ztc | None = Field(json_schema_extra={"is_config": True}, default=None)
    console: Console | None = Field(json_schema_extra={"is_config": True}, description="Represents the console ports available in the system", default=None)
    ssh: Ssh | None = Field(json_schema_extra={"is_config": True}, description="Represents the ssh server that allows Linux shell access to the user", default=None)
    snmp: Snmp | None = Field(json_schema_extra={"is_config": True}, description="Container with SNMP related configurations", default=None)
    restconf: Restconf | None = Field(json_schema_extra={"is_config": True}, description="RESTCONF related configurations.\n\nRESTCONF is a HTTP based protocol that provides an interface for accessing\nYANG data models.", default=None)
    cli: Cli | None = Field(json_schema_extra={"is_config": True}, description="CLI related configurations", default=None)
    netconf: Netconf | None = Field(json_schema_extra={"is_config": True}, description="NETCONF related configurations", default=None)
    grpc: Grpc | None = Field(json_schema_extra={"is_config": True}, description="gRPC/gNMI related configurations", default=None)
    webgui: Webgui | None = Field(json_schema_extra={"is_config": True}, description="WebGUI related configurations", default=None)
    model_selection: ModelSelection | None = Field(json_schema_extra={"is_config": True}, description="Configuration of enabled YANG models", default=None, alias="model-selection")
    multishelf_file_management: RestconfList[MultishelfFileManagementItem] | None = Field(json_schema_extra={"is_config": True}, description="multishelf-file-management YANG models", default=None, alias="multishelf-file-management")
    multishelf_sw_management: RestconfList[MultishelfSwManagementItem] | None = Field(json_schema_extra={"is_config": True}, description="multishelf-sw-management YANG models", default=None, alias="multishelf-sw-management")
    multishelf_discovery: RestconfList[MultishelfDiscoveryItem] | None = Field(json_schema_extra={"is_config": False}, default=None, alias="multishelf-discovery")
    capabilities: Capabilities | None = Field(json_schema_extra={"is_config": True}, description="System capabilities for each function", default=None)

class RstpBridgePortTableItem(YangBaseModel):
    """Table contains port-specific information for rstp config"""

    ifname: str = Field(json_schema_extra={"is_config": True}, description="Interface name of the port")
    cost: int | None = Field(json_schema_extra={"is_config": True}, description="The contribution of this port to the path cost of\npaths towards the spanning tree root which include this port also", ge=2000, le=200000, default=20000)
    priority: int | None = Field(json_schema_extra={"is_config": True}, description="The value of the priority field", ge=0, le=240, default=128)
    port_id: int | None = Field(json_schema_extra={"is_config": True}, description="Bridge port id", ge=0, default=0, alias="port-id")

class RstpConfig(YangBaseModel):
    """Collection of rstp configuration attributes"""

    bridge_priority: int | None = Field(json_schema_extra={"is_config": True}, description="Bridge Priority Value", ge=0, le=61440, default=32768, alias="bridge-priority")
    shutdown: bool | None = Field(json_schema_extra={"is_config": True}, description="Bridge admin state", default=False)
    hold_time: int | None = Field(json_schema_extra={"is_config": True}, description="The time interval during which no more than two\nBPDUs transmitted by this node in seconds - not used in rstp mode (in seconds)", ge=1, le=10, default=2, alias="hold-time")
    hello_time: int | None = Field(json_schema_extra={"is_config": True}, description="The time between the transmission of BPDU's by this node on any\nport, when role is root (in seconds)", ge=1, le=2, default=2, alias="hello-time")
    max_age: int | None = Field(json_schema_extra={"is_config": True}, description="The value that all bridges use for MaxAge when this bridge\nis acting as the root", ge=6, le=40, default=20, alias="max-age")
    forward_delay: int | None = Field(json_schema_extra={"is_config": True}, description="The port on the Switch spends this time in the listening\nstate while moving from the blocking state to the forwarding state (in seconds)", ge=4, le=30, default=15, alias="forward-delay")
    transmit_hold_count: int | None = Field(json_schema_extra={"is_config": True}, description="Maximum BPDU transmission rate", ge=1, le=10, default=2, alias="transmit-hold-count")
    rstp_bridge_port_table: RestconfList[RstpBridgePortTableItem] | None = Field(json_schema_extra={"is_config": True}, description="Table contains port-specific information for rstp config", default=None, alias="rstp-bridge-port-table")

class RstpBridgeAttr(YangBaseModel):
    """Collection of operational rstp bridge attributes"""

    root_bridge_port: int | None = Field(json_schema_extra={"is_config": False}, description="Port id of the root port", ge=0, default=None, alias="root-bridge-port")
    root_path_cost: int | None = Field(json_schema_extra={"is_config": False}, description="The cost of the path to the root as\nseen from this bridge", ge=0, default=None, alias="root-path-cost")
    root_bridge_priority: int | None = Field(json_schema_extra={"is_config": False}, description="Root Bridge Priority Value", ge=0, default=None, alias="root-bridge-priority")
    root_bridge_id: str | None = Field(json_schema_extra={"is_config": False}, description="Root Bridge identifier", min_length=1, max_length=255, default=None, alias="root-bridge-id")
    root_hold_time: int | None = Field(json_schema_extra={"is_config": False}, description="The time interval during which no more than two\nBPDUs transmitted by this node in seconds at root node (in seconds)", ge=0, default=None, alias="root-hold-time")
    root_hello_time: int | None = Field(json_schema_extra={"is_config": False}, description="The time between the transmission of BPDU's used at root node (in seconds)", ge=0, default=None, alias="root-hello-time")
    root_max_age: int | None = Field(json_schema_extra={"is_config": False}, description="The value that all bridges use for MaxAge used at root node", ge=0, default=None, alias="root-max-age")
    root_forward_delay: int | None = Field(json_schema_extra={"is_config": False}, description="The time in seconds spent on the listening state used at root node (in seconds)", ge=0, default=None, alias="root-forward-delay")
    bridge_id: str | None = Field(json_schema_extra={"is_config": False}, description="Bridge identifier of the bridge", min_length=1, max_length=255, default=None, alias="bridge-id")
    topo_change_count: int | None = Field(json_schema_extra={"is_config": False}, description="The total number of topology changes", ge=0, default=None, alias="topo-change-count")
    time_since_topo_change: int | None = Field(json_schema_extra={"is_config": False}, description="Time since last topology changes occurred (in seconds)", ge=0, default=None, alias="time-since-topo-change")

class BridgePortStateEnum(str, Enum):
    """Enumeration for BridgePortStateEnum
    
    Values:
      * discarding
      * blocked
      * learning
      * forwarding
      * unknown
    """

    DISCARDING = "discarding"
    BLOCKED = "blocked"
    LEARNING = "learning"
    FORWARDING = "forwarding"
    UNKNOWN = "unknown"

class BridgePortRoleEnum(str, Enum):
    """Enumeration for BridgePortRoleEnum
    
    Values:
      * designated
      * root
      * alternate
      * disabled
      * backup
      * unknown
    """

    DESIGNATED = "designated"
    ROOT = "root"
    ALTERNATE = "alternate"
    DISABLED = "disabled"
    BACKUP = "backup"
    UNKNOWN = "unknown"

class RstpBridgePortStateTableItem(YangBaseModel):
    """This table contains port-specific information for rstp state attributes"""

    ifname: str = Field(json_schema_extra={"is_config": False}, description="Interface name of the port")
    bridge_port_state: BridgePortStateEnum | None = Field(json_schema_extra={"is_config": False}, description="The port's current state", default=BridgePortStateEnum.UNKNOWN, alias="bridge-port-state")
    bridge_port_role: BridgePortRoleEnum | None = Field(json_schema_extra={"is_config": False}, description="The role payed by this port in the bridge", default=BridgePortRoleEnum.UNKNOWN, alias="bridge-port-role")
    bridge_port_id: int | None = Field(json_schema_extra={"is_config": False}, description="Unique port id of this port", ge=0, default=None, alias="bridge-port-id")
    oper_edge_bridge_port: bool | None = Field(json_schema_extra={"is_config": False}, description="The operational value of the Edge Port parameter", default=None, alias="oper-edge-bridge-port")
    designated_bridge_port: int | None = Field(json_schema_extra={"is_config": False}, description="Port id of the designated port", ge=0, default=None, alias="designated-bridge-port")
    designated_bridgeid: str | None = Field(json_schema_extra={"is_config": False}, description="The Bridge Identifier of the bridge that this port considers\nto be the Designated Bridge for this port's segment", min_length=1, max_length=255, default=None, alias="designated-bridgeid")

class RstpBridgePortStateAttr(YangBaseModel):
    """Collection of operational rstp port related attributes"""

    rstp_bridge_port_state_table: RestconfList[RstpBridgePortStateTableItem] | None = Field(json_schema_extra={"is_config": False}, description="This table contains port-specific information for rstp state attributes", default=None, alias="rstp-bridge-port-state-table")

class RstpState(YangBaseModel):
    """Collection of rstp operational attributes"""

    rstp_bridge_attr: RstpBridgeAttr | None = Field(json_schema_extra={"is_config": False}, description="Collection of operational rstp bridge attributes", default=None, alias="rstp-bridge-attr")
    rstp_bridge_port_state_attr: RstpBridgePortStateAttr | None = Field(json_schema_extra={"is_config": False}, description="Collection of operational rstp port related attributes", default=None, alias="rstp-bridge-port-state-attr")

class RstpBridgeInstanceItem(YangBaseModel):
    """rstp bridge instance, max instance = 4"""

    bridge_name: str = Field(json_schema_extra={"is_config": True}, description="unique name of the bridge", min_length=1, max_length=255, alias="bridge-name")
    rstp_config: RstpConfig | None = Field(json_schema_extra={"is_config": True}, description="Collection of rstp configuration attributes", default=None, alias="rstp-config")
    rstp_state: RstpState | None = Field(json_schema_extra={"is_config": False}, description="Collection of rstp operational attributes", default=None, alias="rstp-state")

class Rstp(YangBaseModel):
    """Open ROADM RSTP top level"""

    rstp_bridge_instance: RestconfList[RstpBridgeInstanceItem] | None = Field(json_schema_extra={"is_config": True}, description="rstp bridge instance, max instance = 4", default=None, alias="rstp-bridge-instance")

class Protocols(YangBaseModel):
    """Container: protocols"""

    rstp: Rstp | None = Field(json_schema_extra={"is_config": True}, description="Open ROADM RSTP top level", default=None)

class Ne(YangBaseModel):
    """Root of the Managed Entity hierarchy, represents the whole Network Element"""

    ne_id: str | None = Field(json_schema_extra={"is_config": True}, description="Network Element's system identification code.\nNote that this is unique identifier for each NE.", min_length=0, max_length=256, default="", alias="ne-id")
    ne_name: str | None = Field(json_schema_extra={"is_config": True}, description="Name assigned to this particular NE.\nA readable name for the NE. It can be used for NE.\nBut not expected to be used by NM for unique NE identification\nThe different function from ne-id is that user can keep ne-id unchanged,\nwhich uniquely identifies the NE, and update ne-name if necessary.", min_length=0, max_length=256, default="", alias="ne-name")
    ne_type: str | None = Field(json_schema_extra={"is_config": False}, description="Type of the NE", default="GROOVE_G30", alias="ne-type")
    ne_location: str | None = Field(json_schema_extra={"is_config": True}, description="Name of the location of this particular NE", min_length=0, max_length=256, default=None, alias="ne-location")
    ne_site: str | None = Field(json_schema_extra={"is_config": True}, description="Name or CLLI of the site where this NE is located", min_length=0, max_length=64, default=None, alias="ne-site")
    ne_altitude: int | None = Field(json_schema_extra={"is_config": True}, description="The altitude of the Network Element in meters", default=None, alias="ne-altitude")
    ne_vendor: str | None = Field(json_schema_extra={"is_config": False}, description="Vendor name of this NE", default="Infinera", alias="ne-vendor")
    ne_temperature: Decimal64 | None = Field(json_schema_extra={"is_config": False}, description="Ambient temperature sensed by the primary shelf for NE level", default=None, alias="ne-temperature")
    shelf: RestconfList[ShelfItem] | None = Field(json_schema_extra={"is_config": True}, default=None)
    inventory_data: InventoryData | None = Field(json_schema_extra={"is_config": False}, description="Simple container for the inventory list", default=None, alias="inventory-data")
    leds: Leds | None = Field(json_schema_extra={"is_config": False}, description="Simple container for the led list.", default=None)
    services: Services | None = Field(json_schema_extra={"is_config": True}, default=None)
    fault: Fault | None = Field(json_schema_extra={"is_config": True}, description="fault management MO, always exist", default=None)
    performance: Performance | None = Field(json_schema_extra={"is_config": True}, description="Container for all PM-Points and for PM related attributes", default=None)
    system: SystemSystem | None = Field(json_schema_extra={"is_config": True}, description="Container with the part of the model with is related with the whole System", default=None)
    protocols: Protocols | None = Field(json_schema_extra={"is_config": True}, default=None)

class NeData(YangBaseModel):
    """Root data model for ne"""

    ne: Ne | None = Field(json_schema_extra={"is_config": True}, description="Root of the Managed Entity hierarchy, represents the whole Network Element", default=None, alias="ne:ne")

class ChangedBy(YangBaseModel):
    """Container: changed-by"""

    # Choice: server-or-user
    # Case: server
    server: bool | None = Field(json_schema_extra={"is_config": None}, description="If present, the change was caused by the server.", default=None)
    # Case: by-user
    user_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None = Field(json_schema_extra={"is_config": None}, description="User name that made the change", min_length=1, max_length=32, default=None, alias="user-name")
    session_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9A-Fa-f.:]*)$", v))] | None = Field(json_schema_extra={"is_config": None}, description="Session ID that made the change", min_length=0, max_length=45, default=None, alias="session-id")
    message_id: str | None = Field(json_schema_extra={"is_config": None}, description="Message ID that matches the request", default=None, alias="message-id")

class DbChangeNotification(YangBaseModel):
    """Generated when the system detects that the <running> configuration datastore has changed"""

    changed_by: ChangedBy | None = Field(json_schema_extra={"is_config": None}, default=None, alias="changed-by")
    change: Any | None = Field(json_schema_extra={"is_config": None}, description="Copy of the running datastore subset and state data that changed.\nThe following metadata is used in this content:\n- 'operation' attribute, used for containers and lists. May have values 'create' and 'delete',\nrepresenting that this node was created or deleted.\n- 'old-value' attribute, used for leaf and leaf-lists. Will contain the previous value of the\nattribute it refers to.\nThese two metadata attributes are qualified with the same namespace as the datastore itself, and\nare defined according with RFC7952.\n\nXML Example:\n<object operation='create'>\n...\n</object>\n<attribute old-value='x'>y</attribute>", default=None)
