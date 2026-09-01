"""Validate Optical Digital Service Workflow."""

from typing import cast

from pydantic_forms.types import State
from structlog import get_logger

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.hal.spectrum import validate_optical_circuit
from orchestrator.optical.hal.transport_channel import (
    get_signal_bandwidth,
    validate_trx_client,
    validate_trx_crossconnect,
    validate_trx_line,
)
from orchestrator.optical.products.product_blocks.optical_digital_service import OpticalDigitalServiceBlock
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalService
from orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service import (
    subscription_description,
)

logger = get_logger(__name__)


@step("Loading initial state")
def load_initial_state_optical_digital_service(
    subscription: OpticalDigitalService,
) -> State:
    """Load the initial state of the subscription."""
    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalDigitalService,
) -> State:
    """Update the subscription description with the service name and the product name."""
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
    }


@step("Verifying transceiver/transponder line ports")
def verify_trx_line_ports(subscription: OpticalDigitalService) -> State:
    """Verify the line port configuration of the transceivers against the devices."""
    ods = subscription.optical_digital_service
    channels = ods.optical_digital_service_transport_channels

    descriptions = tuple(ch.optical_transport_spectrum.optical_spectrum_name for ch in channels)
    central_freqs = tuple(ch.optical_transport_central_frequency for ch in channels)
    modes = tuple(ch.optical_transport_mode for ch in channels)
    devices = tuple(
        cast(AbstractOpticalNodeBlockInactive, port.optical_port_host_node)
        for port in channels[0].optical_transport_line_ports
    )
    port_names = (
        tuple(ch.optical_transport_line_ports[0].optical_port_name for ch in channels),
        tuple(ch.optical_transport_line_ports[1].optical_port_name for ch in channels),
    )

    for i, device in enumerate(devices):
        validate_trx_line(device, port_names[i], central_freqs, modes, descriptions)

    return {}


@step("Verifying transceiver/transponder client ports")
def verify_trx_client_ports(subscription: OpticalDigitalService) -> State:
    """Verify the client port configuration of the transceivers against the devices."""
    ods = subscription.optical_digital_service

    for port in ods.optical_digital_service_client_ports:
        validate_trx_client(
            cast(AbstractOpticalNodeBlockInactive, port.optical_port_host_node),
            port.optical_port_name,
            port.optical_port_description or "",
            subscription.optical_digital_service_speed,
        )

    return {}


@step("Verifying transponder crossconnects")
def verify_transponder_crossconnects(subscription: OpticalDigitalService) -> State:
    """Verify the transponder cross-connects against the devices."""
    ods = subscription.optical_digital_service
    client_a, client_b = ods.optical_digital_service_client_ports
    channels = ods.optical_digital_service_transport_channels

    lines_a, lines_b = [], []
    for channel in channels:
        lines_a.append(channel.optical_transport_line_ports[0])
        lines_b.append(channel.optical_transport_line_ports[1])

    for client, lines in [(client_a, lines_a), (client_b, lines_b)]:
        device = cast(AbstractOpticalNodeBlockInactive, client.optical_port_host_node)
        client_name = client.optical_port_name
        line_names = [line.optical_port_name for line in lines]

        validate_trx_crossconnect(
            device,
            client_name,
            line_names,
            xconn_description=ods.optical_digital_service_name,
        )

    return {}


@step("Verifying optical spectrum sections")
def verify_optical_transport_channels(subscription: OpticalDigitalService) -> State:
    """Verify the optical circuit of every spectrum section against the devices."""
    channels = subscription.optical_digital_service.optical_digital_service_transport_channels

    labels = []
    ch = channels[0]
    subscription_instances_using_channel = ch.in_use_by
    for si in subscription_instances_using_channel:
        ods = OpticalDigitalServiceBlock.from_db(si.subscription_instance_id)
        labels.append(ods.optical_digital_service_name)
    label = "+".join(sorted(labels))

    for channel in channels:
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name
        passband = spectrum.optical_spectrum_passband
        port = channel.optical_transport_line_ports[0]
        carrier_bandwidth = get_signal_bandwidth(
            cast(AbstractOpticalNodeBlockInactive, port.optical_port_host_node),
            port.optical_port_name,
        )
        carrier_frequency = channel.optical_transport_central_frequency
        carrier = (carrier_frequency, carrier_bandwidth)
        circuit_identifier = channel.optical_transport_channel_name

        for section in spectrum.optical_spectrum_sections:
            src_device = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            validate_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
                carrier,
                label,
                circuit_identifier=circuit_identifier,
            )

    return {}


@validate_workflow()
def validate_optical_digital_service() -> StepList:
    """Workflow to validate an Optical Digital Service."""
    return (
        begin
        >> load_initial_state_optical_digital_service
        >> update_subscription_description
        >> verify_trx_line_ports
        >> verify_trx_client_ports
        >> verify_transponder_crossconnects
        >> verify_optical_transport_channels
    )
