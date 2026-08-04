"""Validate Optical Leased Spectrum Workflow."""

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.optical_node import retrieve_ports_spectral_occupations
from orchestrator.optical.hal.optical_port import check_fiber_terminating_port
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlock
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlock
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrum
from orchestrator.optical.workflows.optical_pipe.shared import optical_pipe_subscription_description

logger = get_logger(__name__)


@step("Load Initial State")
def load_initial_state_leased_spectrum(subscription: OpticalLeasedSpectrum) -> State:
    """Load the initial state of the Optical Leased Spectrum pipe."""
    return {"subscription": subscription}


@step("Update Subscription Description")
def update_subscription_description(subscription: OpticalLeasedSpectrum) -> State:
    """Update subscription description during validation."""
    subscription.description = optical_pipe_subscription_description(subscription)
    return {"subscription_description": subscription.description}


@step("Check Leased Spectrum Terminations")
def check_leased_spectrum_terminations(subscription: OpticalLeasedSpectrum) -> State:
    """Verify that the terminating ports of the leased spectrum pipe are correctly configured."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    check_fiber_terminating_port(port_a, port_b)
    check_fiber_terminating_port(port_b, port_a)
    return {}


@step("Retrieve Used Passbands")
def retrieve_leased_spectrum_used_passbands(subscription: OpticalLeasedSpectrum) -> State:
    """Refresh the passbands in use on the terminating ports from the devices."""
    for port in subscription.optical_pipe.optical_pipe_terminations:
        if not isinstance(port, OlsAddDropPortBlock | OlsLinePortBlock):
            continue
        host_node = port.optical_port_host_node
        if host_node.optical_node_role not in (
            OpticalNodeRole.ROADM,
            OpticalNodeRole.TRANSPONDER_XOADM,
            OpticalNodeRole.AMPLIFIER,
        ):
            continue
        if port.optical_port_name is None:
            msg = f"Optical port block of {host_node.pqdn} has no port name"
            raise ValueError(msg)
        port.optical_passbands = retrieve_ports_spectral_occupations(host_node).get(port.optical_port_name, [])
    return {"subscription": subscription}


@validate_workflow()
def validate_leased_spectrum() -> StepList:
    """Workflow to validate an Optical Leased Spectrum subscription."""
    return (
        begin
        >> load_initial_state_leased_spectrum
        >> update_subscription_description
        >> check_leased_spectrum_terminations
        >> retrieve_leased_spectrum_used_passbands
    )
