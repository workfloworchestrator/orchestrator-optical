"""Nokia Groove G30 transponder operations: bandwidth, client/line config, cross-connects and validation.

The configuration is declarative (see :mod:`orchestrator.optical.hal.reconcile`): every
object has one ``render_*`` function returning its desired configuration, and the
configure / validate / factory-reset operations are that rendering applied, verified or
released. The rendering units (scopes) of an owner block on a node are ``line``,
``client:<port>``, ``crossconnect:<client port>`` and ``tx-power:<line port>``.
"""

from decimal import Decimal
from re import search
from typing import Any
from uuid import UUID

from orchestrator.optical.hal._common import _as_decimal, _node_id, _retrieve_required
from orchestrator.optical.hal.adapters.nokia_groove_g30._sdk import G30Client, PortModeEnum
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (
    g30_ids_from_port_name,
    g30_och_os_node,
    g30_port_node,
    get_g30_client,
)
from orchestrator.optical.hal.reconcile import (
    ConfigDriftError,
    Fragment,
    apply_config,
    forget_config,
    fragment,
    release_config,
    verify_config,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.utils.custom_types.frequencies import Frequency

#: Rendering units of the transponder configuration of an owner block on a node.
LINE_SCOPE = "line"
CLIENT_SCOPE = "client:{}"
CROSSCONNECT_SCOPE = "crossconnect:{}"
TX_POWER_SCOPE = "tx-power:{}"

#: The ODU of a Groove G30 client port cross-connected to a line.
_CLIENT_ODU = (
    "/ne:ne/shelf[shelf-id='{shelf}']/slot[slot-id='{slot}']/card/port[port-id='{port}']"
    "/{eth}/odu[odutype-L1='odu4'][oduid-L1='1'][odutype-L2='unused'][oduid-L2='0']"
    "[odutype-L3='unused'][oduid-L3='0'][odutype-L4='unused'][oduid-L4='0']"
)
#: Resolution of ``required-tx-optical-power`` (one fraction digit in the device model).
_TX_POWER_STEP = Decimal("0.1")
_OTU_KEYS = ("otuc2", "otuc3", "otuc4", "otuc5", "otuc6", "otuc7", "otuc9", "otuc11", "otu4", "otu2", "otu2e")
_ODU_KEYS = (
    "odutype_L1",
    "oduid_L1",
    "odutype_L2",
    "oduid_L2",
    "odutype_L3",
    "oduid_L3",
    "odutype_L4",
    "oduid_L4",
)


def _client_speed_config(speed: OpticalDigitalServiceSpeed) -> tuple[str, str, str]:
    """Map a digital service speed to the Groove G30 (port mode, ethernet service, FEC type)."""
    match speed:
        case OpticalDigitalServiceSpeed._100:  # noqa: SLF001
            return "100GBE", "eth100g", "auto"
        case OpticalDigitalServiceSpeed._400:  # noqa: SLF001
            return "400GBE", "eth400g", "enabled"
    msg = f"Unsupported speed {speed} for the Groove G30 client configuration"
    raise NotImplementedError(msg)


def _get_modulation_and_rate_from_mode(port_mode: str) -> tuple[str, str]:
    """Retrieve the modulation and rate class for a given port mode.

    Returns 'not-applicable' if not found or if the port mode has no coherent properties.
    """
    port_mode_map = {
        # PortMode: (ModulationFormat, RateClass)  # noqa: ERA001
        "QPSK_100G": ("DP-QPSK", "100G"),
        "8QAM_300G": ("DP-8QAM", "150G"),  # Note: Desc says 150G
        "16QAM_200G": ("DP-16QAM", "200G"),
        "OCHOS_OTU2": ("NRZ", "10G"),
        "OCHOS_OTU2e": ("NRZ", "11G"),
        "8QAM_200G": ("DP-8QAM", "200G"),
        "64QAM_600G": ("DP-64QAM", "600G"),
        "SPQPSK_100G": ("DP-SPQPSK", "100G"),
        "SPQPSK_QPSK_100G": ("DP-SPQPSK-QPSK", "100G"),
        "QPSK_200G": ("DP-QPSK", "200G"),
        "SP16QAM_200G": ("DP-SP16QAM", "200G"),
        "32QAM_200G": ("DP-32QAM", "200G"),
        "QPSK_SP16QAM_200G": ("DP-QPSK-SP16QAM", "200G"),
        "16QAM_300G": ("DP-16QAM", "300G"),
        "SP16QAM_300G": ("DP-SP16QAM", "300G"),
        "32QAM_300G": ("DP-32QAM", "300G"),
        "64QAM_300G": ("DP-64QAM", "300G"),
        "SP16QAM_16QAM_300G": ("DP-SP16QAM-16QAM", "300G"),
        "16QAM_400G": ("DP-16QAM", "400G"),
        "32QAM_400G": ("DP-32QAM", "400G"),
        "64QAM_400G": ("DP-64QAM", "400G"),
        "16QAM_32QAM_400G": ("DP-16QAM-32QAM", "400G"),
        "32QAM_500G": ("DP-32QAM", "500G"),
        "64QAM_500G": ("DP-64QAM", "500G"),
        "32QAM_64QAM_500G": ("DP-32QAM-64QAM", "500G"),
        "QPSK_100G_TRANSPARENT": ("DP-QPSK", "100G"),
        "SP16QAM_16QAM_200G": ("DP-SP16QAM-16QAM", "200G"),
        "32QAM_64QAM_600G": ("DP-32QAM-64QAM", "600G"),
        "SP16QAM_300G_C": ("DP-SP16QAM", "150G"),  # 2*150G
        "QPSK_SP16QAM_300G_C": ("DP-QPSK-SP16QAM", "150G"),
        "16QAM_32QAM_500G_C": ("DP-16QAM-32QAM", "250G"),  # 2*250G
        "16QAM_500G_C": ("DP-16QAM", "250G"),
        "SP16QAM_500G_C": ("DP-SP16QAM", "250G"),
        "QPSK_SP16QAM_500G_C": ("DP-QPSK-SP16QAM", "250G"),
        "32QAM_64QAM_700G_C": ("DP-32QAM-64QAM", "350G"),  # 2*350G
        "16QAM_700G_C": ("DP-16QAM", "350G"),
        "SP16QAM_16QAM_700G_C": ("DP-SP16QAM-16QAM", "350G"),
        "32QAM_900G_C": ("DP-32QAM", "450G"),  # 2*450G
        "16QAM_32QAM_900G_C": ("DP-16QAM-32QAM", "450G"),
        "32QAM_64QAM_1100G_C": ("DP-32QAM-64QAM", "550G"),  # 2*550G
        "SPQPSK_QPSK_200G": ("DP-SPQPSK-QPSK", "200G"),
        "QPSK_SP16QAM_300G": ("DP-QPSK-SP16QAM", "300G"),
        "SP16QAM_16QAM_400G": ("DP-SP16QAM-16QAM", "400G"),
        "16QAM_32QAM_500G": ("DP-16QAM-32QAM", "500G"),
    }
    # Use .get() to handle non-coherent modes like '100GBE' or 'not-applicable'
    return port_mode_map.get(port_mode, ("not-applicable", "not-applicable"))


def _extract_shelf_slot_port_ids_from_odu_string(
    odu_string: str,
) -> tuple[int, int, int]:
    """Extract the shelf, slot and port ids from a G30 ODU string."""
    shelf_match = search(r"shelf\[shelf-id='(\d+)'\]", odu_string)
    slot_match = search(r"slot\[slot-id='(\d+)'\]", odu_string)
    port_match = search(r"port\[port-id='(\d+)'\]", odu_string)

    if shelf_match is None or slot_match is None or port_match is None:
        msg = f"Could not extract the shelf, slot and port ids from ODU string: {odu_string}"
        raise ValueError(msg)

    return int(shelf_match.group(1)), int(slot_match.group(1)), int(port_match.group(1))


def get_signal_bandwidth(optical_node_block: NokiaGrooveG30BlockProvisioning, port_name: str) -> int:
    """Return the signal bandwidth, in MHz, of the Groove G30 transport channel on the given line port.

    Args:
        optical_node_block: The Groove G30 Optical Node hosting the line port.
        port_name: The line port name.

    Returns:
        The signal bandwidth in MHz.
    """
    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
    och_os = _retrieve_required(
        g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os.retrieve, depth=2, content="config"
    )
    if och_os.fec_type == "SDFEC27ND":
        bw = 75_000
    elif och_os.fec_type == "SDFEC15ND2":
        bw = 68_750
    else:
        bw = 37_500
    return bw


def render_line_transceivers(
    root: Any,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> list[Fragment]:
    """Render the line transceivers of a Groove G30: each line port and its optical channel.

    The optical channel (``och-os``) is created by the device once the port mode is set,
    so it is rendered one stage after its port.

    Args:
        root: The data root navigator of a Groove G30 client (``client.data``).
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Returns:
        The desired configuration of the line ports.
    """
    fragments: list[Fragment] = []
    for port_name, central_frequency, mode, description in zip(
        port_names, central_frequencies, modes, descriptions, strict=True
    ):
        port = g30_port_node(root, port_name)
        modulation, rate = _get_modulation_and_rate_from_mode(mode)
        fragments.append(fragment(port, port_mode=mode, service_label=description, admin_status="up"))
        fragments.append(
            fragment(
                g30_och_os_node(root, port_name),
                stage=1,
                modulation_format=modulation,
                rate_class=rate,
                frequency=central_frequency,
                rx_frequency=central_frequency,
                service_label=description,
                admin_status="up",
                laser_enable="enabled",
                loopback_enable="disabled",
                loopback_type="none",
            )
        )
    return fragments


def render_transceiver_client(
    root: Any,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> list[Fragment]:
    """Render a client port of a Groove G30 transponder: the port and its ethernet facility.

    The ethernet facility is created by the device once the port mode is set, so it is
    rendered one stage after its port.

    Args:
        root: The data root navigator of a Groove G30 client (``client.data``).
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Returns:
        The desired configuration of the client port.
    """
    port = g30_port_node(root, port_name)
    port_mode, eth_name, fec_type = _client_speed_config(speed)
    return [
        fragment(port, admin_status="up", service_label=description, port_mode=PortModeEnum(port_mode)),
        fragment(
            getattr(port, eth_name),
            stage=1,
            admin_status="up",
            service_label=description,
            loopback_enable="disabled",
            test_signal_enable="NONE",
            client_shutdown="no",
            eth_fec_type=fec_type,
        ),
    ]


def render_tx_power(root: Any, line_port_name: str, tx_power: Decimal) -> list[Fragment]:
    """Render the required transmit power of a Groove G30 line port."""
    return [fragment(g30_och_os_node(root, line_port_name), required_tx_optical_power=tx_power)]


def _free_line_odu(
    g30: G30Client,
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    shelf_id: int,
    slot_id: int,
    line_port_ids: list[int],
    used_odus: set[str],
) -> str:
    """Return the first ODU of the given line ports that no cross-connect uses."""
    possible_odus: list[tuple[int, str]] = []
    for line_port_id in line_port_ids:
        och_os = (
            g30.data.ne_ne.shelf(shelf_id)
            .slot(slot_id)
            .card.port(line_port_id)
            .och_os.retrieve(depth=4, content="config")
        )
        otu_key = next((f for f in _OTU_KEYS if getattr(och_os, f, None) is not None), None)
        if otu_key is None:
            msg = f"No OTU service found for line port {line_port_id} on {_node_id(optical_node_block)}"
            raise ValueError(msg)
        for odu in getattr(och_os, otu_key).odu:
            if any(getattr(odu, key, None) is None for key in _ODU_KEYS):
                continue
            if all(getattr(odu, key, None) != "odu4" for key in _ODU_KEYS):
                continue
            odu_string = (
                f"/ne:ne/shelf[shelf-id='{shelf_id}']/slot[slot-id='{slot_id}']/card/port"
                f"[port-id='{line_port_id}']/och-os/{otu_key}/odu[odutype-L1='{odu.odutype_L1}']"
                f"[oduid-L1='{odu.oduid_L1}'][odutype-L2='{odu.odutype_L2}'][oduid-L2='{odu.oduid_L2}']"
                f"[odutype-L3='{odu.odutype_L3}'][oduid-L3='{odu.oduid_L3}']"
                f"[odutype-L4='{odu.odutype_L4}'][oduid-L4='{odu.oduid_L4}']"
            )
            odu_index = int(line_port_id) * 10_000 + int(odu.oduid_L1) * 100 + int(odu.oduid_L2)
            possible_odus.append((odu_index, odu_string))

    available_odus = sorted(odu for odu in possible_odus if odu[1] not in used_odus)
    if not available_odus:
        msg = f"No available ODU for crossconnect on {_node_id(optical_node_block)}"
        raise ValueError(msg)
    return available_odus[0][1]


def render_transponder_crossconnect(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
    *,
    allocate: bool,
) -> list[Fragment]:
    """Render the cross-connect between a client port and the line ports of a Groove G30.

    The cross-connect is keyed by its two ODUs, which only the device knows: the one
    already connecting the client port to one of the line ports is kept, otherwise
    (``allocate``) the first free ODU of the line ports is taken. This is the one
    rendering that reads the device.

    Args:
        optical_node_block: The Optical Node hosting the ports.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).
        line_port_names: List of line port names.
        xconn_description: Optional description for the cross-connect.
        allocate: Whether to pick a free line ODU when no cross-connect exists yet.

    Returns:
        The desired configuration of the cross-connect; empty when there is none and
        ``allocate`` is false.

    Raises:
        ValueError: If the ports are not on the same card, the client port has no
            ethernet service, or no line ODU is free.
    """
    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, c_port_id, _ = g30_ids_from_port_name(client_port_name)

    line_port_ids = []
    for lpn in line_port_names:
        l_shelf_id, l_slot_id, _, line_port_id, _ = g30_ids_from_port_name(lpn)
        if shelf_id != l_shelf_id or slot_id != l_slot_id:
            msg = (
                f"Client and line ports should be on the same shelf and slot. Client: {client_port_name}, Line: {lpn}."
            )
            raise ValueError(msg)
        line_port_ids.append(line_port_id)

    client_port = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(c_port_id).retrieve(depth=3, content="config")
    eth_key = next((f for f in ("eth100g", "eth400g") if getattr(client_port, f, None) is not None), None)
    if not eth_key:
        msg = f"No eth service found on {_node_id(optical_node_block)} {client_port_name}"
        raise ValueError(msg)
    client_odu = _CLIENT_ODU.format(shelf=shelf_id, slot=slot_id, port=c_port_id, eth=eth_key)

    # An empty list reads as no data over NETCONF.
    crs = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config") or []
    for c in crs:
        if client_odu not in {c.src_tp, c.dst_tp}:
            continue
        line_odu = c.dst_tp if c.src_tp == client_odu else c.src_tp
        if _extract_shelf_slot_port_ids_from_odu_string(line_odu) in {(shelf_id, slot_id, i) for i in line_port_ids}:
            return [fragment(g30.data.ne_ne.services.CRS(c.src_tp, c.dst_tp), service_label=xconn_description)]

    if not allocate:
        return []
    used_odus = {tp for c in crs for tp in (c.src_tp, c.dst_tp)}
    line_odu = _free_line_odu(g30, optical_node_block, shelf_id, slot_id, line_port_ids, used_odus)
    return [fragment(g30.data.ne_ne.services.CRS(line_odu, client_odu), service_label=xconn_description)]


def configure_line_transceivers(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Make the given Groove G30 node run the line transceiver configuration; return the applied diff."""
    root = get_g30_client(optical_node_block).data
    fragments = render_line_transceivers(root, port_names, central_frequencies, modes, descriptions)
    return apply_config(optical_node_block, owner_instance_id, LINE_SCOPE, fragments)


def validate_trx_line(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
    *,
    owner_instance_id: UUID | str,
) -> None:
    """Check the line transceiver configuration of the given Groove G30 node.

    Raises:
        ValueError: If the attributes are inconsistent or the device configuration differs.
    """
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)
    if len(set(modes)) != 1:
        msg = f"All modes must be the same but got {modes}."
        raise ValueError(msg)
    root = get_g30_client(optical_node_block).data
    fragments = render_line_transceivers(root, port_names, central_frequencies, modes, descriptions)
    verify_config(optical_node_block, owner_instance_id, LINE_SCOPE, fragments)


def factory_reset_transponder_lines(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    line_port_names: list[str],
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Release the line transceiver configuration of the given Groove G30 node; return the applied diff.

    The line ports go back to their factory configuration unless another owner still
    holds them. The transmit power recorded for the ports is forgotten: the optical
    channel it belongs to goes with the port mode.
    """
    root = get_g30_client(optical_node_block).data
    rendered = [
        fragment(g30_port_node(root, name), port_mode="not-applicable", service_label="", admin_status="down")
        for name in line_port_names
    ]
    for name in line_port_names:
        forget_config(optical_node_block, owner_instance_id, TX_POWER_SCOPE.format(name))
    return release_config(optical_node_block, owner_instance_id, LINE_SCOPE, rendered)


def configure_transceiver_client(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Make the given Groove G30 node run the client port configuration; return the applied diff."""
    fragments = render_transceiver_client(get_g30_client(optical_node_block).data, port_name, description, speed)
    return apply_config(optical_node_block, owner_instance_id, CLIENT_SCOPE.format(port_name), fragments)


def validate_trx_client(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
    *,
    owner_instance_id: UUID | str,
) -> None:
    """Check the client port configuration of the given Groove G30 node.

    Raises:
        ValueError: If the device configuration differs.
    """
    fragments = render_transceiver_client(get_g30_client(optical_node_block).data, port_name, description, speed)
    verify_config(optical_node_block, owner_instance_id, CLIENT_SCOPE.format(port_name), fragments)


def factory_reset_transponder_client(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    port_name: str,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Release the client port configuration of the given Groove G30 node; return the applied diff."""
    port = g30_port_node(get_g30_client(optical_node_block).data, port_name)
    rendered = [fragment(port, port_mode="not-applicable", service_label="", admin_status="down")]
    return release_config(optical_node_block, owner_instance_id, CLIENT_SCOPE.format(port_name), rendered)


def configure_transponder_crossconnect(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Make the given Groove G30 node run the client/line cross-connect; return the applied diff.

    Raises:
        ValueError: If the cross-connect cannot be rendered.
    """
    fragments = render_transponder_crossconnect(
        optical_node_block, client_port_name, line_port_names, xconn_description, allocate=True
    )
    return apply_config(optical_node_block, owner_instance_id, CROSSCONNECT_SCOPE.format(client_port_name), fragments)


def validate_trx_crossconnect(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
    *,
    owner_instance_id: UUID | str,
) -> None:
    """Check the client/line cross-connect of the given Groove G30 node.

    Raises:
        ValueError: If the cross-connect is missing or its description does not match.
    """
    fragments = render_transponder_crossconnect(
        optical_node_block, client_port_name, line_port_names, xconn_description, allocate=False
    )
    if not fragments:
        msg = (
            f"Cross-connect not found for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}. "
            "Please ensure the cross-connect exists and is correctly configured then retry."
        )
        raise ConfigDriftError(msg)
    verify_config(optical_node_block, owner_instance_id, CROSSCONNECT_SCOPE.format(client_port_name), fragments)


def delete_transponder_crossconnect(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    client_port_name: str,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    """Release the cross-connects of a client port of the given Groove G30 node; return the applied diff.

    Besides the cross-connect recorded for the owner, every cross-connect found on the
    device for the client port is released, which covers the ones applied before they
    were recorded. ``CHM1`` cross-connects are not configurable: nothing is sent.

    Raises:
        ValueError: If the client port has no ethernet service.
    """
    scope = CROSSCONNECT_SCOPE.format(client_port_name)
    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(client_port_name)
    card_node = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card

    if _retrieve_required(card_node.retrieve, depth=2).required_type == "CHM1":
        forget_config(optical_node_block, owner_instance_id, scope)
        return {
            "message": (
                f"{_node_id(optical_node_block)} {client_port_name}: no need to delete any xcon,"
                " CHM1 crossconnections are not configurable."
            )
        }

    client_port = card_node.port(port_id).retrieve(depth=3, content="config")
    eth_key = next((f for f in ("eth100g", "eth400g") if getattr(client_port, f, None) is not None), None)
    if not eth_key:
        msg = (
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " This port does not have an ethernet service, it must have been deleted manually."
        )
        raise ValueError(msg)
    client_odu = _CLIENT_ODU.format(shelf=shelf_id, slot=slot_id, port=port_id, eth=eth_key)

    # An empty list reads as no data over NETCONF.
    crs = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config") or []
    found = [
        fragment(g30.data.ne_ne.services.CRS(c.src_tp, c.dst_tp), service_label=c.service_label or "")
        for c in crs
        if client_odu in {c.src_tp, c.dst_tp}
    ]
    return release_config(optical_node_block, owner_instance_id, scope, found)


def align_tx_power_to_target(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    line_port_name: str,
    db_from_target: Decimal | float | str,
    *,
    owner_instance_id: UUID | str,
) -> dict[str, Any]:
    r"""Subtract db_from_target decibels (dB) to the transmitted optical power.

    I.e. :math:`P^{new}_{tx} = P^{old}_{tx} - \Delta P`, where :math:`P^{old}_{tx}`
    is the currently configured required transmit power (``required-tx-optical-power``
    on G30), used as the baseline for the adjustment. The new power is applied and
    recorded like any other intended setting of the node.

    Args:
        optical_node_block: The Optical Node to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.
        owner_instance_id: ``subscription_instance_id`` of the product block the setting belongs to.

    Returns:
        The applied diff.

    Raises:
        ValueError: If no required transmit power is configured.
    """
    db_from_target = _as_decimal(db_from_target)

    min_tx_power = Decimal("-10.00")
    max_tx_power = Decimal("6.00")

    root = get_g30_client(optical_node_block).data
    och_os = _retrieve_required(g30_och_os_node(root, line_port_name).retrieve, content="config", depth=2)
    current_tx_power = och_os.required_tx_optical_power
    if current_tx_power is None:
        msg = f"No required transmit power configured on {_node_id(optical_node_block)} {line_port_name}"
        raise ValueError(msg)
    # The SDK reads the leaf as a float when the device reports its default.
    new_tx_power = max(min_tx_power, min(max_tx_power, _as_decimal(current_tx_power) - db_from_target))
    return apply_config(
        optical_node_block,
        owner_instance_id,
        TX_POWER_SCOPE.format(line_port_name),
        render_tx_power(root, line_port_name, new_tx_power.quantize(_TX_POWER_STEP)),
    )
