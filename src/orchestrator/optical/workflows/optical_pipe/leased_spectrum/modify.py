"""Modify Optical Leased Spectrum Workflow."""

from collections.abc import Sequence
from functools import partial
from typing import Any

from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrum,
    OpticalLeasedSpectrumProvisioning,
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
    """Form generator for modifying an Optical Leased Spectrum pipe.

    Args:
        subscription_id: ID of the subscription being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    subscription = OpticalLeasedSpectrum.from_subscription(subscription_id)
    pipe = subscription.optical_pipe
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    class ModifyLeasedSpectrumForm(FormPage):
        customer_id: customer_choice
        optical_pipe_identifier: str = pipe.optical_pipe_identifier

    user_input = yield ModifyLeasedSpectrumForm
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


@step("Update Leased Spectrum Subscription")
def update_leased_spectrum(
    subscription: OpticalLeasedSpectrumProvisioning,
    customer_id: UUIDstr,
    optical_pipe_identifier: str,
) -> State:
    """Update subscription attributes."""
    subscription.optical_pipe.optical_pipe_identifier = optical_pipe_identifier
    subscription.customer_id = customer_id
    return {"subscription": subscription}


@step("Update Subscription Description")
def update_subscription_description(subscription: OpticalLeasedSpectrum) -> State:
    """Update subscription description."""
    subscription.description = optical_pipe_subscription_description(subscription)
    return {"subscription": subscription}


def modify_leased_spectrum_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the modify_leased_spectrum workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
        **kwargs: Extra arguments forwarded to the ``modify_workflow`` decorator.
    """

    @modify_workflow(
        initial_input_form=partial(
            initial_input_form_generator,
            extra_form_pages=extra_form_pages,
            extra_summary_fields=extra_summary_fields,
        ),
        **kwargs,
    )
    def modify_leased_spectrum() -> StepList:
        """Workflow to modify an existing Optical Leased Spectrum pipe."""
        return (
            pre_steps
            >> begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> update_leased_spectrum
            >> update_subscription_description
            >> set_status(SubscriptionLifecycle.ACTIVE)
            >> post_steps
        )

    return modify_leased_spectrum
