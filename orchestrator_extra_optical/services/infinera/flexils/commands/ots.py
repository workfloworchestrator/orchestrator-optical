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


class OtsResponse(TL1BaseResponse):
    def rename_positional_params(
        self, parsed_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["AID"] = record.pop("positional_param_0_0", "")
            record["RESOURCETYPE"] = record.pop("positional_param_1_0", "")
            record["OPERSTATE"] = record.pop("positional_param_3_0", "")
            record["SUBOPERSTATE"] = record.pop("positional_param_3_1", "")
        return parsed_data


class RetrieveOts(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RTRV-OTS:[<TID>]:[<AID>]:<CTAG>::::"  # Store original template
    )
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "OTS"
    aid: str | None = None
    response_class: ClassVar[type[TL1BaseResponse]] = OtsResponse


class EditOts(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ED-OTS:[<TID>]:<AID>:<CTAG>:::[<PASSPROVNBRTP=passprovnbrtp>][,<LABEL=label>][,<TXFIBERTYPE=txfibertype>][,<PROVRXFIBERTYPE=provrxfibertype>][,<OLOSSOAKTIME=olossoaktime>][,<RXFIBERTYPEOVERRIDE=ENABLE|DISABLE>][,<RXASSOCIATEDOTS=rxassociatedots>][,<TXASSOCIATEDOTS=txassociatedots>][,<HISTSTATS=ENABLE|DISABLE>][,<INLINEDCMTYPE=inlinedcmtype>][,<PRESPANPAD=prespanpad>][,<POSTSPANPAD=postspanpad>][,<SPANDIST=spandist>][,<PROVNBRNODEID=provnbrnodeid>][,<PROVNBROTS=provnbrots>][,<RXEQPTLIST=rxeqptlist>][,<TXEQPTLIST=txeqptlist>][,<ASSOCIATEDSLTETP=associatedsltetp>][,<RXASSOCIATEDSLTEPTP=rxassociatedslteptp>][,<TXTTI=txtti>][,<EXPSAPI=expsapi>][,<EXPDAPI=expdapi>][,<TIMDETMODE=OFF|DAPI|SAPI|SAPI_DAPI>][,<OPTSPECT=CBAND|EXTENDEDCBAND|CLBAND>][,<EXPSPANLOSS=UNDER25DB|OVER25DB>][,<OAMCONTROL=ENABLE|DISABLE>][,<FIBERLABELTX=fiberlabeltx>][,<PEERTLAAMPOTSAID=peertlaampotsaid>][,<OTSOLOSEVTREPORTING=ENABLED|DISABLED>][,<AUTOOTDRTRACE=ENABLED|DISABLED>]"  # Store original template
    )
    verb: ClassVar[str] = "ED"
    modifier: ClassVar[str] = "OTS"
    aid: str
    passprovnbrtp: str | None = None
    label: str | None = None
    txfibertype: str | None = None
    provrxfibertype: str | None = None
    olossoaktime: str | None = None
    rxfibertypeoverride: Literal["ENABLE", "DISABLE"] | None = None
    rxassociatedots: str | None = None
    txassociatedots: str | None = None
    histstats: Literal["ENABLE", "DISABLE"] | None = None
    inlinedcmtype: str | None = None
    prespanpad: str | None = None
    postspanpad: str | None = None
    spandist: str | None = None
    provnbrnodeid: str | None = None
    provnbrots: str | None = None
    rxeqptlist: list[str] | None = None
    txeqptlist: list[str] | None = None
    associatedsltetp: str | None = None
    rxassociatedslteptp: str | None = None
    txtti: str | None = None
    expsapi: str | None = None
    expdapi: str | None = None
    timdetmode: Literal["OFF", "DAPI", "SAPI", "SAPI_DAPI"] | None = None
    optspect: Literal["CBAND", "EXTENDEDCBAND", "CLBAND"] | None = None
    expspanloss: Literal["UNDER25DB", "OVER25DB"] | None = None
    oamcontrol: Literal["ENABLE", "DISABLE"] | None = None
    fiberlabeltx: str | None = None
    peertlaampotsaid: str | None = None
    otsolosevtreporting: Literal["ENABLED", "DISABLED"] | None = None
    autootdrtrace: Literal["ENABLED", "DISABLED"] | None = None
