# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import sleep
from typing import Any

from products.product_blocks.optical_device import (
    DeviceType,
    OpticalDeviceBlock,
    Platform,
)
from products.product_blocks.optical_fiber import (
    OpticalDevicePortBlock,
)
from products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlock,
)
from products.services.optical_device import get_optical_device_client
from products.services.optical_device_port import flexils_check_port_is_in_manualmode2_else_set_it
from services.infinera import FlexilsClient, TL1CommandDeniedError
from utils.attributedispatch import (
    attribute_dispatch_base,
    attributedispatch,
)
from utils.custom_types.frequencies import Bandwidth, Frequency, Passband


def _divide_path_into_omses(
    optical_path: list[OpticalDevicePortBlock],
) -> list[tuple[OpticalDevicePortBlock, OpticalDevicePortBlock]]:
    """
    Divides an optical path into OMS (Optical Multiplex Section) segments,
    i.e. links between ROADMs not including amplifiers.

    Args:
        optical_path: List of optical device ports representing the complete path

    Returns:
        List of tuples containing (start_port, end_port) for each OMS section

    Raises:
        ValueError: If path is invalid or contains unexpected device types
    """
    omses = []
    oms_source_port = optical_path[0]
    if oms_source_port.optical_device.device_type != DeviceType.ROADM:
        msg = "Optical path does not start with a ROADM device"
        raise ValueError(msg)

    for port in optical_path[1:]:
        device_type = port.optical_device.device_type
        if device_type == DeviceType.ROADM:
            if oms_source_port is None:
                oms_source_port = port
            else:
                omses.append((oms_source_port, port))
                oms_source_port = None
        elif device_type != DeviceType.Amplifier:
            msg = f"Unexpected device type in {Platform.FlexILS} optical path: {device_type}"
            raise ValueError(msg)

    if oms_source_port is not None:
        msg = "Optical path does not end with a ROADM device"
        raise ValueError(msg)

    return omses


def _find_or_create_oel(
    oel_name: str,
    source_device: OpticalDeviceBlock,
    dest_device: OpticalDeviceBlock,
    omses: list[tuple[OpticalDevicePortBlock, OpticalDevicePortBlock]],
) -> dict[str, Any]:
    """
    Finds existing OEL (Optical Engineered Lightpath) or creates a new one if needed.

    Args:
        oel_name: Name identifier for the OEL
        source_device: Source optical device object
        dest_device: Destination optical device object
        omses: List of OMS (Optical Multiplex Section) port pairs representing the path

    Returns:
        dict[str, Any]: The OEL configuration data

    Raises:
        TL1CommandDeniedError: If the FlexILS commands fail
    """
    src_name = source_device.fqdn.replace(".garr.net", "")
    dst_name = dest_device.fqdn.replace(".garr.net", "")
    oel_label = f"{source_device.pop.code}-{dest_device.pop.code}".lower()

    explicit_route = []
    for src_port, dst_port in omses:
        src_node = src_port.optical_device
        dst_node = dst_port.optical_device

        src_node_name = src_node.fqdn.replace(".garr.net", "")
        dst_node_name = dst_node.fqdn.replace(".garr.net", "")

        src_port_name = _oteintf_from_port_name(src_node, src_port.port_name)
        dst_port_name = _oteintf_from_port_name(dst_node, dst_port.port_name)

        explicit_route.append((src_node_name, src_port_name, dst_node_name, dst_port_name))

    flex = get_optical_device_client(source_device)
    flex.ent_oel(
        aid=oel_name,
        label=oel_label,
        srcnodename=src_name,
        dstnodename=dst_name,
        explicitroute=explicit_route,
        validfrangelist=[191325000, 196125000],
    )
    flex.opr_valroute_oel(aid=oel_name)

    response = flex.rtrv_oel(aid=oel_name)
    return response.parsed_data[0]


def _oteintf_from_port_name(device: OpticalDeviceBlock, port_name: str) -> str:
    """Find the Optical Traffic Engineering Interface (OTEINTF) corresponding to the given physical port name."""
    device_name = device.fqdn.replace(".garr.net", "")
    flex = get_optical_device_client(device)
    ote_intfs = flex.rtrv_oteintf().parsed_data
    osc_port = port_name.replace("L", "O")

    for intf in ote_intfs:
        if intf["AID"] == osc_port:
            return port_name
        if intf["ASSOCGCC"] == osc_port:
            return intf["AID"]

    msg = f"Could not find the OTEINTF for port {port_name} on device {device_name}"
    raise ValueError(msg)


def _find_fbm_port_if_fmm_port(flex: FlexilsClient, port_name: str) -> str:
    card_aid = port_name.split("-")[:-1]
    card_aid = "-".join(card_aid)
    card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]

    if card["TYPE"] != "FMMC12":
        return port_name

    chassis_sn = flex.rtrv_eqpt(aid="1").parsed_data[0]["SERNO"]
    target_provowremptp = f"{chassis_sn}/{card_aid}-L1"

    fbm_scgs = flex.rtrv_scg(type="FBM").parsed_data
    for scg in fbm_scgs:
        if scg.get("PROVOWREMPTP", "") == target_provowremptp:
            return scg["AID"]

    msg = f"Could not find the FBM port associated to the FMM {card_aid} on device {flex.device_tid}"
    raise ValueError(msg)


def _find_or_create_osnc(
    src_device: OpticalDeviceBlock,
    dst_device: OpticalDeviceBlock,
    osnc_name: str,
    osnc_label: str,
    oel_name: str,
    src_port_name: str,
    dst_port_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
) -> dict[str, Any]:
    src_flex = get_optical_device_client(src_device)
    dst_flex = get_optical_device_client(dst_device)

    src_port_name = _find_fbm_port_if_fmm_port(src_flex, src_port_name)
    dst_port_name = _find_fbm_port_if_fmm_port(dst_flex, dst_port_name)

    dst_node_name = dst_device.fqdn.replace(".garr.net", "")

    existing_osncs = []
    try:
        response = src_flex.rtrv_osnc()
        existing_osncs = response.parsed_data
    except TL1CommandDeniedError as e:
        if "SPECIFIED OBJECT ENTITY DOES NOT EXIST" not in e.response:
            raise

    for osnc in existing_osncs:
        matches_endpoints = src_port_name in osnc["LOCENDPOINT"] and dst_port_name in osnc["REMENDPOINT"]
        if not matches_endpoints:
            continue

        matches_config = (
            osnc_label in osnc["LABEL"]
            and osnc["OELAID"] == oel_name[:64]
            and osnc["CKTIDSUFFIX"] == osnc_name
            and osnc["REMNODETID"] == dst_node_name
        )
        if not matches_config:
            continue

        matches_spectrum = (
            len(osnc["PASSBANDLIST"]) == len(passband)
            and len(osnc["CARRIERLIST"]) == len(carrier)
            and all(int(x) == y for x, y in zip(osnc["PASSBANDLIST"], passband, strict=False))
            and all(int(x) == y for x, y in zip(osnc["CARRIERLIST"], carrier, strict=False))
        )
        if not matches_spectrum:
            continue

        if matches_endpoints and matches_config and matches_spectrum:
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
        oelaid=oel_name,
        cktidsuffix=osnc_name,
        passbandlist=passband,
        carrierlist=carrier,
    )

    response = src_flex.rtrv_osnc(aid=src_endpoint)
    return response.parsed_data[0]


def _find_first_free_sch_id(flex, port_name: str) -> int:
    """Find first available superchannel ID for the given port."""
    min_sch_id = 1
    max_sch_id = 128
    for i in range(min_sch_id, max_sch_id + 1):
        try:
            flex.rtrv_sch(aid=f"{port_name}-{i}")
        except TL1CommandDeniedError as e:
            if "SPECIFIED OBJECT ENTITY DOES NOT EXIST" in e.response:
                return i
            raise
    msg = f"Could not find a free superchannel index for port {port_name}"
    raise ValueError(msg)


def _open_shutter(device: OpticalDeviceBlock, sch_aid: str):
    flex = get_optical_device_client(device)
    flex.put_maintenance(aidtype="SCH", aid=sch_aid)
    flex.ed_sch(aid=sch_aid, shutterstate="OPEN")
    flex.rst_maintenance(aidtype="SCH", aid=sch_aid)


def _find_flexils_osnc(
    optical_spectrum_name: str,
    optical_spectrum_section: OpticalSpectrumSectionBlock,
    passband: Passband | None = None,
) -> tuple[FlexilsClient, dict[str, Any]]:
    """
    Helper function to find an existing OSNC between two FlexILS devices.

    Args:
        optical_spectrum_name: Name identifier for the optical spectrum
        optical_spectrum_section: OpticalSpectrumSectionBlock
        passband: passband of the optical spectrum

    Returns:
        FlexilsClient: The FlexILS client for the device controlling the OSNC
        dict[str, Any]: The OSNC configuration data if found

    Raises:
        ValueError: If no matching OSNC is found.
    """

    def _helper_func(
        osnc_name: str,
        src_port_name: str,
        dst_port_name: str,
        dst_device_name: str,
        passband: Passband | None = None,
    ) -> dict[str, Any] | None:
        response = flex.rtrv_osnc()
        existing_osncs = response.parsed_data
        for osnc in existing_osncs:
            matches_circuit_id = osnc["CKTIDSUFFIX"].strip(r"\" ") == osnc_name
            if not matches_circuit_id:
                continue

            matches_endpoints = (
                osnc["LOCENDPOINT"].startswith(src_port_name)
                and osnc["REMENDPOINT"].startswith(dst_port_name)
                and osnc["REMNODETID"] == dst_device_name
            )
            if not matches_endpoints:
                continue

            if passband is None:
                return osnc

            matches_passband = len(osnc.get("PASSBANDLIST", [])) == len(passband) and all(
                int(x) == y for x, y in zip(osnc["PASSBANDLIST"], passband, strict=False)
            )
            if not matches_passband:
                continue

            return osnc

        return None

    src_device = optical_spectrum_section.add_drop_ports[0].optical_device
    dst_device = optical_spectrum_section.add_drop_ports[1].optical_device

    src_device_name = src_device.fqdn.replace(".garr.net", "")
    dst_device_name = dst_device.fqdn.replace(".garr.net", "")

    flex_a = get_optical_device_client(src_device)
    flex_z = get_optical_device_client(dst_device)

    src_port_name = optical_spectrum_section.add_drop_ports[0].port_name
    dst_port_name = optical_spectrum_section.add_drop_ports[1].port_name

    src_port_name = _find_fbm_port_if_fmm_port(flex_a, src_port_name)
    dst_port_name = _find_fbm_port_if_fmm_port(flex_z, dst_port_name)

    osnc_name = optical_spectrum_name.replace(" ", "_")
    osnc_name = osnc_name.strip(r"\" ")

    flex = flex_a
    osnc = _helper_func(
        osnc_name=osnc_name,
        src_port_name=src_port_name,
        dst_port_name=dst_port_name,
        dst_device_name=dst_device_name,
        passband=passband,
    )

    if osnc is None:
        flex = flex_z
        src_device_name, dst_device_name = dst_device_name, src_device_name
        src_port_name, dst_port_name = dst_port_name, src_port_name
        osnc = _helper_func(
            osnc_name=osnc_name,
            src_port_name=src_port_name,
            dst_port_name=dst_port_name,
            dst_device_name=dst_device_name,
            passband=passband,
        )

    if osnc is None:
        msg = (
            f"Could not find the OSNC for spectrum '{osnc_name}' between "
            f"{src_device.fqdn} {src_port_name} and {dst_device.fqdn} {dst_port_name} "
            f"with passband {passband}. "
        )
        raise ValueError(msg)

    return flex, osnc


@attributedispatch("platform")
def append_optical_circuit_label(
    source_optical_device: OpticalDeviceBlock,
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    label: str,  # noqa: ARG001
) -> dict[str, Any]:
    return attribute_dispatch_base(append_optical_circuit_label, "platform", source_optical_device.platform)


@append_optical_circuit_label.register(Platform.FlexILS)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,
    optical_spectrum_name: str,
    passband: Passband,
    label: str,
) -> dict[str, Any]:
    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section,
        passband,
    )
    old_label = osnc["LABEL"].strip(r"\" ")
    labels = old_label.split("+")
    labels.append(label)
    labels = sorted(label.strip() for label in labels)
    new_label = "+".join(labels)
    flex.ed_osnc(aid=osnc["LOCENDPOINT"], label=rf"{new_label}")
    response = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"])
    osnc = response.parsed_data[0]

    return {"updated_OSNC": osnc}


@append_optical_circuit_label.register(Platform.Groove_G30)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    label: str,  # noqa: ARG001
) -> dict[str, Any]:
    return {"not-applicable": "Groove G30s (H4 links) do not have any internal optical crossconnections to label"}


@attributedispatch("platform")
def deploy_optical_circuit(
    source_optical_device: OpticalDeviceBlock,
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth],  # noqa: ARG001
    label: str | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Deploy an optical circuit based on the platform type.

    Args:
        source_optical_device: The source optical device configuration
        optical_spectrum_section: The spectrum section configuration
        optical_spectrum_name: Name identifier for the optical spectrum
        passband: Frequency range allowed for transmission
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal
        label: Optional label for the circuit

    Returns:
        dict[str, Any]: Platform-specific deployment configuration
    """
    return attribute_dispatch_base(deploy_optical_circuit, "platform", source_optical_device.platform)


@deploy_optical_circuit.register(Platform.FlexILS)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str = "",
) -> dict[str, Any]:
    """Deploy an optical circuit specifically for FlexILS platform devices."""
    add_drop_ports = optical_spectrum_section.add_drop_ports
    path = optical_spectrum_section.optical_path

    src_device = add_drop_ports[0].optical_device
    dst_device = add_drop_ports[1].optical_device
    src_flexils_name = src_device.fqdn.replace(".garr.net", "")
    dst_flexils_name = dst_device.fqdn.replace(".garr.net", "")

    pops = [port.optical_device.pop.code.lower() for port in path[::2]]
    pops.append(path[-1].optical_device.pop.code.lower())
    oel_name = "-".join(pops)

    osnc_name = optical_spectrum_name.replace(" ", "_")
    osnc_label = f"{src_flexils_name}_{dst_flexils_name}" if label == "" else label.strip()

    omses = _divide_path_into_omses(path)
    oel = _find_or_create_oel(
        oel_name,
        src_device,
        dst_device,
        omses,
    )

    for port in optical_spectrum_section.add_drop_ports:
        flexils_check_port_is_in_manualmode2_else_set_it(port.optical_device, port.port_name)

    osnc = _find_or_create_osnc(
        src_device=src_device,
        dst_device=dst_device,
        osnc_name=osnc_name,
        osnc_label=osnc_label,
        oel_name=oel_name,
        src_port_name=optical_spectrum_section.add_drop_ports[0].port_name,
        dst_port_name=optical_spectrum_section.add_drop_ports[1].port_name,
        passband=passband,
        carrier=carrier,
    )

    sleep(5)

    _open_shutter(src_device, osnc["LOCENDPOINT"])
    _open_shutter(dst_device, osnc["REMENDPOINT"])

    flex = get_optical_device_client(src_device)
    osnc = flex.rtrv_osnc(aid=osnc["LOCENDPOINT"]).parsed_data[0]

    return {
        "OEL": oel,
        "OSNC": osnc,
    }


@deploy_optical_circuit.register(Platform.Groove_G30)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth],  # noqa: ARG001
    label: str | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """Deploy an optical circuit specifically for Groove G30 platform devices."""
    return {"not-applicable": "Groove G30s (H4 links) do not need internal optical crossconnections configurations"}


@attributedispatch("platform")
def modify_optical_circuit(
    source_optical_device: OpticalDeviceBlock,
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth],  # noqa: ARG001
    label: str | None = None,  # noqa: ARG001
    old_passband: Passband | None = None,  # noqa: ARG001
    old_spectrum_name: str | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Modify an optical circuit based on the platform type.

    Args:
        source_optical_device: The source optical device configuration
        optical_spectrum_section: The spectrum section configuration
        optical_spectrum_name: Name identifier for the optical spectrum
        passband: Frequency range allowed for transmission
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal
        label: Optional label for the circuit
        old_passband: The old passband of the optical circuit
        old_spectrum_name: The old name of the optical circuit

    Returns:
        dict[str, Any]: Platform-specific deployment configuration
    """
    return attribute_dispatch_base(deploy_optical_circuit, "platform", source_optical_device.platform)


@modify_optical_circuit.register(Platform.FlexILS)
def _(
    source_optical_device: OpticalDeviceBlock,
    optical_spectrum_section: OpticalSpectrumSectionBlock,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    old_passband: Passband | None = None,
    old_spectrum_name: str | None = None,
) -> dict[str, Any]:
    osnc_name = optical_spectrum_name.replace(" ", "_")
    old_osnc_name = old_spectrum_name.replace(" ", "_") if old_spectrum_name else None

    flex, osnc = _find_flexils_osnc(
        old_osnc_name if old_osnc_name else osnc_name,
        optical_spectrum_section,
        old_passband,
    )

    for port in optical_spectrum_section.add_drop_ports:
        od = port.optical_device
        if od.fqdn.startswith(flex.tid):
            continue
        remote_flex = get_optical_device_client(od)

    path = optical_spectrum_section.optical_path
    pops = [port.optical_device.pop.code.lower() for port in path[::2]]
    pops.append(path[-1].optical_device.pop.code.lower())
    oel_name = "-".join(pops)

    matches_oel = osnc["OELAID"].strip(r"\" ") == oel_name[:64]
    if not matches_oel:
        add_drop_ports = optical_spectrum_section.add_drop_ports
        dst_optical_device = add_drop_ports[1].optical_device
        omses = _divide_path_into_omses(path)
        new_oel = _find_or_create_oel(
            oel_name,
            source_optical_device,
            dst_optical_device,
            omses,
        )

    matches_spectrum = all(int(x) == y for x, y in zip(osnc["PASSBANDLIST"], passband, strict=True)) and all(
        int(x) == y for x, y in zip(osnc["CARRIERLIST"], carrier, strict=True)
    )

    if not matches_spectrum or not matches_oel:
        flex.ed_osnc(
            aid=osnc["LOCENDPOINT"],
            passbandlist=passband,
            carrierlist=carrier,
            oelaid=oel_name,
            is_oos="OOS",
        )

    flex.ed_osnc(
        aid=osnc["LOCENDPOINT"],
        cktidsuffix=osnc_name,
        is_oos="IS",
        label=rf"{label}" if label else osnc["LABEL"],
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
        "new OEL": new_oel if not matches_oel else None,
        "OSNC": osnc,
    }


@modify_optical_circuit.register(Platform.Groove_G30)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth],  # noqa: ARG001
    label: str | None = None,  # noqa: ARG001
    old_passband: Passband | None = None,  # noqa: ARG001
    old_spectrum_name: str | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """Modify an optical circuit specifically for Groove G30 platform devices."""
    return {"not-applicable": "Groove G30s (H4 links) do not have any internal optical crossconnections to modify"}


@attributedispatch("platform")
def delete_optical_circuit(
    source_optical_device: OpticalDeviceBlock,
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Delete an optical circuit based on the platform type.

    Args:
        source_optical_device: The source optical device configuration
        optical_spectrum_section: The spectrum section configuration
        optical_spectrum_name: Name identifier for the optical spectrum
        passband: Frequency range allowed for transmission

    Returns:
        dict[str, Any]: Platform-specific deletion result
    """
    return attribute_dispatch_base(delete_optical_circuit, "platform", source_optical_device.platform)


@delete_optical_circuit.register(Platform.FlexILS)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,
    optical_spectrum_name: str,
    passband: Passband,
) -> dict[str, Any]:
    """Delete an optical circuit specifically for FlexILS platform devices."""
    osnc_name = optical_spectrum_name.replace(" ", "_")

    flex, osnc = _find_flexils_osnc(
        osnc_name,
        optical_spectrum_section,
        passband,
    )

    # Lock the OSNC in admin state
    flex.ed_osnc(aid=osnc["LOCENDPOINT"], is_oos="OOS")

    # Delete the OSNC
    flex.dlt_osnc(aid=osnc["LOCENDPOINT"])

    return {"deleted_OSNC": osnc["LOCENDPOINT"]}


@delete_optical_circuit.register(Platform.Groove_G30)
def _(
    source_optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
) -> dict[str, Any]:
    """Delete an optical circuit specifically for Groove G30 platform devices."""
    return {"not-applicable": "Groove G30s (H4 links) do not have any internal optical crossconnections to delete"}


@attributedispatch("platform")
def validate_optical_circuit(
    optical_device: OpticalDeviceBlock,
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth],  # noqa: ARG001
    label: str,  # noqa: ARG001
) -> None:
    """
    Validate the optical spectrum section configuration on the specified optical device.

    Args:
        optical_device: The optical device to validate
        optical_spectrum_section: The optical spectrum section to validate
        optical_spectrum_name: Name of the optical spectrum
        passband: Frequency range allowed for transmission
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal
        label: Service label to validate

    Raises:
        ValueError: If the configuration is invalid
    """
    return attribute_dispatch_base(validate_optical_circuit, "platform", optical_device.platform)


@validate_optical_circuit.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str,
) -> None:
    flex, osnc = _find_flexils_osnc(
        optical_spectrum_name,
        optical_spectrum_section,
        passband,
    )  # already raises error if CKTIDSUFFIX/LOCENDPOINT/REMENDPOINT/PASSBANDLIST do not match

    for port in optical_spectrum_section.add_drop_ports:
        od = port.optical_device
        if od.fqdn.startswith(flex.tid):
            continue
        remote_flex = get_optical_device_client(od)

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


@validate_optical_circuit.register(Platform.Groove_G30)
def _(
    optical_device: OpticalDeviceBlock,  # noqa: ARG001
    optical_spectrum_section: OpticalSpectrumSectionBlock,  # noqa: ARG001
    optical_spectrum_name: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth],  # noqa: ARG001
    label: str,  # noqa: ARG001
) -> None:
    # Groove G30s (H4 links) do not have internal optical crossconnections to validate
    return None


@attributedispatch("platform")
def create_optical_cross_connection(
    optical_device: OpticalDeviceBlock,
    from_port: str,  # noqa: ARG001
    to_port: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth] | None = None,  # noqa: ARG001
    label: str | None = None,  # noqa: ARG001
    circuit_name: str | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Create an optical cross connection based on the platform type.

    Args:
        optical_device: The optical device configuration
        from_port: The port to connect from
        to_port: The port to connect to
        passband: Frequency range allowed for transmission
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal
        label: Optional label for the connection
        circuit_name: Optional name for the circuit

    Returns:
        dict[str, Any]: Platform-specific cross connection configuration
    """
    return attribute_dispatch_base(create_optical_cross_connection, "platform", optical_device.platform)


@create_optical_cross_connection.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    from_port: str,
    to_port: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str = "",
    xconn_name: str = "",
) -> dict[str, Any]:
    """Create an optical cross connection specifically for FlexILS platform devices."""
    if label:
        label = rf'"{label}"'

    if xconn_name:
        xconn_name = rf'"{xconn_name}"'

    if carrier is None:
        carrier = ((passband[0] + passband[-1]) // 2, passband[-1] - passband[0])

    if "S" in to_port:
        # let's use the system port as from_port
        to_port, from_port = from_port, to_port

    flex = get_optical_device_client(optical_device)

    from_sch_id = _find_first_free_sch_id(flex, from_port)
    to_sch_id = _find_first_free_sch_id(flex, to_port)

    fromaid = f"{from_port}-{from_sch_id}"
    toaid = f"{to_port}-{to_sch_id}"

    flex.ent_ocrs(
        fromaid=fromaid,
        toaid=toaid,
        label=label,
        cktidsuffix=xconn_name,
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


@attributedispatch("platform")
def delete_optical_cross_connection(
    optical_device: OpticalDeviceBlock,
    from_port: str,  # noqa: ARG001
    to_port: str,  # noqa: ARG001
    passband: Passband,  # noqa: ARG001
    carrier: tuple[Frequency, Bandwidth] | None = None,  # noqa: ARG001
    label: str | None = None,  # noqa: ARG001
    circuit_name: str | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Delete an optical cross connection based on the platform type.

    Args:
        optical_device: The optical device configuration
        from_port: The port to disconnect from
        to_port: The port to disconnect to
        passband: Frequency range allowed for transmission
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal
        label: Optional label for the connection
        circuit_name: Optional name for the circuit

    Returns:
        dict[str, Any]: A dictionary with the result of the deletion operation.
    """
    return attribute_dispatch_base(delete_optical_cross_connection, "platform", optical_device.platform)


@delete_optical_cross_connection.register(Platform.FlexILS)
def _(
    optical_device: OpticalDeviceBlock,
    from_port: str,
    to_port: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str = "",
    xconn_name: str = "",
) -> dict[str, Any]:
    """Delete an optical cross connection specifically for FlexILS platform devices."""
    if carrier is None:
        carrier = ((passband[0] + passband[-1]) // 2, passband[-1] - passband[0])

    if "S" in to_port:
        # let's use the system port as from_port
        to_port, from_port = from_port, to_port

    flex = get_optical_device_client(optical_device)

    ocrs = flex.rtrv_ocrs().parsed_data
    for ocr in ocrs:
        ocr_from_port = ocr["FROMAID"].split("-")
        ocr_from_port = ocr_from_port[:-1]  # Remove the last part (SCH ID)
        ocr_from_port = "-".join(ocr_from_port)
        ocr_to_port = ocr["TOAID"].split("-")
        ocr_to_port = ocr_to_port[:-1]  # Remove the last part (SCH ID)
        ocr_to_port = "-".join(ocr_to_port)
        ocr_passband = tuple(int(x) for x in ocr["PASSBANDLIST"])
        ocr_carrier = tuple(int(x) for x in ocr["CARRIERLIST"])
        ocr_xconn_name = ocr["CKTIDSUFFIX"].strip(r"\" ")
        ocr_label = ocr["LABEL"].strip(r"\" ")
        if (
            ocr_from_port == from_port
            and ocr_to_port == to_port
            and ocr_passband == passband
            and ocr_carrier == carrier
            and ocr_xconn_name == xconn_name
            and ocr_label == label
        ):
            return flex.dlt_ocrs(fromaid=ocr["FROMAID"], toaid=ocr["TOAID"])

    msg = (
        f"Could not find the optical cross connection from {from_port} to {to_port} "
        f"with passband {passband}, carrier {carrier}, label '{label}', and circuit name '{xconn_name}'"
    )
    raise ValueError(msg)
