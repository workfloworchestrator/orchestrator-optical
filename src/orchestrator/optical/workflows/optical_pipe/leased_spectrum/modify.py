"""Modify Optical Leased Spectrum Workflow."""

from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrum,
    OpticalLeasedSpectrumProvisioning,
)
from orchestrator.optical.workflows.optical_pipe.shared import (
    modify_pipe_summary_form,
    optical_pipe_subscription_description,
)

logger = get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    """Form generator for modifying an Optical Leased Spectrum pipe."""
    subscription = OpticalLeasedSpectrum.from_subscription(subscription_id)
    pipe = subscription.optical_pipe

    class ModifyLeasedSpectrumForm(FormPage):
        optical_pipe_identifier: str = pipe.optical_pipe_identifier

    user_input = yield ModifyLeasedSpectrumForm
    user_input_dict = user_input.model_dump()

    summary_fields = ["optical_pipe_identifier"]
    yield from modify_pipe_summary_form(user_input_dict, pipe, summary_fields)

    return user_input_dict | {"subscription": subscription}


@step("Update Leased Spectrum Subscription")
def update_leased_spectrum(
    subscription: OpticalLeasedSpectrumProvisioning,
    optical_pipe_identifier: str,
) -> State:
    """Update subscription attributes."""
    subscription.optical_pipe.optical_pipe_identifier = optical_pipe_identifier
    return {"subscription": subscription}


@step("Update Subscription Description")
def update_subscription_description(subscription: OpticalLeasedSpectrum) -> State:
    """Update subscription description."""
    subscription.description = optical_pipe_subscription_description(subscription)
    return {"subscription": subscription}


additional_steps = begin


@modify_workflow(
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_leased_spectrum() -> StepList:
    """Workflow to modify an existing Optical Leased Spectrum pipe."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_leased_spectrum
        >> update_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
