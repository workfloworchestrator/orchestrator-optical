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

"""Helpers for custom singledispatch-based generic functions."""

from collections.abc import Callable
from itertools import filterfalse
from typing import Any, NoReturn, cast


def single_dispatch_base(func: Callable, value: Any) -> NoReturn:
    """Raise a TypeError describing the unsupported value type for a generic function.

    Args:
        func: the singledispatch generic function that was called.
        value: the value whose type is not registered.

    Raises:
        TypeError: always, listing the registered model types.
    """
    registry = cast(Any, func).registry

    supported_models = ", ".join(map(str, filterfalse(lambda t: t is object, registry.keys())))
    model_type = type(value)
    func_name = getattr(func, "__name__", repr(func))
    msg = f"`{func_name}` called for unsupported model type {model_type}. Supported model types are: {supported_models}"
    raise TypeError(msg)
