"""Modify Optical Fiber Span workflow.

This module ships the ready-to-use ``modify_fiber_span`` workflow for the
shipped Optical Fiber Span product type, together with the importable parts:
the FormPage of the modify form (as the
:func:`modify_fiber_span_form_pages` page sequence, prefilled with the
current subscription values) and the step list that updates and persists the
Optical Pipe block found in the state under ``OPTICAL_PIPE_BLOCK_STATE_KEY``.

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
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpan
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import (
    load_optical_pipe_block,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
    update_optical_pipe_block,
)
from orchestrator.optical.workflows.shared import modify_summary_form


def modify_fiber_span_form(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_pipe",
) -> type[FormPage]:
    """Return the modify FormPage of the Optical Fiber Span subscription.

    The page is prefilled with the current values of the subscription, so
    unchanged fields remain intact.

    Args:
        subscription: The ACTIVE subscription model of the Optical Fiber Span
            product being modified (any consumer model that has-a the shipped
            block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Pipe block.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """
    pipe = getattr(subscription, block_field_name)
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    class ModifyFiberSpanForm(FormPage):
        customer_id: customer_choice
        optical_pipe_name: str = pipe.optical_pipe_name

    return ModifyFiberSpanForm


def modify_fiber_span_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Yield the FormPage of the Optical Fiber Span modify form.

    This is the shipped modify form as a page sequence: it yields the
    prefilled modify page and returns the collected user input as a flat dict
    of the ``optical_*`` state keys plus ``customer_id``, consumed by the
    shipped steps of :data:`MODIFY_FIBER_SPAN_BLOCK_STEPS`. Consumers yield
    from it in one line inside their own modify form generator, optionally
    interleaving their own pages.

    Args:
        subscription: The ACTIVE subscription model of the Optical Fiber Span
            product being modified (any consumer model that has-a the shipped
            block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Pipe block.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield modify_fiber_span_form(subscription, block_field_name)
    return user_input.model_dump()


def modify_fiber_span_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalFiberSpan,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Fiber Span subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the shipped
    page sequence (:func:`modify_fiber_span_form_pages`) and the summary
    form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Fiber Span product. Consumers that compose the shipped block
            under a different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Pipe block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    pipe = getattr(subscription, block_field_name)

    user_input_dict = yield from modify_fiber_span_form_pages(subscription, block_field_name)

    summary_fields = ["customer_id", "optical_pipe_name"]
    yield from modify_summary_form(
        user_input_dict,
        pipe,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
    )

    return user_input_dict | {"subscription": subscription}


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
