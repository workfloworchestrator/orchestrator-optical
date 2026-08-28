"""Shared validation steps for Optical Nodes."""

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.hal import optical_node as optical_node_hal
from orchestrator.optical.workflows.optical_node.shared.modify import (
    update_optical_node_subscription_description,
)


@step("Load initial state")
def load_initial_state_optical_node(subscription: SubscriptionModel) -> State:
    """Load initial subscription state into the workflow process."""
    return {
        "subscription": subscription,
    }


@step("Refresh Optical Node software version")
def refresh_optical_node_software_version(subscription: SubscriptionModel) -> State:
    """Refresh the software version of the Optical Node from the device.

    The ACTIVE node block of the subscription is loaded from the database, the
    software version is retrieved from the device through the HAL (dispatching
    per vendor) and the version is persisted on the block.

    Args:
        subscription: The Optical Node subscription.

    Returns:
        The state with the subscription, whose node block now carries the
        refreshed software version.
    """
    node_block = node_block_from_subscription(str(subscription.subscription_id))
    version = optical_node_hal.retrieve_software_version(node_block)
    node_block.management.optical_module_node_software_version = version
    node_block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {"subscription": subscription}


#: Validation steps shared by every Optical Node product: the software version
#: of the node is refreshed from the device before the subscription description
#: is recomputed from the refreshed block. Consumers declare their own
#: ``@validate_workflow`` with this step list; consumer models that compose the
#: block under a different attribute name can put the block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the description update.
OPTICAL_NODE_VALIDATE_STEPS: StepList = (
    begin
    >> load_initial_state_optical_node
    >> refresh_optical_node_software_version
    >> update_optical_node_subscription_description
)
