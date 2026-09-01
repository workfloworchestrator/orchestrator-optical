"""Modify Optical Digital Service Workflow."""

from collections.abc import Sequence
from time import sleep
from typing import Annotated, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice, choice_list, unique_conlist

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.db import subscription_instances_by_block_type_and_resource_value
from orchestrator.optical.hal.spectrum import modify_optical_circuit
from orchestrator.optical.hal.transport_channel import get_signal_bandwidth
from orchestrator.optical.products.product_blocks.optical_digital_service import OpticalDigitalServiceBlock
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_types.optical_digital_service import (
    OpticalDigitalService,
    OpticalDigitalServiceProvisioning,
)
from orchestrator.optical.utils.custom_types.frequencies import Bandwidth, Frequency, Passband
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service import (
    configure_trx_client_side,
    configure_trx_crossconnects,
    configure_trx_line_side,
    set_trx_transmitted_power,
)
from orchestrator.optical.workflows.optical_spectrum_service.shared import transceiver_mode_selector
from orchestrator.optical.workflows.shared import (
    merge_summary_fields,
    summary_form,
)

frequency_grid_mhz = 6_250
bandwidth_grid_mhz = 12_500


def initial_input_form_generator(
    subscription_id: UUIDstr,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Digital Service.

    Args:
        subscription_id: Subscription id of the service being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    subscription = OpticalDigitalService.from_subscription(subscription_id)
    ods = subscription.optical_digital_service

    transport_channels = ods.optical_digital_service_transport_channels
    num_carriers = len(transport_channels)
    old_name = ods.optical_digital_service_name
    old_frequencies = [ch.optical_transport_central_frequency for ch in transport_channels]
    old_passbands = [ch.optical_transport_spectrum.optical_spectrum_passband for ch in transport_channels]
    old_bandwidths = [end - start for start, end in old_passbands]
    old_mode = transport_channels[0].optical_transport_mode

    source_client_port = ods.optical_digital_service_client_ports[0]
    source_device = source_client_port.optical_port_host_node

    FrequenciesChoice = Annotated[  # noqa: N806
        unique_conlist(cast(type[int], Frequency), min_items=num_carriers, max_items=num_carriers),
        Field(title="Central frequency (MHz) of each optical carrier"),
    ]

    BandwidthsChoice = Annotated[  # noqa: N806
        choice_list(
            cast(type[Choice], Bandwidth),
            min_items=num_carriers,
            max_items=num_carriers,
            unique_items=False,
        ),
        Field(title="Spectral width (MHz), including guardbands, reserved for each transport channel"),
    ]

    ModeChoice = transceiver_mode_selector(  # noqa: N806
        optical_node_subscription_id=str(source_device.owner_subscription_id),
        port_name=source_client_port.optical_port_name,
        prompt="Select the operating mode of all transport channels",
    )
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    class ModifyOpticalDigitalServiceForm(FormPage):
        """Form for modifying the service name, frequencies, bandwidths and mode."""

        model_config = ConfigDict(title="Optical Transport Channels")

        customer_id: customer_choice
        optical_digital_service_name: str = old_name
        frequencies: FrequenciesChoice = old_frequencies
        bandwidths: BandwidthsChoice = old_bandwidths
        mode: ModeChoice = old_mode

        @model_validator(mode="after")
        def validate_data(self) -> "ModifyOpticalDigitalServiceForm":
            for frequency in self.frequencies:
                if frequency % frequency_grid_mhz != 0:
                    msg = "Frequency must be a multiple of 6_250 MHz"
                    raise ValueError(msg)
            for bandwidth in self.bandwidths:
                if bandwidth % bandwidth_grid_mhz != 0:
                    msg = "Bandwidth must be a multiple of 12_500 MHz"
                    raise ValueError(msg)
            existing_instances = subscription_instances_by_block_type_and_resource_value(
                cast(str, OpticalDigitalServiceBlock.name),
                "optical_digital_service_name",
                self.optical_digital_service_name,
                [
                    SubscriptionLifecycle.INITIAL,
                    SubscriptionLifecycle.PROVISIONING,
                    SubscriptionLifecycle.ACTIVE,
                ],
            )
            if any(
                str(instance.subscription_id) != str(subscription.subscription_id) for instance in existing_instances
            ):
                msg = f"Optical Digital Service name '{self.optical_digital_service_name}' is already in use"
                raise ValueError(msg)
            return self

    user_input = yield ModifyOpticalDigitalServiceForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    summary_fields = ["customer_id", "optical_digital_service_name", "frequencies", "bandwidths", "mode"]
    summary_fields = merge_summary_fields(summary_fields, extra_summary_fields, user_input_dict)
    before = [str(x) for x in (subscription.customer_id, old_name, old_frequencies, old_bandwidths, old_mode)]
    before += [""] * len(extra_summary_fields)
    after = [str(user_input_dict[nm]) for nm in summary_fields]
    yield from summary_form(
        subscription.product.name,
        {
            "labels": summary_fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )

    return user_input_dict | {"subscription": subscription}


@step("Saving new values in the database")
def update_subscription(
    subscription: OpticalDigitalServiceProvisioning,
    customer_id: UUIDstr,
    optical_digital_service_name: str,
    frequencies: list[Frequency],
    bandwidths: list[Bandwidth],
    mode: str,
) -> State:
    """Save the new name, frequencies, bandwidths and mode in the subscription."""
    ods = subscription.optical_digital_service
    old_passbands: list[Passband] = []
    subscription.customer_id = customer_id
    ods.optical_digital_service_name = optical_digital_service_name
    for channel, frequency, bandwidth in zip(
        ods.optical_digital_service_transport_channels,
        frequencies,
        bandwidths,
        strict=True,
    ):
        old_passbands.append(channel.optical_transport_spectrum.optical_spectrum_passband)
        channel.optical_transport_central_frequency = frequency
        channel.optical_transport_spectrum.optical_spectrum_passband = (
            frequency - bandwidth // 2,
            frequency + bandwidth // 2,
        )
        channel.optical_transport_mode = mode

    return {"subscription": subscription, "old_passbands": old_passbands}


@step("Modifying optical spectrum sections")
def modify_optical_sections(
    subscription: OpticalDigitalServiceProvisioning,
    old_passbands: list[Passband],
) -> State:
    """Modify the optical circuit of every spectrum section on the devices."""
    channels = subscription.optical_digital_service.optical_digital_service_transport_channels

    labels = []
    ch = channels[0]
    subscription_instances_using_channel = ch.in_use_by
    for si in subscription_instances_using_channel:
        ods = OpticalDigitalServiceBlock.from_db(si.subscription_instance_id)
        labels.append(ods.optical_digital_service_name)
    label = "+".join(sorted(labels))

    results = {}

    for channel, old_passband in zip(channels, old_passbands, strict=True):
        spectrum = channel.optical_transport_spectrum
        passband = spectrum.optical_spectrum_passband
        spectrum_name = spectrum.optical_spectrum_name
        if spectrum_name is None:
            msg = "Optical spectrum name is not set"
            raise ValueError(msg)
        port = channel.optical_transport_line_ports[0]
        carrier_width = get_signal_bandwidth(
            cast(AbstractOpticalNodeBlockInactive, port.optical_port_host_node),
            port.optical_port_name,
        )
        carrier = (channel.optical_transport_central_frequency, carrier_width)
        circuit_identifier = channel.optical_transport_channel_name

        for section in spectrum.optical_spectrum_sections:
            src_device = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            results[src_device.management.optical_module_node_fqdn] = modify_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
                carrier,
                label=label,
                old_passband=old_passband,
                circuit_identifier=circuit_identifier,
            )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


@modify_workflow(initial_input_form=initial_input_form_generator)
def modify_optical_digital_service() -> StepList:
    """Workflow to modify an existing Optical Digital Service."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> configure_trx_line_side
        >> configure_trx_client_side
        >> configure_trx_crossconnects
        >> modify_optical_sections
        >> step("Sleeping for 10 seconds")(lambda: sleep(10))
        >> set_trx_transmitted_power
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
