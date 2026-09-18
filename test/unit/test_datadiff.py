"""Unit tests for the datadiff helpers and the singledispatch error helper.

These are pure functions over nested dicts/pydantic models, so they are
exercised directly without any device or database.
"""

import functools
from typing import Any

import pytest
from pydantic import BaseModel

from orchestrator.optical.utils.datadiff import (
    anydump,
    compare_dicts,
    compare_jsons,
    flatten,
)
from orchestrator.optical.utils.singledispatch import single_dispatch_base


class _Item(BaseModel):
    name: str
    value: int = 0


def test_flatten_names_list_items_by_unique_id_keys() -> None:
    data = [{"id": 101, "name": "a"}, {"id": 102, "name": "b"}]

    assert flatten(data, unique_id_keys=["id"]) == {
        "root[id='101']['id']": 101,
        "root[id='101']['name']": "a",
        "root[id='102']['id']": 102,
        "root[id='102']['name']": "b",
    }


def test_flatten_falls_back_to_indexes_without_matching_keys() -> None:
    assert flatten([{"name": "a"}], unique_id_keys=["id"]) == {"root[0]['name']": "a"}


def test_compare_jsons_reports_added_removed_and_changed() -> None:
    diff = compare_jsons({"keep": 1, "gone": 2, "flip": 3}, {"keep": 1, "flip": 4, "new": 5})

    assert diff["---"] == {"root['gone']": 2, "root['flip']": 3}
    assert diff["+++"] == {"root['flip']": 4, "root['new']": 5}


def test_compare_jsons_honours_explicit_unique_id_keys() -> None:
    expected = [{"id": 1, "admin": "up"}]
    actual = [{"id": 1, "admin": "down"}]

    assert compare_jsons(expected, actual, unique_id_keys=["id"]) == {
        "---": {"root[id='1']['admin']": "up"},
        "+++": {"root[id='1']['admin']": "down"},
    }


def test_compare_jsons_without_unique_id_keys_uses_indexes() -> None:
    assert compare_jsons([{"a": 1}], [{"a": 2}], unique_id_keys=None) == {
        "---": {"root[0]['a']": 1},
        "+++": {"root[0]['a']": 2},
    }


def test_anydump_returns_empty_for_none() -> None:
    assert anydump(None) == {}


def test_anydump_dumps_single_model_and_lists() -> None:
    assert anydump(_Item(name="x")) == {"name": "x"}
    assert anydump([_Item(name="x"), _Item(name="y", value=2)]) == [{"name": "x"}, {"name": "y", "value": 2}]


def test_compare_dicts_categorises_differences() -> None:
    assert compare_dicts(
        {"same": 1, "missing": 2, "changed": 3},
        {"same": 1, "changed": 4, "extra": 5},
    ) == {
        "missing_key": {"root['missing']": 2},
        "unexpected_key": {"root['extra']": 5},
        "mismatched_value": {"root['changed']": {"expected": 3, "actual": 4}},
    }


def test_compare_dicts_without_differences_is_empty() -> None:
    assert compare_dicts({"a": [1, 2]}, {"a": [1, 2]}) == {
        "missing_key": {},
        "unexpected_key": {},
        "mismatched_value": {},
    }


def test_single_dispatch_base_lists_supported_types() -> None:
    @functools.singledispatch
    def generic(value: Any) -> str:
        return single_dispatch_base(generic, value)

    @generic.register
    def _(value: _Item) -> str:
        return value.name

    assert generic(_Item(name="x")) == "x"
    with pytest.raises(TypeError, match="unsupported model type"):
        generic(42)
