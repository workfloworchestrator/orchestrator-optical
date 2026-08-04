"""Create Nokia FlexILS Optical Node Workflow."""

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.hal.optical_node import discover_flexils_node
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import (
    OpticalNodeNokiaFlexIlsInactive,
    OpticalNodeNokiaFlexIlsProvisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_location.shared import active_location_subscription_selector
from orchestrator.optical.workflows.optical_node.shared import (
    optical_node_subscription_description,
    populate_abstract_optical_node_fields,
    validate_management_ips_uniqueness,
    validate_pqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import create_summary_form

logger = get_logger(__name__)


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating a Nokia FlexILS Optical Node."""
    location_choice = active_location_subscription_selector()

    class CreateNokiaFlexIlsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        location_id: location_choice
        pqdn: Annotated[
            Pqdn,
            Field(
                title="PQDN of the Optical Node. (e.g. if FQDN is `trx1.siteA.domain.com`, PQDN is `trx1.siteA`)"
            ),
        ]
        optical_management_ip: IPAddress | None = None
        optical_loopback_ip: IPAddress | None = None
        optical_flexils_gmpls_id: IPAddress
        tid: Annotated[
            str,
            Field(
                title="Target Identifier (TID) of this FlexILS node (unique identifier in the GMPLS network)."
            )
        ]

        @model_validator(mode="after")
        def validate_form(self) -> "CreateNokiaFlexIlsForm":
            validate_pqdn_uniqueness(self.pqdn)
            validate_management_ips_uniqueness(
                [ip for ip in (self.optical_management_ip, self.optical_loopback_ip) if ip is not None]
            )
            if not self.optical_flexils_gmpls_id:
                msg = "GMPLS ID is required."
                raise ValueError(msg)
            if not self.optical_management_ip and not self.optical_loopback_ip:
                msg = "At least one of management IP or loopback IP must be provided."
                raise ValueError(msg)
            return self

    user_input = yield CreateNokiaFlexIlsForm
    user_input_dict = user_input.model_dump()
    summary_fields = [
        "location_id",
        "pqdn",
        "optical_management_ip",
        "optical_loopback_ip",
        "optical_flexils_gmpls_id",
        "tid",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Discover Nokia FlexILS node properties")
def discover_optical_node_nokia_flexils(
    location_id: UUIDstr,
    tid: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
) -> State:
    """Connect to the node and retrieve its target id, role and software version."""
    discovery = discover_flexils_node(
        location_id=location_id,
        tid=tid,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
    )
    return {
        "optical_flexils_target_id": discovery.target_id,
        "optical_node_role": discovery.role,
        "optical_node_software_version": discovery.software_version,
    }


@step("Construct Subscription model")
def construct_optical_node_nokia_flexils_model(
    product: UUIDstr,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
    optical_flexils_target_id: str | None = None,
    optical_node_software_version: str | None = None,
) -> State:
    """Construct the initial domain subscription model for a Nokia FlexILS Optical Node."""
    subscription = OpticalNodeNokiaFlexIlsInactive.from_product_id(
        product_id=product,
        customer_id=location_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    populate_abstract_optical_node_fields(
        optical_node_block=subscription.optical_node,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_node_software_version=optical_node_software_version,
    )

    if optical_flexils_gmpls_id is not None:
        subscription.optical_node.optical_flexils_gmpls_id = optical_flexils_gmpls_id
    if optical_flexils_target_id is not None:
        subscription.optical_node.optical_flexils_target_id = optical_flexils_target_id

    subscription = OpticalNodeNokiaFlexIlsProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = optical_node_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


@create_workflow(initial_input_form=initial_input_form_generator)
def create_optical_node_nokia_flexils() -> StepList:
    """Workflow to create a new Nokia FlexILS Optical Node."""
    return (
        begin
        >> discover_optical_node_nokia_flexils
        >> construct_optical_node_nokia_flexils_model
        >> store_process_subscription()
    )
