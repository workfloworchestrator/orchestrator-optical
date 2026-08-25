"""Shared functions for the workflows.

This module hosts the form-layer helpers of the workflows: the summary form
generators and the ``Choice`` selectors. Database queries live in the neutral
``orchestrator/optical/db.py`` module, which the selectors import from.
"""

from collections.abc import Callable, Generator, Sequence
from typing import Any, cast

from pydantic import ConfigDict
from pydantic_forms.core import FormPage
from pydantic_forms.validators import (
    Choice,
    MigrationSummary,
    choice_list,
    migration_summary,
)

from orchestrator.core.db import ProductBlockTable, SubscriptionInstanceTable, SubscriptionTable
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import (
    subscription_instance_values_by_block_type_depending_on_instance_id,
    subscriptions_by_product_type,
    subscriptions_by_product_type_and_instance_value,
)


def merge_summary_fields(
    summary_fields: list[str],
    extra_summary_fields: Sequence[str],
    user_input: dict[str, Any],
) -> list[str]:
    """Append user-defined extra field names to a summary field list.

    Extra form pages declared by the user add their field names to the form
    input; this helper adds them to the summary and fails fast when a name
    does not exist in the collected input.

    Args:
        summary_fields: The shipped summary field names.
        extra_summary_fields: Extra field names to append to the summary.
        user_input: The collected form input, used to validate the names.

    Returns:
        The combined summary field names.

    Raises:
        ValueError: If an extra field name is not present in the form input.
    """
    unknown = [name for name in extra_summary_fields if name not in user_input]
    if unknown:
        msg = f"extra_summary_fields not present in the form input: {', '.join(unknown)}"
        raise ValueError(msg)
    return summary_fields + list(extra_summary_fields)


def summary_form(product_name: str, summary_data: dict) -> Generator:
    """Generate a summary form for the product."""

    class SummaryForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} summary")

        product_summary: cast(type[MigrationSummary], migration_summary(summary_data))  # type: ignore[valid-type]

    yield SummaryForm


def create_summary_form(
    user_input: dict,
    product_name: str,
    fields: list[str],
    extra_summary_fields: Sequence[str] = (),
) -> Generator:
    """Create a summary form for the product."""
    fields = merge_summary_fields(fields, extra_summary_fields, user_input)
    columns = [[str(user_input[nm]) for nm in fields]]
    yield from summary_form(product_name, {"labels": fields, "columns": columns})


def modify_summary_form(
    user_input: dict,
    block: ProductBlockModel,
    fields: list[str],
    extra_before: dict[str, str] | None = None,
    extra_summary_fields: Sequence[str] = (),
) -> Generator:
    """Modify the summary form for the product.

    Args:
        user_input: Form input values for the "after" column.
        block: Product block of the subscription being modified.
        fields: Field names to display.
        extra_before: Optional mapping of field names to "before" values that cannot
            be read from the block, e.g. the subscription customer id.
        extra_summary_fields: Extra field names to append to the summary; their
            "before" column is left empty, as they have no previous value.
    """
    fields = merge_summary_fields(fields, extra_summary_fields, user_input)
    before = []
    for nm in fields:
        if extra_before and nm in extra_before:
            before.append(extra_before[nm])
        elif hasattr(block, nm):
            before.append(str(getattr(block, nm)))
        else:
            before.append("")
    after = [str(user_input[nm]) for nm in fields]
    yield from summary_form(
        block.subscription.product.name,
        {
            "labels": fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )


def active_subscription_selector(product_type: str, prompt: str | None = None) -> type[Choice]:
    """Create a `Choice` selector for subscriptions of a given product type.

    Args:
        product_type (str): The type of product to filter subscriptions by.
        prompt (str, optional): Prompt to display in the selection. If not provided,
            a default prompt will be generated.

    Returns:
        type[Choice]: A `Choice` class configured with subscription options
        for the specified product type.
    """
    subscriptions = subscriptions_by_product_type(product_type, [SubscriptionLifecycle.ACTIVE])

    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }

    if not prompt:
        prompt = f"Select a {product_type}"

    return Choice(f"{prompt}", zip(products.keys(), products.items(), strict=False))  # type:ignore  # noqa: PGH003


def active_subscription_selector_by_block_type(
    abstract_block_type: type[ProductBlockModel],
    prompt: str | None = None,
) -> type[Choice]:
    """Create a `Choice` selector for subscriptions of any product implementing an abstract block type.

    The abstract product block is a contract between the developers of this package and
    the users that implement concrete products: every concrete block class inheriting
    from it registers its own product block name in ``__names__`` at class definition
    time, so all the concrete implementations can be matched without knowing them
    upfront.

    Args:
        abstract_block_type: The abstract product block type of the contract (e.g.
            ``OpticalModuleLocationBlockInactive``).
        prompt: Prompt to display in the selection. If not provided, a default prompt
            will be generated.

    Returns:
        type[Choice]: A `Choice` class configured with subscription options for all the
        products that implement the given abstract block type.
    """
    subscriptions = (
        SubscriptionTable.query.join(SubscriptionInstanceTable)
        .join(ProductBlockTable)
        .filter(ProductBlockTable.name.in_(abstract_block_type.__names__))
        .filter(SubscriptionTable.status.in_([SubscriptionLifecycle.ACTIVE]))
        .distinct()
        .all()
    )

    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }

    if not prompt:
        prompt = f"Select a {abstract_block_type.__name__}"

    return Choice(f"{prompt}", zip(products.keys(), products.items(), strict=False))  # type:ignore  # noqa: PGH003


def active_subscription_with_instance_value_selector(
    product_type: str, resource_type: str, value: str, prompt: str | None = None
) -> type[Choice]:
    """Create a Choice selector for subscriptions filtered by product type and instance value.

    Args:
        product_type: The type of product to filter subscriptions by
        resource_type: The resource type to filter by
        value: The instance value to match
        prompt: Optional custom prompt text

    Returns:
        A Choice class configured with filtered subscription options
    """
    subscriptions = subscriptions_by_product_type_and_instance_value(
        product_type, resource_type, value, [SubscriptionLifecycle.ACTIVE]
    )

    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }

    if not prompt:
        prompt = f"Select a {product_type} with {resource_type}={value}"

    return Choice(f"{prompt}", zip(products.keys(), products.items(), strict=False))  # type:ignore  # noqa: PGH003


def single_choice_to_multiple_choices(
    min_items: int,
    max_items: int | None,
    unique_items: bool,  # noqa: FBT001
    single_choice_func: Callable[..., type[Choice]],
    *args: Any,
    **kwargs: Any,
) -> type[list[Choice]]:
    """Convert a single choice function into a multiple choice list.

    Args:
        min_items: Minimum number of selections required
        max_items: Maximum number of selections allowed (None for unlimited)
        unique_items: Whether duplicate selections are allowed
        single_choice_func: Function that returns a single Choice
        *args: Positional arguments to pass to single_choice_func
        **kwargs: Keyword arguments to pass to single_choice_func

    Returns:
        A Choice list type allowing multiple selections
    """
    base_choice = single_choice_func(*args, **kwargs)
    return choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items)


def active_blocks_of_type_depending_on_other_block_selector(
    product_block_type: str,
    sort_product_blocks_by_attribute_name: str,
    depending_on_product_block: ProductBlockModel,
    prompt: str | None = None,
) -> type[Choice]:
    """."""
    subscription_instance_id = depending_on_product_block.subscription_instance_id
    subscription_instance_values = subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type=product_block_type,
        resource_type=sort_product_blocks_by_attribute_name,
        depending_on_instance_id=subscription_instance_id,
        states=[SubscriptionLifecycle.ACTIVE],
    )

    product_blocks = {
        str(siv.subscription_instance_id): siv.value
        for siv in sorted(subscription_instance_values, key=lambda x: x.value)
    }

    if not prompt:
        prompt = f"Select a {product_block_type}"

    dynamic_class = Choice(f"{prompt}", zip(product_blocks.keys(), product_blocks.items(), strict=False))
    return cast(type[Choice], dynamic_class)


def active_blocks_of_type_depending_on_other_block_multiple_selector(
    product_block_type: str,
    sort_product_blocks_by_attribute_name: str,
    depending_on_product_block: ProductBlockModel,
    min_items: int,
    max_items: int | None,
    unique_items: bool,  # noqa: FBT001
    prompt: str | None = None,
) -> type[list[Choice]]:
    """."""
    return single_choice_to_multiple_choices(
        min_items,
        max_items,
        unique_items,
        active_blocks_of_type_depending_on_other_block_selector,
        product_block_type,
        sort_product_blocks_by_attribute_name,
        depending_on_product_block,
        prompt=prompt,
    )
