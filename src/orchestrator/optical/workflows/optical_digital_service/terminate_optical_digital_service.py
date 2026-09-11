"""Terminate Optical Digital Service Workflow."""

from collections.abc import Sequence
from typing import cast

from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, conditional, step
from orchestrator.core.workflows.utils import terminate_workflow
from orchestrator.optical.hal.transport_channel import (
    delete_transponder_crossconnect,
    factory_reset_transponder_client,
    factory_reset_transponder_lines,
)
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlock,
)
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalService
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    delete_optical_spectrum_sections,
    update_used_passbands,
)

logger = get_logger(__name__)


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr,
    customer_id: UUIDstr,  # noqa: ARG001
    extra_form_pages: Sequence[type[FormPage]] = (),
) -> FormGenerator:
    """Generate the initial input form for terminating an Optical Digital Service.

    Args:
        subscription_id: The identifier of the subscription being terminated.
        customer_id: The identifier of the subscription customer (kept for the WFO form signature).
        extra_form_pages: Additional form pages shown after the shipped confirmation page.
    """
    temp_subscription_id = subscription_id

    class TerminateOpticalDigitalServiceForm(FormPage):
        subscription_id: DisplaySubscription = cast(DisplaySubscription, temp_subscription_id)

    user_input = yield TerminateOpticalDigitalServiceForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    return user_input_dict


@step("Factory resetting transponders/transceivers crossconnects")
def factory_reset_trx_crossconnects(subscription: OpticalDigitalService) -> State:
    """Delete the cross-connects of the client ports on the devices."""
    results = {}
    for client in subscription.optical_digital_service.optical_digital_service_client_ports:
        device = cast(AnyOpticalNodeBlockProvisioningUnion, client.optical_port_host_node)
        results[device.management.optical_module_node_fqdn] = delete_transponder_crossconnect(
            device, client.optical_port_name
        )

    return {
        "deleted_xcon": results,
    }


@step("Factory resetting transponders/transceivers client side")
def factory_reset_trx_client_side(subscription: OpticalDigitalService) -> State:
    """Factory reset the client ports of the transponders on the devices."""
    results = {}
    for port in subscription.optical_digital_service.optical_digital_service_client_ports:
        device = cast(AnyOpticalNodeBlockProvisioningUnion, port.optical_port_host_node)
        results[device.management.optical_module_node_fqdn] = factory_reset_transponder_client(
            device, port.optical_port_name
        )

    return {
        "clients_config": results,
    }


@step("Factory resetting transponders/transceivers line side")
def factory_reset_trx_line_side(subscription: OpticalDigitalService) -> State:
    """Factory reset the line ports of the transport channels on the devices."""
    channels = subscription.optical_digital_service.optical_digital_service_transport_channels

    devices = tuple(
        cast(AnyOpticalNodeBlockProvisioningUnion, port.optical_port_host_node)
        for port in channels[0].optical_transport_line_ports
    )
    port_names = (
        tuple(ch.optical_transport_line_ports[0].optical_port_name for ch in channels),
        tuple(ch.optical_transport_line_ports[1].optical_port_name for ch in channels),
    )

    results = {}
    for i, device in enumerate(devices):
        results[device.management.optical_module_node_fqdn] = factory_reset_transponder_lines(
            device, list(port_names[i])
        )

    return {
        "lines_config": results,
    }


@step("Deleting optical sections")
def delete_optical_sections(subscription: OpticalDigitalService) -> State:
    """Delete the optical circuit of every spectrum section from the devices.

    Each transport channel's spectrum sections are torn down by
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.delete_optical_spectrum_sections`,
    which also deletes the OEL of each source node once all of its OSNCs are gone,
    and only when no other OSNC on the node still references it (otherwise the OEL
    is left in place because other OSNCs still need it). The channel identifier is
    used as the circuit identifier, so each channel's circuits and OEL are distinct;
    the results are namespaced by the channel to avoid clobbering across channels.
    """
    results = {}
    for channel in subscription.optical_digital_service.optical_digital_service_transport_channels:
        spectrum = channel.optical_transport_spectrum
        circuit_identifier = channel.optical_transport_channel_name
        channel_results = delete_optical_spectrum_sections(
            spectrum.optical_spectrum_sections,
            spectrum.optical_spectrum_passband,
            spectrum.optical_spectrum_name,
            circuit_identifier,
        )
        results.update({f"{circuit_identifier}:{key}": value for key, value in channel_results.items()})

    return {
        "ols_config": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands_step(subscription: OpticalDigitalService) -> State:
    """Refresh the used passbands of the Open Line System ports in the path from the devices."""
    for channel in subscription.optical_digital_service.optical_digital_service_transport_channels:
        update_used_passbands(channel.optical_transport_spectrum)

    return {"subscription": subscription}


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_optical_digital_service() -> StepList:
    """Workflow to terminate an Optical Digital Service subscription.

    This workflow checks if the subscription is the last client for the transport channels
    and performs necessary steps to reset transponders/transceivers, delete optical sections,
    and update used passbands accordingly.
    """

    def is_last_client_for_transport_channels(state: State) -> bool:
        is_last = state.get("is_last_client_for_transport_channels", None)

        if is_last is not None:
            return is_last

        subscription = state["subscription"]
        ods = subscription.optical_digital_service
        si_id = ods.optical_digital_service_transport_channels[0].subscription_instance_id
        channel = OpticalTransportChannelBlock.from_db(si_id)
        non_terminated_instances_using_channel = [
            instance
            for instance in channel.in_use_by
            if instance.subscription.status != SubscriptionLifecycle.TERMINATED
        ]
        state["is_last_client_for_transport_channels"] = len(non_terminated_instances_using_channel) == 1
        return state["is_last_client_for_transport_channels"]

    return (
        begin
        >> factory_reset_trx_crossconnects
        >> factory_reset_trx_client_side
        >> conditional(is_last_client_for_transport_channels)(factory_reset_trx_line_side)
        >> conditional(is_last_client_for_transport_channels)(delete_optical_sections)
        >> conditional(is_last_client_for_transport_channels)(update_used_passbands_step)
    )
