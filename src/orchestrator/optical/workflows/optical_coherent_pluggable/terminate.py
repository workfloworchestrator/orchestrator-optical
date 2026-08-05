"""Workflow to terminate an Optical Coherent Pluggable subscription."""

from collections.abc import Sequence
from functools import partial
from typing import Any

from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
)

logger = get_logger(__name__)


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
    extra_form_pages: Sequence[type[FormPage]] = (),
) -> FormGenerator:
    """Confirmation form before terminating a pluggable subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalCoherentPluggableForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore[assignment]

    user_input = yield TerminateOpticalCoherentPluggableForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    return user_input_dict


@step("Deprovision Optical Coherent Pluggable")
def deprovision_optical_coherent_pluggable(
    subscription: OpticalCoherentPluggable,
) -> State:
    """Clean up and deprovision the Coherent Pluggable resource."""
    logger.info(
        "Deprovisioning Optical Coherent Pluggable",
        subscription_id=subscription.subscription_id,
        part_number=subscription.optical_coherent_pluggable_part_number,
    )
    return {}


def terminate_optical_coherent_pluggable_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the terminate_optical_coherent_pluggable workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
        **kwargs: Extra arguments forwarded to the ``terminate_workflow`` decorator.
    """

    @terminate_workflow(
        initial_input_form=partial(
            terminate_initial_input_form_generator,
            extra_form_pages=extra_form_pages,
        ),
        **kwargs,
    )
    def terminate_optical_coherent_pluggable() -> StepList:
        """Workflow to terminate an Optical Coherent Pluggable."""
        return pre_steps >> begin >> deprovision_optical_coherent_pluggable >> post_steps

    return terminate_optical_coherent_pluggable
