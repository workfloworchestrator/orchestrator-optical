"""Modify Nokia FlexILS Optical Node Workflow."""

from collections.abc import Sequence
from functools import partial
from typing import Annotated, Any

from pydantic import Field
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, Workflow, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import (
    OpticalNodeNokiaFlexIls,
    OpticalNodeNokiaFlexIlsProvisioning,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared import (
    optical_node_modify_input_form,
    update_optical_node_fields,
    update_optical_node_subscription_description,
    validate_gmpls_id_uniqueness,
)

logger = get_logger(__name__)


def validate_flexils_fields(form: Any, subscription_id: UUIDstr) -> None:
    """Validate the FlexILS-specific form fields."""
    validate_gmpls_id_uniqueness(form.optical_flexils_gmpls_id, exclude_subscription_id=subscription_id)


def initial_input_form_generator(
    subscription_id: UUIDstr,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia FlexILS Optical Node.

    Args:
        subscription_id: The identifier of the subscription being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    yield from optical_node_modify_input_form(
        subscription_id,
        subscription_model=OpticalNodeNokiaFlexIls,
        extra_fields={
            "optical_flexils_gmpls_id": (
                Annotated[IPAddress, Field(title="GMPLS ID of the FlexILS node.")],
                "optical_flexils_gmpls_id",
            ),
            "optical_flexils_target_id": (
                Annotated[
                    str,
                    Field(title="Target Identifier (TID) of this FlexILS node (unique NENAME in the GMPLS network)."),
                ],
                "optical_flexils_target_id",
            ),
        },
        validate_extra=validate_flexils_fields,
        extra_form_pages=extra_form_pages,
        extra_summary_fields=extra_summary_fields,
    )


@step("Updating subscription model")
def update_optical_node_nokia_flexils_subscription(
    subscription: OpticalNodeNokiaFlexIlsProvisioning,
    customer_id: UUIDstr,
    location_id: UUIDstr,
    pqdn: Pqdn,
    optical_flexils_target_id: str,
    optical_flexils_gmpls_id: IPAddress,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
) -> State:
    """Update fields on the Nokia FlexILS Optical Node subscription."""
    update_optical_node_fields(
        subscription=subscription,
        customer_id=customer_id,
        location_id=location_id,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
    )
    subscription.optical_node.optical_flexils_gmpls_id = optical_flexils_gmpls_id
    subscription.optical_node.optical_flexils_target_id = optical_flexils_target_id

    return {"subscription": subscription}


def modify_optical_node_nokia_flexils_workflow(
    *,
    pre_steps: StepList = begin,
    post_steps: StepList = begin,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
    **kwargs: Any,
) -> Workflow:
    """Build the modify_optical_node_nokia_flexils workflow, optionally extended with user hooks.

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
    def modify_optical_node_nokia_flexils() -> StepList:
        """Workflow to modify an existing Nokia FlexILS Optical Node."""
        return (
            pre_steps
            >> begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> update_optical_node_nokia_flexils_subscription
            >> update_optical_node_subscription_description
            >> set_status(SubscriptionLifecycle.ACTIVE)
            >> post_steps
        )

    return modify_optical_node_nokia_flexils
