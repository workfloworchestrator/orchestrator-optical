"""Shared helpers and steps for Optical Coherent Pluggable workflows.

This module ships the parts shared by the create, modify and validate
workflows of the family: the state key under which the shipped Coherent
Pluggable block travels in the workflow state, the human-readable subscription
description (a shipped-product-type concept, because the part number lives on
the subscription) and the block persistence steps.
"""

from typing import Any, cast

from pydantic_forms.types import State

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import step
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggableSubscriptionInactive,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import rehydrate_optical_module_block


def optical_coherent_pluggable_subscription_description(
    subscription: OpticalCoherentPluggableSubscriptionInactive,
    optical_module_block: OpticalCoherentPluggableBlockProvisioning | None = None,
) -> str:
    """Generate the human-readable description of a Coherent Pluggable subscription.

    The description reads the part number from the subscription and the host
    node identity from the block, so it is a shipped-product-type concept. The
    same function can be reused by consumers that compose the shipped block
    under their own attribute: pass the shipped block explicitly, otherwise it
    falls back to the ``optical_coherent_pluggable`` attribute of the shipped
    subscription models.

    Args:
        subscription: The Optical Coherent Pluggable subscription.
        optical_module_block: The Optical Coherent Pluggable block of the
            subscription, when it is not available under the
            ``optical_coherent_pluggable`` attribute.

    Returns:
        The subscription description, e.g. ``"node.example.com port-1 (part)"``.
    """
    pluggable = optical_module_block or _optical_coherent_pluggable_block_of_subscription(subscription)
    host_node = pluggable.optical_port_host_node
    if host_node is not None:
        fqdn = host_node.management.optical_module_node_fqdn
        host_name = str(fqdn) if fqdn is not None else "Unattached Host"
    else:
        host_name = "Unattached Host"
    part_number = subscription.optical_coherent_pluggable_part_number
    return f"{host_name} {pluggable.optical_port_name} ({part_number})"


def optical_coherent_pluggable_block_from_state(
    optical_module_block: OpticalCoherentPluggableBlockProvisioning | dict[str, Any] | None,
) -> OpticalCoherentPluggableBlockProvisioning:
    """Return the Optical Coherent Pluggable block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the full block data) rather than as a domain
    model. This helper returns the value unchanged when it is already a domain
    model (in-process usage, e.g. in tests) and reconstructs the block from the
    serialized data otherwise. The lifecycle variant of the block is resolved
    from the status of its owner subscription, so blocks of any lifecycle are
    loaded as their matching variant (INITIAL, PROVISIONING or ACTIVE). The
    shipped block steps always operate on the PROVISIONING variant: their
    callers construct the block with the mandatory fields set and transition
    the subscription to PROVISIONING before running them (the ACTIVE variant is
    a subtype of the PROVISIONING one, so validation blocks load fine too).

    Args:
        optical_module_block: The block value from the workflow
            state, or None.

    Returns:
        The Optical Coherent Pluggable block as a domain model.

    Raises:
        ValueError: If there is no Optical Coherent Pluggable block in the
            state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``, or if the block in
            the state has no ``subscription_instance_id``.
    """
    if optical_module_block is None:
        msg = "No Optical Coherent Pluggable block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    if isinstance(optical_module_block, OpticalCoherentPluggableBlockProvisioning):
        return optical_module_block
    return _optical_coherent_pluggable_block_from_state(optical_module_block)


def _optical_coherent_pluggable_block_from_state(
    optical_module_block: dict[str, Any],
) -> OpticalCoherentPluggableBlockProvisioning:
    """Reconstruct an Optical Coherent Pluggable block from its serialized form.

    Thin wrapper around the family-agnostic re-hydration
    (:func:`orchestrator.optical.workflows.block.rehydrate_optical_module_block`),
    kept for the narrowed return type and the family-specific error message.

    Args:
        optical_module_block: The serialized block from the workflow state.

    Returns:
        The Optical Coherent Pluggable block as a domain model.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``,
            or if no subscription instance exists with the given id.
    """
    return cast(
        OpticalCoherentPluggableBlockProvisioning,
        rehydrate_optical_module_block(optical_module_block, block_description="Optical Coherent Pluggable"),
    )


def _optical_coherent_pluggable_block_of_subscription(
    subscription: SubscriptionModel,
) -> OpticalCoherentPluggableBlockProvisioning:
    """Return the Optical Coherent Pluggable block under the ``optical_coherent_pluggable`` attribute.

    This is the shipped-model fallback of the family: it reads the block from
    the ``optical_coherent_pluggable`` attribute of the subscription, which the
    shipped subscription models always have. The subscription is expected to be
    in the PROVISIONING lifecycle (or ACTIVE, a subtype of it), so the block
    is the PROVISIONING variant.

    Args:
        subscription: The Optical Coherent Pluggable subscription.

    Returns:
        The Optical Coherent Pluggable block of the subscription.

    Raises:
        ValueError: If the subscription has no block under the attribute.
    """
    pluggable = getattr(subscription, "optical_coherent_pluggable", None)
    if pluggable is None:
        msg = (
            "Optical Coherent Pluggable subscription has no Optical Coherent Pluggable block under attribute "
            "'optical_coherent_pluggable': the subscription model must have-a the Optical Coherent Pluggable "
            "block, e.g. under 'optical_coherent_pluggable'"
        )
        raise ValueError(msg)
    return pluggable


@step("Load optical coherent pluggable block")
def load_optical_coherent_pluggable_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Coherent Pluggable block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_coherent_pluggable`` attribute: it
    makes the block available to the shipped block steps under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. Consumers that compose the
    shipped block under a different attribute name write their own one-step
    wiring instead.

    Args:
        subscription: The Optical Coherent Pluggable subscription.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Coherent Pluggable block
            under the ``optical_coherent_pluggable`` attribute.
    """
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: _optical_coherent_pluggable_block_of_subscription(subscription)}


@step("Updating subscription description")
def update_optical_coherent_pluggable_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalCoherentPluggableBlockProvisioning | None = None,
) -> State:
    """Refresh the description of an Optical Coherent Pluggable subscription.

    This step is for the shipped product type only: the description includes
    the subscription-level part number, kept as the source of truth on the
    subscription (the block also stores a copy, kept in sync by the construct
    step). Consumers with their own product type refresh their own
    description with their own step.

    The block is re-hydrated from the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``:
    the shipped create block steps (and a consumer's construct step) always put
    the block in the state before this step runs, so it does not fall back to
    the ``optical_coherent_pluggable`` attribute of the subscription.

    Args:
        subscription: The Optical Coherent Pluggable subscription being modified or validated.
        optical_module_block: The Optical Coherent Pluggable block of the
            subscription, in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If there is no Optical Coherent Pluggable block in the state
            under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    pluggable = optical_coherent_pluggable_block_from_state(optical_module_block)
    subscription.description = optical_coherent_pluggable_subscription_description(
        cast(OpticalCoherentPluggableSubscriptionInactive, subscription), pluggable
    )
    return {"subscription": subscription, "subscription_description": subscription.description}


__all__ = [
    "OPTICAL_MODULE_BLOCK_STATE_KEY",
    "load_optical_coherent_pluggable_block",
    "optical_coherent_pluggable_block_from_state",
    "optical_coherent_pluggable_subscription_description",
    "update_optical_coherent_pluggable_subscription_description",
]
