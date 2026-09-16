"""Reconcile Optical Digital Service workflow.

This module ships the ready-to-use ``reconcile_optical_digital_service``
workflow for the shipped Optical Digital Service product type, together with
the importable :data:`RECONCILE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS` step list.

Reconcile takes no user input: it pushes the subscription's existing
configuration back onto the devices (the same device push the create workflow
performs, via the idempotent ensure of the optical circuits of every channel,
owned and reused) so the external systems match the orchestrator's state again,
then verifies the result. The device push and verification live in
:mod:`orchestrator.optical.workflows.optical_digital_service.shared`, so this
module is only the composition of the shared parts. Consumers with their own
model that has-a the shipped block declare their own ``@reconcile_workflow``
with :data:`RECONCILE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS`.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import reconcile_workflow
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.optical_digital_service.shared import (
    PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS,
    VERIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS,
    load_optical_digital_service_block,
    refresh_optical_digital_used_passbands,
    set_optical_digital_service_subscription_description,
)

#: Reconcile steps of the Optical Digital Service family. Re-applies the
#: transponder configuration and the optical circuits of every channel (owned and
#: reused) to the devices (the same idempotent ensure push the create workflow
#: performs, which recreates a missing shared OSNC and converges drifted composite
#: labels before verification), refreshes the passbands in use, persists the block
#: and re-verifies the configuration on the devices. Every step is block-level and
#: operates on the block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``;
#: the caller's load step provides it.
RECONCILE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = (
    begin
    >> PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS
    >> refresh_optical_digital_used_passbands
    >> save_optical_module_block
    >> VERIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS
)


@reconcile_workflow()
def reconcile_optical_digital_service() -> StepList:
    """Workflow to reconcile an Optical Digital Service.

    Re-applies the subscription's transponder configuration and optical
    circuits to the devices, re-verifies them and refreshes the subscription
    description, so the external systems match the orchestrator's state again.
    It takes no user input and does not change the subscription lifecycle
    status. It loads the block from the ``optical_digital_service`` attribute
    of the shipped subscription models, so it is only valid for the shipped
    product type: consumers with their own product type compose their own
    reconcile workflow with the shipped parts.
    """
    return (
        begin
        >> load_optical_digital_service_block
        >> RECONCILE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS
        >> set_optical_digital_service_subscription_description
    )


__all__ = [
    "RECONCILE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS",
    "reconcile_optical_digital_service",
]
