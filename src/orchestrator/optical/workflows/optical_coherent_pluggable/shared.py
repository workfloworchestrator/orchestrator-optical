"""Shared helper functions and selectors for Optical Coherent Pluggable workflows."""

from typing import cast

from pydantic_forms.validators import Choice

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_types.optical_coherent_pluggable import OpticalCoherentPluggable
from orchestrator.optical.workflows.shared import subscriptions_by_product_type


def optical_coherent_pluggable_selector(
    status: list[SubscriptionLifecycle] | None = None,
    prompt: str = "",
) -> type[Choice]:
    """Create a Choice selector for active Optical Coherent Pluggable subscriptions.

    Note:
        Currently unused by any workflow; kept for future use.

    Args:
        status: List of lifecycle states to filter by. Defaults to ACTIVE and PROVISIONING.
        prompt: Display prompt for the selector.

    Returns:
        type[Choice]: A Choice class configured with pluggable subscription options.
    """
    if status is None:
        status = [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING]

    subscriptions = subscriptions_by_product_type(OpticalCoherentPluggable.__name__, status)
    products = {str(sub.subscription_id): sub.description for sub in sorted(subscriptions, key=lambda x: x.description)}

    if not prompt:
        prompt = "Select an Optical Coherent Pluggable"

    dynamic_class = Choice(prompt, zip(products.keys(), products.items(), strict=False))
    return cast(type[Choice], dynamic_class)
