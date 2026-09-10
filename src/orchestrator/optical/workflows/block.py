"""Generic re-hydration and persistence of the shipped Optical Module blocks.

Every shipped block family travels in the workflow state under the single
``OPTICAL_MODULE_BLOCK_STATE_KEY`` and is persisted the same way: the block is
re-hydrated from its serialized state (workflow steps execute with the state
serialized between steps) and saved through the generic
:meth:`orchestrator.core.domain.base.ProductBlockModel.save`. Because the
concrete block class and its lifecycle variant are resolved through the product
block registry and the owner subscription status, the logic is family-agnostic
and lives here, shared by every ``*_BLOCK_STEPS`` list.
"""

from typing import Any, cast

from pydantic_forms.types import State

from orchestrator.core.db import SubscriptionInstanceTable, db
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.domain.lifecycle import lookup_specialized_type
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import step
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY


def optical_module_block_from_state(
    optical_module_block: ProductBlockModel | dict[str, Any] | None,
    *,
    block_description: str = "Optical Module",
) -> ProductBlockModel:
    """Return the shipped block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the full block data) rather than as a domain
    model. This helper returns the value unchanged when it is already a domain
    model (in-process usage, e.g. in tests) and reconstructs the block from the
    serialized data otherwise. The concrete block chain is resolved by its
    ``product_block_name`` and its lifecycle variant from the status of its
    owner subscription, so blocks of any family and lifecycle are loaded as
    their matching variant (INITIAL, PROVISIONING or ACTIVE).

    Args:
        optical_module_block: The block value from the workflow state, or None.
        block_description: Human-readable family name used in error messages.

    Returns:
        The shipped block as a domain model.

    Raises:
        ValueError: If there is no block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    if optical_module_block is None:
        msg = f"No {block_description} block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    if isinstance(optical_module_block, ProductBlockModel):
        return optical_module_block
    return rehydrate_optical_module_block(optical_module_block, block_description=block_description)


def rehydrate_optical_module_block(
    optical_module_block: dict[str, Any],
    *,
    block_description: str = "Optical Module",
) -> ProductBlockModel:
    """Reconstruct a shipped block from its serialized form.

    The state dict carries the full block data (the block is serialized with
    ``model_dump``), so the block is reconstructed from it rather than reloaded
    from the database: reloading would discard the mutations made by the
    preceding step, which workflow steps only persist when they explicitly save.
    The concrete block class is resolved through the product block registry and
    its lifecycle variant from the status of its owner subscription, mirroring
    the block-based resolution in ``orchestrator.optical.db``.

    Args:
        optical_module_block: The serialized block from the workflow state.
        block_description: Human-readable family name used in error messages.

    Returns:
        The shipped block as a domain model.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``,
            or if no subscription instance exists with the given id.
    """
    subscription_instance_id = optical_module_block.get("subscription_instance_id")
    if subscription_instance_id is None:
        msg = f"{block_description} block in the state has no subscription_instance_id"
        raise ValueError(msg)
    instance = db.session.get(SubscriptionInstanceTable, subscription_instance_id)
    if instance is None:
        msg = f"No subscription instance with id {subscription_instance_id}"
        raise ValueError(msg)
    block_class = cast(
        type[ProductBlockModel],
        lookup_specialized_type(
            ProductBlockModel.registry[instance.product_block.name],
            SubscriptionLifecycle(instance.subscription.status),
        ),
    )
    return block_class.model_validate(optical_module_block)


@step("Persist optical module block")
def save_optical_module_block(
    subscription: SubscriptionModel,
    optical_module_block: ProductBlockModel | dict[str, Any],
) -> State:
    """Persist the shipped block found in the state to the database.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from its serialized form (see
    :func:`optical_module_block_from_state`) before it is saved. This step saves
    the block tree of the loaded subscription (any consumer subscription model
    that has-a the block works) and returns the block, so it can be composed by
    any consumer workflow. The shipped block steps always operate on the
    PROVISIONING variant: their callers provide the block with the mandatory
    fields set and the owner subscription in the PROVISIONING status.

    Args:
        subscription: The subscription owning the block.
        optical_module_block: The shipped block to persist.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If there is no block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_module_block_from_state(optical_module_block)
    block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


__all__ = [
    "optical_module_block_from_state",
    "rehydrate_optical_module_block",
    "save_optical_module_block",
]
