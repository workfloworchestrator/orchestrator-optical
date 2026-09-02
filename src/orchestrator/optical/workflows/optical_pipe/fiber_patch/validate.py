"""Validate Optical Fiber Patch workflow.

This module ships the ready-to-use ``validate_fiber_patch`` workflow for the
shipped Optical Fiber Patch product type, together with the importable parts:
the state loading step, the shared subscription description step and the
termination check step. Consumers with their own model that has-a the shipped
block declare their own ``@validate_workflow`` with
:data:`FIBER_PATCH_VALIDATE_STEPS`; consumer models that compose the block
under a different attribute name can put the block in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the description step.
"""

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.port import check_fiber_terminating_port
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatchSubscription
from orchestrator.optical.workflows.optical_pipe.shared import (
    load_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


@step("Load Initial State")
def load_initial_state_fiber_patch(subscription: OpticalFiberPatchSubscription) -> State:
    """Load the initial state of the Optical Fiber Patch."""
    return {"subscription": subscription}


@step("Check Fiber Patch Terminations")
def check_patch_terminations(subscription: OpticalFiberPatchSubscription) -> State:
    """Verify that the terminating ports of the fiber patch are correctly configured."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    pipe_type = subscription.optical_pipe.optical_pipe_type
    check_fiber_terminating_port(port_a, port_b, pipe_type)
    check_fiber_terminating_port(port_b, port_a, pipe_type)
    return {}


#: Validation steps of the Optical Fiber Patch family. The block is loaded
#: into the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` so the shared
#: subscription description refresh can read it.
FIBER_PATCH_VALIDATE_STEPS: StepList = (
    begin
    >> load_initial_state_fiber_patch
    >> load_optical_pipe_block
    >> set_optical_pipe_subscription_description
    >> check_patch_terminations
)


@validate_workflow()
def validate_fiber_patch() -> StepList:
    """Workflow to validate an Optical Fiber Patch subscription."""
    return begin >> FIBER_PATCH_VALIDATE_STEPS


__all__ = [
    "FIBER_PATCH_VALIDATE_STEPS",
    "validate_fiber_patch",
]
