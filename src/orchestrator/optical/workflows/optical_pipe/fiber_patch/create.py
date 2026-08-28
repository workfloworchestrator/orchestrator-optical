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
model and puts its block in the state, the shipped block steps persist the
block and configure the patch terminations on the devices, and the shipped
description step finalizes the subscription. The
shipped form generator is a thin composition of the shipped pages and the
summary form, without hooks: consumers build their own form generator by
yielding from the shipped page sequence in one line and adding their own
pages::

    user_input_dict = yield from create_fiber_patch_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Any, cast
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
from orchestrator.optical.hal.optical_port import (
    configure_termination_when_attaching_new_fiber,
    get_device_client_ports_names,
    get_device_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (
    AbstractOpticalPipeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_patch import OpticalFiberPatchBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.unions import PatchPortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import (
    OpticalFiberPatchInactive,
    OpticalFiberPatchProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    default_pipe_identifier,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    optical_node_selector,
    optical_pipe_block_from_state,
    patch_port_block_class,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
    unused_node_port_selector,
)
from orchestrator.optical.workflows.shared import create_summary_form


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


def create_fiber_patch_nodes_form(
    product_name: str,
    node_choice: type[Choice],
) -> type[FormPage]:
    """Return the identity FormPage of the Optical Fiber Patch create form.

    This is the first page of the shipped create form: the two nodes connected
    by the patch. It is a building block for consumers that compose their own
    create form generator: the shipped page sequence
    (:func:`create_fiber_patch_form_pages`) yields it first. The page validates
    that the two ends of the patch are on different nodes.

    Args:
        product_name: Name of the product being created, used as the page title.
        node_choice: The ``Choice`` selector of the Optical Node subscriptions,
            as built by
            :func:`orchestrator.optical.workflows.optical_pipe.shared.optical_node_selector`.

    Returns:
        The identity FormPage of the shipped create form.
    """

    class CreateFiberPatchNodesForm(FormPage):
        model_config = ConfigDict(title=product_name)

        node_a_id: node_choice
        node_b_id: node_choice

        @model_validator(mode="after")
        def validate_distinct_nodes(self) -> "CreateFiberPatchNodesForm":
            """Raise if the two ends of the patch are on the same node."""
            if self.node_a_id == self.node_b_id:
                msg = "The two ends of a fiber patch must be on different nodes."
                raise ValueError(msg)
            return self

    return CreateFiberPatchNodesForm


def create_fiber_patch_terminations_form(
    product_name: str,
    port_a_choice: type[Choice],
    port_b_choice: type[Choice],
) -> type[FormPage]:
    """Return the terminations FormPage of the Optical Fiber Patch create form.

    This is the second page of the shipped create form: the identifier of the
    patch and the terminating ports on the two nodes. It is a building block
    for consumers that compose their own create form generator: the shipped
    page sequence (:func:`create_fiber_patch_form_pages`) yields it second.

    Args:
        product_name: Name of the product being created, used as the page title.
        port_a_choice: The ``Choice`` selector of the unused ports of node A,
            as built by
            :func:`orchestrator.optical.workflows.optical_pipe.shared.unused_node_port_selector`.
        port_b_choice: The ``Choice`` selector of the unused ports of node B,
            as built by
            :func:`orchestrator.optical.workflows.optical_pipe.shared.unused_node_port_selector`.

    Returns:
        The terminations FormPage of the shipped create form.
    """

    class CreateFiberPatchTerminationsForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Terminations")

        port_a_name: port_a_choice
        port_b_name: port_b_choice
        optical_pipe_name: str | None = Field(
            None,
            title="Fiber Patch Identifier",
            description="Unique patch ID or code. Leave empty to use the default 'node A port A --- node B port B'.",
        )

    return CreateFiberPatchTerminationsForm


def create_fiber_patch_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Fiber Patch create form, in order.

    This is the shipped create form as a page sequence: it yields the identity
    page and the terminations page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys, consumed by the shipped steps of
    :data:`CREATE_FIBER_PATCH_BLOCK_STEPS`. Consumers yield from it in one line
    inside their own create form generator, optionally interleaving their own
    pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    node_choice = optical_node_selector(prompt="This fiber patch connects this node:")

    user_input_dict: dict[str, Any] = {}

    nodes_input = yield create_fiber_patch_nodes_form(product_name, node_choice)
    user_input_dict.update(nodes_input.model_dump())

    node_a_block = node_block_from_subscription(user_input_dict["node_a_id"])
    node_b_block = node_block_from_subscription(user_input_dict["node_b_id"])

    port_a_choice = unused_node_port_selector(
        user_input_dict["node_a_id"],
        patch_ports_of_node(node_a_block),
        prompt=f"Select an unused port on {node_a_block.management.optical_module_node_fqdn}",
    )
    port_b_choice = unused_node_port_selector(
        user_input_dict["node_b_id"],
        patch_ports_of_node(node_b_block),
        prompt=f"Select an unused port on {node_b_block.management.optical_module_node_fqdn}",
    )

    terminations_input = yield create_fiber_patch_terminations_form(product_name, port_a_choice, port_b_choice)
    user_input_dict.update(terminations_input.model_dump())

    user_input_dict["optical_pipe_name"] = user_input_dict["optical_pipe_name"] or default_pipe_identifier(
        node_a_block, user_input_dict["port_a_name"], node_b_block, user_input_dict["port_b_name"]
    )
    return user_input_dict


def create_fiber_patch_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Fiber Patch.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_FIBER_PATCH_BLOCK_STEPS`. It is a thin composition
    of the shipped page sequence (:func:`create_fiber_patch_form_pages`) and
    the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_fiber_patch_form_pages(product_name)))

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
    before the subscription model is transitioned to the next lifecycle.

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
    """Construct the initial domain subscription model for an Optical Fiber Patch.

    This step builds the shipped ``OpticalFiberPatch`` model and puts its
    block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the shipped
    block steps of :data:`CREATE_FIBER_PATCH_BLOCK_STEPS`. Consumers that
    define their own product type (composing the ``OpticalFiberPatchBlock``
    under their own attribute name) write their own construct step instead and
    can reuse :func:`build_fiber_patch_block` as the anti-corruption point
    between their model and the shipped block.
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


@step("Configure Fiber Patch Terminations")
def configure_patch_terminations(
    optical_module_block: AbstractOpticalPipeBlockProvisioning,
) -> State:
    """Configure the terminating ports of the fiber patch on the devices.

    Operates only on the Optical Pipe block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``, the same block the rest of the shipped
    block steps act on. The block is re-hydrated from its serialized form (see
    :func:`optical_pipe_block_from_state`); it is read-only here, so only the
    device configuration results are returned.
    """
    pipe_block = optical_pipe_block_from_state(optical_module_block)
    terminations = pipe_block.optical_pipe_terminations
    port_a, port_b = terminations
    host_node_a = port_a.optical_port_host_node
    host_node_b = port_b.optical_port_host_node
    if not isinstance(host_node_a, AbstractOpticalNodeBlockInactive) or not isinstance(
        host_node_b, AbstractOpticalNodeBlockInactive
    ):
        msg = "Fiber patch terminations must be hosted on Optical Nodes"
        raise TypeError(msg)
    if (
        host_node_b.management.optical_module_node_vendor,
        host_node_b.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS) and (
        host_node_a.management.optical_module_node_vendor,
        host_node_a.management.optical_module_node_platform,
    ) != (Vendor.NOKIA, Platform.FLEXILS):
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
    return {"configuration_results": configuration_results, OPTICAL_MODULE_BLOCK_STATE_KEY: pipe_block}


#: Create steps operating on the Optical Pipe block in the state. The block
#: is re-hydrated from the database and persisted by the first step, because
#: workflow steps execute with the state serialized between steps; the
#: terminations are then configured on the devices, the passbands in use are
#: refreshed and the block (with the refreshed passbands) is persisted by the
#: last step. Consumers with their own model run this list after constructing
#: their (inactive) subscription and putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_FIBER_PATCH_BLOCK_STEPS: StepList = (
    begin
    >> configure_patch_terminations
    >> retrieve_optical_pipe_used_passbands
    >> save_optical_pipe_block
)


@create_workflow(initial_input_form=create_fiber_patch_form_generator)
def create_fiber_patch() -> StepList:
    """Workflow to create a new Optical Fiber Patch subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalFiberPatch` model and puts its block in the
    state, the shipped block steps persist the block and configure the patch
    terminations on the devices, and the shipped description step finalizes
    the subscription. It is therefore only valid for the shipped product type;
    consumers with their own product type compose their own create workflow
    with the same parts.
    """
    return (
        begin
        >> construct_fiber_patch_subscription
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
