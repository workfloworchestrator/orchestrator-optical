"""Shared modification steps for Optical Nodes."""

from typing import Any

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import step
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockProvisioning
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.optical_node.shared.create import (
    _optical_node_block_of_subscription,
    optical_node_block_from_state,
    optical_node_subscription_description,
)


def update_optical_node_block_fields(
    optical_module_block: Any,
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
        optical_module_block: The Optical Node block to update (any lifecycle variant).
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.
    """
    optical_module_block.management.optical_module_node_fqdn = optical_module_node_fqdn
    optical_module_block.management.optical_module_node_dcn_loopback_ip = optical_module_node_dcn_loopback_ip
    optical_module_block.management.optical_module_node_dcn_interface_ip = optical_module_node_dcn_interface_ip


@step("Load optical node block")
def load_optical_node_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Node block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_node`` attribute: it makes the block
    available to the shipped block steps under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    Consumers that compose the shipped block under a different attribute name
    write their own one-step wiring instead.

    Args:
        subscription: The Optical Node subscription.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Node block under the
            ``optical_node`` attribute.
    """
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: _optical_node_block_of_subscription(subscription)}


@step("Updating subscription description")
def update_optical_node_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: AbstractOpticalNodeBlockProvisioning | None = None,
) -> State:
    """Update the description of the Optical Node subscription.

    The block is re-hydrated from the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``:
    the shipped block steps (and a consumer's construct step) always put the
    block in the state before this step runs, so it does not fall back to the
    ``optical_node`` attribute of the subscription.

    Args:
        subscription: The Optical Node subscription.
        optical_module_block: The Optical Node block of the subscription, in the
            state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    # Workflow steps execute with the state serialized between steps, so the
    # block arrives as its serialized form and is re-hydrated from the database.
    node_block = optical_node_block_from_state(optical_module_block)
    subscription.description = optical_node_subscription_description(subscription, node_block)
    return {"subscription": subscription, "subscription_description": subscription.description}


@step("Persist optical node block")
def save_optical_node_block(
    subscription: SubscriptionModel,
    optical_module_block: AbstractOpticalNodeBlockProvisioning,
) -> State:
    """Persist the Optical Node block found in the state to the database.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from its serialized form (see
    :func:`optical_node_block_from_state`) before it is saved. This step saves
    the block tree of the loaded subscription (any consumer subscription model
    that has-a the block works) and returns the block, so it can be composed
    by any consumer workflow. The shipped block steps always operate on the
    PROVISIONING variant: their callers provide the block with the mandatory
    fields set and the owner subscription in the PROVISIONING status.

    Args:
        subscription: The subscription owning the block.
        optical_module_block: The Optical Node block to persist.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    node_block = optical_node_block_from_state(optical_module_block)
    node_block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: node_block}
