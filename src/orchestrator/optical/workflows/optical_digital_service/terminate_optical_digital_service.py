"""Terminate Optical Digital Service workflow.

This module ships the ready-to-use ``terminate_optical_digital_service``
workflow for the shipped Optical Digital Service product type, together with
the importable parts: the FormPage of the terminate confirmation form (as the
:func:`terminate_optical_digital_service_form_pages` page sequence) and the
termination steps.

Consumers with their own model that has-a the shipped block declare their own
``@terminate_workflow`` with :data:`TERMINATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS`
and compose their own terminate form generator by yielding from the shipped page
sequence in one line.
"""

from typing import cast

from pydantic_forms.types import FormGenerator, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.optical_digital_service.shared import (
    delete_optical_digital_sections,
    factory_reset_optical_digital_clients,
    factory_reset_optical_digital_crossconnects,
    factory_reset_optical_digital_lines,
    load_optical_digital_service_block,
    prune_departing_service_channel_labels,
    refresh_optical_digital_passbands_after_teardown,
)


def terminate_optical_digital_service_form(subscription_id: UUIDstr) -> type[FormPage]:
    """Return the confirmation FormPage of the Optical Digital Service terminate form.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The confirmation FormPage of the shipped terminate form.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalDigitalServiceForm(FormPage):
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

    return TerminateOpticalDigitalServiceForm


def terminate_optical_digital_service_form_pages(subscription_id: UUIDstr) -> FormGenerator:
    """Yield the FormPage of the Optical Digital Service terminate form.

    This is the shipped terminate form as a page sequence: it yields the
    confirmation page and returns the collected user input. Consumers yield
    from it in one line inside their own terminate form generator, optionally
    adding their own pages.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield terminate_optical_digital_service_form(subscription_id)
    return user_input.model_dump()


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
) -> FormGenerator:
    """Generate the confirmation form before terminating an Optical Digital Service subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).

    Returns:
        The collected user input of the confirmation page.
    """
    user_input = yield from terminate_optical_digital_service_form_pages(subscription_id)
    return user_input


#: Termination steps operating on the Optical Digital Service block in the
#: state. The cross-connects and client ports are always reset; shared circuit
#: labels are pruned of the departing service name first, then the line ports
#: and optical circuits are torn down only when the service is the last client
#: of its transport channels (shared channels stay up for the remaining
#: services, see the gate in the shared steps), and the block is persisted by
#: the last step.
TERMINATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = (
    begin
    >> factory_reset_optical_digital_crossconnects
    >> factory_reset_optical_digital_clients
    >> factory_reset_optical_digital_lines
    >> prune_departing_service_channel_labels
    >> delete_optical_digital_sections
    >> refresh_optical_digital_passbands_after_teardown
    >> save_optical_module_block
)


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_optical_digital_service() -> StepList:
    """Workflow to terminate an Optical Digital Service subscription.

    The workflow is composed from the shipped parts: the block is loaded from
    the ``optical_digital_service`` attribute of the shipped subscription
    models and the shipped block steps reset the transponders, delete the
    circuits when this is the last client, and persist the refreshed passbands.
    It is therefore only valid for the shipped product type; consumers with
    their own product type compose their own terminate workflow with the same
    parts.
    """
    return begin >> load_optical_digital_service_block >> TERMINATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS


__all__ = [
    "TERMINATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS",
    "terminate_initial_input_form_generator",
    "terminate_optical_digital_service",
    "terminate_optical_digital_service_form_pages",
]
