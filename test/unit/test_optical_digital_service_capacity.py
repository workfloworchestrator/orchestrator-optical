"""Unit tests for the per-family transceiver capacity resolution.

The adapter functions are pure (mode string in, capacity out), so they are
tested without fixtures. The HAL dispatcher itself only match-cases on the
host node and needs no test beyond the smoke import.
"""

import pytest

from orchestrator.optical.hal.adapters.nokia_groove_g30.port import (
    get_transceiver_capacity_from_mode as g30_capacity_from_mode,
)
from orchestrator.optical.hal.adapters.nokia_gx_g42.port import (
    get_transceiver_capacity_from_mode as g42_capacity_from_mode,
)


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("QPSK_100G", 100),
        # Effective rate class, not the bitrate in the mode name.
        ("8QAM_300G", 150),
        ("16QAM_200G", 200),
        ("OCHOS_OTU2", 10),
        ("OCHOS_OTU2e", 11),
        ("16QAM_32QAM_400G", 400),
        ("32QAM_64QAM_1100G_C", 550),
        ("not-applicable", None),
        ("DP16QAM", None),
        ("", None),
    ],
)
def test_g30_capacity_from_mode(mode: str, expected: int | None) -> None:
    assert g30_capacity_from_mode(mode) == expected


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("100E.31U", 100),
        ("400E.63P", 400),
        ("800E.96P", 800),
        # Only the E rule is implemented; M modes resolve to unknown.
        ("150M.33P", None),
        ("800M.95P", None),
        ("not-applicable", None),
        ("", None),
    ],
)
def test_g42_capacity_from_mode(mode: str, expected: int | None) -> None:
    assert g42_capacity_from_mode(mode) == expected
