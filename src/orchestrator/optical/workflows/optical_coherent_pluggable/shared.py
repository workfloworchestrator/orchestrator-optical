"""Shared helpers and steps for Optical Coherent Pluggable workflows.

This module ships the parts shared by the create, modify and validate
workflows of the family: the state key under which the shipped Coherent
Pluggable block travels in the workflow state, the resolution of the Optical
Module Packet Node block hosting a pluggable, the human-readable subscription
description (a shipped-product-type concept, because the part number lives on
the subscription) and the block persistence steps.
"""

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import step
from orchestrator.optical.db import packet_node_block_from_subscription
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlockInactive,
)
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
    OpticalCoherentPluggableInactive,
)

#: State key under which the Optical Coherent Pluggable block of the
#: subscription is passed between the shipped block steps. Consumers put the
#: block they compose (under any attribute name of their own model) in the
#: state under this key.
OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY = "optical_coherent_pluggable_block"


def optical_coherent_pluggable_subscription_description(subscription: OpticalCoherentPluggableInactive) -> str:
    """Generate the human-readable description of a Coherent Pluggable subscription.

    The description reads the part number from the subscription and the host
    node identity from the block, so it is a shipped-product-type concept:
    block-level steps never touch it. It is used by the shipped construct step
    and by the shipped-type description refresh step.

    Args:
        subscription: The Optical Coherent Pluggable subscription.

    Returns:
        The subscription description, e.g. ``"node.example.com port-1 (part)"``.
    """
    pluggable = subscription.optical_coherent_pluggable
    host_node = pluggable.optical_port_host_node
    if host_node is not None:
        fqdn = host_node.management.optical_module_node_fqdn
        host_name = str(fqdn) if fqdn is not None else "Unattached Host"
    else:
        host_name = "Unattached Host"
    part_number = subscription.optical_coherent_pluggable_part_number
    return f"{host_name} {pluggable.optical_port_name} ({part_number})"


@step("Load optical coherent pluggable block")
def load_optical_coherent_pluggable_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Coherent Pluggable block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_coherent_pluggable`` attribute: it
    makes the block available to the shipped block steps under
    ``OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY``. Consumers that compose the
    shipped block under a different attribute name write their own one-step
    wiring instead.

    Args:
        subscription: The Optical Coherent Pluggable subscription.

    Returns:
        The state with the block under the ``optical_coherent_pluggable_block`` key.
    """
    return {OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: getattr(subscription, "optical_coherent_pluggable", None)}


@step("Persist optical coherent pluggable block")
def save_optical_coherent_pluggable_block(
    subscription: SubscriptionModel,
    optical_coherent_pluggable_block: OpticalCoherentPluggableBlockInactive,
) -> State:
    """Persist the Optical Coherent Pluggable block found in the state to the database.

    Workflow steps reload the subscription from the database on every step, so
    mutations made on the block in the state are lost unless the block is
    persisted explicitly. This step saves the block tree of the loaded
    subscription (any consumer subscription model that has-a the block works)
    and returns the block, so it can be composed by any consumer workflow.

    Args:
        subscription: The subscription owning the block.
        optical_coherent_pluggable_block: The Optical Coherent Pluggable block to persist.

    Returns:
        The state with the block under the ``optical_coherent_pluggable_block`` key.
    """
    optical_coherent_pluggable_block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: optical_coherent_pluggable_block}


@step("Updating subscription description")
def update_optical_coherent_pluggable_subscription_description(
    subscription: OpticalCoherentPluggable,
) -> State:
    """Refresh the description of an Optical Coherent Pluggable subscription.

    This step is for the shipped product type only: the description includes
    the subscription-level part number, so it cannot be computed from the
    block alone. Consumers with their own product type refresh their own
    description with their own step.

    Args:
        subscription: The Optical Coherent Pluggable subscription being modified or validated.

    Returns:
        The state with the updated subscription.
    """
    subscription.description = optical_coherent_pluggable_subscription_description(subscription)
    return {"subscription": subscription}


__all__ = [
    "OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY",
    "load_optical_coherent_pluggable_block",
    "optical_coherent_pluggable_subscription_description",
    "packet_node_block_from_subscription",
    "save_optical_coherent_pluggable_block",
    "update_optical_coherent_pluggable_subscription_description",
]
