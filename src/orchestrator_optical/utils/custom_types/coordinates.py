
"""Custom coordinate types for latitude and longitude. Copied from GEANT Service Orchestrator project."""

import re
from typing import Annotated

from pydantic import AfterValidator
from typing_extensions import Doc

MAX_LONGITUDE = 180
MIN_LONGITUDE = -180
MAX_LATITUDE = 90
MIN_LATITUDE = -90


def validate_latitude(v: str) -> str:
    """Validate a latitude coordinate."""
    msg = "Invalid latitude coordinate. Valid examples: '40.7128', '-74.0060', '90', '-90', '0'."
    regex = re.compile(r"^-?([1-8]?\d(\.\d+)?|90(\.0+)?)$")
    if not regex.match(str(v)):
        raise ValueError(msg)

    float_v = float(v)
    if float_v > MAX_LATITUDE or float_v < MIN_LATITUDE:
        raise ValueError(msg)

    return v


def validate_longitude(v: str) -> str:
    """Validate a longitude coordinate."""
    regex = re.compile(r"^-?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$")
    msg = "Invalid longitude coordinate. Valid examples: '40.7128', '-74.0060', '180', '-180', '0'."
    if not regex.match(v):
        raise ValueError(msg)

    float_v = float(v)
    if float_v > MAX_LONGITUDE or float_v < MIN_LONGITUDE:
        raise ValueError(msg)

    return v


LatitudeCoordinate = Annotated[
    str,
    AfterValidator(validate_latitude),
    Doc(
        "A latitude coordinate, modeled as a string. "
        "The coordinate must match the format conforming to the latitude range of -90 to +90 degrees. "
        "It can be a floating-point number or an integer. Valid examples: 40.7128, -74.0060, 90, -90, 0."
    ),
]
LongitudeCoordinate = Annotated[
    str,
    AfterValidator(validate_longitude),
    Doc(
        "A longitude coordinate, modeled as a string. "
        "The coordinate must match the format conforming to the longitude "
        "range of -180 to +180 degrees. It can be a floating-point number or an integer. "
        "Valid examples: 40.7128, -74.0060, 180, -180, 0."
    ),
]
