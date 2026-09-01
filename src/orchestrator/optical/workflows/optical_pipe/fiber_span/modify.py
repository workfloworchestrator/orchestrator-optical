"""Modify Optical Fiber Span workflow.

This module ships the ready-to-use ``modify_fiber_span`` workflow for the
shipped Optical Fiber Span product type, together with the importable parts:
the FormPage of the modify form (as the
:func:`modify_fiber_span_form_pages` page sequence, prefilled with the
current subscription values) and the step list that updates and persists the
Optical Pipe block found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages::

    user_input_dict = yield from modify_fiber_span_form_pages(
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
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpanSubscription
from orchestrator.optical.workflows.optical_pipe.shared import (
    load_optical_pipe_block,
    modify_optical_pipe_form_generator,
    modify_optical_pipe_form_pages,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
    update_optical_pipe_block,
)


def modify_fiber_span_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Yield the FormPage of the Optical Fiber Span modify form.

    This is the shipped modify form as a page sequence: it yields the
    prefilled modify page and returns the collected user input as a flat dict
    of the ``optical_*`` state keys, consumed by the shipped steps of
    :data:`MODIFY_FIBER_SPAN_BLOCK_STEPS`. Consumers yield from it in one line
    inside their own modify form generator, optionally interleaving their own
    pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        subscription: The ACTIVE subscription model of the Optical Fiber Span
            product being modified (any consumer model that has-a the shipped
            block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Pipe block.

    Returns:
        The collected user input of the shipped pages.
    """
    return modify_optical_pipe_form_pages(subscription, block_field_name)


def modify_fiber_span_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalFiberSpanSubscription,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Fiber Span subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the shipped page sequence (:func:`modify_fiber_span_form_pages`) and
    the summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Fiber Span product. Consumers that compose the shipped block
            under a different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Pipe block.
    """
    return (yield from modify_optical_pipe_form_generator(subscription_id, subscription_model, block_field_name))


#: Modify steps operating on the Optical Pipe block in the state. The block
#: is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_FIBER_SPAN_BLOCK_STEPS: StepList = begin >> update_optical_pipe_block >> save_optical_pipe_block


@modify_workflow(initial_input_form=modify_fiber_span_form_generator)
def modify_fiber_span() -> StepList:
    """Workflow to modify an existing Optical Fiber Span subscription.

    The workflow is valid for the shipped :class:`OpticalFiberSpan` product
    type only: it loads the block from the ``optical_pipe`` attribute of the
    shipped subscription models. Consumers with their own product type compose
    their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_pipe_block
        >> MODIFY_FIBER_SPAN_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_FIBER_SPAN_BLOCK_STEPS",
    "modify_fiber_span",
    "modify_fiber_span_form_pages",
]
