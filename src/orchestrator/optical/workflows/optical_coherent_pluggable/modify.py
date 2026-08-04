"""Workflow to modify an Optical Coherent Pluggable subscription."""

from typing import Annotated

from pydantic import Field
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
    OpticalCoherentPluggableProvisioning,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.create import (
    subscription_description,
)
from orchestrator.optical.workflows.shared import modify_summary_form

logger = get_logger(__name__)

Instruction = Annotated[
    str,
    Field(
        "Modify port description or firmware version. Unchanged fields will remain intact.",
        title="Instruction",
        json_schema_extra={"disabled": True},
    ),
]


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    """Input form for modifying Coherent Pluggable attributes."""
    subscription = OpticalCoherentPluggable.from_subscription(subscription_id)
    pluggable = subscription.optical_coherent_pluggable

    class ModifyOpticalCoherentPluggableForm(FormPage):
        instruction: Instruction
        optical_port_description: str | None = pluggable.optical_port_description
        optical_coherent_pluggable_firmware_version: str = pluggable.optical_coherent_pluggable_firmware_version

    user_input = yield ModifyOpticalCoherentPluggableForm
    user_input_dict = user_input.model_dump()

    summary_fields = [
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    ]
    yield from modify_summary_form(user_input_dict, subscription.optical_coherent_pluggable, summary_fields)

    return user_input_dict | {"subscription": subscription}


@step("Updating subscription model")
def update_subscription(
    subscription: OpticalCoherentPluggableProvisioning,
    optical_port_description: str | None,
    optical_coherent_pluggable_firmware_version: str,
) -> State:
    """Update fields on the Optical Coherent Pluggable subscription."""
    pluggable = subscription.optical_coherent_pluggable

    # None means "unchanged": clearing the description is not supported by the form.
    if optical_port_description is not None:
        pluggable.optical_port_description = optical_port_description

    if optical_coherent_pluggable_firmware_version:
        pluggable.optical_coherent_pluggable_firmware_version = optical_coherent_pluggable_firmware_version

    return {"subscription": subscription}


@step("Updating subscription description")
def update_subscription_description(
    subscription: OpticalCoherentPluggableProvisioning,
) -> State:
    """Refresh the human-readable description for the subscription."""
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


additional_steps = begin


@modify_workflow(
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_optical_coherent_pluggable() -> StepList:
    """Workflow to modify an Optical Coherent Pluggable."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> update_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
