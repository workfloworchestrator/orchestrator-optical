# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from orchestrator.forms import FormPage
from orchestrator.forms.validators import (
    DisplaySubscription,
)
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, conditional, step
from orchestrator.workflows.utils import terminate_workflow
from pydantic_forms.types import InputForm, State, UUIDstr
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType
from products.product_blocks.transport_channel import (
    OpticalTransportChannelBlock,
)
from products.product_types.optical_digital_service import (
    OpticalDigitalService,
)
from products.services.optical_device import retrieve_ports_spectral_occupations
from products.services.optical_digital_service import (
    delete_transponder_crossconnect,
    factory_reset_transponder_client,
    factory_reset_transponder_line,
)
from products.services.optical_spectrum import delete_optical_circuit

logger = get_logger(__name__)


def terminate_initial_input_form_generator(
    subscription_id: UUIDstr, customer_id: UUIDstr
) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminateOpticalDigitalServiceForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore

    return TerminateOpticalDigitalServiceForm


@step("Factory resetting transponders/transceivers crossconnects")
def factory_reset_trx_crossconnects(subscription: OpticalDigitalService) -> State:
    ods = subscription.optical_digital_service
    client_a, client_b = ods.client_ports
    channels = ods.transport_channels

    lines_a, lines_b = [], []
    for channel in channels:
        lines_a.append(channel.line_ports[0])
        lines_b.append(channel.line_ports[1])

    results = {}
    for pair in [(client_a, lines_a), (client_b, lines_b)]:
        client, lines = pair
        device = client.optical_device
        client = client.port_name
        for i in range(len(lines)):
            lines[i] = lines[i].port_name

        result_key = f"{device.fqdn}"
        results[result_key] = delete_transponder_crossconnect(
            device, client
        )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


@step("Factory resetting transponders/transceivers client side")
def factory_reset_trx_client_side(subscription: OpticalDigitalService) -> State:
    ods = subscription.optical_digital_service
    results = {}
    for port in ods.client_ports:
        result_key = f"{port.optical_device.fqdn}"
        results[result_key] = factory_reset_transponder_client(
            port.optical_device, port.port_name,
        )

    return {
        "configuration_results": results,
    }


@step("Factory resetting transponders/transceivers line side")
def factory_reset_trx_line_side(subscription: OpticalDigitalService) -> State:
    ods = subscription.optical_digital_service
    channels = ods.transport_channels

    results = {}
    for channel in channels:

        for port in channel.line_ports:
            result_key = f"OCh{channel.och_id:03d} {port.optical_device.fqdn}"
            device = port.optical_device
            port_name = port.port_name
            results[result_key] = factory_reset_transponder_line(
                device, port_name,
            )

    return {
        "configuration_results": results,
    }


@step("Deleting optical sections")
def delete_optical_sections(subscription: OpticalDigitalService) -> State:
    channels = subscription.optical_digital_service.transport_channels
    results = {}
    for channel in channels:
        passband = channel.optical_spectrum.passband
        spectrum_name = channel.optical_spectrum.spectrum_name
        for section in channel.optical_spectrum.optical_spectrum_sections:
            src_device = section.add_drop_ports[0].optical_device
            key = f"OCh{channel.och_id:03d} {src_device.platform}"
            results[key] = delete_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
            )

    return {
        "configuration_results": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands(subscription: OpticalDigitalService) -> State:
    passbands_by_device = {}
    for channel in subscription.optical_digital_service.transport_channels:
        for section in channel.optical_spectrum.optical_spectrum_sections:
            for port in section.optical_path:
                device = port.optical_device
                if device.device_type in [
                    DeviceType.ROADM,
                    DeviceType.TransponderAndOADM,
                ]:
                    if device.fqdn not in passbands_by_device:
                        passbands_by_device[device.fqdn] = (
                            retrieve_ports_spectral_occupations(device)
                        )
                    port.used_passbands = passbands_by_device[device.fqdn].get(
                        port.port_name, []
                    )

    return {"subscription": subscription}

additional_steps = begin


@terminate_workflow(
    "terminate optical digital service",
    initial_input_form=terminate_initial_input_form_generator,
    additional_steps=additional_steps,
)
def terminate_optical_digital_service() -> StepList:
    """
    Workflow to terminate an Optical Digital Service subscription.
    This workflow checks if the subscription is the last client for the transport channels
    and performs necessary steps to reset transponders/transceivers, delete optical sections, and update
    used passbands accordingly.
    """
    def is_last_client_for_transport_channels(state: State) -> bool:
        is_last = state.get("is_last_client_for_transport_channels", None)

        if is_last is not None:
            return is_last

        subscription = state["subscription"]
        ods = subscription["optical_digital_service"]
        si_id = ods["transport_channels"][0]["subscription_instance_id"]
        channel = OpticalTransportChannelBlock.from_db(si_id)
        non_terminated_instances_using_channel = [
            instance
            for instance in channel.in_use_by
            if instance.subscription.status != SubscriptionLifecycle.TERMINATED
        ]
        state["is_last_client_for_transport_channels"] = (
            len(non_terminated_instances_using_channel) == 1
        )
        return state["is_last_client_for_transport_channels"]

    return (
        begin
        >> factory_reset_trx_crossconnects
        >> factory_reset_trx_client_side
        >> conditional(is_last_client_for_transport_channels)(
            factory_reset_trx_line_side
        )
        >> conditional(is_last_client_for_transport_channels)(delete_optical_sections)
        >> conditional(is_last_client_for_transport_channels)(update_used_passbands)
    )
