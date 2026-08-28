"""Validate Optical Coherent Pluggable workflow.

This module ships the ready-to-use ``validate_optical_coherent_pluggable``
workflow for the shipped Optical Coherent Pluggable product type, together
with the importable parts: the state loading step and the block validation
step. Consumers with their own model that has-a the shipped block declare
their own ``@validate_workflow`` with
:data:`OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS`; consumer models that compose
the block under a different attribute name can put the block in the state
under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` for the validation step.
"""

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlockInactive,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    _optical_coherent_pluggable_block_of_subscription,
    optical_coherent_pluggable_block_from_state,
)

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_optical_coherent_pluggable(subscription: SubscriptionModel) -> State:
    """Load the subscription state for validation."""
    return {"subscription": subscription}


@step("Validate Optical Coherent Pluggable state")
def validate_optical_coherent_pluggable_state(
    subscription: SubscriptionModel,
    optical_module_block: OpticalCoherentPluggableBlockInactive | None = None,
) -> State:
    """Verify the state and integrity of the Optical Coherent Pluggable block.

    The block is read from the ``optical_module_block`` state key
    when present (e.g. when the shipped block steps ran against a
    consumer-owned block); otherwise it falls back to the
    ``optical_coherent_pluggable`` attribute of the shipped subscription
    models. Workflow steps execute with the state serialized between steps, so
    a block found in the state is re-hydrated before it is validated.

    Args:
        subscription: The Optical Coherent Pluggable subscription being validated.
        optical_module_block: The Optical Coherent Pluggable block
            of the subscription, when it is available in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If the subscription has no Optical Coherent Pluggable block
            under the ``optical_coherent_pluggable`` attribute and no block was
            passed, or if the pluggable block is not fully provisioned.
    """
    pluggable = (
        optical_coherent_pluggable_block_from_state(optical_module_block) if optical_module_block is not None else None
    )
    pluggable = pluggable or _optical_coherent_pluggable_block_of_subscription(subscription)
    if pluggable.optical_port_name is None or pluggable.optical_port_host_node is None:
        msg = "Optical Coherent Pluggable block is not fully provisioned"
        raise ValueError(msg)
    logger.info(
        "Validating Optical Coherent Pluggable",
        port_name=pluggable.optical_port_name,
        host_node=pluggable.optical_port_host_node.management.optical_module_node_fqdn,
        firmware=pluggable.optical_coherent_pluggable_firmware_version,
    )
    return {}


#: Validation steps of the Optical Coherent Pluggable family. The block is
#: validated from the state; the subscription description refresh is a
#: shipped-type-only step exported separately (see
#: ``shared.update_optical_coherent_pluggable_subscription_description``).
OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS: StepList = (
    begin >> load_initial_state_optical_coherent_pluggable >> validate_optical_coherent_pluggable_state
)


@validate_workflow()
def validate_optical_coherent_pluggable() -> StepList:
    """Workflow to validate an Optical Coherent Pluggable subscription."""
    return begin >> OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS


__all__ = [
    "OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS",
    "load_initial_state_optical_coherent_pluggable",
    "validate_optical_coherent_pluggable",
    "validate_optical_coherent_pluggable_state",
]
