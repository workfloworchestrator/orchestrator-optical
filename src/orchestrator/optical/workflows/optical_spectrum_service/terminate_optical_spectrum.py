"""Terminate Optical Spectrum Service Workflow."""

from collections.abc import Sequence
from functools import partial
from typing import Any

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.hal.optical_node import vendor_of
from orchestrator.optical.hal.optical_spectrum import delete_optical_circuit
from orchestrator.optical.products.product_types.optical_spectrum_service import OpticalSpectrum
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum import (
    update_used_passbands_step,
)


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
    extra_form_pages: Sequence[type[FormPage]] = (),
) -> FormGenerator:
    """Generate the initial input form for terminating an Optical Spectrum service.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
    """

    class TerminateOpticalSpectrumForm(FormPage):
        subscription_id: DisplaySubscription = subscription_id  # type: ignore[valid-type]

    user_input = yield TerminateOpticalSpectrumForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    return user_input_dict


@step("Deleting optical sections")
def delete_optical_sections(subscription: OpticalSpectrum) -> State:
    """Delete the optical circuit of every spectrum section from the devices."""
    spectrum = subscription.optical_spectrum_service
    passband = spectrum.optical_spectrum_passband
    spectrum_name = spectrum.optical_spectrum_name
    circuit_identifier = str(spectrum.subscription_instance_id)
    results = {}
    for section in spectrum.optical_spectrum_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        results[vendor_of(src_node)] = delete_optical_circuit(
            src_node,
            section,
            spectrum_name,
            passband,
            circuit_identifier=circuit_identifier,
        )

    return {
        "configuration_results": results,
    }


def terminate_optical_spectrum_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the terminate_optical_spectrum workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
        **kwargs: Extra arguments forwarded to the ``terminate_workflow`` decorator.
    """

    @terminate_workflow(
        initial_input_form=partial(
            terminate_initial_input_form_generator,
            extra_form_pages=extra_form_pages,
        ),
        **kwargs,
    )
    def terminate_optical_spectrum() -> StepList:
        """Workflow to terminate an Optical Spectrum service."""
        return pre_steps >> begin >> delete_optical_sections >> update_used_passbands_step >> post_steps

    return terminate_optical_spectrum
