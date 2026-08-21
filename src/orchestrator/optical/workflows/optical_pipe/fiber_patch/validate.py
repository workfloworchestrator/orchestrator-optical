"""Validate Optical Fiber Patch Workflow."""

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.optical_port import check_fiber_terminating_port
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatch
from orchestrator.optical.workflows.optical_pipe.shared import optical_pipe_subscription_description

logger = get_logger(__name__)


@step("Load Initial State")
def load_initial_state_fiber_patch(subscription: OpticalFiberPatch) -> State:
    """Load the initial state of the Optical Fiber Patch."""
    return {"subscription": subscription}


@step("Update Subscription Description")
def update_subscription_description(subscription: OpticalFiberPatch) -> State:
    """Update subscription description during validation."""
    subscription.description = optical_pipe_subscription_description(subscription)
    return {"subscription_description": subscription.description}


@step("Check Fiber Patch Terminations")
def check_patch_terminations(subscription: OpticalFiberPatch) -> State:
    """Verify that the terminating ports of the fiber patch are correctly configured."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    check_fiber_terminating_port(port_a, port_b)
    check_fiber_terminating_port(port_b, port_a)
    return {}


@validate_workflow()
def validate_fiber_patch() -> StepList:
    """Workflow to validate an Optical Fiber Patch subscription."""
    return begin >> load_initial_state_fiber_patch >> update_subscription_description >> check_patch_terminations
