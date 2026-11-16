"""Nokia GX G42 transponder-level HAL operations.

The configuration is declarative (see :mod:`orchestrator.optical.hal.reconcile`): every
object has one ``render_*`` function returning its desired configuration, and the
configure / validate / factory-reset operations are that rendering applied, verified or
released. The rendering units (scopes) of an owner block on a node are ``line``,
``client:<port>``, ``crossconnect:<client port>`` and ``tx-power:<line port>``.
"""

from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from orchestrator.optical.hal._common import _as_decimal, _node_id, _retrieve_required
from orchestrator.optical.hal.adapters.nokia_gx_g42._sdk import (
    CreateXconInput,
    G42Client,
    LldpAdminStatusEnum,
    LldpModeEnum,
    PayloadTypeEnum,
    PhyModeEnum,
    ServiceTypeEnum,
    SignalTypeEnum,
    XconItem,
)
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import g42_port_node, get_g42_client
from orchestrator.optical.hal.reconcile import (
    ConfigDriftError,
    Fragment,
    apply_config,
    forget_config,
    fragment,
    release_config,
    verify_config,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.utils.labels import conduits_label, label_name

#: Rendering units of the transponder configuration of an owner block on a node.
LINE_SCOPE = "line"
CLIENT_SCOPE = "client:{}"
CROSSCONNECT_SCOPE = "crossconnect:{}"
TX_POWER_SCOPE = "tx-power:{}"

#: Leaves shared by every GX G42 object put in service.
_IN_SERVICE: dict[str, Any] = {"admin_state": "unlock", "alarm_report_control": "allowed"}


def _client_speed_config(speed: OpticalDigitalServiceSpeed) -> tuple[str, str, str, str]:
    """Map a digital service speed to the GX G42 (required type, required subtype, phy mode, service type)."""
    match speed:
        case OpticalDigitalServiceSpeed._100:  # noqa: SLF001
            return "gx:QSFP28", "TOM-100G-Q", "100G", "100GBE"
        case OpticalDigitalServiceSpeed._400:  # noqa: SLF001
            return "gx:QSFPDD", "TOM-400G-Q-DR4", "400GE", "400GBE"
    msg = f"Unsupported speed {speed} for the GX G42 client configuration"
    raise NotImplementedError(msg)


def _client_path(client_port_name: str) -> str:
    """Return the instance-identifier of the ethernet facility of a client port, as sent in ``create-xcon``."""
    return f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"


def _is_client_endpoint(path: str, client_port_name: str) -> bool:
    """Tell whether a cross-connect end-point read from the device is the ethernet facility of a client port.

    The device answers with the module name (``/ioa-network-element:ne/...``) where the
    request holds the YANG prefix (``/ioa-ne:ne/...``): the leading prefix is not compared.
    """
    return path.endswith(f"/facilities/ethernet[name='{client_port_name}']")


def _find_xcon(
    g42: G42Client,
    client_port_name: str,
    line: str,
    direction: str,
    payload_type: str,
) -> XconItem | None:
    """Helper function to find an existing cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client_port_name: The client port name.
        line: Line ID inside the destination ODU string.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.

    Returns:
        The cross-connect configuration if found, otherwise None.

    Raises:
        ValueError: If a cross-connect with the same source and destination already exists.
    """
    # An empty list reads as no data over NETCONF.
    xcons = g42.data.ioa_network_element_ne.services.xcon.retrieve(depth=2, content="config") or []

    for xcon in xcons:
        source_is_client = _is_client_endpoint(xcon.source, client_port_name)
        destination_is_client = _is_client_endpoint(xcon.destination, client_port_name)
        source_destination_match = (source_is_client and line in xcon.destination) or (
            destination_is_client and line in xcon.source
        )
        payload_type_match = xcon.payload_type == payload_type
        direction_match = xcon.direction == direction
        if source_destination_match and payload_type_match and direction_match:
            return xcon

        if source_is_client or destination_is_client:
            msg = (
                f"Tributary already cross-connected:"
                f" {xcon.destination}  x  {xcon.source} ."
                f"Please check and remove manually if wrong."
            )
            raise ValueError(msg)

    return None


def _create_xcon(
    g42: G42Client,
    client: str,
    dst_parent_odu: str,
    direction: str,
    payload_type: str,
    label: str,
    circuit_identifier: str,
    dst_time_slots: str,
) -> None:
    """Helper function to create a cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client: Source client path.
        dst_parent_odu: Destination parent ODU path.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.
        label: Label for the cross-connect.
        circuit_identifier: Circuit id suffix of the cross-connect (the owner block id).
        dst_time_slots: Time slots for the cross-connect.

    Raises:
        RuntimeError: If the cross-connect creation fails (an existing one is not a failure).
    """
    # The SDK marks both cases of the YANG source/destination choices as mandatory, so
    # validating the input would reject this valid one (existing source, new destination
    # ODU): build it unvalidated.
    xcon_input = CreateXconInput.model_construct(
        payload_type=PayloadTypeEnum(payload_type),
        direction=direction,
        label=label,
        circuit_id_suffix=circuit_identifier,
        source=client,
        dst_parent_odu=dst_parent_odu,
        dst_time_slots=dst_time_slots,
    )
    try:
        g42.operations.ioa_services_create_xcon(xcon_input)
    except RuntimeError as e:
        # The SDK maps NETCONF <rpc-error>s to RuntimeError, keeping the RFC 6241 <error-tag>.
        if getattr(e, "rpc_error_tag", None) != "data-exists":
            raise


def _derive_optical_channel_key(line_port_names: list[str]) -> str:
    """Derive the optical channel key of the given line port names."""
    if len(line_port_names) == 1:
        return f"{line_port_names[0]}-1"

    num_lines_if_coupled_mode = 2
    if len(line_port_names) == num_lines_if_coupled_mode:
        for name in line_port_names:
            if name.endswith("L1"):
                return f"{name}-1"

    msg = (
        f"Invalid line port names: {line_port_names}. "
        "For coupled modes, ensure both ports are on the same card, thus one ends with 'L1'."
    )
    raise ValueError(msg)


def _retrieve_payload_type(g42: G42Client, client_port_name: str) -> Literal["100GBE", "400GBE"]:
    """Retrieve the payload type of the given client port on a G42 device."""
    trib_ptp = _retrieve_required(
        g42.data.ioa_network_element_ne.facilities.trib_ptp(client_port_name).retrieve, depth=2, content="config"
    )
    payload_type = trib_ptp.service_type

    if payload_type is None:
        msg = f"Unable to retrieve payload type for {g42.host} {client_port_name}"
        raise ValueError(msg)

    match payload_type.value:
        case "100GBE":
            return "100GBE"
        case "400GBE":
            return "400GBE"
    msg = f"Invalid payload type '{payload_type}' for {g42.host} {client_port_name}. Expected '100GBE' or '400GBE'."
    raise ValueError(msg)


def _retrieve_time_slots(g42: G42Client, odu_name: str, speed: Literal["100GBE", "400GBE"]) -> str:
    """Retrieve the first block of available time slots of the given ODU with enough capacity for the speed."""
    minimum_slots_required = 80 if speed == "100GBE" else 320

    odu = _retrieve_required(g42.data.ioa_network_element_ne.facilities.odu(odu_name).retrieve, depth=2)
    available_time_slots = odu.available_time_slots  # e.g. "1..80,161..480"
    if not available_time_slots:
        msg = f"The key 'available-time-slots' is missing or empty in the ODU data.ODU: {odu}"
        raise ValueError(msg)
    available_time_slots = available_time_slots.split(",")  # e.g. ["1..80", "161..480"]
    available_time_slots = [ts.split("..") for ts in available_time_slots]  # e.g. [["1", "80"], ["161", "480"]]
    available_time_slots = [(int(start), int(end)) for start, end in available_time_slots]  # e.g. [(1, 80), (161, 480)]

    # find next time slot that has at least minimum_slots_required
    for start, end in available_time_slots:
        if end - start + 1 >= minimum_slots_required:
            return f"{start}..{start + minimum_slots_required - 1}"

    msg = (
        f"Not enough available time slots for {g42.host} {odu_name}. "
        f"Minimum required: {minimum_slots_required}, "
        f"Available: {available_time_slots}"
    )
    raise ValueError(msg)


def get_signal_bandwidth(optical_node_block: NokiaGxG42BlockProvisioning, port_name: str) -> int:
    """Return the signal bandwidth, in MHz, of the transport channel carried by a GX G42 line port.

    Args:
        optical_node_block: The Optical Node hosting the line port.
        port_name: The line port name, e.g. ``"1-4-L1"``.

    Returns:
        The signal bandwidth in MHz.

    Raises:
        ValueError: If the channel of the given port cannot be found.
    """
    g42 = get_g42_client(optical_node_block)
    channel = None
    channels = g42.data.ioa_network_element_ne.facilities.super_channel.retrieve(depth=2)
    for ch in channels:
        if any(carrier.startswith(port_name) for carrier in ch.carriers):
            channel = ch
            break

    if channel is None:
        msg = f"Channel of port {port_name} not found"
        raise ValueError(msg)

    if channel.spectral_bandwidth is None:
        msg = f"Channel of port {port_name} has no spectral bandwidth"
        raise ValueError(msg)

    bw = channel.spectral_bandwidth * 1000
    num_carriers_if_coupled = 2
    if len(channel.carriers) == num_carriers_if_coupled:
        bw = bw // 2
    return round(bw)


def render_line_transceivers(
    root: Any,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> list[Fragment]:
    """Render the line transceivers of a GX G42: ports, super-channel groups, super-channel and carriers.

    The optical carriers are created by the device with their super-channel, so they are
    rendered one stage after it.

    Args:
        root: The data root navigator of a GX G42 client (``client.data``).
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Returns:
        The desired configuration of the line side.

    Raises:
        ValueError: If the modes differ.
    """
    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 transponder line configuration but got {modes}."
        raise ValueError(msg)

    facilities = root.ioa_network_element_ne.facilities
    fragments: list[Fragment] = []
    for port_name, description in zip(port_names, descriptions, strict=True):
        fragments.append(fragment(g42_port_node(root, port_name), label=description, **_IN_SERVICE))
        fragments.append(fragment(facilities.super_channel_group(port_name), label=description, **_IN_SERVICE))
    fragments.append(
        fragment(
            facilities.super_channel("_".join(port_names)),
            label=conduits_label(label_name(description) for description in descriptions),
            carrier_mode=modes[0],
            carriers=[f"{port_name}-1" for port_name in port_names],
            **_IN_SERVICE,
        )
    )
    fragments.extend(
        fragment(
            facilities.optical_carrier(f"{port_name}-1"), stage=1, label=description, frequency=frequency, **_IN_SERVICE
        )
        for port_name, description, frequency in zip(port_names, descriptions, central_frequencies, strict=True)
    )
    return fragments


def render_transceiver_client(
    root: Any,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> list[Fragment]:
    """Render a client port of a GX G42 transponder: port, TOM, tributary and ethernet facility.

    Each object is created by the device once the previous one is configured, so they
    are rendered in successive stages.

    Args:
        root: The data root navigator of a GX G42 client (``client.data``).
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Returns:
        The desired configuration of the client port.

    Raises:
        NotImplementedError: If the requested speed is not supported.
    """
    required_type, required_subtype, phy_mode, service_type = _client_speed_config(speed)
    port = g42_port_node(root, port_name)
    facilities = root.ioa_network_element_ne.facilities
    return [
        fragment(port, label=description, **_IN_SERVICE),
        fragment(
            port.tom,
            stage=1,
            label=description,
            required_type=required_type,
            required_subtype=required_subtype,
            phy_mode=PhyModeEnum(phy_mode),
            **_IN_SERVICE,
        ),
        fragment(
            facilities.trib_ptp(port_name),
            stage=2,
            label=description,
            service_type=ServiceTypeEnum(service_type),
            **_IN_SERVICE,
        ),
        fragment(
            facilities.ethernet(port_name),
            stage=3,
            label=description,
            fec_mode="enabled",
            loopback="none",
            test_signal_type=SignalTypeEnum.NONE,
            test_signal_direction="egress",
            test_signal_monitoring=False,
            lldp_admin_status=LldpAdminStatusEnum.RX_ONLY,
            lldp_ingress_mode=LldpModeEnum.SNOOP,
            lldp_egress_mode=LldpModeEnum.SNOOP,
            **_IN_SERVICE,
        ),
    ]


def render_tx_power(root: Any, line_port_name: str, tx_power: Decimal) -> list[Fragment]:
    """Render the transmit power of the optical carrier of a GX G42 line port."""
    carrier = root.ioa_network_element_ne.facilities.optical_carrier(f"{line_port_name}-1")
    return [fragment(carrier, tx_power=tx_power)]


def render_transponder_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
    *,
    circuit_identifier: str,
    allocate: bool,
) -> list[Fragment]:
    """Render the cross-connect between a client port and the line ports of a GX G42.

    A GX G42 cross-connect is created by an RPC, which names it and assigns its time
    slots: the existing one is rendered, and when there is none (``allocate``) it is
    created first. This is the one rendering that reads, and may change, the device.

    Args:
        optical_node_block: The Optical Node hosting the ports.
        client_port_name: The client port name.
        line_port_names: List of line port names.
        xconn_description: Optional description for the cross-connect.
        circuit_identifier: Circuit id suffix of the cross-connect: the id of the owner block.
        allocate: Whether to create the cross-connect when it does not exist yet.

    Returns:
        The desired configuration of the cross-connect; empty when there is none and
        ``allocate`` is false.

    Raises:
        ValueError: If the cross-connect cannot be created.
    """
    g42 = get_g42_client(optical_node_block)
    och_key = _derive_optical_channel_key(line_port_names)
    direction = "two-way"
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcon = _find_xcon(g42, client_port_name, och_key, direction, payload_type)
    if xcon is None and allocate:
        dst_parent_odu = f"{och_key}-ODUCni"
        _create_xcon(
            g42=g42,
            client=_client_path(client_port_name),
            dst_parent_odu=dst_parent_odu,
            direction=direction,
            payload_type=payload_type,
            label=xconn_description,
            circuit_identifier=circuit_identifier,
            dst_time_slots=_retrieve_time_slots(g42, dst_parent_odu, payload_type),
        )
        xcon = _find_xcon(g42, client_port_name, och_key, direction, payload_type)
        if xcon is None:
            msg = f"Unable to create XCON for client {client_port_name} on {_node_id(optical_node_block)}. "
            raise ValueError(msg)
    if xcon is None:
        return []
    node = g42.data.ioa_network_element_ne.services.xcon(xcon.name)
    return [fragment(node, label=xconn_description, circuit_id_suffix=circuit_identifier)]


def configure_line_transceivers(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Make the given GX G42 node run the line transceiver configuration; return the applied diff."""
    root = get_g42_client(optical_node_block).data
    fragments = render_line_transceivers(root, port_names, central_frequencies, modes, descriptions)
    return apply_config(optical_node_block, owner_instance_id, LINE_SCOPE, fragments)


def validate_trx_line(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
    *,
    owner_instance_id: UUID | str,
) -> None:
    """Check the line transceiver configuration of the given GX G42 node.

    Raises:
        ValueError: If the attributes are inconsistent or the device configuration differs.
    """
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)
    root = get_g42_client(optical_node_block).data
    fragments = render_line_transceivers(root, port_names, central_frequencies, modes, descriptions)
    verify_config(optical_node_block, owner_instance_id, LINE_SCOPE, fragments)


def factory_reset_transponder_lines(
    optical_node_block: NokiaGxG42BlockProvisioning,
    line_port_names: list[str],
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Release the line transceiver configuration of the given GX G42 node; return the applied diff.

    The super-channel is deleted and the ports and super-channel groups go back to their
    factory configuration, unless another owner still holds them. The transmit power
    recorded for the ports is forgotten: the optical carrier goes with the super-channel.
    """
    root = get_g42_client(optical_node_block).data
    facilities = root.ioa_network_element_ne.facilities
    rendered = [fragment(facilities.super_channel("_".join(line_port_names)), label="")]
    for name in line_port_names:
        rendered.append(fragment(g42_port_node(root, name), label="", admin_state="lock"))
        rendered.append(fragment(facilities.super_channel_group(name), label="", admin_state="lock"))
        forget_config(optical_node_block, owner_instance_id, TX_POWER_SCOPE.format(name))
    return release_config(optical_node_block, owner_instance_id, LINE_SCOPE, rendered)


def configure_transceiver_client(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Make the given GX G42 node run the client port configuration; return the applied diff."""
    fragments = render_transceiver_client(get_g42_client(optical_node_block).data, port_name, description, speed)
    return apply_config(optical_node_block, owner_instance_id, CLIENT_SCOPE.format(port_name), fragments)


def validate_trx_client(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
    *,
    owner_instance_id: UUID | str,
) -> None:
    """Check the client port configuration of the given GX G42 node.

    Raises:
        ValueError: If the device configuration differs.
    """
    fragments = render_transceiver_client(get_g42_client(optical_node_block).data, port_name, description, speed)
    verify_config(optical_node_block, owner_instance_id, CLIENT_SCOPE.format(port_name), fragments)


def factory_reset_transponder_client(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_name: str,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Release the client port configuration of the given GX G42 node; return the applied diff."""
    root = get_g42_client(optical_node_block).data
    port = g42_port_node(root, port_name)
    facilities = root.ioa_network_element_ne.facilities
    rendered = [
        fragment(node, label="", admin_state="lock")
        for node in (facilities.ethernet(port_name), facilities.trib_ptp(port_name), port.tom, port)
    ]
    return release_config(optical_node_block, owner_instance_id, CLIENT_SCOPE.format(port_name), rendered)


def configure_transponder_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Make the given GX G42 node run the client/line cross-connect; return the applied diff.

    Raises:
        ValueError: If the cross-connect cannot be created.
    """
    fragments = render_transponder_crossconnect(
        optical_node_block,
        client_port_name,
        line_port_names,
        xconn_description,
        circuit_identifier=str(owner_instance_id),
        allocate=True,
    )
    return apply_config(optical_node_block, owner_instance_id, CROSSCONNECT_SCOPE.format(client_port_name), fragments)


def validate_trx_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
    *,
    owner_instance_id: UUID | str,
) -> None:
    """Check the client/line cross-connect of the given GX G42 node.

    Raises:
        ValueError: If the cross-connect is missing or its configuration differs.
    """
    fragments = render_transponder_crossconnect(
        optical_node_block,
        client_port_name,
        line_port_names,
        xconn_description,
        circuit_identifier=str(owner_instance_id),
        allocate=False,
    )
    if not fragments:
        msg = (
            f"Cross-connect not found for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}. "
            "Please ensure the cross-connect exists and is correctly configured then retry."
        )
        raise ConfigDriftError(msg)
    verify_config(optical_node_block, owner_instance_id, CROSSCONNECT_SCOPE.format(client_port_name), fragments)


def delete_transponder_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Release the cross-connects of a client port of the given GX G42 node; return the applied diff.

    Besides the cross-connect recorded for the owner, every cross-connect found on the
    device for the client port is released, which covers the ones applied before they
    were recorded.
    """
    g42 = get_g42_client(optical_node_block)
    # An empty list reads as no data over NETCONF.
    xcons = g42.data.ioa_network_element_ne.services.xcon.retrieve(depth=2, content="config") or []
    found = [
        fragment(g42.data.ioa_network_element_ne.services.xcon(xcon.name), label=xcon.label or "")
        for xcon in xcons
        if _is_client_endpoint(xcon.source, client_port_name) or _is_client_endpoint(xcon.destination, client_port_name)
    ]
    return release_config(optical_node_block, owner_instance_id, CROSSCONNECT_SCOPE.format(client_port_name), found)


def align_tx_power_to_target(
    optical_node_block: NokiaGxG42BlockProvisioning,
    line_port_name: str,
    db_from_target: Decimal | float | str,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Subtract db_from_target decibels (dB) to the transmitted optical power of a GX G42 line port.

    The new power is applied and recorded like any other intended setting of the node.

    Args:
        optical_node_block: The Optical Node to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.
        owner_instance_id: ``subscription_instance_id`` of the product block the setting belongs to.

    Returns:
        The applied diff.

    Raises:
        ValueError: If no transmit power is configured on the line port.
    """
    db_from_target = _as_decimal(db_from_target)

    min_tx_power = Decimal("-6.00")
    max_tx_power = Decimal("9.00")

    root = get_g42_client(optical_node_block).data
    carrier = root.ioa_network_element_ne.facilities.optical_carrier(f"{line_port_name}-1")
    current_tx_power = _retrieve_required(carrier.retrieve, depth=2, content="config").tx_power
    if current_tx_power is None:
        msg = f"No transmit power configured on {_node_id(optical_node_block)} {line_port_name}"
        raise ValueError(msg)
    new_tx_power = max(min_tx_power, min(max_tx_power, round(_as_decimal(current_tx_power) - db_from_target, 2)))
    return apply_config(
        optical_node_block,
        owner_instance_id,
        TX_POWER_SCOPE.format(line_port_name),
        render_tx_power(root, line_port_name, new_tx_power),
    )
