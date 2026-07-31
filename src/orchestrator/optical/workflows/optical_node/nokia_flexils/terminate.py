"""Terminate Nokia FlexILS Optical Node Workflow."""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.workflows.optical_node.shared import (
    delete_optical_node_from_oss_bss,
    terminate_initial_input_form_generator,
)

additional_steps = begin


@terminate_workflow(
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_optical_node_nokia_flexils() -> StepList:
    """Workflow to terminate a Nokia FlexILS Optical Node."""
    return begin >> delete_optical_node_from_oss_bss
