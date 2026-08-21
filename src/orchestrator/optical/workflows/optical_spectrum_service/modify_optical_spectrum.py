"""Modify Optical Spectrum Service Workflow."""

from collections.abc import Sequence
from typing import Annotated

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Divider
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.hal.optical_node import vendor_of
from orchestrator.optical.hal.optical_spectrum import modify_optical_circuit
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_spectrum_service import (
    OpticalSpectrum,
    OpticalSpectrumProvisioning,
)
from orchestrator.optical.utils.custom_types.frequencies import Frequency, Passband
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum import (
    subscription_description,
    update_used_passbands_step,
)
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    NoOpticalPathFoundError,
    multiple_optical_node_selector,
    optical_spectrum_path_selector,
    store_list_of_ports_into_spectrum_sections,
)
from orchestrator.optical.workflows.shared import modify_summary_form

logger = get_logger(__name__)

LINE_SYSTEM_ROLES = [
    OpticalNodeRole.ROADM,
    OpticalNodeRole.TRANSPONDER_XOADM,
    OpticalNodeRole.AMPLIFIER,
]


def initial_input_form_generator(
    subscription_id: UUIDstr,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Spectrum service.

    Args:
        subscription_id: Subscription id of the service being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    subscription = OpticalSpectrum.from_subscription(subscription_id)
    optical_spectrum = subscription.optical_spectrum_service
    old_passband = optical_spectrum.optical_spectrum_passband
    old_spectrum_name = optical_spectrum.optical_spectrum_name

    sections = optical_spectrum.optical_spectrum_sections
    optical_device_a = sections[0].optical_spectrum_section_add_drop_ports[0].optical_port_host_node
    optical_device_b = sections[-1].optical_spectrum_section_add_drop_ports[-1].optical_port_host_node
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    class ModifyOpticalSpectrumForm(FormPage):
        """Form for modifying the service name and the min and max frequencies."""

        customer_id: customer_choice
        optical_spectrum_name: str = old_spectrum_name
        frequency_min: Annotated[Frequency, Field(title="Start frequency (THz)", multiple_of=6250)] = old_passband[0]
        frequency_max: Annotated[Frequency, Field(title="End frequency (THz)", multiple_of=6250)] = old_passband[1]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "ModifyOpticalSpectrumForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            return self

    user_input = yield ModifyOpticalSpectrumForm
    user_input_dict = user_input.model_dump()

    ExcludeOpticalDeviceChoiceList = multiple_optical_node_selector(  # noqa: N806
        roles=LINE_SYSTEM_ROLES,
        prompt="Do *not* pass through these Optical Nodes",
    )

    ExcludeSpanChoiceList = multiple_optical_pipe_selector(  # noqa: N806
        ProductType.OPTICAL_FIBER_SPAN.value,
        prompt="Do *not* pass through these Optical Fiber Spans",
    )

    class OpticalSpectrumConstraintsForm(FormPage):
        """Form for specifying which optical devices or spans MUST NOT be traversed by the optical spectrum."""

        exclude_devices_list: ExcludeOpticalDeviceChoiceList
        divider1: Divider
        exclude_fibers_list: ExcludeSpanChoiceList

    user_input = yield OpticalSpectrumConstraintsForm
    user_input_dict.update(user_input.model_dump())

    passband = (user_input_dict["frequency_min"], user_input_dict["frequency_max"])

    no_path_found_msg = (
        "No optical path found, please adjust the routing constraints"
        " in the previous step or validate fibers in the path."
    )
    try:
        PathChoice = optical_spectrum_path_selector(  # noqa: N806
            str(optical_device_a.subscription_instance_id),
            str(optical_device_b.subscription_instance_id),
            passband,
            user_input_dict["exclude_devices_list"],
            user_input_dict["exclude_fibers_list"],
            prompt=(
                "Select the optical path, if you don't see the desired path,"
                " adjust constraints in previous step or validate fibers along the path."
            ),
        )
    except NoOpticalPathFoundError:
        logger.exception(
            "No optical path found",
            optical_device_a=optical_device_a.subscription_instance_id,
            optical_device_b=optical_device_b.subscription_instance_id,
            passband=passband,
            exclude_devices_list=user_input_dict["exclude_devices_list"],
            exclude_fibers_list=user_input_dict["exclude_fibers_list"],
        )

        PathChoice = Choice(  # noqa: N806
            no_path_found_msg,
            [
                (no_path_found_msg, no_path_found_msg),
            ],
        )

    class OpticalSpectrumPathForm(FormPage):
        """Form for selecting the optical path."""

        optical_path: PathChoice

        @model_validator(mode="after")
        def validate_data(self) -> "OpticalSpectrumPathForm":
            if self.optical_path == no_path_found_msg:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            return self

    user_input = yield OpticalSpectrumPathForm
    user_input_dict.update(user_input.model_dump())

    user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")

    user_input_dict["optical_spectrum_passband"] = (
        user_input_dict["frequency_min"],
        user_input_dict["frequency_max"],
    )
    summary_fields = [
        "customer_id",
        "optical_spectrum_name",
        "optical_spectrum_passband",
    ]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from modify_summary_form(
        user_input_dict,
        subscription.optical_spectrum_service,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
        extra_summary_fields=extra_summary_fields,
    )

    return user_input_dict | {"subscription": subscription}


@step("Update subscription")
def update_subscription(
    subscription: OpticalSpectrumProvisioning,
    customer_id: UUIDstr,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
) -> State:
    """Update the spectrum name and passband on the subscription."""
    spectrum = subscription.optical_spectrum_service
    old_passband = spectrum.optical_spectrum_passband

    # set attributes: name
    spectrum.optical_spectrum_name = optical_spectrum_name

    # set attributes: passband
    passband: Passband = (frequency_min, frequency_max)
    spectrum.optical_spectrum_passband = passband

    subscription.customer_id = customer_id

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
        "old_passband": old_passband,
    }


@step("Update subscription description")
def update_subscription_description(subscription: OpticalSpectrumProvisioning) -> State:
    """Update the subscription description with the spectrum name and the product name."""
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@step("Dividing the optical path into single-device-family sections")
def divide_path_into_sections(
    subscription: OpticalSpectrumProvisioning,
    optical_path: list[UUIDstr],
) -> State:
    """Split the optical path into vendor-specific sections, reusing the existing add/drop ports."""
    sections = subscription.optical_spectrum_service.optical_spectrum_sections
    src_port = sections[0].optical_spectrum_section_add_drop_ports[0]
    dst_port = sections[-1].optical_spectrum_section_add_drop_ports[-1]

    optical_path.insert(0, str(src_port.subscription_instance_id))
    optical_path.append(str(dst_port.subscription_instance_id))

    store_list_of_ports_into_spectrum_sections(optical_path, subscription.optical_spectrum_service)

    return {
        "subscription": subscription,
    }


@step("Modifying optical spectrum sections")
def modify_optical_sections(
    subscription: OpticalSpectrumProvisioning,
    old_passband: Passband,
) -> State:
    """Modify the optical circuit of every spectrum section on the devices."""
    optical_spectrum = subscription.optical_spectrum_service
    passband = optical_spectrum.optical_spectrum_passband
    spectrum_name = optical_spectrum.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    carrier_width = passband[1] - passband[0]
    central_frequency = int((passband[0] + passband[1]) / 2)
    carrier = (central_frequency, carrier_width)
    circuit_identifier = str(optical_spectrum.subscription_instance_id)

    results = {}
    for section in optical_spectrum.optical_spectrum_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        results[vendor_of(src_node)] = modify_optical_circuit(
            src_node,
            section,
            optical_spectrum_name=spectrum_name,
            passband=passband,
            carrier=carrier,
            label=spectrum_name,
            old_passband=old_passband,
            circuit_identifier=circuit_identifier,
        )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


@modify_workflow(initial_input_form=initial_input_form_generator)
def modify_optical_spectrum() -> StepList:
    """Workflow to modify an existing Optical Spectrum service."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> update_subscription_description
        >> divide_path_into_sections
        >> modify_optical_sections
        >> update_used_passbands_step
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
