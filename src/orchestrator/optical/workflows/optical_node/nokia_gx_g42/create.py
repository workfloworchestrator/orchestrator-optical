"""Create Nokia GX G42 Optical Node Workflow."""

from typing import Annotated

from annotated_types import Len
from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_node.nokia_gx_g42 import (
    OpticalNodeNokiaGxG42Inactive,
    OpticalNodeNokiaGxG42Provisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared import (
    optical_node_subscription_description,
    populate_abstract_optical_node_fields,
    validate_pqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import (
    active_subscription_selector,
    create_summary_form,
)

logger = get_logger(__name__)

type IpAddressList = Annotated[list[IPAddress], Len(min_length=1, max_length=10), "List of management IP addresses."]


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating a Nokia GX G42 Optical Node."""
    location_choice = active_subscription_selector(ProductType.ABSTRACT_OPTICAL_LOCATION.value)

    class CreateNokiaGxG42Form(FormPage):
        model_config = ConfigDict(title=product_name)

        location_id: location_choice
        optical_node_role: OpticalNodeRole = OpticalNodeRole.TRANSPONDER
        pqdn: Pqdn
        optical_management_ip_list: IpAddressList
        optical_node_software_version: str | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateNokiaGxG42Form":
            validate_pqdn_uniqueness(self.pqdn)
            return self

    user_input = yield CreateNokiaGxG42Form
    user_input_dict = user_input.model_dump()
    summary_fields = [
        "location_id",
        "optical_node_role",
        "pqdn",
        "optical_management_ip_list",
        "optical_node_software_version",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Construct Subscription model")
def construct_optical_node_nokia_gx_g42_model(
    product: UUIDstr,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip_list: list[IPAddress],
    optical_node_software_version: str | None = None,
) -> State:
    """Construct the initial domain subscription model for a Nokia GX G42 Optical Node."""
    subscription = OpticalNodeNokiaGxG42Inactive.from_product_id(
        product_id=product,
        customer_id=location_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    populate_abstract_optical_node_fields(
        optical_node_block=subscription.optical_node,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip_list=optical_management_ip_list,
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


additional_steps = begin


@create_workflow(
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_optical_node_nokia_gx_g42() -> StepList:
    """Workflow to create a new Nokia GX G42 Optical Node."""
    return begin >> construct_optical_node_nokia_gx_g42_model >> store_process_subscription()
