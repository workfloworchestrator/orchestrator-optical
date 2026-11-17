"""Identifiers of the FlexILS optical circuit objects (OEL AID, OSNC ``CKTIDSUFFIX``).

Both are derived from the Optical Spectrum block, never stored:

- OEL AID: ``"<src>-<dst>-<id8>"``, e.g. ``mil01-rom02-3fa85f64``;
- OSNC ``CKTIDSUFFIX``: ``"<spectrum name> <id8>"``, e.g. ``CH-193.1 3fa85f64``;

where ``<src>`` / ``<dst>`` are the location codes of the two ends of the whole spectrum
path and ``<id8>`` the first 8 characters of the block's ``subscription_instance_id``.

``<id8>`` always comes last and is never cut: it is what an object is recognised by
(:func:`is_own_oel_aid`, :func:`is_own_cktid`), so a renamed spectrum or location is
converged on the device instead of losing the object. Everything longer than an
identifier allows goes to the labels (:mod:`orchestrator.optical.utils.labels`).
"""

from typing import Final
from uuid import UUID

__all__ = [
    "CKTID_SUFFIX_MAX_LENGTH",
    "ID8_LENGTH",
    "OEL_AID_MAX_LENGTH",
    "id8",
    "is_own_cktid",
    "is_own_oel_aid",
    "oel_aid",
    "osnc_cktid",
]

#: Longest OEL AID a FlexILS node accepts (tested on a node).
OEL_AID_MAX_LENGTH: Final = 64
#: Longest OSNC ``CKTIDSUFFIX`` a FlexILS node accepts (tested on a node).
CKTID_SUFFIX_MAX_LENGTH: Final = 48
#: Leading characters of the ``subscription_instance_id`` kept in the identifiers.
ID8_LENGTH: Final = 8

#: Characters a ``CKTIDSUFFIX`` cannot hold (vendor reference).
_CKTID_FORBIDDEN: Final = "\"~%\\,'"


def id8(instance_id: UUID | str) -> str:
    """Return the first 8 characters of a ``subscription_instance_id``.

    Raises:
        ValueError: If the id is empty.
    """
    token = str(instance_id).strip()[:ID8_LENGTH]
    if not token:
        msg = "A subscription instance id is required to build a FlexILS circuit identifier"
        raise ValueError(msg)
    return token


def oel_aid(src: str, dst: str, instance_id: UUID | str) -> str:
    """Return the OEL AID ``"<src>-<dst>-<id8>"``.

    Args:
        src: Location code of the first node of the spectrum path.
        dst: Location code of the last node of the spectrum path.
        instance_id: The ``subscription_instance_id`` of the Optical Spectrum block.

    Returns:
        The AID; both location codes are cut to the same length when it would not fit.
    """
    tail = f"-{id8(instance_id)}"
    per_code = (OEL_AID_MAX_LENGTH - len(tail) - 1) // 2
    return f"{src[:per_code]}-{dst[:per_code]}{tail}"


def osnc_cktid(spectrum_name: str, instance_id: UUID | str) -> str:
    """Return the OSNC ``CKTIDSUFFIX`` ``"<spectrum name> <id8>"``.

    Args:
        spectrum_name: The user-facing name of the optical spectrum.
        instance_id: The ``subscription_instance_id`` of the Optical Spectrum block.

    Returns:
        The identifier; characters the device refuses are replaced by ``_`` and the
        name is cut when it would not fit.

    Raises:
        ValueError: If the spectrum name is blank.
    """
    name = "".join("_" if char in _CKTID_FORBIDDEN else char for char in spectrum_name.strip())
    if not name:
        msg = "A spectrum name is required to build an OSNC CKTIDSUFFIX"
        raise ValueError(msg)
    tail = f" {id8(instance_id)}"
    return f"{name[: CKTID_SUFFIX_MAX_LENGTH - len(tail)].rstrip()}{tail}"


def is_own_oel_aid(aid: str, instance_id: UUID | str) -> bool:
    """Tell whether an OEL AID was built for the given Optical Spectrum block."""
    return aid.endswith(f"-{id8(instance_id)}")


def is_own_cktid(cktid: str, instance_id: UUID | str) -> bool:
    """Tell whether an OSNC ``CKTIDSUFFIX`` was built for the given Optical Spectrum block."""
    return cktid.endswith(f" {id8(instance_id)}")
