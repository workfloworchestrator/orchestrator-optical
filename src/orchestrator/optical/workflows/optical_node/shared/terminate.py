"""Shared termination form and steps for Optical Nodes."""

from pydantic_forms.types import InputForm, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import step


def terminate_initial_input_form_generator(subscription_id: UUIDstr, customer_id: UUIDstr) -> InputForm:
    """Generate initial input form for terminating an Optical Node subscription."""
    temp_subscription_id = subscription_id

    class TerminateOpticalNodeForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore[valid-type]

    return TerminateOpticalNodeForm


@step("Delete subscription from OSS/BSS")
def delete_optical_node_from_oss_bss(subscription: SubscriptionModel) -> State:
    """Delete the Optical Node subscription from OSS/BSS systems."""
    return {}
