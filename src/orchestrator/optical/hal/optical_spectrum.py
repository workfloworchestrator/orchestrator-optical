"""Services for Optical Spectrum circuits.

This module implements the FlexILS-centric engine used to provision optical
circuits on the spectrum sections of an Optical Spectrum subscription: OEL,
OSNC and OCRS TL1 objects, shutters and labels. Operations are dispatched on
the vendor of the Optical Node product block with match/case statements; for
Groove G30 and GX G42 nodes the operations are no-ops, as those platforms do
not have internal optical cross-connections.

The device-side identifiers (OEL AID, OSNC CKTIDSUFFIX, OCRS circuit
identifiers) are derived from the ``circuit_identifier`` parameter, i.e. the
``subscription_instance_id`` of the spectrum subscription, instead of GARR
business logic such as pop codes.
"""

from time import sleep
from typing import Any, cast

from orchestrator.optical.hal.optical_digital_service import FlexilsClientProtocol
from orchestrator.optical.hal.optical_node import Vendor, get_flex_client, vendor_of
from orchestrator.optical.hal.optical_port import flexils_check_port_is_in_manualmode2_else_set_it
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlock,
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalOlsPortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlock,
    OpticalSpectrumSectionBlockInactive,
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.services.nokia.flexils.commands.base import TL1BaseResponse
from orchestrator.optical.services.nokia.flexils.exceptions import TL1CommandDeniedError
from orchestrator.optical.utils.custom_types.frequencies import Bandwidth, Frequency, Passband

OpticalNodeBlock = AbstractOpticalNodeBlock | AbstractOpticalNodeBlockProvisioning | AbstractOpticalNodeBlockInactive
OlsPortBlock = (
    AbstractOpticalOlsPortBlock | AbstractOpticalOlsPortBlockProvisioning | AbstractOpticalOlsPortBlockInactive
)
OpticalSpectrumSectionBlockT = (
    OpticalSpectrumSectionBlock | OpticalSpectrumSectionBlockProvisioning | OpticalSpectrumSectionBlockInactive
)


def _get_flex_client(optical_node_block: OpticalNodeBlock) -> FlexilsClientProtocol:
    """Return a FlexILS TL1 client for the given Optical Node block.

    Wraps `hal.optical_node.get_flex_client`, returning the dynamically-bound TL1
    command surface as a protocol so that it type checks.
    """
    if not isinstance(optical_node_block, NokiaFlexIlsBlockInactive):
        msg = f"Expected a Nokia FlexILS node block, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return cast(FlexilsClientProtocol, get_flex_client(optical_node_block))


def _node_id(optical_node_block: OpticalNodeBlock) -> str:
    """Return the fqdn of the given Optical Node block, for use in identifiers and messages."""
    fqdn = optical_node_block.management.optical_module_node_fqdn
    return fqdn if fqdn is not None else "<no fqdn>"


def _port_name(port: OlsPortBlock) -> str:
    """Return the optical port name of the given Optical Port block."""
    name = port.optical_port_name
    if name is None:
        msg = f"Optical port {port!r} has no name"
        raise ValueError(msg)
    return name


def _node_role(port: OlsPortBlock) -> OpticalNodeRole:
    """Return the role of the Optical Node hosting the given port."""
    role = port.optical_port_host_node.optical_node_role
    if role is None:
        msg = f"Optical port {_port_name(port)} is hosted by a node without a role"
        raise ValueError(msg)
    return role


def _divide_path_into_omses(
    path: list[OlsPortBlock],
) -> list[tuple[OlsPortBlock, OlsPortBlock]]:
    """Divide an optical path into OMS (Optical Multiplex Section) segments, i.e. links between ROADMs.

    Args:
        path: The list of Optical Port blocks representing the complete path, from the source
            add/drop port to the destination add/drop port, including the express ports in between.

    Returns:
        List of tuples containing (start_port, end_port) for each OMS section.

    Raises:
        ValueError: If the path is invalid or contains unexpected node roles.
    """
    if not path:
        msg = "Optical path is empty"
        raise ValueError(msg)

    omses: list[tuple[OlsPortBlock, OlsPortBlock]] = []
    oms_source_port: OlsPortBlock = path[0]
    if _node_role(oms_source_port) != OpticalNodeRole.ROADM:
        msg = "Optical path does not start with a ROADM device"
        raise ValueError(msg)

    for port in path[1:]:
        node_role = _node_role(port)
        if node_role == OpticalNodeRole.ROADM:
            omses.append((oms_source_port, port))
            oms_source_port = port
        elif node_role != OpticalNodeRole.AMPLIFIER:
            msg = f"Unexpected node role in optical path: {node_role}"
            raise ValueError(msg)

    if _node_role(path[-1]) != OpticalNodeRole.ROADM:
        msg = "Optical path does not end with a ROADM device"
        raise ValueError(msg)

    return omses


def _find_or_create_oel(
    oel_aid: str,
    source_device: OpticalNodeBlock,
    dest_device: OpticalNodeBlock,
    omses: list[tuple[OlsPortBlock, OlsPortBlock]],
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

    explicit_route: list[tuple[str, str, str, str]] = []
    for src_port, dst_port in omses:
        src_node = src_port.optical_port_host_node
        dst_node = dst_port.optical_port_host_node

        src_node_name = _node_id(src_node)
        dst_node_name = _node_id(dst_node)

        src_port_name = _oteintf_from_port_name(src_node, _port_name(src_port))
        dst_port_name = _oteintf_from_port_name(dst_node, _port_name(dst_port))

        explicit_route.append((src_node_name, src_port_name, dst_node_name, dst_port_name))

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


def _oteintf_from_port_name(device: OpticalNodeBlock, port_name: str) -> str:
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
    device: OpticalNodeBlock,
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
    src_device: OpticalNodeBlock,
    dst_device: OpticalNodeBlock,
    circuit_identifier: str,
    osnc_label: str,
    oel_aid: str,
    src_port_name: str,
    dst_port_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
) -> dict[str, Any]:
    """Find an existing OSNC on the source device or create a new one.

    The OSNC CKTIDSUFFIX is the circuit identifier (the subscription instance id
    of the circuit) instead of the spectrum name.

    Raises:
        ValueError: If the circuit identifier is empty or the FlexILS commands fail.
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
        return osnc

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

    response = src_flex.rtrv_osnc(aid=src_endpoint)
    if not response.parsed_data:
        msg = f"RTRV-OSNC returned no data for aid {src_endpoint}"
        raise ValueError(msg)
    return response.parsed_data[0]


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


def _open_shutter(device: OpticalNodeBlock, sch_aid: str) -> None:
    """Open the shutter of the given superchannel on the given device."""
    flex = _get_flex_client(device)
    flex.put_maintenance(aidtype="SCH", aid=sch_aid)
    flex.ed_sch(aid=sch_aid, shutterstate="OPEN")
    flex.rst_maintenance(aidtype="SCH", aid=sch_aid)


def _find_flexils_osnc(
    optical_spectrum_name: str,
    optical_spectrum_section: OpticalSpectrumSectionBlockT,
    passband: Passband | None = None,
    circuit_identifier: str = "",
) -> tuple[FlexilsClientProtocol, dict[str, Any]]:
    """Find an existing OSNC between the two FlexILS devices of the given section.

    The OSNC is matched by its CKTIDSUFFIX, which is the circuit identifier (the
    subscription instance id of the circuit) when provided; otherwise the
    spectrum name is used as a fallback.

    Args:
        optical_spectrum_name: The user-facing name of the optical spectrum.
        optical_spectrum_section: The optical spectrum section block.
        passband: The passband of the optical spectrum.
        circuit_identifier: The subscription instance id of the circuit; used as the CKTIDSUFFIX.

    Returns:
        The FlexILS client of the device controlling the OSNC and the OSNC configuration.

    Raises:
        ValueError: If no matching OSNC is found.
    """
    src_port_raw = _port_name(optical_spectrum_section.optical_spectrum_section_add_drop_ports[0])
    dst_port_raw = _port_name(optical_spectrum_section.optical_spectrum_section_add_drop_ports[1])
    src_device = optical_spectrum_section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
    dst_device = optical_spectrum_section.optical_spectrum_section_add_drop_ports[1].optical_port_host_node

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
        passband=passband,
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
        passband=passband,
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
    optical_spectrum_section: OpticalSpectrumSectionBlockT,
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


def deploy_optical_circuit(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    circuit_identifier: str = "",
) -> dict[str, Any]:
    """Deploy an optical circuit for the given optical spectrum section.

    Args:
        optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Optional label for the circuit.
        circuit_identifier: The subscription instance id of the circuit; used to derive the
            device-side OEL AID and OSNC CKTIDSUFFIX.

    Returns:
        Platform-specific deployment configuration.

    Raises:
        ValueError: If the circuit cannot be deployed.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _deploy_optical_circuit_flexils(
                optical_node_block,
                optical_spectrum_section_block,
                optical_spectrum_name,
                passband,
                carrier,
                label,
                circuit_identifier,
            )
        case Vendor.GROOVE_G30:
            return {
                "not-applicable": "Groove G30s (H4 links) do not need internal optical crossconnections configurations"
            }
        case Vendor.GX_G42:
            return {"not-applicable": "GX G42s do not need internal optical crossconnections configurations"}


def _deploy_optical_circuit_flexils(
    optical_node_block: OpticalNodeBlock,  # noqa: ARG001
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    circuit_identifier: str = "",
) -> dict[str, Any]:
    """Deploy an optical circuit specifically for FlexILS platform devices."""
    add_drop_ports = optical_spectrum_section_block.optical_spectrum_section_add_drop_ports
    express_ports = optical_spectrum_section_block.optical_spectrum_section_express_ports
    path: list[OlsPortBlock] = [add_drop_ports[0], *express_ports, add_drop_ports[1]]

    src_device = add_drop_ports[0].optical_port_host_node
    dst_device = add_drop_ports[1].optical_port_host_node
    src_flexils_name = _node_id(src_device)
    dst_flexils_name = _node_id(dst_device)

    oel_aid = circuit_identifier[:127]
    osnc_label = f"{src_flexils_name}_{dst_flexils_name}" if label in (None, "") else label.strip()

    omses = _divide_path_into_omses(path)
    oel = _find_or_create_oel(
        oel_aid,
        src_device,
        dst_device,
        omses,
    )

    for port in add_drop_ports:
        flexils_check_port_is_in_manualmode2_else_set_it(port)

    osnc = _find_or_create_osnc(
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

    _open_shutter(src_device, osnc["LOCENDPOINT"])
    _open_shutter(dst_device, osnc["REMENDPOINT"])

    flex = _get_flex_client(src_device)
    osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]

    return {
        "OEL": oel,
        "OSNC": osnc,
    }


def modify_optical_circuit(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    old_passband: Passband | None = None,
    circuit_identifier: str = "",
) -> dict[str, Any]:
    """Modify an optical circuit for the given optical spectrum section.

    The circuit is found by its circuit identifier, so the spectrum name is not
    expected to change; when it does, the new name is only reflected in the OSNC
    label if provided.

    Args:
        optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: The new frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Optional label for the circuit.
        old_passband: The old passband of the optical circuit.
        circuit_identifier: The subscription instance id of the circuit; used to derive the
            device-side OEL AID and OSNC CKTIDSUFFIX.

    Returns:
        Platform-specific modification result.

    Raises:
        ValueError: If the circuit cannot be modified.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            return _modify_optical_circuit_flexils(
                optical_node_block,
                optical_spectrum_section_block,
                optical_spectrum_name,
                passband,
                carrier,
                label,
                old_passband,
                circuit_identifier,
            )
        case Vendor.GROOVE_G30:
            return {
                "not-applicable": "Groove G30s (H4 links) do not have any internal optical crossconnections to modify"
            }
        case Vendor.GX_G42:
            return {"not-applicable": "GX G42s do not have any internal optical crossconnections to modify"}


def _modify_optical_circuit_flexils(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    old_passband: Passband | None = None,
    circuit_identifier: str = "",
) -> dict[str, Any]:
    """Modify an optical circuit specifically for FlexILS platform devices."""
    osnc_name = circuit_identifier or optical_spectrum_name.replace(" ", "_")

    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section_block,
        old_passband,
        circuit_identifier,
    )

    remote_flex = _remote_flex_for_section(flex, optical_spectrum_section_block)

    add_drop_ports = optical_spectrum_section_block.optical_spectrum_section_add_drop_ports
    express_ports = optical_spectrum_section_block.optical_spectrum_section_express_ports
    path: list[OlsPortBlock] = [add_drop_ports[0], *express_ports, add_drop_ports[1]]

    oel_aid = circuit_identifier[:127]

    matches_oel = osnc.get("OELAID", "").strip(r"\" ") == oel_aid[:64]
    new_oel: dict[str, Any] | None = None
    if not matches_oel:
        dst_optical_device = add_drop_ports[1].optical_port_host_node
        omses = _divide_path_into_omses(path)
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

    flex.put_maintenance(aidtype="SCH", aid=osnc["LOCENDPOINT"])
    flex.ed_sch(aid=osnc["LOCENDPOINT"], shutterstate="OPEN")
    flex.rst_maintenance(aidtype="SCH", aid=osnc["LOCENDPOINT"])

    remote_flex.put_maintenance(aidtype="SCH", aid=osnc["REMENDPOINT"])
    remote_flex.ed_sch(aid=osnc["REMENDPOINT"], shutterstate="OPEN")
    remote_flex.rst_maintenance(aidtype="SCH", aid=osnc["REMENDPOINT"])

    osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"])
    osnc = osnc.parsed_data[0]

    return {
        "new OEL": new_oel,
        "OSNC": osnc,
    }


def delete_optical_circuit(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
    optical_spectrum_name: str,
    passband: Passband,
    circuit_identifier: str = "",
) -> dict[str, Any]:
    """Delete an optical circuit for the given optical spectrum section.

    Args:
        optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Returns:
        Platform-specific deletion result.

    Raises:
        ValueError: If the circuit cannot be found.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
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

            return {"deleted_OSNC": osnc["LOCENDPOINT"]}
        case Vendor.GROOVE_G30:
            return {
                "not-applicable": "Groove G30s (H4 links) do not have any internal optical crossconnections to delete"
            }
        case Vendor.GX_G42:
            return {"not-applicable": "GX G42s do not have any internal optical crossconnections to delete"}


def validate_optical_circuit(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
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
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            flex, osnc = _find_flexils_osnc(
                optical_spectrum_name,
                optical_spectrum_section_block,
                passband,
                circuit_identifier,
            )  # already raises error if CKTIDSUFFIX/LOCENDPOINT/REMENDPOINT/PASSBANDLIST do not match

            remote_flex = _remote_flex_for_section(flex, optical_spectrum_section_block)

            errors = []

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

        case Vendor.GROOVE_G30:
            # Groove G30s (H4 links) do not have internal optical crossconnections to validate
            return
        case Vendor.GX_G42:
            # GX G42s do not have internal optical crossconnections to validate
            return


def append_optical_circuit_label(
    source_optical_node_block: OpticalNodeBlock,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockT,
    optical_spectrum_name: str,
    passband: Passband,
    label: str,
    circuit_identifier: str = "",
) -> dict[str, Any]:
    """Append a label to the OSNC of the given optical spectrum section.

    Args:
        source_optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        label: The label to append.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Returns:
        The updated OSNC configuration.

    Raises:
        ValueError: If the OSNC cannot be found.
    """
    match vendor_of(source_optical_node_block):
        case Vendor.FLEXILS:
            flex, osnc = _find_flexils_osnc(
                optical_spectrum_name,
                optical_spectrum_section_block,
                passband,
                circuit_identifier,
            )
            old_label = osnc.get("LABEL", "").strip(r"\" ")
            labels = old_label.split("+")
            labels.append(label)
            labels = sorted(name.strip() for name in labels)
            new_label = "+".join(labels)
            flex.ed_osnc(aid=osnc["LOCENDPOINT"], label=new_label)
            response = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"])
            osnc = response.parsed_data[0]

            return {"updated_OSNC": osnc}
        case Vendor.GROOVE_G30:
            return {
                "not-applicable": "Groove G30s (H4 links) do not have any internal optical crossconnections to label"
            }
        case Vendor.GX_G42:
            return {"not-applicable": "GX G42s do not have any internal optical crossconnections to label"}


def create_optical_cross_connection(
    optical_node_block: OpticalNodeBlock,
    from_port: OlsPortBlock,
    to_port: OlsPortBlock,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str | None = None,
    circuit_name: str | None = None,  # noqa: ARG001
    circuit_identifier: str = "",
) -> dict[str, Any]:
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
        Platform-specific cross connection configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross connection cannot be created.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
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

            response = flex.rtrv_ocrs(fromaid=fromaid, toaid=toaid)
            return response.parsed_data[0]
        case Vendor.GROOVE_G30:
            msg = "create_optical_cross_connection is not implemented for Groove G30 nodes"
            raise NotImplementedError(msg)
        case Vendor.GX_G42:
            msg = "create_optical_cross_connection is not implemented for GX G42 nodes"
            raise NotImplementedError(msg)


def delete_optical_cross_connection(
    optical_node_block: OpticalNodeBlock,
    from_port: OlsPortBlock,
    to_port: OlsPortBlock,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str | None = None,
    circuit_name: str | None = None,  # noqa: ARG001
    circuit_identifier: str = "",
) -> dict[str, Any] | TL1BaseResponse:
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
        The result of the deletion operation.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross connection cannot be found.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
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
                    return flex.dlt_ocrs(fromaid=ocr["FROMAID"], toaid=ocr["TOAID"])

            msg = (
                f"Could not find the optical cross connection from {from_port_name} to {to_port_name} "
                f"with passband {passband}, carrier {carrier}, label '{label}', "
                f"and circuit identifier '{circuit_identifier}'"
            )
            raise ValueError(msg)
        case Vendor.GROOVE_G30:
            msg = "delete_optical_cross_connection is not implemented for Groove G30 nodes"
            raise NotImplementedError(msg)
        case Vendor.GX_G42:
            msg = "delete_optical_cross_connection is not implemented for GX G42 nodes"
            raise NotImplementedError(msg)
