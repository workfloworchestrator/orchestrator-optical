"""Terminate Optical Coherent Pluggable workflow.

This module ships the ready-to-use ``terminate_optical_coherent_pluggable``
workflow for the shipped Optical Coherent Pluggable product type, together
with the importable parts: the confirmation form and the termination steps.
Consumers with their own model that has-a the shipped block declare their own
``@terminate_workflow`` with :data:`OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS`
and the shipped :func:`terminate_initial_input_form_generator` form.
"""

from collections.abc import Sequence
from typing import cast

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
    extra_form_pages: Sequence[type[FormPage]] = (),
) -> FormGenerator:
    """Generate the confirmation form before terminating a Coherent Pluggable subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalCoherentPluggableForm(FormPage):
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

    user_input = yield TerminateOpticalCoherentPluggableForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    return user_input_dict


@step("Deprovision Optical Coherent Pluggable")
def deprovision_optical_coherent_pluggable(subscription: SubscriptionModel) -> State:  # noqa: ARG001
    """Clean up and deprovision the Coherent Pluggable resource."""
    return {}


#: Termination steps of the Optical Coherent Pluggable family. Consumers
#: declare their own ``@terminate_workflow`` with this step list and the
#: shipped :func:`terminate_initial_input_form_generator` form.
OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS: StepList = begin >> deprovision_optical_coherent_pluggable


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_optical_coherent_pluggable() -> StepList:
    """Workflow to terminate an Optical Coherent Pluggable subscription."""
    return begin >> OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS


__all__ = [
    "OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS",
    "deprovision_optical_coherent_pluggable",
    "terminate_initial_input_form_generator",
    "terminate_optical_coherent_pluggable",
]
