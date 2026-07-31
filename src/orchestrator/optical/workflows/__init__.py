"""."""

from orchestrator.core.workflows import LazyWorkflowInstance

# Nokia FlexILS Optical Node
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

# Nokia Groove G30 Optical Node
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_groove_g30.create",
    "create_optical_node_nokia_groove_g30",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify",
    "modify_optical_node_nokia_groove_g30",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_groove_g30.terminate",
    "terminate_optical_node_nokia_groove_g30",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_groove_g30.validate",
    "validate_optical_node_nokia_groove_g30",
)

# Nokia GX G42 Optical Node
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_gx_g42.create",
    "create_optical_node_nokia_gx_g42",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_gx_g42.modify",
    "modify_optical_node_nokia_gx_g42",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_gx_g42.terminate",
    "terminate_optical_node_nokia_gx_g42",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_node.nokia_gx_g42.validate",
    "validate_optical_node_nokia_gx_g42",
)
