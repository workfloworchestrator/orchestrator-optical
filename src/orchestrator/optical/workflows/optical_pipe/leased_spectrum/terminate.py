"""Terminate Optical Leased Spectrum Workflow."""

from typing import Annotated

from pydantic import Field, model_validator
from pydantic_forms.types import InputForm, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.hal.optical_port import factory_reset_port_configuration
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrum

logger = get_logger(__name__)

WARNING_MSG = "To confirm termination of this Optical Leased Spectrum pipe, type 'TERMINATE' below."
WarningField = Annotated[
    str,
    Field(
        WARNING_MSG,
        title="⚠️ WARNING",
        json_schema_extra={"format": "long"},
    ),
]


def terminate_initial_input_form_generator(subscription_id: UUIDstr, customer_id: UUIDstr) -> InputForm:  # noqa: ARG001
    """Input form generator for terminating an Optical Leased Spectrum pipe."""
    temp_subscription_id = subscription_id

    class TerminateLeasedSpectrumForm(FormPage):
        warning: WarningField
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore[assignment]

        @model_validator(mode="after")
        def validate_confirmation(self) -> "TerminateLeasedSpectrumForm":
            if self.warning != "TERMINATE":
                msg = "You must enter 'TERMINATE' to confirm deletion."
                raise ValueError(msg)
            return self

    return TerminateLeasedSpectrumForm


@step("Factory Reset Leased Spectrum Ports")
def factory_reset_leased_spectrum_ports(subscription: OpticalLeasedSpectrum) -> State:
    """Prune the configuration of the terminating ports of the leased spectrum pipe."""
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


additional_steps = begin


@terminate_workflow(
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_leased_spectrum() -> StepList:
    """Workflow to terminate an Optical Leased Spectrum pipe."""
    return begin >> factory_reset_leased_spectrum_ports
