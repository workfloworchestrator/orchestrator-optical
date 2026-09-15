"""Terminate Optical Spectrum Service Workflow.

This module ships the ready-to-use ``terminate_optical_spectrum`` workflow for
the shipped Optical Spectrum Service product type, together with the importable
parts: the FormPage of the terminate confirmation form (as the
:func:`terminate_optical_spectrum_form_pages` page sequence) and the
termination steps.

Consumers with their own model that has-a the shipped block declare their own
``@terminate_workflow`` with :data:`TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS` and
compose their own terminate form generator by yielding from the shipped page
sequence in one line.
"""

from typing import cast

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.products.product_blocks.optical_spectrum import OpticalSpectrumServiceBlockInactive
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    delete_optical_spectrum_sections,
    load_optical_spectrum_block,
    optical_spectrum_block_from_state,
    refresh_optical_spectrum_used_passbands,
)


def terminate_optical_spectrum_form(subscription_id: UUIDstr) -> type[FormPage]:
    """Return the confirmation FormPage of the Optical Spectrum terminate form.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The confirmation FormPage of the shipped terminate form.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalSpectrumForm(FormPage):
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

    return TerminateOpticalSpectrumForm


def terminate_optical_spectrum_form_pages(subscription_id: UUIDstr) -> FormGenerator:
    """Yield the FormPage of the Optical Spectrum terminate form.

    This is the shipped terminate form as a page sequence: it yields the
    confirmation page and returns the collected user input. Consumers yield
    from it in one line inside their own terminate form generator, optionally
    adding their own pages.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield terminate_optical_spectrum_form(subscription_id)
    return user_input.model_dump()


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
) -> FormGenerator:
    """Generate the confirmation form before terminating an Optical Spectrum subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).

    Returns:
        The collected user input of the confirmation page.
    """
    user_input = yield from terminate_optical_spectrum_form_pages(subscription_id)
    return user_input


@step("Deleting optical sections")
def delete_optical_sections(optical_module_block: OpticalSpectrumServiceBlockInactive) -> State:
    """Delete the optical circuit of every spectrum section from the devices.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``: the block is re-hydrated from its
    serialized form (see
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.optical_spectrum_block_from_state`)
    and every section is deleted on the source Optical Node of the section.

    The teardown, including the OEL of each source node, is delegated to
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.delete_optical_spectrum_sections`:
    once all of the circuit's OSNCs are gone, the node's OEL is deleted only when no
    other OSNC on that node still references it; otherwise it is left in place because
    other OSNCs still need it.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    spectrum_name = block.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    results = delete_optical_spectrum_sections(
        block.optical_spectrum_sections,
        block.optical_spectrum_passband,
        spectrum_name,
        str(block.subscription_instance_id),
    )

    return {"configuration_results": results}


#: Termination steps operating on the Optical Spectrum block in the state. The
#: optical circuit of every section is deleted from the devices together with the
#: OEL of each source node when no other OSNC still references it, the passbands
#: in use are refreshed and the block is persisted by the last step, because
#: workflow steps execute with the state serialized between steps (the block is
#: re-hydrated from its serialized form before every step operates on it).
TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS: StepList = (
    begin >> delete_optical_sections >> refresh_optical_spectrum_used_passbands >> save_optical_module_block
)


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_optical_spectrum() -> StepList:
    """Workflow to terminate an Optical Spectrum service subscription.

    The workflow is composed from the shipped parts: the block is loaded from
    the ``optical_spectrum_service`` attribute of the shipped subscription
    models and the shipped block steps delete the circuits and persist the
    refreshed passbands. It is therefore only valid for the shipped product
    type; consumers with their own product type compose their own terminate
    workflow with the same parts.
    """
    return begin >> load_optical_spectrum_block >> TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS


__all__ = [
    "TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS",
    "terminate_initial_input_form_generator",
    "terminate_optical_spectrum",
    "terminate_optical_spectrum_form_pages",
]
