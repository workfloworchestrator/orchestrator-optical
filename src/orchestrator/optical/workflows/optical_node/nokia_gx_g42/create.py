"""Create Nokia GX G42 Optical Node workflow.

This module ships the ready-to-use ``create_optical_node_nokia_gx_g42``
workflow for the shipped Nokia GX G42 product type, together with the
importable parts: the form generator, the block population logic and the step
list that operates on the Nokia GX G42 node block found in the state under
``OPTICAL_NODE_BLOCK_STATE_KEY``. Consumers that keep the shipped product type
register the shipped workflow; consumers with their own model that has-a the
shipped block compose their own ``@create_workflow`` with the parts.
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
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockInactive
from orchestrator.optical.products.product_types.optical_node.nokia_gx_g42 import (
    OpticalNodeNokiaGxG42Inactive,
    OpticalNodeNokiaGxG42Provisioning,
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
    validate_pqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_optical_node_nokia_gx_g42_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for creating a Nokia GX G42 Optical Node.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_NOKIA_GX_G42_BLOCK_STEPS`.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    location_choice = active_location_subscription_selector()
    customer_choice = customer_choice_selector()

    class CreateNokiaGxG42Form(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        location_id: location_choice
        optical_node_role: OpticalNodeRole = OpticalNodeRole.TRANSPONDER
        pqdn: Annotated[
            Pqdn,
            Field(title="PQDN of the Optical Node. (e.g. if FQDN is `trx1.siteA.domain.com`, PQDN is `trx1.siteA`)"),
        ]
        optical_management_ip: IPAddress | None = None
        optical_loopback_ip: IPAddress | None = None
        optical_node_software_version: str | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateNokiaGxG42Form":
            validate_pqdn_uniqueness(self.pqdn)
            if not self.optical_management_ip and not self.optical_loopback_ip:
                msg = "At least one of management IP or loopback IP must be provided."
                raise ValueError(msg)
            return self

    user_input = yield CreateNokiaGxG42Form
    user_input_dict = user_input.model_dump()
    summary_fields = [
        "customer_id",
        "location_id",
        "optical_node_role",
        "pqdn",
        "optical_management_ip",
        "optical_loopback_ip",
        "optical_node_software_version",
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


def populate_optical_node_nokia_gx_g42_block(
    optical_node_block: NokiaGxG42BlockInactive,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_node_software_version: str | None = None,
) -> None:
    """Populate a Nokia GX G42 node block from the create-form state keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle.

    Args:
        optical_node_block: The Nokia GX G42 node block to populate (any lifecycle variant).
        location_id: Subscription id of the Optical Location hosting the node.
        optical_node_role: Role of the node.
        pqdn: PQDN of the node.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
        optical_node_software_version: Software version of the node.
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


@step("Populate Nokia GX G42 node block")
def populate_optical_node_nokia_gx_g42_block_step(
    optical_node_block: NokiaGxG42BlockInactive,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_node_software_version: str | None = None,
) -> State:
    """Populate the Nokia GX G42 node block found in the state from the create-form keys.

    Args:
        optical_node_block: The Nokia GX G42 node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY``.
        location_id: Subscription id of the Optical Location hosting the node.
        optical_node_role: Role of the node.
        pqdn: PQDN of the node.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
        optical_node_software_version: Software version of the node.
    """
    populate_optical_node_nokia_gx_g42_block(
        optical_node_block=optical_node_block,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_node_software_version=optical_node_software_version,
    )
    return {OPTICAL_NODE_BLOCK_STATE_KEY: optical_node_block}


@step("Construct Subscription model")
def construct_optical_node_nokia_gx_g42_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_node_software_version: str | None = None,
) -> State:
    """Construct the initial domain subscription model for a Nokia GX G42 Optical Node.

    This step builds the shipped ``OpticalNodeNokiaGxG42`` subscription model
    and populates its node block. Consumers that define their own product type
    (composing the ``NokiaGxG42Block`` under their own attribute name) write
    their own construct step instead and can reuse
    :func:`populate_optical_node_nokia_gx_g42_block` as the anti-corruption
    point between their model and the shipped block.
    """
    subscription = OpticalNodeNokiaGxG42Inactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    populate_optical_node_nokia_gx_g42_block(
        optical_node_block=subscription.optical_node,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_node_software_version=optical_node_software_version,
    )

    subscription = OpticalNodeNokiaGxG42Provisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = optical_node_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


#: Create steps operating on the Nokia GX G42 node block in the state.
#: Consumers that keep the shipped product type do not need this list (the
#: shipped construct step populates the block itself); consumers with their own
#: model run it after constructing their (inactive) subscription and putting
#: their block in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
CREATE_NOKIA_GX_G42_BLOCK_STEPS: StepList = (
    begin >> populate_optical_node_nokia_gx_g42_block_step >> save_optical_node_block
)


@create_workflow(initial_input_form=create_optical_node_nokia_gx_g42_form_generator)
def create_optical_node_nokia_gx_g42() -> StepList:
    """Workflow to create a new Nokia GX G42 Optical Node subscription.

    The workflow is valid for the shipped :class:`OpticalNodeNokiaGxG42`
    product type only: the construct step builds the shipped subscription
    model. Consumers with their own product type compose their own create
    workflow with the shipped parts.
    """
    return begin >> construct_optical_node_nokia_gx_g42_subscription >> store_process_subscription()


__all__ = [
    "CREATE_NOKIA_GX_G42_BLOCK_STEPS",
    "construct_optical_node_nokia_gx_g42_subscription",
    "create_optical_node_nokia_gx_g42",
    "create_optical_node_nokia_gx_g42_form_generator",
    "populate_optical_node_nokia_gx_g42_block",
    "populate_optical_node_nokia_gx_g42_block_step",
]
