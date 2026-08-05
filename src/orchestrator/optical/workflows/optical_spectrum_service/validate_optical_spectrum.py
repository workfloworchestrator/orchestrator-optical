"""Validate Optical Spectrum Service Workflow."""

from typing import Any

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.optical_spectrum import validate_optical_circuit
from orchestrator.optical.products.product_types.optical_spectrum_service import OpticalSpectrum
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum import (
    subscription_description,
)


@step("Load initial state")
def load_initial_state_optical_spectrum(subscription: OpticalSpectrum) -> State:
    """Load the initial state of the subscription."""
    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalSpectrum,
) -> State:
    """Update the subscription description with the spectrum name and the product name."""
    subscription.description = subscription_description(subscription)
    return {
        "subscription": subscription,
        "subscription_description": subscription.description,
    }


@step("Verifying optical spectrum sections")
def verify_optical_transport_channels(subscription: OpticalSpectrum) -> State:
    """Verify the optical circuit of every spectrum section against the devices."""
    spectrum = subscription.optical_spectrum_service
    spectrum_name = spectrum.optical_spectrum_name
    passband = spectrum.optical_spectrum_passband
    central_frequency = int((passband[0] + passband[1]) / 2)
    bandwidth = passband[1] - passband[0]
    carrier = (
        central_frequency,
        bandwidth,
    )
    circuit_identifier = str(spectrum.subscription_instance_id)
    for section in spectrum.optical_spectrum_sections:
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


def validate_optical_spectrum_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    **kwargs: Any,
) -> Workflow:
    """Build the validate_optical_spectrum workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        **kwargs: Extra arguments forwarded to the ``validate_workflow`` decorator.
    """

    @validate_workflow(**kwargs)
    def validate_optical_spectrum() -> StepList:
        """Workflow to validate an Optical Spectrum service."""
        return (
            pre_steps
            >> begin
            >> load_initial_state_optical_spectrum
            >> update_subscription_description
            >> verify_optical_transport_channels
            >> post_steps
        )

    return validate_optical_spectrum
