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

import re
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass

from services.infinera.flexils.exceptions import TL1CommandDeniedError
from services.infinera.flexils.utils import TL1CompletionStatus, generate_ctag

if TYPE_CHECKING:
    from services.infinera.flexils.client import FlexilsClient

T = TypeVar("T", bound="TL1BaseResponse")


class TL1CommandRegistry:
    commands: dict[str, type["TL1BaseCommand"]] = {}

    @classmethod
    def register(cls, command_class: type["TL1BaseCommand"]) -> None:
        verb = command_class.verb.lower()
        modifier = command_class.modifier.lower()
        modifier = modifier.replace("-", "_")
        method_name = f"{verb}_{modifier}"
        cls.commands[method_name] = command_class


class TL1CommandMeta(ModelMetaclass):
    """Metaclass that combines Pydantic's ModelMetaclass with TL1 command registration."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "TL1BaseCommand":
            TL1CommandRegistry.register(cls)
        return cls


class TL1BaseResponse(BaseModel):
    """Base class for TL1 responses."""

    status: TL1CompletionStatus = Field(..., description="Response status (e.g., COMPLD, DENY).")
    raw_data: str = Field(..., description="Raw response data.")
    parsed_data: list[dict[str, Any]] = Field(..., description="Parsed response data.")
    ctag: str = Field(generate_ctag(), description="Correlation Tag.")
    sid: str | None = Field(None, description="Source Identifier.")
    tid: str | None = Field(None, description="Target Identifier.")

    def rename_positional_params(self, parsed_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform parsed data with command-specific field names.
        Override in subclasses to customize field names.
        """
        return parsed_data

    @classmethod
    def from_raw_text(cls, message: str, tag: str) -> "TL1BaseResponse":
        """Parse a raw TL1 response into a structured response object."""
        index = message.rfind(tag)
        if index == -1:
            raise ValueError(f"Could not find tag {tag} in message: {message}")
        match = re.match(r"\s*(\w+)", message[index + len(tag) :])
        status = match.group(1)

        index = message.find(tag)
        message = message[index:]
        records = []
        lines = message.strip().splitlines()

        def split_preserving_quotes(text, delimiter=":"):
            parts = []
            current = []
            in_quotes = False
            i = 0

            while i < len(text):
                if i + 2 < len(text):
                    if text[i : i + 3] in (r"=\"", r":\""):
                        in_quotes = True
                    elif text[i : i + 3] in (r"\",", r"\":"):
                        in_quotes = False
                if text[i] == delimiter and not in_quotes:
                    parts.append("".join(current))
                    current = []
                else:
                    current.append(text[i])
                i += 1
            parts.append("".join(current))
            return parts

        for line in lines[1:]:
            line = line.strip(" ;")
            if not line or line[0] != '"':  # Skip lines that don't start with a quote
                continue
            line = line.strip('"')
            record = {}

            sections = split_preserving_quotes(line, ":")
            for i, section in enumerate(sections):
                if not section.strip():
                    continue

                parts = split_preserving_quotes(section, ",")
                for j, part in enumerate(parts):
                    if "=" in part:
                        key, value = part.split("=", 1)  # Split on first = only
                        key, value = key.strip(), value.strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]  # Remove surrounding quotes
                        if "&-" in value:
                            value = [v.split("&") for v in value.split("&-")]
                        elif "&" in value:
                            value = value.split("&")
                        record[key] = value
                    else:
                        record[f"positional_param_{i}_{j}"] = part.strip()

            records.append(record)

        # Create instance first to get proper typing of status
        instance = cls(
            status=TL1CompletionStatus(status),
            raw_data=message,
            parsed_data=records,
            ctag=tag,
        )
        # Now rename params with properly initialized instance
        instance.parsed_data = instance.rename_positional_params(records)
        return instance


class TL1BaseCommand(BaseModel, metaclass=TL1CommandMeta):
    """Base class for TL1 commands."""

    help_text: ClassVar[str]
    verb: ClassVar[str]
    modifier: ClassVar[str]
    response_class: ClassVar[type[TL1BaseResponse]] = TL1BaseResponse
    tid: str | None = Field(None, description="Target Identifier (optional).")
    aid: str | None = Field(None, description="Access Identifier (optional).")
    ctag: str = Field(generate_ctag(), description="Correlation Tag for tracking the response.")

    def execute(self, client: "FlexilsClient") -> TL1BaseResponse:
        """
        Execute the command on the device and return the response.
        Raises ValueError if the command is denied.
        """
        command_str = self.to_string()
        response_str = client.execute_raw_command(command_str, self.ctag)
        if TL1CompletionStatus.DENY in response_str and TL1CompletionStatus.ALREADY not in response_str:
            raise TL1CommandDeniedError(client.tid, command_str, response_str)
        return self.response_class.from_raw_text(response_str, self.ctag)

    def to_string(self) -> str:
        """Convert the command object into a TL1-formatted message."""
        # Split template into sections
        sections = self.help_text.split(":")
        result = [f"{self.verb}-{self.modifier}"]

        # Process each parameter section
        for section in sections[1:]:
            if not section.strip():
                result.append("")
                continue

            section = section.replace(",]", "],")
            section = section.replace("[,", ",[")

            params = []
            section_parts = section.split(",")

            for part in section_parts:
                is_optional = part.startswith("[") and part.endswith("]")
                part = part.strip("[]<>")
                if not part:
                    continue

                if "=" in part:
                    # Handle named parameters
                    name = part.split("=")[0]
                    key = name.lower().replace("-", "_")
                    value = getattr(self, key, None)
                    if value is not None:
                        if isinstance(value, (list, tuple)):
                            if isinstance(value[0], (list, tuple)):
                                # Handle list of tuples/lists - join tuples with '&-'
                                value = "&-".join(["&".join(str(item) for item in v) for v in value])
                            else:
                                # Handle single tuple/list - join elements with '&'
                                value = "&".join(str(item) for item in value)
                        params.append(f"{name}={value}")
                else:
                    # Handle positional parameters (TID, AID, CTAG, etc)
                    name = part.lower()
                    name = name.replace("-", "_")
                    name = name.replace("|", "_")
                    value = getattr(self, name, None)
                    if value is not None:
                        params.append(str(value))
                    # For required positional parameters, add empty placeholder
                    elif not is_optional:
                        params.append("")

            if all(param == "" for param in params):
                # If all parameters are empty, append an empty string
                result.append("")
            else:
                result.append(",".join(params))

        return ":".join(result) + ";"
