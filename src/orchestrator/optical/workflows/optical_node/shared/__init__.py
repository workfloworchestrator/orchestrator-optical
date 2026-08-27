"""Shared workflow parts and utilities for Optical Nodes.

The shared parts are the block-level steps and the state key under which the
Optical Node block travels in the workflow state
(``OPTICAL_NODE_BLOCK_STATE_KEY``). The shipped block steps bind to that state
key and never to a specific subscription model: consumers compose the shipped
block with a has-a relation on their own model and inject it into the state.
"""

from orchestrator.optical.workflows.optical_node.shared.create import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    OPTICAL_NODE_PRODUCT_TYPES,
    optical_node_block_from_state,
    optical_node_subscription_description,
    populate_abstract_optical_node_fields,
    validate_gmpls_id_uniqueness,
    validate_management_ips_uniqueness,
    validate_optical_flexils_target_id_uniqueness,
    validate_optical_node_fqdn_uniqueness,
)
from orchestrator.optical.workflows.optical_node.shared.forms import (
    create_optical_node_location_form,
    create_optical_node_management_form,
)
from orchestrator.optical.workflows.optical_node.shared.modify import (
    load_optical_node_block,
    save_optical_node_block,
    update_optical_node_block_fields,
    update_optical_node_subscription_description,
)
from orchestrator.optical.workflows.optical_node.shared.terminate import (
    OPTICAL_NODE_TERMINATE_STEPS,
    delete_optical_node_from_oss_bss,
    terminate_initial_input_form_generator,
    terminate_optical_node_form,
    terminate_optical_node_form_pages,
)
from orchestrator.optical.workflows.optical_node.shared.validate import (
    OPTICAL_NODE_VALIDATE_STEPS,
    load_initial_state_optical_node,
    refresh_optical_node_software_version,
)

__all__ = [
    "OPTICAL_NODE_BLOCK_STATE_KEY",
    "OPTICAL_NODE_PRODUCT_TYPES",
    "OPTICAL_NODE_TERMINATE_STEPS",
    "OPTICAL_NODE_VALIDATE_STEPS",
    "create_optical_node_location_form",
    "create_optical_node_management_form",
    "delete_optical_node_from_oss_bss",
    "load_initial_state_optical_node",
    "load_optical_node_block",
    "optical_node_block_from_state",
    "optical_node_subscription_description",
    "populate_abstract_optical_node_fields",
    "refresh_optical_node_software_version",
    "save_optical_node_block",
    "terminate_initial_input_form_generator",
    "terminate_optical_node_form",
    "terminate_optical_node_form_pages",
    "update_optical_node_block_fields",
    "update_optical_node_subscription_description",
    "validate_gmpls_id_uniqueness",
    "validate_management_ips_uniqueness",
    "validate_optical_flexils_target_id_uniqueness",
    "validate_optical_node_fqdn_uniqueness",
]
