"""Validate Optical Leased Spectrum workflow.

This module ships the ready-to-use ``validate_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the importable
parts: the state loading step and the block-level validation step list
(:data:`VALIDATE_LEASED_SPECTRUM_BLOCK_STEPS`). Consumers with their own model
that has-a the shipped block declare their own ``@validate_workflow`` composing
the state loading step, :func:`load_optical_pipe_block`,
:data:`VALIDATE_LEASED_SPECTRUM_BLOCK_STEPS` and the shared description step;
consumer models that compose the block under a different attribute name put the
block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the description
step.
"""

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrumSubscription
from orchestrator.optical.workflows.optical_pipe.shared import (
    check_pipe_terminations,
    load_optical_pipe_block,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


@step("Load Initial State")
def load_initial_state_leased_spectrum(subscription: OpticalLeasedSpectrumSubscription) -> State:
    """Load the initial state of the Optical Leased Spectrum pipe."""
    return {"subscription": subscription}


#: Block-level validation steps of the Optical Leased Spectrum family. Every
#: step operates only on the Optical Pipe block found in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (which the caller's
#: :func:`load_optical_pipe_block` step puts there): the terminations are
#: checked against their remote end, the passbands in use are refreshed from
#: the devices and the block (with the refreshed passbands) is persisted by the
#: last step. Consumers with their own model run this list after loading their
#: block into the state and finalize the subscription with the shared
#: description step.
VALIDATE_LEASED_SPECTRUM_BLOCK_STEPS: StepList = (
    begin >> check_pipe_terminations >> retrieve_optical_pipe_used_passbands >> save_optical_pipe_block
)


@validate_workflow()
def validate_leased_spectrum() -> StepList:
    """Workflow to validate an Optical Leased Spectrum subscription.

    The subscription-level wiring (loading the subscription and its block into
    the state, then recomputing the subscription description from the validated
    block) is kept in the workflow, while the shipped
    :data:`VALIDATE_LEASED_SPECTRUM_BLOCK_STEPS` operate only on the block
    found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    return (
        begin
        >> load_initial_state_leased_spectrum
        >> load_optical_pipe_block
        >> VALIDATE_LEASED_SPECTRUM_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
    )


__all__ = [
    "VALIDATE_LEASED_SPECTRUM_BLOCK_STEPS",
    "validate_leased_spectrum",
]
