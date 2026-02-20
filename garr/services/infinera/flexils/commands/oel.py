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


class OperateValrouteOel(TL1BaseCommand):
    help_text: ClassVar[str] = "OPR-VALROUTE-OEL:[<TID>]:<AID>:<CTAG>::::"
    verb: ClassVar[str] = "OPR"
    modifier: ClassVar[str] = "VALROUTE-OEL"
    aid: str


class OelResponse(TL1BaseResponse):
    def rename_positional_params(
        self, parsed_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["AID"] = record.pop("positional_param_0_0")
            record["RESOURCETYPE"] = record.pop("positional_param_1_0")
            record["OPERSTATE"] = record.pop("positional_param_3_0")
        return parsed_data


class RetrieveOel(TL1BaseCommand):
    help_text: ClassVar[str] = "RTRV-OEL:[<TID>]:[<AID>]:<CTAG>::::"
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "OEL"
    aid: str | None = None
    response_class: ClassVar[type[TL1BaseResponse]] = OelResponse


class EnterOel(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ENT-OEL:[<TID>]:<AID>:<CTAG>:::[<LABEL=label>,]<SRCNODENAME=srcnodename>,<DSTNODENAME=dstnodename>,<MODULATION=PM-NONE|PM-QPSK|PM-BPSK|PM-3QAM|PM-8QAM|PM-16QAM|PM-EBPSK|PM-MEPSK>,[<ENCODMOD=None|BC|BDLOpt|BDETOpt>,]<RATE=NA|500G|375G|250G|100G|50G|200G|150G|75G>,<SPECTYPE=NA|CS|SS>,<CARDTYPE=cardtype>,<FREQSLOTPLANTYPE=freqslotplantype>,[<COMPCARDTYPELIST=compcardtypelist>,][<VALIDFSLOTLIST=validfslotlist>,][<VALIDFRANGELIST=validfrangelist>,][<SRCPOWEROFFSET=srcpoweroffset>,][<DSTPOWEROFFSET=dstpoweroffset>,]<EXPLICITROUTE=explicitroute>[,<OELSOURCE=manual|NPS>][,<OEVERSION=oeversion>][,<NPSVERSION=npsversion>][,<BAUDRATE=NA|17G|22G|33G>][,<INTERCARRIERSPACING=18.75GHZ|25GHZ|37.5GHZ|50GHZ|62.5GHZ|75GHZ|NA>][,<GAURDBAND=gaurdband>][,<GAINSHARING=ENABLED|DISABLED>][,<CDDISPPRECOMP=ENABLED|DISABLED>][,<AGGPOLARTRACKING=ENABLED|DISABLED>][,<FECOHRATIO=FECOH-20|FECOH-25>][,<NUMFECITRNS=numfecitrns>]:[IS|OOS|AINS]"
    )
    verb: ClassVar[str] = "ENT"
    modifier: ClassVar[str] = "OEL"
    aid: str
    explicitroute: list[
        tuple[str, str, str, str]
    ]  # e.g. [('flex.aa00', '1-A-2-L1', 'flex.zz99', '1-A-1-L1')]
    label: str
    srcnodename: str
    dstnodename: str
    modulation: Literal[
        "PM-NONE",
        "PM-QPSK",
        "PM-BPSK",
        "PM-3QAM",
        "PM-8QAM",
        "PM-16QAM",
        "PM-EBPSK",
        "PM-MEPSK",
    ] = "PM-NONE"
    encodmod: Literal["None", "BC", "BDLOpt", "BDETOpt"] | None = "None"
    rate: Literal[
        "NA", "500G", "375G", "250G", "100G", "50G", "200G", "150G", "75G"
    ] = "NA"
    spectype: Literal["NA", "CS", "SS"] = "NA"
    cardtype: str = "UNKNOWN"
    freqslotplantype: str = "FREQ-SLOT-PLAN-NONE"
    compcardtypelist: list[str] | None = "UNKNOWN"
    srcpoweroffset: str | None = 0
    dstpoweroffset: str | None = 0
    oelsource: Literal["manual", "NPS"] | None = "MANUAL"
    gaurdband: str | None = 0
    numfecitrns: str | None = 4
    is_oos_ains: str | None = "IS"
    validfslotlist: list[str] | None = None
    validfrangelist: list[int]
    oeversion: str | None = None
    npsversion: str | None = None
    baudrate: Literal["NA", "17G", "22G", "33G"] | None = None
    intercarrierspacing: Literal["18.75GHZ", "25GHZ", "37.5GHZ", "50GHZ", "62.5GHZ", "75GHZ", "NA"] | None = None
    gainsharing: Literal["ENABLED", "DISABLED"] | None = None
    cddispprecomp: Literal["ENABLED", "DISABLED"] | None = None
    aggpolartracking: Literal["ENABLED", "DISABLED"] | None = None
    fecohratio: Literal["FECOH-20", "FECOH-25"] | None = None


class EditOel(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ED-OEL:[<TID>]:<AID>:<CTAG>:::[<LABEL=label>][,<OELSOURCE=manual|NPS>][,<COMPCARDTYPELIST=compcardtypelist>]:[IS|OOS|AINS]"
    )
    verb: ClassVar[str] = "ED"
    modifier: ClassVar[str] = "OEL"
    aid: str
    label: str | None = None
    oelsource: Literal["manual", "NPS"] | None = None
    compcardtypelist: list[str] | None = None
    is_oos_ains: str | None = None
