"""Resolution of the user-defined customer choice function.

The ``customer_id`` of every subscription created or modified by the workflows of
this package is chosen by the end user through a ``Choice`` selector. Which
subscriptions qualify as customers is deployment-specific, so the function that
builds the selector must be defined in the user code-space and wired up either
through the ``OPTICAL_CUSTOMER_CHOICE`` setting (``module.path:function_name``)
or by calling :func:`register_customer_choice` at application startup.
"""

from collections.abc import Callable
from functools import lru_cache
from importlib import import_module
from typing import cast

from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.optical.settings import get_settings

CustomerChoiceFunction = Callable[[], type[Choice]]

# Module-level registry instead of a module global to keep the linter happy:
# the registered function takes precedence over the OPTICAL_CUSTOMER_CHOICE setting.
_registered_customer_choice: dict[str, CustomerChoiceFunction] = {}

_NOT_CONFIGURED_MSG = (
    "No customer choice function is configured. Set the OPTICAL_CUSTOMER_CHOICE "
    "environment variable to 'module.path:function_name' or call "
    "register_customer_choice() before generating forms."
)


def register_customer_choice(customer_choice: CustomerChoiceFunction) -> None:
    """Register the user-defined customer choice function.

    Takes precedence over the ``OPTICAL_CUSTOMER_CHOICE`` setting. Call it once at
    application startup, e.g. from the user code-space module that defines the
    function.

    Args:
        customer_choice: Callable returning a ``type[Choice]`` whose option values
            are the customer ids to be set as the subscription ``customer_id``.
    """
    _registered_customer_choice["customer_choice"] = customer_choice


@lru_cache
def _customer_choice_from_settings() -> CustomerChoiceFunction:
    """Import the customer choice function from the ``OPTICAL_CUSTOMER_CHOICE`` setting."""
    import_path = get_settings().customer_choice
    if not import_path:
        msg = _NOT_CONFIGURED_MSG
        raise ValueError(msg)
    module_path, separator, attribute = import_path.partition(":")
    if not separator or not attribute:
        msg = f"OPTICAL_CUSTOMER_CHOICE must be 'module.path:function_name', got {import_path!r}"
        raise ValueError(msg)
    try:
        module = import_module(module_path)
    except ModuleNotFoundError as exc:
        msg = f"Could not import {module_path!r} from OPTICAL_CUSTOMER_CHOICE: {exc}"
        raise ValueError(msg) from exc
    try:
        customer_choice = getattr(module, attribute)
    except AttributeError as exc:
        msg = f"OPTICAL_CUSTOMER_CHOICE attribute {attribute!r} not found in module {module_path!r}"
        raise ValueError(msg) from exc
    return customer_choice


def _customer_choice_function() -> CustomerChoiceFunction:
    if _registered_customer_choice:
        return _registered_customer_choice["customer_choice"]
    return _customer_choice_from_settings()


def customer_choice_selector(include: UUIDstr | None = None) -> type[Choice]:
    """Create a ``Choice`` selector for the customer of a subscription.

    The selector is built by the user-defined customer choice function (see
    :func:`register_customer_choice`); its option values are the customer ids to
    be passed as the subscription ``customer_id``.

    Args:
        include: Optional customer id that must be present among the options even
            if it is not returned by the user function, e.g. the current customer
            of a subscription being modified. It is shown as "current customer".

    Returns:
        type[Choice]: A ``Choice`` class configured with the customer options.

    Raises:
        ValueError: If no customer choice function is configured.
        TypeError: If the configured function does not return a ``type[Choice]``.
    """
    customer_choice = _customer_choice_function()
    choice = customer_choice()
    if not isinstance(choice, type):
        msg = f"customer choice function must return type[Choice], got {type(choice).__name__}"
        raise TypeError(msg)

    if include is not None:
        options = [(member.value, (member.value, member.label)) for member in choice.__members__.values()]
        if include not in {value for value, _ in options}:
            options.append((include, (include, "current customer")))
            choice = cast(type[Choice], Choice(choice.__name__, options))

    return choice
