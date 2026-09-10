"""Tests for the shipped ready-to-use workflows of the Optical module.

The shipped workflow set is **not** hand-maintained here: it is the set computed by
``discover_shipped_workflows()`` (the same discovery the migration generator uses), so
these tests cannot drift from the workflows that are actually shipped. The migration
``WorkflowMigration`` record carries the workflow ``name`` and ``target`` but not its
module, so the module for each discovered workflow is resolved by walking the
``orchestrator.optical.workflows`` package once and indexing the decorated workflow
functions by their shipped name.

For every discovered workflow these tests verify that it (a) is importable from its
module, (b) is a ``Workflow`` instance whose ``.name`` matches, (c) has the target
reported by discovery, and (d) instantiates through
``LazyWorkflowInstance(<module>, <name>)``.
"""

import inspect
import pkgutil
from importlib import import_module

import pytest

import orchestrator.optical.workflows
from orchestrator.core.targets import Target
from orchestrator.core.workflow import Workflow
from orchestrator.core.workflows import LazyWorkflowInstance
from orchestrator.optical.migrations.generate import discover_shipped_workflows


def _modules_by_workflow_name() -> dict[str, str]:
    """Index every decorated shipped workflow function by its shipped name.

    Returns:
        A mapping of workflow ``name`` to the import path of the module that defines it.
    """
    modules: dict[str, str] = {}
    for module_info in pkgutil.walk_packages(
        orchestrator.optical.workflows.__path__, orchestrator.optical.workflows.__name__ + "."
    ):
        if module_info.name.endswith("__init__"):
            continue
        module = import_module(module_info.name)
        for attribute in vars(module).values():
            if inspect.isfunction(attribute) and isinstance(getattr(attribute, "target", None), Target):
                modules[attribute.name] = module_info.name
    return modules


#: Discovery is the single source of truth for the shipped workflow set; the module index
#: only supplies the import path that ``WorkflowMigration`` does not carry.
_DISCOVERED_WORKFLOWS = discover_shipped_workflows()
_WORKFLOW_MODULES = _modules_by_workflow_name()

#: ``(name, module, target)`` triples, one per discovered shipped workflow.
WORKFLOW_PARAMS = sorted(
    (workflow.name, _WORKFLOW_MODULES[workflow.name], workflow.target) for workflow in _DISCOVERED_WORKFLOWS
)


@pytest.mark.parametrize(("name", "module_name", "target"), WORKFLOW_PARAMS)
def test_shipped_workflow_exists_with_matching_name_and_target(name, module_name, target) -> None:
    """Every discovered workflow is importable, is a ``Workflow`` and reports name/target."""
    workflow = getattr(import_module(module_name), name)

    assert isinstance(workflow, Workflow)
    assert workflow.name == name
    assert workflow.target == Target(target)


@pytest.mark.parametrize(("name", "module_name", "target"), WORKFLOW_PARAMS)
def test_shipped_workflows_instantiate_through_lazy_workflow_instance(name, module_name, target) -> None:
    """Every discovered workflow instantiates through ``LazyWorkflowInstance``."""
    lazy = LazyWorkflowInstance(module_name, name)
    workflow = lazy.instantiate()

    assert isinstance(workflow, Workflow)
    assert workflow.name == name
    assert workflow.target == Target(target)
