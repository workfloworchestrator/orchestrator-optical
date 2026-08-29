"""Create Nokia FlexILS Optical Node workflow.

This module ships the ready-to-use ``create_optical_node_nokia_flexils``
workflow for the shipped Nokia FlexILS product type, together with the
importable parts: the FormPages of the create form (as the
:func:`create_optical_node_nokia_flexils_form_pages` page sequence), the
discovery step, the block population logic and the step list that operates on
the Nokia FlexILS node block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model, populates its block with the create-form values (the mandatory fields
of the PROVISIONING lifecycle) and transitions it to PROVISIONING, the shipped
block steps discover the node role and software version from the device and
persist the block found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``,
and the shipped description step finalizes the subscription. The shipped form
generator is a thin composition of the shipped pages and the summary form,
without hooks: consumers build their own form generator by yielding from the
shipped page sequence in one line and adding their own pages::

    user_input_dict = yield from create_optical_node_nokia_flexils_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import (
    OpticalNodeNokiaFlexIlsInactive,
    OpticalNodeNokiaFlexIlsProvisioning,
)
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    populate_abstract_optical_node_fields,
    save_optical_node_block,
    update_optical_node_subscription_description,
    validate_gmpls_id_uniqueness,
    validate_optical_flexils_target_id_uniqueness,
)
from orchestrator.optical.workflows.optical_node.shared.forms import (
    create_optical_node_location_form,
    create_optical_node_management_form,
)
from orchestrator.optical.workflows.optical_node.shared.retrieve import (
    retrieve_optical_node_role_and_software_version,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_optical_node_nokia_flexils_vendor_form(product_name: str) -> type[FormPage]:
    """Return the vendor FormPage of the Nokia FlexILS Optical Node create form.

    This is the FlexILS-specific page of the shipped create form: the GMPLS ID
    and the Target Identifier (TID) of the node. It is a building block for
    consumers that compose their own create form generator: the shipped page
    sequence (:func:`create_optical_node_nokia_flexils_form_pages`) yields it
    after the shared location and management pages. The page validates that
    the GMPLS ID and the Target Identifier are not already in use by another
    Nokia FlexILS subscription.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The vendor FormPage of the shipped create form.
    """

    class CreateNokiaFlexIlsVendorForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - FlexILS")

        optical_flexils_gmpls_id: Annotated[
            IPAddress,
            Field(title="GMPLS ID of the FlexILS node."),
        ]
        optical_flexils_target_id: Annotated[
            str,
            Field(title="Target Identifier (TID) of this FlexILS node (unique NENAME in the GMPLS network)."),
        ]

        @model_validator(mode="after")
        def validate_form(self) -> "CreateNokiaFlexIlsVendorForm":
            """Raise if the GMPLS ID or the Target Identifier is already in use by another subscription."""
            validate_gmpls_id_uniqueness(self.optical_flexils_gmpls_id)
            validate_optical_flexils_target_id_uniqueness(self.optical_flexils_target_id)
            return self

    return CreateNokiaFlexIlsVendorForm


def create_optical_node_nokia_flexils_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Nokia FlexILS Optical Node create form, in order.

    This is the shipped create form as a page sequence: it yields the shared
    location page and management page, then the FlexILS vendor page, and
    returns the collected user input as a flat dict of the ``optical_*`` state
    keys plus ``location_id``, consumed by the shipped construct step
    (:func:`construct_optical_node_nokia_flexils_subscription`). Consumers
    yield from it in one line inside their own create form generator,
    optionally interleaving their own pages. The customer of the subscription
    is collected separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict: dict[str, str | None] = {}
    user_input_dict.update((yield create_optical_node_location_form(product_name)).model_dump())
    user_input_dict.update((yield create_optical_node_management_form(product_name, require_dcn_ip=False)).model_dump())
    user_input_dict.update((yield create_optical_node_nokia_flexils_vendor_form(product_name)).model_dump())
    return user_input_dict


def create_optical_node_nokia_flexils_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating a Nokia FlexILS Optical Node.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step (:func:`construct_optical_node_nokia_flexils_subscription`).
    It is a thin composition of the shipped page sequence
    (:func:`create_optical_node_nokia_flexils_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_node_nokia_flexils_form_pages(product_name)))

    summary_fields = [
        "customer_id",
        "location_id",
        "optical_module_node_fqdn",
        "optical_flexils_target_id",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
        "optical_flexils_gmpls_id",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def populate_optical_node_nokia_flexils_block(
    optical_module_block: NokiaFlexIlsBlockInactive,
    *,
    location_id: UUIDstr,
    optical_module_node_fqdn: Fqdn,
    optical_flexils_gmpls_id: IPAddress,
    optical_flexils_target_id: str,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> None:
    """Populate a Nokia FlexILS node block from the create-form state keys.

    The node role and software version are not set here: the shared retrieval
    step (:func:`retrieve_optical_node_role_and_software_version`) writes them
    onto the block after the subscription is transitioned to PROVISIONING.
    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the PROVISIONING
    lifecycle.

    Args:
        optical_module_block: The Nokia FlexILS node block to populate (any lifecycle variant).
        location_id: Subscription id of the Optical Location hosting the node.
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_flexils_gmpls_id: GMPLS ID of the node.
        optical_flexils_target_id: Target Identifier (TID) of the node.
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
        optical_module_node_platform=Platform.FLEXILS,
    )
    optical_module_block.optical_flexils_gmpls_id = optical_flexils_gmpls_id
    optical_module_block.optical_flexils_target_id = optical_flexils_target_id


@step("Construct Subscription model")
def construct_optical_node_nokia_flexils_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    location_id: UUIDstr,
    optical_module_node_fqdn: Fqdn,
    optical_flexils_gmpls_id: IPAddress,
    optical_flexils_target_id: str,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Construct the PROVISIONING domain subscription model for a Nokia FlexILS Optical Node.

    This step builds the shipped ``OpticalNodeNokiaFlexIls`` model, populates
    its block with the create-form values through
    :func:`populate_optical_node_nokia_flexils_block` (the anti-corruption
    point) and transitions the subscription to PROVISIONING in memory, so the
    block found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` is the
    PROVISIONING variant with its mandatory fields already set — the contract
    of the shipped block steps of :data:`CREATE_NOKIA_FLEXILS_BLOCK_STEPS`
    (the node role and software version are still unset: the shared retrieval
    step discovers them from the device before the block is persisted).

    Consumers that define their own product type (composing the
    ``NokiaFlexIlsBlock`` under their own attribute name) write their own
    construct step instead: it builds their subscription, populates the
    composed block with the mandatory fields set (e.g. via
    :func:`populate_optical_node_nokia_flexils_block`), transitions it to
    PROVISIONING and puts the block in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    subscription = OpticalNodeNokiaFlexIlsInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    populate_optical_node_nokia_flexils_block(
        optical_module_block=subscription.optical_node,
        location_id=location_id,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
        optical_flexils_target_id=optical_flexils_target_id,
    )
    subscription = OpticalNodeNokiaFlexIlsProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_node,
    }


#: Create steps operating on the Nokia FlexILS node block in the state. Every
#: step is block-level: the shared retrieval step discovers the
#: ``optical_node_role`` and ``optical_module_node_software_version`` from the
#: device and writes them onto the block, and the last step persists the
#: block, because workflow steps execute with the state serialized between
#: steps (the block is re-hydrated from the database before every step operates
#: on it). The block is assumed to be in the PROVISIONING lifecycle status with
#: its mandatory fields already set: the caller's construct step provides it
#: (see :func:`construct_optical_node_nokia_flexils_subscription`). Consumers
#: with their own model run this list after constructing their subscription the
#: same way and putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_NOKIA_FLEXILS_BLOCK_STEPS: StepList = (
    begin >> retrieve_optical_node_role_and_software_version >> save_optical_node_block
)


@create_workflow(initial_input_form=create_optical_node_nokia_flexils_form_generator)
def create_optical_node_nokia_flexils() -> StepList:
    """Workflow to create a new Nokia FlexILS Optical Node subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalNodeNokiaFlexIls` model, populates its block
    with the create-form values and transitions it to PROVISIONING, the shipped
    block steps discover the node role and software version from the device
    and persist the block, and the shipped description step finalizes the
    subscription. It is therefore only valid for the shipped product type;
    consumers with their own product type compose their own create workflow
    with the same parts.
    """
    return (
        begin
        >> construct_optical_node_nokia_flexils_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_NOKIA_FLEXILS_BLOCK_STEPS
        >> update_optical_node_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_NOKIA_FLEXILS_BLOCK_STEPS",
    "create_optical_node_nokia_flexils",
    "create_optical_node_nokia_flexils_form_pages",
    "populate_optical_node_nokia_flexils_block",
]
