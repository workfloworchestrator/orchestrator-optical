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

import builtins
from typing import Any, ClassVar, Literal

from services.infinera.flexils.commands.base import TL1BaseCommand, TL1BaseResponse


class ScgResponse(TL1BaseResponse):
    def rename_positional_params(
        self, parsed_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["AID"] = record.pop("positional_param_0_0", "")
            record["RESOURCETYPE"] = record.pop("positional_param_1_0", "")
            record["OPERSTATE"] = record.pop("positional_param_3_0", "")
            record["SUBOPERSTATE"] = record.pop("positional_param_3_1", "")
        return parsed_data


class RetrieveScg(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RTRV-SCG:[<TID>]:[<AID>]:<CTAG>::[FMM|FRM|FSM|OFX|FMP|FMMF250|FMMC5|XT|FMMC12|FBM|MXP|FMMC6|FMMC6L]::"  # Store original template
    )
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "SCG"
    type: Literal["FMM", "FRM", "FSM", "OFX", "FMP", "FMMF250", "FMMC5", "XT", "FMMC12", "FBM", "MXP", "FMMC6", "FMMC6L"] | None = None
    response_class: ClassVar[builtins.type[TL1BaseResponse]] = ScgResponse


class EditScg(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ED-SCG:[<TID>]:<AID>:<CTAG>:::[<LABEL=label>][,<PROVNBRTP=provnbrtp>][,<PASSPROVNBRTP=passprovnbrtp>][,<PROVFPMPO=provfpmpo>][,<INTFTYP=INFWAVE|OPENWAVE|ASEIDLER|MANUALMODE-1|MANUALMODE-2|SLTEMANUAL-1|PASSIVE>][,<HISTSTATS=ENABLE|DISABLE>][,<PROVOWREMPTP=provowremptp>][,<TXPROVOWREMPTP=txprovowremptp>][,<RXPROVOWREMPTP=rxprovowremptp>][,<CMDMDE=NORM|FRCD>][,<PROVENCMODE=BC|BDLOPT|BDETOPT>][,<LINESYSMODE=MODESCG|MODEOPENWAVE|MODESCGPASSIVEMUX_1|MODEOPENAUTOMATED>][,<TARGETTXPOWEROFFSET=targettxpoweroffset>][,<TXEDFAPOWEROFFSET=txedfapoweroffset>][,<RXEDFAPOWEROFFSET=rxedfapoweroffset>][,<RXPOWEROFFSET=rxpoweroffset>][,<TXPOWEROFFSET=txpoweroffset>][,<RXPROVNBRTP=rxprovnbrtp>][,<ADSOAKTIMER=adsoaktimer>][,<PROVALPHABIN=Alphabin_2|Alphabin_8>][,<TRAFFICMOD=ADDDROP|PATHLOSSCHECKSOURCE>][,<SERVICESTATEFWD=ENABLED|DISABLED>][,<SERVICESTATEBWD=ENABLED|DISABLED>][,<CARRIERCOUNT=carriercount>][,<OWTARGETTXSCGPOWER=owtargettxscgpower>][,<PEERPORTAID=peerportaid>][,<PROVSPECTRUMTYPE=CS|SS|SS-A|SS-B>][,<RXEDFAGAIN=rxedfagain>][,<PROVFECOHRATIO=FECOH_20|FECOH_25>][,<OPMODE=GEN1|GEN2|FLEX>][,<PROVNBRTPTYPE=UNKNOWN|FBMSCGPTP>][,<LINEOPMODE=PASSIVE|ACTIVE>][,<DEFFLEXLICMODFORMAT=BPSK|QPSK|3QAM|8QAM|16QAM>][,<RXPCLOPRMODE=CONSTANTPOWER|CONSTANTGAIN>][,<CARRCNT33G=carrcnt33g>][,<CARRCNT22G=carrcnt22g>][,<CARRCNT17G=carrcnt17g>][,<OPTICALSIGNAL=ENABLED|MUTE|SHUTDOWN>][,<PERCARRTGTTXPWR=percarrtgttxpwr>][,<AUTODISCNBR=ENABLE|DISABLE>][,<LOTUNABLE=MASTER|SLAVE>][,<OWCONTENTIONCHECK=ENABLED|DISABLED>][,<FORCEDOPERATION=TRUE|FALSE>][,<INTFPROFILE=DEFAULT|SLTE_ADDDROP>]:[IS|OOS]"  # Store original template
    )
    verb: ClassVar[str] = "ED"
    modifier: ClassVar[str] = "SCG"
    aid: str
    label: str | None = None
    provnbrtp: str | None = None
    passprovnbrtp: str | None = None
    provfpmpo: str | None = None
    intftyp: Literal["INFWAVE", "OPENWAVE", "ASEIDLER", "MANUALMODE-1", "MANUALMODE-2", "SLTEMANUAL-1", "PASSIVE"] | None = None
    histstats: Literal["ENABLE", "DISABLE"] | None = None
    provowremptp: str | None = None
    txprovowremptp: str | None = None
    rxprovowremptp: str | None = None
    cmdmde: Literal["NORM", "FRCD"] | None = None
    provencmode: Literal["BC", "BDLOPT", "BDETOPT"] | None = None
    linesysmode: Literal["MODESCG", "MODEOPENWAVE", "MODESCGPASSIVEMUX_1", "MODEOPENAUTOMATED"] | None = None
    targettxpoweroffset: str | None = None
    txedfapoweroffset: str | None = None
    rxedfapoweroffset: str | None = None
    rxpoweroffset: str | None = None
    txpoweroffset: str | None = None
    rxprovnbrtp: str | None = None
    adsoaktimer: str | None = None
    provalphabin: Literal["Alphabin_2", "Alphabin_8"] | None = None
    trafficmod: Literal["ADDDROP", "PATHLOSSCHECKSOURCE"] | None = None
    servicestatefwd: Literal["ENABLED", "DISABLED"] | None = None
    servicestatebwd: Literal["ENABLED", "DISABLED"] | None = None
    carriercount: str | None = None
    owtargettxscgpower: str | None = None
    peerportaid: str | None = None
    provspectrumtype: Literal["CS", "SS", "SS-A", "SS-B"] | None = None
    rxedfagain: str | None = None
    provfecohratio: Literal["FECOH_20", "FECOH_25"] | None = None
    opmode: Literal["GEN1", "GEN2", "FLEX"] | None = None
    provnbrtptype: Literal["UNKNOWN", "FBMSCGPTP"] | None = None
    lineopmode: Literal["PASSIVE", "ACTIVE"] | None = None
    defflexlicmodformat: Literal["BPSK", "QPSK", "3QAM", "8QAM", "16QAM"] | None = (
        None
    )
    rxpcloprmode: Literal["CONSTANTPOWER", "CONSTANTGAIN"] | None = None
    carrcnt33g: str | None = None
    carrcnt22g: str | None = None
    carrcnt17g: str | None = None
    opticalsignal: Literal["ENABLED", "MUTE", "SHUTDOWN"] | None = None
    percarrtgttxpwr: str | None = None
    autodiscnbr: Literal["ENABLE", "DISABLE"] | None = None
    lotunable: Literal["MASTER", "SLAVE"] | None = None
    owcontentioncheck: Literal["ENABLED", "DISABLED"] | None = None
    forcedoperation: Literal["TRUE", "FALSE"] | None = None
    intfprofile: Literal["DEFAULT", "SLTE_ADDDROP"] | None = None
    is_oos: str | None = None
