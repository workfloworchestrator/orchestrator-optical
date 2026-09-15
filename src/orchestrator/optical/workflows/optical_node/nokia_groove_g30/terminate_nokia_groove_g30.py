"""Terminate Nokia Groove G30 Optical Node workflow.

This module ships the ready-to-use ``terminate_optical_node_nokia_groove_g30``
workflow for the shipped Nokia Groove G30 product type. The termination steps
are shared by every Optical Node product (see
:data:`orchestrator.optical.workflows.optical_node.shared.OPTICAL_NODE_TERMINATE_STEPS`).
Consumers with their own model that has-a the shipped block declare their own
``@terminate_workflow`` with the shared step list and the shipped
:func:`terminate_initial_input_form_generator` form.
"""

from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_TERMINATE_STEPS,
    terminate_initial_input_form_generator,
)


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to terminate a Nokia Groove G30 Optical Node subscription."""
    return begin >> OPTICAL_NODE_TERMINATE_STEPS


__all__ = ["terminate_optical_node_nokia_groove_g30"]
