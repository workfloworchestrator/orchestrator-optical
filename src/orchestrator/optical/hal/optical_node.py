"""Services for Optical Nodes.

This module provides the discovery logic used when creating a Nokia FlexILS
Optical Node subscription: it connects to the node (directly through its
management IPs or, for subtended network elements (SNE), through the closest
Gateway Network Element (GNE)) and retrieves the node properties that cannot
be known upfront: the target id, the node role and the software version.

It also provides the vendor dispatch helper (``vendor_of``) and the client
retrieval, retrieval and validation services for the Optical Node product
blocks of all the supported vendors.
"""

import ipaddress
import json
from math import cos, radians, sin
from typing import Any, ClassVar, cast

from pydantic_forms.types import strEnum
from structlog import get_logger

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import location_block_from_subscription, subscription_instances_by_block_type
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30Block,
    NokiaGrooveG30BlockInactive,
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import (
    NokiaGxG42Block,
    NokiaGxG42BlockInactive,
    NokiaGxG42BlockProvisioning,
)
from orchestrator.optical.services.nokia import G30Client, G42Client
from orchestrator.optical.services.nokia.flexils.client import FlexilsClient
from orchestrator.optical.utils.custom_types.frequencies import available_to_used_passbands
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.utils.datadiff import compare_pydantic_objects

logger = get_logger(__name__)

Vector = tuple[float, float, float]

_MAX_GNE_CANDIDATES = 7


class FlexilsGneProvider:
    """Provide the Gateway Network Element (GNE) nodes to reach subtended FlexILS nodes.

    The GNE candidates are the already-created NokiaFlexIlsBlock subscriptions that
    carry at least one management IP and a known location. Distances are computed on
    the great-circle approximation of the unit sphere, so the closest GNEs can be
    tried first when a node cannot be reached directly.
    """

    _tid_ip_xyz_of_gnes: ClassVar[list[tuple[str, str, Vector]]] = []

    @classmethod
    def _initialize_cache(cls) -> None:
        """Populate the GNE cache from the NokiaFlexIlsBlock subscriptions in the database."""
        instances = subscription_instances_by_block_type("NokiaFlexIlsBlock", [SubscriptionLifecycle.ACTIVE])

        gnes: list[tuple[str, str, Vector]] = []
        for instance in instances:
            try:
                block = NokiaFlexIlsBlock.from_db(instance.subscription_instance_id)
            except Exception:  # noqa: BLE001
                logger.warning(
                    "Skipping unreadable NokiaFlexIlsBlock while building GNE cache",
                    subscription_instance_id=str(instance.subscription_instance_id),
                )
                continue

            management_ips = block.optical_management_ip if block.optical_management_ip else block.optical_loopback_ip
            if not management_ips:
                continue

            location = block.location
            if location is None or location.latitude is None or location.longitude is None:
                continue

            try:
                lat = radians(float(location.latitude))
                lon = radians(float(location.longitude))
            except (TypeError, ValueError):
                logger.warning(
                    "Skipping NokiaFlexIlsBlock with invalid location coordinates",
                    subscription_instance_id=str(instance.subscription_instance_id),
                    latitude=location.latitude,
                    longitude=location.longitude,
                )
                continue

            cos_lat = cos(lat)
            vector = (cos_lat * cos(lon), cos_lat * sin(lon), sin(lat))
            gnes.append((block.pqdn, management_ips[0], vector))

        cls._tid_ip_xyz_of_gnes = gnes
        logger.debug("Initialized FlexilsGneProvider cache", gnes=[tid for tid, _, _ in gnes])

    @classmethod
    def find_closest_gnes(cls, latitude: float, longitude: float) -> list[tuple[str, str]]:
        """Return the (tid, management ip) pairs of the closest GNE nodes to the given coordinates.

        Args:
            latitude: Latitude of the target location in degrees.
            longitude: Longitude of the target location in degrees.

        Returns:
            List of (tid, management ip) tuples ordered from closest to farthest.
            Empty list if no GNE nodes are known.
        """
        if not cls._tid_ip_xyz_of_gnes:
            cls._initialize_cache()

        if not cls._tid_ip_xyz_of_gnes:
            return []

        lat = radians(latitude)
        lon = radians(longitude)
        cos_lat = cos(lat)
        target_vector = (cos_lat * cos(lon), cos_lat * sin(lon), sin(lat))

        def dot_product(candidate: Vector) -> float:
            return target_vector[0] * candidate[0] + target_vector[1] * candidate[1] + target_vector[2] * candidate[2]

        ordered = sorted(cls._tid_ip_xyz_of_gnes, key=lambda item: dot_product(item[2]), reverse=True)
        return [(tid, ip) for tid, ip, _ in ordered[:_MAX_GNE_CANDIDATES]]


def _record_value(record: dict[str, Any], key: str) -> str | None:
    """Extract a single string value from a parsed TL1 record, defensively."""
    value = record.get(key)
    if value is None:
        return None
    if isinstance(value, list):
        value = value[0] if value else None
    if value is None:
        return None
    return str(value).strip()


def _find_node_entry(
    flex: FlexilsClient,
    tid: str | None,
    optical_flexils_gmpls_id: IPAddress | None,
) -> dict[str, Any]:
    """Find the RTRV-TOPONODE entry of the node we are trying to create."""
    flex = cast(Any, flex)  # the TL1 command methods are bound dynamically by the client
    response = flex.rtrv_toponode()
    records = response.parsed_data

    if optical_flexils_gmpls_id is not None:
        gmpls_id = str(optical_flexils_gmpls_id).strip()
        for record in records:
            if _record_value(record, "ROUTERID") == gmpls_id:
                return record
        msg = f"Node with GMPLS ID {gmpls_id} not found in RTRV-TOPONODE on {flex.gne_ip}"
        raise ValueError(msg)

    if tid is not None:
        for record in records:
            if _record_value(record, "NENAME") == tid:
                return record
        for record in records:
            name = _record_value(record, "NENAME")
            if name is not None and tid in name:
                return record
        msg = f"Node {tid} not found in RTRV-TOPONODE on {flex.gne_ip}"
        raise ValueError(msg)

    msg = "Cannot identify the node: provide at least one management IP or a GMPLS ID"
    raise ValueError(msg)


def _retrieve_node_properties(flex: FlexilsClient, target_id: str) -> tuple[OpticalNodeRole, str]:
    """Retrieve the node role and software version of the node with the given target id."""
    flex = cast(Any, flex)  # the TL1 command methods are bound dynamically by the client
    # NETYPE values reported by RTRV-SYS mapped to the OpticalNodeRole.
    netype_to_role: dict[str, OpticalNodeRole] = {
        "ROADM": OpticalNodeRole.ROADM,
        "OLA": OpticalNodeRole.AMPLIFIER,
        "OA": OpticalNodeRole.AMPLIFIER,
    }

    response = flex.rtrv_sys(tid=target_id)
    records = response.parsed_data
    if not records:
        msg = f"RTRV-SYS returned no data for node {target_id}"
        raise ValueError(msg)

    sys_record = records[0]

    netype = _record_value(sys_record, "NETYPE")
    role = netype_to_role.get(netype or "")
    if role is None:
        msg = f"RTRV-SYS returned unknown NETYPE {netype!r} for node {target_id}"
        raise ValueError(msg)

    software_version = _record_value(sys_record, "SWVERSION")
    if software_version is None:
        msg = f"RTRV-SYS did not report a software version for node {target_id}"
        raise ValueError(msg)

    return role, software_version


def _discover_via_client(
    flex: FlexilsClient,
    optical_flexils_target_id: str | None,
    optical_flexils_gmpls_id: IPAddress | None,
) -> tuple[OpticalNodeRole, str]:
    """Run the discovery against a single FlexILS client connection."""
    node_entry = _find_node_entry(flex, optical_flexils_target_id, optical_flexils_gmpls_id)

    target_id = _record_value(node_entry, "NENAME")
    if target_id is None:
        msg = f"RTRV-TOPONODE entry for node {optical_flexils_target_id} is missing the 'NENAME' field"
        raise ValueError(msg)

    role, software_version = _retrieve_node_properties(flex, target_id)

    logger.info(
        "Discovered FlexILS node properties",
        tid=flex.tid,
        gne_ip=flex.gne_ip,
        target_id=target_id,
        role=role.value,
        software_version=software_version,
    )
    return (role, software_version)


def discover_flexils_node(
    location_id: str,
    optical_flexils_target_id: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
) -> tuple[OpticalNodeRole, str]:
    """Discover the properties of a Nokia FlexILS node.

    If one or more management IPs are provided the node is contacted directly
    (each IP is tried in order). Otherwise the node is assumed to be a
    subtended network element (SNE): the closest GNE nodes to the location of
    the node are contacted and the node is looked up by its GMPLS ID.

    Args:
        location_id: Subscription id of the Optical Location hosting the node.
        optical_flexils_target_id: Target ID of the node.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
        optical_flexils_gmpls_id: GMPLS ID of the node (mandatory for SNEs).

    Returns:
        The discovered node properties.

    Raises:
        ValueError: If the node cannot be reached, identified or queried.
    """
    management_ips = [x for x in [optical_management_ip, optical_loopback_ip] if x is not None]

    if management_ips:
        candidates = [(optical_flexils_target_id, str(ip)) for ip in management_ips]
    else:
        if optical_flexils_gmpls_id is None:
            msg = "At least one of management IP or GMPLS ID must be provided to discover the node"
            raise ValueError(msg)

        location = location_block_from_subscription(location_id)
        if location is None or location.latitude is None or location.longitude is None:
            msg = f"Location {location_id} has no coordinates, cannot find a GNE for node {optical_flexils_target_id}"
            raise ValueError(msg)

        candidates = FlexilsGneProvider.find_closest_gnes(float(location.latitude), float(location.longitude))
        if not candidates:
            msg = f"No FlexILS GNE node found to reach subtended node {optical_flexils_target_id}"
            raise ValueError(msg)

    errors: list[str] = []
    for target_id, gne_ip in candidates:
        try:
            flex = FlexilsClient.get_instance(tid=target_id, gne_ip=gne_ip)
            return _discover_via_client(flex, optical_flexils_target_id, optical_flexils_gmpls_id)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{gne_ip} (tid={target_id}): {exc}")
            logger.warning("FlexILS discovery attempt failed", gne_ip=gne_ip, tid=target_id, error=str(exc))

    msg = f"Could not discover FlexILS node {optical_flexils_target_id}. Attempts: {'; '.join(errors)}"
    raise ValueError(msg)


class Vendor(strEnum):
    """Vendor of an Optical Node product block."""

    FLEXILS = "FlexILS"
    GROOVE_G30 = "Groove G30"
    GX_G42 = "GX G42"


def vendor_of(optical_node_block: AbstractOpticalNodeBlockInactive) -> Vendor:
    """Return the vendor of the given Optical Node product block.

    Args:
        optical_node_block: The Optical Node product block (any lifecycle variant).

    Returns:
        The vendor of the block.

    Raises:
        TypeError: If the block type is not a supported Optical Node vendor.
    """
    match optical_node_block:
        case NokiaFlexIlsBlock() | NokiaFlexIlsBlockProvisioning() | NokiaFlexIlsBlockInactive():
            return Vendor.FLEXILS
        case NokiaGrooveG30Block() | NokiaGrooveG30BlockProvisioning() | NokiaGrooveG30BlockInactive():
            return Vendor.GROOVE_G30
        case NokiaGxG42Block() | NokiaGxG42BlockProvisioning() | NokiaGxG42BlockInactive():
            return Vendor.GX_G42
        case _:
            msg = f"No vendor found for optical node block type {type(optical_node_block).__name__}"
            raise TypeError(msg)


def _as_flexils_block(optical_node_block: AbstractOpticalNodeBlockInactive) -> NokiaFlexIlsBlockInactive:
    """Narrow an Optical Node block to the Nokia FlexILS block type."""
    if not isinstance(optical_node_block, NokiaFlexIlsBlockInactive):
        msg = f"Expected a NokiaFlexIlsBlock, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _as_g30_block(optical_node_block: AbstractOpticalNodeBlockInactive) -> NokiaGrooveG30BlockInactive:
    """Narrow an Optical Node block to the Nokia Groove G30 block type."""
    if not isinstance(optical_node_block, NokiaGrooveG30BlockInactive):
        msg = f"Expected a NokiaGrooveG30Block, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _as_g42_block(optical_node_block: AbstractOpticalNodeBlockInactive) -> NokiaGxG42BlockInactive:
    """Narrow an Optical Node block to the Nokia GX G42 block type."""
    if not isinstance(optical_node_block, NokiaGxG42BlockInactive):
        msg = f"Expected a NokiaGxG42Block, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _find_closest_gne_ip(tid: str, latitude: float, longitude: float) -> str:
    """Find the management IP of the closest GNE through which the given node is reachable.

    The GNE candidates are probed with RTRV-TOPONODE until one of them reports
    the node among its toponode entries.

    Args:
        tid: The tid of the node to reach.
        latitude: Latitude of the node location in degrees.
        longitude: Longitude of the node location in degrees.

    Returns:
        The management IP of the GNE through which the node is reachable.

    Raises:
        ValueError: If no GNE can be found for the node.
    """
    candidates = FlexilsGneProvider.find_closest_gnes(latitude, longitude)
    if not candidates:
        msg = f"No FlexILS GNE node found to reach subtended node {tid}"
        raise ValueError(msg)

    errors: list[str] = []
    for gne_tid, gne_ip in candidates:
        try:
            flex = FlexilsClient.get_instance(tid=gne_tid, gne_ip=gne_ip)
            _find_node_entry(flex, tid, None)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{gne_ip} (tid={gne_tid}): {exc}")
            logger.warning("FlexILS GNE probing failed", gne_ip=gne_ip, tid=gne_tid, error=str(exc))
        else:
            return gne_ip

    msg = f"Could not find a GNE for FlexILS node {tid}. Attempts: {'; '.join(errors)}"
    raise ValueError(msg)


def get_flex_client(optical_node_block: NokiaFlexIlsBlockInactive) -> FlexilsClient:
    """Return a TL1 client to reach the given Nokia FlexILS node.

    The node is contacted directly through its management IPs, tried in order
    (management IP first, then loopback IP) until one is reachable; otherwise
    the closest Gateway Network Element (GNE) is found and probed with
    RTRV-TOPONODE until one reports the node.

    Args:
        optical_node_block: The Nokia FlexILS node block (any lifecycle variant).

    Returns:
        A FlexILS TL1 client.

    Raises:
        ValueError: If the node cannot be reached or identified.
    """
    tid = optical_node_block.pqdn
    if tid is None:
        msg = "Cannot create a FlexILS client: the node has no Target ID"
        raise ValueError(msg)

    gne_ips = [
        ip
        for ip in [optical_node_block.optical_management_ip, optical_node_block.optical_loopback_ip]
        if ip is not None
    ]

    if gne_ips:
        errors: list[str] = []
        for gne_ip in gne_ips:
            try:
                flex = FlexilsClient.get_instance(tid=tid, gne_ip=gne_ip)
                _find_node_entry(flex, tid, None)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{gne_ip}: {exc}")
                logger.warning("FlexILS direct client probe failed", gne_ip=gne_ip, tid=tid, error=str(exc))
            else:
                return flex

        msg = f"Could not reach FlexILS node {tid} through any management IP. Attempts: {'; '.join(errors)}"
        raise ValueError(msg)

    location = optical_node_block.location
    if location is None or location.latitude is None or location.longitude is None:
        msg = f"Cannot reach FlexILS node {tid}: no management IP and no location coordinates to find a GNE"
        raise ValueError(msg)
    gne_ip = _find_closest_gne_ip(tid, float(location.latitude), float(location.longitude))

    return FlexilsClient.get_instance(tid=tid, gne_ip=gne_ip)


def get_g30_client(optical_node_block: AbstractOpticalNodeBlockInactive) -> G30Client:
    """Return a RESTCONF client to reach the given Nokia Groove G30 node.

    Args:
        optical_node_block: The Nokia Groove G30 node block (any lifecycle variant).

    Returns:
        A Groove G30 RESTCONF client.
    """
    return G30Client(
        loopback_ip=str(optical_node_block.optical_loopback_ip or "") or None,
        management_ip=str(optical_node_block.optical_management_ip or "") or None,
    )


def get_g42_client(optical_node_block: AbstractOpticalNodeBlockInactive) -> G42Client:
    """Return a RESTCONF client to reach the given Nokia GX G42 node.

    Args:
        optical_node_block: The Nokia GX G42 node block (any lifecycle variant).

    Returns:
        A GX G42 RESTCONF client.
    """
    return G42Client(
        loopback_ip=str(optical_node_block.optical_loopback_ip or "") or None,
        management_ip=str(optical_node_block.optical_management_ip or "") or None,
    )


def get_optical_node_client(
    optical_node_block: AbstractOpticalNodeBlockInactive,
) -> FlexilsClient | G30Client | G42Client:
    """Return the client to reach the given Optical Node, based on its vendor.

    Args:
        optical_node_block: The Optical Node block (any lifecycle variant).

    Returns:
        The client to reach the node.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return get_flex_client(_as_flexils_block(optical_node_block))
        case Vendor.GROOVE_G30:
            return get_g30_client(optical_node_block)
        case Vendor.GX_G42:
            return get_g42_client(optical_node_block)


def _retrieve_omses_flexils(optical_node_block: NokiaFlexIlsBlockInactive) -> list[dict[str, Any]]:
    """Retrieve the Optical Muxed Sections terminating on a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    response = flex.rtrv_otelink()
    omses: list[dict[str, Any]] = []
    for otelink in response.parsed_data:
        if _record_value(otelink, "REACHSCOPE") != "Local":
            continue
        aid = _record_value(otelink, "AID")
        mate = _record_value(otelink, "MATETELINK")
        if aid is None or mate is None or "-" not in aid or "-" not in mate:
            msg = f"RTRV-OTELINK entry with AID={aid!r} and MATETELINK={mate!r} is missing or malformed"
            raise ValueError(msg)
        local_device, local_port = aid.split("-", 1)
        remote_device, remote_port = mate.split("-", 1)

        avail_freq_ranges = otelink.get("AVAILFREQRANGELIST")
        if not isinstance(avail_freq_ranges, list) or not avail_freq_ranges:
            msg = f"RTRV-OTELINK entry {aid} has no AVAILFREQRANGELIST"
            raise ValueError(msg)
        if not isinstance(avail_freq_ranges[0], list):
            avail_freq_ranges = [avail_freq_ranges]
        available_passbands = [[int(x) for x in inner_list] for inner_list in avail_freq_ranges]
        omses.append(
            {
                "local_port": local_port,
                "remote_port": remote_port,
                "local_device": local_device,
                "remote_device": remote_device,
                "available_passbands": available_passbands,
            }
        )
    return omses


def retrieve_omses_terminating_on_device(optical_node_block: AbstractOpticalNodeBlockInactive) -> list[dict[str, Any]]:
    """Retrieve all the Optical Muxed Sections terminating on a given Optical Node.

    Args:
        optical_node_block: The Optical Node block for which Optical Muxed Sections are to be retrieved.

    Returns:
        A list of dictionaries containing information about the Optical Muxed Sections.

    Example return:
        [
            {
                'local_port': '1-A-2-L1',
                'remote_port': '1-A-1-L1',
                'local_device': 'flex.aa00',
                'remote_device': 'flex.zz99',
                'available_passbands': [
                    [191362500, 191375000],
                ]
            },
        ]
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _retrieve_omses_flexils(_as_flexils_block(optical_node_block))
        case Vendor.GROOVE_G30:
            return []
        case Vendor.GX_G42:
            return []


def _retrieve_ports_spectral_occupations_flexils(
    optical_node_block: NokiaFlexIlsBlockInactive,
) -> dict[str, list[tuple[int, int]]]:
    """Retrieve the spectral occupations of the ports of a Nokia FlexILS node."""
    spectral_occupations: dict[str, list[tuple[int, int]]] = {}
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    response = flex.rtrv_otelink()
    for otelink in response.parsed_data:
        if otelink["REACHSCOPE"] == "Local":
            _, local_port = otelink["AID"].split("-", 1)
            if not isinstance(otelink["AVAILFREQRANGELIST"][0], list):
                otelink["AVAILFREQRANGELIST"] = [otelink["AVAILFREQRANGELIST"]]
            available_passbands = [
                (int(inner_list[0]), int(inner_list[1])) for inner_list in otelink["AVAILFREQRANGELIST"]
            ]
            used_passbands = available_to_used_passbands(available_passbands)
            spectral_occupations[local_port] = [(int(start), int(end)) for start, end in used_passbands]
    return spectral_occupations


def retrieve_ports_spectral_occupations(
    optical_node_block: AbstractOpticalNodeBlockInactive,
) -> dict[str, list[tuple[int, int]]]:
    """Retrieve the spectral occupations of the ports of a given Optical Node.

    Args:
        optical_node_block: The Optical Node block for which port spectral occupations are to be retrieved.

    Returns:
        A dictionary where keys are port names and values are lists of spectral occupations.
        Empty for the vendors that do not support this retrieval.

    Example return:
        {
            '1-A-2-L1': [
                (191362500, 191375000),
            ],
        }
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _retrieve_ports_spectral_occupations_flexils(_as_flexils_block(optical_node_block))
        case Vendor.GROOVE_G30:
            return {}
        case Vendor.GX_G42:
            return {}


def _validate_management_network_config_g30(optical_node_block: NokiaGrooveG30BlockInactive) -> None:
    """Check the network configuration of a Nokia Groove G30 node against the expected template."""
    g30 = get_g30_client(optical_node_block)
    intf_navigator = g30.data.ne_ne.system.networking.interface
    intf_config = intf_navigator.retrieve(content="config", depth=5)
    rtp_navigator = g30.data.ne_ne.system.networking.routing.routing_protocol
    rtp_config = rtp_navigator.retrieve(content="config", depth=5)
    opt_intf_config = g30.data.ne_ne.services.optical_interfaces.retrieve(content="config", depth=4)

    lo_ip = optical_node_block.optical_loopback_ip
    eth1_ip = optical_node_block.optical_management_ip

    eth1_intf_name, eth1_gateway, is_g30_connected_to_switch, eth1_prefix_len = _get_eth1_details(eth1_ip)

    lo_intf_name = next((i.if_name for i in intf_config if i.if_type == "softwareLoopback"), "")
    osc_names = [osc.osc_name for osc in getattr(opt_intf_config, "osc", [])]
    oscx_intf_names = [f"intf_oscx{osc_name.split('/')[0]}" for osc_name in osc_names]

    desired_intf_config = intf_navigator.from_template(
        lo_ip=lo_ip,
        lo_name=lo_intf_name,
        eth1_ip=eth1_ip,
        eth1_prefix_length=eth1_prefix_len,
        osc_names=osc_names,
    )

    desired_rtp_config = rtp_navigator.from_template(
        ospf_router_id=lo_ip,
        is_ospf_asbr=is_g30_connected_to_switch,
        oscx_intf_names=oscx_intf_names,
        eth1_intf_name=eth1_intf_name,
        eth1_default_gateway=eth1_gateway,
        eth1_default_out_intf_name=eth1_intf_name,
    )

    intf_diffs = compare_pydantic_objects(expected=desired_intf_config, actual=intf_config, unique_id_keys=["if-name"])
    rtp_diffs = compare_pydantic_objects(
        expected=desired_rtp_config,
        actual=rtp_config,
        unique_id_keys=["rtp-type", "ospf-area-id", "ospf-if-name", "destination-prefix", "index"],
    )
    diffs = {
        "+++": intf_diffs["+++"] | rtp_diffs["+++"],
        "---": intf_diffs["---"] | rtp_diffs["---"],
    }

    if any(diffs.values()):
        msg = f"Configuration mismatch for {optical_node_block.pqdn}:\n{json.dumps(diffs, indent=2, sort_keys=True)}\n"
        raise ValueError(msg)


def _get_eth1_details(eth1_ip: str | None) -> tuple[str | None, str | None, bool, int]:
    """Derive the expected eth1 interface configuration from its management IP address."""
    switch_nets = [ipaddress.ip_network(n) for n in ["10.127.0.0/16", "172.16.0.0/16"]]
    p2p_nets = [ipaddress.ip_network("10.10.0.0/16")]

    if not eth1_ip:
        return None, None, False, 0

    ip = ipaddress.ip_address(eth1_ip)

    if any(ip in net for net in switch_nets):
        prefix_len = 24
        subnet = ipaddress.ip_network(f"{eth1_ip}/{prefix_len}", strict=False)
        gateway = str(subnet.network_address + 1)
        return "eth1", gateway, True, prefix_len

    if any(ip in net for net in p2p_nets):
        prefix_len = 30
        subnet = ipaddress.ip_network(f"{eth1_ip}/{prefix_len}", strict=False)
        gateway = str(next(x for x in subnet.hosts() if x != ip))
        return "eth1", gateway, False, prefix_len

    msg = f"Invalid management IP: {eth1_ip}. Out of allowed ranges."
    raise ValueError(msg)


def validate_management_network_config(optical_node_block: AbstractOpticalNodeBlockInactive) -> None:
    """Check the network configuration of a given Optical Node.

    Args:
        optical_node_block: The Optical Node block for which the network configuration is to be checked.

    Returns:
        None

    Raises:
        ValueError: If the network configuration does not meet the expected criteria.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            msg = "Not yet implemented for FlexILS"
            logger.warning(msg)
        case Vendor.GROOVE_G30:
            _validate_management_network_config_g30(_as_g30_block(optical_node_block))
        case Vendor.GX_G42:
            pass
