"""Shared modification steps for Optical Nodes."""

from typing import Any

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import step
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockInactive
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared.create import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    _optical_node_block_of_subscription,
    optical_node_block_from_state,
    optical_node_subscription_description,
)


def update_optical_node_block_fields(
    optical_node_block: Any,
    *,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> None:
    """Update the common Optical Node block fields.

    The block is intentionally untyped: the abstract Optical Node block does
    not declare the fields populated here (they are vendor-specific), and the
    helper is shared by all vendors and their consumers.

    Args:
        optical_node_block: The Optical Node block to update (any lifecycle variant).
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.
    """
    optical_node_block.management.optical_module_node_fqdn = optical_module_node_fqdn
    optical_node_block.management.optical_module_node_dcn_loopback_ip = optical_module_node_dcn_loopback_ip
    optical_node_block.management.optical_module_node_dcn_interface_ip = optical_module_node_dcn_interface_ip


@step("Load optical node block")
def load_optical_node_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Node block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_node`` attribute: it makes the block
    available to the shipped block steps under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    Consumers that compose the shipped block under a different attribute name
    write their own one-step wiring instead.

    Args:
        subscription: The Optical Node subscription.

    Returns:
        The state with the block under the ``optical_node_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Node block under the
            ``optical_node`` attribute.
    """
    return {OPTICAL_NODE_BLOCK_STATE_KEY: _optical_node_block_of_subscription(subscription)}


@step("Updating subscription description")
def update_optical_node_subscription_description(
    subscription: SubscriptionModel,
    optical_node_block: AbstractOpticalNodeBlockInactive | None = None,
) -> State:
    """Update the description of the Optical Node subscription.

    The block is read from the ``optical_node_block`` state key when present
    (e.g. when the shipped block steps ran against a consumer-owned block);
    otherwise it falls back to the ``optical_node`` attribute of the shipped
    subscription models.

    Args:
        subscription: The Optical Node subscription.
        optical_node_block: The Optical Node block of the subscription, when it
            is available in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    """
    subscription.description = optical_node_subscription_description(subscription, optical_node_block)
    return {"subscription": subscription, "subscription_description": subscription.description}


@step("Persist optical node block")
def save_optical_node_block(
    subscription: SubscriptionModel,
    optical_node_block: AbstractOpticalNodeBlockInactive,
) -> State:
    """Persist the Optical Node block found in the state to the database.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from its serialized form (see
    :func:`optical_node_block_from_state`) before it is saved. This step saves
    the block tree of the loaded subscription (any consumer subscription model
    that has-a the block works) and returns the block, so it can be composed
    by any consumer workflow.

    Args:
        subscription: The subscription owning the block.
        optical_node_block: The Optical Node block to persist.

    Returns:
        The state with the block under the ``optical_node_block`` key.

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    """
    node_block = optical_node_block_from_state(optical_node_block)
    if node_block is None:
        msg = "No Optical Node block in the state under OPTICAL_NODE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    node_block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {OPTICAL_NODE_BLOCK_STATE_KEY: node_block}
