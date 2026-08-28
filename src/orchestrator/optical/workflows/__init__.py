"""Workflows of the Optical module.

This package ships the **ready-to-use workflows of the shipped product types**:
one module-level ``@create_workflow`` / ``@modify_workflow`` /
``@terminate_workflow`` / ``@validate_workflow``-decorated function per product
and lifecycle target, named exactly as the shipped name (the translation keys
in ``orchestrator/optical/translations/en-GB.json``). The workflows are bound
to the shipped subscription models and are therefore only valid when the
shipped product types are used as-is.

The package also ships the **parts** of the workflows — the **FormPages** of the
shipped forms (as page sequences, e.g. ``create_optical_module_location_form_pages``)
and importable step lists — for consumers that define their own product type
that has-a a shipped block and compose their own workflows with the parts.
Shipped form generators are thin compositions of the shipped pages and the
summary form; they carry no hooks, so consumers compose their own form
generators by yielding from the shipped page sequences in one line and
optionally interleaving their own pages. See the README for the complete
consumption model.

This package never registers workflows itself. Consumers register the shipped
workflows with the standard orchestrator-core mechanism, one
``LazyWorkflowInstance`` line per workflow in their own workflows package::

    from orchestrator.core.workflows import LazyWorkflowInstance

    LazyWorkflowInstance(
        "orchestrator.optical.workflows.optical_node.nokia_flexils.create",
        "create_optical_node_nokia_flexils",
    )
    LazyWorkflowInstance(
        "orchestrator.optical.workflows.optical_node.nokia_flexils.modify",
        "modify_optical_node_nokia_flexils",
    )
    LazyWorkflowInstance(
        "orchestrator.optical.workflows.optical_node.nokia_flexils.terminate",
        "terminate_optical_node_nokia_flexils",
    )
    LazyWorkflowInstance(
        "orchestrator.optical.workflows.optical_node.nokia_flexils.validate",
        "validate_optical_node_nokia_flexils",
    )

and persist them with ``orchestrator db migrate-workflows``. The full list of
shipped workflows and their import paths is in the README. Consumers with
their own product type compose their own workflows with the shipped parts; see
the README for the complete consumption model.
"""

#: The single state key under which a shipped block travels in the workflow
#: state. All shipped block steps of every family bind to this one key: a
#: consumer injects the block they compose (has-a the shipped block under any
#: attribute name of their own model) in the state under this key.
OPTICAL_MODULE_BLOCK_STATE_KEY = "optical_module_block"

__all__ = ["OPTICAL_MODULE_BLOCK_STATE_KEY"]
