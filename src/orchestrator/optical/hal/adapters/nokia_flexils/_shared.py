"""Device-level, cross-area shared helpers for the Nokia FlexILS adapter."""

from collections.abc import Sequence
from typing import Any, Protocol, cast

from structlog import get_logger

from orchestrator.optical.hal._common import _as_flexils_block, _node_id
from orchestrator.optical.hal.adapters.nokia_flexils._sdk import FlexilsClient, TL1BaseResponse
from orchestrator.optical.hal.adapters.nokia_flexils.gne import FlexilsGneProvider
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning
from orchestrator.optical.settings import get_settings
from orchestrator.optical.utils.custom_types.ip_address import IPAddress

logger = get_logger(__name__)


def _flexils_client(tid: str, gne_ip: str) -> FlexilsClient:
    """Return the cached TL1 client for ``tid`` behind ``gne_ip``, configured from the settings.

    Args:
        tid: Target ID the TL1 commands are addressed to.
        gne_ip: IP of the network element terminating the SSH session.

    Returns:
        The cached FlexILS TL1 client.
    """
    settings = get_settings()
    return FlexilsClient.get_instance(
        tid=tid,
        gne_ip=gne_ip,
        username=settings.flexils_user,
        password=settings.flexils_password,
        verify_host_key=settings.flexils_verify_host_key,
    )


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

    def ed_oel(
        self,
        aid: str,
        label: str | None = None,
        oelsource: str | None = None,
        compcardtypelist: Sequence[str] | None = None,
        is_oos_ains: str | None = None,
    ) -> TL1BaseResponse:
        """Edit the configuration of the given OEL."""

    def dlt_oel(self, aid: str) -> TL1BaseResponse:
        """Delete the given OEL."""

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


def _retrieve_node_properties(flex: FlexilsClient) -> tuple[OpticalNodeRole, str]:
    """Retrieve the node role and software version of the node the client targets."""
    flex = cast(Any, flex)  # the TL1 command methods are bound dynamically by the client
    # NETYPE values reported by RTRV-SYS mapped to the OpticalNodeRole.
    netype_to_role: dict[str, OpticalNodeRole] = {
        "ROADM": OpticalNodeRole.ROADM,
        "OLA": OpticalNodeRole.AMPLIFIER,
        "OA": OpticalNodeRole.AMPLIFIER,
    }

    response = flex.rtrv_sys()
    records = response.parsed_data
    if not records:
        msg = f"RTRV-SYS returned no data for node {flex.tid}"
        raise ValueError(msg)

    sys_record = records[0]

    netype = _record_value(sys_record, "NETYPE")
    role = netype_to_role.get(netype or "")
    if role is None:
        msg = f"RTRV-SYS returned unknown NETYPE {netype!r} for node {flex.tid}"
        raise ValueError(msg)

    software_version = _record_value(sys_record, "SWVERSION")
    if software_version is None:
        msg = f"RTRV-SYS did not report a software version for node {flex.tid}"
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

    # The probe client may be keyed on the GNE's tid (so RTRV-TOPONODE returns the
    # GNE's topology). RTRV-SYS must target the node itself, so rebind to a client
    # whose tid is the node's NENAME over the same session endpoint.
    node_flex = _flexils_client(tid=target_id, gne_ip=flex.gne_ip)
    role, software_version = _retrieve_node_properties(node_flex)

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
        candidates = [(optical_flexils_target_id, [ip]) for ip in management_ips]
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
    for target_id, gne_ips in candidates:
        for gne_ip in gne_ips:
            try:
                flex = _flexils_client(tid=target_id, gne_ip=gne_ip)
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
    for gne_tid, gne_ips in candidates:
        for gne_ip in gne_ips:
            try:
                flex = _flexils_client(tid=gne_tid, gne_ip=gne_ip)
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
            optical_node_block.management.optical_module_node_dcn_interface_ip,
            optical_node_block.management.optical_module_node_dcn_loopback_ip,
        ]
        if ip is not None
    ]

    if gne_ips:
        errors: list[str] = []
        for gne_ip in gne_ips:
            try:
                flex = _flexils_client(tid=tid, gne_ip=gne_ip)
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

    return _flexils_client(tid=tid, gne_ip=gne_ip)


def _get_flex_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> FlexilsClientProtocol:
    """Return a FlexILS TL1 client for the given Optical Node block.

    Wraps :func:`get_flex_client`, returning the dynamically-bound TL1 command
    surface as a protocol so that it type checks.
    """
    return cast(FlexilsClientProtocol, get_flex_client(_as_flexils_block(optical_node_block)))


def _get_remote_node_id(remote_port_block: AnyOpticalPortBlockProvisioning) -> str:
    """Extract the node id of the device hosting the remote port, based on its vendor.

    Args:
        remote_port_block: Optical Port product block of the remote port.

    Returns:
        The Groove G30 shelf serial number, the Target Identifier (TID) for FlexILS,
        or the fqdn for the other vendors.

    Raises:
        ValueError: If the node id cannot be determined.
    """
    host_node = remote_port_block.optical_port_host_node
    match (host_node.management.optical_module_node_vendor, host_node.management.optical_module_node_platform):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            # Imported here: only a FlexILS port facing a G30 needs the G30 SDK.
            from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (  # noqa: PLC0415
                g30_shelf_serial_number,
            )

            return g30_shelf_serial_number(host_node)
        case (Vendor.NOKIA, Platform.GX_G42) | (Vendor.NOKIA, Platform.FLEXILS):
            return _node_id(host_node)
        case _:
            msg = f"Unsupported remote platform for FlexILS connection: {type(host_node).__name__}"
            raise ValueError(msg)
