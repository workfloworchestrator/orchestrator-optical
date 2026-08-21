"""Shared functions for the workflows."""

from collections.abc import Callable, Generator, Sequence
from typing import Any, TypeVar, cast

from pydantic import ConfigDict
from pydantic_forms.core import FormPage
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import (
    Choice,
    MigrationSummary,
    choice_list,
    migration_summary,
)

from orchestrator.core.db import (
    ProductBlockTable,
    ProductTable,
    ResourceTypeTable,
    SubscriptionInstanceRelationTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
)
from orchestrator.core.domain import SUBSCRIPTION_MODEL_REGISTRY, SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle

T = TypeVar("T")
S = TypeVar("S", bound=SubscriptionModel)


def subscriptions_by_product_type(product_type: str, status: list[SubscriptionLifecycle]) -> list[SubscriptionTable]:
    """Retrieve_subscription_list_by_product.

    This function lets you retrieve a list of all subscriptions of a
    given product type. For example, you could call this like so:

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
    """
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


def subscription_from_subscription[S: SubscriptionModel](abstract_model_type: type[S], subscription_id: UUIDstr) -> S:
    """Load a subscription through the concrete model class implementing an abstract subscription model.

    The abstract subscription model is a contract between the developers of this package
    and the users that implement concrete products: calling ``from_subscription`` on the
    abstract class itself cannot work, because the abstract root block name never matches
    the concrete product block stored in the database. The concrete model class is
    therefore resolved through the subscription model registry, like
    ``node_block_from_subscription`` does for Optical Nodes.

    Args:
        abstract_model_type: The abstract subscription model type of the contract (e.g.
            ``AbstractOpticalLocationInactive``).
        subscription_id: Subscription id of the subscription to load.

    Returns:
        The loaded subscription model, cast to the abstract model type.

    Raises:
        ValueError: If the subscription is not a known product or its product does not
            implement the given abstract model type.
    """
    subscription = SubscriptionTable.query.filter(SubscriptionTable.subscription_id == subscription_id).one()
    model_class = SUBSCRIPTION_MODEL_REGISTRY.get(subscription.product.name)
    if model_class is None or not issubclass(model_class, abstract_model_type):
        msg = f"Subscription {subscription_id} is not a {abstract_model_type.__name__} subscription"
        raise ValueError(msg)
    return cast(S, model_class.from_subscription(subscription_id))


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


def subscription_instances_by_block_type(
    product_block_type: str,
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Retrieve the subscription instances that match a specific product block type.

    Args:
        product_block_type: The name of the product block type (e.g., "NokiaFlexIlsBlock").
        states: List of subscription lifecycle states the owner subscription must be in.

    Returns:
        List of SubscriptionInstanceTable entries (i.e. rows of the subscription_instances table)
            whose product block type matches and whose owner subscription is in one of the given states.
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name == product_block_type)
        .all()
    )


def subscription_instances_by_block_type_and_resource_value(
    product_block_type: str,
    resource_type: str,
    resource_value: str,
    states: list[SubscriptionLifecycle] = [SubscriptionLifecycle.ACTIVE],  # noqa: B006
) -> list[SubscriptionInstanceTable]:
    """From the database, retrieve the subscription instances that match specific product block type and resource value.

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
    """Retrieve subscription instance values of a block type depending on another instance.

    This function retrieves a list of all subscription instance values (i.e. product block attributes, e.g.
    port_name) of a specific product block type (e.g. OpticalDevicePort) that depend on the given instance id
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
