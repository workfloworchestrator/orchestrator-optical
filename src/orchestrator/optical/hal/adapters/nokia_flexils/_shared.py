"""Device-level, cross-area shared helpers for the Nokia FlexILS adapter."""

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, cast

from structlog import get_logger

from orchestrator.optical.hal._common import _as_flexils_block, _node_id
from orchestrator.optical.hal.adapters.nokia_flexils._sdk import (
    BaseRequest,
    BaseResponse,
    FlexSdkClientBase,
    GeneratedMethods,
    SshTransport,
    TL1DeniedError,
    parse_reply,
)
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

#: Marker of a denial telling that the entity is already in the requested state.
_ALREADY = "ALREADY"

#: Marker of a denial telling that the requested object does not exist on the node.
_OBJECT_DOES_NOT_EXIST = "SPECIFIED OBJECT ENTITY DOES NOT EXIST"

#: Positional slots of the standard TL1 record (``<AID>:<TYPE>:<KEY=value,...>:<PST>,<SST>``) that the
#: generated surface leaves unnamed for most commands, under the names the adapter reads them by. The
#: slots the surface does name keep its names (``AID``, ``FROMAID``, ``TOAID``, ``PST``, ``MONVAL``, ...).
_SLOT_NAMES = {"1.0": "TYPE", "3.0": "PST", "3.1": "SST"}

#: Record values that are ``&``-separated lists (``&-`` between the groups of a nested list).
_LIST_KEYS = frozenset({"PASSBANDLIST", "CARRIERLIST", "AVAILFREQRANGELIST"})


class FlexilsClient(GeneratedMethods, FlexSdkClientBase):
    """The generated TL1 client of the node ``tid``, reached through the network element at ``gne_ip``.

    It is the generated command surface plus the SDK runtime (exactly what the SDK's
    ``get_client`` assembles), with the two things the adapter adds: the identity of the
    node it targets, and the rule that makes the adapter's state transitions idempotent.
    """

    def __init__(self, tid: str, gne_ip: str, **kwargs: Any) -> None:
        """Bind the client to ``tid`` behind ``gne_ip``; no connection is opened here."""
        super().__init__(tid, gne_ip, **kwargs)
        self.tid = tid
        self.gne_ip = gne_ip

    def execute[R: BaseResponse](
        self,
        command: BaseRequest[R],
        *,
        raise_on_deny: bool = True,
        timeout: float | None = None,
    ) -> R:
        """Execute ``command``, treating a denial for an entity ALREADY in the requested state as done.

        The adapter drives admin states and creations as "bring it there from wherever it
        is" (e.g. put in service, then lock), so the node answering that nothing had to
        change is a success, not an error. Every other denial raises.

        Returns:
            The typed response; of the denial itself when the entity was already there.
        """
        try:
            # The SDK runtime, named: the generated surface only declares ``execute`` for type checkers.
            return FlexSdkClientBase.execute(self, command, raise_on_deny=raise_on_deny, timeout=timeout)
        except TL1DeniedError as exc:
            if _ALREADY not in exc.raw:
                raise
            return cast(R, command.response_class.from_reply(parse_reply(exc.raw)))


def _flexils_client(tid: str, gne_ip: str) -> FlexilsClient:
    """Return the cached TL1 client for ``tid`` behind ``gne_ip``, configured from the settings.

    Args:
        tid: Target ID the TL1 commands are addressed to.
        gne_ip: IP of the network element terminating the SSH session.

    Returns:
        The cached FlexILS TL1 client (one session per ``tid`` and ``gne_ip``).

    Raises:
        ValueError: If the FlexILS credentials are not configured.
    """
    settings = get_settings()
    if not settings.flexils_user or not settings.flexils_password:
        msg = "FlexILS credentials are not configured: set OPTICAL_FLEXILS_USER and OPTICAL_FLEXILS_PASSWORD"
        raise ValueError(msg)
    # The transport is only used when the client is not cached yet (building one opens no connection).
    transport = SshTransport(
        gne_ip,
        username=settings.flexils_user,
        password=settings.flexils_password,
        known_hosts=_known_hosts(settings.flexils_verify_host_key),
    )
    client = FlexilsClient.get_instance(
        tid,
        gne_ip,
        transport=transport,
        username=settings.flexils_user,
        password=settings.flexils_password,
    )
    return cast(FlexilsClient, client)


def _known_hosts(verify_host_key: bool | str) -> Path | None:  # noqa: FBT001
    """Map the ``OPTICAL_FLEXILS_VERIFY_HOST_KEY`` setting to the known-hosts file of the SSH transport.

    Args:
        verify_host_key: ``True`` (the user's known-hosts file), a path to a known-hosts
            file, or ``False`` (no verification).

    Returns:
        The file unknown or changed host keys are rejected against, or ``None`` to accept any host key.
    """
    if verify_host_key is False:
        logger.warning("SSH host key verification is disabled for the FlexILS client. Do not use in production.")
        return None
    if verify_host_key is True:
        return Path.home() / ".ssh" / "known_hosts"
    return Path(verify_host_key).expanduser()


def _is_object_missing(exc: TL1DeniedError) -> bool:
    """Return whether a TL1 command was denied because the requested object does not exist."""
    return _OBJECT_DOES_NOT_EXIST in exc.raw.upper()


def _tl1_quoted(text: str) -> str:
    r"""Return ``text`` as a TL1 quoted string (``"..."``, inner quotes and backslashes escaped).

    Free text (labels) is always sent quoted, the empty string included: ``""`` is the
    value that clears a field. The SDK sends an already quoted value as it is.
    """
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _tl1_list(values: Iterable[object]) -> str:
    """Return ``values`` as a TL1 list: ``&`` between the items, ``&-`` between the groups of a nested list."""
    items = list(values)
    if items and all(isinstance(item, list | tuple) for item in items):
        return "&-".join(_tl1_list(cast(Iterable[object], group)) for group in items)
    return "&".join(str(item) for item in items)


def _records(response: BaseResponse) -> list[dict[str, Any]]:
    """Return the records of a TL1 response as wire-keyed dicts, the shape the adapter works on.

    Every value the node sent is kept, under its wire key (``LABEL``, ``PROVNBRTP``, ...):
    an empty value is ``""``, a key the node did not send is absent, and the values of
    :data:`_LIST_KEYS` are split into (possibly nested) lists of strings. Positional
    values are keyed by the generated field name (``AID``, ``FROMAID``, ...) or by
    :data:`_SLOT_NAMES`; a slot neither names is kept under its ``<section>.<index>``.
    """
    records: list[dict[str, Any]] = []
    for model in response.records:
        values = model.model_dump(by_alias=True, exclude_unset=True)
        slots: dict[str, str] = values.pop("UNMAPPED", {})
        record: dict[str, Any] = {}
        for key, value in values.items():
            text = "" if value is None else value
            record[key] = _split_list(text) if key in _LIST_KEYS else text
        for slot, value in slots.items():
            record[_SLOT_NAMES.get(slot, slot)] = value
        records.append(record)
    return records


def _all_records(retrieve: Callable[[], BaseResponse]) -> list[dict[str, Any]]:
    """Return the :func:`_records` of an unfiltered retrieve, ``[]`` when the node has no such object.

    A node with none of the requested objects (e.g. no OCRS yet) denies the unfiltered
    ``RTRV-*`` with ``IENE`` (object does not exist) instead of an empty reply.
    """
    try:
        return _records(retrieve())
    except TL1DeniedError as exc:
        if not _is_object_missing(exc):
            raise
        return []


def _split_list(value: str) -> list[Any]:
    """Split a TL1 list value: nested (``a&b&-c&d``) into groups, flat (``a&b``) into items."""
    if not value:
        return []
    if "&-" in value:
        return [group.split("&") for group in value.split("&-")]
    return value.split("&")


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
    records = _records(flex.rtrv_toponode())

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
    # NETYPE values reported by RTRV-SYS mapped to the OpticalNodeRole.
    netype_to_role: dict[str, OpticalNodeRole] = {
        "ROADM": OpticalNodeRole.ROADM,
        "OLA": OpticalNodeRole.AMPLIFIER,
        "OA": OpticalNodeRole.AMPLIFIER,
    }

    records = _records(flex.rtrv_sys())
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


def _get_flex_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> FlexilsClient:
    """Return a FlexILS TL1 client for the given Optical Node block, narrowed to a FlexILS node."""
    return get_flex_client(_as_flexils_block(optical_node_block))


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
