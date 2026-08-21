"""Modify Optical Fiber Span Workflow."""

from collections.abc import Sequence

from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import (
    OpticalFiberSpan,
    OpticalFiberSpanProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import (
    modify_pipe_summary_form,
    optical_pipe_subscription_description,
)

logger = get_logger(__name__)


def initial_input_form_generator(
    subscription_id: UUIDstr,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Form generator for modifying an Optical Fiber Span.

    Args:
        subscription_id: ID of the subscription being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    subscription = OpticalFiberSpan.from_subscription(subscription_id)
    pipe = subscription.optical_pipe
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    class ModifyFiberSpanForm(FormPage):
        customer_id: customer_choice
        optical_pipe_identifier: str = pipe.optical_pipe_identifier

    user_input = yield ModifyFiberSpanForm
    user_input_dict = user_input.model_dump()

    summary_fields = ["customer_id", "optical_pipe_identifier"]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from modify_pipe_summary_form(
        user_input_dict,
        pipe,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
        extra_summary_fields=extra_summary_fields,
    )

    return user_input_dict | {"subscription": subscription}


@step("Update Fiber Span Subscription")
def update_fiber_span(
    subscription: OpticalFiberSpanProvisioning,
    customer_id: UUIDstr,
    optical_pipe_identifier: str,
) -> State:
    """Update subscription attributes."""
    subscription.optical_pipe.optical_pipe_identifier = optical_pipe_identifier
    subscription.customer_id = customer_id
    return {"subscription": subscription}


@step("Update Subscription Description")
def update_subscription_description(subscription: OpticalFiberSpan) -> State:
    """Update the description of the subscription."""
    subscription.description = optical_pipe_subscription_description(subscription)
    return {"subscription": subscription}


@modify_workflow(initial_input_form=initial_input_form_generator)
def modify_fiber_span() -> StepList:
    """Workflow to modify an existing Optical Fiber Span."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_fiber_span
        >> update_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
