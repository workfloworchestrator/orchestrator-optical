"""Shared validation steps for Optical Nodes."""

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.optical.workflows.optical_node.shared.modify import (
    update_optical_node_subscription_description,
)


@step("Load initial state")
def load_initial_state_optical_node(subscription: SubscriptionModel) -> State:
    """Load initial subscription state into the workflow process."""
    return {
        "subscription": subscription,
    }


#: Validation steps shared by every Optical Node product. Consumers declare
#: their own ``@validate_workflow`` with this step list; consumer models that
#: compose the block under a different attribute name can put the block in the
#: state under ``OPTICAL_NODE_BLOCK_STATE_KEY`` for the description update.
OPTICAL_NODE_VALIDATE_STEPS: StepList = (
    begin >> load_initial_state_optical_node >> update_optical_node_subscription_description
)
