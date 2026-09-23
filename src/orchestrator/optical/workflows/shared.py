"""Shared functions for the workflows.

This module hosts the form-layer helpers of the workflows: the summary form
generators and the ``Choice`` selectors. Database queries live in the neutral
``orchestrator/optical/db.py`` module, which the selectors import from.
"""

from collections.abc import Callable, Generator, Sequence
from typing import Any, cast

from pydantic import ConfigDict
from pydantic_forms.core import FormPage
from pydantic_forms.types import SummaryData
from pydantic_forms.validators import (
    Choice,
    choice_list,
    migration_summary,
)

from orchestrator.core.db import SubscriptionInstanceTable, db
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import (
    subscription_instance_values_by_block_type_depending_on_instance_id,
    subscription_instances_by_block_names,
    subscription_instances_by_block_types_and_resource_values,
)
from orchestrator.optical.hal.port import get_device_ports_by_role
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockInactive
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole


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


def summary_form(product_name: str, summary_data: SummaryData) -> Generator:
    """Generate a summary form for the product."""

    class SummaryForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} summary")

        product_summary: migration_summary(summary_data)  # type: ignore[valid-type]

    yield SummaryForm


def create_summary_form(
    user_input: dict,
    product_name: str,
    fields: list[str],
    extra_summary_fields: Sequence[str] = (),
) -> Generator:
    """Create a summary form for the product."""
    fields = merge_summary_fields(fields, extra_summary_fields, user_input)
    columns: list[list[str | int | bool | float]] = [[str(user_input[nm]) for nm in fields]]
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
    before: list[str | int | bool | float] = []
    for nm in fields:
        if extra_before and nm in extra_before:
            before.append(extra_before[nm])
        elif hasattr(block, nm):
            before.append(str(getattr(block, nm)))
        else:
            before.append("")
    after: list[str | int | bool | float] = [str(user_input[nm]) for nm in fields]
    subscription = block.subscription
    if subscription is None:
        msg = f"Block {block.subscription_instance_id} has no subscription"
        raise ValueError(msg)
    yield from summary_form(
        subscription.product.name,
        {
            "labels": fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )


def active_instance_selector_by_block_type(
    abstract_block_type: type[ProductBlockModel],
    prompt: str | None = None,
    resource_values: dict[str, str | list[str] | set[str]] | None = None,
) -> type[Choice]:
    """Create a `Choice` selector for the blocks of any product implementing an abstract block type.

    The same block-filtered contract as the former subscription-id twin (every
    concrete block class inheriting from the abstract block registers its
    product block name in ``__names__``), but option values are the block
    subscription instance ids — never subscription ids or models. Labels are
    the owner subscriptions' descriptions, so the selector works for any
    current or future block family without knowing its fields.

    Args:
        abstract_block_type: The abstract product block type of the contract (e.g.
            ``OpticalModuleLocationBlockInactive``).
        prompt: Prompt to display in the selection. If not provided, a default prompt
            will be generated.
        resource_values: Optional mapping of stored resource type to acceptable
            value(s), restricting the offered blocks (e.g.
            ``{"optical_node_role": ["ROADM"]}``). The filter runs in the
            database query; None (default) offers every active block.

    Returns:
        type[Choice]: A `Choice` class configured with the block options of all
        the products that implement the given abstract block type.
    """
    if resource_values:
        instances = subscription_instances_by_block_types_and_resource_values(
            abstract_block_type.__names__, resource_values, [SubscriptionLifecycle.ACTIVE]
        )
    else:
        instances = subscription_instances_by_block_names(abstract_block_type.__names__, [SubscriptionLifecycle.ACTIVE])
    options = []
    for instance in instances:
        description = instance.subscription.description if instance.subscription is not None else ""
        options.append((str(instance.subscription_instance_id), description))
    products = dict(sorted(options, key=lambda item: item[1]))

    if not prompt:
        prompt = f"Select a {abstract_block_type.__name__}"

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
    subscription_instance_id = str(depending_on_product_block.subscription_instance_id)
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


#: Optical Port block types whose ``optical_port_name`` marks a device port as in
#: use by a pipe, spectrum or transport channel subscription.
PORT_BLOCK_TYPES = [
    "OlsLinePortBlock",
    "OlsAddDropPortBlock",
    "OpticalTransponderClientPortBlock",
    "OpticalTransponderLinePortBlock",
]


def used_port_names_on_node(
    node_block: AbstractOpticalNodeBlockInactive,
    *,
    exclude_subscription_id: str | None = None,
) -> set[str]:
    """Return the names of the ports of a node that are already used by other subscriptions.

    The port blocks of all pipe, spectrum and transport channel subscriptions are
    stored in the database as instances that depend on the Optical Node block of the
    node that hosts them; this function collects the ``optical_port_name`` of all of
    them. Subscriptions being created (INITIAL) count as users, so two concurrent
    creates cannot book the same port name.

    Args:
        node_block: Optical Node block of the node to check.
        exclude_subscription_id: Subscription id whose own port blocks are not
            considered in use (e.g. the subscription being modified).

    Returns:
        The set of port names of the node that are in use by other subscriptions.
    """
    used_ports: set[str] = set()
    for block_type in PORT_BLOCK_TYPES:
        instance_values = subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type=block_type,
            resource_type="optical_port_name",
            depending_on_instance_id=str(node_block.subscription_instance_id),
            states=[
                SubscriptionLifecycle.INITIAL,
                SubscriptionLifecycle.ACTIVE,
                SubscriptionLifecycle.PROVISIONING,
            ],
        )
        for instance_value in instance_values:
            if exclude_subscription_id is not None:
                instance = db.session.get(SubscriptionInstanceTable, instance_value.subscription_instance_id)
                if instance is not None and str(instance.subscription_id) == exclude_subscription_id:
                    continue
            used_ports.add(str(instance_value.value))
    return used_ports


def optical_port_selector(
    optical_node_block: AbstractOpticalNodeBlockInactive,
    roles: list[OpticalPortRole] | None = None,
    prompt: str | None = None,
    *,
    exclude_in_use: bool = True,
) -> type[Choice]:
    """Create a ``Choice`` selector for the ports of an Optical Node of the given roles.

    This is the single port selector of the module: the ports are enumerated from
    the device by their Optical Port role (``None`` selects every role the node's
    vendor/platform supports) and, by default, the ports already in use by another
    subscription are excluded.

    Args:
        optical_node_block: Optical Node block hosting the ports.
        roles: The Optical Port roles to offer. ``None`` (the default) offers every
            role the node's vendor/platform supports.
        prompt: Prompt of the selector. When omitted, a default prompt is generated.
        exclude_in_use: When True (the default), ports already used by another
            subscription are not offered.

    Returns:
        A ``Choice`` class whose value and label are the device port name.

    Raises:
        UnsupportedPortRoleError: If a requested role is not supported by the node's vendor/platform.
        UnsupportedPlatformError: If the Optical Node is not supported by this operation.
    """
    ports = get_device_ports_by_role(cast(AnyOpticalNodeBlockProvisioningUnion, optical_node_block), roles)
    if exclude_in_use:
        used_ports = used_port_names_on_node(optical_node_block)
        ports = [port for port in ports if port not in used_ports]
    if not prompt:
        prompt = f"Select a port on {optical_node_block.management.optical_module_node_fqdn}"
    return cast(type[Choice], Choice(prompt, zip(ports, ports, strict=False)))
