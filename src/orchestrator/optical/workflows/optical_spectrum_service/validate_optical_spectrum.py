"""Validate Optical Spectrum Service Workflow.

This module ships the ready-to-use ``validate_optical_spectrum`` workflow for
the shipped Optical Spectrum Service product type, together with the importable
parts: the state loading step and the block-level validation step list
(:data:`VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS`). Consumers with their own model
that has-a the shipped block declare their own ``@validate_workflow`` composing
the state loading step, :func:`load_optical_spectrum_block`,
:data:`VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS` and the shared description step;
consumer models that compose the block under a different attribute name put the
block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the validation
step.
"""

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.spectrum import validate_optical_circuit
from orchestrator.optical.products.product_blocks.optical_spectrum import OpticalSpectrumBlockInactive
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    load_optical_spectrum_block,
    optical_spectrum_block_from_state,
    set_optical_spectrum_subscription_description,
)


@step("Verifying optical spectrum sections")
def verify_optical_spectrum_sections(optical_module_block: OpticalSpectrumBlockInactive) -> State:
    """Verify the optical circuit of every spectrum section against the devices.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``: the block is re-hydrated from its
    serialized form (see
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.optical_spectrum_block_from_state`)
    and every section is verified on the source Optical Node of the section.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    spectrum_name = block.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    passband = block.optical_spectrum_passband
    central_frequency = int((passband[0] + passband[1]) / 2)
    bandwidth = passband[1] - passband[0]
    carrier = (
        central_frequency,
        bandwidth,
    )
    circuit_identifier = str(block.subscription_instance_id)
    for section in block.optical_spectrum_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        validate_optical_circuit(
            src_node,
            section,
            spectrum_name,
            passband,
            carrier,
            label=spectrum_name,
            circuit_identifier=circuit_identifier,
        )

    return {}


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
