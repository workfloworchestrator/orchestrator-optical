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

from re import match
from typing import Annotated

from pydantic import AfterValidator


def validate_fqdn(value: str) -> str:
    # Regular expression for validating an FQDN
    regex = r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z0-9-]{1,63})+$"
    if not match(regex, value):
        raise ValueError(f"'{value}' is not a valid FQDN")
    return value


def validate_fqdn_prefix(value: str) -> str:
    # Regular expression for validating an FQDN
    regex = r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z0-9-]{1,63})*$"
    if not match(regex, value):
        raise ValueError(f"'{value}' is not a valid FQDN")
    return value


FQDN = Annotated[str, AfterValidator(validate_fqdn)]
FQDNPrefix = Annotated[str, AfterValidator(validate_fqdn_prefix)]
