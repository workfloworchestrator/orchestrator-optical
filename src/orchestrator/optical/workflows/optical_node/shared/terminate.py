"""Shared termination form and steps for Optical Nodes."""

from collections.abc import Sequence

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
    extra_form_pages: Sequence[type[FormPage]] = (),
) -> FormGenerator:
    """Generate initial input form for terminating an Optical Node subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
    """
    temp_subscription_id = subscription_id

    class TerminateOpticalNodeForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore[valid-type]

    user_input = yield TerminateOpticalNodeForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    return user_input_dict


@step("Delete subscription from OSS/BSS")
def delete_optical_node_from_oss_bss(subscription: SubscriptionModel) -> State:  # noqa: ARG001
    """Delete the Optical Node subscription from OSS/BSS systems."""
    return {}


#: Termination steps shared by every Optical Node product. Consumers declare
#: their own ``@terminate_workflow`` with this step list and the shipped
#: :func:`terminate_initial_input_form_generator` form.
OPTICAL_NODE_TERMINATE_STEPS: StepList = begin >> delete_optical_node_from_oss_bss
