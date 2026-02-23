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

"""Shared functions for the workflows."""

from collections.abc import Callable, Generator
from typing import Any, TypeVar, cast

from orchestrator.db import (
    ProductBlockTable,
    ProductTable,
    ResourceTypeTable,
    SubscriptionInstanceRelationTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
)
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import ConfigDict
from pydantic_forms.core import FormPage
from pydantic_forms.validators import (
    Choice,
    MigrationSummary,
    choice_list,
    migration_summary,
)

T = TypeVar("T")


def subscriptions_by_product_type(product_type: str, status: list[SubscriptionLifecycle]) -> list[SubscriptionTable]:
    """
    retrieve_subscription_list_by_product This function lets you retrieve a
    list of all subscriptions of a given product type. For example, you could
    call this like so:

    >>> subscriptions_by_product_type("Node", [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING])
        [SubscriptionTable(su...note=None), SubscriptionTable(su...note=None)]

    You now have a list of all active Node subscription instances and can then
    use them in your workflow.

    Args:
        product_type (str): The product type in the DB (i.e. Node, User, etc.)
        status (List[SubscriptionLifecycle]): The lifecycle states you want returned (i.e. SubscriptionLifecycle.ACTIVE)

    Returns:
        List[SubscriptionTable]: A list of all the subscriptions that match
            your criteria.
    """  # noqa: D415
    return (
        SubscriptionTable.query.join(ProductTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )


def subscriptions_by_product_type_and_instance_value(
    product_type: str,
    resource_type: str,
    value: str,
    status: list[SubscriptionLifecycle],
) -> list[SubscriptionTable]:
    """Retrieve a list of Subscriptions by product_type, resource_type and value.

    Args:
        product_type: type of subscriptions
        resource_type: name of the resource type
        value: value of the resource type
        status: lifecycle status of the subscriptions

    Returns:
        list[SubscriptionTable]: List of matching subscriptions.
    """
    return (
        SubscriptionTable.query.join(ProductTable)
        .join(SubscriptionInstanceTable)
        .join(SubscriptionInstanceValueTable)
        .join(ResourceTypeTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionInstanceValueTable.value == value)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )


def summary_form(product_name: str, summary_data: dict) -> Generator:
    """Generate a summary form for the product."""

    class SummaryForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} summary")

        product_summary: cast(type[MigrationSummary], migration_summary(summary_data))  # type: ignore[valid-type]

    yield SummaryForm


def create_summary_form(user_input: dict, product_name: str, fields: list[str]) -> Generator:
    """Create a summary form for the product."""
    columns = [[str(user_input[nm]) for nm in fields]]
    yield from summary_form(product_name, {"labels": fields, "columns": columns})


def modify_summary_form(user_input: dict, block: ProductBlockModel, fields: list[str]) -> Generator:
    """Modify the summary form for the product."""
    before = [str(getattr(block, nm)) for nm in fields]
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
    """
    Create a `Choice` selector for subscriptions of a given product type.

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
    single_choice_func: Callable[..., Choice],
    *args: Any,
    **kwargs: Any,
) -> type[list[Choice]]:
    """
    Convert a single choice function into a multiple choice list.

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


def subscription_instances_by_block_type_and_resource_value(
    product_block_type: str,
    resource_type: str,
    resource_value: str,
    states: list[SubscriptionLifecycle] = [SubscriptionLifecycle.ACTIVE],  # noqa: B006
) -> list[SubscriptionInstanceTable]:
    """
    From the database, retrieve the subscription instances that match specific product block type and resource value.
    Usage example:
        >>> sis = subscription_instances_by_block_type_and_resource_value(
        ...     "OpticalDevicePort",
        ...     "port_name",
        ...     "ge-0/0/0",
        ...     [SubscriptionLifecycle.ACTIVE]
        ... )
        >>> for si in sis:
        ...     print(si.subscription_instance_id).

    This function finds subscription instances that:
    1. are instances of the product block of the specified type
    2. the value of the specified resource attribute matches the specified value
    3. Belong to a subscription in one of the specified lifecycle states

    Args:
        product_block_type: The name of the product block type (e.g., "OpticalDevicePort")
        resource_type: The name of the resource attribute (e.g., "port_name")
        resource_value: The specific value to match (e.g., "ge-0/0/0")
        states: List of subscription lifecycle states to include in the search

    Returns:
        List of SubscriptionInstanceTable objects (i.e. entries of the subscription_instances table in the DB)
            matching all criteria
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionInstanceValueTable)
        .join(ResourceTypeTable)
        .join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name == product_block_type)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .filter(SubscriptionInstanceValueTable.value == resource_value)
        .all()
    )


def subscription_instance_values_by_block_type_depending_on_instance_id(
    product_block_type: str,
    resource_type: str,
    depending_on_instance_id: str,
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceValueTable]:
    """
    This function retrieves a list of all subscription instance values (i.e. product block attributes, e.g. port_name)
    of a specific product block type (e.g. OpticalDevicePort) that depend on the given instance id
    (e.g. OpticalDeviceBlock of flex.ba01 subscription instance id) and whose owner subscription
    (e.g. OpticalFiber flex.ba01---flex.mt00 might own an optical port of flex.ba01)
    is in the specified lifecycle states.

    For example:
    >>> an_optical_device_instance_id = an_optical_device_subscription.optical_device.subscription_instance_id
    >>> subscription_instances_values = subscription_instances_of_type_that_depends_on(
            "OpticalDevicePort",
            "port_name",
            an_optical_device_instance_id,
            [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING]
        )
    [SubscriptionInstanceValueTable(su...value=xe-0/0/0), SubscriptionInstanceValueTable(su...value=et-1/0/0)]
                                               ^^^^^^^^                                             ^^^^^^^^
    You now have a list of all rows from the subscription instance values table in the DB.
    Each row corresponds to a subscription instance that depends on "an_optical_device".
    Each of these instances also belongs to a subscription whose status is in one of the specified states.
    You can use these subscription instances in your workflow like this:
    >>> subscription_instance_id = subscription_instances_values[0].subscription_instance_id
    >>> optical_port_block = OpticalDevicePortBlock.from_db(subscription_instance_id)

    Args:
        product_block_type (str): The product block type in the DB (i.e. product name, e.g. OpticalDevicePort)
        resource_type (str): The resource type in the DB (i.e. product block attribute name, e.g. port_name, etc.)
        depending_on_instance_id (str): The subscription_instance_id of theproduct block that the returned product
            blocks depend on.
        states (List[SubscriptionLifecycle]): The lifecycle states you want returned (i.e. SubscriptionLifecycle.ACTIVE)

    Returns:
        List[SubscriptionInstanceValueTable]: A list of all the subscription instance values that match your criteria.
    """
    return (
        SubscriptionInstanceValueTable.query.join(
            SubscriptionInstanceTable,
            SubscriptionInstanceTable.subscription_instance_id
            == SubscriptionInstanceValueTable.subscription_instance_id,
        )
        .join(
            SubscriptionInstanceRelationTable,
            SubscriptionInstanceTable.subscription_instance_id == SubscriptionInstanceRelationTable.in_use_by_id,
        )
        .join(
            SubscriptionTable,
            SubscriptionInstanceTable.subscription_id == SubscriptionTable.subscription_id,
        )
        .join(
            ProductBlockTable,
            SubscriptionInstanceTable.product_block_id == ProductBlockTable.product_block_id,
        )
        .join(
            ResourceTypeTable,
            SubscriptionInstanceValueTable.resource_type_id == ResourceTypeTable.resource_type_id,
        )
        .filter(SubscriptionInstanceRelationTable.depends_on_id == depending_on_instance_id)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name == product_block_type)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .all()
    )


def active_blocks_of_type_depending_on_other_block_selector(
    product_block_type: str,
    sort_product_blocks_by_attribute_name: str,
    depending_on_product_block: ProductBlockModel,
    prompt: str | None = None,
) -> type[Choice]:
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

    return Choice(f"{prompt}", zip(product_blocks.keys(), product_blocks.items(), strict=False))


def active_blocks_of_type_depending_on_other_block_multiple_selector(
    product_block_type: str,
    sort_product_blocks_by_attribute_name: str,
    depending_on_product_block: ProductBlockModel,
    min_items: int,
    max_items: int | None,
    unique_items: bool,  # noqa: FBT001
    prompt: str | None = None,
) -> type[list[Choice]]:
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
