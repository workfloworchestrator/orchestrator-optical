"""Validate Nokia GX G42 Optical Node workflow.

This module ships the ready-to-use ``validate_optical_node_nokia_gx_g42``
workflow for the shipped Nokia GX G42 product type. The validation steps are
shared by every Optical Node product (see
:data:`orchestrator.optical.workflows.optical_node.shared.OPTICAL_NODE_VALIDATE_STEPS`).
Consumers with their own model that has-a the shipped block declare their own
``@validate_workflow`` with the shared step list.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_node.shared import OPTICAL_NODE_VALIDATE_STEPS


@validate_workflow()
def validate_optical_node_nokia_gx_g42() -> StepList:
    """Workflow to validate a Nokia GX G42 Optical Node subscription."""
    return begin >> OPTICAL_NODE_VALIDATE_STEPS


__all__ = ["validate_optical_node_nokia_gx_g42"]
