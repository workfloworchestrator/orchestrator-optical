"""Tests for the extensible workflow factories of the Optical module."""

import sys
import types
from importlib import import_module

import pytest

from orchestrator.core.forms import FormPage
from orchestrator.core.workflow import Workflow, begin, step
from orchestrator.core.workflows import ALL_WORKFLOWS
from orchestrator.optical.workflows import SHIPPED_WORKFLOW_NAMES, register_workflows
from orchestrator.optical.workflows.optical_pipe.fiber_span.create import create_fiber_span_workflow
from orchestrator.optical.workflows.optical_pipe.fiber_span.terminate import terminate_fiber_span_workflow
from orchestrator.optical.workflows.optical_pipe.fiber_span.validate import validate_fiber_span_workflow
from orchestrator.optical.workflows.shared import merge_summary_fields

#: Import path of the module shipping the factory of every workflow name.
WORKFLOW_MODULES = {
    "create_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.create",
    "modify_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.modify",
    "terminate_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.terminate",
    "validate_optical_node_nokia_flexils": "orchestrator.optical.workflows.optical_node.nokia_flexils.validate",
    "create_optical_node_nokia_groove_g30": "orchestrator.optical.workflows.optical_node.nokia_groove_g30.create",
    "modify_optical_node_nokia_groove_g30": "orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify",
    "terminate_optical_node_nokia_groove_g30": "orchestrator.optical.workflows.optical_node.nokia_groove_g30.terminate",
    "validate_optical_node_nokia_groove_g30": "orchestrator.optical.workflows.optical_node.nokia_groove_g30.validate",
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


def test_shipped_workflow_names_match_factory_mapping() -> None:
    assert set(WORKFLOW_MODULES) == set(SHIPPED_WORKFLOW_NAMES)


def test_every_factory_builds_a_workflow_with_the_shipped_name() -> None:
    for name, module_name in WORKFLOW_MODULES.items():
        factory = getattr(import_module(module_name), f"{name}_workflow")
        workflow = factory()
        assert isinstance(workflow, Workflow)
        assert workflow.name == name


def test_pre_and_post_steps_wrap_the_shipped_steps() -> None:
    @step("user pre step")
    def pre_step() -> dict:
        return {}

    @step("user post step")
    def post_step() -> dict:
        return {}

    workflow = create_fiber_span_workflow(pre_steps=begin >> pre_step, post_steps=begin >> post_step)
    names = [s.name for s in workflow.steps]

    assert names.index("user pre step") < names.index("Construct Fiber Span Model")
    assert names.index("Construct Fiber Span Model") < names.index("Retrieve Used Passbands")
    assert names.index("Retrieve Used Passbands") < names.index("user post step")


def test_factory_without_hooks_keeps_the_shipped_steps() -> None:
    workflow = create_fiber_span_workflow()
    names = [s.name for s in workflow.steps]

    shipped_order = [
        "Construct Fiber Span Model",
        "Create Process Subscription relation",
        "Configure Fiber Span Terminations",
        "Retrieve Used Passbands",
    ]
    positions = [names.index(step_name) for step_name in shipped_order]
    assert positions == sorted(positions)


def test_terminate_pre_and_post_steps_wrap_the_shipped_steps() -> None:
    @step("user pre step")
    def pre_step() -> dict:
        return {}

    @step("user post step")
    def post_step() -> dict:
        return {}

    workflow = terminate_fiber_span_workflow(pre_steps=begin >> pre_step, post_steps=begin >> post_step)
    names = [s.name for s in workflow.steps]

    assert workflow.name == "terminate_fiber_span"
    assert names.index("user pre step") < names.index("Factory Reset Fiber Span Ports")
    assert names.index("Factory Reset Fiber Span Ports") < names.index("user post step")


def test_terminate_factory_accepts_extra_form_pages() -> None:
    class _ExtraPage(FormPage):
        pass

    workflow = terminate_fiber_span_workflow(extra_form_pages=[_ExtraPage])
    assert workflow.name == "terminate_fiber_span"

    assert terminate_fiber_span_workflow().name == "terminate_fiber_span"


def test_validate_pre_and_post_steps_wrap_the_shipped_steps() -> None:
    @step("user pre step")
    def pre_step() -> dict:
        return {}

    @step("user post step")
    def post_step() -> dict:
        return {}

    workflow = validate_fiber_span_workflow(pre_steps=begin >> pre_step, post_steps=begin >> post_step)
    names = [s.name for s in workflow.steps]

    assert workflow.name == "validate_fiber_span"
    assert names.index("user pre step") < names.index("Check Fiber Span Terminations")
    assert names.index("Check Fiber Span Terminations") < names.index("user post step")


def test_merge_summary_fields_appends_and_validates_names() -> None:
    user_input = {"a": 1, "b": 2}
    assert merge_summary_fields(["a"], ["b"], user_input) == ["a", "b"]

    with pytest.raises(ValueError, match="extra_summary_fields"):
        merge_summary_fields(["a"], ["unknown"], user_input)


def _stub_workflow_module(workflow_instances: dict[str, object]) -> types.ModuleType:
    module = types.ModuleType("mywfo.test_workflows")
    for name, workflow in workflow_instances.items():
        setattr(module, name, workflow)
    sys.modules["mywfo"] = types.ModuleType("mywfo")
    sys.modules[module.__name__] = module
    return module


def _unregister_workflows(names: list[str]) -> None:
    for name in names:
        ALL_WORKFLOWS.pop(name, None)


def test_register_workflows_with_explicit_names() -> None:
    from orchestrator.optical.workflows.optical_pipe.fiber_patch.create import create_fiber_patch_workflow

    module = _stub_workflow_module(
        {
            "create_fiber_span": create_fiber_span_workflow(),
            "create_fiber_patch": create_fiber_patch_workflow(),
        }
    )
    try:
        register_workflows(module.__name__, ["create_fiber_span", "create_fiber_patch"])
        assert set(ALL_WORKFLOWS) >= {"create_fiber_span", "create_fiber_patch"}
        assert ALL_WORKFLOWS["create_fiber_span"].instantiate().name == "create_fiber_span"
        assert ALL_WORKFLOWS["create_fiber_span"].package == module.__name__
    finally:
        _unregister_workflows(["create_fiber_span", "create_fiber_patch"])


def test_register_workflows_defaults_to_all_shipped_names_defined_in_module() -> None:
    from orchestrator.optical.workflows.optical_pipe.fiber_patch.create import create_fiber_patch_workflow

    module = _stub_workflow_module(
        {
            "create_fiber_span": create_fiber_span_workflow(),
            "create_fiber_patch": create_fiber_patch_workflow(),
        }
    )
    try:
        register_workflows(module.__name__)
        assert "create_fiber_span" in ALL_WORKFLOWS
        assert "create_fiber_patch" in ALL_WORKFLOWS
        assert "create_optical_node_nokia_flexils" not in ALL_WORKFLOWS
    finally:
        _unregister_workflows(["create_fiber_span", "create_fiber_patch"])


def test_register_workflows_raises_on_missing_explicit_name() -> None:
    module = _stub_workflow_module({})
    try:
        with pytest.raises(ValueError, match="create_fiber_span"):
            register_workflows(module.__name__, ["create_fiber_span"])
    finally:
        _unregister_workflows([])


def test_register_workflows_rejects_a_factory_instead_of_a_workflow() -> None:
    from orchestrator.optical.workflows.optical_pipe.fiber_span.create import create_fiber_span_workflow as factory

    module = _stub_workflow_module({"create_fiber_span": factory})
    try:
        with pytest.raises(TypeError, match="Workflow"):
            register_workflows(module.__name__, ["create_fiber_span"])
    finally:
        _unregister_workflows([])
