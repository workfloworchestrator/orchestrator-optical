"""Reconcile Optical Spectrum Service workflow.

This module ships the ready-to-use ``reconcile_optical_spectrum`` workflow for
the shipped Optical Spectrum Service product type, together with the importable
:data:`RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS` step list.

Reconcile takes no user input: it pushes the subscription's existing
configuration back onto the devices (the same device push the create workflow
performs, via the idempotent find-or-create of the optical circuits) so the
external systems match the orchestrator's state again, then verifies the result.
The device push lives in
:mod:`orchestrator.optical.workflows.optical_spectrum_service.shared`, so this
module is only the composition of the shared parts. Consumers with their own
model that has-a the shipped block declare their own ``@reconcile_workflow``
with :data:`RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS`.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import reconcile_workflow
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    load_optical_spectrum_block,
    provision_optical_sections,
    refresh_optical_spectrum_used_passbands,
    set_optical_spectrum_subscription_description,
    verify_optical_spectrum_sections,
)

#: Reconcile steps of the Optical Spectrum Service family. Re-applies the
#: optical circuits of the sections to the devices (the same idempotent device
#: push the create workflow performs), refreshes the passbands in use, persists
#: the block and re-verifies the circuits on the devices. Every step is
#: block-level and operates on the block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``; the caller's load step provides it.
RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS: StepList = (
    begin
    >> provision_optical_sections
    >> refresh_optical_spectrum_used_passbands
    >> save_optical_module_block
    >> verify_optical_spectrum_sections
)


@reconcile_workflow()
def reconcile_optical_spectrum() -> StepList:
    """Workflow to reconcile an Optical Spectrum service.

    Re-applies the subscription's optical circuits to the devices, re-verifies
    them and refreshes the subscription description, so the external systems
    match the orchestrator's state again. It takes no user input and does not
    change the subscription lifecycle status. It loads the block from the
    ``optical_spectrum_service`` attribute of the shipped subscription models,
    so it is only valid for the shipped product type: consumers with their own
    product type compose their own reconcile workflow with the shipped parts.
    """
    return (
        begin
        >> load_optical_spectrum_block
        >> RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS
        >> set_optical_spectrum_subscription_description
    )


__all__ = [
    "RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS",
    "reconcile_optical_spectrum",
]
