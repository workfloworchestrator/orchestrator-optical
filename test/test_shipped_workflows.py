"""Tests for the shipped ready-to-use workflows of the Optical module.

The module ships one create/modify/terminate/validate workflow per shipped
product type as a module-level decorated ``Workflow`` with the shipped name.
Consumers using the shipped product types register them with
``LazyWorkflowInstance(<module>, <name>)``; these tests verify that every
shipped workflow exists under its expected name, target and module, and that
the ``LazyWorkflowInstance`` registration mechanism instantiates them.
"""

from importlib import import_module

import pytest

from orchestrator.core.targets import Target
from orchestrator.core.workflow import Workflow
from orchestrator.core.workflows import LazyWorkflowInstance

#: Import path of the module shipping every shipped workflow name.
WORKFLOW_MODULES = {
    "create_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.create",
    "modify_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.modify",
    "terminate_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.terminate",
    "validate_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.validate",
    "create_optical_node_nokia_groove_g30": "orchestrator.optical.workflows.optical_node.nokia_groove_g30.create",
    "modify_optical_node_nokia_groove_g30": "orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify",
    "terminate_optical_node_nokia_groove_g30": (
        "orchestrator.optical.workflows.optical_node.nokia_groove_g30.terminate"
    ),
    "validate_optical_node_nokia_groove_g30": ("orchestrator.optical.workflows.optical_node.nokia_groove_g30.validate"),
    "create_optical_node_nokia_gx_g42": "orchestrator.optical.workflows.optical_node.nokia_gx_g42.create",
    "modify_optical_node_nokia_gx_g42": "orchestrator.optical.workflows.optical_node.nokia_gx_g42.modify",
    "terminate_optical_node_nokia_gx_g42": "orchestrator.optical.workflows.optical_node.nokia_gx_g42.terminate",
    "validate_optical_node_nokia_gx_g42": "orchestrator.optical.workflows.optical_node.nokia_gx_g42.validate",
    "create_fiber_span": "orchestrator.optical.workflows.optical_pipe.fiber_span.create",
    "modify_fiber_span": "orchestrator.optical.workflows.optical_pipe.fiber_span.modify",
    "terminate_fiber_span": "orchestrator.optical.workflows.optical_pipe.fiber_span.terminate",
    "validate_fiber_span": "orchestrator.optical.workflows.optical_pipe.fiber_span.validate",
    "create_fiber_patch": "orchestrator.optical.workflows.optical_pipe.fiber_patch.create",
    "modify_fiber_patch": "orchestrator.optical.workflows.optical_pipe.fiber_patch.modify",
    "terminate_fiber_patch": "orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate",
    "validate_fiber_patch": "orchestrator.optical.workflows.optical_pipe.fiber_patch.validate",
    "create_leased_spectrum": "orchestrator.optical.workflows.optical_pipe.leased_spectrum.create",
    "modify_leased_spectrum": "orchestrator.optical.workflows.optical_pipe.leased_spectrum.modify",
    "terminate_leased_spectrum": "orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate",
    "validate_leased_spectrum": "orchestrator.optical.workflows.optical_pipe.leased_spectrum.validate",
    "create_optical_coherent_pluggable": "orchestrator.optical.workflows.optical_coherent_pluggable.create",
    "modify_optical_coherent_pluggable": "orchestrator.optical.workflows.optical_coherent_pluggable.modify",
    "terminate_optical_coherent_pluggable": "orchestrator.optical.workflows.optical_coherent_pluggable.terminate",
    "validate_optical_coherent_pluggable": "orchestrator.optical.workflows.optical_coherent_pluggable.validate",
    "create_optical_spectrum": "orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum",
    "modify_optical_spectrum": "orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum",
    "terminate_optical_spectrum": "orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum",
    "validate_optical_spectrum": "orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum",
    "create_optical_digital_service": "orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service",  # noqa: E501
    "modify_optical_digital_service": "orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service",  # noqa: E501
    "terminate_optical_digital_service": "orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service",  # noqa: E501
    "validate_optical_digital_service": "orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service",  # noqa: E501
}

EXPECTED_TARGETS = {
    "create_": Target.CREATE,
    "modify_": Target.MODIFY,
    "terminate_": Target.TERMINATE,
    "validate_": Target.VALIDATE,
}


@pytest.mark.parametrize(("name", "module_name"), sorted(WORKFLOW_MODULES.items()))
def test_shipped_workflow_exists_with_matching_name_and_target(name, module_name) -> None:
    workflow = getattr(import_module(module_name), name)

    assert isinstance(workflow, Workflow)
    assert workflow.name == name
    expected_target = next(target for prefix, target in EXPECTED_TARGETS.items() if name.startswith(prefix))
    assert workflow.target == expected_target


@pytest.mark.parametrize(("name", "module_name"), sorted(WORKFLOW_MODULES.items()))
def test_shipped_workflows_instantiate_through_lazy_workflow_instance(name, module_name) -> None:
    lazy = LazyWorkflowInstance(module_name, name)
    workflow = lazy.instantiate()

    assert isinstance(workflow, Workflow)
    assert workflow.name == name
