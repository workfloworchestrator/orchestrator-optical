"""Shared step that retrieves the node role and software version from the device."""

from typing import Any

from pydantic_forms.types import State

from orchestrator.core.workflow import step
from orchestrator.optical.hal.optical_node import (
    retrieve_optical_node_role_and_software_version as _retrieve_optical_node_role_and_software_version,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.optical_node.shared.create import (
    optical_node_block_from_state,
)


@step("Retrieve node role and software version")
def retrieve_optical_node_role_and_software_version(
    optical_module_block: AbstractOpticalNodeBlockInactive | dict[str, Any] | None,
) -> State:
    """Connect to the node and write its role and software version to the block.

    This is the shared device-discovery step of the Optical Node create
    workflows: it resolves the block from the state and retrieves the node role
    and the software version from the device, dispatching on the vendor and
    platform of the node through
    :func:`orchestrator.optical.hal.optical_node.retrieve_optical_node_role_and_software_version`.
    It runs after the populate step, which writes the connection data (target
    ID, GMPLS ID, management IPs and location) onto the block.

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    node_block = optical_node_block_from_state(optical_module_block)
    role, software_version = _retrieve_optical_node_role_and_software_version(node_block)
    node_block.optical_node_role = role
    node_block.management.optical_module_node_software_version = software_version
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: node_block}
