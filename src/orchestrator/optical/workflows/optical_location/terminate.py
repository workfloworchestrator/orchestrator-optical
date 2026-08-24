"""Terminate Optical Module Location workflow.

This module ships the ready-to-use ``terminate_optical_module_location``
workflow for the shipped Optical Module Location product type, together
with the importable parts: the FormPage of the terminate confirmation form
(as the :func:`terminate_optical_module_location_form_pages` page sequence)
and the termination steps.

Consumers with their own model that has-a the shipped block declare their own
``@terminate_workflow`` with :data:`OPTICAL_MODULE_LOCATION_TERMINATE_STEPS`
and compose their own terminate form generator by yielding from the shipped
page sequence in one line.
"""

from typing import cast

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow


def terminate_optical_module_location_form(subscription_id: UUIDstr) -> type[FormPage]:
    """Return the confirmation FormPage of the Optical Module Location terminate form.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The confirmation FormPage of the shipped terminate form.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalModuleLocationForm(FormPage):
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

    return TerminateOpticalModuleLocationForm


def terminate_optical_module_location_form_pages(subscription_id: UUIDstr) -> FormGenerator:
    """Yield the FormPage of the Optical Module Location terminate form.

    This is the shipped terminate form as a page sequence: it yields the
    confirmation page and returns the collected user input. Consumers yield
    from it in one line inside their own terminate form generator, optionally
    adding their own pages.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield terminate_optical_module_location_form(subscription_id)
    return user_input.model_dump()


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
) -> FormGenerator:
    """Generate the confirmation form before terminating an Optical Module Location subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
    """
    return terminate_optical_module_location_form_pages(subscription_id)


@step("Deprovision Optical Module Location")
def deprovision_optical_module_location(subscription: SubscriptionModel) -> State:  # noqa: ARG001
    """Clean up and deprovision the Optical Module Location resource."""
    return {}


#: Termination steps of the Optical Module Location family. Consumers
#: declare their own ``@terminate_workflow`` with this step list and the
#: shipped :func:`terminate_initial_input_form_generator` form.
OPTICAL_MODULE_LOCATION_TERMINATE_STEPS: StepList = begin >> deprovision_optical_module_location


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_optical_module_location() -> StepList:
    """Workflow to terminate an Optical Module Location subscription."""
    return begin >> OPTICAL_MODULE_LOCATION_TERMINATE_STEPS


__all__ = [
    "OPTICAL_MODULE_LOCATION_TERMINATE_STEPS",
    "deprovision_optical_module_location",
    "terminate_initial_input_form_generator",
    "terminate_optical_module_location",
    "terminate_optical_module_location_form",
    "terminate_optical_module_location_form_pages",
]
