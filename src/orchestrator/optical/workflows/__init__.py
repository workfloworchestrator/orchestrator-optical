"""Workflow factories of the Optical module.

This package does not register any workflow itself: every consumer declares one
workflow per shipped workflow in their own code-space (a 1:1 mirror of this
package) by calling the workflow factory functions, e.g.
``create_fiber_span_workflow()``, and then registers the declared workflows by
calling :func:`register_workflows`. See the README for a complete example.
"""

from collections.abc import Sequence
from importlib import import_module

import structlog

from orchestrator.core.workflow import Workflow
from orchestrator.core.workflows import LazyWorkflowInstance

logger = structlog.get_logger(__name__)

#: Names of the workflows shipped by this package; the keys a consumer's
#: workflow module must declare (usually one attribute per name, holding the
#: workflow instance returned by the corresponding factory function).
SHIPPED_WORKFLOW_NAMES = frozenset(
    {
        "create_optical_node_nokia_flexils",
        "modify_optical_node_nokia_flexils",
        "terminate_optical_node_nokia_flexils",
        "validate_optical_node_nokia_flexils",
        "create_optical_node_nokia_groove_g30",
        "modify_optical_node_nokia_groove_g30",
        "terminate_optical_node_nokia_groove_g30",
        "validate_optical_node_nokia_groove_g30",
        "create_optical_node_nokia_gx_g42",
        "modify_optical_node_nokia_gx_g42",
        "terminate_optical_node_nokia_gx_g42",
        "validate_optical_node_nokia_gx_g42",
        "create_fiber_span",
        "modify_fiber_span",
        "terminate_fiber_span",
        "validate_fiber_span",
        "create_fiber_patch",
        "modify_fiber_patch",
        "terminate_fiber_patch",
        "validate_fiber_patch",
        "create_leased_spectrum",
        "modify_leased_spectrum",
        "terminate_leased_spectrum",
        "validate_leased_spectrum",
        "create_optical_coherent_pluggable",
        "modify_optical_coherent_pluggable",
        "terminate_optical_coherent_pluggable",
        "validate_optical_coherent_pluggable",
        "create_optical_spectrum",
        "modify_optical_spectrum",
        "terminate_optical_spectrum",
        "validate_optical_spectrum",
        "create_optical_digital_service",
        "modify_optical_digital_service",
        "terminate_optical_digital_service",
        "validate_optical_digital_service",
    }
)


def register_workflows(module_name: str, names: Sequence[str] | None = None) -> None:
    """Register the optical workflows declared in *module_name* with WFO.

    The module is expected to define one workflow per shipped optical workflow
    (see :data:`SHIPPED_WORKFLOW_NAMES`), produced by calling the workflow
    factory functions of this package. Call this function at the end of the
    module that declares the workflows.

    Args:
        module_name: Import path of the module declaring the workflows.
        names: Workflow names to register. Defaults to every shipped workflow
            name that is defined in the module.

    Raises:
        TypeError: If a module attribute with the given name is not a workflow
            instance, e.g. because the factory function itself was re-exported
            instead of its result.
    """
    module = import_module(module_name)
    for name in names if names is not None else SHIPPED_WORKFLOW_NAMES:
        workflow = getattr(module, name, None)
        if not isinstance(workflow, Workflow):
            if workflow is None:
                if names is None:
                    logger.warning("Skipping missing optical workflow declaration", module=module_name, workflow=name)
                    continue
                msg = f"Workflow {name!r} is not defined in module {module_name!r}"
                raise ValueError(msg)
            msg = (
                f"Attribute {name!r} of module {module_name!r} is not a Workflow (did you forget to call the factory?)"
            )
            raise TypeError(msg)
        LazyWorkflowInstance(module_name, name)
