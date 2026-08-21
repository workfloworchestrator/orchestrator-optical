"""Validate Nokia FlexILS Optical Node workflow.

This module ships the ready-to-use ``validate_optical_node_nokia_flexils``
workflow for the shipped Nokia FlexILS product type. The validation steps are
shared by every Optical Node product (see
:data:`orchestrator.optical.workflows.optical_node.shared.OPTICAL_NODE_VALIDATE_STEPS`).
Consumers with their own model that has-a the shipped block declare their own
``@validate_workflow`` with the shared step list.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_node.shared import OPTICAL_NODE_VALIDATE_STEPS


@validate_workflow()
def validate_optical_node_nokia_flexils() -> StepList:
    """Workflow to validate a Nokia FlexILS Optical Node subscription."""
    return begin >> OPTICAL_NODE_VALIDATE_STEPS


__all__ = ["validate_optical_node_nokia_flexils"]
