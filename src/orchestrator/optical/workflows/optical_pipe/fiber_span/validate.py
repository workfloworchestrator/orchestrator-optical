"""Validate Optical Fiber Span Workflow."""

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.optical_node import retrieve_ports_spectral_occupations
from orchestrator.optical.hal.optical_port import check_fiber_terminating_port
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpan
from orchestrator.optical.workflows.optical_pipe.shared import optical_pipe_subscription_description

logger = get_logger(__name__)


@step("Load Initial State")
def load_initial_state_fiber_span(subscription: OpticalFiberSpan) -> State:
    """Load the initial state of the Optical Fiber Span."""
    return {"subscription": subscription}


@step("Update Subscription Description")
def update_subscription_description(subscription: OpticalFiberSpan) -> State:
    """Update subscription description during validation."""
    subscription.description = optical_pipe_subscription_description(subscription)
    return {"subscription_description": subscription.description}


@step("Check Fiber Span Terminations")
def check_span_terminations(subscription: OpticalFiberSpan) -> State:
    """Verify that the terminating line ports of the fiber span are correctly configured."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    check_fiber_terminating_port(port_a, port_b)
    check_fiber_terminating_port(port_b, port_a)
    return {}


@step("Retrieve Used Passbands")
def retrieve_span_used_passbands(subscription: OpticalFiberSpan) -> State:
    """Refresh the passbands in use on the terminating ports from the devices."""
    for port in subscription.optical_pipe.optical_pipe_terminations:
        host_node = port.optical_port_host_node
        if host_node.optical_node_role not in (
            OpticalNodeRole.ROADM,
            OpticalNodeRole.TRANSPONDER_XOADM,
            OpticalNodeRole.AMPLIFIER,
        ):
            continue
        if port.optical_port_name is None:
            msg = f"Optical port block of {host_node.management.optical_module_node_fqdn} has no port name"
            raise ValueError(msg)
        port.optical_passbands = retrieve_ports_spectral_occupations(host_node).get(port.optical_port_name, [])
    return {"subscription": subscription}


@validate_workflow()
def validate_fiber_span() -> StepList:
    """Workflow to validate an Optical Fiber Span subscription."""
    return (
        begin
        >> load_initial_state_fiber_span
        >> update_subscription_description
        >> check_span_terminations
        >> retrieve_span_used_passbands
    )
