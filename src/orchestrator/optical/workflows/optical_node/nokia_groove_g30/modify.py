"""Modify Nokia Groove G30 Optical Node Workflow."""

from collections.abc import Sequence
from functools import partial
from typing import Any

from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_node.nokia_groove_g30 import (
    OpticalNodeNokiaGrooveG30,
    OpticalNodeNokiaGrooveG30Provisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared import (
    optical_node_modify_input_form,
    update_optical_node_fields,
    update_optical_node_subscription_description,
)

logger = get_logger(__name__)


def initial_input_form_generator(
    subscription_id: UUIDstr,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia Groove G30 Optical Node.

    Args:
        subscription_id: The identifier of the subscription being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    yield from optical_node_modify_input_form(
        subscription_id,
        subscription_model=OpticalNodeNokiaGrooveG30,
        extra_form_pages=extra_form_pages,
        extra_summary_fields=extra_summary_fields,
    )


@step("Updating subscription model")
def update_optical_node_nokia_groove_g30_subscription(
    subscription: OpticalNodeNokiaGrooveG30Provisioning,
    customer_id: UUIDstr,
    location_id: UUIDstr,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
) -> State:
    """Update fields on the Nokia Groove G30 Optical Node subscription."""
    update_optical_node_fields(
        subscription=subscription,
        customer_id=customer_id,
        location_id=location_id,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
    )

    return {"subscription": subscription}


def modify_optical_node_nokia_groove_g30_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the modify_optical_node_nokia_groove_g30 workflow, optionally extended with user hooks.

    Args:
        pre_steps: Steps run before the shipped workflow steps.
        post_steps: Steps run after the shipped workflow steps.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
        **kwargs: Extra arguments forwarded to the ``modify_workflow`` decorator.
    """

    @modify_workflow(
        initial_input_form=partial(
            initial_input_form_generator,
            extra_form_pages=extra_form_pages,
            extra_summary_fields=extra_summary_fields,
        ),
        **kwargs,
    )
    def modify_optical_node_nokia_groove_g30() -> StepList:
        """Workflow to modify an existing Nokia Groove G30 Optical Node."""
        return (
            pre_steps
            >> begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> update_optical_node_nokia_groove_g30_subscription
            >> update_optical_node_subscription_description
            >> set_status(SubscriptionLifecycle.ACTIVE)
            >> post_steps
        )

    return modify_optical_node_nokia_groove_g30
