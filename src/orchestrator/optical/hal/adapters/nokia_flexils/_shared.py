"""Device-level, cross-area shared helpers for the Nokia FlexILS adapter."""

from collections.abc import Sequence
from math import cos, radians, sin
from typing import Any, ClassVar, Protocol, cast

from structlog import get_logger

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import subscription_instances_by_block_type
from orchestrator.optical.hal._common import _as_flexils_block, _node_id
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import get_g30_client
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node._abstracts import (
    _AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port._abstracts import _AbstractOpticalPortBlockProvisioning
from orchestrator.optical.services.nokia.flexils.client import FlexilsClient
from orchestrator.optical.services.nokia.flexils.commands.base import TL1BaseResponse
from orchestrator.optical.services.nokia.g30.data_models.ne import EquipmentTypeEnum_1
from orchestrator.optical.utils.custom_types.ip_address import IPAddress

logger = get_logger(__name__)

Vector = tuple[float, float, float]

_MAX_GNE_CANDIDATES = 7


class FlexilsClientProtocol(Protocol):
    """Typing protocol for the dynamically-bound TL1 commands of :class:`FlexilsClient`.

    The FlexILS client binds its command methods (``rtrv_osnc``, ``ent_ocrs``, ...) to
    the instance at runtime, so static type checkers cannot see them on the class.
    This protocol documents the subset of the command surface used by the HAL.
    """

    tid: str
    gne_ip: str

    def rtrv_oteintf(self) -> TL1BaseResponse:
        """Retrieve the OTEINTF entries of the node."""

    def rtrv_eqpt(self, aid: str | None = None) -> TL1BaseResponse:
        """Retrieve the equipment inventory entries of the node."""

    def rtrv_scg(self, aid: str | None = None, type: str | None = None) -> TL1BaseResponse:  # noqa: A002
        """Retrieve the SCG entries of the node, optionally filtered by type."""

    def ent_oel(
        self,
        aid: str,
        label: str,
        srcnodename: str,
        dstnodename: str,
        explicitroute: list[tuple[str, str, str, str]],
        validfrangelist: list[int],
    ) -> TL1BaseResponse:
        """Enter a new Optical Engineered Lightpath (OEL)."""

    def opr_valroute_oel(self, aid: str) -> TL1BaseResponse:
        """Validate the route of the given OEL."""

    def rtrv_oel(self, aid: str | None = None) -> TL1BaseResponse:
        """Retrieve the OEL entries of the node."""

    def rtrv_osnc(self, aid: str | None = None, oelaid: str | None = None) -> TL1BaseResponse:
        """Retrieve the OSNC entries of the node."""

    def ent_osnc(
        self,
        aid: str,
        label: str,
        remnodetid: str,
        remendpoint: str,
        oelaid: str,
        cktidsuffix: str,
        passbandlist: Sequence[str | int],
        carrierlist: Sequence[str | int],
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Enter a new OSNC between a local and a remote endpoint."""

    def ed_osnc(
        self,
        aid: str,
        label: str | None = None,
        oelaid: str | None = None,
        cktidsuffix: str | None = None,
        passbandlist: Sequence[str | int] | None = None,
        carrierlist: Sequence[str | int] | None = None,
        is_oos: str | None = None,
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Edit the configuration of the given OSNC."""

    def dlt_osnc(self, aid: str) -> TL1BaseResponse:
        """Delete the given OSNC."""

    def rtrv_sch(self, aid: str | None = None) -> TL1BaseResponse:
        """Retrieve the superchannel entries of the node."""

    def ed_sch(
        self,
        aid: str,
        label: str | None = None,
        shutterstate: str | None = None,
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Edit the configuration of the given superchannel."""

    def rtrv_ocrs(
        self,
        fromaid: str | None = None,
        toaid: str | None = None,
        sigtype: str | None = None,
    ) -> TL1BaseResponse:
        """Retrieve the optical cross-connection entries of the node."""

    def ent_ocrs(
        self,
        fromaid: str,
        toaid: str,
        label: str | None = None,
        cktidsuffix: str | None = None,
        freqslotplantype: str | None = None,
        schoffset: str | None = None,
        passbandlist: Sequence[str | int] | None = None,
        carrierlist: Sequence[str | int] | None = None,
        autoretunelmsch: str | None = None,
        intracarrspecshaping: str | None = None,
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Enter a new optical cross-connection (OCRS)."""

    def dlt_ocrs(self, fromaid: str, toaid: str) -> TL1BaseResponse:
        """Delete the given optical cross-connection (OCRS)."""

    def put_maintenance(self, aidtype: str, aid: str) -> TL1BaseResponse:
        """Put the given entity into maintenance state."""

    def rst_maintenance(self, aidtype: str, aid: str) -> TL1BaseResponse:
        """Restore the given entity from maintenance state."""

    def rtrv_pm_sch(self, aid: str, montype: str | None = None) -> TL1BaseResponse:
        """Retrieve the performance monitoring data of the given superchannel."""


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

            management_ips = [
                ip
                for ip in (
                    block.management.optical_module_node_dcn_loopback_ip,
                    block.management.optical_module_node_dcn_interface_ip,
                )
                if ip is not None
            ]
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
            gnes.append((block.optical_flexils_target_id, management_ips[0], vector))

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
    optical_flexils_target_id: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
    location: OpticalModuleLocationBlockProvisioning | None = None,
) -> tuple[OpticalNodeRole, str]:
    """Discover the properties of a Nokia FlexILS node.

    If one or more management IPs are provided the node is contacted directly
    (each IP is tried in order). Otherwise the node is assumed to be a
    subtended network element (SNE): the closest GNE nodes to the location of
    the node are contacted and the node is looked up by its GMPLS ID.

    Args:
        optical_flexils_target_id: Target ID of the node.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
        optical_flexils_gmpls_id: GMPLS ID of the node (mandatory for SNEs).
        location: The Optical Location block hosting the node, used to find a GNE.

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

        if location is None or location.latitude is None or location.longitude is None:
            msg = f"Location {location} has no coordinates, cannot find a GNE for node {optical_flexils_target_id}"
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


def get_flex_client(optical_node_block: NokiaFlexIlsBlockProvisioning) -> FlexilsClient:
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
    tid = optical_node_block.optical_flexils_target_id
    if tid is None:
        msg = "Cannot create a FlexILS client: the node has no Target ID"
        raise ValueError(msg)

    gne_ips = [
        ip
        for ip in [
            optical_node_block.management.optical_module_node_dcn_loopback_ip,
            optical_node_block.management.optical_module_node_dcn_interface_ip,
        ]
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


def _get_flex_client(optical_node_block: _AbstractOpticalNodeBlockProvisioning) -> FlexilsClientProtocol:
    """Return a FlexILS TL1 client for the given Optical Node block.

    Wraps :func:`get_flex_client`, returning the dynamically-bound TL1 command
    surface as a protocol so that it type checks.
    """
    return cast(FlexilsClientProtocol, get_flex_client(_as_flexils_block(optical_node_block)))


def _get_remote_node_id(remote_port_block: _AbstractOpticalPortBlockProvisioning) -> str:
    """Extract the node id of the device hosting the remote port, based on its vendor.

    Args:
        remote_port_block: Optical Port product block of the remote port.

    Returns:
        The Groove G30 shelf serial number, or the fqdn for the other vendors.

    Raises:
        ValueError: If the node id cannot be determined.
    """
    host_node = remote_port_block.optical_port_host_node
    match (host_node.management.optical_module_node_vendor, host_node.management.optical_module_node_platform):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            g30 = get_g30_client(host_node)
            inventory = g30.data.ne_ne.inventory_data.inventory.retrieve(depth=2)

            for item in inventory:
                if item.equipment_type == EquipmentTypeEnum_1.SHELF and item.shelf_id == 1:
                    serial_number = item.serial_number
                    if serial_number is None:
                        msg = (
                            f"Shelf 1 of G30 device "
                            f"{host_node.management.optical_module_node_fqdn} has no serial number"
                        )
                        raise ValueError(msg)
                    return serial_number

            msg = f"Could not find shelf serial number for G30 device {host_node.management.optical_module_node_fqdn}"
            raise ValueError(msg)
        case (Vendor.NOKIA, Platform.GX_G42) | (Vendor.NOKIA, Platform.FLEXILS):
            return _node_id(host_node)
        case _:
            msg = f"Unsupported remote platform for FlexILS connection: {type(host_node).__name__}"
            raise ValueError(msg)
