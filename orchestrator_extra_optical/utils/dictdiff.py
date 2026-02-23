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

from typing import Any


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list | tuple):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


def compare_dicts(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Compare two nested dictionaries and return the differences.
    The comparison checks for missing keys, unexpected keys, and mismatched values.

    Args:
        expected (dict): The expected dictionary structure and values.
        actual (dict): The actual dictionary structure and values to compare against the expected.

    Returns:
        dict: A dictionary containing the differences categorized as 'missing_key', 'unexpected_key', and 'mismatched_value'.
    """
    expected_flat = flatten_dict(expected)
    actual_flat = flatten_dict(actual)

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
