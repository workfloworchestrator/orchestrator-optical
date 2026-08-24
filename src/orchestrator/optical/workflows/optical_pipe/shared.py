"""Shared workflow utilities for optical pipes."""

from collections.abc import Generator, Sequence
from typing import Annotated, Any, TypeVar, cast
from uuid import UUID

from pydantic import ConfigDict, Field
from pydantic_forms.core import FormPage
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice, MigrationSummary, choice_list, migration_summary

from orchestrator.core.db import ProductTable, SubscriptionTable, db
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel, ProductModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.hal.optical_node import Vendor, vendor_of
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import AbstractOpticalPipeBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.abstracts import AbstractOpticalPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_line import (
    OpticalTransponderLinePortBlockInactive,
)
from orchestrator.optical.products.product_types.optical_node.abstracts import AbstractOpticalNodeInactive
from orchestrator.optical.workflows.optical_node.shared import OPTICAL_NODE_PRODUCT_TYPES
from orchestrator.optical.workflows.shared import (
    merge_summary_fields,
    subscription_from_subscription,
    subscription_instance_values_by_block_type_depending_on_instance_id,
)

T = TypeVar("T", bound=AbstractOpticalPortBlockInactive)

PORT_BLOCK_TYPES = [
    "OlsLinePortBlock",
    "OlsAddDropPortBlock",
    "OpticalTransponderClientPortBlock",
    "OpticalTransponderLinePortBlock",
]


def optical_pipe_subscription_description(subscription: SubscriptionModel) -> str:
    """Generate a standard description for an optical pipe subscription."""
    pipe = getattr(subscription, "optical_pipe", None)
    if pipe and getattr(pipe, "optical_pipe_name", None):
        return f"{pipe.optical_pipe_name} ({subscription.product.name})"
    return subscription.product.name


def active_subscriptions_by_product_type(product_type: str) -> list[SubscriptionTable]:
    """Retrieve all active subscriptions of a given product type."""
    return (
        SubscriptionTable.query.join(SubscriptionTable.product)
        .filter(SubscriptionTable.product.has(product_type=product_type))
        .filter(SubscriptionTable.status == SubscriptionLifecycle.ACTIVE)
        .all()
    )


def optical_pipe_selector(product_type: str, prompt: str | None = None) -> type[Choice]:
    """Create a Choice selector for active optical pipe subscriptions of a given product type."""
    subscriptions = active_subscriptions_by_product_type(product_type)
    products = {str(sub.subscription_id): sub.description for sub in sorted(subscriptions, key=lambda x: x.description)}

    if not prompt:
        prompt = f"Select an {product_type}"

    dynamic_class = Choice(prompt, zip(products.keys(), products.items(), strict=False))
    return cast(type[Choice], dynamic_class)


def multiple_optical_pipe_selector(
    product_type: str,
    prompt: str = "Select optical pipes",
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
) -> type[list[Choice]]:
    """Selector for multiple optical pipe subscriptions."""
    base_choice = optical_pipe_selector(product_type, prompt)
    dynamic_class = choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items)
    return Annotated[dynamic_class, Field(title=prompt)]  # type: ignore[valid-type]


def summary_form(product_name: str, summary_data: dict[str, Any]) -> Generator[type[FormPage]]:
    """Generate a migration summary form."""

    class SummaryForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} summary")

        product_summary: cast(type[MigrationSummary], migration_summary(summary_data))  # type: ignore[valid-type]

    yield SummaryForm


def create_pipe_summary_form(
    user_input: dict[str, Any],
    product_name: str,
    fields: list[str],
    extra_summary_fields: Sequence[str] = (),
) -> Generator[type[FormPage]]:
    """Create a summary form for pipe creation."""
    fields = merge_summary_fields(fields, extra_summary_fields, user_input)
    columns = [[str(user_input.get(nm, "")) for nm in fields]]
    yield from summary_form(product_name, {"labels": fields, "columns": columns})


def modify_pipe_summary_form(
    user_input: dict[str, Any],
    block: ProductBlockModel,
    fields: list[str],
    extra_before: dict[str, str] | None = None,
    extra_summary_fields: Sequence[str] = (),
) -> Generator[type[FormPage]]:
    """Create a summary form for pipe modification.

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
        else:
            before.append(str(getattr(block, nm, "")))
    after = [str(user_input.get(nm, "")) for nm in fields]
    subscription = block.subscription
    if subscription is None:
        msg = "Cannot generate a summary form for a block without a subscription"
        raise ValueError(msg)
    yield from summary_form(
        subscription.product.name,
        {
            "labels": fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )


def optical_node_selector(prompt: str = "Select an Optical Node") -> type[Choice]:
    """Create a Choice selector for active Optical Node subscriptions of any vendor."""
    subscriptions: list[SubscriptionTable] = []
    for product_type in OPTICAL_NODE_PRODUCT_TYPES:
        subscriptions.extend(active_subscriptions_by_product_type(product_type))

    products = {str(sub.subscription_id): sub.description for sub in sorted(subscriptions, key=lambda x: x.description)}
    return cast(type[Choice], Choice(prompt, zip(products.keys(), products.items(), strict=False)))


def node_block_from_subscription(node_subscription_id: UUIDstr) -> AbstractOpticalNodeBlockInactive:
    """Return the Optical Node product block of the given node subscription.

    The concrete subscription model is resolved through the subscription model registry,
    because the abstract Optical Node model cannot load a subscription: its root block
    type has no product block name, so the concrete node block is never matched during
    loading.

    Args:
        node_subscription_id: Subscription id of an active Optical Node subscription.

    Returns:
        The Optical Node product block of the subscription.

    Raises:
        ValueError: If the subscription is not an Optical Node subscription.
    """
    node_subscription = subscription_from_subscription(AbstractOpticalNodeInactive, node_subscription_id)
    return node_subscription.optical_node


def used_port_names_on_node(node_block: AbstractOpticalNodeBlockInactive) -> set[str]:
    """Return the names of the ports of a node that are already used by other subscriptions.

    The port blocks of all pipe, spectrum and transport channel subscriptions are stored
    in the database as instances that depend on the Optical Node block of the node that
    hosts them; this function collects the ``optical_port_name`` of all of them.

    Args:
        node_block: Optical Node block of the node to check.

    Returns:
        The set of port names of the node that are in use by other subscriptions.
    """
    used_ports: set[str] = set()
    for block_type in PORT_BLOCK_TYPES:
        instance_values = subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type=block_type,
            resource_type="optical_port_name",
            depending_on_instance_id=str(node_block.subscription_instance_id),
            states=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
        )
        used_ports.update(str(instance_value.value) for instance_value in instance_values)
    return used_ports


def unused_node_port_selector(
    node_subscription_id: UUIDstr,
    ports: list[str],
    prompt: str | None = None,
) -> type[Choice]:
    """Create a Choice selector for the unused ports of a node subscription.

    The value of each choice is the port name; the label is ``"<pqdn> <port name>"``.

    Args:
        node_subscription_id: Subscription id of the Optical Node hosting the ports.
        ports: The port names of the node to select from.
        prompt: Optional prompt for the selector.

    Returns:
        A Choice class configured with the unused ports of the node.
    """
    node_block = node_block_from_subscription(node_subscription_id)
    used_ports = used_port_names_on_node(node_block)
    unused_ports = [port for port in ports if port not in used_ports]

    if not prompt:
        prompt = f"Select an unused port on {node_block.pqdn}"
    options = {port: f"{node_block.pqdn} {port}" for port in unused_ports}
    return cast(type[Choice], Choice(prompt, zip(options.keys(), options.items(), strict=False)))


def patch_port_block_class(
    host_node_block: AbstractOpticalNodeBlockInactive,
    port_name: str,
    client_ports: list[str],
) -> type[AbstractOpticalPortBlockInactive]:
    """Return the Fiber Patch port block class for a port of a node.

    The ports of the client enumeration of a Nokia FlexILS node are its OLS add/drop
    (SCG) ports, while on Groove G30 and GX G42 nodes they are transponder client
    ports. FlexILS OTS ports are OLS line ports, which are not part of the Fiber
    Patch port block union: they are never offered by the patch port selector and,
    if selected anyway, they map to the transponder line port block. All the other
    enumerated ports are line ports and are mapped to the transponder line port block.

    Args:
        host_node_block: Optical Node block hosting the port.
        port_name: The name of the port to map.
        client_ports: The names of the client ports of the node.

    Returns:
        The inactive port block class to use for the port.
    """
    if port_name in client_ports:
        if vendor_of(host_node_block) == Vendor.FLEXILS:
            return OlsAddDropPortBlockInactive
        return OpticalTransponderClientPortBlockInactive
    return OpticalTransponderLinePortBlockInactive


def leased_spectrum_port_block_class(
    host_node_block: AbstractOpticalNodeBlockInactive,
    port_name: str,
    client_ports: list[str],
) -> type[AbstractOpticalPortBlockInactive]:
    """Return the Leased Spectrum port block class for a port of a node.

    The ports of the client enumeration of a Nokia FlexILS node are its OLS add/drop
    (SCG) ports, while its line ports (OTS) are OLS line ports. Groove G30 and GX G42
    nodes only expose transponder line ports for leased spectrum subscriptions.

    Args:
        host_node_block: Optical Node block hosting the port.
        port_name: The name of the port to map.
        client_ports: The names of the client ports of the node.

    Returns:
        The inactive port block class to use for the port.
    """
    if vendor_of(host_node_block) != Vendor.FLEXILS:
        return OpticalTransponderLinePortBlockInactive
    if port_name in client_ports:
        return OlsAddDropPortBlockInactive
    return OlsLinePortBlockInactive


def new_pipe_port_block[T: AbstractOpticalPortBlockInactive](
    subscription_id: UUID,
    host_node_block: AbstractOpticalNodeBlockInactive,
    port_name: str,
    port_description: str,
    port_block_class: type[T],
) -> T:
    """Create a new Optical Port product block for a pipe termination.

    The host node block comes from an existing Optical Node subscription and is linked
    to the new port block as a foreign instance: saving the port block only records the
    relation to the node and never touches the node subscription itself.

    Args:
        subscription_id: Subscription id of the pipe subscription owning the port block.
        host_node_block: Optical Node block hosting the port.
        port_name: The name of the port on the device.
        port_description: Description of the port.
        port_block_class: The inactive port block class to instantiate.

    Returns:
        The created port block.
    """
    kwargs: dict[str, Any] = {
        "optical_port_name": port_name,
        "optical_port_host_node": host_node_block,
        "optical_port_description": port_description,
    }
    return port_block_class.new(subscription_id=subscription_id, **kwargs)


def new_optical_pipe_subscription(
    subscription_model: type[SubscriptionModel],
    product_id: UUIDstr,
    customer_id: str,
    pipe_block: AbstractOpticalPipeBlockInactive,
) -> SubscriptionModel:
    """Build a new pipe subscription model around a pre-built pipe block.

    ``from_product_id`` cannot be used for optical pipes: the placeholder terminations
    it creates cannot be validated, because the Optical Port blocks require a host node
    at construction time. The pipe block is therefore built first, with its two
    terminations already in place, and the subscription model is assembled from it.

    Args:
        subscription_model: The inactive subscription model of the pipe product.
        product_id: Id of the pipe product.
        customer_id: Customer (location subscription) id of the pipe.
        pipe_block: The pipe block with its two terminations.

    Returns:
        The new pipe subscription model in the INITIAL state.
    """
    product_db = db.session.get(ProductTable, product_id)
    if product_db is None:
        msg = f"Could not find a product for the given product_id {product_id}"
        raise KeyError(msg)

    product = ProductModel(
        product_id=product_db.product_id,
        name=product_db.name,
        description=product_db.description,
        product_type=product_db.product_type,
        tag=product_db.tag,
        status=product_db.status,
        created_at=product_db.created_at,
        end_date=product_db.end_date,
    )
    description = f"Initial subscription of {product_db.description}"
    subscription_id = pipe_block.owner_subscription_id
    subscription = SubscriptionTable(
        subscription_id=subscription_id,
        product_id=product_id,
        customer_id=customer_id,
        description=description,
        status=SubscriptionLifecycle.INITIAL.value,
        insync=False,
        version=1,
    )
    db.session.add(subscription)

    fixed_inputs = {fixed_input.name: fixed_input.value for fixed_input in product_db.fixed_inputs}
    model_data: dict[str, Any] = {
        "product": product,
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "description": description,
        "status": SubscriptionLifecycle.INITIAL,
        "insync": False,
        "start_date": None,
        "end_date": None,
        "note": None,
        "version": 1,
        **fixed_inputs,
        "optical_pipe": pipe_block,
    }
    model = subscription_model(**model_data)
    model.db_model = subscription
    return model


def default_pipe_identifier(
    node_a_block: AbstractOpticalNodeBlockInactive,
    port_a_name: str,
    node_b_block: AbstractOpticalNodeBlockInactive,
    port_b_name: str,
) -> str:
    """Return the default identifier of a pipe, e.g. ``"nodeA portA --- nodeB portB"``."""
    return f"{node_a_block.pqdn} {port_a_name} --- {node_b_block.pqdn} {port_b_name}"
