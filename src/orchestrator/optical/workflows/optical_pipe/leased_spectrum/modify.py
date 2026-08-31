"""Modify Optical Leased Spectrum workflow.

This module ships the ready-to-use ``modify_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the
importable parts: the FormPage of the modify form (as the
:func:`modify_leased_spectrum_form_pages` page sequence, prefilled with the
current subscription values) and the step list that updates and persists the
Optical Leased Spectrum block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages::

    user_input_dict = yield from modify_leased_spectrum_form_pages(
        subscription, block_field_name="optical_pipe"
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from pydantic_forms.types import FormGenerator, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrum
from orchestrator.optical.workflows.optical_pipe.shared import (
    load_optical_pipe_block,
    modify_optical_pipe_form_generator,
    modify_optical_pipe_form_pages,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
    update_optical_pipe_block,
)


def modify_leased_spectrum_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Yield the FormPage of the Optical Leased Spectrum modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page and returns the collected user input as a flat dict of the
    ``optical_*`` state keys, consumed by the shipped steps of
    :data:`MODIFY_LEASED_SPECTRUM_BLOCK_STEPS`. Consumers yield from it in one
    line inside their own modify form generator, optionally interleaving their
    own pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        subscription: The ACTIVE subscription model of the Optical Leased
            Spectrum product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Leased Spectrum block.

    Returns:
        The collected user input of the shipped pages.
    """
    return modify_optical_pipe_form_pages(subscription, block_field_name)


def modify_leased_spectrum_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalLeasedSpectrum,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Leased Spectrum subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the shipped page sequence
    (:func:`modify_leased_spectrum_form_pages`) and the summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Leased Spectrum product. Consumers that compose the shipped block
            under a different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Leased Spectrum block.
    """
    return (yield from modify_optical_pipe_form_generator(subscription_id, subscription_model, block_field_name))


#: Modify steps operating on the Optical Leased Spectrum block in the state.
#: Only the ``optical_pipe_name`` is written to the block; the block is
#: persisted by the last step, because workflow steps reload the subscription
#: from the database and would otherwise lose the mutations.
MODIFY_LEASED_SPECTRUM_BLOCK_STEPS: StepList = begin >> update_optical_pipe_block >> save_optical_pipe_block


@modify_workflow(initial_input_form=modify_leased_spectrum_form_generator)
def modify_leased_spectrum() -> StepList:
    """Workflow to modify an existing Optical Leased Spectrum pipe.

    The workflow is valid for the shipped :class:`OpticalLeasedSpectrum`
    product type only: it loads the block from the ``optical_pipe`` attribute
    of the shipped subscription models. Consumers with their own product type
    compose their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_pipe_block
        >> MODIFY_LEASED_SPECTRUM_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_LEASED_SPECTRUM_BLOCK_STEPS",
    "modify_leased_spectrum",
    "modify_leased_spectrum_form_pages",
]
