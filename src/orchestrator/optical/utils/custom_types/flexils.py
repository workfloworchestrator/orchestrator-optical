"""Nokia FlexILS specific custom types."""

import re
from typing import Annotated

from pydantic import AfterValidator
from typing_extensions import Doc

# A FlexILS Target Identifier (a GMPLS NENAME): 1-20 characters, starting with a
# letter, the rest being letters, digits, hyphens, dots or underscores. No spaces.
_FLEXILS_TARGET_ID_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,19}$")


def validate_flexils_target_id(value: str) -> str:
    """Validate a Nokia FlexILS Target Identifier (TID)."""
    if not _FLEXILS_TARGET_ID_REGEX.fullmatch(value):
        msg = (
            "FlexILS Target Identifier must be 1-20 characters, start with a letter, and "
            "contain only letters, digits, hyphens, dots or underscores (no spaces)."
        )
        raise ValueError(msg)
    return value


FlexIlsTargetId = Annotated[
    str,
    AfterValidator(validate_flexils_target_id),
    Doc(
        "Nokia FlexILS Target Identifier (TID): a GMPLS NENAME of up to 20 characters, "
        "starting with a letter, made of letters, digits, hyphens, dots or underscores."
    ),
]
