from typing import Any, ClassVar, Literal

from services.infinera.flexils.commands.base import TL1BaseCommand, TL1BaseResponse


class OcrsResponse(TL1BaseResponse):
    def rename_positional_params(self, parsed_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["FROMAID"] = record.pop("positional_param_0_0")
            record["TOAID"] = record.pop("positional_param_0_1")
            record["CrossConnectType"] = record.pop("positional_param_1_0")
            record["OPERSTATE"] = record.pop("positional_param_3_0")
            # record["SUBOPERSTATE"] = record.pop("positional_param_3_1")
        return parsed_data


class RetrieveOcrs(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RTRV-OCRS:[<TID>]:[<FROMAID>,<TOAID>]:<CTAG>:::[<CHANPLANTYPE=CUSTOM-CHPLAN-1|FLEX-CHPLAN-1|FLEX-CHPLAN-2|FLEX-CHPLAN-3|FLEX-CHPLAN-4|OCG-CHPLAN-1|OCG-CHPLAN-2|DEFAULT-CHPLAN-AOFX>][,<SIGTYPE=SIGNALED|MANUAL>][,<OELAID=oelaid>]:"
    )
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "OCRS"
    response_class: ClassVar[type[TL1BaseResponse]] = OcrsResponse
    fromaid: str | None = None
    toaid: str | None = None
    chanplantype: (
        Literal[
            "CUSTOM-CHPLAN-1",
            "FLEX-CHPLAN-1",
            "FLEX-CHPLAN-2",
            "FLEX-CHPLAN-3",
            "FLEX-CHPLAN-4",
            "OCG-CHPLAN-1",
            "OCG-CHPLAN-2",
            "DEFAULT-CHPLAN-AOFX",
        ]
        | None
    ) = None
    sigtype: Literal["SIGNALED", "MANUAL"] | None = None
    oelaid: str | None = None


class EnterOcrs(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ENT-OCRS:[<TID>]:<FROMAID>,<TOAID>:<CTAG>:::[<LABEL=label>,][<SUPCHNUM=supchnum>,][<CKTIDSUFFIX=cktidsuffix>,]<FREQSLOTPLANTYPE=freqslotplantype>[,<OELAID=oelaid>][,<SCHOFFSET=schoffset>][,<FREQSLOTLIST=freqslotlist>][,<POSSIBLEFREQSLOTLIST=possiblefreqslotlist>][,<LMSCH=lmsch>][,<PASSBANDLIST=passbandlist>][,<CARRIERLIST=carrierlist>][,<POSSIBLEPASSBANDLIST=possiblepassbandlist>][,<BAUDRATE=NA|16G|17G|22G|33G>][,<RXSCHOFFSET=rxschoffset>][,<AUTORETUNELMSCH=ENABLED|DISABLED>][,<MODULATIONCAT=NA|16G|17G-DAC|17G-DAC-12GOFFSET|22G-DAC|22G-DAC-12GOFFSET|33G-DAC|33G-DAC-12GOFFSET>][,<PROFSCHNUM=profschnum>][,<SCHPROFID=schprofid>][,<SCHTHPROFLIST=schthproflist>][,<PGAID=pgaid>][,<INTRACARRSPECSHAPING=ENABLED|DISABLED>]"
    )
    verb: ClassVar[str] = "ENT"
    modifier: ClassVar[str] = "OCRS"
    fromaid: str
    toaid: str
    label: str | None = None
    supchnum: str | None = None
    cktidsuffix: str | None = None
    freqslotplantype: str
    oelaid: str | None = None
    schoffset: str | None = None
    freqslotlist: list[str] | None = None
    possiblefreqslotlist: list[str] | None = None
    lmsch: str | None = None
    passbandlist: list[str | int] | None = None
    carrierlist: list[str | int] | None = None
    possiblepassbandlist: list[str] | None = None
    baudrate: Literal["NA", "16G", "17G", "22G", "33G"] | None = None
    rxschoffset: str | None = None
    autoretunelmsch: Literal["ENABLED", "DISABLED"] | None = None
    modulationcat: (
        Literal[
            "NA", "16G", "17G-DAC", "17G-DAC-12GOFFSET", "22G-DAC", "22G-DAC-12GOFFSET", "33G-DAC", "33G-DAC-12GOFFSET"
        ]
        | None
    ) = None
    profschnum: str | None = None
    schprofid: str | None = None
    schthproflist: list[str] | None = None
    pgaid: str | None = None
    intracarrspecshaping: Literal["ENABLED", "DISABLED"] | None = None


class EditOcrs(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "ED-OCRS:[<TID>]:<FROMAID>,<TOAID>:<CTAG>:::[<LABEL=label>][,<CKTIDSUFFIX=cktidsuffix>][,<FREQSLOTLIST=freqslotlist>][,<POSSIBLEFREQSLOTLIST=possiblefreqslotlist>][,<LMSCH=lmsch>][,<PASSBANDLIST=passbandlist>][,<CARRIERLIST=carrierlist>][,<POSSIBLEPASSBANDLIST=possiblepassbandlist>][,<ACTIVEPASSBANDLIST=activepassbandlist>][,<RXSCHOFFSET=rxschoffset>][,<AUTORETUNELMSCH=ENABLED|DISABLED>][,<SCHTHPROFLIST=schthproflist>][,<INTRACARRSPECSHAPING=ENABLED|DISABLED>]"
    )
    verb: ClassVar[str] = "ED"
    modifier: ClassVar[str] = "OCRS"
    fromaid: str
    toaid: str
    label: str | None = None
    cktidsuffix: str | None = None
    freqslotlist: list[str] | None = None
    possiblefreqslotlist: list[str] | None = None
    lmsch: str | None = None
    passbandlist: list[str] | None = None
    carrierlist: list[str] | None = None
    possiblepassbandlist: list[str] | None = None
    activepassbandlist: list[str] | None = None
    rxschoffset: str | None = None
    autoretunelmsch: Literal["ENABLED", "DISABLED"] | None = None
    schthproflist: list[str] | None = None
    intracarrspecshaping: Literal["ENABLED", "DISABLED"] | None = None


class DeleteOcrs(TL1BaseCommand):
    help_text: ClassVar[str] = "DLT-OCRS:[<TID>]:<FROMAID>,<TOAID>:<CTAG>::"
    verb: ClassVar[str] = "DLT"
    modifier: ClassVar[str] = "OCRS"
    fromaid: str
    toaid: str
