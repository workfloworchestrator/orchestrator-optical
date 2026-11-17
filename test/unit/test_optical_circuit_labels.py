"""Unit tests for the identifiers and labels of the FlexILS optical circuit objects.

OEL AID ``"<src>-<dst>-<id8>"``, OSNC CKTIDSUFFIX ``"<spectrum name> <id8>"``, OEL label
``"<spectrum name> <hops>"`` and OSNC label ``"<services> <hops>"``. The helpers are pure,
so they are tested without fixtures or database access.
"""

from types import SimpleNamespace

import pytest

from orchestrator.optical.utils import identifiers, labels
from orchestrator.optical.workflows.optical_digital_service.shared import ensure_circuit_label_token_valid

UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def test_oel_aid_joins_the_path_ends_and_the_id8() -> None:
    assert identifiers.oel_aid("mil01", "rom02", UUID) == "mil01-rom02-3fa85f64"


def test_oel_aid_cuts_the_location_codes_and_keeps_the_id8() -> None:
    aid = identifiers.oel_aid("a" * 63, "b" * 63, UUID)

    assert len(aid) <= identifiers.OEL_AID_MAX_LENGTH
    assert aid == f"{'a' * 27}-{'b' * 27}-3fa85f64"


def test_osnc_cktid_is_the_spectrum_name_and_the_id8() -> None:
    assert identifiers.osnc_cktid("CH-193.1", UUID) == "CH-193.1 3fa85f64"


def test_osnc_cktid_cuts_the_name_and_keeps_the_id8() -> None:
    cktid = identifiers.osnc_cktid("x" * 80, UUID)

    assert len(cktid) == identifiers.CKTID_SUFFIX_MAX_LENGTH
    assert cktid.endswith(" 3fa85f64")


def test_osnc_cktid_replaces_the_characters_the_device_refuses() -> None:
    assert identifiers.osnc_cktid("a\"b~c%d\\e,f'g", UUID) == "a_b_c_d_e_f_g 3fa85f64"


def test_osnc_cktid_rejects_a_blank_name() -> None:
    with pytest.raises(ValueError, match="spectrum name"):
        identifiers.osnc_cktid("  ", UUID)


def test_id8_rejects_an_empty_id() -> None:
    with pytest.raises(ValueError, match="subscription instance id"):
        identifiers.id8("")


def test_own_objects_are_recognised_by_the_id8_ending_only() -> None:
    assert identifiers.is_own_oel_aid("old01-old02-3fa85f64", UUID)
    assert identifiers.is_own_cktid("renamed spectrum 3fa85f64", UUID)
    # A legacy identifier (the whole UUID) or a hand-made one is not ours.
    assert not identifiers.is_own_oel_aid(UUID, UUID)
    assert not identifiers.is_own_cktid(UUID, UUID)
    assert not identifiers.is_own_cktid("CH-193.1", UUID)


def test_oel_label_is_the_spectrum_name_and_the_hops() -> None:
    assert labels.oel_label("CH-193.1", ["mil01", "bol01", "rom02"]) == "CH-193.1 mil01bol01rom02"


def test_osnc_label_lists_the_services_sorted_once_then_the_hops() -> None:
    assert labels.osnc_label(["svcB", "svcA", "svcB"], ["mil01", "rom02"]) == "svcAsvcB mil01rom02"


def test_osnc_label_of_a_bare_spectrum_is_the_hops() -> None:
    assert labels.osnc_label([], ["mil01", "rom02"]) == "mil01rom02"


def test_labels_are_cut_from_the_right() -> None:
    label = labels.osnc_label(["svc"], [f"hop{index:02d}" for index in range(40)])

    assert len(label) == labels.FLEXILS_CIRCUIT_LABEL_MAX_LENGTH
    assert label.startswith("svc hop00hop01")


def _section(*nodes: tuple[str, str]) -> SimpleNamespace:
    ports = [
        SimpleNamespace(
            optical_port_host_node=SimpleNamespace(optical_node_role=role, location=SimpleNamespace(location_code=code))
        )
        for code, role in nodes
    ]
    return SimpleNamespace(
        optical_spectrum_section_add_drop_ports=[ports[0], ports[-1]],
        optical_spectrum_section_express_ports=ports[1:-1],
    )


def test_path_location_codes_span_every_section_without_amplifiers_or_repeats() -> None:
    """The hops are end to end: every section, amplifiers left out, a location counted once."""
    from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole

    roadm, amplifier = OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER
    first = _section(("mil01", roadm), ("mil01", roadm), ("ila01", amplifier), ("bol01", roadm), ("bol01", roadm))
    second = _section(("bol01", roadm), ("bol01", roadm), ("rom02", roadm), ("rom02", roadm))

    assert labels.path_location_codes([first, second]) == ["mil01", "bol01", "rom02"]


@pytest.mark.parametrize("name", ["svc+A", "svc: A", "ch:01", "a:b", 'sv"c'])
def test_token_validation_rejects_separators(name: str) -> None:
    """Names containing label separators would make the label ambiguous."""
    with pytest.raises(ValueError, match="ambiguous"):
        ensure_circuit_label_token_valid(name, "digital service")


def test_token_validation_strips_and_returns() -> None:
    """Surrounding whitespace is stripped, inner content kept."""
    assert ensure_circuit_label_token_valid("  svcA  ", "digital service") == "svcA"


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
