"""Workflow to terminate an Optical Coherent Pluggable subscription."""

from pydantic_forms.types import InputForm, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
)

logger = get_logger(__name__)


def terminate_initial_input_form_generator(subscription_id: UUIDstr, customer_id: UUIDstr) -> InputForm:  # noqa: ARG001
    """Confirmation form before terminating a pluggable subscription."""
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalCoherentPluggableForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore[assignment]

    return TerminateOpticalCoherentPluggableForm


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


additional_steps = begin


@terminate_workflow(
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_optical_coherent_pluggable() -> StepList:
    """Workflow to terminate an Optical Coherent Pluggable."""
    return begin >> deprovision_optical_coherent_pluggable
