"""Spectrum-area operations for the Nokia FlexILS device adapter."""

from collections.abc import Sequence
from time import sleep
from typing import Any

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
    RTRV-OSNC first; if any OSNC references the OEL, it is left in place (no-op).

    Args:
        flex: TL1 client of the node hosting the OEL.
        oel_aid: Access identifier of the OEL.
    """
    aid = oel_aid[:127]
    for record in flex.rtrv_osnc().parsed_data:
        if record.get("OELAID", "").strip(r"\" ") == aid[:64]:
            return
    flex.dlt_oel(aid=aid)


def delete_oel(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    circuit_identifier: str,
) -> DiffResult:
    """Delete the OEL of the given circuit on the node, when no other OSNC uses it.

    The OEL explicit route cannot be edited with ED-OEL, so a path change is applied
    by deleting the OEL and re-entering it (see :func:`deploy`). This helper performs
    the guarded deletion: it leaves the OEL in place while another OSNC on the node
    still references it (a shared OEL is legitimate on FlexILS).

    Args:
        optical_node_block: The Optical Node block hosting the OEL.
        circuit_identifier: The circuit identifier used as OEL AID.

    Returns:
        The difference between the OEL configuration before and after the
        deletion: a deleted OEL shows up as a removal, while an OEL kept because
        another OSNC still references it yields an empty diff.
    """
    oel_aid = circuit_identifier[:127]
    flex = _get_flex_client(optical_node_block)
    before_oel = _rtrv_oel_or_none(flex, oel_aid)
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
    src_name = _node_id(source_device)
    dst_name = _node_id(dest_device)
    oel_label = f"{src_name}-{dst_name}"

    explicit_route = _explicit_route_from_omses(omses)

    flex = _get_flex_client(source_device)
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
    try:
        response = client.rtrv_osnc()
        existing_osncs = response.parsed_data
    except TL1CommandDeniedError as e:
        if "SPECIFIED OBJECT ENTITY DOES NOT EXIST" not in str(e.response):
            raise
        return None

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

    Raises:
        ValueError: If the circuit identifier is empty or the FlexILS commands fail.

    Returns:
        The OSNC record and whether it was created (``False`` when it was found).
    """
    if not circuit_identifier:
        msg = "An OSNC circuit identifier is required to create or retrieve an OSNC"
        raise ValueError(msg)

    _src_node_name, src_flex, src_port_name = _get_flexils_name_client_tributary(src_device, src_port_name)
    dst_node_name, dst_flex, dst_port_name = _get_flexils_name_client_tributary(dst_device, dst_port_name)

    oel_aid = oel_aid[:127]

    osnc = _find_matching_osnc_on_flexils(
        client=src_flex,
        circuit_identifier=circuit_identifier,
        src_port_name=src_port_name,
        dst_port_name=dst_port_name,
        dst_node_name=dst_node_name,
        passband=passband,
        carrier=carrier,
        osnc_label=osnc_label,
        oel_aid=oel_aid,
    )

    if osnc is not None:
        return osnc, False

    dst_sch_id = _find_first_free_sch_id(dst_flex, dst_port_name)
    src_sch_id = _find_first_free_sch_id(src_flex, src_port_name)

    src_endpoint = f"{src_port_name}-{src_sch_id}"
    dst_endpoint = f"{dst_port_name}-{dst_sch_id}"

    src_flex.ent_osnc(
        aid=src_endpoint,
        label=osnc_label,
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
    return response.parsed_data[0], True


def _find_first_free_sch_id(flex: FlexilsClientProtocol, port_name: str) -> int:
    """Find the first available superchannel ID for the given port."""
    min_sch_id = 1
    max_sch_id = 128
    for i in range(min_sch_id, max_sch_id + 1):
        try:
            flex.rtrv_sch(aid=f"{port_name}-{i}")
        except TL1CommandDeniedError as e:
            if "SPECIFIED OBJECT ENTITY DOES NOT EXIST" in str(e.response):
                return i
            raise
    msg = f"Could not find a free superchannel index for port {port_name}"
    raise ValueError(msg)


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
        ValueError: If no matching OSNC is found.
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
    raise ValueError(msg)


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


def deploy(
    optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    circuit_identifier: str = "",
) -> DiffResult:
    """Deploy an optical circuit specifically for FlexILS platform devices.

    Returns:
        The difference between the circuit configuration before and after the
        deployment: the OEL and OSNC of a freshly deployed circuit show up as
        additions, while a circuit already present on the node yields an empty diff.
    """
    add_drop_ports = optical_spectrum_section_block.optical_spectrum_section_add_drop_ports
    express_ports = optical_spectrum_section_block.optical_spectrum_section_express_ports

    src_device = _as_flexils_block(add_drop_ports[0].optical_port_host_node)
    dst_device = _as_flexils_block(add_drop_ports[1].optical_port_host_node)
    src_flexils_name = _node_id(src_device)
    dst_flexils_name = _node_id(dst_device)

    oel_aid = circuit_identifier[:127]
    osnc_label = f"{src_flexils_name}_{dst_flexils_name}" if label in (None, "") else label.strip()

    src_flex = _get_flex_client(src_device)
    before_oel = _rtrv_oel_or_none(src_flex, oel_aid)

    omses = _omses_from_line_ports(express_ports)
    oel = _find_or_create_oel(
        oel_aid,
        src_device,
        dst_device,
        omses,
    )

    for port in add_drop_ports:
        _ensure_manualmode2(port)

    osnc, osnc_created = _find_or_create_osnc(
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
    before_osnc = None if osnc_created else osnc

    sleep(5)

    _open_shutter(src_device, osnc["LOCENDPOINT"])
    _open_shutter(dst_device, osnc["REMENDPOINT"])

    osnc = src_flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]

    return compare_jsons(
        {"OEL": before_oel or {}, "OSNC": before_osnc or {}},
        {"OEL": oel, "OSNC": osnc},
    )


def modify(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    old_passband: Passband | None = None,
    circuit_identifier: str = "",
) -> DiffResult:
    """Modify an optical circuit specifically for FlexILS platform devices.

    Returns:
        The difference between the circuit configuration before and after the
        modification.
    """
    osnc_name = circuit_identifier or optical_spectrum_name.replace(" ", "_")

    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section_block,
        old_passband,
        circuit_identifier,
    )
    before_osnc = osnc

    remote_flex = _remote_flex_for_section(flex, optical_spectrum_section_block)

    add_drop_ports = optical_spectrum_section_block.optical_spectrum_section_add_drop_ports
    express_ports = optical_spectrum_section_block.optical_spectrum_section_express_ports

    oel_aid = circuit_identifier[:127]

    before_oel = _rtrv_oel_or_none(_get_flex_client(optical_node_block), oel_aid)

    matches_oel = osnc.get("OELAID", "").strip(r"\" ") == oel_aid[:64]
    new_oel: dict[str, Any] | None = None
    if not matches_oel:
        dst_optical_device = _as_flexils_block(add_drop_ports[1].optical_port_host_node)
        omses = _omses_from_line_ports(express_ports)
        new_oel = _find_or_create_oel(
            oel_aid,
            optical_node_block,
            dst_optical_device,
            omses,
        )

    osnc_passband = osnc.get("PASSBANDLIST", [])
    osnc_carrier = osnc.get("CARRIERLIST", [])
    matches_spectrum = (
        len(osnc_passband) == len(passband)
        and all(int(x) == y for x, y in zip(osnc_passband, passband, strict=False))
        and len(osnc_carrier) == len(carrier)
        and all(int(x) == y for x, y in zip(osnc_carrier, carrier, strict=False))
    )

    if not matches_spectrum or not matches_oel:
        flex.ed_osnc(
            aid=osnc["LOCENDPOINT"],
            passbandlist=passband,
            carrierlist=carrier,
            oelaid=oel_aid,
            is_oos="OOS",
        )

    flex.ed_osnc(
        aid=osnc["LOCENDPOINT"],
        cktidsuffix=osnc_name,
        is_oos="IS",
        label=label if label else osnc.get("LABEL", ""),
    )

    sleep(3)

    flex.put_maintenance(aidtype="SCH", aid=osnc["LOCENDPOINT"])
    flex.ed_sch(aid=osnc["LOCENDPOINT"], shutterstate="OPEN")
    flex.rst_maintenance(aidtype="SCH", aid=osnc["LOCENDPOINT"])

    remote_flex.put_maintenance(aidtype="SCH", aid=osnc["REMENDPOINT"])
    remote_flex.ed_sch(aid=osnc["REMENDPOINT"], shutterstate="OPEN")
    remote_flex.rst_maintenance(aidtype="SCH", aid=osnc["REMENDPOINT"])

    after_osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]
    after_oel = new_oel if new_oel is not None else before_oel

    return compare_jsons(
        {"OEL": before_oel or {}, "OSNC": before_osnc},
        {"OEL": after_oel or {}, "OSNC": after_osnc},
    )


def delete(
    optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    circuit_identifier: str = "",
) -> DiffResult:
    """Delete an optical circuit specifically for FlexILS platform devices.

    Returns:
        The difference between the circuit configuration before and after the
        deletion: the deleted OSNC shows up as a removal.
    """
    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section_block,
        passband,
        circuit_identifier,
    )

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
    if label not in actual_label:
        errors.append(f"Label mismatch: expected to contain '{label}', got '{actual_label}'")

    local_shutter = flex.rtrv_sch(aid=osnc["LOCENDPOINT"]).parsed_data[0]
    if local_shutter.get("SHUTTERSTATE") != "OPEN":
        errors.append(f"Local shutter not OPEN: {local_shutter.get('SHUTTERSTATE')}")

    remote_shutter = remote_flex.rtrv_sch(aid=osnc["REMENDPOINT"]).parsed_data[0]
    if remote_shutter.get("SHUTTERSTATE") != "OPEN":
        errors.append(f"Remote shutter not OPEN: {remote_shutter.get('SHUTTERSTATE')}")

    if errors:
        msg = f"OSNC validation failed for {optical_spectrum_name}: " + "; ".join(errors)
        raise ValueError(msg)


def append_label(
    source_optical_node_block: NokiaFlexIlsBlockProvisioning,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    label: str,
    circuit_identifier: str = "",
) -> DiffResult:
    """Append a label to the OSNC of the given optical spectrum section.

    Args:
        source_optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        label: The label to append.
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
    old_label = osnc.get("LABEL", "").strip(r"\" ")
    labels = old_label.split("+")
    labels.append(label)
    labels = sorted(name.strip() for name in labels)
    new_label = "+".join(labels)
    flex.ed_osnc(aid=osnc["LOCENDPOINT"], label=new_label)
    after_osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]

    return compare_jsons({"OSNC": before_osnc}, {"OSNC": after_osnc})


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
