"""Create Optical Coherent Pluggable workflow.

This module ships the ready-to-use ``create_optical_coherent_pluggable``
workflow for the shipped Optical Coherent Pluggable product type, together
with the importable parts: the form generator, the block population logic and
the step list that operates on the Optical Coherent Pluggable block found in
the state under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``. Consumers that
keep the shipped product type register the shipped workflow; consumers with
their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts.
"""

from collections.abc import Sequence
from typing import Annotated, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
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
    OpticalCoherentPluggableProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY,
    optical_coherent_pluggable_subscription_description,
    packet_node_block_from_subscription,
    save_optical_coherent_pluggable_block,
)
from orchestrator.optical.workflows.shared import (
    active_subscription_selector_by_block_type,
    create_summary_form,
    subscription_instances_by_block_type_and_resource_value,
)


def create_optical_coherent_pluggable_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for creating an Optical Coherent Pluggable.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS`.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    packet_node_choice = active_subscription_selector_by_block_type(
        OpticalModulePacketNodeInactive, prompt="Select an Optical Packet Node"
    )
    part_number_choice = Choice(
        "Select Optical Coherent Pluggable Part Number",
        [(item.value, item.value) for item in OpticalCoherentPluggablePartNumber],
    )
    customer_choice = customer_choice_selector()

    class CreateOpticalCoherentPluggableForm(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
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

            # Check if this port on the host node is already assigned. The
            # check is block-based: the shipped block name is persisted by
            # every consumer that has-a the shipped block, so the check also
            # covers composed product types without hardcoding a product type.
            existing_instances = subscription_instances_by_block_type_and_resource_value(
                cast(str, OpticalCoherentPluggableBlock.name),
                "optical_port_name",
                self.optical_port_name,
                [
                    SubscriptionLifecycle.INITIAL,
                    SubscriptionLifecycle.PROVISIONING,
                    SubscriptionLifecycle.ACTIVE,
                ],
            )
            for instance in existing_instances:
                # The ACTIVE class is the most-derived subclass, so it can load
                # INITIAL, PROVISIONING and ACTIVE blocks (unlike the
                # PROVISIONING class).
                pluggable_block = OpticalCoherentPluggableBlock.from_db(
                    subscription_instance_id=instance.subscription_instance_id
                )
                host_node = pluggable_block.optical_port_host_node
                if host_node is not None and host_node.subscription_instance_id == node_block.subscription_instance_id:
                    msg = (
                        f"Port {self.optical_port_name} on node "
                        f"{node_block.management.optical_module_node_fqdn} "
                        f"is already occupied by subscription {instance.subscription_id}"
                    )
                    raise ValueError(msg)

            return self

    user_input = yield CreateOpticalCoherentPluggableForm
    user_input_dict = user_input.model_dump()

    summary_fields = [
        "customer_id",
        "optical_packet_node_id",
        "optical_coherent_pluggable_part_number",
        "optical_port_name",
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    ]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from create_summary_form(
        user_input_dict,
        product_name,
        summary_fields,
        extra_summary_fields=extra_summary_fields,
    )

    return user_input_dict


def populate_optical_coherent_pluggable_block(
    optical_coherent_pluggable_block: OpticalCoherentPluggableBlockInactive,
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
    ``optical_packet_node_id``.

    Args:
        optical_coherent_pluggable_block: The Optical Coherent Pluggable block to populate (any lifecycle variant).
        optical_port_host_node: Optical Module Packet Node block hosting the pluggable.
        optical_port_name: Name of the port of the host node.
        optical_port_description: Description of the port.
        optical_coherent_pluggable_firmware_version: Firmware version of the pluggable.
    """
    optical_coherent_pluggable_block.optical_port_host_node = optical_port_host_node
    optical_coherent_pluggable_block.optical_port_name = optical_port_name
    optical_coherent_pluggable_block.optical_port_description = optical_port_description
    optical_coherent_pluggable_block.optical_coherent_pluggable_firmware_version = (
        optical_coherent_pluggable_firmware_version
    )


@step("Populate Optical Coherent Pluggable block")
def populate_optical_coherent_pluggable_block_step(
    optical_coherent_pluggable_block: OpticalCoherentPluggableBlockInactive,
    optical_packet_node_id: UUIDstr,
    optical_port_name: str,
    optical_port_description: str | None = None,
    optical_coherent_pluggable_firmware_version: str | None = None,
) -> State:
    """Populate the Optical Coherent Pluggable block found in the state from the create-form keys.

    Args:
        optical_coherent_pluggable_block: The Optical Coherent Pluggable block
            in the state under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``.
        optical_packet_node_id: Subscription id of the Optical Packet Node hosting the pluggable.
        optical_port_name: Name of the port of the host node.
        optical_port_description: Description of the port.
        optical_coherent_pluggable_firmware_version: Firmware version of the pluggable.
    """
    host_node = packet_node_block_from_subscription(optical_packet_node_id)
    populate_optical_coherent_pluggable_block(
        optical_coherent_pluggable_block=optical_coherent_pluggable_block,
        optical_port_host_node=host_node,
        optical_port_name=optical_port_name,
        optical_port_description=optical_port_description,
        optical_coherent_pluggable_firmware_version=optical_coherent_pluggable_firmware_version,
    )
    return {OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: optical_coherent_pluggable_block}


@step("Construct Subscription model")
def construct_optical_coherent_pluggable_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    optical_packet_node_id: UUIDstr,
    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber,
    optical_port_name: str,
    optical_port_description: str | None,
    optical_coherent_pluggable_firmware_version: str,
) -> State:
    """Construct the initial domain subscription model for an Optical Coherent Pluggable.

    This step builds the shipped ``OpticalCoherentPluggable`` subscription
    model, populates its block and computes the subscription description (the
    description reads the subscription-level part number, so it can only be
    computed here). Consumers that define their own product type (composing
    the ``OpticalCoherentPluggableBlock`` under their own attribute name)
    write their own construct step instead and can reuse
    :func:`populate_optical_coherent_pluggable_block` as the anti-corruption
    point between their model and the shipped block.
    """
    host_node = packet_node_block_from_subscription(optical_packet_node_id)

    subscription = OpticalCoherentPluggableInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.optical_coherent_pluggable_part_number = optical_coherent_pluggable_part_number
    populate_optical_coherent_pluggable_block(
        optical_coherent_pluggable_block=subscription.optical_coherent_pluggable,
        optical_port_host_node=host_node,
        optical_port_name=optical_port_name,
        optical_port_description=optical_port_description,
        optical_coherent_pluggable_firmware_version=optical_coherent_pluggable_firmware_version,
    )

    subscription = OpticalCoherentPluggableProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = optical_coherent_pluggable_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


#: Create steps operating on the Optical Coherent Pluggable block in the state.
#: Consumers that keep the shipped product type do not need this list (the
#: shipped construct step populates the block itself); consumers with their own
#: model run it after constructing their (inactive) subscription and putting
#: their block in the state under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``.
CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS: StepList = (
    begin >> populate_optical_coherent_pluggable_block_step >> save_optical_coherent_pluggable_block
)


@create_workflow(initial_input_form=create_optical_coherent_pluggable_form_generator)
def create_optical_coherent_pluggable() -> StepList:
    """Workflow to create a new Optical Coherent Pluggable subscription.

    The workflow is valid for the shipped :class:`OpticalCoherentPluggable`
    product type only: the construct step builds the shipped subscription
    model. Consumers with their own product type compose their own create
    workflow with the shipped parts.
    """
    return begin >> construct_optical_coherent_pluggable_subscription >> store_process_subscription()


__all__ = [
    "CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS",
    "construct_optical_coherent_pluggable_subscription",
    "create_optical_coherent_pluggable",
    "create_optical_coherent_pluggable_form_generator",
    "populate_optical_coherent_pluggable_block",
    "populate_optical_coherent_pluggable_block_step",
]
