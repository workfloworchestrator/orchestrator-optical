"""Spectrum-area operations for the Nokia FlexILS device adapter."""

from collections.abc import Sequence
from time import sleep
from typing import Any

from structlog import get_logger

from orchestrator.optical.hal._common import (
    _as_flexils_block,
    _node_id,
    _port_name,
)
from orchestrator.optical.hal.adapters.nokia_flexils._shared import FlexilsClientProtocol, _get_flex_client
from orchestrator.optical.hal.adapters.nokia_flexils.port import _ensure_manualmode2
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.services.nokia.flexils.exceptions import TL1CommandDeniedError
from orchestrator.optical.utils.custom_types.frequencies import Bandwidth, Frequency, Passband
from orchestrator.optical.utils.datadiff import DiffResult, compare_jsons

#: TL1 response marker returned when a requested object does not exist on the node.
_OBJECT_DOES_NOT_EXIST = "SPECIFIED OBJECT ENTITY DOES NOT EXIST"

logger = get_logger(__name__)


class _OsncNotFoundError(ValueError):
    """Raised when no OSNC matches the requested circuit on either end of a section."""


def _tl1_label(label: str) -> str:
    """Quote an OSNC label for the TL1 wire.

    The TL1 serializer sends parameter values unquoted, so a label containing
    ``":"`` (the composite ``"<channel>: <svcA> + <svcB>"`` form), commas or
    semicolons would corrupt the command framing. Double-quoting the value keeps
    it a single TL1 parameter; retrieval already strips surrounding quotes, so
    the round-trip is transparent. Idempotent: pre-quoted input is not quoted twice.

    Args:
        label: The raw label to send.

    Returns:
        The double-quoted label.

    Raises:
        ValueError: If the label is blank.
    """
    clean = label.strip().strip('"')
    if not clean:
        msg = "Cannot send a blank optical circuit label"
        raise ValueError(msg)
    return f'"{clean}"'


def _node_role(port: AnyOpticalPortBlockProvisioning) -> OpticalNodeRole:
    """Return the role of the Optical Node hosting the given port."""
    role = port.optical_port_host_node.optical_node_role
    if role is None:
        msg = f"Optical port {_port_name(port)} is hosted by a node without a role"
        raise ValueError(msg)
    return role


def _is_object_missing(exc: TL1CommandDeniedError) -> bool:
    """Return whether a TL1 command was denied because the requested object does not exist."""
    return _OBJECT_DOES_NOT_EXIST in str(exc.response).upper()


def _rtrv_oel_or_none(flex: FlexilsClientProtocol, aid: str) -> dict[str, Any] | None:
    """Retrieve an OEL, returning ``None`` when the node does not have it.

    Args:
        flex: TL1 client of the node hosting the OEL.
        aid: Access identifier of the OEL.

    Returns:
        The OEL record, or ``None`` when the OEL does not exist.
    """
    try:
        response = flex.rtrv_oel(aid=aid)
    except TL1CommandDeniedError as e:
        if not _is_object_missing(e):
            raise
        return None
    return response.parsed_data[0] if response.parsed_data else None


def _rtrv_ocrs_or_none(
    flex: FlexilsClientProtocol,
    fromaid: str | None = None,
    toaid: str | None = None,
) -> dict[str, Any] | None:
    """Retrieve an OCRS, returning ``None`` when the node does not have it.

    Args:
        flex: TL1 client of the node hosting the cross-connection.
        fromaid: Access identifier of the ``from`` endpoint.
        toaid: Access identifier of the ``to`` endpoint.

    Returns:
        The OCRS record, or ``None`` when the cross-connection does not exist.
    """
    try:
        response = flex.rtrv_ocrs(fromaid=fromaid, toaid=toaid)
    except TL1CommandDeniedError as e:
        if not _is_object_missing(e):
            raise
        return None
    return response.parsed_data[0] if response.parsed_data else None


def _omses_from_line_ports(
    line_ports: Sequence[AnyOpticalPortBlockProvisioning],
) -> list[tuple[AnyOpticalPortBlockProvisioning, AnyOpticalPortBlockProvisioning]]:
    """Divide the interior line ports of an optical path into OMS (Optical Multiplex Section) segments.

    An OMS is a link between two ROADMs, so its endpoints are ROADM line ports: the ports
    are paired two at a time, skipping any amplifier ports in between. The add/drop ports
    of the section are *not* OMS endpoints (they are tributary ports on the ROADMs) and
    must not be passed here.

    Args:
        line_ports: The ordered interior OLS line ports of the section, from the source
            add/drop port to the destination add/drop port.

    Returns:
        List of tuples containing (start_port, end_port) for each OMS section.

    Raises:
        ValueError: If the path is empty or contains unexpected node roles.
    """
    if not line_ports:
        msg = "Optical path is empty"
        raise ValueError(msg)

    if _node_role(line_ports[0]) != OpticalNodeRole.ROADM:
        msg = "Optical path does not start with a ROADM device"
        raise ValueError(msg)

    omses: list[tuple[AnyOpticalPortBlockProvisioning, AnyOpticalPortBlockProvisioning]] = []
    oms_source_port: AnyOpticalPortBlockProvisioning | None = line_ports[0]
    for port in line_ports[1:]:
        node_role = _node_role(port)
        if node_role == OpticalNodeRole.ROADM:
            if oms_source_port is None:
                oms_source_port = port
            else:
                omses.append((oms_source_port, port))
                oms_source_port = None
        elif node_role != OpticalNodeRole.AMPLIFIER:
            msg = f"Unexpected node role in optical path: {node_role}"
            raise ValueError(msg)

    if oms_source_port is not None:
        msg = "Optical path does not end with a ROADM device"
        raise ValueError(msg)

    return omses


def _explicit_route_from_omses(
    omses: list[tuple[AnyOpticalPortBlockProvisioning, AnyOpticalPortBlockProvisioning]],
) -> list[tuple[str, str, str, str]]:
    """Build the OEL explicit route (list of OMS hops) from the given OMS port pairs."""
    explicit_route: list[tuple[str, str, str, str]] = []
    for src_port, dst_port in omses:
        src_node = _as_flexils_block(src_port.optical_port_host_node)
        dst_node = _as_flexils_block(dst_port.optical_port_host_node)

        src_node_name = _node_id(src_node)
        dst_node_name = _node_id(dst_node)

        src_port_name = _oteintf_from_port_name(src_node, _port_name(src_port))
        dst_port_name = _oteintf_from_port_name(dst_node, _port_name(dst_port))

        explicit_route.append((src_node_name, src_port_name, dst_node_name, dst_port_name))
    return explicit_route


def _delete_oel_if_unused(flex: FlexilsClientProtocol, oel_aid: str) -> None:
    """Delete the given OEL only when no OSNC on the node still references it.

    On FlexILS the same OEL may be shared by more than one OSNC, so deleting it while
    it is still referenced would break those circuits. The node is queried with
    RTRV-OSNC first; if any OSNC references the OEL, it is left in place (no-op). A
    node with no OSNC at all is a legitimate end-state (the last OSNC was just
    deleted): the device denies RTRV-OSNC with the "object does not exist" marker in
    that case, which is treated as "nothing references the OEL", not as an error.

    Once no OSNC references the OEL, the OEL is locked (put OOS) and only then
    deleted: FlexILS refuses DLT-OEL with "OEL is not Locked" otherwise.

    Args:
        flex: TL1 client of the node hosting the OEL.
        oel_aid: Access identifier of the OEL.
    """
    aid = oel_aid[:127]
    try:
        osncs = flex.rtrv_osnc().parsed_data
    except TL1CommandDeniedError as e:
        if not _is_object_missing(e):
            raise
        osncs = []
    for record in osncs:
        if record.get("OELAID", "").strip(r"\" ") == aid[:64]:
            return
    flex.ed_oel(aid=aid, is_oos_ains="OOS")
    flex.dlt_oel(aid=aid)


def delete_oel(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    circuit_identifier: str,
) -> DiffResult:
    """Delete the OEL of the given circuit on the node, when no other OSNC uses it.

    The OEL explicit route cannot be edited with ED-OEL, so a path change is applied
    by deleting the OEL and re-entering it (see :func:`deploy`). This helper performs
    the guarded deletion: it leaves the OEL in place while another OSNC on the node
    still references it (a shared OEL is legitimate on FlexILS), locks it (OOS) once
    no OSNC references it, and only then deletes it. When the OEL is already absent
    the call is a no-op yielding an empty diff, so a retried or partially applied
    teardown is safe (idempotent).

    Args:
        optical_node_block: The Optical Node block hosting the OEL.
        circuit_identifier: The circuit identifier used as OEL AID.

    Returns:
        The difference between the OEL configuration before and after the
        deletion: a deleted OEL shows up as a removal, while an OEL kept because
        another OSNC still references it (or already absent) yields an empty diff.
    """
    oel_aid = circuit_identifier[:127]
    flex = _get_flex_client(optical_node_block)
    before_oel = _rtrv_oel_or_none(flex, oel_aid)
    if before_oel is not None:
        _delete_oel_if_unused(flex, circuit_identifier)
    after_oel = _rtrv_oel_or_none(flex, oel_aid)
    return compare_jsons({"OEL": before_oel or {}}, {"OEL": after_oel or {}})


def _find_or_create_oel(
    oel_aid: str,
    source_device: NokiaFlexIlsBlockProvisioning,
    dest_device: NokiaFlexIlsBlockProvisioning,
    omses: list[tuple[AnyOpticalPortBlockProvisioning, AnyOpticalPortBlockProvisioning]],
) -> dict[str, Any]:
    """Find an existing OEL (Optical Engineered Lightpath) or create a new one.

    The OEL access identifier is derived from the circuit identifier (the
    subscription instance id of the circuit) instead of GARR pop codes.

    Args:
        oel_aid: The circuit identifier used as OEL AID.
        source_device: The source Optical Node block.
        dest_device: The destination Optical Node block.
        omses: The OMS port pairs representing the path.

    Returns:
        The OEL configuration data.

    Raises:
        ValueError: If the circuit identifier is empty or the FlexILS commands fail.
    """
    if not oel_aid:
        msg = "An OEL access identifier is required to create or retrieve an OEL"
        raise ValueError(msg)

    aid = oel_aid[:127]
    flex = _get_flex_client(source_device)
    existing = _rtrv_oel_or_none(flex, aid)
    if existing is not None:
        return existing

    src_name = _node_id(source_device)
    dst_name = _node_id(dest_device)
    oel_label = f"{src_name}-{dst_name}"

    explicit_route = _explicit_route_from_omses(omses)

    flex.ent_oel(
        aid=aid,
        label=oel_label,
        srcnodename=src_name,
        dstnodename=dst_name,
        explicitroute=explicit_route,
        validfrangelist=[191325000, 196125000],
    )
    flex.opr_valroute_oel(aid=aid)

    response = flex.rtrv_oel(aid=aid)
    if not response.parsed_data:
        msg = f"RTRV-OEL returned no data for aid {aid}"
        raise ValueError(msg)
    return response.parsed_data[0]


def _oteintf_from_port_name(device: NokiaFlexIlsBlockProvisioning, port_name: str) -> str:
    """Find the Optical Traffic Engineering Interface (OTEINTF) corresponding to the given physical port name."""
    device_name = _node_id(device)
    flex = _get_flex_client(device)
    ote_intfs = flex.rtrv_oteintf().parsed_data
    osc_port = port_name.replace("L", "O")

    for intf in ote_intfs:
        if intf["AID"] == osc_port:
            return port_name
        if intf["ASSOCGCC"] == osc_port:
            return intf["AID"]

    msg = f"Could not find the OTEINTF for port {port_name} on device {device_name}"
    raise ValueError(msg)


def _find_fbm_port_if_fmm_port(flex: FlexilsClientProtocol, port_name: str) -> str:
    """Return the FBM port corresponding to the given FMM port, if any."""
    card_aid = "-".join(port_name.split("-")[:-1])
    card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]

    if card["TYPE"] != "FMMC12":
        return port_name

    chassis_sn = flex.rtrv_eqpt(aid="1").parsed_data[0]["SERNO"]
    target_provowremptp = f"{chassis_sn}/{card_aid}-L1"

    fbm_scgs = flex.rtrv_scg(type="FBM").parsed_data
    for scg in fbm_scgs:
        if scg.get("PROVOWREMPTP", "") == target_provowremptp:
            return scg["AID"]

    msg = f"Could not find the FBM port associated to the FMM {card_aid} on device {flex.tid}"
    raise ValueError(msg)


def _get_flexils_name_client_tributary(
    device: NokiaFlexIlsBlockProvisioning,
    port_name: str,
) -> tuple[str, FlexilsClientProtocol, str]:
    """Extract node name, flex client, and tributary endpoint for the given port."""
    node_name = _node_id(device)
    flex = _get_flex_client(device)
    fbm_port = _find_fbm_port_if_fmm_port(flex, port_name)
    return node_name, flex, fbm_port


def _rtrv_all_osnc_or_empty(flex: FlexilsClientProtocol) -> list[dict[str, Any]]:
    """Return every OSNC of the node, or an empty list when the node has none.

    A node without any OSNC denies ``RTRV-OSNC`` with the "object does not exist"
    marker; that is a legitimate empty state (e.g. the last OSNC was deleted or, on a
    remote node, the circuit is controlled from the other end), not an error.

    Args:
        flex: TL1 client of the node to query.

    Returns:
        The parsed OSNC records of the node, or an empty list.
    """
    try:
        return list(flex.rtrv_osnc().parsed_data)
    except TL1CommandDeniedError as e:
        if not _is_object_missing(e):
            raise
        return []


def _match_osnc(
    existing_osncs: list[dict[str, Any]],
    circuit_identifier: str,
    src_port_name: str,
    dst_port_name: str,
    dst_node_name: str,
    passband: Passband | None = None,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    osnc_label: str | None = None,
    oel_aid: str | None = None,
) -> dict[str, Any] | None:
    """Return the first OSNC of the given records matching the requested circuit.

    The match is by tributary ports (the ``-<id>`` suffix stripped), remote node and
    circuit identifier, optionally narrowed by label, OEL reference, passband and
    carrier. Pure function over pre-fetched records: no device access.

    Args:
        existing_osncs: The OSNC records to search.
        circuit_identifier: The expected OSNC CKTIDSUFFIX.
        src_port_name: The local tributary port name (without superchannel suffix).
        dst_port_name: The remote tributary port name (without superchannel suffix).
        dst_node_name: The expected remote node name.
        passband: Optional passband the OSNC must carry.
        carrier: Optional carrier the OSNC must carry.
        osnc_label: Optional label the OSNC must contain.
        oel_aid: Optional OEL access identifier the OSNC must reference.

    Returns:
        The first matching OSNC record, or ``None``.
    """
    for osnc in existing_osncs:
        if not (
            src_port_name == "-".join(osnc.get("LOCENDPOINT", "").split("-")[:-1])
            and dst_port_name == "-".join(osnc.get("REMENDPOINT", "").split("-")[:-1])
            and osnc.get("REMNODETID") == dst_node_name
        ):
            continue

        if osnc.get("CKTIDSUFFIX", "").strip(r"\" ") != circuit_identifier:
            continue

        if osnc_label is not None and osnc_label not in osnc.get("LABEL", ""):
            continue
        if oel_aid is not None and osnc.get("OELAID", "").strip(r"\" ") != oel_aid[:64]:
            continue

        if passband is not None:
            osnc_pb = osnc.get("PASSBANDLIST", [])
            if len(osnc_pb) != len(passband) or not all(int(x) == y for x, y in zip(osnc_pb, passband, strict=False)):
                continue

        if carrier is not None:
            osnc_carrier = osnc.get("CARRIERLIST", [])
            if len(osnc_carrier) != len(carrier) or not all(
                int(x) == y for x, y in zip(osnc_carrier, carrier, strict=False)
            ):
                continue

        return osnc

    return None


def _find_matching_osnc_on_flexils(
    client: FlexilsClientProtocol,
    circuit_identifier: str,
    src_port_name: str,
    dst_port_name: str,
    dst_node_name: str,
    passband: Passband | None = None,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    osnc_label: str | None = None,
    oel_aid: str | None = None,
) -> dict[str, Any] | None:
    """Query a device and find a matching OSNC safely."""
    return _match_osnc(
        _rtrv_all_osnc_or_empty(client),
        circuit_identifier,
        src_port_name,
        dst_port_name,
        dst_node_name,
        passband,
        carrier,
        osnc_label,
        oel_aid,
    )


def _osnc_endpoint_aids(osncs: list[dict[str, Any]]) -> set[str]:
    """Return the endpoint AIDs used by the given OSNC records.

    Both the local (``LOCENDPOINT``) and remote (``REMENDPOINT``) AIDs occupy the
    ``<port>-<id>`` endpoint namespace of their node: an id must not be reused for a
    new OSNC on the same tributary port even when no superchannel object exists for
    it anymore (a dangling pre-provisioned OSNC has endpoints but no superchannels).

    Args:
        osncs: The OSNC records to collect the endpoints from.

    Returns:
        The non-empty endpoint AIDs of the records.
    """
    aids: set[str] = set()
    for osnc in osncs:
        for key in ("LOCENDPOINT", "REMENDPOINT"):
            aid = osnc.get(key, "")
            if aid:
                aids.add(str(aid))
    return aids


def _find_or_create_osnc(
    src_device: NokiaFlexIlsBlockProvisioning,
    dst_device: NokiaFlexIlsBlockProvisioning,
    circuit_identifier: str,
    osnc_label: str,
    oel_aid: str,
    src_port_name: str,
    dst_port_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
) -> tuple[dict[str, Any], bool]:
    """Find an existing OSNC on the source device or create a new one.

    The OSNC CKTIDSUFFIX is the circuit identifier (the subscription instance id
    of the circuit) instead of the spectrum name.

    The new endpoint ids avoid every ``<port>-<id>`` AID already used as an OSNC
    endpoint on either node (not just the existing superchannels): the same tributary
    port carries up to 128 logical channels, so a foreign OSNC on ``<port>-1`` must
    push the new circuit to ``<port>-2`` instead of colliding with it. A spectral
    overlap with that foreign circuit is left to the device: ``ENT-OSNC`` itself is
    denied then, and that denial propagates untouched. After entering, the re-read
    record is verified to carry the requested circuit identifier: an ``ENT-OSNC``
    denied with "already exists" does not raise on the TL1 wire, so without this
    check a foreign occupant would be mistaken for the created circuit.

    Raises:
        ValueError: If the circuit identifier is empty, if the re-read record carries
            another circuit identifier (endpoint occupied by a foreign OSNC), or if the
            FlexILS commands fail.

    Returns:
        The OSNC record and whether it was created (``False`` when it was found).
    """
    if not circuit_identifier:
        msg = "An OSNC circuit identifier is required to create or retrieve an OSNC"
        raise ValueError(msg)

    _src_node_name, src_flex, src_port_name = _get_flexils_name_client_tributary(src_device, src_port_name)
    dst_node_name, dst_flex, dst_port_name = _get_flexils_name_client_tributary(dst_device, dst_port_name)

    oel_aid = oel_aid[:127]

    src_osncs = _rtrv_all_osnc_or_empty(src_flex)
    osnc = _match_osnc(
        src_osncs,
        circuit_identifier,
        src_port_name,
        dst_port_name,
        dst_node_name,
        passband,
        carrier,
        osnc_label,
        oel_aid,
    )

    if osnc is not None:
        return osnc, False

    occupied_aids = _osnc_endpoint_aids(src_osncs) | _osnc_endpoint_aids(_rtrv_all_osnc_or_empty(dst_flex))
    dst_sch_id = _find_first_free_endpoint_id(dst_flex, dst_port_name, occupied_aids)
    src_sch_id = _find_first_free_endpoint_id(src_flex, src_port_name, occupied_aids)

    src_endpoint = f"{src_port_name}-{src_sch_id}"
    dst_endpoint = f"{dst_port_name}-{dst_sch_id}"

    src_flex.ent_osnc(
        aid=src_endpoint,
        label=_tl1_label(osnc_label),
        remnodetid=dst_node_name,
        remendpoint=dst_endpoint,
        oelaid=oel_aid,
        cktidsuffix=circuit_identifier,
        passbandlist=passband,
        carrierlist=carrier,
    )

    sleep(3)

    response = src_flex.rtrv_osnc(aid=src_endpoint)
    if not response.parsed_data:
        msg = f"RTRV-OSNC returned no data for aid {src_endpoint}"
        raise ValueError(msg)
    created = response.parsed_data[0]
    if created.get("CKTIDSUFFIX", "").strip(r"\" ") != circuit_identifier:
        occupant = created.get("CKTIDSUFFIX", "").strip(r"\" ")
        occupant_label = created.get("LABEL", "").strip(r"\" ")
        msg = (
            f"OSNC endpoint {src_endpoint} is occupied by another circuit "
            f"(CKTIDSUFFIX={occupant!r}, LABEL={occupant_label!r}); "
            f"cannot create circuit {circuit_identifier!r} there"
        )
        raise ValueError(msg)
    return created, True


def _find_first_free_endpoint_id(flex: FlexilsClientProtocol, port_name: str, occupied_aids: set[str]) -> int:
    """Find the first available endpoint ID for a new OSNC on the given tributary port.

    An id is available only when no superchannel object exists for ``<port>-<id>`` and
    no OSNC on either end of the section uses it as an endpoint: OSNC endpoints live
    past their superchannels (a dangling pre-provisioned OSNC has endpoints but no
    superchannels), and the same tributary port carries up to 128 logical channels, so
    reusing an occupied id makes ``ENT-OSNC`` collide with the foreign circuit.

    Args:
        flex: TL1 client of the node hosting the tributary port.
        port_name: The tributary port name (without superchannel suffix).
        occupied_aids: Endpoint AIDs already used as OSNC endpoints on either node.

    Returns:
        The first free superchannel/endpoint id.

    Raises:
        ValueError: If no free id exists for the port.
    """
    min_sch_id = 1
    max_sch_id = 128
    for i in range(min_sch_id, max_sch_id + 1):
        if f"{port_name}-{i}" in occupied_aids:
            continue
        try:
            flex.rtrv_sch(aid=f"{port_name}-{i}")
        except TL1CommandDeniedError as e:
            if _is_object_missing(e):
                return i
            raise
    msg = f"Could not find a free superchannel index for port {port_name}"
    raise ValueError(msg)


def _find_first_free_sch_id(flex: FlexilsClientProtocol, port_name: str) -> int:
    """Find the first available superchannel ID for the given port."""
    return _find_first_free_endpoint_id(flex, port_name, set())


def _open_shutter(device: NokiaFlexIlsBlockProvisioning, sch_aid: str) -> None:
    """Open the shutter of the given superchannel on the given device."""
    flex = _get_flex_client(device)
    flex.put_maintenance(aidtype="SCH", aid=sch_aid)
    flex.ed_sch(aid=sch_aid, shutterstate="OPEN")
    flex.rst_maintenance(aidtype="SCH", aid=sch_aid)


def _find_flexils_osnc(
    optical_spectrum_name: str,
    optical_spectrum_section: OpticalSpectrumSectionBlockProvisioning,
    passband: Passband | None = None,
    circuit_identifier: str = "",
) -> tuple[FlexilsClientProtocol, dict[str, Any]]:
    """Find an existing OSNC between the two FlexILS devices of the given section.

    The OSNC is matched by its CKTIDSUFFIX, which is the circuit identifier (the
    subscription instance id of the circuit) when provided; otherwise the
    spectrum name is used as a fallback, plus the local/remote endpoints and the
    remote node. The passband is deliberately *not* part of the match: the
    circuit identifier already identifies the OSNC uniquely, while the passband
    stored in the subscription can legitimately differ from the device during a
    retried modify (the device is updated before the database transaction is
    committed, see :func:`modify`), so matching on it would make retries fail to
    find the OSNC. ``passband`` is only used to build the error message.

    Args:
        optical_spectrum_name: The user-facing name of the optical spectrum.
        optical_spectrum_section: The optical spectrum section block.
        passband: The passband of the optical spectrum, used only in the error message.
        circuit_identifier: The subscription instance id of the circuit; used as the CKTIDSUFFIX.

    Returns:
        The FlexILS client of the device controlling the OSNC and the OSNC configuration.

    Raises:
        _OsncNotFoundError: If no matching OSNC is found (a ``ValueError`` subclass).
    """
    src_port_raw = _port_name(optical_spectrum_section.optical_spectrum_section_add_drop_ports[0])
    dst_port_raw = _port_name(optical_spectrum_section.optical_spectrum_section_add_drop_ports[1])
    src_device = _as_flexils_block(
        optical_spectrum_section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
    )
    dst_device = _as_flexils_block(
        optical_spectrum_section.optical_spectrum_section_add_drop_ports[1].optical_port_host_node
    )

    src_node_name, src_flex, src_port = _get_flexils_name_client_tributary(src_device, src_port_raw)
    dst_node_name, dst_flex, dst_port = _get_flexils_name_client_tributary(dst_device, dst_port_raw)

    osnc_name = circuit_identifier if circuit_identifier else optical_spectrum_name.replace(" ", "_").strip(r"\" ")

    # Attempt A -> Z
    osnc = _find_matching_osnc_on_flexils(
        client=src_flex,
        circuit_identifier=osnc_name,
        src_port_name=src_port,
        dst_port_name=dst_port,
        dst_node_name=dst_node_name,
    )
    if osnc is not None:
        return src_flex, osnc

    # Attempt Z -> A (swap src and dst parameters)
    osnc = _find_matching_osnc_on_flexils(
        client=dst_flex,
        circuit_identifier=osnc_name,
        src_port_name=dst_port,
        dst_port_name=src_port,
        dst_node_name=src_node_name,  # Notice dst is now src_node_name
    )
    if osnc is not None:
        return dst_flex, osnc

    msg = (
        f"Could not find the OSNC for spectrum '{osnc_name}' between "
        f"{src_node_name} {src_port} and {dst_node_name} {dst_port} "
        f"with passband {passband}. "
    )
    raise _OsncNotFoundError(msg)


def _osnc_matches(
    osnc: dict[str, Any],
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    oel_aid: str,
    label: str,
) -> tuple[bool, bool, bool]:
    """Return the ``(oel, spectrum, label)`` match flags of an OSNC against the desired state.

    Args:
        osnc: The OSNC record retrieved from the device.
        passband: The desired frequency range allowed for transmission.
        carrier: The desired ``(central frequency, bandwidth)`` carrier signal.
        oel_aid: The desired OEL access identifier (full length; compared truncated to 64 chars).
        label: The desired OSNC label (unquoted; compared stripped of surrounding quotes/whitespace).

    Returns:
        A triple of booleans telling whether the OEL reference, the
        passband/carrier pair and the label already match the desired state.
    """
    matches_oel = osnc.get("OELAID", "").strip(r"\" ") == oel_aid[:64]
    osnc_passband = osnc.get("PASSBANDLIST", [])
    osnc_carrier = osnc.get("CARRIERLIST", [])
    matches_spectrum = (
        len(osnc_passband) == len(passband)
        and all(int(x) == y for x, y in zip(osnc_passband, passband, strict=False))
        and len(osnc_carrier) == len(carrier)
        and all(int(x) == y for x, y in zip(osnc_carrier, carrier, strict=False))
    )
    matches_label = osnc.get("LABEL", "").strip(r"\" ") == label.strip()
    return matches_oel, matches_spectrum, matches_label


def _remote_flex_for_section(
    flex: FlexilsClientProtocol,
    optical_spectrum_section: OpticalSpectrumSectionBlockProvisioning,
) -> FlexilsClientProtocol:
    """Return the FlexILS client of the node at the far end of the given section.

    Args:
        flex: The FlexILS client of the local node.
        optical_spectrum_section: The optical spectrum section block.

    Returns:
        The FlexILS client of the far-end node; the given client itself when no
        other node is found in the section.
    """
    remote_flex = flex
    for port in optical_spectrum_section.optical_spectrum_section_add_drop_ports:
        od = port.optical_port_host_node
        if _node_id(od) == flex.tid:
            continue
        remote_flex = _get_flex_client(od)
    return remote_flex


def _converge_osnc(
    flex: FlexilsClientProtocol,
    osnc: dict[str, Any],
    oel_aid: str,
    osnc_name: str,
    osnc_label: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    circuit_identifier: str,
) -> tuple[bool, bool, bool]:
    """Converge a present OSNC to the desired state, honouring the admin-state rule.

    ``PASSBANDLIST``/``CARRIERLIST``/``OELAID`` are only editable while the OSNC
    is already out of service, so an OOS-param drift first locks the OSNC with a
    bare ``ED-OSNC:::OOS`` and only then edits the drifted OOS params (each sent
    only when it drifted) while locked. ``CKTIDSUFFIX``/``LABEL`` are
    in-service edits applied in the final ``ED-OSNC … :IS`` step, which also
    unlocks the circuit; a label-only drift therefore stays a single
    in-service command. When the OOS edit fails, the lock is best-effort
    restored to ``IS`` before the original error propagates.

    Args:
        flex: TL1 client of the node controlling the OSNC.
        osnc: The OSNC record retrieved from the device.
        oel_aid: The desired OEL access identifier (sent only on OEL drift).
        osnc_name: The desired OSNC CKTIDSUFFIX.
        osnc_label: The desired OSNC label.
        passband: The desired frequency range allowed for transmission (sent
            only on spectrum drift, together with the carrier).
        carrier: The desired ``(central frequency, bandwidth)`` carrier signal.
        circuit_identifier: The subscription instance id of the circuit, used in
            log records.

    Returns:
        The ``(oel, spectrum, label)`` match flags, for the caller to decide
        whether a re-read is needed.
    """
    matches_oel, matches_spectrum, matches_label = _osnc_matches(osnc, passband, carrier, oel_aid, osnc_label)
    oos_drift = not matches_oel or not matches_spectrum
    logger.debug(
        "Converging FlexILS optical circuit",
        locendpoint=osnc["LOCENDPOINT"],
        circuit_identifier=circuit_identifier,
        matches_oel=matches_oel,
        matches_spectrum=matches_spectrum,
        matches_label=matches_label,
        actual_oelaid=osnc.get("OELAID", ""),
        expected_oelaid=oel_aid[:64],
        actual_passband=osnc.get("PASSBANDLIST", []),
        expected_passband=list(passband),
    )

    if oos_drift:
        # Lock first: the device denies OOS params combined with the lock
        # transition in a single command (``OELAid cannot be updated when Admin
        # state is not locked``).
        flex.ed_osnc(aid=osnc["LOCENDPOINT"], is_oos="OOS")
        oos_params: dict[str, Any] = {"aid": osnc["LOCENDPOINT"], "is_oos": "OOS"}
        if not matches_oel:
            oos_params["oelaid"] = oel_aid
        if not matches_spectrum:
            oos_params["passbandlist"] = passband
            oos_params["carrierlist"] = carrier
        try:
            flex.ed_osnc(**oos_params)
        except Exception:
            logger.warning(
                "OOS optical-circuit edit failed, restoring the circuit in service",
                locendpoint=osnc["LOCENDPOINT"],
                circuit_identifier=circuit_identifier,
            )
            try:
                flex.ed_osnc(aid=osnc["LOCENDPOINT"], is_oos="IS")
            except Exception:
                logger.exception(
                    "Failed to restore the optical circuit in service after a failed edit",
                    locendpoint=osnc["LOCENDPOINT"],
                    circuit_identifier=circuit_identifier,
                )
            raise
    if oos_drift or not matches_label:
        flex.ed_osnc(
            aid=osnc["LOCENDPOINT"],
            cktidsuffix=osnc_name,
            is_oos="IS",
            label=_tl1_label(osnc_label),
        )
        sleep(3)
    return matches_oel, matches_spectrum, matches_label


def delete(
    optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    circuit_identifier: str = "",
) -> DiffResult:
    """Delete an optical circuit specifically for FlexILS platform devices.

    The operation is idempotent: a circuit whose OSNC is already gone (for instance
    because the terminal nodes were torn down beforehand) is treated as already
    deleted and yields an empty diff instead of failing.

    Returns:
        The difference between the circuit configuration before and after the
        deletion: the deleted OSNC shows up as a removal, while an already absent
        OSNC yields an empty diff.
    """
    try:
        flex, osnc = _find_flexils_osnc(
            optical_spectrum_name,
            optical_spectrum_section_block,
            passband,
            circuit_identifier,
        )
    except _OsncNotFoundError:
        return compare_jsons({}, {})

    # Lock the OSNC in admin state
    flex.ed_osnc(aid=osnc["LOCENDPOINT"], is_oos="OOS")

    # Delete the OSNC
    flex.dlt_osnc(aid=osnc["LOCENDPOINT"])

    return compare_jsons({"OSNC": osnc}, {"OSNC": {}})


def validate(
    optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str,
    circuit_identifier: str = "",
) -> None:
    """Validate the optical spectrum section configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        optical_spectrum_section_block: The optical spectrum section to validate.
        optical_spectrum_name: Name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Service label to validate.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Raises:
        ValueError: If the configuration is invalid.
    """
    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section_block,
        passband,
        circuit_identifier,
    )  # already raises error if CKTIDSUFFIX/LOCENDPOINT/REMENDPOINT do not match

    remote_flex = _remote_flex_for_section(flex, optical_spectrum_section_block)

    errors = []

    actual_passband = tuple(int(x) for x in osnc.get("PASSBANDLIST", []))
    if actual_passband != tuple(passband):
        errors.append(f"Passband mismatch: expected {tuple(passband)}, got {actual_passband}")

    actual_carrier = tuple(int(x) for x in osnc.get("CARRIERLIST", []))
    expected_carrier = carrier
    if actual_carrier != expected_carrier:
        errors.append(f"Carrier mismatch: expected {expected_carrier}, got {actual_carrier}")

    actual_label = osnc.get("LABEL", "").strip(r"\" ")
    if actual_label != label.strip():
        errors.append(f"Label mismatch: expected '{label.strip()}', got '{actual_label}'")

    local_shutter = flex.rtrv_sch(aid=osnc["LOCENDPOINT"]).parsed_data[0]
    if local_shutter.get("SHUTTERSTATE") != "OPEN":
        errors.append(f"Local shutter not OPEN: {local_shutter.get('SHUTTERSTATE')}")

    remote_shutter = remote_flex.rtrv_sch(aid=osnc["REMENDPOINT"]).parsed_data[0]
    if remote_shutter.get("SHUTTERSTATE") != "OPEN":
        errors.append(f"Remote shutter not OPEN: {remote_shutter.get('SHUTTERSTATE')}")

    if errors:
        msg = f"OSNC validation failed for {optical_spectrum_name}: " + "; ".join(errors)
        raise ValueError(msg)


def set_label(
    source_optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    label: str,
    circuit_identifier: str = "",
) -> DiffResult:
    """Overwrite the OSNC label of the given optical spectrum section.

    The composite digital-service circuit label (``"<channel>: <svcA> + <svcB>"``)
    is always written in full, so reused channels converge to the expected value
    and reconcile repairs drift instead of accumulating tokens. The label is
    double-quoted on the TL1 wire so the ``":"`` separator survives command framing.

    Args:
        source_optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        label: The full label to write.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Returns:
        The difference between the OSNC configuration before and after the update.

    Raises:
        ValueError: If the OSNC cannot be found.
    """
    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section_block,
        passband,
        circuit_identifier,
    )
    before_osnc = osnc
    new_label = label.strip()
    if not new_label:
        msg = "Cannot set an empty optical circuit label"
        raise ValueError(msg)
    flex.ed_osnc(aid=osnc["LOCENDPOINT"], label=_tl1_label(new_label))
    after_osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]

    return compare_jsons({"OSNC": before_osnc}, {"OSNC": after_osnc})


def ensure(
    optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    circuit_identifier: str = "",
) -> DiffResult:
    """Ensure the optical circuit of a section exists and converges to the desired state.

    This is the single idempotent primitive for every FlexILS optical-circuit
    write: create, modify and reconcile all flow through it. The OSNC is looked
    up by identity only (circuit identifier plus endpoints, either direction,
    see :func:`_find_flexils_osnc`): the label, passband, carrier and OEL
    reference are convergent attributes, never part of the identity. A missing
    OEL or OSNC is created (lock-free: ``ENT-OSNC`` needs no admin-state
    transition); a present OSNC whose attributes drifted is edited in place;
    shutters are reopened when closed. A circuit already in the desired state
    yields an empty diff and issues no device write.

    Device admin-state rule: ``PASSBANDLIST``/``CARRIERLIST``/``OELAID`` are only
    editable while the OSNC is already out of service, so an OOS-param drift
    first locks the OSNC with a bare ``ED-OSNC:::OOS`` and only then edits the
    drifted OOS params (each sent only when it drifted) while locked — the
    device denies them combined with the lock transition in a single command
    (``OELAid cannot be updated when Admin state is not locked``).
    ``CKTIDSUFFIX``/``LABEL`` are in-service edits and are always applied in the
    final ``ED-OSNC … :IS`` step, which also unlocks the circuit. A label-only
    drift therefore stays a single in-service command with no traffic impact.
    When the OOS edit fails, the lock is best-effort restored to ``IS`` before
    the original error propagates, so a failed converge never leaves the
    circuit out of service. Unlike :func:`set_label` (which raises when the
    OSNC is absent), ``ensure`` both heals a deleted OSNC and converges a stale
    label without duplicating.

    Args:
        optical_node_block: The Optical Node block hosting the OEL (source of the section).
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Optional label for the circuit.
        circuit_identifier: The subscription instance id of the circuit; used to derive the
            device-side OEL AID and OSNC CKTIDSUFFIX.

    Returns:
        The difference between the circuit configuration before and after the call.

    Raises:
        ValueError: If the circuit identifier is empty or the FlexILS commands fail.
    """
    add_drop_ports = optical_spectrum_section_block.optical_spectrum_section_add_drop_ports
    express_ports = optical_spectrum_section_block.optical_spectrum_section_express_ports

    src_device = _as_flexils_block(add_drop_ports[0].optical_port_host_node)
    dst_device = _as_flexils_block(add_drop_ports[1].optical_port_host_node)
    src_flexils_name = _node_id(src_device)
    dst_flexils_name = _node_id(dst_device)

    oel_aid = circuit_identifier[:127]
    osnc_label = f"{src_flexils_name}_{dst_flexils_name}" if label in (None, "") else label.strip()
    osnc_name = circuit_identifier or optical_spectrum_name.replace(" ", "_")

    src_flex = _get_flex_client(src_device)
    before_oel = _rtrv_oel_or_none(src_flex, oel_aid)
    if before_oel is None:
        omses = _omses_from_line_ports(express_ports)
        oel = _find_or_create_oel(oel_aid, src_device, dst_device, omses)
    else:
        oel = before_oel

    for port in add_drop_ports:
        _ensure_manualmode2(port)

    try:
        flex, osnc = _find_flexils_osnc(
            optical_spectrum_name, optical_spectrum_section_block, passband, circuit_identifier
        )
    except _OsncNotFoundError:
        created, _ = _find_or_create_osnc(
            src_device=src_device,
            dst_device=dst_device,
            circuit_identifier=circuit_identifier,
            osnc_label=osnc_label,
            oel_aid=oel_aid,
            src_port_name=_port_name(add_drop_ports[0]),
            dst_port_name=_port_name(add_drop_ports[1]),
            passband=passband,
            carrier=carrier,
        )
        sleep(5)
        _open_shutter(src_device, created["LOCENDPOINT"])
        _open_shutter(dst_device, created["REMENDPOINT"])
        after_osnc = src_flex.rtrv_osnc(aid=created["LOCENDPOINT"]).parsed_data[0]
        return compare_jsons(
            {"OEL": before_oel or {}, "OSNC": {}},
            {"OEL": oel, "OSNC": after_osnc},
        )

    before_osnc = osnc
    remote_flex = _remote_flex_for_section(flex, optical_spectrum_section_block)
    matches_oel, matches_spectrum, matches_label = _converge_osnc(
        flex,
        osnc,
        oel_aid,
        osnc_name,
        osnc_label,
        passband,
        carrier,
        circuit_identifier,
    )

    local_shutter = flex.rtrv_sch(aid=osnc["LOCENDPOINT"]).parsed_data[0]
    remote_shutter = remote_flex.rtrv_sch(aid=osnc["REMENDPOINT"]).parsed_data[0]
    if local_shutter.get("SHUTTERSTATE") != "OPEN" or remote_shutter.get("SHUTTERSTATE") != "OPEN":
        flex.put_maintenance(aidtype="SCH", aid=osnc["LOCENDPOINT"])
        flex.ed_sch(aid=osnc["LOCENDPOINT"], shutterstate="OPEN")
        flex.rst_maintenance(aidtype="SCH", aid=osnc["LOCENDPOINT"])
        remote_flex.put_maintenance(aidtype="SCH", aid=osnc["REMENDPOINT"])
        remote_flex.ed_sch(aid=osnc["REMENDPOINT"], shutterstate="OPEN")
        remote_flex.rst_maintenance(aidtype="SCH", aid=osnc["REMENDPOINT"])

    if matches_oel and matches_spectrum and matches_label:
        after_osnc = before_osnc
        if local_shutter.get("SHUTTERSTATE") == "OPEN" and remote_shutter.get("SHUTTERSTATE") == "OPEN":
            return compare_jsons(
                {"OEL": before_oel or {}, "OSNC": before_osnc},
                {"OEL": oel, "OSNC": after_osnc},
            )
    after_osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]
    return compare_jsons(
        {"OEL": before_oel or {}, "OSNC": before_osnc},
        {"OEL": oel, "OSNC": after_osnc},
    )


def create_cross_connection(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    from_port: AnyOpticalPortBlockProvisioning,
    to_port: AnyOpticalPortBlockProvisioning,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str | None = None,
    circuit_name: str | None = None,  # noqa: ARG001
    circuit_identifier: str = "",
) -> DiffResult:
    """Create an optical cross connection on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        from_port: The Optical Port block to connect from.
        to_port: The Optical Port block to connect to.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Label for the connection.
        circuit_name: Deprecated; kept for backwards compatibility, device-side circuit
            identifiers are derived from `circuit_identifier`.
        circuit_identifier: The subscription instance id of the circuit; used as the OCRS CKTIDSUFFIX.

    Returns:
        The difference between the cross connection configuration before and after
        the creation: a freshly created cross connection shows up as an addition,
        while one already present yields an empty diff.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross connection cannot be created.
    """
    from_port_name = _port_name(from_port)
    to_port_name = _port_name(to_port)

    if label:
        label = rf'"{label}"'

    if carrier is None:
        carrier = ((passband[0] + passband[-1]) // 2, passband[-1] - passband[0])

    if "S" in to_port_name:
        # let's use the system port as from_port
        to_port_name, from_port_name = from_port_name, to_port_name

    flex = _get_flex_client(optical_node_block)

    from_sch_id = _find_first_free_sch_id(flex, from_port_name)
    to_sch_id = _find_first_free_sch_id(flex, to_port_name)

    fromaid = f"{from_port_name}-{from_sch_id}"
    toaid = f"{to_port_name}-{to_sch_id}"

    before_ocrs = _rtrv_ocrs_or_none(flex, fromaid, toaid)

    flex.ent_ocrs(
        fromaid=fromaid,
        toaid=toaid,
        label=label,
        cktidsuffix=circuit_identifier,
        freqslotplantype="FREQ-SLOT-PLAN-NONE",
        schoffset="0",
        passbandlist=passband,
        carrierlist=carrier,
        autoretunelmsch="DISABLED",
        intracarrspecshaping="ENABLED",
    )

    flex.put_maintenance(aidtype="SCH", aid=fromaid)
    flex.ed_sch(aid=fromaid, shutterstate="OPEN")
    flex.rst_maintenance(aidtype="SCH", aid=fromaid)

    after_ocrs = flex.rtrv_ocrs(fromaid=fromaid, toaid=toaid).parsed_data[0]
    return compare_jsons({"OCRS": before_ocrs or {}}, {"OCRS": after_ocrs})


def delete_cross_connection(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    from_port: AnyOpticalPortBlockProvisioning,
    to_port: AnyOpticalPortBlockProvisioning,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str | None = None,
    circuit_name: str | None = None,  # noqa: ARG001
    circuit_identifier: str = "",
) -> DiffResult:
    """Delete an optical cross connection on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        from_port: The Optical Port block to disconnect from.
        to_port: The Optical Port block to disconnect to.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Label of the connection.
        circuit_name: Deprecated; kept for backwards compatibility, device-side circuit
            identifiers are derived from `circuit_identifier`.
        circuit_identifier: The subscription instance id of the circuit; used as the OCRS CKTIDSUFFIX.

    Returns:
        The difference between the cross connection configuration before and after
        the deletion: the deleted OCRS shows up as a removal.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross connection cannot be found.
    """
    from_port_name = _port_name(from_port)
    to_port_name = _port_name(to_port)

    if carrier is None:
        carrier = ((passband[0] + passband[-1]) // 2, passband[-1] - passband[0])

    if "S" in to_port_name:
        # let's use the system port as from_port
        to_port_name, from_port_name = from_port_name, to_port_name

    flex = _get_flex_client(optical_node_block)

    ocrs = flex.rtrv_ocrs().parsed_data
    for ocr in ocrs:
        ocr_from_port = "-".join(ocr.get("FROMAID", "").split("-")[:-1])
        ocr_to_port = "-".join(ocr.get("TOAID", "").split("-")[:-1])
        ocr_passband = tuple(int(x) for x in ocr.get("PASSBANDLIST", []))
        ocr_carrier = tuple(int(x) for x in ocr.get("CARRIERLIST", []))
        ocr_cktidsuffix = ocr.get("CKTIDSUFFIX", "").strip(r"\" ")
        ocr_label = ocr.get("LABEL", "").strip(r"\" ")
        if (
            ocr_from_port == from_port_name
            and ocr_to_port == to_port_name
            and ocr_passband == passband
            and ocr_carrier == carrier
            and ocr_cktidsuffix == circuit_identifier
            and ocr_label == (label or "")
        ):
            flex.dlt_ocrs(fromaid=ocr["FROMAID"], toaid=ocr["TOAID"])
            return compare_jsons({"OCRS": ocr}, {"OCRS": {}})

    msg = (
        f"Could not find the optical cross connection from {from_port_name} to {to_port_name} "
        f"with passband {passband}, carrier {carrier}, label '{label}', "
        f"and circuit identifier '{circuit_identifier}'"
    )
    raise ValueError(msg)
