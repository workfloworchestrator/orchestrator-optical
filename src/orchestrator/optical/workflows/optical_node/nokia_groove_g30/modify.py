"""Modify Nokia Groove G30 Optical Node Workflow."""

from typing import Annotated

from annotated_types import Len
from pydantic import Field
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_node.nokia_groove_g30 import (
    OpticalNodeNokiaGrooveG30,
    OpticalNodeNokiaGrooveG30Provisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared import (
    update_abstract_optical_node_fields,
    update_optical_node_subscription_description,
)
from orchestrator.optical.workflows.shared import active_subscription_selector

logger = get_logger(__name__)

type IpAddressList = Annotated[list[IPAddress], Len(min_length=1, max_length=10), "List of management IP addresses."]

Instruction = Annotated[
    str,
    Field(
        "Select or enter only the fields you want to modify. The subscription will be updated with the new values.",
        title="ℹ️ Instruction ℹ️",
        json_schema_extra={"disabled": True},
    ),
]


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia Groove G30 Optical Node."""
    location_choice = active_subscription_selector(ProductType.ABSTRACT_OPTICAL_LOCATION.value)

    subscription = OpticalNodeNokiaGrooveG30.from_subscription(subscription_id)

    class ModifyNokiaGrooveG30Form(FormPage):
        instruction: Instruction
        location_id: location_choice | None = None
        optical_node_role: OpticalNodeRole | None = None
        pqdn: Pqdn | None = None
        optical_management_ip_list: IpAddressList | None = None
        optical_node_software_version: str | None = None

    user_input = yield ModifyNokiaGrooveG30Form
    user_input_dict = user_input.model_dump()

    return user_input_dict | {"subscription": subscription}


@step("Updating subscription model")
def update_optical_node_nokia_groove_g30_subscription(
    subscription: OpticalNodeNokiaGrooveG30Provisioning,
    location_id: UUIDstr | None = None,
    optical_node_role: OpticalNodeRole | None = None,
    pqdn: Pqdn | None = None,
    optical_management_ip_list: list[IPAddress] | None = None,
    optical_node_software_version: str | None = None,
) -> State:
    """Update fields on the Nokia Groove G30 Optical Node subscription."""
    update_abstract_optical_node_fields(
        optical_node_block=subscription.optical_node,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip_list=optical_management_ip_list,
        optical_node_software_version=optical_node_software_version,
    )

    return {"subscription": subscription}


additional_steps = begin


@modify_workflow(
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to modify an existing Nokia Groove G30 Optical Node."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_optical_node_nokia_groove_g30_subscription
        >> update_optical_node_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
