"""Bulk-task workflows of the Optical module.

This package ships the **system tasks** of the module: ``Target.SYSTEM``
workflows that operators run manually from the WFO UI, currently the CSV bulk
creation of Optical Nodes and Optical Pipes. Unlike the product workflows of
the families (create/modify/terminate/validate), tasks are not bound to a
product type: each task fans out to the shipped product workflows by launching
one sub-workflow per CSV row with ``start_process``.

Like the shipped product workflows, tasks are never registered by this module.
Consumers register them with the standard orchestrator-core mechanism, one
``LazyWorkflowInstance`` line per task in their own workflows package::

    from orchestrator.core.workflows import LazyWorkflowInstance

    LazyWorkflowInstance(
        "orchestrator.optical.workflows.tasks.bulk_create_optical_nodes",
        "bulk_create_optical_nodes",
    )
    LazyWorkflowInstance(
        "orchestrator.optical.workflows.tasks.bulk_create_optical_pipes",
        "bulk_create_optical_pipes",
    )

and persist them with ``orchestrator db migrate-workflows``.
"""
