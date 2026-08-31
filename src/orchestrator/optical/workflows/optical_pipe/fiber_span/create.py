"""Create Optical Fiber Span workflow.

This module ships the ready-to-use ``create_fiber_span`` workflow for the
shipped Optical Fiber Span product type, together with the importable parts:
the FormPages of the create form (as the :func:`create_fiber_span_form_pages`
page sequence), the block population logic and the step list that operates on
the Optical Pipe block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model, populates its block with the create-form values (the mandatory fields
of the PROVISIONING lifecycle) and transitions it to PROVISIONING, the shipped
block steps configure the span terminations on the devices, refresh the
passbands in use and persist the PROVISIONING block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``, and the shipped description step finalizes
the subscription. The shipped form generator is a thin composition of the
shipped pages and the summary form, without hooks: consumers build their own
form generator by yielding from the shipped page sequence in one line and
adding their own pages::

    user_input_dict = yield from create_fiber_span_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from uuid import UUID, uuid4

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.hal.optical_port import get_device_line_ports_names
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import OpticalFiberSpanBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import (
    OpticalFiberSpanInactive,
    OpticalFiberSpanProvisioning,
)
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    configure_pipe_terminations,
    create_optical_pipe_form_generator,
    create_pipe_form_pages,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    pipe_terminations_form,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


def create_fiber_span_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Fiber Span create form, in order.

    This is the shipped create form as a page sequence: it yields the two-nodes
    page and the terminations page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys, consumed by the shipped
    construct step (:func:`construct_fiber_span_subscription`). A Fiber Span is
    terminated by line ports on both nodes. Consumers yield from it in one line
    inside their own create form generator, optionally interleaving their own
    pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    return create_pipe_form_pages(
        product_name,
        port_universe=get_device_line_ports_names,
        terminations_form=pipe_terminations_form,
    )


def create_fiber_span_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Fiber Span.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step (:func:`construct_fiber_span_subscription`). It is a thin
    composition of the shipped page sequence
    (:func:`create_fiber_span_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    return (
        yield from create_optical_pipe_form_generator(
            product_name,
            create_fiber_span_form_pages,
            ["customer_id", "optical_pipe_name", "node_a_id", "port_a_name", "node_b_id", "port_b_name"],
        )
    )


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
    end), before their subscription model is transitioned to the PROVISIONING
    lifecycle.

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
    """Construct the PROVISIONING domain subscription model for an Optical Fiber Span.

    This step builds the shipped ``OpticalFiberSpan`` model, populates its
    block with the create-form values through :func:`build_fiber_span_block`
    (the anti-corruption point) and transitions the subscription to
    PROVISIONING in memory, so the block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY`` is the PROVISIONING variant with its
    terminations already set — the contract of the shipped block steps of
    :data:`CREATE_FIBER_SPAN_BLOCK_STEPS`.

    Consumers that define their own product type (composing the
    ``OpticalFiberSpanBlock`` under their own attribute name) write their own
    construct step instead: it builds their subscription, populates the
    composed block with the mandatory fields set (e.g. via
    :func:`build_fiber_span_block`), transitions it to PROVISIONING and puts
    the block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
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
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_pipe,
    }


#: Create steps operating on the Optical Pipe block in the state. Every step
#: is block-level: the terminations are configured on the devices, the
#: passbands in use are refreshed and the block (with the refreshed passbands)
#: is persisted by the last step, because workflow steps execute with the
#: state serialized between steps (the block is re-hydrated from its
#: serialized form before every step operates on it). The block is assumed to
#: be in the PROVISIONING lifecycle status with its terminations already set:
#: the caller's construct step provides it (see
#: :func:`construct_fiber_span_subscription`). Consumers with their own model
#: run this list after constructing their subscription the same way and
#: putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_FIBER_SPAN_BLOCK_STEPS: StepList = (
    begin >> configure_pipe_terminations >> retrieve_optical_pipe_used_passbands >> save_optical_pipe_block
)


@create_workflow(initial_input_form=create_fiber_span_form_generator)
def create_fiber_span() -> StepList:
    """Workflow to create a new Optical Fiber Span subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalFiberSpan` model, populates its block with the
    create-form values and transitions it to PROVISIONING, the shipped block
    steps configure the span terminations on the devices, refresh the
    passbands in use and persist the block, and the shipped description step
    finalizes the subscription. It is therefore only valid for the shipped
    product type; consumers with their own product type compose their own
    create workflow with the same parts.
    """
    return (
        begin
        >> construct_fiber_span_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_FIBER_SPAN_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_FIBER_SPAN_BLOCK_STEPS",
    "build_fiber_span_block",
    "create_fiber_span",
    "create_fiber_span_form_pages",
]
