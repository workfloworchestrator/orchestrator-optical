"""Terminate Optical Spectrum Service Workflow."""

from pydantic_forms.types import InputForm, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.hal.optical_node import vendor_of
from orchestrator.optical.hal.optical_spectrum import delete_optical_circuit
from orchestrator.optical.products.product_types.optical_spectrum_service import OpticalSpectrum
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum import (
    update_used_passbands_step,
)


def terminate_initial_input_form_generator(subscription_id: UUIDstr, customer_id: UUIDstr) -> InputForm:  # noqa: ARG001
    """Generate the initial input form for terminating an Optical Spectrum service."""

    class TerminateOpticalSpectrumForm(FormPage):
        subscription_id: DisplaySubscription = subscription_id  # type: ignore[valid-type]

    return TerminateOpticalSpectrumForm


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


additional_steps = begin


@terminate_workflow(
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_optical_spectrum() -> StepList:
    """Workflow to terminate an Optical Spectrum service."""
    return begin >> delete_optical_sections >> update_used_passbands_step
