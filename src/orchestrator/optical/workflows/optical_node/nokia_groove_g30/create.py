"""Create Nokia Groove G30 Optical Node Workflow."""

from collections.abc import Sequence
from functools import partial
from typing import Any

from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_node.nokia_groove_g30 import (
    OpticalNodeNokiaGrooveG30Inactive,
    OpticalNodeNokiaGrooveG30Provisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_location.shared import active_location_subscription_selector
from orchestrator.optical.workflows.optical_node.shared import (
    optical_node_subscription_description,
    populate_abstract_optical_node_fields,
    validate_pqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import create_summary_form

logger = get_logger(__name__)


def initial_input_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for creating a Nokia Groove G30 Optical Node.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    location_choice = active_location_subscription_selector()
    customer_choice = customer_choice_selector()

    class CreateNokiaGrooveG30Form(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        location_id: location_choice
        optical_node_role: OpticalNodeRole = OpticalNodeRole.TRANSPONDER
        pqdn: Pqdn
        optical_management_ip: IPAddress | None = None
        optical_loopback_ip: IPAddress | None = None
        optical_node_software_version: str | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateNokiaGrooveG30Form":
            validate_pqdn_uniqueness(self.pqdn)
            if not self.optical_management_ip and not self.optical_loopback_ip:
                msg = "At least one of management IP or loopback IP must be provided."
                raise ValueError(msg)
            return self

    user_input = yield CreateNokiaGrooveG30Form
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


@step("Construct Subscription model")
def construct_optical_node_nokia_groove_g30_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_node_software_version: str | None = None,
) -> State:
    """Construct the initial domain subscription model for a Nokia Groove G30 Optical Node."""
    subscription = OpticalNodeNokiaGrooveG30Inactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
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

    subscription = OpticalNodeNokiaGrooveG30Provisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = optical_node_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


def create_optical_node_nokia_groove_g30_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the create_optical_node_nokia_groove_g30 workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
        **kwargs: Extra arguments forwarded to the ``create_workflow`` decorator.
    """

    @create_workflow(
        initial_input_form=partial(
            initial_input_form_generator,
            extra_form_pages=extra_form_pages,
            extra_summary_fields=extra_summary_fields,
        ),
        **kwargs,
    )
    def create_optical_node_nokia_groove_g30() -> StepList:
        """Workflow to create a new Nokia Groove G30 Optical Node."""
        return (
            pre_steps
            >> begin
            >> construct_optical_node_nokia_groove_g30_model
            >> store_process_subscription()
            >> post_steps
        )

    return create_optical_node_nokia_groove_g30
