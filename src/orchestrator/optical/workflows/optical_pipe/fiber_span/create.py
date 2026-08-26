"""Create Optical Fiber Span workflow.

This module ships the ready-to-use ``create_fiber_span`` workflow for the
shipped Optical Fiber Span product type, together with the importable parts:
the FormPages of the create form (as the :func:`create_fiber_span_form_pages`
page sequence), the block population logic and the step list that operates on
the Optical Pipe block found in the state under
``OPTICAL_PIPE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model and puts its block in the state, the shipped block steps persist the
block, and the shipped description step finalizes the subscription. The
shipped form generator is a thin composition of the shipped pages and the
summary form, without hooks: consumers build their own form generator by
yielding from the shipped page sequence in one line and adding their own
pages::

    user_input_dict = yield from create_fiber_span_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Any
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.hal.optical_node import Vendor, retrieve_ports_spectral_occupations, vendor_of
from orchestrator.optical.hal.optical_port import (
    configure_termination_when_attaching_new_fiber,
    get_device_line_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import OpticalFiberSpanBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import (
    OpticalFiberSpanInactive,
    OpticalFiberSpanProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_PIPE_BLOCK_STATE_KEY,
    default_pipe_identifier,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    optical_node_selector,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
    unused_node_port_selector,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_fiber_span_identity_form(
    product_name: str,
    customer_choice: type[Choice],
    node_choice: type[Choice],
) -> type[FormPage]:
    """Return the identity FormPage of the Optical Fiber Span create form.

    This is the first page of the shipped create form: the customer and the
    two nodes connected by the span. It is a building block for consumers
    that compose their own create form generator: the shipped page sequence
    (:func:`create_fiber_span_form_pages`) yields it first. The page
    validates that the two ends of the span are on different nodes.

    Args:
        product_name: Name of the product being created, used as the page title.
        customer_choice: The ``Choice`` selector of the subscription customer,
            as built by
            :func:`orchestrator.optical.workflows.customer.customer_choice_selector`.
        node_choice: The ``Choice`` selector of the Optical Node subscriptions,
            as built by
            :func:`orchestrator.optical.workflows.optical_pipe.shared.optical_node_selector`.

    Returns:
        The identity FormPage of the shipped create form.
    """

    class CreateFiberSpanIdentityForm(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        node_a_id: node_choice
        node_b_id: node_choice

        @model_validator(mode="after")
        def validate_distinct_nodes(self) -> "CreateFiberSpanIdentityForm":
            if self.node_a_id == self.node_b_id:
                msg = "The two ends of a fiber span must be on different nodes."
                raise ValueError(msg)
            return self

    return CreateFiberSpanIdentityForm


def create_fiber_span_terminations_form(
    product_name: str,
    port_a_choice: type[Choice],
    port_b_choice: type[Choice],
) -> type[FormPage]:
    """Return the terminations FormPage of the Optical Fiber Span create form.

    This is the second page of the shipped create form: the identifier of the
    span and the terminating line ports on the two nodes. It is a building
    block for consumers that compose their own create form generator: the
    shipped page sequence (:func:`create_fiber_span_form_pages`) yields it
    second.

    Args:
        product_name: Name of the product being created, used as the page title.
        port_a_choice: The ``Choice`` selector of the unused line ports of node A,
            as built by
            :func:`orchestrator.optical.workflows.optical_pipe.shared.unused_node_port_selector`.
        port_b_choice: The ``Choice`` selector of the unused line ports of node B,
            as built by
            :func:`orchestrator.optical.workflows.optical_pipe.shared.unused_node_port_selector`.

    Returns:
        The terminations FormPage of the shipped create form.
    """

    class CreateFiberSpanTerminationsForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Terminations")

        optical_pipe_name: str | None = Field(
            None,
            title="Fiber Span Identifier",
            description="Unique span ID or code. Leave empty to use the default 'node A port A --- node B port B'.",
        )
        port_a_name: port_a_choice
        port_b_name: port_b_choice

    return CreateFiberSpanTerminationsForm


def create_fiber_span_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Fiber Span create form, in order.

    This is the shipped create form as a page sequence: it yields the identity
    page and the terminations page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys plus ``customer_id``, consumed
    by the shipped steps of :data:`CREATE_FIBER_SPAN_BLOCK_STEPS`. Consumers
    yield from it in one line inside their own create form generator,
    optionally interleaving their own pages.

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    node_choice = optical_node_selector(prompt="This fiber span connects this node:")
    customer_choice = customer_choice_selector()

    user_input_dict: dict[str, Any] = {}
    user_input_dict.update(
        (yield create_fiber_span_identity_form(product_name, customer_choice, node_choice)).model_dump()
    )

    node_a_block = node_block_from_subscription(user_input_dict["node_a_id"])
    node_b_block = node_block_from_subscription(user_input_dict["node_b_id"])

    port_a_choice = unused_node_port_selector(
        user_input_dict["node_a_id"],
        get_device_line_ports_names(node_a_block),
        prompt=f"Select an unused line port on {node_a_block.management.optical_module_node_fqdn}",
    )
    port_b_choice = unused_node_port_selector(
        user_input_dict["node_b_id"],
        get_device_line_ports_names(node_b_block),
        prompt=f"Select an unused line port on {node_b_block.management.optical_module_node_fqdn}",
    )
    user_input_dict.update(
        (yield create_fiber_span_terminations_form(product_name, port_a_choice, port_b_choice)).model_dump()
    )

    user_input_dict["optical_pipe_name"] = user_input_dict["optical_pipe_name"] or default_pipe_identifier(
        node_a_block, user_input_dict["port_a_name"], node_b_block, user_input_dict["port_b_name"]
    )
    return user_input_dict


def create_fiber_span_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Fiber Span.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_FIBER_SPAN_BLOCK_STEPS`. It is a thin composition
    of the shipped page sequence (:func:`create_fiber_span_form_pages`) and
    the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from create_fiber_span_form_pages(product_name)

    summary_fields = [
        "customer_id",
        "optical_pipe_name",
        "node_a_id",
        "port_a_name",
        "node_b_id",
        "port_b_name",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def build_fiber_span_block(
    subscription_id: UUID,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_name: str,
) -> OpticalFiberSpanBlockInactive:
    """Build the Optical Fiber Span block of a new subscription.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step to build the shipped block with its
    two terminating line port blocks (each physically connected to the remote
    end), before the subscription model is transitioned to the next lifecycle.

    Args:
        subscription_id: Subscription id of the new pipe subscription.
        node_a_id: Subscription id of the Optical Node hosting end A of the span.
        node_b_id: Subscription id of the Optical Node hosting end B of the span.
        port_a_name: Name of the terminating line port on node A.
        port_b_name: Name of the terminating line port on node B.
        optical_pipe_name: Identifier of the span.

    Returns:
        The inactive Optical Fiber Span block with its two terminations.
    """
    node_a_block = node_block_from_subscription(node_a_id)
    node_b_block = node_block_from_subscription(node_b_id)

    port_a = new_pipe_port_block(
        subscription_id,
        node_a_block,
        port_a_name,
        f"Physically connected to {node_b_block.management.optical_module_node_fqdn} {port_b_name}.",
        OlsLinePortBlockInactive,
    )
    port_b = new_pipe_port_block(
        subscription_id,
        node_b_block,
        port_b_name,
        f"Physically connected to {node_a_block.management.optical_module_node_fqdn} {port_a_name}.",
        OlsLinePortBlockInactive,
    )

    pipe_block = OpticalFiberSpanBlockInactive.new(
        subscription_id=subscription_id,
        optical_pipe_terminations=[port_a, port_b],
    )
    pipe_block.optical_pipe_name = optical_pipe_name
    return pipe_block


@step("Construct Fiber Span Subscription")
def construct_fiber_span_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_name: str,
) -> State:
    """Construct the initial domain subscription model for an Optical Fiber Span.

    This step builds the shipped ``OpticalFiberSpan`` model and puts its
    block in the state under ``OPTICAL_PIPE_BLOCK_STATE_KEY`` for the shipped
    block steps of :data:`CREATE_FIBER_SPAN_BLOCK_STEPS`. Consumers that
    define their own product type (composing the ``OpticalFiberSpanBlock``
    under their own attribute name) write their own construct step instead and
    can reuse :func:`build_fiber_span_block` as the anti-corruption point
    between their model and the shipped block.
    """
    subscription_id = uuid4()
    pipe_block = build_fiber_span_block(
        subscription_id, node_a_id, node_b_id, port_a_name, port_b_name, optical_pipe_name
    )

    subscription = new_optical_pipe_subscription(OpticalFiberSpanInactive, product, customer_id, pipe_block)
    subscription = OpticalFiberSpanProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_PIPE_BLOCK_STATE_KEY: subscription.optical_pipe,
    }


#: Create steps operating on the Optical Pipe block in the state. The block
#: is re-hydrated from the database and persisted by the last step, because
#: workflow steps execute with the state serialized between steps. Consumers
#: with their own model run this list after constructing their (inactive)
#: subscription and putting their block in the state under
#: ``OPTICAL_PIPE_BLOCK_STATE_KEY``.
CREATE_FIBER_SPAN_BLOCK_STEPS: StepList = begin >> save_optical_pipe_block


@step("Configure Fiber Span Terminations")
def configure_span_terminations(subscription: OpticalFiberSpanProvisioning) -> State:
    """Configure the terminating line ports of the fiber span on the devices."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    if (
        vendor_of(port_b.optical_port_host_node) == Vendor.FLEXILS
        and vendor_of(port_a.optical_port_host_node) != Vendor.FLEXILS
    ):
        # Configure the FlexILS side first: its configuration references the remote node.
        port_a, port_b = port_b, port_a

    configuration_results = {
        f"{port_a.optical_port_host_node.management.optical_module_node_fqdn} {port_a.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(port_a, port_b)
        ),
        f"{port_b.optical_port_host_node.management.optical_module_node_fqdn} {port_b.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(port_b, port_a)
        ),
    }
    return {"configuration_results": configuration_results, "subscription": subscription}


@step("Retrieve Used Passbands")
def retrieve_span_used_passbands(subscription: OpticalFiberSpanProvisioning) -> State:
    """Refresh the passbands in use on the terminating ports from the devices."""
    for port in subscription.optical_pipe.optical_pipe_terminations:
        host_node = port.optical_port_host_node
        if host_node.optical_node_role not in (
            OpticalNodeRole.ROADM,
            OpticalNodeRole.TRANSPONDER_XOADM,
            OpticalNodeRole.AMPLIFIER,
        ):
            continue
        if port.optical_port_name is None:
            msg = f"Optical port block of {host_node.management.optical_module_node_fqdn} has no port name"
            raise ValueError(msg)
        port.optical_passbands = retrieve_ports_spectral_occupations(host_node).get(port.optical_port_name, [])
    return {"subscription": subscription}


@create_workflow(initial_input_form=create_fiber_span_form_generator)
def create_fiber_span() -> StepList:
    """Workflow to create a new Optical Fiber Span subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalFiberSpan` model and puts its block in the
    state, the shipped block steps persist the block, and the shipped
    description step finalizes the subscription. It is therefore only valid
    for the shipped product type; consumers with their own product type
    compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_fiber_span_subscription
        >> CREATE_FIBER_SPAN_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> store_process_subscription()
        >> configure_span_terminations
        >> retrieve_span_used_passbands
    )


__all__ = [
    "CREATE_FIBER_SPAN_BLOCK_STEPS",
    "build_fiber_span_block",
    "configure_span_terminations",
    "construct_fiber_span_subscription",
    "create_fiber_span",
    "create_fiber_span_form_generator",
    "create_fiber_span_form_pages",
    "create_fiber_span_identity_form",
    "create_fiber_span_terminations_form",
    "retrieve_span_used_passbands",
]
