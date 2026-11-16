"""Unit tests for the "before" column of the Optical Digital Service modify summary."""

from types import SimpleNamespace
from typing import Any, cast

from orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service import (
    _current_channel_values,
)


def _channel(name: str, mode: str, frequency: int, passband: tuple[int, int]) -> SimpleNamespace:
    return SimpleNamespace(
        optical_transport_channel_name=name,
        optical_transport_mode=mode,
        optical_transport_central_frequency=frequency,
        optical_transport_spectrum=SimpleNamespace(optical_spectrum_passband=passband),
    )


def test_current_channel_values_cover_every_channel_summary_field() -> None:
    block = SimpleNamespace(
        optical_digital_service_transport_channels=[
            _channel("ch-a", "16QAM_200G", 193_100_000, (193_062_500, 193_137_500)),
            _channel("ch-b", "16QAM_200G", 193_200_000, (193_150_000, 193_250_000)),
        ]
    )

    assert _current_channel_values(cast(Any, block)) == {
        "channel_name_1": "ch-a",
        "channel_name_2": "ch-b",
        "optical_transport_mode": "16QAM_200G",
        "frequency_1": "193100000",
        "bandwidth_1": "75000",
        "frequency_2": "193200000",
        "bandwidth_2": "100000",
    }
