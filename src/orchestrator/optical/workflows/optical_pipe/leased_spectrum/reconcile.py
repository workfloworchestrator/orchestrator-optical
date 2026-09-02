"""Reconcile Optical Leased Spectrum workflow.

This module ships the ready-to-use ``reconcile_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the importable
parts: the block-level step list that re-applies the pipe's terminations
configuration to the devices and re-verifies it. Reconcile takes no user
input: it pushes the subscription's existing configuration back onto the
devices (the same device configuration the create workflow performs) so the
external systems match the orchestrator's state again, then verifies the
result. Consumers with their own model that has-a the shipped block declare
their own ``@reconcile_workflow`` with
:data:`RECONCILE_LEASED_SPECTRUM_BLOCK_STEPS`.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import reconcile_workflow
from orchestrator.optical.workflows.optical_pipe.shared import (
    check_pipe_terminations,
    configure_pipe_terminations,
    load_optical_pipe_block,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)

#: Reconcile steps of the Optical Leased Spectrum family. Re-applies the
#: terminations configuration to the devices (the same device push the create
#: workflow performs), refreshes the passbands in use, persists the block and
#: re-verifies the terminations on the devices. Every step is block-level and
#: operates on the block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``;
#: the caller's load step provides it.
RECONCILE_LEASED_SPECTRUM_BLOCK_STEPS: StepList = (
    begin
    >> configure_pipe_terminations
    >> retrieve_optical_pipe_used_passbands
    >> save_optical_pipe_block
    >> check_pipe_terminations
)


@reconcile_workflow()
def reconcile_leased_spectrum() -> StepList:
    """Workflow to reconcile an Optical Leased Spectrum subscription.

    Re-applies the subscription's terminations configuration to the devices,
    re-verifies it, and refreshes the subscription description, so the external
    systems match the orchestrator's state again. It takes no user input and
    does not change the subscription lifecycle status. It is valid for the
    shipped ``OpticalLeasedSpectrum`` product type only; consumers with their
    own product type compose their own reconcile workflow with the shipped
    parts.
    """
    return (
        begin
        >> load_optical_pipe_block
        >> RECONCILE_LEASED_SPECTRUM_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
    )


__all__ = [
    "RECONCILE_LEASED_SPECTRUM_BLOCK_STEPS",
    "reconcile_leased_spectrum",
]
