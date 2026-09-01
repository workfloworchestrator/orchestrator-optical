"""Nokia GX G42 transponder-level HAL operations."""

from decimal import Decimal
from typing import Any, Literal

from requests.exceptions import HTTPError

from orchestrator.optical.hal._common import _as_decimal, _node_id
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.services.nokia import G42Client
from orchestrator.optical.services.nokia.g42.data_models.ioa_network_element import (
    AdminStateEnum,
    AlarmReportControlEnum,
    EnableSwitchEnum,
    LldpAdminStatusEnum,
    LldpModeEnum,
    LoopbackEnum,
    PhyModeEnum,
    PrbsDirectionEnum,
    ServiceTypeEnum,
    SignalTypeEnum,
    XconItem,
)
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.utils.datadiff import compare_dicts, compare_pydantic_objects


def _client_speed_config(speed: OpticalDigitalServiceSpeed) -> tuple[str, str, str, str]:
    """Map a digital service speed to the GX G42 (required type, required subtype, phy mode, service type)."""
    match speed:
        case OpticalDigitalServiceSpeed._100:  # noqa: SLF001
            return "gx:QSFP28", "TOM-100G-Q", "100G", "100GBE"
        case OpticalDigitalServiceSpeed._400:  # noqa: SLF001
            return "gx:QSFPDD", "TOM-400G-Q-DR4", "400GE", "400GBE"
    msg = f"Unsupported speed {speed} for the GX G42 client configuration"
    raise NotImplementedError(msg)


def _find_xcon(
    g42: G42Client,
    client: str,
    line: str,
    direction: str,
    payload_type: str,
) -> XconItem | None:
    """Helper function to find an existing cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client: Source client path.
        line: Line ID inside the destination ODU string.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.

    Returns:
        The cross-connect configuration if found, otherwise None.

    Raises:
        ValueError: If a cross-connect with the same source and destination already exists.
    """
    try:
        xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            return None
        raise

    for xcon in xcons:
        source_destination_match = (xcon.source == client and line in xcon.destination) or (
            xcon.destination == client and line in xcon.source
        )
        payload_type_match = xcon.payload_type == payload_type
        direction_match = xcon.direction == direction
        if source_destination_match and payload_type_match and direction_match:
            return xcon

        if client in (xcon.source, xcon.destination):
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
        dst_time_slots: Time slots for the cross-connect.

    Raises:
        HTTPError: If the cross-connect creation fails.
    """
    try:
        g42.operations.create_xcon(
            payload_type=payload_type,
            direction=direction,
            label=label,
            circuit_id_suffix=label,
            source=client,
            dst_parent_odu=dst_parent_odu,
            dst_time_slots=dst_time_slots,
        )
    except HTTPError as e:
        xcon_already_exists_code = 412
        if e.response.status_code == xcon_already_exists_code:
            pass
        else:
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
    trib_ptp = g42.data.ne.facilities.trib_ptp(client_port_name).retrieve(depth=2, content="config")
    payload_type = trib_ptp.service_type

    if payload_type is None:
        msg = f"Unable to retrieve payload type for {g42.url} {client_port_name}"
        raise ValueError(msg)

    match payload_type:
        case ServiceTypeEnum("100GBE"):
            return "100GBE"
        case ServiceTypeEnum("400GBE"):
            return "400GBE"
    msg = f"Invalid payload type '{payload_type}' for {g42.url} {client_port_name}. Expected '100GBE' or '400GBE'."
    raise ValueError(msg)


def _retrieve_time_slots(g42: G42Client, odu_name: str, speed: Literal["100GBE", "400GBE"]) -> str:
    """Retrieve the first block of available time slots of the given ODU with enough capacity for the speed."""
    minimum_slots_required = 80 if speed == "100GBE" else 320

    odu = g42.data.ne.facilities.odu(odu_name).retrieve(depth=2)
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
        f"Not enough available time slots for {g42.url} {odu}. "
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
    channels = g42.data.ne.facilities.super_channel.retrieve(depth=2)
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


def configure_line_transceivers(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> dict[str, Any]:
    """Configure the line transceivers on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Returns:
        A dictionary of configuration diffs, keyed by port/facility name.

    Raises:
        ValueError: If the configuration is invalid.
    """
    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 transponder line configuration but got {modes}."
        raise ValueError(msg)

    g42 = get_g42_client(optical_node_block)
    configurations = {}

    # port
    for port_name, description in zip(port_names, descriptions, strict=True):
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        before = navigator.retrieve(content="config", depth=2)
        conf = before.model_copy(deep=True)
        conf.admin_state = AdminStateEnum.UNLOCK
        conf.label = description
        conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
        navigator.update(conf)
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"port-{port_name}"] = diffs

        # super-channel-group
        navigator = g42.data.ne.facilities.super_channel_group(port_name)
        before = navigator.retrieve(content="config", depth=2)
        navigator.update(name=port_name, admin_state="unlock", label=description, alarm_report_control="allowed")
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"super-channel-group-{port_name}"] = diffs

    # super-channel
    sup_ch_name = "_".join(port_names)
    navigator = g42.data.ne.facilities.super_channel(sup_ch_name)
    before = navigator.retrieve(content="config", depth=2)
    navigator.update(
        name=sup_ch_name,
        admin_state="unlock",
        label="+".join(descriptions),
        alarm_report_control="allowed",
        carrier_mode=modes[0],
        carriers=[f"{port_name}-1" for port_name in port_names],
    )
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["super-channel"] = diffs

    # optical-carrier
    for port_name, description, frequency in zip(port_names, descriptions, central_frequencies, strict=True):
        navigator = g42.data.ne.facilities.optical_carrier(f"{port_name}-1")
        before = navigator.retrieve(content="config", depth=2)
        navigator.update(
            name=f"{port_name}-1",
            admin_state="unlock",
            label=description,
            alarm_report_control="allowed",
            frequency=frequency,
        )
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"optical-carrier-{port_name}-1"] = diffs

    return configurations


def configure_transceiver_client(  # noqa: PLR0915
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> dict[str, Any]:
    """Configure the client port of a transceiver on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Returns:
        A dictionary of configuration diffs, keyed by facility name.

    Raises:
        NotImplementedError: If the requested speed is not supported.
        ValueError: If the configuration is invalid.
    """
    g42 = get_g42_client(optical_node_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
    required_type, required_subtype, phy_mode, service_type = _client_speed_config(speed)

    configurations = {}

    # port
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["1.port"] = diffs

    # TOM
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.required_type = required_type
    conf.required_subtype = required_subtype
    conf.phy_mode = PhyModeEnum(phy_mode)
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["2.tom"] = diffs

    # trib-ptp
    navigator = g42.data.ne.facilities.trib_ptp(port_name)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    conf.service_type = ServiceTypeEnum(service_type)
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["3.trib-ptp"] = diffs

    # ethernet
    navigator = g42.data.ne.facilities.ethernet(port_name)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    conf.fec_mode = EnableSwitchEnum.ENABLED
    conf.loopback = LoopbackEnum.NONE
    conf.test_signal_type = SignalTypeEnum.NONE
    conf.test_signal_direction = PrbsDirectionEnum.EGRESS
    conf.test_signal_monitoring = False
    conf.lldp_admin_status = LldpAdminStatusEnum.RX_ONLY
    conf.lldp_ingress_mode = LldpModeEnum.SNOOP
    conf.lldp_egress_mode = LldpModeEnum.SNOOP
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["4.ethernet"] = diffs

    return configurations


def configure_transponder_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    """Configure a cross-connect between client and line ports on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).
        line_port_names: List of line port names.
        xconn_description: Optional description for the cross-connect.

    Returns:
        The created cross-connect configuration.

    Raises:
        ValueError: If the cross-connect cannot be created.
    """
    g42 = get_g42_client(optical_node_block)

    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"
    och_key = _derive_optical_channel_key(line_port_names)
    dst_parent_odu = f"{och_key}-ODUCni"
    direction = "two-way"
    label = xconn_description
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcon = _find_xcon(g42, client, och_key, direction, payload_type)
    if xcon:
        endpoint = g42.data.ne.services.xcon(xcon.name)
        before = endpoint.retrieve(depth=2, content="config")
        xcon = before.model_copy(deep=True)
        xcon.label = label
        xcon.circuit_id_suffix = label
        endpoint.update(xcon)
        after = endpoint.retrieve(depth=2, content="config")
        return compare_pydantic_objects(before, after)

    dst_time_slots = _retrieve_time_slots(g42, dst_parent_odu, payload_type)
    _create_xcon(
        g42=g42,
        client=client,
        dst_parent_odu=dst_parent_odu,
        direction=direction,
        payload_type=payload_type,
        label=label,
        dst_time_slots=dst_time_slots,
    )
    xcon = _find_xcon(g42, client, och_key, direction, payload_type)
    if xcon:
        return xcon.model_dump(exclude_unset=True)

    msg = f"Unable to create XCON for client {client_port_name} on {_node_id(optical_node_block)}. "
    raise ValueError(msg)


def delete_transponder_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
) -> dict[str, Any]:
    """Delete a cross-connect between client and line ports on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node (transponder) to configure.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).

    Returns:
        A dictionary with a ``"message"`` and the list of deleted cross-connects.
    """
    result = {"message": "", "deleted_xcon": []}

    g42 = get_g42_client(optical_node_block)
    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"

    try:
        xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            xcons = []
        else:
            raise

    deleted_xcons = []
    for xcon in xcons:
        if client in (xcon.source, xcon.destination):
            uri = g42.data.ne.services.xcon(xcon.name)
            uri.delete()
            deleted_xcons.append(xcon)

    if not deleted_xcons:
        result["message"] = (
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " There was no cross-connection associated to this client port in the configuration."
        )
        return result

    result["deleted_xcon"] = deleted_xcons
    return result


def factory_reset_transponder_client(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_name: str,
) -> dict[str, Any]:
    """Factory reset the client port configuration of the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to reset.
        port_name: The client port name.

    Returns:
        The reset configuration.
    """
    g42 = get_g42_client(optical_node_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    configurations = {}

    # 1. Ethernet configuration
    navigator = g42.data.ne.facilities.ethernet(port_name)
    conf = navigator.retrieve(content="config", depth=2)
    navigator.update(name=port_name, admin_state="lock", label="")
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["1.ethernet"] = diff

    # 2. Tributary point-to-point configuration
    navigator = g42.data.ne.facilities.trib_ptp(port_name)
    conf = navigator.retrieve(content="config", depth=2)
    navigator.update(name=port_name, label="", admin_state="lock")
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["2.trib-ptp"] = diff

    # 3. TOM configuration
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    conf = navigator.retrieve(content="config", depth=2)
    updated_conf = conf.model_copy(deep=True)
    updated_conf.label = ""
    updated_conf.admin_state = AdminStateEnum.LOCK
    navigator.update(updated_conf)
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["3.tom"] = diff

    # 4. Port configuration
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = navigator.retrieve(content="config", depth=2)
    updated_conf = conf.model_copy(deep=True)
    updated_conf.label = ""
    updated_conf.admin_state = AdminStateEnum.LOCK
    navigator.update(updated_conf)
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["4.port"] = diff

    return configurations


def factory_reset_transponder_lines(
    optical_node_block: NokiaGxG42BlockProvisioning,
    line_port_names: list[str],
) -> dict[str, Any]:
    """Factory reset the transponder line configuration of the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to reset.
        line_port_names: The line port names.

    Returns:
        The reset configuration.
    """
    g42 = get_g42_client(optical_node_block)
    configurations = {}

    for port_name in line_port_names:
        # port
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        before = navigator.retrieve(content="config", depth=2)
        conf = before.model_copy(deep=True)
        conf.admin_state = AdminStateEnum.LOCK
        conf.label = ""
        conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
        navigator.update(conf)
        after = navigator.retrieve(content="config", depth=2)
        diff = compare_pydantic_objects(before, after)
        configurations[f"port-{port_name}"] = diff

        # super-channel-group
        navigator = g42.data.ne.facilities.super_channel_group(port_name)
        before = navigator.retrieve(depth=2, content="config")
        navigator.update(name=port_name, admin_state="lock", label="", alarm_report_control="allowed")
        after = navigator.retrieve(depth=2, content="config")
        diff = compare_pydantic_objects(before, after)
        configurations[f"super-channel-group-{port_name}"] = diff

    # super-channel
    sup_ch_name = "_".join(line_port_names)
    navigator = g42.data.ne.facilities.super_channel(sup_ch_name)
    before = navigator.retrieve(depth=2, content="config")
    navigator.delete()
    configurations[f"super-channel-{sup_ch_name}"] = compare_pydantic_objects(before, None)

    return configurations


def validate_trx_line(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    """Validate the transceiver line configuration on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Raises:
        ValueError: If the configuration is invalid.
    """
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)

    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 validation but got {modes}."
        raise ValueError(msg)

    g42 = get_g42_client(optical_node_block)

    actual_config: dict[str, Any] = {
        "ports": {},
        "super-channel-groups": {},
        "optical-carriers": {},
        "super-channel": {},
    }

    desired_config: dict[str, Any] = {
        "ports": {},
        "super-channel-groups": {},
        "optical-carriers": {},
        "super-channel": {},
    }

    for port_name, central_frequency, description in zip(
        port_names,
        central_frequencies,
        descriptions,
        strict=False,
    ):
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        actual_config["ports"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

        endpoint = g42.data.ne.facilities.super_channel_group(port_name)
        actual_config["super-channel-groups"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(
            exclude_unset=True
        )

        endpoint = g42.data.ne.facilities.optical_carrier(f"{port_name}-1")
        actual_config["optical-carriers"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(
            exclude_unset=True
        )

        desired_config["ports"][port_name] = {
            "name": port_id,
            "label": description,
            "admin-state": "unlock",
            "alarm-report-control": "allowed",
        }
        desired_config["super-channel-groups"][port_name] = {
            "name": f"{shelf_id}-{slot_id}-{port_id}",
            "label": description,
            "admin-state": "unlock",
            "line-system-mode": "openwave",
            "alarm-report-control": "allowed",
        }
        desired_config["optical-carriers"][port_name] = {
            "name": f"{shelf_id}-{slot_id}-{port_id}-1",
            "label": description,
            "tx-cd": "0.00",
            "frequency": str(central_frequency),
            "admin-state": "unlock",
            "frequency-offset": 0,
            "alarm-report-control": "allowed",
        }

    super_channel_name = "_".join(port_names)
    endpoint = g42.data.ne.facilities.super_channel(super_channel_name)
    actual_config["super-channel"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

    carriers = [f"{port_name}-1" for port_name in port_names]
    desired_config["super-channel"] = {
        "name": super_channel_name,
        "label": "+".join(descriptions),
        "carriers": carriers,
        "admin-state": "unlock",
        "carrier-mode": modes[0],
        "alarm-report-control": "allowed",
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {port_names}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def validate_trx_client(
    optical_node_block: NokiaGxG42BlockProvisioning,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> None:
    """Validate the transceiver client configuration on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Raises:
        ValueError: If the configuration is invalid.
    """
    g42 = get_g42_client(optical_node_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    required_type, required_subtype, phy_mode, service_type = _client_speed_config(speed)

    actual_config = {}
    # port
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    actual_config["port"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # TOM
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    actual_config["tom"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # trib-ptp
    endpoint = g42.data.ne.facilities.trib_ptp(port_name)
    actual_config["trib-ptp"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # ethernet
    endpoint = g42.data.ne.facilities.ethernet(port_name)
    actual_config["ethernet"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

    desired_config = {
        "tom": {
            "label": description,
            "phy-mode": phy_mode,
            "admin-state": "unlock",
            "required-type": required_type,
            "required-subtype": required_subtype,
            "alarm-report-control": "allowed",
        },
        "port": {
            "label": description,
            "admin-state": "unlock",
            "alarm-report-control": "allowed",
        },
        "trib-ptp": {
            "label": description,
            "admin-state": "unlock",
            "service-type": service_type,
            "alarm-report-control": "allowed",
        },
        "ethernet": {
            "label": description,
            "fec-mode": "enabled",
            "loopback": "none",
            "admin-state": "unlock",
            "lldp-egress-mode": "snoop",
            "test-signal-type": "none",
            "lldp-admin-status": "rx-only",
            "lldp-ingress-mode": "snoop",
            "alarm-report-control": "allowed",
            "test-signal-direction": "egress",
            "test-signal-monitoring": False,
        },
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {port_name}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def validate_trx_crossconnect(
    optical_node_block: NokiaGxG42BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    """Validate the transponder cross-connect configuration on the given GX G42 Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        client_port_name: The client port name.
        line_port_names: The line port names.
        xconn_description: The description of the cross-connect.

    Raises:
        ValueError: If the configuration is invalid.
    """
    g42 = get_g42_client(optical_node_block)

    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"
    och_key = _derive_optical_channel_key(line_port_names)
    direction = "two-way"
    label = xconn_description
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")

    actual_config = None
    for xcon in xcons:
        if (xcon.source == client and och_key in xcon.destination) or (
            xcon.destination == client and och_key in xcon.source
        ):
            actual_config = xcon.model_dump(exclude_unset=True)
            break

    if actual_config is None:
        msg = (
            f"Cross-connect not found for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}. "
            "Please ensure the cross-connect exists and is correctly configured then retry."
        )
        raise ValueError(msg)

    desired_config = {
        "label": label,
        "direction": direction,
        "payload-type": payload_type,
        "circuit-id-suffix": label,
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def align_tx_power_to_target(
    optical_node_block: NokiaGxG42BlockProvisioning,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, Any]:
    """Subtract db_from_target decibels (dB) to the transmitted optical power of a GX G42 line port.

    Args:
        optical_node_block: The Optical Node to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.

    Returns:
        A dictionary indicating the old and new required transmit power.

    Raises:
        ValueError: If no transmit power is configured on the line port.
    """
    db_from_target = _as_decimal(db_from_target)

    min_tx_power = Decimal("-6.00")
    max_tx_power = Decimal("9.00")

    g42 = get_g42_client(optical_node_block)
    uri = g42.data.ne.facilities.optical_carrier(f"{line_port_name}-1")
    conf = uri.retrieve(depth=2, content="config")
    current_tx_power = conf.tx_power
    if current_tx_power is None:
        msg = f"No transmit power configured on {_node_id(optical_node_block)} {line_port_name}"
        raise ValueError(msg)
    new_tx_power = round(current_tx_power - db_from_target, 2)
    new_tx_power = min(max_tx_power, new_tx_power)
    new_tx_power = max(min_tx_power, new_tx_power)
    new_conf = conf.model_copy(deep=True)
    new_conf.tx_power = new_tx_power
    uri.update(new_conf)
    return compare_pydantic_objects(conf, new_conf)
