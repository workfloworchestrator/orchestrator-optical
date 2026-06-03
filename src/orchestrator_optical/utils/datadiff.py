# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for deep comparison of nested dictionaries."""

from typing import Any, Literal

JsonData = str | int | float | bool | None | dict[str, Any] | list[Any]
FlatDict = dict[str, str | int | float | bool | None]
DiffResult = dict[str, FlatDict]


def flatten(data: JsonData, path: str = "root", unique_id_keys: list[str] | None = None) -> FlatDict:
    """
    Flattens a nested dictionary or list into a flat dictionary.

    Args:
        data (JsonData): The data to flatten.
        path (str, optional): The current path in the data structure. Defaults to "root".
        unique_id_keys (list[str], optional): If a list is encountered, use any of these keys to identify unique
         items so that the list can be treated as a dictionary.
         e.g. unique_id_keys = ["id"] data = [{"id": 101, "name": "a"}, {"id": 102, "name": "b"}] will be flattened
         as {"root[id='101']['name']": "a", "root[id='102']['name']": "b"}

    Returns:
        dict[str, str | int | float | bool | None]: The flattened dictionary.
    """
    if unique_id_keys is None:
        unique_id_keys = []

    result: FlatDict = {}
    stack = [(data, path)]

    while stack:
        curr, curr_path = stack.pop()

        if isinstance(curr, dict):
            for key, value in curr.items():
                stack.append((value, f"{curr_path}['{key}']"))

        elif isinstance(curr, list):
            for i in range(len(curr) - 1, -1, -1):
                item = curr[i]
                suffix = str(i)

                if isinstance(item, dict) and unique_id_keys:
                    uids = [f"{k}='{item[k]}'" for k in unique_id_keys if item.get(k) is not None]
                    if uids:
                        suffix = ",".join(uids)

                stack.append((item, f"{curr_path}[{suffix}]"))
        else:
            result[curr_path] = curr

    return result


def compare_jsons(
    expected: JsonData, actual: JsonData, unique_id_keys: list[str] | Literal["default"] | None = "default"
) -> DiffResult:
    """
    Compares two JSON-like structures by flattening them and checking set differences.

    Args:
        expected (JsonData): The expected JSON-like structure.
        actual (JsonData): The actual JSON-like structure to compare against the expected.
        unique_id_keys (list[str], optional): If a list is encountered, use any of these keys to identify unique
         items so that the list can be treated as a dictionary. for example, if unique_id_keys = ["id"] and
         data = [{"id": 101, "name": "a"}, {"id": 102, "name": "b"}], then it will be flattened
         as {"root[id='101']['name']": "a", "root[id='102']['name']": "b"}

    Returns:
        dict[str, dict[str, str | int | float | bool | None]]: A dictionary containing the differences
         categorized as '---' (removed) and '+++' (added) with respect to the expected object.
    """
    if unique_id_keys == "default":
        unique_id_keys = ["alias-name", "name", "id", "AID"]

    expected_flat = flatten(expected, unique_id_keys=unique_id_keys)
    actual_flat = flatten(actual, unique_id_keys=unique_id_keys)

    diff: DiffResult = {"---": {}, "+++": {}}
    all_keys = expected_flat.keys() | actual_flat.keys()

    for key in all_keys:
        val_exp = expected_flat.get(key)
        val_act = actual_flat.get(key)

        if key not in expected_flat:
            diff["+++"][key] = val_act
        elif key not in actual_flat:
            diff["---"][key] = val_exp
        elif val_exp != val_act:
            diff["---"][key] = val_exp
            diff["+++"][key] = val_act

    return diff


def anydump(model):
    if model is None:
        return {}
    if isinstance(model, list):
        return [i.model_dump(exclude_unset=True) for i in model]
    return model.model_dump(exclude_unset=True)


def compare_pydantic_objects(
    expected: Any, actual: Any, unique_id_keys: list[str] | Literal["default"] | None = "default"
) -> DiffResult:
    return compare_jsons(
        anydump(expected),
        anydump(actual),
        unique_id_keys=unique_id_keys,
    )


def compare_dicts(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Deprecated. Use compare_jsons instead.

    Compare two nested dictionaries and return the differences.
    The comparison checks for missing keys, unexpected keys, and mismatched values.

    Args:
        expected (dict): The expected dictionary structure and values.
        actual (dict): The actual dictionary structure and values to compare against the expected.

    Returns:
        dict: A dictionary containing the differences categorized as 'missing_key',
        'unexpected_key', and 'mismatched_value'.
    """
    expected_flat = flatten(expected)
    actual_flat = flatten(actual)

    differences = {"missing_key": {}, "unexpected_key": {}, "mismatched_value": {}}
    sorted_keys = sorted(expected_flat.keys() | actual_flat.keys())
    for key in sorted_keys:
        if key not in expected_flat:
            differences["unexpected_key"][key] = actual_flat[key]
        elif key not in actual_flat:
            differences["missing_key"][key] = expected_flat[key]
        elif expected_flat.get(key) != actual_flat.get(key):
            differences["mismatched_value"][key] = {"expected": expected_flat[key], "actual": actual_flat[key]}

    return differences
