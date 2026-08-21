"""Modify Optical Coherent Pluggable workflow.

This module ships the ready-to-use ``modify_optical_coherent_pluggable``
workflow for the shipped Optical Coherent Pluggable product type, together
with the importable parts: the form generator (parameterized by the
subscription model and the attribute name of the composed block) and the step
list that updates and persists the Optical Coherent Pluggable block found in
the state under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``. Consumers that
keep the shipped product type register the shipped workflow; consumers with
their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts.
"""

from collections.abc import Sequence
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
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY,
    load_optical_coherent_pluggable_block,
    save_optical_coherent_pluggable_block,
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


def modify_optical_coherent_pluggable_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalCoherentPluggable,
    block_field_name: str = "optical_coherent_pluggable",
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying a Coherent Pluggable subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Coherent
            Pluggable product. Consumers that compose the shipped block under a
            different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Coherent Pluggable block.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    pluggable = getattr(subscription, block_field_name)
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    class ModifyOpticalCoherentPluggableForm(FormPage):
        customer_id: customer_choice
        instruction: Instruction
        optical_port_description: str | None = pluggable.optical_port_description
        optical_coherent_pluggable_firmware_version: str = pluggable.optical_coherent_pluggable_firmware_version

    user_input = yield ModifyOpticalCoherentPluggableForm
    user_input_dict = user_input.model_dump()

    summary_fields = [
        "customer_id",
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    ]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from modify_summary_form(
        user_input_dict,
        pluggable,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
        extra_summary_fields=extra_summary_fields,
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

    Args:
        optical_coherent_pluggable_block: The Optical Coherent Pluggable block
            in the state under ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``
            (the provisioning variant, while the subscription is being modified).
        optical_port_description: Description of the port.
        optical_coherent_pluggable_firmware_version: Firmware version of the pluggable.
    """
    if optical_port_description is not None:
        optical_coherent_pluggable_block.optical_port_description = optical_port_description

    if optical_coherent_pluggable_firmware_version:
        optical_coherent_pluggable_block.optical_coherent_pluggable_firmware_version = (
            optical_coherent_pluggable_firmware_version
        )

    return {OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: optical_coherent_pluggable_block}


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
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS",
    "modify_optical_coherent_pluggable",
    "modify_optical_coherent_pluggable_form_generator",
    "update_optical_coherent_pluggable_block",
]
