"""Validate Nokia Groove G30 Optical Node Workflow."""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_node.shared import (
    load_initial_state_optical_node,
    update_optical_node_subscription_description,
)


@validate_workflow()
def validate_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to validate a Nokia Groove G30 Optical Node."""
    return begin >> load_initial_state_optical_node >> update_optical_node_subscription_description
