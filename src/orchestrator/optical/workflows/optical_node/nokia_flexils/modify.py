"""Modify Nokia FlexILS Optical Node workflow.

This module ships the ready-to-use ``modify_optical_node_nokia_flexils``
workflow for the shipped Nokia FlexILS product type, together with the
importable parts: the FormPages of the modify form (as the
:func:`modify_optical_node_nokia_flexils_form_pages` page sequence, prefilled
with the current subscription values) and the step list that updates and
persists the Nokia FlexILS node block found in the state under
``OPTICAL_NODE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages::

    user_input_dict = yield from modify_optical_node_nokia_flexils_form_pages(
        subscription, block_field_name="router"
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from typing import Annotated, Any, cast

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import OpticalNodeNokiaFlexIls
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    load_optical_node_block,
    modify_optical_node_management_form,
    optical_node_block_from_state,
    save_optical_node_block,
    update_optical_node_block_fields,
    validate_gmpls_id_uniqueness,
    validate_optical_flexils_target_id_uniqueness,
)
from orchestrator.optical.workflows.shared import modify_summary_form

Instruction = Annotated[
    str,
    Field(
        "Modify the fields you want to change. Unchanged fields will remain intact.",
        title="Instruction",
        json_schema_extra={"disabled": True},
    ),
]


def modify_optical_node_nokia_flexils_vendor_form(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_node",
) -> type[FormPage]:
    """Return the vendor FormPage of the Nokia FlexILS Optical Node modify form.

    The page collects the FlexILS-specific fields of the node: the GMPLS ID and
    the Target Identifier (TID). It is prefilled with the current values of the
    subscription, so unchanged fields remain intact, and validates that neither
    the GMPLS ID nor the Target Identifier is already in use by another Nokia
    FlexILS subscription, excluding the subscription being modified.

    Args:
        subscription: The ACTIVE subscription model of the Nokia FlexILS
            Optical Node product being modified (any consumer model that has-a
            the shipped block works).
        block_field_name: Name of the attribute of the subscription model
            holding the Nokia FlexILS node block.

    Returns:
        The vendor FormPage of the shipped modify form.
    """
    node = getattr(subscription, block_field_name)

    class ModifyNokiaFlexIlsVendorForm(FormPage):
        instruction: Instruction
        optical_flexils_gmpls_id: Annotated[
            IPAddress,
            Field(title="GMPLS ID of the FlexILS node."),
        ] = node.optical_flexils_gmpls_id
        optical_flexils_target_id: Annotated[
            str,
            Field(title="Target Identifier (TID) of this FlexILS node (unique NENAME in the GMPLS network)."),
        ] = node.optical_flexils_target_id

        @model_validator(mode="after")
        def validate_form(self) -> "ModifyNokiaFlexIlsVendorForm":
            """Raise if the GMPLS ID or the Target Identifier is already in use by another subscription."""
            validate_gmpls_id_uniqueness(
                self.optical_flexils_gmpls_id,
                exclude_subscription_id=str(subscription.subscription_id),
            )
            validate_optical_flexils_target_id_uniqueness(
                self.optical_flexils_target_id,
                exclude_subscription_id=str(subscription.subscription_id),
            )
            return self

    return ModifyNokiaFlexIlsVendorForm


def modify_optical_node_nokia_flexils_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_node",
) -> FormGenerator:
    """Yield the FormPage of the Nokia FlexILS Optical Node modify form.

    This is the shipped modify form as a page sequence: it yields the shared
    management page and the FlexILS vendor page, and returns the collected user
    input as a flat dict of the ``optical_*`` state keys, consumed by the
    shipped steps of :data:`MODIFY_NOKIA_FLEXILS_BLOCK_STEPS`. Consumers yield
    from it in one line inside their own modify form generator, optionally
    interleaving their own pages. The customer of the subscription is collected
    separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        subscription: The ACTIVE subscription model of the Nokia FlexILS
            Optical Node product being modified (any consumer model that has-a
            the shipped block works).
        block_field_name: Name of the attribute of the subscription model
            holding the Nokia FlexILS node block.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict: dict[str, object] = {}
    user_input_dict.update((yield modify_optical_node_management_form(subscription, block_field_name)).model_dump())
    user_input_dict.update(
        (yield modify_optical_node_nokia_flexils_vendor_form(subscription, block_field_name)).model_dump()
    )
    return user_input_dict


def modify_optical_node_nokia_flexils_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalNodeNokiaFlexIls,
    block_field_name: str = "optical_node",
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia FlexILS Optical Node subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the shipped
    page sequence (:func:`modify_optical_node_nokia_flexils_form_pages`) and
    the summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Nokia
            FlexILS Optical Node product. Consumers that compose the shipped
            block under a different attribute name pass their own model class
            here.
        block_field_name: Name of the attribute of the subscription model
            holding the Nokia FlexILS node block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    node = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=str(subscription.customer_id))
    user_input_dict.update((yield from modify_optical_node_nokia_flexils_form_pages(subscription, block_field_name)))

    summary_fields = [
        "customer_id",
        "optical_module_node_fqdn",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
        "optical_flexils_gmpls_id",
        "optical_flexils_target_id",
    ]
    yield from modify_summary_form(
        user_input_dict,
        node.management,
        summary_fields,
        extra_before={
            "customer_id": str(subscription.customer_id),
            "optical_flexils_gmpls_id": str(node.optical_flexils_gmpls_id) if node.optical_flexils_gmpls_id else "",
            "optical_flexils_target_id": str(node.optical_flexils_target_id) if node.optical_flexils_target_id else "",
        },
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Nokia FlexILS node block")
def update_optical_node_nokia_flexils_block(
    optical_node_block: NokiaFlexIlsBlockProvisioning | dict[str, Any] | None,
    optical_module_node_fqdn: Fqdn,
    optical_flexils_target_id: str,
    optical_flexils_gmpls_id: IPAddress,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Update the Nokia FlexILS node block in the state from the modify-form keys.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from the database by its ``subscription_instance_id``
    before it is updated. The common fields are updated through
    :func:`orchestrator.optical.workflows.optical_node.shared.update_optical_node_block_fields`
    and the FlexILS-specific fields are set directly.

    Args:
        optical_node_block: The Nokia FlexILS node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_flexils_target_id: Target Identifier (TID) of the node.
        optical_flexils_gmpls_id: GMPLS ID of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.

    Raises:
        ValueError: If there is no Nokia FlexILS node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    """
    node_block = optical_node_block_from_state(optical_node_block)
    update_optical_node_block_fields(
        node_block,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
    )
    flexils_block = cast(NokiaFlexIlsBlockProvisioning, node_block)
    flexils_block.optical_flexils_gmpls_id = optical_flexils_gmpls_id
    flexils_block.optical_flexils_target_id = optical_flexils_target_id

    return {OPTICAL_NODE_BLOCK_STATE_KEY: node_block}


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
    "modify_optical_node_nokia_flexils_form_pages",
    "modify_optical_node_nokia_flexils_vendor_form",
    "update_optical_node_nokia_flexils_block",
]
