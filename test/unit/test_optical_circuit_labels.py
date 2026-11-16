"""Unit tests for the composite OLS optical circuit labels.

The label carries both the conduit transport channel and every digital service
it carries (``"<channel>: <svcA> + <svcB>"``). The build/parse/validate helpers
are pure, so they are tested without fixtures or database access.
"""

import pytest

from orchestrator.optical.workflows.optical_digital_service.shared import (
    build_optical_circuit_label,
    ensure_circuit_label_token_valid,
    parse_optical_circuit_label,
)


def test_build_label_single_service() -> None:
    """A new single-channel service labels its circuit with channel and service."""
    assert build_optical_circuit_label("ch-01", ["svcA"]) == "ch-01: svcA"


def test_build_label_sorts_and_dedupes_services() -> None:
    """A normally muxed channel lists every carried service once, sorted."""
    assert build_optical_circuit_label("ch-01", ["svcB", "svcA", "svcB"]) == "ch-01: svcA + svcB"


def test_build_label_reverse_mux_pair_shares_service_name() -> None:
    """Each reverse-multiplexed channel carries its own conduit plus the shared service."""
    assert build_optical_circuit_label("ch-1", ["svc"]) == "ch-1: svc"
    assert build_optical_circuit_label("ch-2", ["svc"]) == "ch-2: svc"


def test_build_label_rejects_empty_services() -> None:
    """A label without carried services is never written."""
    with pytest.raises(ValueError, match="At least one digital service name"):
        build_optical_circuit_label("ch-01", [])


def test_build_label_rejects_blank_channel() -> None:
    """A label without a conduit channel is never written."""
    with pytest.raises(ValueError, match="cannot be blank"):
        build_optical_circuit_label("  ", ["svcA"])


@pytest.mark.parametrize("name", ["svc+A", "svc: A", "ch:01", "a:b", 'sv"c'])
def test_token_validation_rejects_separators(name: str) -> None:
    """Names containing label separators would make the label ambiguous."""
    with pytest.raises(ValueError, match="ambiguous"):
        ensure_circuit_label_token_valid(name, "digital service")


def test_token_validation_strips_and_returns() -> None:
    """Surrounding whitespace is stripped, inner content kept."""
    assert ensure_circuit_label_token_valid("  svcA  ", "digital service") == "svcA"


def test_parse_round_trip() -> None:
    """Parse inverts build for well-formed labels."""
    assert parse_optical_circuit_label("ch-01: svcB + svcA") == ("ch-01", ["svcA", "svcB"])


def test_parse_tolerates_legacy_unspaced_plus() -> None:
    """Legacy '+'-joined labels without spaces parse the same way."""
    assert parse_optical_circuit_label("ch-01: svcB+svcA") == ("ch-01", ["svcA", "svcB"])


def test_parse_legacy_label_yields_empty() -> None:
    """Legacy single-name labels are not composite labels."""
    assert parse_optical_circuit_label("svcA") == ("", [])


def test_channel_name_lookups_read_stored_values_in_any_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Names of other services' channels come from the stored values, never from loading the blocks.

    Loading an ACTIVE channel with the Inactive block class is refused by core, which made the
    modify identity page fail as soon as any channel was active.
    """
    from types import SimpleNamespace

    from orchestrator.optical.workflows.optical_digital_service import shared

    instances = [
        SimpleNamespace(subscription_instance_id="own", subscription_id="sub-own"),
        SimpleNamespace(subscription_instance_id="other", subscription_id="sub-other"),
    ]
    values = [
        SimpleNamespace(subscription_instance_id="own", value="OCh1"),
        SimpleNamespace(subscription_instance_id="other", value="OCh2"),
    ]
    monkeypatch.setattr(shared, "subscription_instances_by_block_type", lambda _name, _states: instances)
    monkeypatch.setattr(
        shared,
        "subscription_instance_values_by_instance_ids_and_resource_type",
        lambda ids, resource_type: values
        if (ids, resource_type) == (["own", "other"], "optical_transport_channel_name")
        else [],
    )

    assert shared.channel_names_taken_by_others({"own"}) == {"OCh2": "sub-other"}
    assert shared.channel_name_in_use("OCh1")
    assert not shared.channel_name_in_use("OCh3")
