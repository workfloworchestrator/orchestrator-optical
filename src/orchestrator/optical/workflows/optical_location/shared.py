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
)
from orchestrator.optical.workflows.shared import active_subscription_selector_by_block_type

#: State key under which the Optical Module Location block of the subscription
#: is passed between the shipped block steps. Consumers put the block they
#: compose (under any attribute name of their own model) in the state under
#: this key.
OPTICAL_LOCATION_BLOCK_STATE_KEY = "optical_location_block"


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


def active_location_subscription_selector(prompt: str | None = None) -> type[Choice]:
    """Create a `Choice` selector for active Optical Location subscriptions.

    Every concrete Optical Location product implementing the abstract location contract
    is matched through the product block names registered in
    ``OpticalModuleLocationBlockInactive.__names__``, regardless of how the users
    implement their concrete product blocks and subscriptions.

    Args:
        prompt: Prompt to display in the selection. If not provided, a default prompt
            will be generated.

    Returns:
        type[Choice]: A `Choice` class configured with the active location subscription
        options.
    """
    return active_subscription_selector_by_block_type(OpticalModuleLocationBlockInactive, prompt=prompt)


def optical_location_block_from_state(
    optical_location_block: OpticalModuleLocationBlockInactive | dict[str, Any] | None,
) -> OpticalModuleLocationBlockInactive | None:
    """Return the Optical Module Location block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_LOCATION_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the ``subscription_instance_id``) rather
    than as a domain model. This helper returns the value unchanged when it is
    already a domain model (in-process usage, e.g. in tests) and re-hydrates
    the block from the database by its ``subscription_instance_id`` otherwise.
    The most-derived block class is used, so blocks of any lifecycle are
    loaded.

    Args:
        optical_location_block: The block value from the workflow state, or None.

    Returns:
        The Optical Module Location block as a domain model, or None when the
        value is None.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``.
    """
    if optical_location_block is None:
        return None
    if isinstance(optical_location_block, OpticalModuleLocationBlockInactive):
        return optical_location_block
    subscription_instance_id = optical_location_block.get("subscription_instance_id")
    if subscription_instance_id is None:
        msg = "Optical Module Location block in the state has no subscription_instance_id"
        raise ValueError(msg)
    return OpticalModuleLocationBlock.from_db(subscription_instance_id=subscription_instance_id)


def optical_module_location_subscription_description(
    subscription: SubscriptionModel,
    optical_location_block: OpticalModuleLocationBlockInactive | None = None,
) -> str:
    """Generate the human-readable description of an Optical Module Location subscription.

    The description is derived from the block fields, so the same function can
    be reused by consumers that compose the shipped block under their own
    attribute: pass the shipped block explicitly, otherwise it falls back to
    the ``optical_location`` attribute of the shipped subscription models.

    Args:
        subscription: The Optical Module Location subscription.
        optical_location_block: The Optical Module Location block of the
            subscription, when it is not available under the
            ``optical_location`` attribute.

    Returns:
        The subscription description, e.g. ``"Amsterdam (ams-01)"`` or ``"ams-01"``.

    Raises:
        ValueError: If the subscription has no Optical Module Location block.
    """
    location = optical_location_block or getattr(subscription, "optical_location", None)
    if location is None:
        msg = "Optical Module Location subscription has no Optical Module Location block"
        raise ValueError(msg)
    if location.location_name:
        return f"{location.location_name} ({location.location_code})"
    return f"{location.location_code}"


@step("Set Optical Module Location subscription description")
def set_optical_module_location_subscription_description(
    subscription: SubscriptionModel,
    optical_location_block: OpticalModuleLocationBlockInactive | None = None,
) -> State:
    """Set the description of the Optical Module Location subscription.

    The block is read from the ``optical_location_block`` state key when
    present (e.g. when the shipped block steps ran against a consumer-owned
    block under a different attribute name); otherwise it falls back to the
    ``optical_location`` attribute of the shipped subscription models.

    Args:
        subscription: The Optical Module Location subscription.
        optical_location_block: The Optical Module Location block of the
            subscription, when it is available in the state under
            ``OPTICAL_LOCATION_BLOCK_STATE_KEY``.
    """
    location = optical_location_block_from_state(optical_location_block)
    subscription.description = optical_module_location_subscription_description(subscription, location)
    return {"subscription": subscription, "subscription_description": subscription.description}


@step("Load optical module location block")
def load_optical_module_location_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Module Location block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_location`` attribute: it makes the
    block available to the shipped block steps under
    ``OPTICAL_LOCATION_BLOCK_STATE_KEY``. Consumers that compose the shipped
    block under a different attribute name write their own one-step wiring
    instead.

    Args:
        subscription: The Optical Module Location subscription.

    Returns:
        The state with the block under the ``optical_location_block`` key.
    """
    return {OPTICAL_LOCATION_BLOCK_STATE_KEY: getattr(subscription, "optical_location", None)}


@step("Persist optical module location block")
def save_optical_module_location_block(
    subscription: SubscriptionModel,
    optical_location_block: OpticalModuleLocationBlockInactive,
) -> State:
    """Persist the Optical Module Location block found in the state to the database.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from the database by its ``subscription_instance_id``
    before it is saved. This step saves the block tree of the loaded
    subscription (any consumer subscription model that has-a the block)
    and returns the block, so it can be composed by any consumer workflow.

    Args:
        subscription: The subscription owning the block.
        optical_location_block: The Optical Module Location block to persist.

    Returns:
        The state with the block under the ``optical_location_block`` key.
    """
    location_block = optical_location_block_from_state(optical_location_block)
    if location_block is None:
        msg = "No Optical Module Location block in the state under OPTICAL_LOCATION_BLOCK_STATE_KEY"
        raise ValueError(msg)
    location_block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {OPTICAL_LOCATION_BLOCK_STATE_KEY: location_block}


__all__ = [
    "OPTICAL_LOCATION_BLOCK_STATE_KEY",
    "active_location_subscription_selector",
    "check_location_code_uniqueness",
    "load_optical_module_location_block",
    "optical_location_block_from_state",
    "optical_module_location_subscription_description",
    "save_optical_module_location_block",
    "set_optical_module_location_subscription_description",
]
