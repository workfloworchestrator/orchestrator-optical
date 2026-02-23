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


class EqptResponse(TL1BaseResponse):
    def rename_positional_params(
        self, parsed_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["AID"] = record.pop("positional_param_0_0")
            record["TYPE"] = record.pop("positional_param_1_0")
            record["OPERSTATE"] = record.pop("positional_param_3_0")
        return parsed_data

class RetrieveEqpt(TL1BaseCommand):
    help_text: ClassVar[str] = (
        "RTRV-EQPT:[<TID>]:[<AID>]:<CTAG>::[<ctype>]:[<PROVSTATUS=PROV|UNPROV>][,<SAUPGPENDING=TRUE>]:"
    )
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "EQPT"
    ctype: str | None = None
    provstatus: Literal["PROV", "UNPROV"] | None = None
    saupgpending: str | None = None
    response_class: ClassVar[type[TL1BaseResponse]] = EqptResponse
