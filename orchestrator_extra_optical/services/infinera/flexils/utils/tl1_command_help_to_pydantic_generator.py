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

"""
This script converts TL1 command help text to Pydantic class definition.
It is used manually to generate Pydantic classes for TL1 commands.
It is not used in the codebase.

ATCHUNG! You need to allign the generated code to the existing command classes.
For example, the generated code does not handle the `response_class` attribute
and includes the ctag field without setting its default value to the one stored
in the base class (thus, you should most probably delete the ctag field).
"""

mapping = {
    "ENT": "Enter",
    "ED": "Edit",
    "RTRV": "Retrieve",
    "DLT": "Delete",
    "RST": "Reset",
    "ACT": "Activate",
    "CANC": "Cancel",
    "SET": "Set",
    "CHG": "Change",
    "RLS": "Release",
    "OPR": "Operate",
    "INIT": "Initialize",
    "RMV": "Remove",
}


def is_optional(param: str) -> bool:
    return param.startswith("[") and param.endswith("]")


def parse_param(param: str) -> tuple[str, list[str] | None, bool]:
    """Returns (param_name, enum_values, is_optional)"""
    optional = is_optional(param)
    # Strip after checking optionality
    clean_param = param.strip("[]<>")

    if "=" not in clean_param:
        clean_param = clean_param.replace("|", "_")
        return clean_param.lower(), None, optional

    name, values = clean_param.split("=", 1)
    if "|" in values:
        return name.lower(), values.split("|"), optional
    return name.lower(), None, optional


def parse_tl1_help(help_text: str) -> str:
    """Convert TL1 help syntax to Pydantic class"""
    parts = help_text.split(":")
    verb, modifier = parts[0].split("-", 1)
    model_name = f"{mapping[verb]}{modifier.capitalize()}"
    code_lines = [
        "from .base import TL1BaseCommand, TL1BaseResponse",
        "from typing import List, Optional, Literal, ClassVar, Dict, Any, Type",
        "",
        f"class {modifier.capitalize()}Response(TL1BaseResponse):",
        "    def rename_positional_params(",
        "        self, parsed_data: List[Dict[str, Any]]",
        "    ) -> List[Dict[str, Any]]:",
        "        for record in parsed_data:",
        '            # record["AID"] = record.pop("positional_param_0_0")',
        "            pass",
        "        return parsed_data",
        "",
        f"class {model_name}(TL1BaseCommand):",
        f'    help_text: ClassVar[str] = "{help_text}"',
        f'    verb: ClassVar[str] = "{verb}"',
        f'    modifier: ClassVar[str] = "{modifier}"',
        f"    response_class: ClassVar[Type[TL1BaseResponse]] = {modifier.capitalize()}Response",
    ]

    for part in parts[1:]:
        if not part.strip():
            continue

        part = part.replace(",]", "],")
        part = part.replace("[,", ",[")

        params = part.split(",")
        for param in params:
            if not param.strip():
                continue

            name, enum_values, optional = parse_param(param)
            name = name.replace("-", "_")

            if enum_values:
                type_hint = f"Literal[{', '.join(repr(v) for v in enum_values)}]"
            elif "list" in name:
                type_hint = "List[str]"
            else:
                type_hint = "str"

            if optional:
                code_lines.append(f"    {name}: Optional[{type_hint}] = None")
            else:
                code_lines.append(f"    {name}: {type_hint}")

    return "\n".join(code_lines)


# Example usage
help_text = "RTRV-OCRS:[<TID>]:[<FROMAID>,<TOAID>]:<CTAG>:::[<CHANPLANTYPE=CUSTOM-CHPLAN-1|FLEX-CHPLAN-1|FLEX-CHPLAN-2|FLEX-CHPLAN-3|FLEX-CHPLAN-4|OCG-CHPLAN-1|OCG-CHPLAN-2|DEFAULT-CHPLAN-AOFX>][,<SIGTYPE=SIGNALED|MANUAL>][,<OELAID=oelaid>]:"
print(parse_tl1_help(help_text))
