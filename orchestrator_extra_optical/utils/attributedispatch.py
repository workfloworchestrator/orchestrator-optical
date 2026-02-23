# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import types
from collections.abc import Callable
from typing import Any, NoReturn, TypeVar

T = TypeVar("T")


def attributedispatch(attr_name: str, func: Callable | None = None):
    """
    A decorator that enables dynamic function dispatching based on a specific attribute's value.

    :param attr_name: The name of the attribute to use for dispatching
    :param func: The function to be decorated (optional)
    :return: A wrapper function with enhanced dispatching capabilities
    """
    # Allow the decorator to be used with or without parentheses
    if func is None:
        return lambda f: attributedispatch(attr_name, f)

    # Create registries to manage different function implementations
    registry = {}

    def dispatch(obj):
        """
        Core dispatching logic to find the appropriate implementation.

        :param obj: The object being dispatched
        :return: The most appropriate implementation function
        :raises AttributeError: If the specified attribute doesn't exist
        """
        # Verify that the object has the specified attribute
        if not hasattr(obj, attr_name):
            raise AttributeError(f"Object does not have attribute '{attr_name}'")

        # Extract the value of the specified attribute
        attr_value = getattr(obj, attr_name)

        # Look for an exact match of the attribute value in our registry
        if attr_value in registry:
            return registry[attr_value]

        # If no specific implementation is found, fall back to the default implementation
        return func

    def register(attr_value, implementation=None):
        """
        Register a specific implementation for a given attribute value.

        :param attr_value: The attribute value to match
        :param implementation: The function to use for this attribute value
        :return: Decorator or registered function
        """
        # If no implementation is provided, return a lambda
        if implementation is None:
            return lambda f: register(attr_value, f)

        # Store the implementation in the registry
        registry[attr_value] = implementation
        return implementation

    def wrapper(*args, **kwargs):
        """
        The main wrapper function that orchestrates the dispatching.

        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: Result of the dispatched function
        :raises TypeError: If no arguments are provided
        """
        # Ensure at least one argument is passed
        if not args:
            raise TypeError(f"{func.__name__} requires at least 1 positional argument")

        # Dispatch based on the first argument's attribute
        try:
            implementation = dispatch(args[0])
            return implementation(*args, **kwargs)
        except Exception as e:
            # Enhanced error handling to provide more context
            raise TypeError(
                f"Error in {func.__name__} "
                f"with {attr_name}={getattr(args[0], attr_name, 'UNKNOWN')}. "
                f"Original error: {e!s}"
            ) from e

    # Attach additional methods and metadata to the wrapper
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)

    # Preserve the metadata of the original function
    functools.update_wrapper(wrapper, func)

    return wrapper


def attribute_dispatch_base(
    func: Callable, attr_name: str, attr_value: Any
) -> NoReturn:
    """
    Raise a TypeError with information about supported attribute values.

    Args:
        func: The function being dispatched
        attr_name: Name of the attribute being dispatched on
        attr_value: The unsupported attribute value that was encountered

    Raises:
        TypeError: Always, with details about supported values
    """
    registry = func.registry
    supported_values = ", ".join(registry.keys())
    raise TypeError(
        f"`{func.__name__}` called for unsupported value '{attr_value}' for attribute '{attr_name}'. "
        f"Supported values are: {supported_values}"
    )
