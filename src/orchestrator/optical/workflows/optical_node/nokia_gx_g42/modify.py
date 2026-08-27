"""Modify Nokia GX G42 Optical Node workflow.

This module ships the ready-to-use ``modify_optical_node_nokia_gx_g42``
workflow for the shipped Nokia GX G42 product type, together with the
importable parts: the FormPage of the modify form (as the
:func:`modify_optical_node_nokia_gx_g42_form_pages` page sequence, prefilled
with the current subscription values) and the step list that updates and
persists the Nokia GX G42 node block found in the state under
``OPTICAL_NODE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages::

    user_input_dict = yield from modify_optical_node_nokia_gx_g42_form_pages(
        subscription, block_field_name="router"
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from typing import Annotated, Any

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_types.optical_node.nokia_gx_g42 import OpticalNodeNokiaGxG42
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_form_pages
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    load_optical_node_block,
    optical_node_block_from_state,
    save_optical_node_block,
    update_optical_node_block_fields,
    validate_management_ips_uniqueness,
    validate_optical_node_fqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import modify_summary_form

Instruction = Annotated[
    str,
    Field(
        "Modify the node fields. Unchanged fields will remain intact.",
        title="Instruction",
        json_schema_extra={"disabled": True},
    ),
]


def modify_optical_node_nokia_gx_g42_form(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_node",
) -> type[FormPage]:
    """Return the modify FormPage of the Nokia GX G42 subscription.

    The page is prefilled with the current values of the subscription, so
    unchanged fields remain intact. The page requires at least one of the two
    DCN IPs and validates that the FQDN and the management IPs are not already
    in use by another Optical Node subscription, excluding the subscription
    being modified.

    Args:
        subscription: The ACTIVE subscription model of the Nokia GX G42
            Optical Node product being modified (any consumer model that has-a
            the shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Nokia GX G42 node block.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """
    node = getattr(subscription, block_field_name)

    class ModifyOpticalNodeNokiaGxG42Form(FormPage):
        instruction: Instruction
        optical_module_node_fqdn: Annotated[
            Fqdn,
            Field(title="FQDN of the Optical Node"),
        ] = node.management.optical_module_node_fqdn
        optical_module_node_dcn_loopback_ip: IPAddress | None = node.management.optical_module_node_dcn_loopback_ip
        optical_module_node_dcn_interface_ip: IPAddress | None = node.management.optical_module_node_dcn_interface_ip

        @model_validator(mode="after")
        def validate_form(self) -> "ModifyOpticalNodeNokiaGxG42Form":
            """Validate the management data and the uniqueness of the FQDN and the management IPs."""
            if not self.optical_module_node_dcn_loopback_ip and not self.optical_module_node_dcn_interface_ip:
                msg = "At least one of DCN loopback IP or DCN interface IP must be provided."
                raise ValueError(msg)
            validate_optical_node_fqdn_uniqueness(
                self.optical_module_node_fqdn, exclude_subscription_id=str(subscription.subscription_id)
            )
            validate_management_ips_uniqueness(
                [
                    ip
                    for ip in (self.optical_module_node_dcn_loopback_ip, self.optical_module_node_dcn_interface_ip)
                    if ip is not None
                ],
                exclude_subscription_id=str(subscription.subscription_id),
            )
            return self

    return ModifyOpticalNodeNokiaGxG42Form


def modify_optical_node_nokia_gx_g42_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_node",
) -> FormGenerator:
    """Yield the FormPage of the Nokia GX G42 modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page and returns the collected user input as a flat dict of the
    ``optical_*`` state keys, consumed by the shipped steps of
    :data:`MODIFY_NOKIA_GX_G42_BLOCK_STEPS`. Consumers yield from it in one
    line inside their own modify form generator, optionally interleaving their
    own pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_pages`).

    Args:
        subscription: The ACTIVE subscription model of the Nokia GX G42
            Optical Node product being modified (any consumer model that has-a
            the shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Nokia GX G42 node block.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield modify_optical_node_nokia_gx_g42_form(subscription, block_field_name)
    return user_input.model_dump()


def modify_optical_node_nokia_gx_g42_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalNodeNokiaGxG42,
    block_field_name: str = "optical_node",
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia GX G42 Optical Node.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the shipped
    page sequence (:func:`modify_optical_node_nokia_gx_g42_form_pages`) and the
    summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Nokia
            GX G42 Optical Node product. Consumers that compose the shipped
            block under a different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Nokia GX G42 node block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    node = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_pages(include=str(subscription.customer_id))
    user_input_dict.update((yield from modify_optical_node_nokia_gx_g42_form_pages(subscription, block_field_name)))

    summary_fields = [
        "customer_id",
        "optical_module_node_fqdn",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
    ]
    yield from modify_summary_form(
        user_input_dict,
        node.management,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Nokia GX G42 node block")
def update_optical_node_nokia_gx_g42_block(
    optical_node_block: NokiaGxG42BlockProvisioning | dict[str, Any] | None,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Update the Nokia GX G42 node block in the state from the modify-form keys.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from its serialized form before it is updated.

    Args:
        optical_node_block: The Nokia GX G42 node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.

    Raises:
        ValueError: If there is no Nokia GX G42 node block in the state.
    """
    node_block = optical_node_block_from_state(optical_node_block)
    if node_block is None:
        msg = "No Optical Node block in the state under OPTICAL_NODE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    update_optical_node_block_fields(
        optical_node_block=node_block,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
    )

    return {OPTICAL_NODE_BLOCK_STATE_KEY: node_block}


#: Modify steps operating on the Nokia GX G42 node block in the state.
#: The block is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_NOKIA_GX_G42_BLOCK_STEPS: StepList = begin >> update_optical_node_nokia_gx_g42_block >> save_optical_node_block


@modify_workflow(initial_input_form=modify_optical_node_nokia_gx_g42_form_generator)
def modify_optical_node_nokia_gx_g42() -> StepList:
    """Workflow to modify an existing Nokia GX G42 Optical Node subscription.

    The workflow is valid for the shipped :class:`OpticalNodeNokiaGxG42`
    product type only: it loads the block from the ``optical_node`` attribute
    of the shipped subscription models. Consumers with their own product type
    compose their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_node_block
        >> MODIFY_NOKIA_GX_G42_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_NOKIA_GX_G42_BLOCK_STEPS",
    "modify_optical_node_nokia_gx_g42",
    "modify_optical_node_nokia_gx_g42_form",
    "modify_optical_node_nokia_gx_g42_form_generator",
    "modify_optical_node_nokia_gx_g42_form_pages",
    "update_optical_node_nokia_gx_g42_block",
]
