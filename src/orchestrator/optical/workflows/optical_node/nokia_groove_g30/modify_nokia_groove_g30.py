"""Modify Nokia Groove G30 Optical Node workflow.

This module ships the ready-to-use ``modify_optical_node_nokia_groove_g30``
workflow for the shipped Nokia Groove G30 product type, together with the
importable parts: the FormPages of the modify form (as the
:func:`modify_optical_node_nokia_groove_g30_form_pages` page sequence,
prefilled with the current block values) and the step list that updates
and persists the Nokia Groove G30 node block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages. The consumer extracts the
block with plain Python at any nesting depth (shipped code never traverses
the subscription)::

    block = subscription.optical_module_block  # or subscription.router.optical_module
    user_input_dict = yield from modify_optical_node_nokia_groove_g30_form_pages(
        block, exclude_subscription_id=...
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from typing import Any

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30Block,
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node.nokia_groove_g30 import (
    OpticalNodeNokiaGrooveG30Subscription,
)
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    load_optical_node_block,
    modify_optical_node_management_form,
    optical_node_block_from_state,
    update_optical_node_block_fields,
    update_optical_node_subscription_description,
    validate_optical_node_management_fields_uniqueness,
)
from orchestrator.optical.workflows.optical_node.shared.retrieve import retrieve_optical_node_role_and_software_version
from orchestrator.optical.workflows.shared import modify_summary_form


def modify_optical_node_nokia_groove_g30_form_pages(
    node: NokiaGrooveG30Block,
    *,
    exclude_subscription_id: UUIDstr | None = None,
) -> FormGenerator:
    """Yield the FormPage of the Nokia Groove G30 modify form.

    This is the shipped modify form as a page sequence: it yields the shared
    management page (prefilled with the current block values) and
    returns the collected user input as a flat dict of the ``optical_*`` state
    keys, consumed by the shipped steps of
    :data:`MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS`. Consumers yield from it in one
    line inside their own modify form generator, optionally interleaving their
    own pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        node: The Nokia Groove G30 node block being modified.
        exclude_subscription_id: Identifier of the subscription being modified,
            whose own node block is not a conflict. Defaults to the owner
            subscription of the block.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield modify_optical_node_management_form(node, exclude_subscription_id=exclude_subscription_id)
    return user_input.model_dump()


def modify_optical_node_nokia_groove_g30_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalNodeNokiaGrooveG30Subscription,
    block_field_name: str = "optical_node",
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia Groove G30 Optical Node subscription.

    The form is prefilled with the current values of the block, so
    unchanged fields remain intact. It is a thin composition of the shipped
    page sequence (:func:`modify_optical_node_nokia_groove_g30_form_pages`)
    and the summary form. Shipped-product only: consumers compose their own
    form generator from the shipped page sequence.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Nokia
            Groove G30 product.
        block_field_name: Name of the attribute of the subscription model holding
            the Nokia Groove G30 node block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    node = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=subscription.customer_id)
    user_input_dict.update(
        (
            yield from modify_optical_node_nokia_groove_g30_form_pages(
                node, exclude_subscription_id=str(subscription.subscription_id)
            )
        )
    )

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
        extra_before={"customer_id": subscription.customer_id},
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Nokia Groove G30 node block")
def update_optical_node_nokia_groove_g30_block(
    optical_module_block: NokiaGrooveG30BlockProvisioning | dict[str, Any] | None,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Update the Nokia Groove G30 node block in the state from the modify-form keys.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from the database by its ``subscription_instance_id``
    before it is updated. It re-checks the uniqueness of the FQDN and the DCN
    IPs at execution time, excluding the subscription being modified, so
    consumers bypassing the form validation are still guarded against duplicates.

    Args:
        optical_module_block: The Nokia Groove G30 node block
            in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the
            provisioning variant, while the subscription is being modified).
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.

    Raises:
        ValueError: If the FQDN or a DCN IP is already in use by another subscription.
    """
    node_block = optical_node_block_from_state(optical_module_block)
    exclude_subscription_id = str(node_block.owner_subscription_id)
    validate_optical_node_management_fields_uniqueness(
        optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
        exclude_subscription_id=exclude_subscription_id,
    )
    update_optical_node_block_fields(
        optical_module_block=node_block,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
    )
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: node_block}


#: Modify steps operating on the Nokia Groove G30 node block in the state. The
#: block is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS: StepList = (
    begin
    >> update_optical_node_nokia_groove_g30_block
    >> retrieve_optical_node_role_and_software_version
    >> save_optical_module_block
)


@modify_workflow(initial_input_form=modify_optical_node_nokia_groove_g30_form_generator)
def modify_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to modify an existing Nokia Groove G30 Optical Node subscription.

    The workflow is valid for the shipped :class:`OpticalNodeNokiaGrooveG30`
    product type only: it loads the block from the ``optical_node`` attribute
    of the shipped subscription models. The shipped description step refreshes
    the subscription description from the updated node FQDN. Consumers with
    their own product type compose their own modify workflow with the shipped
    parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_node_block
        >> MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS
        >> update_optical_node_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS",
    "modify_optical_node_nokia_groove_g30",
    "modify_optical_node_nokia_groove_g30_form_generator",
    "modify_optical_node_nokia_groove_g30_form_pages",
    "update_optical_node_nokia_groove_g30_block",
]
