"""Validate Nokia Groove G30 Optical Node workflow.

This module ships the ready-to-use ``validate_optical_node_nokia_groove_g30``
workflow for the shipped Nokia Groove G30 product type. The block-level refresh
step is shared by every Optical Node product (see
:data:`orchestrator.optical.workflows.optical_node.shared.OPTICAL_NODE_VALIDATE_STEPS`),
while the subscription-level steps (loading the subscription into the state and
recomputing the subscription description) live here, bound to the shipped
product type. Consumers with their own model that has-a the shipped block
declare their own ``@validate_workflow`` with the shared block-level step list.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_node.shared import (
    load_initial_state_optical_node,
    update_optical_node_subscription_description,
)
from orchestrator.optical.workflows.optical_node.shared.validate import VALIDATE_OPTICAL_NODE_BLOCK_STEPS


@validate_workflow()
def validate_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to validate a Nokia Groove G30 Optical Node subscription."""
    return (
        begin
        >> load_initial_state_optical_node
        >> VALIDATE_OPTICAL_NODE_BLOCK_STEPS
        >> update_optical_node_subscription_description
    )


__all__ = ["validate_optical_node_nokia_groove_g30"]
