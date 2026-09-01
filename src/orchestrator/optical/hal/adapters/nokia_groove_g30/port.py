"""Nokia Groove G30 port operations: discovery, description, admin state, termination and checks."""

import json
from decimal import Decimal
from typing import Any, Literal

from orchestrator.optical.hal._common import _node_id, _port_name
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (
    g30_ids_from_port_name,
    g30_port_navigator_node_from_port_name,
    get_g30_client,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning
from orchestrator.optical.services.nokia.g30.data_models.ne import (
    AdminStatusEnum,
    CardTypeEnum,
    ControlModeEnum,
    EnableSwitchEnum,
    GainRangeControlEnum,
    GainRangeTypeEnum,
    PortModeEnum,
    TiltControlModeEnum,
    YesNoEnum,
)


def get_device_ports_names(optical_node_block: NokiaGrooveG30BlockProvisioning) -> list[str]:
    """Return the aliases of all the ports of a Groove G30 node."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    ports_name: list[str] = []
    max_slot_id_with_useful_ports = 4
    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            ports_name.extend(p.alias_name for p in (slot.card.port or []) if p.alias_name is not None)

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                for port in subslot.subcard.port or []:
                    if port.alias_name is not None:
                        ports_name.append(port.alias_name)
                    if port.subport:
                        ports_name.extend(sp.alias_name for sp in port.subport if sp.alias_name is not None)

    return ports_name


def get_device_client_ports_names(optical_node_block: NokiaGrooveG30BlockProvisioning) -> list[str]:
    """Return the aliases of the client ports of a Groove G30 node."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    ports_name: list[str] = []
    max_slot_id_with_useful_ports = 4

    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            for port in slot.card.port or []:
                is_sub_interface = "." in (port.alias_name or "")
                is_in_client_range = 3 <= port.port_id <= 12  # noqa: PLR2004

                if (is_sub_interface or is_in_client_range) and port.alias_name is not None:
                    ports_name.append(port.alias_name)

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                for port in subslot.subcard.port or []:
                    if port.alias_name is not None:
                        ports_name.append(port.alias_name)
                    if port.subport:
                        ports_name.extend(sp.alias_name for sp in port.subport if sp.alias_name is not None)

    return ports_name


def get_device_line_ports_names(optical_node_block: NokiaGrooveG30BlockProvisioning) -> list[str]:
    """Return the aliases of the line ports of a Groove G30 node."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=5, content="config")

    ports_name: list[str] = []
    max_slot_id_with_useful_ports = 4

    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > max_slot_id_with_useful_ports or not slot.card:
                continue

            for port in slot.card.port or []:
                is_in_line_range = 1 <= (port.port_id or 999) <= 2  # noqa: PLR2004

                if is_in_line_range and port.alias_name is not None:
                    ports_name.append(port.alias_name)

    return ports_name


def retrieve_transceiver_modes(optical_node_block: NokiaGrooveG30BlockProvisioning, port_name: str) -> list[str]:
    """Return the supported transceiver modes of a Groove G30 line port."""
    # fmt: off
    mapping = {
        CardTypeEnum.CHM1: [
            "not-applicable",      "QPSK_100G",          "16QAM_200G",          "8QAM_300G",
        ],
        CardTypeEnum.CHM2T: [
            "16QAM_200G",          "16QAM_300G",         "16QAM_32QAM_400G",    "16QAM_32QAM_500G",
            "16QAM_400G",          "32QAM_200G",          "32QAM_300G",          "32QAM_400G",
            "32QAM_500G",          "32QAM_64QAM_500G",    "32QAM_64QAM_600G",    "64QAM_300G",
            "64QAM_400G",          "64QAM_500G",          "64QAM_600G",          "QPSK_100G",
            "QPSK_200G",           "QPSK_SP16QAM_200G",   "QPSK_SP16QAM_300G",   "SP16QAM_16QAM_200G",
            "SP16QAM_16QAM_300G",  "SP16QAM_16QAM_400G",  "SP16QAM_200G",        "SP16QAM_300G",
            "SPQPSK_100G",         "SPQPSK_QPSK_100G",    "SPQPSK_QPSK_200G",    "not-applicable",
        ],
    }
    # fmt: on

    shelf_id, slot_id, _, _, _ = g30_ids_from_port_name(port_name)

    g30 = get_g30_client(optical_node_block)

    card = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.retrieve(depth=2)

    card_type = card.required_type

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


def set_port_description(
    port_block: AnyOpticalPortBlockProvisioning,
    port_description: str,
) -> dict[str, Any]:
    """Set the description of a Groove G30 optical port.

    Args:
        port_block: Optical Port of which the description is to be set.
        port_description: The description to set on the port.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = port_block.optical_port_host_node
    port_name = _port_name(port_block)
    endpoint, _, _, _, _, _ = g30_port_navigator_node_from_port_name(host_node, port_name)
    endpoint.update(service_label=port_description)
    return endpoint.retrieve(content="config", depth=2).model_dump()


def set_channel_description(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    facility_id: str,
    description: str,
) -> dict[str, Any]:
    """Set the description of a Groove G30 optical channel.

    Args:
        optical_node_block: Optical Node of which the optical channel is to be modified.
        facility_id: The id of the optical channel to set the description on (e.g. ``"1/1/1"``).
        description: The description to set on the channel.

    Returns:
        The channel configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(facility_id)
    uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os

    och_os = uri.retrieve(content="config", depth=2)
    och_os.service_label = description
    uri.update(och_os)

    return uri.retrieve(content="config", depth=2).model_dump()


def set_port_admin_state(
    port_block: AnyOpticalPortBlockProvisioning,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Set the administrative state of a Groove G30 optical port.

    Args:
        port_block: Optical Port of which the admin state is to be set.
        admin_state: The administrative state to set on the port: ["up", "down", "maintenance"].

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = port_block.optical_port_host_node
    port_name = _port_name(port_block)
    mapping = {
        "up": AdminStatusEnum.UP,
        "down": AdminStatusEnum.DOWN,
        "maintenance": AdminStatusEnum.UP_NO_ALM,
    }
    status = mapping[admin_state]

    port_uri = g30_port_navigator_node_from_port_name(host_node, port_name)[0]

    port_uri.update(admin_status=status)
    return port_uri.retrieve(depth=2, content="config").model_dump()


def configure_termination(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> dict[str, Any]:
    """Configure a Groove G30 port when attaching a fiber to it."""
    host_node = optical_port_block.optical_port_host_node
    remote_host_node = remote_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    remote_port_name = _port_name(remote_port_block)

    endpoint, shelf_id, slot_id, subslot_id, port_id, _ = g30_port_navigator_node_from_port_name(host_node, port_name)

    match (
        remote_host_node.management.optical_module_node_vendor,
        remote_host_node.management.optical_module_node_platform,
    ):
        case (Vendor.NOKIA, Platform.FLEXILS):
            endpoint.update(
                external_connectivity=YesNoEnum.YES,
                connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
                admin_status=AdminStatusEnum.UP,
            )
            return endpoint.retrieve(depth=2, content="config").model_dump()
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            is_same_device = _same_node(host_node, remote_host_node)
            is_amplifier_port = slot_id == 3 and subslot_id == 3 and port_id == 1  # noqa: PLR2004

            if is_same_device:
                endpoint.update(
                    external_connectivity=YesNoEnum.NO,
                    connected_to=f"patched to {remote_port_name}",
                    admin_status=AdminStatusEnum.UP,
                )
                return endpoint.retrieve(depth=2, content="config").model_dump()

            if not is_amplifier_port:
                endpoint.update(
                    external_connectivity=YesNoEnum.YES,
                    connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
                    admin_status=AdminStatusEnum.UP,
                )
                return endpoint.retrieve(depth=2, content="config").model_dump()

            # link H4: the port is an amplifier port of a different Groove G30 device
            if subslot_id is None:
                msg = "Amplifier port configuration requires a subslot id"
                raise ValueError(msg)

            g30 = get_g30_client(host_node)

            booster_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(2).subcard.amplifier("ba")
            booster = booster_uri.retrieve(content="config", depth=2)
            booster.admin_status = AdminStatusEnum.UP
            booster.amplifier_enable = EnableSwitchEnum.ENABLED
            booster.input_los_shutdown = EnableSwitchEnum.DISABLED
            booster.control_mode = ControlModeEnum.MANUAL
            booster.gain_range_control = GainRangeControlEnum.MANUAL
            booster.target_gain_range = GainRangeTypeEnum.STANDARD
            booster.target_gain = Decimal("22.0")
            booster.output_voa = Decimal("10.0")
            booster.tilt_control_mode = TiltControlModeEnum.MANUAL
            booster.gain_tilt = Decimal("0.0")
            booster_uri.update(booster)

            preamp_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.subslot(subslot_id).subcard.amplifier("pa")
            preamp = preamp_uri.retrieve(content="config", depth=2)
            preamp.admin_status = AdminStatusEnum.UP
            preamp.amplifier_enable = EnableSwitchEnum.ENABLED
            preamp.input_los_shutdown = EnableSwitchEnum.DISABLED
            preamp.control_mode = ControlModeEnum.AUTO
            preamp.gain_range_control = GainRangeControlEnum.AUTO
            preamp.target_gain_range = GainRangeTypeEnum.STANDARD
            preamp.tilt_control_mode = TiltControlModeEnum.AUTO
            preamp_uri.update(preamp)

            endpoint.update(
                external_connectivity=YesNoEnum.YES,
                connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
                admin_status=AdminStatusEnum.UP,
            )

            return {
                "port": endpoint.retrieve(depth=2, content="config").model_dump(),
                "booster": booster_uri.retrieve(depth=2, content="config").model_dump(),
                "preamp": preamp_uri.retrieve(depth=2, content="config").model_dump(),
            }
        case _:
            msg = (
                "Unsupported remote optical device platform when configuring Groove G30 remote port: "
                f"{type(remote_host_node).__name__}"
            )
            raise ValueError(msg)


def factory_reset(optical_port_block: AnyOpticalPortBlockProvisioning) -> dict[str, Any]:
    """Prune the configuration of a Groove G30 port."""
    host_node = optical_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    port_uri = g30_port_navigator_node_from_port_name(host_node, port_name)[0]

    if "." in port_name:  # inside OCC2 card
        port_uri.update(connected_to="")
    else:
        port_uri.update(
            external_connectivity=YesNoEnum.NO,
            connected_to="",
            admin_status=AdminStatusEnum.DOWN,
            port_mode=PortModeEnum.NOT_APPLICABLE,
            service_label="",
        )

    return port_uri.retrieve(content="config", depth=2).model_dump()


def check_fiber(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> None:
    """Check if a Groove G30 port attached to a fiber is correctly configured."""
    host_node = optical_port_block.optical_port_host_node
    remote_host_node = remote_port_block.optical_port_host_node
    port_name = _port_name(optical_port_block)
    endpoint = g30_port_navigator_node_from_port_name(host_node, port_name)[0]
    port_data = endpoint.retrieve(depth=2)

    if (
        remote_host_node.management.optical_module_node_vendor,
        remote_host_node.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.GROOVE_G30) and _same_node(host_node, remote_host_node):
        con_to_string = f"patched to {_port_name(remote_port_block)}"
        ext_connectivity = YesNoEnum.NO
    else:
        con_to_string = f"{_node_id(remote_host_node)} {_port_name(remote_port_block)}"
        ext_connectivity = YesNoEnum.YES

    checks = (
        port_data.admin_status == AdminStatusEnum.UP
        and port_data.external_connectivity == ext_connectivity
        and port_data.connected_to == con_to_string
    )

    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": _node_id(host_node),
                    "port_name": port_name,
                    "expected": {
                        "admin-status": "up",
                        "external-connectivity": ext_connectivity.value,
                        "connected-to": con_to_string,
                    },
                    "actual": {
                        "admin-status": port_data.admin_status,
                        "external-connectivity": port_data.external_connectivity,
                        "connected-to": port_data.connected_to,
                    },
                },
                indent=4,
            )
        )


def _same_node(
    node_a: AnyOpticalNodeBlockProvisioningUnion,
    node_b: AnyOpticalNodeBlockProvisioningUnion,
) -> bool:
    """Return whether two Optical Node blocks refer to the same device."""
    if node_a is node_b:
        return True
    fqdn_a = node_a.management.optical_module_node_fqdn
    fqdn_b = node_b.management.optical_module_node_fqdn
    return fqdn_a is not None and fqdn_a == fqdn_b
