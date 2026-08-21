"""Modify Nokia FlexILS Optical Node workflow.

This module ships the ready-to-use ``modify_optical_node_nokia_flexils``
workflow for the shipped Nokia FlexILS product type, together with the
importable parts: the form generator (parameterized by the subscription model
and the attribute name of the composed block) and the step list that updates
and persists the Nokia FlexILS node block found in the state under
``OPTICAL_NODE_BLOCK_STATE_KEY``. Consumers that keep the shipped product type
register the shipped workflow; consumers with their own model that has-a the
shipped block compose their own ``@modify_workflow`` with the parts.
"""

from collections.abc import Sequence
from typing import Annotated, Any

from pydantic import Field
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import OpticalNodeNokiaFlexIls
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    load_optical_node_block,
    optical_node_modify_input_form,
    save_optical_node_block,
    update_optical_node_block_fields,
    validate_gmpls_id_uniqueness,
)


def validate_flexils_fields(form: Any, subscription_id: UUIDstr) -> None:
    """Validate the FlexILS-specific form fields."""
    validate_gmpls_id_uniqueness(form.optical_flexils_gmpls_id, exclude_subscription_id=subscription_id)


def modify_optical_node_nokia_flexils_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalNodeNokiaFlexIls,
    block_field_name: str = "optical_node",
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia FlexILS Optical Node.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical Node product.
            Defaults to the shipped :class:`OpticalNodeNokiaFlexIls`; consumers that compose
            the shipped block under a different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Nokia FlexILS node block. Consumers that compose the shipped block
            under a different attribute name pass their own attribute name here.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    yield from optical_node_modify_input_form(
        subscription_id,
        subscription_model=subscription_model,
        block_field_name=block_field_name,
        extra_fields={
            "optical_flexils_gmpls_id": (
                Annotated[IPAddress, Field(title="GMPLS ID of the FlexILS node.")],
                "optical_flexils_gmpls_id",
            ),
            "optical_flexils_target_id": (
                Annotated[
                    str,
                    Field(title="Target Identifier (TID) of this FlexILS node (unique NENAME in the GMPLS network)."),
                ],
                "optical_flexils_target_id",
            ),
        },
        validate_extra=validate_flexils_fields,
        extra_form_pages=extra_form_pages,
        extra_summary_fields=extra_summary_fields,
    )


@step("Updating Nokia FlexILS node block")
def update_optical_node_nokia_flexils_block(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    location_id: UUIDstr,
    pqdn: Pqdn,
    optical_flexils_target_id: str,
    optical_flexils_gmpls_id: IPAddress,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
) -> State:
    """Update the Nokia FlexILS node block in the state from the modify-form keys.

    Args:
        optical_node_block: The Nokia FlexILS node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        location_id: Subscription id of the Optical Location hosting the node.
        pqdn: PQDN of the node.
        optical_flexils_target_id: Target Identifier (TID) of the node.
        optical_flexils_gmpls_id: GMPLS ID of the node.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
    """
    update_optical_node_block_fields(
        optical_node_block=optical_node_block,
        location_id=location_id,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
    )
    optical_node_block.optical_flexils_gmpls_id = optical_flexils_gmpls_id
    optical_node_block.optical_flexils_target_id = optical_flexils_target_id

    return {OPTICAL_NODE_BLOCK_STATE_KEY: optical_node_block}


#: Modify steps operating on the Nokia FlexILS node block in the state. The
#: block is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_NOKIA_FLEXILS_BLOCK_STEPS: StepList = begin >> update_optical_node_nokia_flexils_block >> save_optical_node_block


@modify_workflow(initial_input_form=modify_optical_node_nokia_flexils_form_generator)
def modify_optical_node_nokia_flexils() -> StepList:
    """Workflow to modify an existing Nokia FlexILS Optical Node subscription.

    The workflow is valid for the shipped :class:`OpticalNodeNokiaFlexIls`
    product type only: it loads the block from the ``optical_node`` attribute
    of the shipped subscription models. Consumers with their own product type
    compose their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_node_block
        >> MODIFY_NOKIA_FLEXILS_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_NOKIA_FLEXILS_BLOCK_STEPS",
    "modify_optical_node_nokia_flexils",
    "modify_optical_node_nokia_flexils_form_generator",
    "update_optical_node_nokia_flexils_block",
    "validate_flexils_fields",
]
