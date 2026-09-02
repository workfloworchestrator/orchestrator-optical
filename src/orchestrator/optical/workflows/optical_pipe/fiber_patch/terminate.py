"""Terminate Optical Fiber Patch workflow.

This module ships the ready-to-use ``terminate_fiber_patch`` workflow for the
shipped Optical Fiber Patch product type, together with the importable parts:
the FormPage of the terminate confirmation form (as the
:func:`terminate_fiber_patch_form_pages` page sequence) and the termination
steps.

Consumers with their own model that has-a the shipped block declare their own
``@terminate_workflow`` with :data:`FIBER_PATCH_TERMINATE_STEPS` and compose
their own terminate form generator by yielding from the shipped page sequence
in one line.
"""

from typing import Annotated, cast

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.hal.port import factory_reset_port_configuration
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatchSubscription

WARNING_MSG = "To confirm termination of this Optical Fiber Patch, type 'TERMINATE' below."
WarningField = Annotated[
    str,
    Field(
        WARNING_MSG,
        title="⚠️ WARNING",
        json_schema_extra={"format": "long"},
    ),
]


def terminate_fiber_patch_form(subscription_id: UUIDstr) -> type[FormPage]:
    """Return the confirmation FormPage of the Optical Fiber Patch terminate form.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The confirmation FormPage of the shipped terminate form.
    """
    # Alias is required: a class body cannot reference a same-named enclosing parameter.
    temp_subscription_id = subscription_id

    class TerminateFiberPatchForm(FormPage):
        warning: WarningField
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

        @model_validator(mode="after")
        def validate_confirmation(self) -> "TerminateFiberPatchForm":
            """Raise unless the user typed 'TERMINATE' to confirm the termination."""
            if self.warning != "TERMINATE":
                msg = "You must enter 'TERMINATE' to confirm deletion."
                raise ValueError(msg)
            return self

    return TerminateFiberPatchForm


def terminate_fiber_patch_form_pages(subscription_id: UUIDstr) -> FormGenerator:
    """Yield the FormPage of the Optical Fiber Patch terminate form.

    This is the shipped terminate form as a page sequence: it yields the
    confirmation page and returns the collected user input. Consumers yield
    from it in one line inside their own terminate form generator, optionally
    adding their own pages.

    Args:
        subscription_id: The identifier of the subscription being terminated.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield terminate_fiber_patch_form(subscription_id)
    return user_input.model_dump()


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
) -> FormGenerator:
    """Generate the confirmation form before terminating an Optical Fiber Patch subscription.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).

    Returns:
        The collected user input of the confirmation page.
    """
    user_input = yield from terminate_fiber_patch_form_pages(subscription_id)
    return user_input


@step("Factory Reset Fiber Patch Ports")
def factory_reset_patch_ports(subscription: OpticalFiberPatchSubscription) -> State:
    """Prune the configuration of the terminating ports of the fiber patch."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    pipe_type = subscription.optical_pipe.optical_pipe_type
    configuration_results = {
        f"{port_a.optical_port_host_node.management.optical_module_node_fqdn} {port_a.optical_port_name}": (
            factory_reset_port_configuration(port_a, port_b, pipe_type)
        ),
        f"{port_b.optical_port_host_node.management.optical_module_node_fqdn} {port_b.optical_port_name}": (
            factory_reset_port_configuration(port_b, port_a, pipe_type)
        ),
    }
    return {"configuration_results": configuration_results}


#: Termination steps of the Optical Fiber Patch family. Consumers declare
#: their own ``@terminate_workflow`` with this step list and the shipped
#: :func:`terminate_initial_input_form_generator` form.
FIBER_PATCH_TERMINATE_STEPS: StepList = begin >> factory_reset_patch_ports


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_fiber_patch() -> StepList:
    """Workflow to terminate an Optical Fiber Patch subscription."""
    return begin >> FIBER_PATCH_TERMINATE_STEPS


__all__ = [
    "FIBER_PATCH_TERMINATE_STEPS",
    "terminate_fiber_patch",
    "terminate_fiber_patch_form_pages",
]
