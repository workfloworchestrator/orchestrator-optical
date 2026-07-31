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
from typing import Annotated

from pydantic import AfterValidator

# Standard label matches: 1-63 chars, alphanumeric and hyphens.
# Cannot start or end with a hyphen.
LABEL_REGEX = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)

# Optional: SRV and internal records sometimes require underscores.
LABEL_WITH_UNDERSCORE_REGEX = re.compile(r"^[a-z0-9_]([a-z0-9-_]{0,61}[a-z0-9_])?$", re.IGNORECASE)


def validate_domain_syntax(
    value: str,
    *,
    min_labels: int = 1,
    allow_numeric_tld: bool = True,
    allow_wildcard: bool = False,
    allow_underscore: bool = False,
) -> str:
    if not isinstance(value, str):
        msg = "Domain name must be a string"
        raise TypeError(msg)

    # 1. Normalize and strip whitespace
    normalized = value.strip()
    if not normalized:
        msg_0 = "Domain name cannot be empty"
        raise ValueError(msg_0)

    # 2. Handle absolute domain names (trailing dot)
    is_absolute = normalized.endswith(".")
    clean_value = normalized[:-1] if is_absolute else normalized

    # 3. Handle IDNs (Internationalized Domain Names) by converting to Punycode
    try:
        ascii_value = clean_value.encode("idna").decode("ascii")
    except UnicodeError as e:
        msg_1 = f"Invalid Internationalized Domain Name (IDN): {e}"
        raise ValueError(msg_1) from e

    # 4. Enforce RFC 1035 total length limit (253 characters)
    if len(ascii_value) > 253:
        msg_2 = "Domain name exceeds maximum length of 253 characters"
        raise ValueError(msg_2)

    labels = ascii_value.split(".")

    # 5. Handle wildcard prefix (e.g., *.example.com) for subdomains
    if allow_wildcard and labels and labels[0] == "*":
        labels = labels[1:]
        if not labels:
            msg_3 = "Wildcard operator '*' must be followed by a valid domain"
            raise ValueError(msg_3)

    if not labels or any(not label for label in labels):
        msg_4 = "Domain name contains empty labels (double dots are invalid)"
        raise ValueError(msg_4)

    # 6. Validate individual labels
    for i, label in enumerate(labels):
        is_tld = i == len(labels) - 1

        # Select matching rule (TLD can never contain underscores)
        if is_tld:
            pattern = LABEL_REGEX
            allowed_chars_msg = "alphanumeric and hyphens"
        else:
            pattern = LABEL_WITH_UNDERSCORE_REGEX if allow_underscore else LABEL_REGEX
            allowed_chars_msg = (
                "alphanumeric, hyphens, and underscores" if allow_underscore else "alphanumeric and hyphens"
            )

        # Special case: single-character label must be alphanumeric
        if len(label) == 1:
            is_valid = label.isalnum() or (allow_underscore and not is_tld and label == "_")
            if not is_valid:
                msg_5 = f"Label '{label}' must be a single alphanumeric character"
                raise ValueError(msg_5)
        elif not pattern.match(label):
            msg_6 = (
                f"Label '{label}' is invalid: must be 1-63 characters, "
                f"containing only {allowed_chars_msg}, and cannot start or end with a hyphen/underscore"
            )
            raise ValueError(msg_6)

    # 7. Positional label count constraints
    if len(labels) < min_labels:
        label_word = "label" if min_labels == 1 else "labels"
        msg_7 = f"Domain name must have at least {min_labels} {label_word}"
        raise ValueError(msg_7)

    # 8. RFC 1123: Top-level domain (last label) cannot be purely numeric for FQDNs
    if not allow_numeric_tld and labels[-1].isdigit():
        msg_8 = "The top-level domain (last label) cannot be purely numeric"
        raise ValueError(msg_8)

    # Return lowercase normalized representation
    return normalized.lower()


# --- Pydantic v2 Type Declarations ---


# 1. FQDN (Fully Qualified Domain Name)
# Must have at least 2 labels, TLD cannot be numeric, no wildcards.
def _fqdn_validator(v: str) -> str:
    return validate_domain_syntax(v, min_labels=2, allow_numeric_tld=False, allow_wildcard=False)


Fqdn = Annotated[str, AfterValidator(_fqdn_validator)]


# 2. PQDN (Partially Qualified Domain Name)
# Allows 1 or more labels (e.g. 'localhost', 'my-server-12', 'database.local')
def _pqdn_validator(v: str) -> str:
    return validate_domain_syntax(v, min_labels=1, allow_numeric_tld=True, allow_wildcard=False)


Pqdn = Annotated[str, AfterValidator(_pqdn_validator)]


# 3. Subdomain / Wildcard Domain
# Allows optional wildcard prefixes (e.g. '*.example.com')
def _subdomain_validator(v: str) -> str:
    return validate_domain_syntax(v, min_labels=2, allow_numeric_tld=False, allow_wildcard=True)


Subdomain = Annotated[str, AfterValidator(_subdomain_validator)]


# 4. Subdomain Prefix
# Represents a portion of a domain that can be prepended (e.g. 'dev.api' or 'api')
# Can have 1 or more labels, allows underscores if needed.
def _subdomain_prefix_validator(v: str) -> str:
    return validate_domain_syntax(v, min_labels=1, allow_numeric_tld=True, allow_wildcard=False, allow_underscore=True)


SubdomainPrefix = Annotated[str, AfterValidator(_subdomain_prefix_validator)]
