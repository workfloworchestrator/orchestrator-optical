"""Validate Nokia GX G42 Optical Node Workflow."""

from typing import Any

from orchestrator.core.workflow import StepList, Workflow, begin
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_node.shared import (
    load_initial_state_optical_node,
    update_optical_node_subscription_description,
)


def validate_optical_node_nokia_gx_g42_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    **kwargs: Any,
) -> Workflow:
    """Build the validate_optical_node_nokia_gx_g42 workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        **kwargs: Extra arguments forwarded to the ``validate_workflow`` decorator.
    """

    @validate_workflow(**kwargs)
    def validate_optical_node_nokia_gx_g42() -> StepList:
        """Workflow to validate a Nokia GX G42 Optical Node."""
        return (
            pre_steps
            >> begin
            >> load_initial_state_optical_node
            >> update_optical_node_subscription_description
            >> post_steps
        )

    return validate_optical_node_nokia_gx_g42
