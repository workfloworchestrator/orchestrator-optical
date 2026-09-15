"""Validate Optical Spectrum Service Workflow.

This module ships the ready-to-use ``validate_optical_spectrum`` workflow for
the shipped Optical Spectrum Service product type, together with the importable
parts: the state loading step and the block-level validation step list
(:data:`VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS`). The circuit verification step
itself is shared (see
:mod:`orchestrator.optical.workflows.optical_spectrum_service.shared`) because
the shipped reconcile workflow reuses it. Consumers with their own model that
has-a the shipped block declare their own ``@validate_workflow`` composing the
state loading step, :func:`load_optical_spectrum_block`,
:data:`VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS` and the shared description step;
consumer models that compose the block under a different attribute name put the
block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the validation
step.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    load_optical_spectrum_block,
    set_optical_spectrum_subscription_description,
    verify_optical_spectrum_sections,
)

#: Validation steps of the Optical Spectrum Service family. The block is loaded
#: from the ``optical_spectrum_service`` attribute of the shipped subscription
#: models and verified from the state; the subscription description refresh is
#: applied by the workflow.
VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS: StepList = (
    begin >> load_optical_spectrum_block >> verify_optical_spectrum_sections
)


@validate_workflow()
def validate_optical_spectrum() -> StepList:
    """Workflow to validate an Optical Spectrum service subscription.

    The workflow is composed from the shipped parts: the block is loaded from
    the ``optical_spectrum_service`` attribute of the shipped subscription
    models, the shipped block steps verify it and the shared description step
    refreshes the subscription description. It is therefore only valid for the
    shipped product type; consumers with their own product type compose their
    own validate workflow with the same parts.
    """
    return begin >> VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS >> set_optical_spectrum_subscription_description


__all__ = [
    "VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS",
    "validate_optical_spectrum",
    "verify_optical_spectrum_sections",
]
