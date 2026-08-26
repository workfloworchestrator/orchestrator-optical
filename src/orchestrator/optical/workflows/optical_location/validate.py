"""Validate Optical Module Location workflow.

This module ships the ready-to-use ``validate_optical_module_location``
workflow for the shipped Optical Module Location product type, together
with the importable parts: the state loading step and the block validation
step. Consumers with their own model that has-a the shipped block declare
their own ``@validate_workflow`` with
:data:`OPTICAL_MODULE_LOCATION_VALIDATE_STEPS`; consumer models that compose
the block under a different attribute name can put the block in the state
under ``OPTICAL_LOCATION_BLOCK_STATE_KEY`` for the validation step.
"""

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockInactive
from orchestrator.optical.workflows.optical_location.shared import (
    _optical_module_location_block_of_subscription,
    optical_location_block_from_state,
)

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_optical_module_location(subscription: SubscriptionModel) -> State:
    """Load the subscription state for validation.

    The subscription model is loaded from the database on every step, so the
    pydantic model validation itself happens here.

    Args:
        subscription: The Optical Module Location subscription being validated.
    """
    return {"subscription": subscription}


@step("Validate Optical Module Location state")
def validate_optical_module_location_state(
    subscription: SubscriptionModel,
    optical_module_location_block: OpticalModuleLocationBlockInactive | None = None,
) -> State:
    """Verify the state and integrity of the Optical Module Location block.

    The block is read from the ``optical_module_location_block`` state key
    when present (e.g. when the shipped block steps ran against a
    consumer-owned block); otherwise it falls back to the
    ``optical_location`` attribute of the shipped subscription models.

    Args:
        subscription: The Optical Module Location subscription being validated.
        optical_module_location_block: The Optical Module Location block
            of the subscription, when it is available in the state under
            ``OPTICAL_LOCATION_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If the subscription has no Optical Module Location block
            under the ``optical_location`` attribute and no block was passed,
            or if the location block is not fully provisioned.
    """
    location = (
        optical_location_block_from_state(optical_module_location_block)
        if optical_module_location_block is not None
        else None
    )
    location = location or _optical_module_location_block_of_subscription(subscription)
    if location.longitude is None or location.latitude is None or location.location_code is None:
        msg = "Optical Module Location block is not fully provisioned"
        raise ValueError(msg)
    logger.info(
        "Validating Optical Module Location",
        location_code=location.location_code,
        location_name=location.location_name,
        longitude=location.longitude,
        latitude=location.latitude,
    )
    return {}


#: Validation steps of the Optical Module Location family. The block is
#: validated from the state; the subscription description refresh is a
#: shipped-type-only step exported separately (see
#: ``shared.optical_module_location_subscription_description``).
OPTICAL_MODULE_LOCATION_VALIDATE_STEPS: StepList = (
    begin >> load_initial_state_optical_module_location >> validate_optical_module_location_state
)


@validate_workflow()
def validate_optical_module_location() -> StepList:
    """Workflow to validate an Optical Module Location subscription."""
    return begin >> OPTICAL_MODULE_LOCATION_VALIDATE_STEPS


__all__ = [
    "OPTICAL_MODULE_LOCATION_VALIDATE_STEPS",
    "load_initial_state_optical_module_location",
    "validate_optical_module_location",
    "validate_optical_module_location_state",
]
