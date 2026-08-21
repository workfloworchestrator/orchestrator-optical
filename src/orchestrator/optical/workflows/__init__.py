"""Workflows of the Optical module.

This package ships the **ready-to-use workflows of the shipped product types**:
one module-level ``@create_workflow`` / ``@modify_workflow`` /
``@terminate_workflow`` / ``@validate_workflow``-decorated function per product
and lifecycle target, named exactly as the shipped name (the translation keys
in ``orchestrator/optical/translations/en-GB.json``). The workflows are bound
to the shipped subscription models and are therefore only valid when the
shipped product types are used as-is.

The package also ships the **parts** of the workflows — importable form
generators and step lists — for consumers that define their own product type
that has-a a shipped block and compose their own workflows with the parts.

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
