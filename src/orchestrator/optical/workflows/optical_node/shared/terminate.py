"""Shared termination form and steps for Optical Nodes.

The terminate form ships as a page sequence (:func:`terminate_optical_node_form_pages`)
plus the page factory (:func:`terminate_optical_node_form`), so consumers compose
their own terminate form generator by yielding from the page sequence in one line
and optionally interleaving their own pages. The termination steps are shared by
every Optical Node product.
"""

from typing import cast

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step


def terminate_optical_node_form(subscription_id: UUIDstr) -> type[FormPage]:
    """Return the confirmation FormPage of the Optical Node terminate form.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The confirmation FormPage of the shipped terminate form.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateOpticalNodeForm(FormPage):
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

    return TerminateOpticalNodeForm


def terminate_optical_node_form_pages(subscription_id: UUIDstr) -> FormGenerator:
    """Yield the FormPage of the Optical Node terminate form.

    This is the shipped terminate form as a page sequence: it yields the
    confirmation page and returns the collected user input. Consumers yield
    from it in one line inside their own terminate form generator, optionally
    adding their own pages.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield terminate_optical_node_form(subscription_id)
    return user_input.model_dump()


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
) -> FormGenerator:
    """Generate the confirmation form before terminating an Optical Node subscription.

    It is a thin composition of the shipped page sequence
    (:func:`terminate_optical_node_form_pages`).

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).

    Returns:
        The collected user input of the confirmation page.
    """
    user_input = yield from terminate_optical_node_form_pages(subscription_id)
    return user_input


@step("Delete subscription from OSS/BSS")
def delete_optical_node_from_oss_bss(subscription: SubscriptionModel) -> State:  # noqa: ARG001
    """Delete the Optical Node subscription from OSS/BSS systems."""
    return {}


#: Termination steps shared by every Optical Node product. Consumers declare
#: their own ``@terminate_workflow`` with this step list and the shipped
#: :func:`terminate_initial_input_form_generator` form.
OPTICAL_NODE_TERMINATE_STEPS: StepList = begin >> delete_optical_node_from_oss_bss


__all__ = [
    "OPTICAL_NODE_TERMINATE_STEPS",
    "delete_optical_node_from_oss_bss",
    "terminate_initial_input_form_generator",
    "terminate_optical_node_form",
    "terminate_optical_node_form_pages",
]
