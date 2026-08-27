"""Create Nokia Groove G30 Optical Node workflow.

This module ships the ready-to-use ``create_optical_node_nokia_groove_g30``
workflow for the shipped Nokia Groove G30 product type, together with the
importable parts: the FormPages of the create form (as the
:func:`create_optical_node_nokia_groove_g30_form_pages` page sequence), the
node discovery step, the block population logic and the step list that
operates on the Nokia Groove G30 node block found in the state under
``OPTICAL_NODE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model and puts its block in the state, the shipped block steps retrieve the
node software version from the device, populate and persist the block, and
the shipped description step finalizes the subscription. The shipped form
generator is a thin composition of the shipped pages and the summary form,
without hooks: consumers build their own form generator by yielding from the
shipped page sequence in one line and adding their own pages::

    user_input_dict = yield from create_optical_node_nokia_groove_g30_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Annotated, Any, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.hal.optical_node import retrieve_g30_software_version
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30BlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_types.optical_node.nokia_groove_g30 import (
    OpticalNodeNokiaGrooveG30Inactive,
)
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_location.shared import active_location_subscription_selector
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    optical_node_block_from_state,
    populate_abstract_optical_node_fields,
    save_optical_node_block,
    update_optical_node_subscription_description,
    validate_management_ips_uniqueness,
    validate_optical_node_fqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_optical_node_nokia_groove_g30_identity_form(
    product_name: str,
    customer_choice: type[Choice],
) -> type[FormPage]:
    """Return the identity FormPage of the Nokia Groove G30 create form.

    This is the first page of the shipped create form: the customer, the
    Optical Location hosting the node, the role of the node and its FQDN. It
    is a building block for consumers that compose their own create form
    generator: the shipped page sequence
    (:func:`create_optical_node_nokia_groove_g30_form_pages`) yields it first.
    The page validates that the FQDN is not already in use by another Optical
    Node subscription.

    Args:
        product_name: Name of the product being created, used as the page title.
        customer_choice: The ``Choice`` selector of the subscription customer,
            as built by :func:`orchestrator.optical.workflows.customer.customer_choice_selector`.

    Returns:
        The identity FormPage of the shipped create form.
    """

    class CreateOpticalNodeNokiaGrooveG30IdentityForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Identity")

        customer_id: customer_choice
        location_id: active_location_subscription_selector()
        optical_node_role: OpticalNodeRole = OpticalNodeRole.TRANSPONDER
        optical_module_node_fqdn: Annotated[
            Fqdn,
            Field(title="FQDN of the Optical Node"),
        ]

        @model_validator(mode="after")
        def validate_fqdn(self) -> "CreateOpticalNodeNokiaGrooveG30IdentityForm":
            """Raise if the FQDN is already in use by another subscription."""
            validate_optical_node_fqdn_uniqueness(self.optical_module_node_fqdn)
            return self

    return CreateOpticalNodeNokiaGrooveG30IdentityForm


def create_optical_node_nokia_groove_g30_management_form(product_name: str) -> type[FormPage]:
    """Return the management FormPage of the Nokia Groove G30 create form.

    This is the second page of the shipped create form: the DCN loopback and
    interface IPs through which the node can be reached. It is a building block
    for consumers that compose their own create form generator: the shipped
    page sequence (:func:`create_optical_node_nokia_groove_g30_form_pages`)
    yields it second. The page requires at least one DCN IP and validates that
    the DCN IPs are not already in use by another Optical Node subscription.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The management FormPage of the shipped create form.
    """

    class CreateOpticalNodeNokiaGrooveG30ManagementForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Management")

        optical_module_node_dcn_loopback_ip: IPAddress | None = None
        optical_module_node_dcn_interface_ip: IPAddress | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateOpticalNodeNokiaGrooveG30ManagementForm":
            """Raise if neither DCN IP is given or the IPs are already in use."""
            if not self.optical_module_node_dcn_loopback_ip and not self.optical_module_node_dcn_interface_ip:
                msg = "At least one of DCN loopback IP or DCN interface IP must be provided."
                raise ValueError(msg)
            validate_management_ips_uniqueness(
                [
                    ip
                    for ip in (self.optical_module_node_dcn_loopback_ip, self.optical_module_node_dcn_interface_ip)
                    if ip is not None
                ]
            )
            return self

    return CreateOpticalNodeNokiaGrooveG30ManagementForm


def create_optical_node_nokia_groove_g30_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Nokia Groove G30 create form, in order.

    This is the shipped create form as a page sequence: it yields the identity
    page and the management page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys plus ``customer_id``, consumed
    by the shipped steps of :data:`CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS`.
    Consumers yield from it in one line inside their own create form
    generator, optionally interleaving their own pages.

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    customer_choice = customer_choice_selector()

    user_input_dict: dict[str, str | None] = {}
    user_input_dict.update(
        (yield create_optical_node_nokia_groove_g30_identity_form(product_name, customer_choice)).model_dump()
    )
    user_input_dict.update((yield create_optical_node_nokia_groove_g30_management_form(product_name)).model_dump())
    return user_input_dict


def create_optical_node_nokia_groove_g30_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating a Nokia Groove G30 Optical Node.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS`. It is a thin
    composition of the shipped page sequence
    (:func:`create_optical_node_nokia_groove_g30_form_pages`) and the summary
    form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from create_optical_node_nokia_groove_g30_form_pages(product_name)

    summary_fields = [
        "customer_id",
        "location_id",
        "optical_node_role",
        "optical_module_node_fqdn",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Discover Nokia Groove G30 node properties")
def discover_optical_node_nokia_groove_g30(
    optical_node_block: AbstractOpticalNodeBlockInactive | dict[str, Any] | None,
    optical_node_role: OpticalNodeRole,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Connect to the node and write its role and software version to the block.

    The first block-level step of :data:`CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS`:
    it resolves the block from the state, writes the node role (from the
    create form) and the software version (retrieved from the device) onto it,
    which the shipped populate step then reads from the block.

    Raises:
        ValueError: If there is no Nokia Groove G30 node block in the state
            under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    """
    node_block = optical_node_block_from_state(optical_node_block)
    if node_block is None:
        msg = "No Optical Node block in the state under OPTICAL_NODE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    software_version = retrieve_g30_software_version(
        dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        dcn_interface_ip=optical_module_node_dcn_interface_ip,
    )
    node_block.optical_node_role = optical_node_role
    node_block.management.optical_module_node_software_version = software_version
    return {OPTICAL_NODE_BLOCK_STATE_KEY: node_block}


def populate_optical_node_nokia_groove_g30_block(
    optical_node_block: NokiaGrooveG30BlockInactive,
    *,
    location_id: UUIDstr,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> None:
    """Populate a Nokia Groove G30 node block from the create-form state keys.

    The node role and software version are not set here: the block-level
    discovery step (:func:`discover_optical_node_nokia_groove_g30`) writes them
    onto the block before this function runs. This is the internal
    implementation of the populate step of
    :data:`CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS`.

    Args:
        optical_node_block: The Nokia Groove G30 node block to populate (any lifecycle variant).
        location_id: Subscription id of the Optical Location hosting the node.
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.
    """
    populate_abstract_optical_node_fields(
        optical_node_block=optical_node_block,
        location_id=location_id,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
        optical_module_node_vendor=Vendor.NOKIA,
        optical_module_node_platform=Platform.GROOVE_G30,
    )


@step("Populate Nokia Groove G30 node block")
def populate_optical_node_nokia_groove_g30_block_step(
    optical_node_block: AbstractOpticalNodeBlockInactive | dict[str, Any] | None,
    location_id: UUIDstr,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
) -> State:
    """Populate the Nokia Groove G30 node block found in the state from the create-form keys.

    The node role and software version are read from the block, where the
    block-level discovery step wrote them. Workflow steps execute with the
    state serialized between steps, so the block is re-hydrated from the
    database by its ``subscription_instance_id`` before it is populated.

    Args:
        optical_node_block: The Nokia Groove G30 node block
            in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
        location_id: Subscription id of the Optical Location hosting the node.
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.
    """
    node_block = optical_node_block_from_state(optical_node_block)
    if node_block is None:
        msg = "No Optical Node block in the state under OPTICAL_NODE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    populate_optical_node_nokia_groove_g30_block(
        optical_node_block=cast(NokiaGrooveG30BlockInactive, node_block),
        location_id=location_id,
        optical_module_node_fqdn=optical_module_node_fqdn,
        optical_module_node_dcn_loopback_ip=optical_module_node_dcn_loopback_ip,
        optical_module_node_dcn_interface_ip=optical_module_node_dcn_interface_ip,
    )
    return {OPTICAL_NODE_BLOCK_STATE_KEY: node_block}


@step("Construct Subscription model")
def construct_optical_node_nokia_groove_g30_subscription(product: UUIDstr, customer_id: UUIDstr) -> State:
    """Construct the initial domain subscription model for a Nokia Groove G30 Optical Node.

    This step builds the shipped ``OpticalNodeNokiaGrooveG30`` subscription
    model and puts its node block in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``
    for the shipped block steps of :data:`CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS`.
    Consumers that define their own product type (composing the
    ``NokiaGrooveG30Block`` under their own attribute name) write their own
    construct step instead: it builds their (inactive) subscription, puts their
    composed block in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``, and then
    runs :data:`CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS`.
    """
    subscription = OpticalNodeNokiaGrooveG30Inactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_NODE_BLOCK_STATE_KEY: subscription.optical_node,
    }


#: Create steps operating on the Nokia Groove G30 node block in the state.
#: Every step is block-level: the device discovery step writes the node role
#: and the discovered ``optical_module_node_software_version`` onto the block,
#: the populate step writes the remaining create-form fields, and the last
#: step persists the block, because workflow steps execute with the state
#: serialized between steps (the block is re-hydrated from the database
#: before every step operates on it). Consumers with their own model run this
#: list after constructing their (inactive) subscription and putting their
#: block in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS: StepList = (
    begin
    >> discover_optical_node_nokia_groove_g30
    >> populate_optical_node_nokia_groove_g30_block_step
    >> save_optical_node_block
)


@create_workflow(initial_input_form=create_optical_node_nokia_groove_g30_form_generator)
def create_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to create a new Nokia Groove G30 Optical Node subscription.

    The workflow is composed from the shipped parts: the construct step
    builds the shipped :class:`OpticalNodeNokiaGrooveG30` model and puts its
    block in the state, the shipped block steps retrieve the node software
    version from the device, populate and persist the block, and the shipped
    description step finalizes the subscription. It is therefore only valid
    for the shipped product type; consumers with their own product type
    compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_optical_node_nokia_groove_g30_subscription
        >> CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_optical_node_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_NOKIA_GROOVE_G30_BLOCK_STEPS",
    "create_optical_node_nokia_groove_g30",
    "create_optical_node_nokia_groove_g30_form_pages",
]
