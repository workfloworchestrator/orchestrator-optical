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

from typing import Any, ClassVar

from services.infinera.flexils.commands.base import TL1BaseCommand, TL1BaseResponse


class OteintfResponse(TL1BaseResponse):
    def rename_positional_params(
        self, parsed_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for record in parsed_data:
            record["AID"] = record.pop("positional_param_0_0")
            record["OPERSTATE"] = record.pop("positional_param_3_0")
            record["FACILITY"] = record.pop("positional_param_1_0")
        return parsed_data

class RetrieveOteintf(TL1BaseCommand):
    help_text: ClassVar[str] = "RTRV-OTEINTF:[<TID>]:[<AID>]:<CTAG>::::"
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "OTEINTF"
    response_class: ClassVar[type[TL1BaseResponse]] = OteintfResponse
