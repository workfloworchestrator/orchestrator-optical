"""Create Nokia FlexILS Optical Node workflow.

This module ships the ready-to-use ``create_optical_node_nokia_flexils``
workflow for the shipped Nokia FlexILS product type, together with the
importable parts: the form generator, the discovery step, the block population
logic and the step list that operates on the Nokia FlexILS node block found in
the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``. Consumers that keep the
shipped product type register the shipped workflow; consumers with their own
model that has-a the shipped block compose their own ``@create_workflow`` with
the parts.
"""

from collections.abc import Sequence
from typing import Annotated

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.hal.optical_node import discover_flexils_node
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import (
    OpticalNodeNokiaFlexIlsInactive,
    OpticalNodeNokiaFlexIlsProvisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_location.shared import active_location_subscription_selector
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    optical_node_subscription_description,
    populate_abstract_optical_node_fields,
    save_optical_node_block,
    validate_gmpls_id_uniqueness,
    validate_management_ips_uniqueness,
    validate_pqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_optical_node_nokia_flexils_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for creating a Nokia FlexILS Optical Node.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_NOKIA_FLEXILS_BLOCK_STEPS`.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    location_choice = active_location_subscription_selector()
    customer_choice = customer_choice_selector()

    class CreateNokiaFlexIlsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        location_id: location_choice
        pqdn: Annotated[
            Pqdn,
            Field(title="PQDN of the Optical Node. (e.g. if FQDN is `trx1.siteA.domain.com`, PQDN is `trx1.siteA`)"),
        ]
        optical_flexils_target_id: Annotated[
            str, Field(title="Target Identifier (TID) of this FlexILS node (unique NENAME in the GMPLS network).")
        ]
        optical_management_ip: IPAddress | None = None
        optical_loopback_ip: IPAddress | None = None
        optical_flexils_gmpls_id: IPAddress | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateNokiaFlexIlsForm":
            if not self.optical_management_ip and not self.optical_loopback_ip and not self.optical_flexils_gmpls_id:
                msg = "At least one of management IP or loopback IP or GMPLS ID must be provided."
                raise ValueError(msg)
            validate_pqdn_uniqueness(self.pqdn)
            validate_management_ips_uniqueness(
                [ip for ip in (self.optical_management_ip, self.optical_loopback_ip) if ip is not None]
            )
            if self.optical_flexils_gmpls_id is not None:
                validate_gmpls_id_uniqueness(self.optical_flexils_gmpls_id)
            return self

    user_input = yield CreateNokiaFlexIlsForm
    user_input_dict = user_input.model_dump()
    summary_fields = [
        "customer_id",
        "location_id",
        "pqdn",
        "optical_management_ip",
        "optical_loopback_ip",
        "optical_flexils_gmpls_id",
        "optical_flexils_target_id",
    ]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from create_summary_form(
        user_input_dict,
        product_name,
        summary_fields,
        extra_summary_fields=extra_summary_fields,
    )

    return user_input_dict


@step("Discover Nokia FlexILS node properties")
def discover_optical_node_nokia_flexils(
    location_id: UUIDstr,
    optical_flexils_target_id: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
) -> State:
    """Connect to the node and retrieve its role and software version.

    The step is block-free: it only adds the discovered ``optical_node_role``
    and ``optical_node_software_version`` keys to the state, which the shipped
    construct step and the shipped populate step consume.
    """
    role, software_version = discover_flexils_node(
        location_id=location_id,
        optical_flexils_target_id=optical_flexils_target_id,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
    )
    return {
        "optical_node_role": role,
        "optical_node_software_version": software_version,
    }


def populate_optical_node_nokia_flexils_block(
    optical_node_block: NokiaFlexIlsBlockInactive,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_node_software_version: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
    optical_flexils_target_id: str | None = None,
) -> None:
    """Populate a Nokia FlexILS node block from the create-form state keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle.

    Args:
        optical_node_block: The Nokia FlexILS node block to populate (any lifecycle variant).
        location_id: Subscription id of the Optical Location hosting the node.
        optical_node_role: Role of the node, as discovered from the device.
        pqdn: PQDN of the node.
        optical_node_software_version: Software version of the node, as discovered from the device.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
        optical_flexils_gmpls_id: GMPLS ID of the node.
        optical_flexils_target_id: Target Identifier (TID) of the node.
    """
    populate_abstract_optical_node_fields(
        optical_node_block=optical_node_block,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_node_software_version=optical_node_software_version,
    )
    optical_node_block.optical_flexils_gmpls_id = optical_flexils_gmpls_id
    optical_node_block.optical_flexils_target_id = optical_flexils_target_id


@step("Populate Nokia FlexILS node block")
def populate_optical_node_nokia_flexils_block_step(
    optical_node_block: NokiaFlexIlsBlockInactive,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_node_software_version: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
    optical_flexils_target_id: str | None = None,
) -> State:
    """Populate the Nokia FlexILS node block found in the state from the create-form keys.

    Args:
        optical_node_block: The Nokia FlexILS node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY``.
        location_id: Subscription id of the Optical Location hosting the node.
        optical_node_role: Role of the node, as discovered from the device.
        pqdn: PQDN of the node.
        optical_node_software_version: Software version of the node, as discovered from the device.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
        optical_flexils_gmpls_id: GMPLS ID of the node.
        optical_flexils_target_id: Target Identifier (TID) of the node.
    """
    populate_optical_node_nokia_flexils_block(
        optical_node_block=optical_node_block,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_node_software_version=optical_node_software_version,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
        optical_flexils_target_id=optical_flexils_target_id,
    )
    return {OPTICAL_NODE_BLOCK_STATE_KEY: optical_node_block}


@step("Construct Subscription model")
def construct_optical_node_nokia_flexils_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_flexils_target_id: str,
    optical_node_software_version: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
) -> State:
    """Construct the initial domain subscription model for a Nokia FlexILS Optical Node.

    This step builds the shipped ``OpticalNodeNokiaFlexIls`` subscription model
    and populates its node block. Consumers that define their own product type
    (composing the ``NokiaFlexIlsBlock`` under their own attribute name) write
    their own construct step instead and can reuse
    :func:`populate_optical_node_nokia_flexils_block` as the anti-corruption
    point between their model and the shipped block.
    """
    subscription = OpticalNodeNokiaFlexIlsInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    populate_optical_node_nokia_flexils_block(
        optical_node_block=subscription.optical_node,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_node_software_version=optical_node_software_version,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
        optical_flexils_target_id=optical_flexils_target_id,
    )

    subscription = OpticalNodeNokiaFlexIlsProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = optical_node_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


#: Create steps operating on the Nokia FlexILS node block in the state.
#: Consumers that keep the shipped product type do not need this list (the
#: shipped construct step populates the block itself); consumers with their own
#: model run it after constructing their (inactive) subscription and putting
#: their block in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
CREATE_NOKIA_FLEXILS_BLOCK_STEPS: StepList = (
    begin >> populate_optical_node_nokia_flexils_block_step >> save_optical_node_block
)


@create_workflow(initial_input_form=create_optical_node_nokia_flexils_form_generator)
def create_optical_node_nokia_flexils() -> StepList:
    """Workflow to create a new Nokia FlexILS Optical Node subscription.

    The workflow is valid for the shipped :class:`OpticalNodeNokiaFlexIls`
    product type only: the construct step builds the shipped subscription
    model. Consumers with their own product type compose their own create
    workflow with the shipped parts.
    """
    return (
        begin
        >> discover_optical_node_nokia_flexils
        >> construct_optical_node_nokia_flexils_subscription
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_NOKIA_FLEXILS_BLOCK_STEPS",
    "construct_optical_node_nokia_flexils_subscription",
    "create_optical_node_nokia_flexils",
    "create_optical_node_nokia_flexils_form_generator",
    "discover_optical_node_nokia_flexils",
    "populate_optical_node_nokia_flexils_block",
    "populate_optical_node_nokia_flexils_block_step",
]
