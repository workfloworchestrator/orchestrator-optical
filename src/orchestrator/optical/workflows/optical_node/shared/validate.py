"""Shared validation steps for Optical Nodes."""

from typing import Any

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.optical.hal.reconcile import config_overrides, golden_config
from orchestrator.optical.hal.sessions import device_sessions
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.optical_node.shared.create import (
    _optical_node_block_of_subscription,
    optical_node_block_from_state,
)
from orchestrator.optical.workflows.optical_node.shared.retrieve import retrieve_optical_node_role_and_software_version


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


@step("Show applied configuration")
@device_sessions()
def show_optical_node_applied_configuration(
    optical_module_block: AnyOpticalNodeBlockProvisioningUnion | dict[str, Any] | None,
) -> State:
    """Put the golden configuration and the overrides of the node in the state, visible in the process detail.

    ``golden_config`` is every ``{path: value}`` the product blocks applied on the node and
    ``config_overrides`` every ``{path: value}`` the NOC set on it (an overridden path is in
    both). They are read from the database, not from the device, and they are empty for the
    nodes that are not configured declaratively (FlexILS).

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_node_block_from_state(optical_module_block)
    return {"golden_config": golden_config(block), "config_overrides": config_overrides(block)}


#: Validation step list shared by every Optical Node product: the software
#: version of the node is refreshed from the device, the configuration applied
#: by the orchestrator on the node is shown, and the refreshed block is
#: persisted by the last step. This is the block-level step list of the family;
#: the subscription-level steps (loading the subscription and its block into the
#: state and recomputing the subscription description from the refreshed block)
#: belong to the shipped per-vendor validate workflows, not to this reusable
#: step list. Consumers declare their own ``@validate_workflow`` with this step
#: list, loading the block into the state (the shipped
#: :func:`load_initial_state_optical_node` puts the ``subscription`` and its
#: block in the state) before it runs.
VALIDATE_OPTICAL_NODE_BLOCK_STEPS: StepList = (
    begin
    >> retrieve_optical_node_role_and_software_version
    >> show_optical_node_applied_configuration
    >> save_optical_module_block
)
