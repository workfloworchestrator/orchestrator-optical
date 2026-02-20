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


class EnterOsnc(TL1BaseCommand):
    # Class variables
    help_text: ClassVar[str] = (
        "ENT-OSNC:[<TID>]:<AID>:<CTAG>:::[<LABEL=label>,]<REMENDPOINT=remendpoint>,<REMNODETID=remnodetid>[,<OELAID=oelaid>][,<RESTORABLE=NONE|ENDTOEND|REVENDTOEND>][,<CKTIDSUFFIX=cktidsuffix>][,<PREPROV=TRUE|FALSE>][,<FREQSLOTLIST=freqslotlist>][,<PREFSUPCHLIST=prefsupchlist>][,<SRCLMSCH=srclmsch>][,<DSTLMSCH=dstlmsch>][,<TAG=tag>][,<PASSBANDLIST=passbandlist>][,<CARRIERLIST=carrierlist>][,<AUTORETUNELMSCH=ENABLED|DISABLED>][,<SRCRXSCHOFFSET=srcrxschoffset>][,<DSTRXSCHOFFSET=dstrxschoffset>][,<MODULATIONCAT=NA|16G|17G-DAC|17G-DAC-12GOFFSET|22G-DAC|22G-DAC-12GOFFSET|33G-DAC|33G-DAC-12GOFFSET>][,<PROFSCHNUM=profschnum>][,<SCHPROFID=schprofid>][,<PREFOELLIST=prefoellist>][,<SRCSCHTHPROFLIST=srcschthproflist>][,<DSTSCHTHPROFLIST=dstschthproflist>][,<WTR=wtr>][,<FAULTSOAKTIMER=faultsoaktimer>][,<BAUDRATE=NA|17G|22G|33G|16G>][,<MODULATION=PM-QPSK|PM-BPSK|PM-EBPSK|PM-3QAM|PM-8QAM|PM-16QAM|PM-NONE>][,<FREQSLOTPLANTYPE=freqslotplantype>][,<SRCSCHPOWEROFFSET=srcschpoweroffset>][,<DSTSCHPOWEROFFSET=dstschpoweroffset>][,<ROUTETYPE=OEL|DYNAMIC>][,<INCLISTROUTTYP=LOOSE|STRICT>][,<INCLIST=inclist>][,<EXCLISTROUTTYP=LOOSE|STRICT>][,<EXCLIST=exclist>][,<RESTINCLISTROUTTYP=LOOSE|STRICT>][,<RESTINCLIST=restinclist>][,<RESTEXCLISTROUTTYP=LOOSE|STRICT>][,<RESTEXCLIST=restexclist>][,<INTRACARRSPECSHAPING=ENABLED|DISABLED>][,<DIGITRIGGER=TRUE|FALSE>][,<RESTORATIONTRIGGER=OPTICALSF|DIGITALSF|DIGITALSFNSD>]:[IS|OOS]"
    )
    verb: ClassVar[str] = "ENT"
    modifier: ClassVar[str] = "OSNC"

    # Instance fields
    cktidsuffix: str  # name of the OSNC
    aid: str  # local endpoint sch aid, e.g. 1-A-1-L1-1
    label: str
    remendpoint: str
    remnodetid: str
    oelaid: str
    passbandlist: list[str | int]
    carrierlist: list[str | int]
    restorable: Literal["NONE", "ENDTOEND", "REVENDTOEND"] | None = "NONE"
    preprov: Literal["TRUE", "FALSE"] | None = "TRUE"
    freqslotlist: list[str] | None = None
    prefsupchlist: list[str] | None = None
    srclmsch: str | None = None
    dstlmsch: str | None = None
    tag: str | None = None
    autoretunelmsch: Literal["ENABLED", "DISABLED"] | None = "DISABLED"
    srcrxschoffset: str | None = "0"
    dstrxschoffset: str | None = "0"
    modulationcat: Literal["NA", "16G", "17G-DAC", "17G-DAC-12GOFFSET", "22G-DAC", "22G-DAC-12GOFFSET", "33G-DAC", "33G-DAC-12GOFFSET"] | None = None
    profschnum: str | None = None
    schprofid: str | None = None
    prefoellist: list[str] | None = None
    srcschthproflist: list[str] | None = None
    dstschthproflist: list[str] | None = None
    wtr: str | None = None
    faultsoaktimer: str | None = "5"
    baudrate: Literal["NA", "17G", "22G", "33G", "16G"] | None = "NA"
    modulation: Literal["PM-QPSK", "PM-BPSK", "PM-EBPSK", "PM-3QAM", "PM-8QAM", "PM-16QAM", "PM-NONE"] | None = "PM-NONE"
    freqslotplantype: str | None = "FREQ-SLOT-PLAN-NONE"
    srcschpoweroffset: str | None = "0"
    dstschpoweroffset: str | None = "0"
    routetype: Literal["OEL", "DYNAMIC"] | None = "OEL"
    inclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    inclist: list[str] | None = None
    exclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    exclist: list[str] | None = None
    restinclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    restinclist: list[str] | None = None
    restexclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    restexclist: list[str] | None = None
    intracarrspecshaping: Literal["ENABLED", "DISABLED"] | None = "ENABLED"
    digitrigger: Literal["TRUE", "FALSE"] | None = "FALSE"
    restorationtrigger: Literal["OPTICALSF", "DIGITALSF", "DIGITALSFNSD"] | None = (
        "OPTICALSF"
    )
    is_oos: str | None = "IS"


class OsncResponse(TL1BaseResponse):
    def rename_positional_params(
        self, parsed_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["LOCENDPOINT"] = record.pop("positional_param_0_0")
            record["OPERSTATE"] = record.pop("positional_param_3_0")
        return parsed_data


class RetrieveOsnc(TL1BaseCommand):
    # Class variables
    help_text: ClassVar[str] = "RTRV-OSNC:[<TID>]:[<AID>]:<CTAG>:::[<OELAID=oelaid>]:"
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "OSNC"
    response_class: ClassVar[type[TL1BaseResponse]] = OsncResponse

    # Instance fields
    aid: str | None = None
    oelaid: str | None = None


class EditOsnc(TL1BaseCommand):
    # Class variables
    help_text: ClassVar[str] = (
        "ED-OSNC:[<TID>]:<AID>:<CTAG>:::[<LABEL=label>][,<OELAID=oelaid>][,<RESTORABLE=NONE|ENDTOEND|REVENDTOEND>][,<PREFSUPCHLIST=prefsupchlist>][,<CKTIDSUFFIX=cktidsuffix>][,<PREPROV=TRUE|FALSE>][,<SRCLMSCH=srclmsch>][,<DSTLMSCH=dstlmsch>][,<TAG=tag>][,<PASSBANDLIST=passbandlist>][,<CARRIERLIST=carrierlist>][,<AUTORETUNELMSCH=ENABLED|DISABLED>][,<SRCRXSCHOFFSET=srcrxschoffset>][,<DSTRXSCHOFFSET=dstrxschoffset>][,<PROFSCHNUM=profschnum>][,<SCHPROFID=schprofid>][,<PREFOELLIST=prefoellist>][,<SRCSCHTHPROFLIST=srcschthproflist>][,<DSTSCHTHPROFLIST=dstschthproflist>][,<WTR=wtr>][,<FAULTSOAKTIMER=faultsoaktimer>][,<BAUDRATE=NA|17G|22G|33G|16G>][,<MODULATION=PM-QPSK|PM-BPSK|PM-EBPSK|PM-3QAM|PM-8QAM|PM-16QAM|PM-NONE>][,<FREQSLOTPLANTYPE=freqslotplantype>][,<SRCSCHPOWEROFFSET=srcschpoweroffset>][,<DSTSCHPOWEROFFSET=dstschpoweroffset>][,<ROUTETYPE=OEL|DYNAMIC>][,<INCLISTROUTTYP=LOOSE|STRICT>][,<INCLIST=inclist>][,<EXCLISTROUTTYP=LOOSE|STRICT>][,<EXCLIST=exclist>][,<RESTINCLISTROUTTYP=LOOSE|STRICT>][,<RESTINCLIST=restinclist>][,<RESTEXCLISTROUTTYP=LOOSE|STRICT>][,<RESTEXCLIST=restexclist>][,<INTRACARRSPECSHAPING=ENABLED|DISABLED>][,<DIGITRIGGER=TRUE|FALSE>][,<RESTORATIONTRIGGER=OPTICALSF|DIGITALSF|DIGITALSFNSD>]:[IS|OOS]"
    )
    verb: ClassVar[str] = "ED"
    modifier: ClassVar[str] = "OSNC"

    # Instance fields
    aid: str
    label: str | None = None
    oelaid: str | None = None
    restorable: Literal["NONE", "ENDTOEND", "REVENDTOEND"] | None = None
    prefsupchlist: list[str] | None = None
    cktidsuffix: str | None = None
    preprov: Literal["TRUE", "FALSE"] | None = None
    srclmsch: str | None = None
    dstlmsch: str | None = None
    tag: str | None = None
    passbandlist: list[str | int] | None = None
    carrierlist: list[str | int] | None = None
    autoretunelmsch: Literal["ENABLED", "DISABLED"] | None = None
    srcrxschoffset: str | None = None
    dstrxschoffset: str | None = None
    profschnum: str | None = None
    schprofid: str | None = None
    prefoellist: list[str] | None = None
    srcschthproflist: list[str] | None = None
    dstschthproflist: list[str] | None = None
    wtr: str | None = None
    faultsoaktimer: str | None = None
    baudrate: Literal["NA", "17G", "22G", "33G", "16G"] | None = None
    modulation: Literal["PM-QPSK", "PM-BPSK", "PM-EBPSK", "PM-3QAM", "PM-8QAM", "PM-16QAM", "PM-NONE"] | None = None
    freqslotplantype: str | None = None
    srcschpoweroffset: str | None = None
    dstschpoweroffset: str | None = None
    routetype: Literal["OEL", "DYNAMIC"] | None = None
    inclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    inclist: list[str] | None = None
    exclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    exclist: list[str] | None = None
    restinclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    restinclist: list[str] | None = None
    restexclistrouttyp: Literal["LOOSE", "STRICT"] | None = None
    restexclist: list[str] | None = None
    intracarrspecshaping: Literal["ENABLED", "DISABLED"] | None = None
    digitrigger: Literal["TRUE", "FALSE"] | None = None
    restorationtrigger: Literal["OPTICALSF", "DIGITALSF", "DIGITALSFNSD"] | None = (
        None
    )
    is_oos: str | None = None


class DeleteOsnc(TL1BaseCommand):
    # Class variables
    help_text: ClassVar[str] = "DLT-OSNC:[<TID>]:<AID>:<CTAG>::::"
    verb: ClassVar[str] = "DLT"
    modifier: ClassVar[str] = "OSNC"

    # Instance fields
    aid: str
