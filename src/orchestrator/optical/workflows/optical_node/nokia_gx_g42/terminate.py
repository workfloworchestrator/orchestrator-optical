"""Terminate Nokia GX G42 Optical Node Workflow."""

from collections.abc import Sequence
from functools import partial
from typing import Any

from orchestrator.core.forms import FormPage
from orchestrator.core.workflow import StepList, Workflow, begin
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.workflows.optical_node.shared import (
    delete_optical_node_from_oss_bss,
    terminate_initial_input_form_generator,
)


def terminate_optical_node_nokia_gx_g42_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the terminate_optical_node_nokia_gx_g42 workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
        **kwargs: Extra arguments forwarded to the ``terminate_workflow`` decorator.
    """

    @terminate_workflow(
        initial_input_form=partial(
            terminate_initial_input_form_generator,
            extra_form_pages=extra_form_pages,
        ),
        **kwargs,
    )
    def terminate_optical_node_nokia_gx_g42() -> StepList:
        """Workflow to terminate a Nokia GX G42 Optical Node."""
        return pre_steps >> begin >> delete_optical_node_from_oss_bss >> post_steps

    return terminate_optical_node_nokia_gx_g42
