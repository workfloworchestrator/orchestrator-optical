"""Validate Optical Module Location workflow.

This module ships the ready-to-use ``validate_optical_module_location``
workflow for the shipped Optical Module Location product type, together
with the importable parts: the state loading step and the block validation
step. Consumers with their own model that has-a the shipped block declaretheir own ``@validate_workflow`` with
:data:`OPTICAL_MODULE_LOCATION_VALIDATE_STEPS`; consumer models that compose
the block under a different attribute name can put the block in the state
under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the validation step.
"""

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
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


def validate_optical_module_location_block(
    optical_module_block: OpticalModuleLocationBlockInactive,
) -> None:
    """Verify the state and integrity of an Optical Module Location block.

    This is the block-level validation of the family: it operates only on the
    block and is the anti-corruption point for consumers that keep their own
    model. It raises when the block is not fully provisioned (any of the
    required fields is unset) and logs the validated block.

    Args:
        optical_module_block: The Optical Module Location block to validate.

    Raises:
        ValueError: If the location block is not fully provisioned.
    """
    if (
        optical_module_block.longitude is None
        or optical_module_block.latitude is None
        or optical_module_block.location_code is None
    ):
        msg = "Optical Module Location block is not fully provisioned"
        raise ValueError(msg)
    logger.info(
        "Validating Optical Module Location",
        location_code=optical_module_block.location_code,
        location_name=optical_module_block.location_name,
        longitude=optical_module_block.longitude,
        latitude=optical_module_block.latitude,
    )


@step("Validate Optical Module Location state")
def validate_optical_module_location_block_step(
    subscription: SubscriptionModel,
    optical_module_block: OpticalModuleLocationBlockProvisioning | None = None,
) -> State:
    """Validate the Optical Module Location block loaded for the subscription.

    The block is read from the ``optical_module_block`` state key
    when present (e.g. when the shipped block steps ran against a
    consumer-owned block); otherwise it falls back to the
    ``optical_location`` attribute of the shipped subscription models. The
    block-level validation is delegated to
    :func:`validate_optical_module_location_block`.

    Args:
        subscription: The Optical Module Location subscription being validated.
        optical_module_block: The Optical Module Location block
            of the subscription, when it is available in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If the subscription has no Optical Module Location block
            under the ``optical_location`` attribute and no block was passed,
            or if the location block is not fully provisioned.
    """
    location = optical_location_block_from_state(optical_module_block) if optical_module_block is not None else None
    location = location or _optical_module_location_block_of_subscription(subscription)
    validate_optical_module_location_block(location)
    return {}


#: Validation steps of the Optical Module Location family. The block is
#: validated from the state; the subscription description refresh is a
#: shipped-type-only step exported separately (see
#: ``shared.optical_module_location_subscription_description``).
OPTICAL_MODULE_LOCATION_VALIDATE_STEPS: StepList = (
    begin >> load_initial_state_optical_module_location >> validate_optical_module_location_block_step
)


@validate_workflow()
def validate_optical_module_location() -> StepList:
    """Workflow to validate an Optical Module Location subscription."""
    return begin >> OPTICAL_MODULE_LOCATION_VALIDATE_STEPS


__all__ = [
    "OPTICAL_MODULE_LOCATION_VALIDATE_STEPS",
    "validate_optical_module_location",
    "validate_optical_module_location_block",
]
