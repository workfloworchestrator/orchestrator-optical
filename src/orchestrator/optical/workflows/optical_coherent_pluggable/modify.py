"""Modify Optical Coherent Pluggable workflow.

This module ships the ready-to-use ``modify_optical_coherent_pluggable``
workflow for the shipped Optical Coherent Pluggable product type, together
with the importable parts: the FormPage of the modify form (as the
:func:`modify_optical_coherent_pluggable_form_pages` page sequence, prefilled
with the current subscription values) and the step list that updates and
persists the Optical Coherent Pluggable block found in the state under
``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages::

    user_input_dict = yield from modify_optical_coherent_pluggable_form_pages(
        subscription, block_field_name="router"
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from typing import Annotated

from pydantic import Field
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
)
from orchestrator.optical.workflows.customer import customer_choice_form_pages
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY,
    load_optical_coherent_pluggable_block,
    optical_coherent_pluggable_block_from_state,
    save_optical_coherent_pluggable_block,
    update_optical_coherent_pluggable_subscription_description,
)
from orchestrator.optical.workflows.shared import modify_summary_form

Instruction = Annotated[
    str,
    Field(
        "Modify port description or firmware version. Unchanged fields will remain intact.",
        title="Instruction",
        json_schema_extra={"disabled": True},
    ),
]


def modify_optical_coherent_pluggable_form(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_coherent_pluggable",
) -> type[FormPage]:
    """Return the modify FormPage of the Optical Coherent Pluggable subscription.

    The page is prefilled with the current values of the subscription, so
    unchanged fields remain intact.

    Args:
        subscription: The ACTIVE subscription model of the Optical Coherent
            Pluggable product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Coherent Pluggable block.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """
    pluggable = getattr(subscription, block_field_name)

    class ModifyOpticalCoherentPluggableForm(FormPage):
        instruction: Instruction
        optical_port_description: str | None = pluggable.optical_port_description
        optical_coherent_pluggable_firmware_version: str = pluggable.optical_coherent_pluggable_firmware_version

    return ModifyOpticalCoherentPluggableForm


def modify_optical_coherent_pluggable_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_coherent_pluggable",
) -> FormGenerator:
    """Yield the FormPage of the Optical Coherent Pluggable modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page and returns the collected user input as a flat dict of the
    ``optical_*`` state keys, consumed by the shipped steps of
    :data:`MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS`. Consumers yield from
    it in one line inside their own modify form generator, optionally
    interleaving their own pages. The customer of the subscription is collected
    separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_pages`).

    Args:
        subscription: The ACTIVE subscription model of the Optical Coherent
            Pluggable product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Coherent Pluggable block.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield modify_optical_coherent_pluggable_form(subscription, block_field_name)
    return user_input.model_dump()


def modify_optical_coherent_pluggable_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalCoherentPluggable,
    block_field_name: str = "optical_coherent_pluggable",
) -> FormGenerator:
    """Generate the initial input form for modifying a Coherent Pluggable subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the shipped
    page sequence (:func:`modify_optical_coherent_pluggable_form_pages`) and
    the summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Coherent
            Pluggable product. Consumers that compose the shipped block under a
            different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Coherent Pluggable block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    pluggable = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_pages(include=str(subscription.customer_id))
    user_input_dict.update((yield from modify_optical_coherent_pluggable_form_pages(subscription, block_field_name)))

    summary_fields = [
        "customer_id",
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    ]
    yield from modify_summary_form(
        user_input_dict,
        pluggable,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Optical Coherent Pluggable block")
def update_optical_coherent_pluggable_block(
    optical_coherent_pluggable_block: OpticalCoherentPluggableBlockProvisioning,
    optical_port_description: str | None,
    optical_coherent_pluggable_firmware_version: str,
) -> State:
    """Update the Optical Coherent Pluggable block in the state from the modify-form keys.

    None means "unchanged": clearing the description is not supported by the form.
    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from the database by its ``subscription_instance_id``
    before it is updated.

    Args:
        optical_coherent_pluggable_block: The Optical Coherent Pluggable block
            in the state under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``
            (the provisioning variant, while the subscription is being modified).
        optical_port_description: Description of the port.
        optical_coherent_pluggable_firmware_version: Firmware version of the pluggable.

    Raises:
        ValueError: If there is no Optical Coherent Pluggable block in the state
            under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``.
    """
    pluggable = optical_coherent_pluggable_block_from_state(optical_coherent_pluggable_block)
    if pluggable is None:
        msg = "No Optical Coherent Pluggable block in the state under OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY"
        raise ValueError(msg)

    if optical_port_description is not None:
        pluggable.optical_port_description = optical_port_description

    if optical_coherent_pluggable_firmware_version:
        pluggable.optical_coherent_pluggable_firmware_version = optical_coherent_pluggable_firmware_version

    return {OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: pluggable}


#: Modify steps operating on the Optical Coherent Pluggable block in the state.
#: The block is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS: StepList = (
    begin >> update_optical_coherent_pluggable_block >> save_optical_coherent_pluggable_block
)


@modify_workflow(initial_input_form=modify_optical_coherent_pluggable_form_generator)
def modify_optical_coherent_pluggable() -> StepList:
    """Workflow to modify an existing Optical Coherent Pluggable subscription.

    The workflow is valid for the shipped :class:`OpticalCoherentPluggable`
    product type only: it loads the block from the
    ``optical_coherent_pluggable`` attribute of the shipped subscription
    models. Consumers with their own product type compose their own modify
    workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_coherent_pluggable_block
        >> MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS
        >> update_optical_coherent_pluggable_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS",
    "modify_optical_coherent_pluggable",
    "modify_optical_coherent_pluggable_form",
    "modify_optical_coherent_pluggable_form_generator",
    "modify_optical_coherent_pluggable_form_pages",
    "update_optical_coherent_pluggable_block",
]
