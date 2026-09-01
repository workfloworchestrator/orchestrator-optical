"""Validate Optical Fiber Span workflow.

This module ships the ready-to-use ``validate_fiber_span`` workflow for the
shipped Optical Fiber Span product type, together with the importable parts:
the state loading step, the shared subscription description step and the
termination check steps. Consumers with their own model that has-a the
shipped block declare their own ``@validate_workflow`` with
:data:`FIBER_SPAN_VALIDATE_STEPS`; consumer models that compose the block
under a different attribute name can put the block in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the description step.
"""

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.port import check_fiber_terminating_port
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpanSubscription
from orchestrator.optical.workflows.optical_pipe.shared import (
    load_optical_pipe_block,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


@step("Load Initial State")
def load_initial_state_fiber_span(subscription: OpticalFiberSpanSubscription) -> State:
    """Load the initial state of the Optical Fiber Span."""
    return {"subscription": subscription}


@step("Check Fiber Span Terminations")
def check_span_terminations(subscription: OpticalFiberSpanSubscription) -> State:
    """Verify that the terminating line ports of the fiber span are correctly configured."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    check_fiber_terminating_port(port_a, port_b)
    check_fiber_terminating_port(port_b, port_a)
    return {}


#: Validation steps of the Optical Fiber Span family. The block is put in the
#: state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` and the refreshed passbands
#: are persisted by the last step; the subscription description refresh is a
#: shared step that reads the block from the state.
FIBER_SPAN_VALIDATE_STEPS: StepList = (
    begin
    >> load_initial_state_fiber_span
    >> load_optical_pipe_block
    >> set_optical_pipe_subscription_description
    >> check_span_terminations
    >> retrieve_optical_pipe_used_passbands
    >> save_optical_pipe_block
)


@validate_workflow()
def validate_fiber_span() -> StepList:
    """Workflow to validate an Optical Fiber Span subscription."""
    return begin >> FIBER_SPAN_VALIDATE_STEPS


__all__ = [
    "FIBER_SPAN_VALIDATE_STEPS",
    "validate_fiber_span",
]
