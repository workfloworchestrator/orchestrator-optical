"""Shared helpers and steps for Optical Module Location workflows.

This module ships the parts shared by the create, modify and validate
workflows of the family: the state key under which the shipped Optical Module
Location block travels in the workflow state, the location subscription
selectors, the human-readable subscription description, the block re-hydration
and persistence steps.
"""

from typing import Any, cast

from pydantic_forms.types import State
from pydantic_forms.validators import Choice

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import step
from orchestrator.optical.db import subscription_instances_by_block_type_and_resource_value
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import rehydrate_optical_module_block
from orchestrator.optical.workflows.shared import active_instance_selector_by_block_type


def check_location_code_uniqueness(
    location_code: str,
    exclude_subscription_id: str | None = None,
) -> None:
    """Raise if the location code is already in use by another location subscription.

    The check is block-based: it queries the subscription instances of the
    shipped ``OpticalModuleLocationBlock`` block type whose ``location_code``
    resource value equals the given code and whose owner subscription is
    INITIAL, PROVISIONING or ACTIVE. Because every consumer that composes the
    shipped block persists it under the shipped block name, the check also
    covers composed product types without hardcoding a product type. The
    subscription being modified is excluded by ``exclude_subscription_id``, so
    a subscription never conflicts with its own location block.

    This is an application-level check only: the module ships no database
    migrations (consumers generate them), so no unique constraint enforces the
    uniqueness in the database. As a known limitation there is a residual
    TOCTOU race between the check and the subsequent block save; the block
    population and update steps re-check at execution time to shrink the
    window, but it cannot be fully closed by the module.

    Args:
        location_code: The location code to check.
        exclude_subscription_id: Identifier of the subscription being modified,
            whose own location block is not a conflict.

    Raises:
        ValueError: If another subscription already uses the location code,
            naming the conflicting code and the conflicting subscription.
    """
    instances = subscription_instances_by_block_type_and_resource_value(
        cast(str, OpticalModuleLocationBlock.name),
        "location_code",
        location_code,
        [SubscriptionLifecycle.INITIAL, SubscriptionLifecycle.PROVISIONING, SubscriptionLifecycle.ACTIVE],
    )
    for instance in instances:
        if exclude_subscription_id is not None and str(instance.subscription_id) == str(exclude_subscription_id):
            continue
        description = instance.subscription.description if instance.subscription is not None else None
        conflicting = str(instance.subscription_id) + (f" ('{description}')" if description else "")
        msg = f"Location code '{location_code}' is already in use by subscription {conflicting}"
        raise ValueError(msg)


def active_location_instance_selector(prompt: str | None = None) -> type[Choice]:
    """Create a `Choice` selector for active Optical Location blocks.

    Every concrete Optical Location product implementing the abstract location contract
    is matched through the product block names registered in
    ``OpticalModuleLocationBlockInactive.__names__``, regardless of how the users
    implement their concrete product blocks and subscriptions. Option values are
    the location block subscription instance ids, resolved with
    :func:`orchestrator.optical.db.location_block_from_instance`.

    Args:
        prompt: Prompt to display in the selection. If not provided, a default prompt
            will be generated.

    Returns:
        type[Choice]: A `Choice` class configured with the active location block
        options.
    """
    return active_instance_selector_by_block_type(
        OpticalModuleLocationBlockInactive, ["location_name", "location_code"], prompt=prompt
    )


def optical_location_block_from_state(
    optical_module_block: OpticalModuleLocationBlockProvisioning | dict[str, Any] | None,
) -> OpticalModuleLocationBlockProvisioning:
    """Return the Optical Module Location block of the workflow state as a domain model.

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
        optical_module_block: The block value from the workflow state, or None.

    Returns:
        The Optical Module Location block as a domain model, or None when the
        value is None.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``.
    """
    if optical_module_block is None:
        msg = "No Optical Module Location block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    if isinstance(optical_module_block, OpticalModuleLocationBlockProvisioning):
        return optical_module_block
    return _optical_module_location_block_from_state(optical_module_block)


def _optical_module_location_block_from_state(
    optical_module_block: dict[str, Any],
) -> OpticalModuleLocationBlockProvisioning:
    """Reconstruct an Optical Module Location block from its serialized form.

    Thin wrapper around the family-agnostic re-hydration
    (:func:`orchestrator.optical.workflows.block.rehydrate_optical_module_block`),
    kept for the narrowed return type and the family-specific error message.

    Args:
        optical_module_block: The serialized block from the workflow state.

    Returns:
        The Optical Module Location block as a domain model.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``,
            or if no subscription instance exists with the given id.
    """
    return cast(
        OpticalModuleLocationBlockProvisioning,
        rehydrate_optical_module_block(optical_module_block, block_description="Optical Module Location"),
    )


def _optical_module_location_block_of_subscription(
    subscription: SubscriptionModel,
) -> OpticalModuleLocationBlockInactive:
    """Return the Optical Module Location block under the ``optical_location`` attribute.

    This is the shipped-model fallback of the family: it reads the block from
    the ``optical_location`` attribute of the subscription, which the shipped
    subscription models always have.

    Args:
        subscription: The Optical Module Location subscription.

    Returns:
        The Optical Module Location block of the subscription.

    Raises:
        ValueError: If the subscription has no block under the attribute.
    """
    location = getattr(subscription, "optical_location", None)
    if location is None:
        msg = (
            "Optical Module Location subscription has no Optical Module Location block under attribute "
            "'optical_location': the subscription model must have-a the Optical Module Location block, "
            "e.g. under 'optical_location'"
        )
        raise ValueError(msg)
    return location


def optical_module_location_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalModuleLocationBlockProvisioning | None = None,
) -> str:
    """Generate the human-readable description of an Optical Module Location subscription.

    The description is derived from the block fields, so the same function can
    be reused by consumers that compose the shipped block under their own
    attribute: pass the shipped block explicitly, otherwise it falls back to
    the ``optical_location`` attribute of the shipped subscription models.

    Args:
        subscription: The Optical Module Location subscription.
        optical_module_block: The Optical Module Location block of the
            subscription, when it is not available under the
            ``optical_location`` attribute.

    Returns:
        The subscription description, e.g. ``"Amsterdam (ams-01)"`` or ``"ams-01"``.

    Raises:
        ValueError: If the subscription has no Optical Module Location block
            under the ``optical_location`` attribute and no block was passed.
    """
    location = optical_module_block or _optical_module_location_block_of_subscription(subscription)
    if location.location_name:
        return f"{location.location_name} ({location.location_code})"
    return f"{location.location_code}"


@step("Set Optical Module Location subscription description")
def set_optical_module_location_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalModuleLocationBlockProvisioning | None = None,
) -> State:
    """Set the description of the Optical Module Location subscription.

    The block is re-hydrated from the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``:
    the shipped create block steps (and a consumer's construct step) always put
    the block in the state before this step runs, so it does not fall back to
    the ``optical_location`` attribute of the subscription.

    Args:
        subscription: The Optical Module Location subscription.
        optical_module_block: The Optical Module Location block of the
            subscription, in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If there is no Optical Module Location block in the state
            under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    location = optical_location_block_from_state(optical_module_block)
    subscription.description = optical_module_location_subscription_description(subscription, location)
    return {"subscription": subscription, "subscription_description": subscription.description}


@step("Load optical module location block")
def load_optical_module_location_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Module Location block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_location`` attribute: it makes the
    block available to the shipped block steps under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. Consumers that compose the shipped
    block under a different attribute name write their own one-step wiring
    instead.

    Args:
        subscription: The Optical Module Location subscription.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Module Location block
            under the ``optical_location`` attribute.
    """
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: _optical_module_location_block_of_subscription(subscription)}


__all__ = [
    "OPTICAL_MODULE_BLOCK_STATE_KEY",
    "active_location_instance_selector",
    "check_location_code_uniqueness",
    "load_optical_module_location_block",
    "optical_location_block_from_state",
    "optical_module_location_subscription_description",
    "set_optical_module_location_subscription_description",
]
