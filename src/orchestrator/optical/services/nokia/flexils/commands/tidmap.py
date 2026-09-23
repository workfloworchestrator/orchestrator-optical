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

"""RTRV-TIDMAP command for Nokia FlexILS nodes."""

from typing import Any, ClassVar

from orchestrator.optical.services.nokia.flexils.commands.base import TL1BaseCommand, TL1BaseResponse


class TidmapResponse(TL1BaseResponse):
    """Response model for the RTRV-TIDMAP command."""

    def rename_positional_params(self, parsed_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """RTRV-TIDMAP responses carry only key=value parameters, nothing to rename."""
        return parsed_data


class RetrieveTidmap(TL1BaseCommand):
    """Retrieve the TID to ROUTERID (GMPLS ID) mapping of the FlexILS network."""

    help_text: ClassVar[str] = "RTRV-TIDMAP:[<TID>]::<CTAG>::::"
    verb: ClassVar[str] = "RTRV"
    modifier: ClassVar[str] = "TIDMAP"
    response_class: ClassVar[type[TL1BaseResponse]] = TidmapResponse
