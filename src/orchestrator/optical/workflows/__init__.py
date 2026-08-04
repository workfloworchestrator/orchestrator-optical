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

# Fiber Span Workflows
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.create", "create_fiber_span")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.modify", "modify_fiber_span")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.terminate", "terminate_fiber_span")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.validate", "validate_fiber_span")

# Fiber Patch Workflows
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.create", "create_fiber_patch")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.modify", "modify_fiber_patch")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate", "terminate_fiber_patch")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.validate", "validate_fiber_patch")

# Leased Spectrum Workflows
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.create", "create_leased_spectrum")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.modify", "modify_leased_spectrum")
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate", "terminate_leased_spectrum"
)
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.validate", "validate_leased_spectrum")

# Optical Coherent Pluggable Workflows
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_coherent_pluggable.create",
    "create_optical_coherent_pluggable",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_coherent_pluggable.modify",
    "modify_optical_coherent_pluggable",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_coherent_pluggable.terminate",
    "terminate_optical_coherent_pluggable",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_coherent_pluggable.validate",
    "validate_optical_coherent_pluggable",
)

# Optical Spectrum Workflows
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum",
    "create_optical_spectrum",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum",
    "modify_optical_spectrum",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum",
    "terminate_optical_spectrum",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum",
    "validate_optical_spectrum",
)

# Optical Digital Service Workflows
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service",
    "create_optical_digital_service",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service",
    "modify_optical_digital_service",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service",
    "terminate_optical_digital_service",
)
LazyWorkflowInstance(
    "orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service",
    "validate_optical_digital_service",
)
