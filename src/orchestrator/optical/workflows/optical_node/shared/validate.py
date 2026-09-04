"""Shared validation steps for Optical Nodes."""

from typing import Any

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.optical.hal.node import retrieve_software_version
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.optical_node.shared.create import (
    _optical_node_block_of_subscription,
    optical_node_block_from_state,
)
from orchestrator.optical.workflows.optical_node.shared.modify import save_optical_node_block


@step("Load initial state")
def load_initial_state_optical_node(subscription: SubscriptionModel) -> State:
    """Load initial subscription state into the workflow process.

    The subscription and its Optical Node block are put in the state, so the
    shared steps (which act on the block under ``OPTICAL_MODULE_BLOCK_STATE_KEY``)
    can operate on them.

    Args:
        subscription: The Optical Node subscription.

    Returns:
        The state with the subscription and its block under the
        ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Node block under the
            ``optical_node`` attribute.
    """
    return {
        "subscription": subscription,
        OPTICAL_MODULE_BLOCK_STATE_KEY: _optical_node_block_of_subscription(subscription),
    }


@step("Refresh Optical Node software version")
def refresh_optical_node_software_version(
    optical_module_block: AnyOpticalNodeBlockProvisioningUnion | dict[str, Any] | None,
) -> State:
    """Refresh the software version of the Optical Node from the device.

    This is the block-level refresh step of the Optical Node validation: it
    operates only on the block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the same block the rest of the shipped
    block steps act on). The block is re-hydrated from its serialized form (see
    :func:`optical_node_block_from_state`) and the software version is retrieved
    from the device through the HAL (dispatching per vendor). The refreshed
    block is returned under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` and persisted by
    the save step that follows it in the shared validation step list, so a
    stale ``subscription`` returned by the framework's automatic persistence
    (``inject_args`` -> ``_save_models``) cannot re-save the pre-refresh block.

    Args:
        optical_module_block: The Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Returns:
        The state with the refreshed node block under
        ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    node_block = optical_node_block_from_state(optical_module_block)
    version = retrieve_software_version(node_block)
    node_block.management.optical_module_node_software_version = version
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: node_block}


#: Validation step list shared by every Optical Node product: the software
#: version of the node is refreshed from the device and the refreshed block is
#: persisted by the last step. This is the block-level step list of the family;
#: the subscription-level steps (loading the subscription and its block into the
#: state and recomputing the subscription description from the refreshed block)
#: belong to the shipped per-vendor validate workflows, not to this reusable
#: step list. Consumers declare their own ``@validate_workflow`` with this step
#: list, loading the block into the state (the shipped
#: :func:`load_initial_state_optical_node` puts the ``subscription`` and its
#: block in the state) before it runs.
VALIDATE_OPTICAL_NODE_BLOCK_STEPS: StepList = begin >> refresh_optical_node_software_version >> save_optical_node_block
