"""Create Optical Fiber Patch workflow.

This module ships the ready-to-use ``create_fiber_patch`` workflow for the
shipped Optical Fiber Patch product type, together with the importable parts:
the FormPages of the create form (as the :func:`create_fiber_patch_form_pages`
page sequence), the block population logic and the step list that operates on
the Optical Pipe block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model, populates its block with the create-form values (the mandatory fields
of the PROVISIONING lifecycle) and transitions it to PROVISIONING, the shipped
block steps configure the patch terminations on the devices, refresh the
passbands in use and persist the PROVISIONING block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``, and the shipped description step finalizes
the subscription. The
shipped form generator is a thin composition of the shipped pages and the
summary form, without hooks: consumers build their own form generator by
yielding from the shipped page sequence in one line and adding their own
pages::

    user_input_dict = yield from create_fiber_patch_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import cast
from uuid import UUID, uuid4

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.hal.port import (
    get_device_client_ports_names,
    get_device_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_patch import OpticalFiberPatchBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.unions import PatchPortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import (
    OpticalFiberPatchInactive,
    OpticalFiberPatchProvisioning,
)
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    configure_pipe_terminations,
    create_optical_pipe_form_generator,
    create_pipe_form_pages,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    patch_port_block_class,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


def patch_ports_of_node(node_block: AbstractOpticalNodeBlockInactive) -> list[str]:
    """Return the ports of a node that can terminate a fiber patch.

    On a Nokia FlexILS node only the client (SCG) ports are selectable: the OTS
    ports are OLS line ports, which are not part of the Fiber Patch port block
    union. On Groove G30 and GX G42 nodes the client and line ports of the
    transponder cards are selectable.
    """
    client_ports = get_device_client_ports_names(node_block)
    if (
        node_block.management.optical_module_node_vendor,
        node_block.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS):
        return client_ports
    all_ports = get_device_ports_names(node_block)
    return list(dict.fromkeys([*client_ports, *all_ports]))


def create_fiber_patch_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Fiber Patch create form, in order.

    This is the shipped create form as a page sequence: it yields the two-nodes
    page and the terminations page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys, consumed by the shipped
    construct step (:func:`construct_fiber_patch_subscription`). A Fiber Patch
    is terminated by the client (SCG) ports of a Nokia FlexILS node, or by the
    client and line ports of a Groove G30 or GX G42 node
    (:func:`patch_ports_of_node`). Consumers yield from it in one line inside
    their own create form generator, optionally interleaving their own pages.
    The customer of the subscription is collected separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    return create_pipe_form_pages(
        product_name,
        port_universe=patch_ports_of_node,
    )


def create_fiber_patch_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Fiber Patch.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step (:func:`construct_fiber_patch_subscription`). It is a thin
    composition of the shipped page sequence
    (:func:`create_fiber_patch_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    return (
        yield from create_optical_pipe_form_generator(
            product_name,
            create_fiber_patch_form_pages,
            ["customer_id", "optical_pipe_name", "node_a_id", "port_a_name", "node_b_id", "port_b_name"],
        )
    )


def build_fiber_patch_block(
    subscription_id: UUID,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_name: str,
) -> OpticalFiberPatchBlockInactive:
    """Build the Optical Fiber Patch block of a new subscription.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step to build the shipped block with its
    two terminating port blocks (each physically connected to the remote end),
    before their subscription model is transitioned to the PROVISIONING
    lifecycle.

    Args:
        subscription_id: Subscription id of the new pipe subscription.
        node_a_id: Subscription id of the Optical Node hosting end A of the patch.
        node_b_id: Subscription id of the Optical Node hosting end B of the patch.
        port_a_name: Name of the terminating port on node A.
        port_b_name: Name of the terminating port on node B.
        optical_pipe_name: Identifier of the patch.

    Returns:
        The inactive Optical Fiber Patch block with its two terminations.
    """
    node_a_block = node_block_from_subscription(node_a_id)
    node_b_block = node_block_from_subscription(node_b_id)

    client_ports_a = get_device_client_ports_names(node_a_block)
    client_ports_b = get_device_client_ports_names(node_b_block)
    port_a = new_pipe_port_block(
        subscription_id,
        node_a_block,
        port_a_name,
        f"Physically connected to {node_b_block.management.optical_module_node_fqdn} {port_b_name}.",
        patch_port_block_class(node_a_block, port_a_name, client_ports_a),
    )
    port_b = new_pipe_port_block(
        subscription_id,
        node_b_block,
        port_b_name,
        f"Physically connected to {node_a_block.management.optical_module_node_fqdn} {port_a_name}.",
        patch_port_block_class(node_b_block, port_b_name, client_ports_b),
    )

    pipe_block = OpticalFiberPatchBlockInactive.new(
        subscription_id=subscription_id,
        optical_pipe_terminations=cast(list[PatchPortBlockInactive], [port_a, port_b]),
    )
    pipe_block.optical_pipe_name = optical_pipe_name
    return pipe_block


@step("Construct Fiber Patch Subscription")
def construct_fiber_patch_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_name: str,
) -> State:
    """Construct the PROVISIONING domain subscription model for an Optical Fiber Patch.

    This step builds the shipped ``OpticalFiberPatch`` model, populates its
    block with the create-form values through :func:`build_fiber_patch_block`
    (the anti-corruption point) and transitions the subscription to
    PROVISIONING in memory, so the block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY`` is the PROVISIONING variant with its
    terminations already set — the contract of the shipped block steps of
    :data:`CREATE_FIBER_PATCH_BLOCK_STEPS`.

    Consumers that define their own product type (composing the
    ``OpticalFiberPatchBlock`` under their own attribute name) write their own
    construct step instead: it builds their subscription, populates the
    composed block with the mandatory fields set (e.g. via
    :func:`build_fiber_patch_block`), transitions it to PROVISIONING and puts
    the block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    subscription_id = uuid4()
    pipe_block = build_fiber_patch_block(
        subscription_id, node_a_id, node_b_id, port_a_name, port_b_name, optical_pipe_name
    )

    subscription = new_optical_pipe_subscription(OpticalFiberPatchInactive, product, customer_id, pipe_block)
    subscription = OpticalFiberPatchProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)

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
#: :func:`construct_fiber_patch_subscription`). Consumers with their own model
#: run this list after constructing their subscription the same way and
#: putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_FIBER_PATCH_BLOCK_STEPS: StepList = (
    begin >> configure_pipe_terminations >> retrieve_optical_pipe_used_passbands >> save_optical_pipe_block
)


@create_workflow(initial_input_form=create_fiber_patch_form_generator)
def create_fiber_patch() -> StepList:
    """Workflow to create a new Optical Fiber Patch subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalFiberPatch` model, populates its block with the
    create-form values and transitions it to PROVISIONING, the shipped block
    steps configure the patch terminations on the devices, refresh the
    passbands in use and persist the block, and the shipped description step
    finalizes the subscription. It is therefore only valid for the shipped
    product type; consumers with their own product type compose their own
    create workflow with the same parts.
    """
    return (
        begin
        >> construct_fiber_patch_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_FIBER_PATCH_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_FIBER_PATCH_BLOCK_STEPS",
    "build_fiber_patch_block",
    "create_fiber_patch",
    "create_fiber_patch_form_pages",
]
