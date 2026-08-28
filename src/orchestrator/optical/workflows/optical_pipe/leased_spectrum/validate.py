"""Validate Optical Leased Spectrum workflow.

This module ships the ready-to-use ``validate_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the
importable parts: the state loading step, the termination check step and the
passband retrieval step. Consumers with their own model that has-a the
shipped block declare their own ``@validate_workflow`` with
:data:`LEASED_SPECTRUM_VALIDATE_STEPS`.
"""

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.optical_port import check_fiber_terminating_port
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrum
from orchestrator.optical.workflows.optical_pipe.shared import (
    load_optical_pipe_block,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


@step("Load Initial State")
def load_initial_state_leased_spectrum(subscription: OpticalLeasedSpectrum) -> State:
    """Load the initial state of the Optical Leased Spectrum pipe."""
    return {"subscription": subscription}


@step("Check Leased Spectrum Terminations")
def check_leased_spectrum_terminations(subscription: OpticalLeasedSpectrum) -> State:
    """Verify that the terminating ports of the leased spectrum pipe are correctly configured."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    check_fiber_terminating_port(port_a, port_b)
    check_fiber_terminating_port(port_b, port_a)
    return {}


#: Validation steps of the Optical Leased Spectrum family. The block is put in
#: the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` and the refreshed
#: passbands are persisted by the last step; the subscription description
#: refresh is a shared step that reads the block from the state.
LEASED_SPECTRUM_VALIDATE_STEPS: StepList = (
    begin
    >> load_initial_state_leased_spectrum
    >> load_optical_pipe_block
    >> set_optical_pipe_subscription_description
    >> check_leased_spectrum_terminations
    >> retrieve_optical_pipe_used_passbands
    >> save_optical_pipe_block
)


@validate_workflow()
def validate_leased_spectrum() -> StepList:
    """Workflow to validate an Optical Leased Spectrum subscription."""
    return begin >> LEASED_SPECTRUM_VALIDATE_STEPS


__all__ = [
    "LEASED_SPECTRUM_VALIDATE_STEPS",
    "validate_leased_spectrum",
]
