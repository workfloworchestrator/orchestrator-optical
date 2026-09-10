"""Tests for the FlexIlsTargetId custom type."""

import pytest
from pydantic import TypeAdapter, ValidationError

from orchestrator.optical.utils.custom_types.flexils import FlexIlsTargetId

_ADAPTER = TypeAdapter(FlexIlsTargetId)


@pytest.mark.parametrize(
    "value",
    [
        "a",
        "TID-1",
        "flexils-node-01",
        "span-dflt-a",
        "A.b_c-d",
        "a" * 20,
    ],
)
def test_valid_target_id(value: str) -> None:
    assert _ADAPTER.validate_python(value) == value


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ("", "empty"),
        ("1abc", "starts with a digit"),
        ("-abc", "starts with a hyphen"),
        ("a b", "contains a space"),
        ("a" * 21, "longer than 20 characters"),
        ("has/slash", "disallowed character"),
        ("has!bang", "disallowed character"),
    ],
)
def test_invalid_target_id(value: str, reason: str) -> None:
    with pytest.raises(ValidationError, match="FlexILS Target Identifier"):
        _ADAPTER.validate_python(value)
