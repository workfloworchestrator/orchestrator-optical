"""Create Optical Digital Service Workflow."""

from collections.abc import Sequence
from time import sleep
from typing import Annotated, cast
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice, choice_list, unique_conlist
from structlog import get_logger

from orchestrator.core.db import ProductTable, SubscriptionTable, db
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Divider, Label
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import subscription_instances_by_block_type_and_resource_value
from orchestrator.optical.hal.spectrum import deploy_optical_circuit
from orchestrator.optical.hal.transponder import (
    align_tx_power_to_target,
    configure_line_transceivers,
    configure_transceiver_client,
    configure_transponder_crossconnect,
    delta_rx_power_vs_target,
    get_signal_bandwidth,
)
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlock,
    OpticalDigitalServiceBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_line import (
    OpticalTransponderLinePortBlock,
)
from orchestrator.optical.products.product_blocks.optical_spectrum import OpticalSpectrumBlockInactive
from orchestrator.optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlockInactive,
)
from orchestrator.optical.products.product_types.optical_digital_service import (
    OpticalDigitalServiceInactive,
    OpticalDigitalServiceProvisioning,
    OpticalDigitalServiceSpeed,
    OpticalDigitalServiceType,
)
from orchestrator.optical.products.product_types.optical_node.abstracts import AbstractOpticalNode
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_digital_service.shared import (
    trx_line_port_patched_but_not_used_multiple_selector,
)
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    NoOpticalPathFoundError,
    find_add_drop_ports,
    multiple_optical_node_selector,
    optical_node_selector_of_roles,
    store_list_of_ports_into_spectrum_sections,
    transceiver_mode_selector,
    transport_channel_path_selector,
    unused_optical_client_port_selector,
    update_used_passbands,
)

logger = get_logger(__name__)

FlexBandwidth = Annotated[int, Field(ge=37_500, multiple_of=12_500)]

TRANSCEIVER_ROLES = [
    OpticalNodeRole.TRANSPONDER,
    OpticalNodeRole.TRANSPONDER_XOADM,
]

LINE_SYSTEM_ROLES = [
    OpticalNodeRole.ROADM,
    OpticalNodeRole.TRANSPONDER_XOADM,
    OpticalNodeRole.AMPLIFIER,
]

# 800 Gbit/s is not supported by the HAL yet, so it is excluded from the speed selector
SUPPORTED_SPEEDS = [
    OpticalDigitalServiceSpeed._100,  # noqa: SLF001
    OpticalDigitalServiceSpeed._400,  # noqa: SLF001
]


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate the subscription description for an Optical Digital Service."""
    ods = getattr(subscription, "optical_digital_service", None)
    if ods and getattr(ods, "optical_digital_service_name", None):
        return f"{ods.optical_digital_service_name} ({subscription.product.name})"
    return subscription.product.name


def initial_input_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),  # noqa: ARG001
) -> FormGenerator:
    """Generate the initial input form for creating an Optical Digital Service.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the form is submitted.
        extra_summary_fields: Accepted for uniformity but unused, because this workflow has no summary form.
    """
    node_a_choice = optical_node_selector_of_roles(
        roles=TRANSCEIVER_ROLES,
        prompt="This service connects this node: ",
    )
    node_b_choice = optical_node_selector_of_roles(
        roles=TRANSCEIVER_ROLES,
        prompt="...to this other node: ",
    )
    speed_choice = Choice(
        "What speed should this service have?",
        [(speed, f"{speed.value} Gbit/s") for speed in SUPPORTED_SPEEDS],
    )
    service_type_choice = Choice(
        "What type of service is this?",
        [(service_type.value, service_type.value) for service_type in OpticalDigitalServiceType],
    )
    num_carrier_choice = Choice(
        "By how many optical transport channels is this service transported?",
        [(1, "1"), (2, "2 (reverse multiplexing)")],
    )
    customer_choice = customer_choice_selector()

    class OdsForm0(FormPage):
        """Form for the service name, speed, type, nodes and number of carriers."""

        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        optical_digital_service_name: Annotated[str, Field(title="Optical Digital Service name")]
        optical_digital_service_speed: speed_choice = OpticalDigitalServiceSpeed._100  # noqa: SLF001
        optical_digital_service_type: service_type_choice = OpticalDigitalServiceType.ETHERNET
        num_carriers: num_carrier_choice = 1
        id_node_a: node_a_choice
        id_node_b: node_b_choice

        @model_validator(mode="after")
        def validate_data(self) -> "OdsForm0":
            if self.id_node_a == self.id_node_b:
                msg = "Only different devices can be connected"
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
            if existing_instances:
                msg = f"Optical Digital Service name '{self.optical_digital_service_name}' is already in use"
                raise ValueError(msg)

            return self

    user_input = yield OdsForm0
    user_input_dict = user_input.model_dump()

    sub_node_a = AbstractOpticalNode.from_subscription(user_input_dict["id_node_a"])
    optical_node_a = sub_node_a.optical_node
    sub_node_b = AbstractOpticalNode.from_subscription(user_input_dict["id_node_b"])
    optical_node_b = sub_node_b.optical_node

    ClientAChoice = unused_optical_client_port_selector(  # noqa: N806
        user_input_dict["id_node_a"],
        prompt=f"Select the client port on {optical_node_a.management.optical_module_node_fqdn}",
        product_block_type="OpticalTransponderClientPortBlock",
    )
    ClientBChoice = unused_optical_client_port_selector(  # noqa: N806
        user_input_dict["id_node_b"],
        prompt=f"Select the client port on {optical_node_b.management.optical_module_node_fqdn}",
        product_block_type="OpticalTransponderClientPortBlock",
    )

    class OdsForm1(FormPage):
        """Form for selecting the client ports of both nodes."""

        model_config = ConfigDict(title="Client Ports")

        name_client_port_a: ClientAChoice
        name_client_port_b: ClientBChoice

    user_input = yield OdsForm1
    user_input_dict.update(user_input.model_dump())

    num_carriers = user_input_dict["num_carriers"]

    LinesAChoice = trx_line_port_patched_but_not_used_multiple_selector(  # noqa: N806
        optical_node_subscription_id=user_input_dict["id_node_a"],
        client_port_name=user_input_dict["name_client_port_a"],
        prompt=f"Select the line port for each carrier on {optical_node_a.management.optical_module_node_fqdn}",
        min_items=num_carriers,
        max_items=num_carriers,
        unique_items=True,
    )
    LinesBChoice = trx_line_port_patched_but_not_used_multiple_selector(  # noqa: N806
        optical_node_subscription_id=user_input_dict["id_node_b"],
        client_port_name=user_input_dict["name_client_port_b"],
        prompt=f"Select the line port for each carrier on {optical_node_b.management.optical_module_node_fqdn}",
        min_items=num_carriers,
        max_items=num_carriers,
        unique_items=True,
    )

    ModeChoice = transceiver_mode_selector(  # noqa: N806
        optical_node_subscription_id=user_input_dict["id_node_a"],
        port_name=user_input_dict["name_client_port_a"],
        prompt="Select the operating mode of the transport channels",
    )

    FrequenciesChoice = Annotated[  # noqa: N806
        unique_conlist(cast(type[int], Frequency), min_items=num_carriers, max_items=num_carriers),
        Field(title="Central frequency (MHz) of each optical carrier"),
    ]

    BandwidthsChoice = Annotated[  # noqa: N806
        choice_list(
            cast(type[Choice], FlexBandwidth),
            min_items=num_carriers,
            max_items=num_carriers,
            unique_items=False,
        ),
        Field(title="Spectral width (MHz), including guardbands, reserved for each transport channel"),
    ]

    ExcludeOpticalDeviceChoiceList = multiple_optical_node_selector(  # noqa: N806
        roles=LINE_SYSTEM_ROLES,
        prompt="Do *not* pass through these Optical Nodes",
    )

    ExcludeSpanChoiceList = multiple_optical_pipe_selector(  # noqa: N806
        ProductType.OPTICAL_FIBER_SPAN.value,
        prompt="Do *not* pass through these Optical Fiber Spans",
    )

    class OdsForm2(FormPage):
        """Form for the optical transport channels parameters and routing constraints."""

        model_config = ConfigDict(title="Optical Transport Channels")

        line_ports_a: LinesAChoice
        line_ports_b: LinesBChoice
        frequencies: FrequenciesChoice
        bandwidths: BandwidthsChoice
        mode: ModeChoice

        routing_constraints: Label
        divider_002: Divider
        exclude_devices_list: ExcludeOpticalDeviceChoiceList | None = []  # noqa: RUF012
        exclude_fibers_list: ExcludeSpanChoiceList | None = []  # noqa: RUF012

    user_input = yield OdsForm2
    user_input_dict.update(user_input.model_dump())

    passband = (
        user_input_dict["frequencies"][0] - user_input_dict["bandwidths"][0] // 2,
        user_input_dict["frequencies"][0] + user_input_dict["bandwidths"][0] // 2,
    )

    no_path_found_msg = (
        "No optical path found, please adjust the routing constraints"
        " in the previous step or validate fibers in the path."
    )
    try:
        PathChoice = transport_channel_path_selector(  # noqa: N806
            user_input_dict["line_ports_a"][0],
            user_input_dict["line_ports_b"][0],
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
            line_ports_a=user_input_dict["line_ports_a"],
            line_ports_b=user_input_dict["line_ports_b"],
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

    class OdsForm3(FormPage):
        """Form for selecting the optical path."""

        model_config = ConfigDict(title="Optical Path")

        optical_path: PathChoice

        @model_validator(mode="after")
        def validate_data(self) -> "OdsForm3":
            if self.optical_path == no_path_found_msg:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            return self

    user_input = yield OdsForm3
    user_input_dict.update(user_input.model_dump())

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")

    return user_input_dict


@step("Saving input data into the optical digital service model")
def construct_optical_digital_service_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    id_node_a: UUIDstr,
    id_node_b: UUIDstr,
    optical_digital_service_name: str,
    optical_digital_service_speed: OpticalDigitalServiceSpeed,
    optical_digital_service_type: OpticalDigitalServiceType,
    num_carriers: int,
    name_client_port_a: str,
    name_client_port_b: str,
    frequencies: list[Frequency],
    bandwidths: list[FlexBandwidth],
    mode: str,
    line_ports_a: list[UUIDstr],
    line_ports_b: list[UUIDstr],
) -> State:
    """Construct the initial subscription and populate the Optical Digital Service model.

    The subscription is assembled manually because the speed and the type are
    required subscription-level fields that ``from_product_id`` cannot set: the
    product blocks are built first, with the transport channel name set to the
    subscription instance id of the channel block, and the subscription model is
    wrapped around them.
    """
    sub_node_a = AbstractOpticalNode.from_subscription(id_node_a)
    node_a = sub_node_a.optical_node
    sub_node_b = AbstractOpticalNode.from_subscription(id_node_b)
    node_b = sub_node_b.optical_node

    subscription_id = uuid4()

    client_ports = [
        OpticalTransponderClientPortBlockInactive.new(
            subscription_id=subscription_id,
            optical_port_name=name_client_port_a,
            optical_port_host_node=node_a,
            optical_port_description=(
                f"{optical_digital_service_name} remote:{node_b.management.optical_module_node_fqdn}"
                f" {name_client_port_b}"
            ),
        ),
        OpticalTransponderClientPortBlockInactive.new(
            subscription_id=subscription_id,
            optical_port_name=name_client_port_b,
            optical_port_host_node=node_b,
            optical_port_description=(
                f"{optical_digital_service_name} remote:{node_a.management.optical_module_node_fqdn}"
                f" {name_client_port_a}"
            ),
        ),
    ]

    transport_channels = []
    for i in range(num_carriers):
        passband = (
            frequencies[i] - bandwidths[i] // 2,
            frequencies[i] + bandwidths[i] // 2,
        )
        optical_spectrum = OpticalSpectrumBlockInactive.new(
            subscription_id=subscription_id,
            optical_spectrum_name=optical_digital_service_name,
            optical_spectrum_passband=passband,
        )
        channel = OpticalTransportChannelBlockInactive.new(
            subscription_id=subscription_id,
            optical_transport_central_frequency=frequencies[i],
            optical_transport_mode=mode,
            optical_transport_line_ports=[
                OpticalTransponderLinePortBlock.from_db(UUID(line_ports_a[i])),
                OpticalTransponderLinePortBlock.from_db(UUID(line_ports_b[i])),
            ],
            optical_transport_spectrum=optical_spectrum,
        )
        channel.optical_transport_channel_name = str(channel.subscription_instance_id)
        transport_channels.append(channel)

    ods_block = OpticalDigitalServiceBlockInactive.new(
        subscription_id=subscription_id,
        optical_digital_service_name=optical_digital_service_name,
        optical_digital_service_client_ports=client_ports,
        optical_digital_service_transport_channels=transport_channels,
    )

    product_db = db.session.get(ProductTable, product)
    if product_db is None:
        msg = f"Could not find a product for the given product_id {product}"
        raise KeyError(msg)

    product_model = ProductModel(
        product_id=product_db.product_id,
        name=product_db.name,
        description=product_db.description,
        product_type=product_db.product_type,
        tag=product_db.tag,
        status=product_db.status,
        created_at=product_db.created_at,
        end_date=product_db.end_date,
    )
    description = f"Initial subscription of {product_db.description}"
    subscription = SubscriptionTable(
        subscription_id=subscription_id,
        product_id=product,
        customer_id=customer_id,
        description=description,
        status=SubscriptionLifecycle.INITIAL.value,
        insync=False,
        version=1,
    )
    db.session.add(subscription)

    fixed_inputs = {fixed_input.name: fixed_input.value for fixed_input in product_db.fixed_inputs}
    subscription_model = OpticalDigitalServiceInactive(
        product=product_model,
        customer_id=customer_id,
        subscription_id=subscription_id,
        description=description,
        status=SubscriptionLifecycle.INITIAL,
        insync=False,
        start_date=None,
        end_date=None,
        note=None,
        version=1,
        **fixed_inputs,
        optical_digital_service_speed=optical_digital_service_speed,
        optical_digital_service_type=optical_digital_service_type,
        optical_digital_service=ods_block,
    )
    subscription_model.db_model = subscription

    return {
        "subscription": subscription_model,
        "subscription_id": subscription_model.subscription_id,  # for older generic step functions
    }


@step("Dividing the optical path into single-device-family sections")
def divide_path_into_sections(
    subscription: OpticalDigitalServiceInactive,
    optical_path: list[UUIDstr],
) -> State:
    """Split the optical path of every transport channel into vendor-specific sections."""
    if optical_path == ["direct_connection"]:
        # direct connection between transceivers without any managed line system in the middle
        return {
            "subscription": subscription,
        }

    ods = subscription.optical_digital_service
    channels = ods.optical_digital_service_transport_channels
    optical_spectrum = channels[0].optical_transport_spectrum
    store_list_of_ports_into_spectrum_sections(optical_path, optical_spectrum)

    if len(channels) == 2:  # noqa: PLR2004
        first_add_drop_port, last_add_drop_port = find_add_drop_ports(
            str(channels[1].optical_transport_line_ports[0].subscription_instance_id),
            str(channels[1].optical_transport_line_ports[1].subscription_instance_id),
        )
        # build a new list of UUID strings, replacing the path endpoints with the add/drop ports
        channel_2_path = list(optical_path)
        channel_2_path[0] = str(first_add_drop_port.subscription_instance_id)
        channel_2_path[-1] = str(last_add_drop_port.subscription_instance_id)

        store_list_of_ports_into_spectrum_sections(channel_2_path, channels[1].optical_transport_spectrum)

    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    """Update the subscription description with the service name and the product name."""
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
        "subscription": subscription,
    }


@step("Configuring the line ports on the transponders/transceivers")
def configure_trx_line_side(subscription: OpticalDigitalServiceProvisioning) -> State:
    """Configure the line ports of the transport channels on the devices."""
    ods = subscription.optical_digital_service
    channels = ods.optical_digital_service_transport_channels

    descriptions: list[str] = []
    central_freqs: list[int] = []
    modes: list[str] = []
    for channel in channels:
        spectrum_name = channel.optical_transport_spectrum.optical_spectrum_name
        if spectrum_name is None:
            msg = "Optical spectrum name is not set"
            raise ValueError(msg)
        descriptions.append(spectrum_name)
        central_freqs.append(channel.optical_transport_central_frequency)
        modes.append(channel.optical_transport_mode)

    devices = tuple(
        cast(AbstractOpticalNodeBlockInactive, port.optical_port_host_node)
        for port in channels[0].optical_transport_line_ports
    )
    port_names = (
        tuple(ch.optical_transport_line_ports[0].optical_port_name for ch in channels),
        tuple(ch.optical_transport_line_ports[1].optical_port_name for ch in channels),
    )

    results = {}
    for i, device in enumerate(devices):
        results[device.management.optical_module_node_fqdn] = configure_line_transceivers(
            device,
            port_names[i],
            tuple(central_freqs),
            tuple(modes),
            tuple(descriptions),
        )

    return {
        "configuration_results": results,
    }


@step("Configuring the client ports on the transponders/transceivers")
def configure_trx_client_side(subscription: OpticalDigitalServiceProvisioning) -> State:
    """Configure the client ports of the transponders on the devices."""
    ods = subscription.optical_digital_service
    results = {}
    for port in ods.optical_digital_service_client_ports:
        device = cast(AbstractOpticalNodeBlockInactive, port.optical_port_host_node)
        results[device.management.optical_module_node_fqdn] = configure_transceiver_client(
            device,
            port.optical_port_name,
            port.optical_port_description or "",
            subscription.optical_digital_service_speed,
        )

    return {
        "configuration_results": results,
    }


@step("Configuring the cross-connections in the transponders")
def configure_trx_crossconnects(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    """Configure the cross-connections between client and line ports in the transponders."""
    ods = subscription.optical_digital_service
    client_a, client_b = ods.optical_digital_service_client_ports
    channels = ods.optical_digital_service_transport_channels

    lines_a, lines_b = [], []
    for channel in channels:
        lines_a.append(channel.optical_transport_line_ports[0])
        lines_b.append(channel.optical_transport_line_ports[1])

    results = {}
    for client, lines in [(client_a, lines_a), (client_b, lines_b)]:
        device = cast(AbstractOpticalNodeBlockInactive, client.optical_port_host_node)
        client_name = client.optical_port_name
        line_names = [line.optical_port_name for line in lines]

        result_key = f"{device.management.optical_module_node_fqdn}"
        results[result_key] = configure_transponder_crossconnect(
            device,
            client_name,
            line_names,
            xconn_description=ods.optical_digital_service_name,
        )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


@step("Provisioning optical spectrum sections")
def provision_optical_sections(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    """Deploy the optical circuit of every spectrum section on the devices."""
    ods = subscription.optical_digital_service
    results = {}
    for channel in ods.optical_digital_service_transport_channels:
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
            src_port = section.optical_spectrum_section_add_drop_ports[0]
            src_device = src_port.optical_port_host_node
            result_key = f"{src_device.management.optical_module_node_fqdn} {src_port.optical_port_name}"
            results[result_key] = deploy_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
                carrier,
                label=ods.optical_digital_service_name,
                circuit_identifier=circuit_identifier,
            )

    return {
        "configuration_results": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands_step(subscription: OpticalDigitalServiceProvisioning) -> State:
    """Refresh the used passbands of the Open Line System ports in the path from the devices."""
    for channel in subscription.optical_digital_service.optical_digital_service_transport_channels:
        update_used_passbands(channel.optical_transport_spectrum)

    return {"subscription": subscription}


@step("Setting the transmitted optical power to match the line system target")
def set_trx_transmitted_power(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    """Align the transmitted optical power of the transceivers to the line system target."""
    ods = subscription.optical_digital_service
    results = {}

    for channel in ods.optical_digital_service_transport_channels:
        line_ports = channel.optical_transport_line_ports
        optical_spectrum = channel.optical_transport_spectrum
        spectrum_name = optical_spectrum.optical_spectrum_name
        if spectrum_name is None:
            msg = "Optical spectrum name is not set"
            raise ValueError(msg)

        add_drop_ports: list[OlsAddDropPortBlockProvisioning] = []
        for section in optical_spectrum.optical_spectrum_sections:
            section_src = section.optical_spectrum_section_add_drop_ports[0]
            if (
                section_src.optical_port_host_node.management.optical_module_node_vendor,
                section_src.optical_port_host_node.management.optical_module_node_platform,
            ) == (Vendor.NOKIA, Platform.FLEXILS):
                add_drop_ports = section.optical_spectrum_section_add_drop_ports
                break

        if add_drop_ports == []:
            continue

        for i, trib_port in enumerate(add_drop_ports):
            trib_device = trib_port.optical_port_host_node
            db_from_target = delta_rx_power_vs_target(
                trib_device,
                spectrum_name,
                circuit_identifier=channel.optical_transport_channel_name,
            )

            min_acceptable_diff = 0.0
            max_acceptable_diff = 1.5
            if min_acceptable_diff <= db_from_target <= max_acceptable_diff:
                result_key = f"{trib_device.management.optical_module_node_fqdn} {trib_port.optical_port_name}"
                results[result_key] = f"P_rx_measured - P_rx_target = {db_from_target} dB"
                continue

            trx_line_port = line_ports[i]
            trx = cast(AbstractOpticalNodeBlockInactive, trx_line_port.optical_port_host_node)
            trx_port_name = trx_line_port.optical_port_name
            result_key = f"{trx.management.optical_module_node_fqdn} {trx_port_name}"
            results[result_key] = align_tx_power_to_target(trx, trx_port_name, db_from_target)
            sleep(5)  # wait for the power to stabilize before measuring the next port
            db_from_target = delta_rx_power_vs_target(
                trib_device,
                spectrum_name,
                circuit_identifier=channel.optical_transport_channel_name,
            )
            result_key = f"{trib_device.management.optical_module_node_fqdn} {trib_port.optical_port_name}"
            results[result_key] = f"P_rx_measured - P_rx_target = {db_from_target} dB"

    return {
        "configuration_results": results,
    }


@create_workflow(initial_input_form=initial_input_form_generator)
def create_optical_digital_service() -> StepList:
    """Workflow to create a new Optical Digital Service."""
    return (
        begin
        >> construct_optical_digital_service_model
        >> store_process_subscription()
        >> divide_path_into_sections
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription_description
        >> configure_trx_line_side
        >> configure_trx_client_side
        >> configure_trx_crossconnects
        >> provision_optical_sections
        >> update_used_passbands_step
        >> step("Sleeping for 30 seconds")(lambda: sleep(30))
        >> set_trx_transmitted_power
    )
