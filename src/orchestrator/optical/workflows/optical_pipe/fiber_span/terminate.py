"""Terminate Optical Fiber Span Workflow."""

from collections.abc import Sequence
from typing import Annotated

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.hal.optical_port import factory_reset_port_configuration
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpan

logger = get_logger(__name__)

WARNING_MSG = (
    "Terminating an Optical Fiber Span will disable line ports and remove path configurations. "
    "To confirm termination, type 'TERMINATE' below."
)
WarningField = Annotated[
    str,
    Field(
        WARNING_MSG,
        title="⚠️ WARNING",
        json_schema_extra={"format": "long"},
    ),
]


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
    extra_form_pages: Sequence[type[FormPage]] = (),
) -> FormGenerator:
    """Input form generator for terminating an Optical Fiber Span.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
    """
    temp_subscription_id = subscription_id

    class TerminateFiberSpanForm(FormPage):
        warning: WarningField
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore[assignment]

        @model_validator(mode="after")
        def validate_confirmation(self) -> "TerminateFiberSpanForm":
            if self.warning != "TERMINATE":
                msg = "You must enter 'TERMINATE' to confirm deletion."
                raise ValueError(msg)
            return self

    user_input = yield TerminateFiberSpanForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    return user_input_dict


@step("Factory Reset Fiber Span Ports")
def factory_reset_span_ports(subscription: OpticalFiberSpan) -> State:
    """Prune the configuration of the terminating line ports of the fiber span."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    configuration_results = {
        f"{port_a.optical_port_host_node.pqdn} {port_a.optical_port_name}": factory_reset_port_configuration(
            port_a, port_b
        ),
        f"{port_b.optical_port_host_node.pqdn} {port_b.optical_port_name}": factory_reset_port_configuration(
            port_b, port_a
        ),
    }
    return {"configuration_results": configuration_results}


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_fiber_span() -> StepList:
    """Workflow to terminate an Optical Fiber Span."""
    return begin >> factory_reset_span_ports
