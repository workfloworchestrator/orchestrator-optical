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

"""Frequency, bandwidth and passband types plus passband arithmetic helpers."""

import ast
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field
from typing_extensions import Doc

Frequency = Annotated[
    int,
    Field(ge=191_312_500, le=196_137_500, multiple_of=6_250, title="Frequency in MHz"),
]

Bandwidth = Annotated[
    int,
    Field(ge=3125, title="Bandwidth in MHz"),
]

SpectralWidth = Annotated[
    int,
    Field(ge=3125, multiple_of=12_500, title="Spectral Width in MHz"),
]


def passband_from(central_frequency: int, bandwidth: int) -> tuple[int, int]:
    """Return the ``(start, end)`` passband of a central frequency and spectral width in MHz."""
    return (central_frequency - bandwidth // 2, central_frequency + bandwidth // 2)


def is_passband_aligned_to_grid(passband: tuple[int, int] | list[int], grid: int) -> bool:
    """Return whether both edges of the given passband lie on the given frequency grid.

    The check is purely arithmetic so it stays platform-neutral: callers pass
    the grid of the target platform (e.g. ``12500`` MHz for FlexILS).

    Args:
        passband: The ``(start, end)`` frequency range in MHz.
        grid: The required grid alignment in MHz.

    Returns:
        True when both edges are exact multiples of ``grid``.
    """
    return passband[0] % grid == 0 and passband[1] % grid == 0


def ensure_passband_aligned_to_grid(passband: tuple[int, int] | list[int], grid: int) -> None:
    """Raise if either edge of the given passband is off the given frequency grid.

    Form-layer reject path: called while the operator can still fix the input,
    so it fails instead of snapping.

    Args:
        passband: The ``(start, end)`` frequency range in MHz.
        grid: The required grid alignment in MHz.

    Raises:
        ValueError: If either edge is not an exact multiple of ``grid``.
    """
    if not is_passband_aligned_to_grid(passband, grid):
        msg = (
            f"Passband edges must be aligned to {grid} MHz "
            f"(12.5 GHz grid uses multiples of 12500 MHz); got ({passband[0]}, {passband[1]})"
        )
        raise ValueError(msg)


def snap_passband_to_grid(
    passband: tuple[int, int] | list[int],
    grid: int,
    carrier: tuple[int, int] | None = None,
) -> tuple[int, int]:
    """Snap the given passband to the given frequency grid, preserving the carrier when given.

    Execution-layer safety net: called after workflow inputs are immutable, so
    it adjusts instead of failing. Already aligned input is returned unchanged.
    Otherwise the passband is shrunk inward to the nearest on-grid interval;
    when that interval is empty or would clip the carrier span, it is expanded
    outward instead. The carrier, when given as ``(center frequency, bandwidth)``,
    is never modified: the snapped passband is guaranteed to still contain the
    full ``carrier ± bandwidth / 2`` span.

    Args:
        passband: The ``(start, end)`` frequency range in MHz.
        grid: The required grid alignment in MHz.
        carrier: Optional ``(center frequency, bandwidth)`` in MHz that the
            snapped passband must still contain.

    Returns:
        The on-grid ``(start, end)`` passband.
    """
    start, end = int(passband[0]), int(passband[1])
    if start % grid == 0 and end % grid == 0:
        return (start, end)
    carrier_span: tuple[int, int] | None = None
    if carrier is not None:
        carrier_span = passband_from(int(carrier[0]), int(carrier[1]))
    shrunk = (((start + grid - 1) // grid) * grid, (end // grid) * grid)
    if shrunk[0] < shrunk[1] and (
        carrier_span is None or (shrunk[0] <= carrier_span[0] and carrier_span[1] <= shrunk[1])
    ):
        return shrunk
    return ((start // grid) * grid, ((end + grid - 1) // grid) * grid)


def parse_if_string(value):
    """Parse a string value with :func:`ast.literal_eval`, returning other types unchanged."""
    if isinstance(value, str):
        return ast.literal_eval(value)
    return value


def validate_passband_order(value: list[Frequency]) -> list[Frequency]:
    """Validate that the start frequency is lower than the end frequency."""
    if value[0] >= value[1]:
        msg = "Start frequency must be less than end frequency"
        raise ValueError(msg)
    return value


Passband = Annotated[
    tuple[Frequency, Frequency],
    BeforeValidator(parse_if_string),
    AfterValidator(validate_passband_order),
    Doc("A passband, modeled as a list of two frequencies."),
]


def disjoint_intervals_overlap_search(
    intervals: list[tuple[int, int]],
    target_interval: tuple[int, int],
) -> tuple[int, int] | None:
    """Searches for an overlapping interval in a sorted list of *disjoint* intervals using binary search.

    Intervals include the start and do NOT include the end.

    Args:
        intervals (List[Tuple[int, int]]): A sorted list of disjoint intervals, where each interval is a tuple/list
            (start, end).
        target_interval (Tuple[int, int]): The interval to search for overlaps with (start, end).

    Returns:
        Optional[Tuple[int, int]]: The interval from `intervals` that overlaps with `target_interval`,
        or None if no such interval exists.
    """
    low = 0
    high = len(intervals) - 1

    while low <= high:
        mid = (low + high) // 2
        current_interval = intervals[mid]

        # Check for overlap:
        if current_interval[0] < target_interval[1] and target_interval[0] < current_interval[1]:
            return current_interval

        if current_interval[0] > target_interval[1]:  # Current interval starts after the target ends
            high = mid - 1
        else:  # current_interval[1] < target_interval[0] Current interval ends before the target starts
            low = mid + 1

    return None


def available_to_used_passbands(
    available_passbands: list[Passband],
    absolute_min_freq: Frequency = 191_325_000,
    absolute_max_freq: Frequency = 196_125_000,
) -> list[Passband]:
    """Calculate used frequency passbands within an absolute frequency range.

    Given a list of available (unused) frequency passbands, returns the used gaps.

    Args:
        available_passbands: A list of Passbands. Assumed to be
            sorted by start frequency and non-overlapping.
        absolute_min_freq: The minimum frequency of the absolute range.
        absolute_max_freq: The maximum frequency of the absolute range.

    Returns:
        A list of Passband, where each passband represents an used frequency
        passband as (start_freq, end_freq). Returns an empty list if there are no used passbands.
    """
    entire_band = (absolute_min_freq, absolute_max_freq)
    used_passbands = [entire_band]

    for available_passband in available_passbands:
        current_used_passband = used_passbands.pop()

        intersection_start = max(current_used_passband[0], available_passband[0])
        intersection_end = min(current_used_passband[1], available_passband[1])

        if intersection_start <= intersection_end:
            if current_used_passband[0] < available_passband[0]:
                used_passbands.append((current_used_passband[0], available_passband[0]))
            if current_used_passband[1] > available_passband[1]:
                used_passbands.append((available_passband[1], current_used_passband[1]))
        else:
            used_passbands.append(current_used_passband)

    return used_passbands
