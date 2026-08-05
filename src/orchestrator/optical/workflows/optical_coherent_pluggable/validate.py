"""Workflow to validate an Optical Coherent Pluggable subscription."""

from typing import Any

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.create import (
    subscription_description,
)

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_optical_coherent_pluggable(
    subscription: OpticalCoherentPluggable,
) -> State:
    """Load the subscription state for validation."""
    return {"subscription": subscription}


@step("Update subscription description")
def update_subscription_description(
    subscription: OpticalCoherentPluggable,
) -> State:
    """Ensure subscription description is consistent with state."""
    subscription.description = subscription_description(subscription)
    return {"subscription_description": subscription.description}


@step("Validate Optical Coherent Pluggable state")
def validate_pluggable_state(subscription: OpticalCoherentPluggable) -> State:
    """Verify state and integrity of the Optical Coherent Pluggable."""
    pluggable = subscription.optical_coherent_pluggable
    logger.info(
        "Validating Optical Coherent Pluggable",
        port_name=pluggable.optical_port_name,
        host_node=pluggable.optical_port_host_node.pqdn,
        firmware=pluggable.optical_coherent_pluggable_firmware_version,
    )
    return {}


def validate_optical_coherent_pluggable_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    **kwargs: Any,
) -> Workflow:
    """Build the validate_optical_coherent_pluggable workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        **kwargs: Extra arguments forwarded to the ``validate_workflow`` decorator.
    """

    @validate_workflow(**kwargs)
    def validate_optical_coherent_pluggable() -> StepList:
        """Workflow to validate an Optical Coherent Pluggable."""
        return (
            pre_steps
            >> begin
            >> load_initial_state_optical_coherent_pluggable
            >> update_subscription_description
            >> validate_pluggable_state
            >> post_steps
        )

    return validate_optical_coherent_pluggable
