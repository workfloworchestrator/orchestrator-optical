"""Create Nokia GX G42 Optical Node workflow.

This module ships the ready-to-use ``create_optical_node_nokia_gx_g42``
workflow for the shipped Nokia GX G42 product type, together with the
importable parts: the FormPages of the create form (as the
:func:`create_optical_node_nokia_gx_g42_form_pages` page sequence), the
discovery step, the block population logic and the step list that operates on
the Nokia GX G42 node block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model and puts its block in the state, the shipped block steps read the
software version from the device, populate and persist the block, and the
shipped description step finalizes the subscription. The shipped form
generator is a thin composition of the shipped pages and the summary form,
without hooks: consumers build their own form generator by yielding from the
shipped page sequence in one line and adding their own pages::

    user_input_dict = yield from create_optical_node_nokia_gx_g42_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Any, cast

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockInactive
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_types.optical_node.nokia_gx_g42 import OpticalNodeNokiaGxG42Inactive
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    optical_node_block_from_state,
    populate_abstract_optical_node_fields,
    save_optical_node_block,
    update_optical_node_subscription_description,
)
from orchestrator.optical.workflows.optical_node.shared.forms import (
    create_optical_node_location_form,
    create_optical_node_management_form,
)
from orchestrator.optical.workflows.optical_node.shared.retrieve import (
    retrieve_optical_node_role_and_software_version,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_optical_node_nokia_gx_g42_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Nokia GX G42 create form, in order.

    This is the shipped create form as a page sequence: it yields the location
    page and the management page (shared with the other Optical Node vendors),
    and returns the collected user input as a flat dict of the ``optical_*``
    state keys plus ``location_id``, consumed by the shipped steps of
    :data:`CREATE_NOKIA_GX_G42_BLOCK_STEPS`. Consumers yield from it in one
    line inside their own create form generator, optionally interleaving their
    own pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict: dict[str, str | None] = {}
    user_input_dict.update((yield create_optical_node_location_form(product_name)).model_dump())
    user_input_dict.update((yield create_optical_node_management_form(product_name)).model_dump())
    return user_input_dict


def create_optical_node_nokia_gx_g42_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating a Nokia GX G42 Optical Node.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_NOKIA_GX_G42_BLOCK_STEPS`. It is a thin composition
    of the shipped page sequence
    (:func:`create_optical_node_nokia_gx_g42_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_node_nokia_gx_g42_form_pages(product_name)))

    summary_fields = [
        "customer_id",
        "location_id",
        "optical_module_node_fqdn",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def populate_optical_node_nokia_gx_g42_block(
    optical_module_block: NokiaGxG42BlockInactive,
    *,
    location_id: UUIDstr,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> None:
    """Populate a Nokia GX G42 node block from the create-form state keys.

    The node role and software version are not set here: the shared retrieval
    step (:func:`retrieve_optical_node_role_and_software_version`) writes them
    onto the block after this function runs. This is the internal
    implementation of the populate step of
    :data:`CREATE_NOKIA_GX_G42_BLOCK_STEPS`.

    Args:
        optical_module_block: The Nokia GX G42 node block to populate (any lifecycle variant).
        location_id: Subscription id of the Optical Location hosting the node.
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.
    """
    populate_abstract_optical_node_fields(
        optical_module_block=optical_module_block,
        location_id=location_id,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
        optical_module_node_vendor=Vendor.NOKIA,
        optical_module_node_platform=Platform.GX_G42,
    )


@step("Populate Nokia GX G42 node block")
def populate_optical_node_nokia_gx_g42_block_step(
    optical_module_block: AbstractOpticalNodeBlockInactive | dict[str, Any] | None,
    location_id: UUIDstr,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Populate the Nokia GX G42 node block found in the state from the create-form keys.

    The node role and software version are written to the block by the shared
    retrieval step that runs after this one. Workflow steps execute with the
    state serialized between steps, so the block is re-hydrated from its
    serialized form before it is populated.

    Args:
        optical_module_block: The Nokia GX G42 node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
        location_id: Subscription id of the Optical Location hosting the node.
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.

    Raises:
        ValueError: If there is no Nokia GX G42 node block in the state.
    """
    node_block = optical_node_block_from_state(optical_module_block)
    populate_optical_node_nokia_gx_g42_block(
        optical_module_block=cast(NokiaGxG42BlockInactive, node_block),
        location_id=location_id,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
    )
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: node_block}


@step("Construct Subscription model")
def construct_optical_node_nokia_gx_g42_subscription(product: UUIDstr, customer_id: UUIDstr) -> State:
    """Construct the initial domain subscription model for a Nokia GX G42 Optical Node.

    This step builds the shipped ``OpticalNodeNokiaGxG42`` subscription model
    and puts its node block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``
    for the shipped block steps of :data:`CREATE_NOKIA_GX_G42_BLOCK_STEPS`.
    Consumers that define their own product type (composing the
    ``NokiaGxG42Block`` under their own attribute name) write their own
    construct step instead: it builds their (inactive) subscription, puts their
    composed block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``, and then
    runs :data:`CREATE_NOKIA_GX_G42_BLOCK_STEPS`.
    """
    subscription = OpticalNodeNokiaGxG42Inactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_node,
    }


#: Create steps operating on the Nokia GX G42 node block in the state. Every
#: step is block-level: the populate step writes the connection data and the
#: remaining create-form fields onto the block, the shared retrieval step
#: writes the node role and the discovered ``optical_module_node_software_version``
#: onto it, and the last step persists the block, because workflow steps execute
#: with the state serialized between steps (the block is re-hydrated from the
#: database before every step operates on it). Consumers with their own model
#: run this list after constructing their (inactive) subscription and putting
#: their block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_NOKIA_GX_G42_BLOCK_STEPS: StepList = (
    begin
    >> populate_optical_node_nokia_gx_g42_block_step
    >> retrieve_optical_node_role_and_software_version
    >> save_optical_node_block
)


@create_workflow(initial_input_form=create_optical_node_nokia_gx_g42_form_generator)
def create_optical_node_nokia_gx_g42() -> StepList:
    """Workflow to create a new Nokia GX G42 Optical Node subscription.

    The workflow is composed from the shipped parts: the construct step
    builds the shipped :class:`OpticalNodeNokiaGxG42` model and puts its
    block in the state, the shipped block steps read the software version
    from the device, populate and persist the block, and the shipped
    description step finalizes the subscription. It is therefore only valid
    for the shipped product type; consumers with their own product type
    compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_optical_node_nokia_gx_g42_subscription
        >> CREATE_NOKIA_GX_G42_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_optical_node_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_NOKIA_GX_G42_BLOCK_STEPS",
    "create_optical_node_nokia_gx_g42",
    "create_optical_node_nokia_gx_g42_form_pages",
]
