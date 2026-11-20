"""Unit tests of the ``<marker> path: value`` lines of the configuration override (no device, no SDK)."""

import pytest

from orchestrator.optical.hal.reconcile import ConfigOverride, format_config_lines, parse_override_lines

PORT = "/ne:ne/shelf[shelf-id='1']/slot[slot-id='2']/card/port[port-id='1']"


def test_lines_are_sorted_by_marker_and_split_at_the_colon_ending_the_path() -> None:
    text = f"+ {PORT}/admin-status: down\n- {PORT}/service-label: a\n# {PORT}/connected-to: x"

    assert parse_override_lines(text) == ConfigOverride(
        set={f"{PORT}/admin-status": "down"},
        remove={f"{PORT}/service-label": "a"},
        restore={f"{PORT}/connected-to": "x"},
    )


def test_a_colon_inside_a_quoted_key_does_not_end_the_path() -> None:
    path = "/ioa-network-element:ne/services/xcon[name='a: b']/label"

    assert parse_override_lines(f"+ {path}: to: core").set == {path: "to: core"}


def test_blank_lines_are_skipped_and_an_empty_value_is_kept() -> None:
    text = f"\n  + {PORT}/service-label:\n\n+ {PORT}/admin-status: up  \n"

    assert parse_override_lines(text).set == {f"{PORT}/service-label": "", f"{PORT}/admin-status": "up"}


def test_empty_text_changes_nothing() -> None:
    assert parse_override_lines("") == ConfigOverride()


@pytest.mark.parametrize(
    "line",
    [
        f"{PORT}/admin-status: down",
        f"= {PORT}/admin-status: down",
        f"- {PORT}/admin-status",
        "+ admin-status: down",
        f"+ {PORT}/admin-status:down",
    ],
)
def test_a_line_that_is_not_marker_path_colon_value_is_refused(line: str) -> None:
    with pytest.raises(ValueError, match="Line 1 is not"):
        parse_override_lines(line)


def test_a_path_given_twice_is_refused_whatever_the_markers() -> None:
    with pytest.raises(ValueError, match="Line 2 gives"):
        parse_override_lines(f"+ {PORT}/admin-status: up\n- {PORT}/admin-status: up")


def test_the_change_survives_the_workflow_state() -> None:
    change = parse_override_lines(f"+ {PORT}/admin-status: down\n# {PORT}/service-label: a")

    assert ConfigOverride.from_dict(change.as_dict()) == change


def test_formatted_lines_are_sorted() -> None:
    config = {f"{PORT}/service-label": "x y", f"{PORT}/admin-status": "up", f"{PORT}/enabled": True}

    assert format_config_lines(config).splitlines() == [
        f"{PORT}/admin-status: up",
        f"{PORT}/enabled: true",
        f"{PORT}/service-label: x y",
    ]
