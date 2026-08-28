"""Create Optical Coherent Pluggable workflow.

This module ships the ready-to-use ``create_optical_coherent_pluggable``
workflow for the shipped Optical Coherent Pluggable product type, together
with the importable parts: the FormPage of the create form (as the
:func:`create_optical_coherent_pluggable_form_pages` page sequence), the block
population logic and the step list that operates on the Optical Coherent
Pluggable block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model and puts its block in the state, the shipped block steps populate and
persist the block, and the shipped description step finalizes the
subscription. The shipped form generator is a thin composition of the shipped
pages and the summary form, without hooks: consumers build their own form
generator by yielding from the shipped page sequence in one line and adding
their own pages::

    user_input_dict = yield from create_optical_coherent_pluggable_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Annotated, Any, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import subscription_instances_by_block_type_and_resource_value
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_packet_node import (
    OpticalModulePacketNodeInactive,
)
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggableInactive,
    OpticalCoherentPluggablePartNumber,
)
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    optical_coherent_pluggable_block_from_state,
    packet_node_block_from_subscription,
    save_optical_coherent_pluggable_block,
    update_optical_coherent_pluggable_subscription_description,
)
from orchestrator.optical.workflows.shared import active_subscription_selector_by_block_type, create_summary_form


def check_optical_coherent_pluggable_port_uniqueness(
    optical_port_name: str,
    host_node_block: OpticalModulePacketNodeInactive,
    exclude_subscription_id: str | None = None,
) -> None:
    """Raise if the port name is already occupied on the host node by another subscription.

    The check is block-based: it queries the subscription instances of the
    shipped ``OpticalCoherentPluggableBlock`` block type whose
    ``optical_port_name`` resource value equals the given port name and whose
    owner subscription is INITIAL, PROVISIONING or ACTIVE. Because every
    consumer that composes the shipped block persists it under the shipped
    block name, the check also covers composed product types without
    hardcoding a product type. The subscription owning the pluggable is
    excluded by ``exclude_subscription_id``, so a subscription never conflicts
    with its own pluggable block.

    This is an application-level check only: the module ships no database
    migrations (consumers generate them), so no unique constraint enforces the
    uniqueness in the database. As a known limitation there is a residual
    TOCTOU race between the check and the subsequent block save; the block
    population step re-checks at execution time to shrink the window, but it
    cannot be fully closed by the module.

    Args:
        optical_port_name: Name of the port of the host node.
        host_node_block: Optical Module Packet Node block hosting the port.
        exclude_subscription_id: Identifier of the subscription owning the
            pluggable, whose own block is not a conflict.

    Raises:
        ValueError: If another subscription already uses the port on the host
            node, naming the conflicting port and subscription.
    """
    existing_instances = subscription_instances_by_block_type_and_resource_value(
        cast(str, OpticalCoherentPluggableBlock.name),
        "optical_port_name",
        optical_port_name,
        [SubscriptionLifecycle.INITIAL, SubscriptionLifecycle.PROVISIONING, SubscriptionLifecycle.ACTIVE],
    )
    for instance in existing_instances:
        if exclude_subscription_id is not None and str(instance.subscription_id) == str(exclude_subscription_id):
            continue
        # The ACTIVE class is the most-derived subclass, so it can load
        # INITIAL, PROVISIONING and ACTIVE blocks (unlike the
        # PROVISIONING class).
        pluggable_block = OpticalCoherentPluggableBlock.from_db(
            subscription_instance_id=instance.subscription_instance_id
        )
        host_node = pluggable_block.optical_port_host_node
        if host_node is not None and host_node.subscription_instance_id == host_node_block.subscription_instance_id:
            msg = (
                f"Port {optical_port_name} on node "
                f"{host_node_block.management.optical_module_node_fqdn} "
                f"is already occupied by subscription {instance.subscription_id}"
            )
            raise ValueError(msg)


def create_optical_coherent_pluggable_form(
    product_name: str,
    packet_node_choice: type[Choice],
    part_number_choice: type[Choice],
) -> type[FormPage]:
    """Return the FormPage of the Optical Coherent Pluggable create form.

    This is the single page of the shipped create form: the Optical Module
    Packet Node hosting the pluggable, the part number and the port data of the
    pluggable. It is a building block for consumers that compose their own
    create form generator: the shipped page sequence
    (:func:`create_optical_coherent_pluggable_form_pages`) yields it. The page
    validates that the entered port name is not already occupied on the host
    node by another subscription.

    Args:
        product_name: Name of the product being created, used as the page title.
        packet_node_choice: The ``Choice`` selector of the Optical Module
            Packet Node subscriptions, as built by
            :func:`orchestrator.optical.workflows.shared.active_subscription_selector_by_block_type`.
        part_number_choice: The ``Choice`` selector of the pluggable part numbers.

    Returns:
        The create FormPage of the shipped create form.
    """

    class CreateOpticalCoherentPluggableForm(FormPage):
        model_config = ConfigDict(title=product_name)

        optical_packet_node_id: packet_node_choice
        optical_coherent_pluggable_part_number: part_number_choice
        optical_port_name: Annotated[
            str,
            Field(title="Name of the port of the packet node that hosts the pluggable."),
        ]
        optical_port_description: str | None = None
        optical_coherent_pluggable_firmware_version: str

        @model_validator(mode="after")
        def validate_unique_port_on_node(self) -> "CreateOpticalCoherentPluggableForm":
            node_block = packet_node_block_from_subscription(self.optical_packet_node_id)
            check_optical_coherent_pluggable_port_uniqueness(
                self.optical_port_name,
                node_block,
            )
            return self

    return CreateOpticalCoherentPluggableForm


def create_optical_coherent_pluggable_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPage of the Optical Coherent Pluggable create form.

    This is the shipped create form as a page sequence: it yields the create
    page and returns the collected user input as a flat dict of the flat
    ``optical_*`` state keys, consumed by the shipped steps of
    :data:`CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS`. Consumers yield from
    it in one line inside their own create form generator, optionally
    interleaving their own pages. The customer of the subscription is collected
    separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    packet_node_choice = active_subscription_selector_by_block_type(
        OpticalModulePacketNodeInactive, prompt="Select an Optical Packet Node"
    )
    part_number_choice = cast(
        type[Choice],
        Choice(
            "Select Optical Coherent Pluggable Part Number",
            [(item.value, item.value) for item in OpticalCoherentPluggablePartNumber],
        ),
    )

    user_input_dict: dict[str, Any] = {}
    user_input_dict.update(
        (
            yield create_optical_coherent_pluggable_form(product_name, packet_node_choice, part_number_choice)
        ).model_dump()
    )
    return user_input_dict


def create_optical_coherent_pluggable_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Coherent Pluggable.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS`. It is a thin
    composition of the shipped page sequence
    (:func:`create_optical_coherent_pluggable_form_pages`) and the summary
    form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_coherent_pluggable_form_pages(product_name)))

    summary_fields = [
        "customer_id",
        "optical_packet_node_id",
        "optical_coherent_pluggable_part_number",
        "optical_port_name",
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def populate_optical_coherent_pluggable_block(
    optical_module_block: OpticalCoherentPluggableBlockInactive,
    optical_port_host_node: OpticalModulePacketNodeInactive,
    optical_port_name: str,
    optical_port_description: str | None = None,
    optical_coherent_pluggable_firmware_version: str | None = None,
) -> None:
    """Populate an Optical Coherent Pluggable block from the create-form state keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle. The
    host node block comes from the Optical Packet Node subscription hosting
    the pluggable: consumers pass the shipped packet node block of their own
    model, the shipped steps resolve it from the form's
    ``optical_packet_node_id``. It re-checks the uniqueness of the port on the
    host node at execution time, so consumers bypassing the form validation are
    still guarded against duplicates.

    Args:
        optical_module_block: The Optical Coherent Pluggable block to populate (any lifecycle variant).
        optical_port_host_node: Optical Module Packet Node block hosting the pluggable.
        optical_port_name: Name of the port of the host node.
        optical_port_description: Description of the port.
        optical_coherent_pluggable_firmware_version: Firmware version of the pluggable.

    Raises:
        ValueError: If the port is already occupied on the host node by another subscription.
    """
    check_optical_coherent_pluggable_port_uniqueness(
        optical_port_name,
        optical_port_host_node,
        exclude_subscription_id=str(optical_module_block.owner_subscription_id),
    )
    optical_module_block.optical_port_host_node = optical_port_host_node
    optical_module_block.optical_port_name = optical_port_name
    optical_module_block.optical_port_description = optical_port_description
    optical_module_block.optical_coherent_pluggable_firmware_version = optical_coherent_pluggable_firmware_version


@step("Populate Optical Coherent Pluggable block")
def populate_optical_coherent_pluggable_block_step(
    optical_module_block: OpticalCoherentPluggableBlockInactive,
    optical_packet_node_id: UUIDstr,
    optical_port_name: str,
    optical_port_description: str | None = None,
    optical_coherent_pluggable_firmware_version: str | None = None,
) -> State:
    """Populate the Optical Coherent Pluggable block found in the state from the create-form keys.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from the database by its ``subscription_instance_id``
    before it is populated.

    Args:
        optical_module_block: The Optical Coherent Pluggable block
            in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
        optical_packet_node_id: Subscription id of the Optical Packet Node hosting the pluggable.
        optical_port_name: Name of the port of the host node.
        optical_port_description: Description of the port.
        optical_coherent_pluggable_firmware_version: Firmware version of the pluggable.

    Raises:
        ValueError: If there is no Optical Coherent Pluggable block in the state
            under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    pluggable = optical_coherent_pluggable_block_from_state(optical_module_block)
    if pluggable is None:
        msg = "No Optical Coherent Pluggable block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    host_node = packet_node_block_from_subscription(optical_packet_node_id)
    populate_optical_coherent_pluggable_block(
        optical_module_block=pluggable,
        optical_port_host_node=host_node,
        optical_port_name=optical_port_name,
        optical_port_description=optical_port_description,
        optical_coherent_pluggable_firmware_version=optical_coherent_pluggable_firmware_version,
    )
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: pluggable}


@step("Construct Subscription model")
def construct_optical_coherent_pluggable_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber,
) -> State:
    """Construct the initial domain subscription model for an Optical Coherent Pluggable.

    This step builds the shipped ``OpticalCoherentPluggable`` subscription
    model and puts its block in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the shipped block steps
    of :data:`CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS`. Consumers that
    define their own product type (composing the
    ``OpticalCoherentPluggableBlock`` under their own attribute name) write
    their own construct step instead and can reuse
    :func:`populate_optical_coherent_pluggable_block` as the anti-corruption
    point between their model and the shipped block.
    """
    subscription = OpticalCoherentPluggableInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.optical_coherent_pluggable_part_number = optical_coherent_pluggable_part_number

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_coherent_pluggable,
    }


#: Create steps operating on the Optical Coherent Pluggable block in the state.
#: The block is re-hydrated from the database and persisted by the last step,
#: because workflow steps execute with the state serialized between steps.
#: Consumers with their own model run this list after constructing their
#: (inactive) subscription and putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS: StepList = (
    begin >> populate_optical_coherent_pluggable_block_step >> save_optical_coherent_pluggable_block
)


@create_workflow(initial_input_form=create_optical_coherent_pluggable_form_generator)
def create_optical_coherent_pluggable() -> StepList:
    """Workflow to create a new Optical Coherent Pluggable subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalCoherentPluggable` model and puts its block in
    the state, the shipped block steps populate and persist the block, and the
    shipped description step finalizes the subscription. It is therefore only
    valid for the shipped product type; consumers with their own product type
    compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_optical_coherent_pluggable_subscription
        >> CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_optical_coherent_pluggable_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS",
    "check_optical_coherent_pluggable_port_uniqueness",
    "construct_optical_coherent_pluggable_subscription",
    "create_optical_coherent_pluggable",
    "create_optical_coherent_pluggable_form",
    "create_optical_coherent_pluggable_form_generator",
    "create_optical_coherent_pluggable_form_pages",
    "populate_optical_coherent_pluggable_block",
    "populate_optical_coherent_pluggable_block_step",
]
