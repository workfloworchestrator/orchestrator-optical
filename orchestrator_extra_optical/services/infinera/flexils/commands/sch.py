# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, ClassVar, Literal

from services.infinera.flexils.commands.base import TL1BaseCommand, TL1BaseResponse


class SchResponse(TL1BaseResponse):
    def rename_positional_params(self, parsed_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["AID"] = record.pop("positional_param_0_0", "")
            record["RESOURCETYPE"] = record.pop("positional_param_1_0", "")
            record["OPERSTATE"] = record.pop("positional_param_3_0", "")
            record["SUBOPERSTATE"] = record.pop("positional_param_3_1", "")
        return parsed_data


class RetrieveSch(TL1BaseCommand):
    help_text: ClassVar[str] = "RTRV-SCH:[<TID>]:[<AID>]:<CTAG>::::"
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "SCH"
    aid: str | None = None
    response_class: ClassVar[type[TL1BaseResponse]] = SchResponse


class EditSch(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ED-SCH:[<TID>]:<AID>:<CTAG>:::[<LABEL=label>][,<HISTSTATS=ENABLE|DISABLE>][,<MODULATION=PM-QPSK|PM-BPSK|PM-3QAM|PM-8QAM|PM-16QAM|PM-MEPSK>][,<SUPCHNUM=supchnum>][,<EXPTTI=exptti>][,<TXTTI=txtti>][,<SHUTTERSTATE=OPEN|CLOSED>][,<INTRASCHCARRRIPPLETH=intraschcarrrippleth>][,<INTRASCHCARRIERRIPPLE=Enabled|Disabled>][,<BAUDRATE=17G|22G|33G>][,<PROVPBLIST=provpblist>][,<PROVSUPPORTINGCARRGRPLIST=provsupportingcarrgrplist>][,<RXSCHPWROFFSET=rxschpwroffset>][,<OPTICALSIGNAL=ENABLED|SHUTDOWN>][,<MUXPWRCONTROLLOOP=MANUAL|AUTOMATIC>][,<DEMUXPWRCONTROLLOOP=ENABLED|DISABLED>][,<DEMUXSHUTTERSTATE=OPEN|CLOSED>][,<OSNRADD=osnradd>][,<SCHOFFSET=schoffset>][,<OFFSETOVERRIDE=ENABLED|DISABLED>][,<ADJSCHCTP=adjschctp>]:[IS|OOS]"
    )
    verb: ClassVar[str] = "ED"
    modifier: ClassVar[str] = "SCH"
    aid: str
    label: str | None = None
    histstats: Literal["ENABLE", "DISABLE"] | None = None
    modulation: Literal["PM-QPSK", "PM-BPSK", "PM-3QAM", "PM-8QAM", "PM-16QAM", "PM-MEPSK"] | None = None
    supchnum: str | None = None
    exptti: str | None = None
    txtti: str | None = None
    shutterstate: Literal["OPEN", "CLOSED"] | None = None
    intraschcarrrippleth: str | None = None
    intraschcarrierripple: Literal["Enabled", "Disabled"] | None = None
    baudrate: Literal["17G", "22G", "33G"] | None = None
    provpblist: list[str] | None = None
    provsupportingcarrgrplist: list[str] | None = None
    rxschpwroffset: str | None = None
    opticalsignal: Literal["ENABLED", "SHUTDOWN"] | None = None
    muxpwrcontrolloop: Literal["MANUAL", "AUTOMATIC"] | None = None
    demuxpwrcontrolloop: Literal["ENABLED", "DISABLED"] | None = None
    demuxshutterstate: Literal["OPEN", "CLOSED"] | None = None
    osnradd: str | None = None
    schoffset: str | None = None
    offsetoverride: Literal["ENABLED", "DISABLED"] | None = None
    adjschctp: str | None = None
    is_oos: str | None = None


class EnterSch(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ENT-SCH:[<TID>]:<AID>:<CTAG>:::[<FREQSLOTPLANTYPE=freqslotplantype>][,<SUPCHNUM=supchnum>][,<MODULATION=PM-QPSK|PM-BPSK|PM-3QAM|PM-8QAM|PM-16QAM|PM-MEPSK>][,<BAUDRATE=17G|22G|33G>][,<PROVPBLIST=provpblist>][,<PROVSUPPORTINGCARRGRPLIST=provsupportingcarrgrplist>][,<LABEL=label>][,<SCHPROFID=schprofid>][,<PROFSCHNUM=profschnum>]:[IS|OOS]"
    )
    verb: ClassVar[str] = "ENT"
    modifier: ClassVar[str] = "SCH"
    aid: str
    freqslotplantype: str | None = None
    supchnum: str | None = None
    modulation: Literal["PM-QPSK", "PM-BPSK", "PM-3QAM", "PM-8QAM", "PM-16QAM", "PM-MEPSK"] | None = None
    baudrate: Literal["17G", "22G", "33G"] | None = None
    provpblist: list[str] | None = None
    provsupportingcarrgrplist: list[str] | None = None
    label: str | None = None
    schprofid: str | None = None
    profschnum: str | None = None
    is_oos: str | None = None


class DeleteSch(TL1BaseCommand):
    help_text: ClassVar[str] = "DLT-SCH:[<TID>]:<AID>:<CTAG>::::"
    verb: ClassVar[str] = "DLT"
    modifier: ClassVar[str] = "SCH"
    aid: str


class MaintenanceSch(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RMV-{EQPT|OCH|DTPCTP|TRIB|OC768|OC192|OC48|OC12|OC3|STM256|STM64|STM16|STM4|STM1|10GBE|SNC|1GBE|10GCC|4GCC|HD1485CC|HD1483CC|SD270CC|DVB270CC|DV6000CC|ESCON200CC|IB25GCC|IB10GCC|25GCC|1G0625CC|1G25CC|2G125CC|NCT|SUBCLIENT|VCG|DCH|OTU1|OTU1E|OTU2|OTU3|OTU4|OTUC1I10|OTUC1I|OTUC2I|OTUC3I50|OTUC1I7G5|OTUC1I15|OTUC2I22G5|OTUC2I30|OTUC2I37G5|OTUC3I45|OTUC3I52G5|OTUC3I|OTUC4I67G5|OTUC4I75|OTUC24I|OTUC18I|OTUC12I|OTUC10I|OTUC20I|OTUC8I150|OTUC15I|OTUC5I|OTUC2I|OTUC1I|OTUC4I|OTUC9I|OTUC6I|OTUC8I|OTUC1I10|OTUC1I5|OTUC5I90|OTUC22I|OTUC16I|OTUC14I|OTUC17I330|OTUC14I270|OTUC11I210|OTUC11I|OTUC7I|OTUC9I165|OTUC7I135|OTUC6I105|OTUC6I110|OTUC4I70|OTUC3I55|OTUC2I35|OTUC2I25|OTUC5I82G5|OTU2E|OTU3E1|OTU3E2|ODU0|ODU1|ODU2|ODU3|ODU4|ODU1E|ODU2E|ODU3E1|ODU3E2|ODU1T|ODU1ET|ODU2T|ODU2ET|ODU2IT|ODU3IT|ODUFLEXIT|ODU3IPT|ODU4IT|OTU3I|OTU3IP|OTU4I|ODU2I|ODU3I|ODUFLEXI|ODUFLEX|ODU3IP|ODU4I|ODUC1I10|ODUC1I|ODUC2I|ODUC3I50|ODUC1I7G5|ODUC1I15|ODUC2I22G5|ODUC2I30|ODUC2I37G5|ODUC3I45|ODUC3I52G5|ODUC3I|ODUC4I67G5|ODUC4I75|ODUC24I|ODUC18I|ODUC12I|ODUC10I|ODUC20I|ODUC8I150|ODUC15I|ODUC5I|ODUC4I|ODUC9I|ODUC6I|ODUC8I|ODUC1I5|ODUC5I90|ODUC22I|ODUC16I|ODUC14I|ODUC17I330|ODUC14I270|ODUC11I210|ODUC11I|ODUC7I|ODUC9I165|ODUC7I135|ODUC6I105|ODUC6I110|ODUC4I70|ODUC3I55|ODUC2I35|ODUC2I25|ODUC5I82G5|1GFC|2GFC|4GFC|8GFC|10GFC|40GBE|100GBE|400GBE|10G3CC|OCHCTP|OCHPTP|11G1CC|GFP|GTP|SCH|PWRFEED|IDLERCTP|IDLERPTP|OSNC|CARRIERCTP|DIGITALWRAPPER|FLEXCARRIER|BANDPTP|NTP|ETHIF|AC|NWIF|VSI|PW|OPSMPTP|SCG|OCG|OLDPSCH|IKE|ASEPTP|BAND|OTS|EXPNPTP|NCC|OSC}:[<TID>]:<AID>:<CTAG>::[<mode>],[<state>]"
    )
    verb: ClassVar[str] = "RMV"
    modifier: ClassVar[str] = "SCH"
    aid: str
    mode: str | None = None
    state: str | None = None


class RestoreAdminStateSch(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RMV-{EQPT|OCH|DTPCTP|TRIB|OC768|OC192|OC48|OC12|OC3|STM256|STM64|STM16|STM4|STM1|10GBE|SNC|1GBE|10GCC|4GCC|HD1485CC|HD1483CC|SD270CC|DVB270CC|DV6000CC|ESCON200CC|IB25GCC|IB10GCC|25GCC|1G0625CC|1G25CC|2G125CC|NCT|SUBCLIENT|VCG|DCH|OTU1|OTU1E|OTU2|OTU3|OTU4|OTUC1I10|OTUC1I|OTUC2I|OTUC3I50|OTUC1I7G5|OTUC1I15|OTUC2I22G5|OTUC2I30|OTUC2I37G5|OTUC3I45|OTUC3I52G5|OTUC3I|OTUC4I67G5|OTUC4I75|OTUC24I|OTUC18I|OTUC12I|OTUC10I|OTUC20I|OTUC8I150|OTUC15I|OTUC5I|OTUC2I|OTUC1I|OTUC4I|OTUC9I|OTUC6I|OTUC8I|OTUC1I10|OTUC1I5|OTUC5I90|OTUC22I|OTUC16I|OTUC14I|OTUC17I330|OTUC14I270|OTUC11I210|OTUC11I|OTUC7I|OTUC9I165|OTUC7I135|OTUC6I105|OTUC6I110|OTUC4I70|OTUC3I55|OTUC2I35|OTUC2I25|OTUC5I82G5|OTU2E|OTU3E1|OTU3E2|ODU0|ODU1|ODU2|ODU3|ODU4|ODU1E|ODU2E|ODU3E1|ODU3E2|ODU1T|ODU1ET|ODU2T|ODU2ET|ODU2IT|ODU3IT|ODUFLEXIT|ODU3IPT|ODU4IT|OTU3I|OTU3IP|OTU4I|ODU2I|ODU3I|ODUFLEXI|ODUFLEX|ODU3IP|ODU4I|ODUC1I10|ODUC1I|ODUC2I|ODUC3I50|ODUC1I7G5|ODUC1I15|ODUC2I22G5|ODUC2I30|ODUC2I37G5|ODUC3I45|ODUC3I52G5|ODUC3I|ODUC4I67G5|ODUC4I75|ODUC24I|ODUC18I|ODUC12I|ODUC10I|ODUC20I|ODUC8I150|ODUC15I|ODUC5I|ODUC4I|ODUC9I|ODUC6I|ODUC8I|ODUC1I5|ODUC5I90|ODUC22I|ODUC16I|ODUC14I|ODUC17I330|ODUC14I270|ODUC11I210|ODUC11I|ODUC7I|ODUC9I165|ODUC7I135|ODUC6I105|ODUC6I110|ODUC4I70|ODUC3I55|ODUC2I35|ODUC2I25|ODUC5I82G5|1GFC|2GFC|4GFC|8GFC|10GFC|40GBE|100GBE|400GBE|10G3CC|OCHCTP|OCHPTP|11G1CC|GFP|GTP|SCH|PWRFEED|IDLERCTP|IDLERPTP|OSNC|CARRIERCTP|DIGITALWRAPPER|FLEXCARRIER|BANDPTP|NTP|ETHIF|AC|NWIF|VSI|PW|OPSMPTP|SCG|OCG|OLDPSCH|IKE|ASEPTP|BAND|OTS|EXPNPTP|NCC|OSC}:[<TID>]:<AID>:<CTAG>::[<mode>],[<state>]"
    )
    verb: ClassVar[str] = "RMV"
    modifier: ClassVar[str] = "SCH"
    aid: str
    mode: str | None = None
    state: str | None = None


class RetrieveSchPm(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RTRV-PM-SCH:[<TID>]:<AID>:<CTAG>::[<montype>],[1-UP],[NEND|FEND|NA],[RCV|TRMT|NA],[15-MIN|1-DAY],[<mondat>],[<montm>]::;"
    )
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "PM-SCH"
    aid: str
    montype: str | None = None
    mondat: str | None = None
    montm: str | None = None
    one_up: Literal["1-UP"] | None = None
    nend_fend_na: Literal["NEND", "FEND", "NA"] | None = None
    rcv_trmt_na: Literal["RCV", "TRMT", "NA"] | None = None
    time_interval: Literal["15-MIN", "1-DAY"] | None = None
