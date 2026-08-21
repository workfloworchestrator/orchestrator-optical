"""Shared helpers and selectors for Optical Location workflows."""

from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockInactive
from orchestrator.optical.products.product_types.optical_location import AbstractOpticalLocationInactive
from orchestrator.optical.workflows.shared import (
    active_subscription_selector_by_block_type,
    subscription_from_subscription,
)


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


def location_block_from_subscription(location_id: UUIDstr) -> OpticalModuleLocationBlockInactive:
    """Return the Optical Location product block of the given location subscription.

    The concrete subscription model is resolved through the subscription model registry,
    because the abstract Optical Location model cannot load a subscription: its root
    block type never matches the concrete product block stored in the database.

    Args:
        location_id: Subscription id of an active Optical Location subscription.

    Returns:
        The Optical Location product block of the subscription.

    Raises:
        ValueError: If the subscription is not an Optical Location subscription.
    """
    location_subscription = subscription_from_subscription(AbstractOpticalLocationInactive, location_id)
    return location_subscription.optical_location
