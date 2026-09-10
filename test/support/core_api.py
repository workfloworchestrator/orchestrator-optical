"""Shim over the private orchestrator-core internals used by the tests.

The composition tests reach into private orchestrator-core attributes: the
undecorated function behind a workflow step and the product-block field
classification computed by ``ProductBlockModel``. Centralizing those accesses
here keeps a future orchestrator-core bump to a single file.
"""

from collections.abc import Iterable
from typing import Any, cast


def unwrap_step(step: Any) -> Any:
    """Return the undecorated function wrapped by a workflow step object."""
    return cast(Any, step).__wrapped__


def step_functions(steps: Iterable[Any]) -> list[Any]:
    """Return the undecorated functions of a sequence of workflow step objects."""
    return [unwrap_step(step) for step in steps]


def product_block_fields(cls: type) -> dict[str, Any]:
    """Return the product-block field names mapped to their block classes."""
    return cast(Any, cls)._product_block_fields_


def non_product_block_fields(cls: type) -> dict[str, Any]:
    """Return the scalar (non product-block) field names mapped to their types."""
    return cast(Any, cls)._non_product_block_fields_
