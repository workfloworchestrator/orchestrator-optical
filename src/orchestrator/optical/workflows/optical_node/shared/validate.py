"""Shared validation steps for Optical Nodes."""

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.optical_node.shared.create import (
    _optical_node_block_of_subscription,
)
from orchestrator.optical.workflows.optical_node.shared.modify import save_optical_node_block
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
VALIDATE_OPTICAL_NODE_BLOCK_STEPS: StepList = (
    begin >> retrieve_optical_node_role_and_software_version >> save_optical_node_block
)
