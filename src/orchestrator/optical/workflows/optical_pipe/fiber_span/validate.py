"""Validate Optical Fiber Span workflow.

This module ships the ready-to-use ``validate_fiber_span`` workflow for the
shipped Optical Fiber Span product type, together with the importable parts:
the state loading step, the shared subscription description step and the
termination check steps. Consumers with their own model that has-a the
shipped block declare their own ``@validate_workflow`` with
:data:`FIBER_SPAN_VALIDATE_STEPS`; consumer models that compose the block
under a different attribute name can put the block in the state under
``OPTICAL_PIPE_BLOCK_STATE_KEY`` for the description step.
"""

from pydantic_forms.types import State

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.optical_node import retrieve_ports_spectral_occupations
from orchestrator.optical.hal.optical_port import check_fiber_terminating_port
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpan
from orchestrator.optical.workflows.optical_pipe.shared import set_optical_pipe_subscription_description


@step("Load Initial State")
def load_initial_state_fiber_span(subscription: OpticalFiberSpan) -> State:
    """Load the initial state of the Optical Fiber Span."""
    return {"subscription": subscription}


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


#: Validation steps of the Optical Fiber Span family. The subscription
#: description refresh is a shared step that reads the block from the state
#: under ``OPTICAL_PIPE_BLOCK_STATE_KEY`` when present, and otherwise falls
#: back to the ``optical_pipe`` attribute of the shipped subscription models.
FIBER_SPAN_VALIDATE_STEPS: StepList = (
    begin
    >> load_initial_state_fiber_span
    >> set_optical_pipe_subscription_description
    >> check_span_terminations
    >> retrieve_span_used_passbands
)


@validate_workflow()
def validate_fiber_span() -> StepList:
    """Workflow to validate an Optical Fiber Span subscription."""
    return begin >> FIBER_SPAN_VALIDATE_STEPS


__all__ = [
    "FIBER_SPAN_VALIDATE_STEPS",
    "validate_fiber_span",
]
