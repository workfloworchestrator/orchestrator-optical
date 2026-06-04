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

from decimal import Decimal
from re import search
from typing import Any, Literal

from requests.exceptions import HTTPError

from orchestrator_optical.products.product_blocks.optical_digital_service import (
    ClientSpeednType,
)
from orchestrator_optical.products.product_blocks.optical_node import (
    OpticalNodeBlockUnion,
    VendorAndPlatform,
)
from orchestrator_optical.products.services.optical_node import get_optical_node_client
from orchestrator_optical.products.services.optical_port import (
    g30_ids_from_port_name,
    g30_port_navigator_node_from_port_name,
)
from orchestrator_optical.services.nokia import G42Client
from orchestrator_optical.services.nokia.g42.data_models.ioa_network_element import XconItem
from orchestrator_optical.services.nokia.g42.data_navigators.ioa_network_element import (
    PortItemNode,
    SuperChannelItemNode,
    TomNode,
)
from orchestrator_optical.utils.attributedispatch import (
    attribute_dispatch_base,
    attributedispatch,
)
from orchestrator_optical.utils.custom_types.frequencies import Frequency
from orchestrator_optical.utils.datadiff import compare_dicts, compare_pydantic_objects


def _g30_get_modulation_and_rate_from_mode(port_mode: str) -> tuple[str, str]:
    """
    Retrieves modulation and rate class for a given port mode.
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
    # Use .get() to handle non-coherent modes like '10GBE' or 'not-applicable'
    return port_mode_map.get(port_mode, ("not-applicable", "not-applicable"))


@attributedispatch("vendor_and_platform")
def get_signal_bandwidth(optical_node: OpticalNodeBlockUnion, port_name: str) -> int:  # noqa: ARG001
    return attribute_dispatch_base(get_signal_bandwidth, "vendor_and_platform", optical_node.vendor_and_platform)


@get_signal_bandwidth.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(optical_node: OpticalNodeBlockUnion, port_name: str) -> int:
    endpoint = g30_port_navigator_node_from_port_name(optical_node, port_name)[0]
    och_os = endpoint.och_os.retrieve(depth=2, content="config")
    if och_os.fec_type == "SDFEC27ND":
        bw = 75_000
    elif och_os.fec_type == "SDFEC15ND2":
        bw = 68_750
    else:
        bw = 37_500

    return bw


@get_signal_bandwidth.register(VendorAndPlatform.NOKIA_GX_G42)
def _(optical_node: OpticalNodeBlockUnion, port_name: str) -> int:
    g42 = get_optical_node_client(optical_node)

    channel = None
    channels = g42.data.ne.facilities.super_channel.retrieve(depth=2)
    for ch in channels:
        if any(carrier.startswith(port_name) for carrier in ch.carriers):
            channel = ch
            break

    if channel is None:
        msg = f"Channel of port {port_name} not found"
        raise ValueError(msg)

    bw = channel.spectral_bandwidth
    bw = bw * 1000
    num_carriers_if_coupled = 2
    if len(channel.carriers) == num_carriers_if_coupled:
        bw = bw // 2
    return round(bw)


@attributedispatch("vendor_and_platform")
def configure_line_transceivers(
    optical_node: OpticalNodeBlockUnion,
    port_names: tuple[str],  # noqa: ARG001
    central_frequencies: tuple[Frequency],  # noqa: ARG001
    modes: tuple[str],  # noqa: ARG001
    descriptions: tuple[str],  # noqa: ARG001
) -> dict[str, Any]:
    return attribute_dispatch_base(configure_line_transceivers, "vendor_and_platform", optical_node.vendor_and_platform)


@configure_line_transceivers.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_names: tuple[str],
    central_frequencies: tuple[Frequency],
    modes: tuple[str],
    descriptions: tuple[str],
) -> dict[str, Any]:
    configurations = {}
    for port_name, central_frequency, mode, description in zip(
        port_names,
        central_frequencies,
        modes,
        descriptions,
        strict=True,
    ):
        uri, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node, port_name)
        before = uri.retrieve(depth=3, content="config")
        uri.update(
            port_id=port_id,
            port_mode=mode,
            service_label=description,
            admin_status="up",
        )
        modulation, rate = _g30_get_modulation_and_rate_from_mode(mode)
        uri.och_os.update(
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
        after = uri.retrieve(depth=3, content="config")
        diffs = compare_pydantic_objects(before, after)
        configurations[port_name] = diffs

    return configurations


@configure_line_transceivers.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_names: tuple[str],
    central_frequencies: tuple[Frequency],
    modes: tuple[str],
    descriptions: tuple[str],
) -> dict[str, Any]:
    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 transponder line configuration but got {modes}."
        raise ValueError(msg)

    g42 = get_optical_node_client(optical_node)
    configurations = {}

    # port
    for port_name, description in zip(port_names, descriptions, strict=True):
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        navigator: PortItemNode = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        before = navigator.retrieve(content="config", depth=2)
        conf = before.model_copy(deep=True)
        conf.admin_state = "unlock"
        conf.label = description
        conf.alarm_report_control = "allowed"
        navigator.update(conf)
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"port-{port_name}"] = diffs

        # super-channel-group
        navigator = g42.data.ne.facilities.super_channel_group(port_name)
        before = navigator.retrieve(content="config", depth=2)
        navigator.update(name=port_name, admin_state="unlock", label=description, alarm_report_control="allowed")
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"super-channel-group-{port_name}"] = diffs

    # super-channel
    sup_ch_name = "_".join(port_names)
    navigator: SuperChannelItemNode = g42.data.ne.facilities.super_channel(sup_ch_name)
    before = navigator.retrieve(content="config", depth=2)
    navigator.update(
        name=sup_ch_name,
        admin_state="unlock",
        label="+".join(descriptions),
        alarm_report_control="allowed",
        carrier_mode=modes[0],
        carriers=[f"{port_name}-1" for port_name in port_names],
    )
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["super-channel"] = diffs

    # optical-carrier
    for port_name, description, frequency in zip(port_names, descriptions, central_frequencies, strict=True):
        navigator = g42.data.ne.facilities.optical_carrier(f"{port_name}-1")
        before = navigator.retrieve(content="config", depth=2)
        navigator.update(
            name=f"{port_name}-1",
            admin_state="unlock",
            label=description,
            alarm_report_control="allowed",
            frequency=frequency,
            enable_advanced_parameters=True,
            sop_data_collection=20,
        )
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"optical-carrier-{port_name}-1"] = diffs

    return configurations


@attributedispatch("vendor_and_platform")
def configure_transceiver_client(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,  # noqa: ARG001
    description: str,  # noqa: ARG001
    service_type_n_speed: ClientSpeednType,  # noqa: ARG001
) -> dict[str, Any]:
    return attribute_dispatch_base(
        configure_transceiver_client, "vendor_and_platform", optical_node.vendor_and_platform
    )


@configure_transceiver_client.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,
    description: str,
    service_type_n_speed: ClientSpeednType,
) -> dict[str, Any]:
    navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node, port_name)

    if service_type_n_speed == ClientSpeednType.Ethernet100Gbps:
        port_mode = "100GBE"
        eth = navigator.eth100g
        fec_type = "auto"
    elif service_type_n_speed == ClientSpeednType.Ethernet400Gbps:
        port_mode = "400GBE"
        eth = navigator.eth400g
        fec_type = "enabled"
    else:
        msg = f"Unsupported service type and speed: {service_type_n_speed} for {optical_node.pqdn} {port_name}"
        raise ValueError(msg)

    before = navigator.retrieve(content="config", depth=3)

    navigator.update(
        port_id=port_id,
        admin_status="up",
        service_label=description,
        port_mode=port_mode,
    )

    eth.update(
        admin_status="up",
        service_label=description,
        loopback_enable="disabled",
        test_signal_enable="NONE",
        client_shutdown="no",
        eth_fec_type=fec_type,
    )

    after = navigator.retrieve(content="config", depth=3)

    return compare_pydantic_objects(before, after)


@configure_transceiver_client.register(VendorAndPlatform.NOKIA_GX_G42)
def _(  # noqa: PLR0915
    optical_node: OpticalNodeBlockUnion,
    port_name: str,
    description: str,
    service_type_n_speed: ClientSpeednType,
) -> dict[str, Any]:
    g42 = get_optical_node_client(optical_node)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    if service_type_n_speed == ClientSpeednType.Ethernet100Gbps:
        required_type = "gx:QSFP28"
        required_subtype = "TOM-100G-Q"
        phy_mode = "100G"
        service_type = "100GBE"
    elif service_type_n_speed == ClientSpeednType.Ethernet400Gbps:
        required_type = "gx:QSFPDD"
        required_subtype = "TOM-400G-Q-DR4"
        phy_mode = "400GE"
        service_type = "400GBE"

    configurations = {}

    # port
    navigator: PortItemNode = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = "unlock"
    conf.label = description
    conf.alarm_report_control = "allowed"
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["1.port"] = diffs

    # TOM
    navigator: TomNode = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = "unlock"
    conf.label = description
    conf.required_type = required_type
    conf.required_subtype = required_subtype
    conf.phy_mode = phy_mode
    conf.alarm_report_control = "allowed"
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["2.tom"] = diffs

    # trib-ptp
    navigator = g42.data.ne.facilities.trib_ptp(port_name)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = "unlock"
    conf.label = description
    conf.alarm_report_control = "allowed"
    conf.service_type = service_type
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["3.trib-ptp"] = diffs

    # ethernet
    navigator = g42.data.ne.facilities.ethernet(port_name)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = "unlock"
    conf.label = description
    conf.alarm_report_control = "allowed"
    conf.fec_mode = "enabled"
    conf.loopback = "none"
    conf.test_signal_type = "none"
    conf.test_signal_direction = "egress"
    conf.test_signal_monitoring = False
    conf.lldp_admin_status = "rx-only"
    conf.lldp_ingress_mode = "snoop"
    conf.lldp_egress_mode = "snoop"
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["4.ethernet"] = diffs

    return configurations


@attributedispatch("vendor_and_platform")
def configure_transponder_crossconnect(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,  # noqa: ARG001
    line_port_names: list[str],  # noqa: ARG001
    xconn_description: str = "",  # noqa: ARG001
) -> dict[str, Any]:
    """
    Configure a cross-connect between client and line ports on an optical device.

    Args:
        optical_node: The optical device to configure
        client_port_name: The client port name (e.g. "port-1/2/3")
        line_port_names: List of line port names
        xconn_description: Optional description for the cross-connect

    Returns:
        The created cross-connect configuration
    """
    return attribute_dispatch_base(
        configure_transponder_crossconnect, "vendor_and_platform", optical_node.vendor_and_platform
    )


@configure_transponder_crossconnect.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(  # noqa: PLR0912, PLR0915
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    g30 = get_optical_node_client(optical_node)
    shelf_id, slot_id, _, c_port_id, _ = g30_ids_from_port_name(client_port_name)

    before = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")

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
        msg = f"No eth service found on {optical_node.pqdn} {client_port_name}"
        raise ValueError(msg)

    odu_a = (
        f"/ne:ne/shelf[shelf-id='{shelf_id}']/slot[slot-id='{slot_id}']/card/port[port-id='{c_port_id}']"
        f"/{eth_key}/odu[odutype-L1='odu4'][oduid-L1='1'][odutype-L2='unused'][oduid-L2='0']"
        f"[odutype-L3='unused'][oduid-L3='0'][odutype-L4='unused'][oduid-L4='0']"
    )

    odu_b = None
    try:
        crs = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            crs = []
        else:
            raise
    for c in crs:
        if c.src_tp == odu_a:
            odu_b = c.dst_tp
            odu_a, odu_b = (
                odu_b,
                odu_a,
            )  # swap the strings, so that src-tp is odu_b string
            break
        if c.dst_tp == odu_a:
            odu_b = c.src_tp
            break

    if odu_b:
        id1, id2, id3 = _extract_shelf_slot_port_ids_from_odu_string(odu_b)

        if shelf_id != id1 or slot_id != id2 or id3 not in line_port_ids:
            xconn = g30.data.ne_ne.services.CRS(odu_b, odu_a)
            xconn.delete()
            odu_b = None

    if odu_b is None:
        possible_odus: list[tuple[int, str]] = []
        for line_port_id in line_port_ids:
            och_os = (
                g30.data.ne_ne.shelf(shelf_id)
                .slot(slot_id)
                .card.port(line_port_id)
                .och_os.retrieve(depth=4, content="config")
            )
            otu_key = next(
                (
                    f
                    for f in (
                        "otuc2",
                        "otuc3",
                        "otuc4",
                        "otuc5",
                        "otuc6",
                        "otuc7",
                        "otuc9",
                        "otuc11",
                        "otu4",
                        "otu2",
                        "otu2e",
                    )
                    if getattr(client_port, f, None) is not None
                ),
                None,
            )
            for odu in getattr(och_os, otu_key).odu:
                key_list = [
                    "odutype-L1",
                    "oduid-L1",
                    "odutype-L2",
                    "oduid-L2",
                    "odutype-L3",
                    "oduid-L3",
                    "odutype-L4",
                    "oduid-L4",
                ]

                if any(getattr(odu, key, None) is None for key in key_list):
                    continue

                if all(getattr(odu, key, None) != "odu4" for key in key_list):
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

        used_odus = set()
        for c in crs:
            used_odus.add(c.dst_tp)
            used_odus.add(c.src_tp)

        available_odus = [odu for odu in possible_odus if odu[1] not in used_odus]
        if not available_odus:
            msg = f"No available ODU for crossconnect on {optical_node.pqdn}"
            raise ValueError(msg)
        available_odus.sort(key=lambda x: x[0])  # sort by index
        odu_b = available_odus[0][1]  # take the first available ODU string

    xconn = g30.data.ne_ne.services.CRS(odu_b, odu_a)
    xconn.update(
        src_tp=odu_b,
        dst_tp=odu_a,
        service_label=xconn_description,
    )

    after = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    return compare_pydantic_objects(before, after)


def _extract_shelf_slot_port_ids_from_odu_string(
    odu_string: str,
) -> tuple[int, int, int]:
    shelf_match = search(r"shelf\[shelf-id='(\d+)'\]", odu_string)
    slot_match = search(r"slot\[slot-id='(\d+)'\]", odu_string)
    port_match = search(r"port\[port-id='(\d+)'\]", odu_string)

    shelf_id = shelf_match.group(1) if shelf_match else None
    slot_id = slot_match.group(1) if slot_match else None
    port_id = port_match.group(1) if port_match else None

    return int(shelf_id), int(slot_id), int(port_id)


@configure_transponder_crossconnect.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    g42 = get_optical_node_client(optical_node)

    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"
    och_key = _derive_optical_channel_key(line_port_names)
    dst_parent_odu = f"{och_key}-ODUCni"
    direction = "two-way"
    label = xconn_description
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcon = _find_xcon_g42(g42, client, och_key, direction, payload_type)
    if xcon:
        endpoint = g42.data.ne.services.xcon(xcon.name)
        before = endpoint.retrieve(depth=2, content="config")
        xcon = before.model_copy(deep=True)
        xcon.label = label
        xcon.circuit_id_suffix = label
        endpoint.update(xcon)
        after = endpoint.retrieve(depth=2, content="config")
        return compare_pydantic_objects(before, after)

    dst_time_slots = _retrieve_time_slots(g42, dst_parent_odu, payload_type)
    _create_xcon_g42(
        g42=g42,
        client=client,
        dst_parent_odu=dst_parent_odu,
        direction=direction,
        payload_type=payload_type,
        label=label,
        dst_time_slots=dst_time_slots,
    )
    xcon = _find_xcon_g42(g42, client, och_key, direction, payload_type)
    if xcon:
        return xcon.model_dump(exclude_unset=True)

    msg = f"Unable to create XCON for client {client_port_name} on {optical_node.pqdn}. "
    raise ValueError(msg)


def _find_xcon_g42(
    g42: G42Client,
    client: str,
    line: str,
    direction: str,
    payload_type: str,
) -> XconItem | None:
    """
    Helper function to find an existing cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client: Source client path.
        line: Line ID inside the destination ODU string.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.

    Returns:
        The cross-connect configuration if found, otherwise None.

    Raises:
        ValueError: If a cross-connect with the same source and destination already exists.
    """
    try:
        xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            return None
        raise

    for xcon in xcons:
        source_destination_match = (xcon.source == client and line in xcon.destination) or (
            xcon.destination == client and line in xcon.source
        )
        payload_type_match = xcon.payload_type == payload_type
        direction_match = xcon.direction == direction
        if source_destination_match and payload_type_match and direction_match:
            return xcon

        if client in (xcon.source, xcon.destination):
            msg = (
                f"Tributary already cross-connected:"
                f" {xcon.destination}  x  {xcon.source} ."
                f"Please check and remove manually if wrong."
            )
            raise ValueError(msg)

    return None


def _create_xcon_g42(
    g42: G42Client,
    client: str,
    dst_parent_odu: str,
    direction: str,
    payload_type: str,
    label: str,
    dst_time_slots: str,
) -> None:
    """
    Helper function to create a cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client: Source client path.
        dst_parent_odu: Destination parent ODU path.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.
        label: Label for the cross-connect.
        dst_time_slots: Time slots for the cross-connect.

    Raises:
        HTTPError: If the cross-connect creation fails.
    """
    try:
        g42.operations.create_xcon(
            payload_type=payload_type,
            direction=direction,
            label=label,
            circuit_id_suffix=label,
            source=client,
            dst_parent_odu=dst_parent_odu,
            dst_time_slots=dst_time_slots,
        )
    except HTTPError as e:
        xcon_already_exists_code = 412
        if e.response.status_code == xcon_already_exists_code:
            pass
        else:
            raise


def _derive_optical_channel_key(line_port_names: list[str]) -> str:
    if len(line_port_names) == 1:
        return f"{line_port_names[0]}-1"

    num_lines_if_coupled_mode = 2
    if len(line_port_names) == num_lines_if_coupled_mode:
        for name in line_port_names:
            if name.endswith("L1"):
                return f"{name}-1"

    msg = (
        f"Invalid line port names: {line_port_names}. "
        "For coupled modes, ensure both ports are on the same card, thus one ends with 'L1'."
    )
    raise ValueError(msg)


def _retrieve_payload_type(g42: G42Client, client_port_name: str) -> Literal["100GBE", "400GBE"]:
    trib_ptp = g42.data.ne.facilities.trib_ptp(client_port_name).retrieve(depth=2, content="config")
    payload_type = trib_ptp.service_type

    if payload_type is None:
        msg = f"Unable to retrieve payload type for {g42.url} {client_port_name}"
        raise ValueError(msg)
    if payload_type not in ["100GBE", "400GBE"]:
        msg = f"Invalid payload type '{payload_type}' for {g42.url} {client_port_name}. Expected '100GBE' or '400GBE'."
        raise ValueError(msg)

    return payload_type


def _retrieve_time_slots(g42: G42Client, odu_name: str, speed: Literal["100GBE", "400GBE"]) -> str:
    minimum_slots_required = 80 if speed == "100GBE" else 320

    odu = g42.data.ne.facilities.odu(odu_name).retrieve(depth=2)
    available_time_slots = odu.available_time_slots  # e.g. "1..80,161..480"
    if not available_time_slots:
        msg = f"The key 'available-time-slots' is missing or empty in the ODU data.ODU: {odu}"
        raise ValueError(msg)
    available_time_slots = available_time_slots.split(",")  # e.g. ["1..80", "161..480"]
    available_time_slots = [ts.split("..") for ts in available_time_slots]  # e.g. [["1", "80"], ["161", "480"]]
    available_time_slots = [(int(start), int(end)) for start, end in available_time_slots]  # e.g. [(1, 80), (161, 480)]

    # find next time slot that has at least minimum_slots_required
    for start, end in available_time_slots:
        if end - start + 1 >= minimum_slots_required:
            return f"{start}..{start + minimum_slots_required - 1}"

    msg = (
        f"Not enough available time slots for {g42.url} {odu}. "
        f"Minimum required: {minimum_slots_required}, "
        f"Available: {available_time_slots}"
    )
    raise ValueError(msg)


@attributedispatch("vendor_and_platform")
def delete_transponder_crossconnect(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Delete a cross-connect between client and line ports on transponder device.

    Args:
        optical_node: The transponder
        client_port_name: The client port name (e.g. "port-1/2/3")

    Returns:
        dict: {
            "message": f"{optical_node.pqdn} {client_port_name}: {variable message}",
            "deleted_xcon": list of deleted xcons
        }
    """
    return attribute_dispatch_base(
        delete_transponder_crossconnect, "vendor_and_platform", optical_node.vendor_and_platform
    )


@delete_transponder_crossconnect.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,
) -> dict[str, Any]:
    result = {"message": "", "deleted_xcon": []}

    g30 = get_optical_node_client(optical_node)

    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(client_port_name)

    uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card

    card = uri.retrieve(depth=2)
    if card.required_type == "CHM1":
        result["message"] = (
            f"{optical_node.pqdn} {client_port_name}: no need to delete any xcon,"
            " CHM1 crossconnections are not configurable."
        )
        return result

    client_port = uri.port(port_id).retrieve(depth=3, content="config")
    eth_key = next((f for f in ("eth100g", "eth400g") if getattr(client_port, f, None) is not None), None)
    if not eth_key:
        result["message"] = (
            f"{optical_node.pqdn} {client_port_name}:"
            " This port does not have an ethernet service, it must have been deleted manually."
        )
        return result

    odu_string = (
        f"/ne:ne/shelf[shelf-id='{shelf_id}']/slot[slot-id='{slot_id}']"
        f"/card/port[port-id='{port_id}']/{eth_key}/odu[odutype-L1='odu4']"
        f"[oduid-L1='1'][odutype-L2='unused'][oduid-L2='0']"
        f"[odutype-L3='unused'][oduid-L3='0'][odutype-L4='unused'][oduid-L4='0']"
    )

    try:
        crs = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            crs = []
        else:
            raise

    deleted_crs = []
    for c in crs:
        if odu_string in {c.src_tp, c.dst_tp}:
            g30.data.ne_ne.services.CRS(c.src_tp, c.dst_tp).delete()
            deleted_crs.append(c)

    if not deleted_crs:
        result["message"] = (
            f"{optical_node.pqdn} {client_port_name}:"
            " There was no cross-connection associated to this client port in the configuration."
        )
        return result

    result["deleted_xcon"] = deleted_crs
    return result


@delete_transponder_crossconnect.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,
) -> dict[str, Any]:
    result = {"message": "", "deleted_xcon": []}

    g42 = get_optical_node_client(optical_node)
    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"

    try:
        xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            xcons = []
        else:
            raise

    deleted_xcons = []
    for xcon in xcons:
        if client in (xcon.source, xcon.destination):
            uri = g42.data.ne.services.xcon(xcon.name)
            uri.delete()
            deleted_xcons.append(xcon)

    if not deleted_xcons:
        result["message"] = (
            f"{optical_node.pqdn} {client_port_name}:"
            " There was no cross-connection associated to this client port in the configuration."
        )
        return result

    result["deleted_xcon"] = deleted_xcons
    return result


@attributedispatch("vendor_and_platform")
def factory_reset_transponder_client(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,  # noqa: ARG001
) -> dict[str, Any]:
    return attribute_dispatch_base(
        factory_reset_transponder_client, "vendor_and_platform", optical_node.vendor_and_platform
    )


@factory_reset_transponder_client.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,
) -> dict[str, Any]:
    navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node, port_name)
    before = navigator.retrieve(depth=3, content="config")
    navigator.update(
        port_id=port_id,
        admin_status="down",
        service_label="",
        port_mode="not-applicable",
    )
    after = navigator.retrieve(depth=3, content="config")
    return compare_pydantic_objects(before, after)


@factory_reset_transponder_client.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,
) -> dict[str, Any]:
    g42 = get_optical_node_client(optical_node)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    configurations = {}

    # 1. Ethernet configuration
    navigator = g42.data.ne.facilities.ethernet(port_name)
    conf = navigator.retrieve(content="config", depth=2)
    navigator.update(name=port_name, label="")
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["1.ethernet"] = diff

    # 2. Tributary point-to-point configuration
    navigator = g42.data.ne.facilities.trib_ptp(port_name)
    conf = navigator.retrieve(content="config", depth=2)
    navigator.update(name=port_name, label="", admin_state="lock")
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["2.trib-ptp"] = diff

    # 3. TOM configuration
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    conf = navigator.retrieve(content="config", depth=2)
    updated_conf = conf.model_copy(deep=True)
    updated_conf.label = ""
    updated_conf.admin_state = "lock"
    navigator.update(updated_conf)
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["3.tom"] = diff

    # 4. Port configuration
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = navigator.retrieve(content="config", depth=2)
    updated_conf = conf.model_copy(deep=True)
    updated_conf.label = ""
    updated_conf.admin_state = "lock"
    navigator.update(updated_conf)
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["4.port"] = diff

    return configurations


@attributedispatch("vendor_and_platform")
def factory_reset_transponder_lines(
    optical_node: OpticalNodeBlockUnion,
    line_port_names: list[str],  # noqa: ARG001
) -> dict[str, Any]:
    """
    Factory reset the transponder line configuration for the specified port.

    Args:
        optical_node: The optical device to reset.
        line_port_names: The line port names.

    Returns:
        The reset configuration.
    """
    return attribute_dispatch_base(
        factory_reset_transponder_lines, "vendor_and_platform", optical_node.vendor_and_platform
    )


@factory_reset_transponder_lines.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    line_port_names: list[str],
) -> dict[str, Any]:
    result = []
    for port_name in line_port_names:
        navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node, port_name)
        before = navigator.retrieve(depth=3, content="config")
        navigator.update(
            port_id=port_id,
            admin_status="down",
            service_label="",
            port_mode="not-applicable",
        )
        after = navigator.retrieve(depth=3, content="config")
        result.append(compare_pydantic_objects(before, after))
    return result


@factory_reset_transponder_lines.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    line_port_names: list[str],
) -> dict[str, Any]:
    g42 = get_optical_node_client(optical_node)
    configurations = {}

    for port_name in line_port_names:
        # port
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        navigator: PortItemNode = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        before = navigator.retrieve(content="config", depth=2)
        conf = before.model_copy(deep=True)
        conf.admin_state = "lock"
        conf.label = ""
        conf.alarm_report_control = "allowed"
        navigator.update(conf)
        after = navigator.retrieve(content="config", depth=2)
        diff = compare_pydantic_objects(before, after)
        configurations[f"port-{port_name}"] = diff

        # super-channel-group
        navigator = g42.data.ne.facilities.super_channel_group(port_name)
        before = navigator.retrieve(depth=2, content="config")
        navigator.update(name=port_name, admin_state="lock", label="", alarm_report_control="allowed")
        after = navigator.retrieve(depth=2, content="config")
        diff = compare_pydantic_objects(before, after)
        configurations[f"super-channel-group-{port_name}"] = diff

    # super-channel
    sup_ch_name = "_".join(line_port_names)
    navigator: SuperChannelItemNode = g42.data.ne.facilities.super_channel(sup_ch_name)
    before = navigator.retrieve(depth=2, content="config")
    navigator.delete()
    configurations[f"super-channel-{sup_ch_name}"] = compare_pydantic_objects(before, None)

    return configurations


@attributedispatch("vendor_and_platform")
def validate_trx_line(
    optical_node: OpticalNodeBlockUnion,
    port_names: tuple[str, ...],  # noqa: ARG001
    central_frequencies: tuple[Frequency, ...],  # noqa: ARG001
    modes: tuple[str, ...],  # noqa: ARG001
    descriptions: tuple[str, ...],  # noqa: ARG001
) -> None:
    """
    Validate the transceiver line configuration on the specified optical device.

    Args:
        optical_node: The optical device to validate.
        port_names: The line port names grouped by device.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Raises:
        ValueError: If the configuration is invalid.
    """
    return attribute_dispatch_base(validate_trx_line, "vendor_and_platform", optical_node.vendor_and_platform)


@validate_trx_line.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)

    if len(set(modes)) != 1:
        msg = f"All modes must be the same but got {modes}."
        raise ValueError(msg)

    g30 = get_optical_node_client(optical_node)

    for port_name, central_frequency, mode, description in zip(
        port_names,
        central_frequencies,
        modes,
        descriptions,
        strict=False,
    ):
        shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
        port_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)
        actual_config = port_uri.retrieve(depth=3, content="config").model_dump(exclude_unset=True)
        """ e.g. config looks like this:
            {
                "och-os": {
                    "fec-type": "SDFEC27ND",
                    "frequency": 194062500,
                    "alias-name": "och-os-2/1/2",
                    "rate-class": "300G",
                    "preemphasis": "enabled",
                    "admin-status": "up",
                    "cd-range-low": -280000,
                    "laser-enable": "enabled",
                    "rx-frequency": 194062500,
                    "cd-range-high": 280000,
                    "fast-sop-mode": "disabled",
                    "loopback-type": "none",
                    "service-label": "OCh173 sr00-pa01",
                    "rx-attenuation": "0.0",
                    "loopback-enable": "disabled",
                    "modulation-format": "DP-SP16QAM",
                    "preemphasis-value": "1.0",
                    "tx-filter-roll-off": "0.30",
                    "cd-compensation-mode": "auto",
                    "cd-compensation-value": 0,
                    "required-tx-optical-power": "3.0"
                },
                "port-id": 2,
                "port-mode": "SP16QAM_300G",
                "alias-name": "port-2/1/2",
                "admin-status": "up",
                "connected-to": "flex.pa01.garr.net 1-E1-1-T2B",
                "service-label": "OCh173 sr00-pa01",
                "external-connectivity": "yes"
            }
        """

        desired_config = {
            "och-os": {
                "frequency": central_frequency,
                "rx-frequency": central_frequency,
                "service-label": description,
                "admin-status": "up",
                "laser-enable": "enabled",
                "loopback-enable": "disabled",
                "loopback-type": "none",
            },
            "port-mode": mode,
            "service-label": description,
            "admin-status": "up",
        }

        diff = compare_dicts(desired_config, actual_config)
        if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
            msg = (
                f"Configuration mismatch for {optical_node.pqdn} {port_name}:\n"
                f"mismatch: {diff['mismatched_value']}\n"
                f"missing: {diff['missing_key']}\n"
            )
            raise ValueError(msg)


@validate_trx_line.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)

    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 validation but got {modes}."
        raise ValueError(msg)

    g42 = get_optical_node_client(optical_node)

    actual_config: dict[str, Any] = {
        "ports": {},
        "super-channel-groups": {},
        "optical-carriers": {},
        "super-channel": {},
    }

    desired_config: dict[str, Any] = {
        "ports": {},
        "super-channel-groups": {},
        "optical-carriers": {},
        "super-channel": {},
    }

    for port_name, central_frequency, description in zip(
        port_names,
        central_frequencies,
        descriptions,
        strict=False,
    ):
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        actual_config["ports"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

        endpoint = g42.data.ne.facilities.super_channel_group(port_name)
        actual_config["super-channel-groups"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(
            exclude_unset=True
        )

        endpoint = g42.data.ne.facilities.optical_carrier(f"{port_name}-1")
        actual_config["optical-carriers"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(
            exclude_unset=True
        )

        desired_config["ports"][port_name] = {
            "name": port_id,
            "label": description,
            "admin-state": "unlock",
            "alarm-report-control": "allowed",
        }
        desired_config["super-channel-groups"][port_name] = {
            "name": f"{shelf_id}-{slot_id}-{port_id}",
            "label": description,
            "admin-state": "unlock",
            "line-system-mode": "openwave",
            "alarm-report-control": "allowed",
        }
        desired_config["optical-carriers"][port_name] = {
            "name": f"{shelf_id}-{slot_id}-{port_id}-1",
            "label": description,
            "tx-cd": "0.00",
            "frequency": str(central_frequency),
            "admin-state": "unlock",
            "frequency-offset": 0,
            "alarm-report-control": "allowed",
        }

    super_channel_name = "_".join(port_names)
    endpoint = g42.data.ne.facilities.super_channel(super_channel_name)
    actual_config["super-channel"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

    carriers = [f"{port_name}-1" for port_name in port_names]
    desired_config["super-channel"] = {
        "name": super_channel_name,
        "label": "+".join(descriptions),
        "carriers": carriers,
        "admin-state": "unlock",
        "carrier-mode": modes[0],
        "alarm-report-control": "allowed",
    }

    """ e.g. actual config looks like this:
    {
        "ports": {
            "2-4-L1": {
                "name": "L1",
                "label": "OCh133 pa01-ct01",
                "alias-name": "",
                "admin-state": "unlock",
                "connected-to": "flex.ct01.garr.net 1-E2-4-T1A",
                "alarm-report-control": "allowed",
                "external-connectivity": "yes"
            }
        },
        "super-channel": {
            "2-4-L1": {
                "name": "2-4-L1",
                "label": "OCh133 pa01-ct01",
                "carriers": [
                    "2-4-L1-1"
                ],
                "admin-state": "unlock",
                "carrier-mode": "400E.96P",
                "alarm-report-control": "allowed"
            }
        },
        "optical-carrier": {
            "name": "2-4-L1-1",
            "label": "OCh133 pa01-ct01",
            "tx-cd": "0.00",
            "tx-power": "0.00",
            "frequency": "194368750",
            "admin-state": "unlock",
            "frequency-offset": 0,
            "dgd-high-threshold": 300,
            "sop-data-collection": "disabled",
            "alarm-report-control": "allowed",
            "enable-advanced-parameters": false,
            "pre-fec-q-sig-deg-threshold": "6.00",
            "post-fec-q-sig-deg-threshold": "18.0",
            "pre-fec-q-sig-deg-hysteresis": "0.5",
            "post-fec-q-sig-deg-hysteresis": "2.5"
        },
        "super-channel-group": {
            "2-4-L1": {
                "name": "2-4-L1",
                "label": "OCh133 pa01-ct01",
                "admin-state": "unlock",
                "line-system-mode": "openwave",
                "valid-signal-time": 480,
                "alarm-report-control": "allowed",
                "auto-in-service-enabled": false,
                "openwave-contention-check": false
            }
        }
    }
    """

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {optical_node.pqdn} {port_names}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


@attributedispatch("vendor_and_platform")
def validate_trx_client(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,  # noqa: ARG001
    description: str,  # noqa: ARG001
    service_type_n_speed: ClientSpeednType,  # noqa: ARG001
) -> None:
    """
    Validate the transceiver client configuration on the specified optical device.

    Args:
        optical_node: The optical device to validate.
        port_name: The client port name.
        description: The description of the client service.
        service_type_n_speed: The service type and speed of the client.

    Raises:
        ValueError: If the configuration is invalid.
    """
    return attribute_dispatch_base(validate_trx_client, "vendor_and_platform", optical_node.vendor_and_platform)


@validate_trx_client.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,
    description: str,
    service_type_n_speed: ClientSpeednType,
) -> None:
    g30 = get_optical_node_client(optical_node)

    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)

    port_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    if service_type_n_speed == ClientSpeednType.Ethernet100Gbps:
        port_mode = "100GBE"
        eth_name = "eth100g"
        fec_type = "auto"
    elif service_type_n_speed == ClientSpeednType.Ethernet400Gbps:
        port_mode = "400GBE"
        eth_name = "eth400g"
        fec_type = "enabled"
    else:
        msg = f"Unsupported service type and speed: {service_type_n_speed} for {optical_node.pqdn} {port_name}"
        raise ValueError(msg)

    actual_config = port_uri.retrieve(depth=3, content="config").model_dump(exclude_unset=True)
    """ e.g. config looks like this:
        {
            "eth100g": {
                "odu": {},
                "alias-name": "100gbe-3/3/3",
                "admin-status": "up",
                "eth-fec-type": "auto",
                "mapping-mode": "GMP",
                "near-end-als": "no",
                "loopback-type": "none",
                "service-label": "f155c01 OCh179 tp01-pa01 remote:g30.tp01.garr.net port-1/1/3",
                "holdoff-signal": "no",
                "lldp-status-if": "disabled",
                "client-shutdown": "no",
                "gfp-payload-fcs": "disabled",
                "loopback-enable": "disabled",
                "als-degrade-mode": "disabled",
                "test-signal-type": "NONE",
                "test-signal-enable": "NONE",
                "transmit-interpacketgap": 8,
                "client-shutdown-holdoff-timer": 0
            },
            "port-id": 3,
            "arc-timer": 1440,
            "pluggable": {
                "alias-name": "pluggable-3/3/3",
                "admin-status": "up",
                "required-type": "QSFP",
                "equipment-name": "QSFP-03-03-03"
            },
            "port-mode": "100GBE",
            "alias-name": "port-3/3/3",
            "arc-config": "nalm-qi",
            "admin-status": "up",
            "connected-to": "",
            "service-label": "f155c01 OCh179 tp01-pa01 remote:g30.tp01.garr.net port-1/1/3",
            "external-connectivity": "no"
        }
    """

    desired_config = {
        eth_name: {
            "admin-status": "up",
            "service-label": description,
            "loopback-enable": "disabled",
            "test-signal-enable": "NONE",
            "client-shutdown": "no",
            "eth-fec-type": fec_type,
            "mapping-mode": "GMP",
        },
        "pluggable": {
            "admin-status": "up",
        },
        "port-mode": port_mode,
        "admin-status": "up",
        "service-label": description,
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {optical_node.pqdn} {port_name}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


@validate_trx_client.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    port_name: str,
    description: str,
    service_type_n_speed: ClientSpeednType,
) -> None:
    g42 = get_optical_node_client(optical_node)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    if service_type_n_speed == ClientSpeednType.Ethernet100Gbps:
        required_type = "gx:QSFP28"
        required_subtype = "TOM-100G-Q"
        phy_mode = "100G"
        service_type = "100GBE"
    elif service_type_n_speed == ClientSpeednType.Ethernet400Gbps:
        required_type = "gx:QSFPDD"
        required_subtype = "TOM-400G-Q-DR4"
        phy_mode = "400GE"
        service_type = "400GBE"

    actual_config = {}
    # port
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    actual_config["port"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # TOM
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    actual_config["tom"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # trib-ptp
    endpoint = g42.data.ne.facilities.trib_ptp(port_name)
    actual_config["trib-ptp"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # ethernet
    endpoint = g42.data.ne.facilities.ethernet(port_name)
    actual_config["ethernet"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    """ e.g. actual config looks like this:
    {
        "port": {
            "tom": {},
            "name": "T1",
            "label": "f102c01 OCh133 pa01-ct01 remote:g42.pa01.garr.net 1-4-T1",
            "alias-name": "",
            "admin-state": "unlock",
            "connected-to": "",
            "alarm-report-control": "allowed",
            "external-connectivity": "no"
        },
        "tom": {
            "label": "f102c01 OCh133 pa01-ct01 remote:g42.pa01.garr.net 1-4-T1",
            "phy-mode": "400GE",
            "alias-name": "",
            "admin-state": "unlock",
            "required-type": "gx:QSFPDD",
            "required-subtype": "TOM-400G-Q-DR4",
            "alarm-report-control": "allowed"
        },
        "trib-ptp": {
            "name": "2-4-T1",
            "label": "f102c01 OCh133 pa01-ct01 remote:g42.pa01.garr.net 1-4-T1",
            "admin-state": "unlock",
            "service-type": "400GBE",
            "valid-signal-time": 480,
            "alarm-report-control": "allowed",
            "forward-defect-trigger": true,
            "auto-in-service-enabled": false,
            "tributary-disable-action": "send-idles",
            "power-threshold-low-offset": "0.00",
            "power-threshold-high-offset": "0.00"
        },
        "ethernet": {
            "name": "2-4-T1",
            "label": "f102c01 OCh133 pa01-ct01 remote:g42.pa01.garr.net 1-4-T1",
            "fec-mode": "enabled",
            "loopback": "none",
            "admin-state": "unlock",
            "lldp-egress-mode": "snoop",
            "test-signal-type": "none",
            "lldp-admin-status": "rx-only",
            "lldp-ingress-mode": "snoop",
            "alarm-report-control": "allowed",
            "test-signal-direction": "egress",
            "test-signal-monitoring": false,
            "fec-degraded-ser-monitoring": "disabled",
            "fec-degraded-ser-monitoring-period": 10,
            "fec-degraded-ser-activate-threshold": "0.0000100000",
            "fec-degraded-ser-deactivate-threshold": "0.00000800000"
        }
    }
    """

    desired_config = {
        "tom": {
            "label": description,
            "phy-mode": phy_mode,
            "admin-state": "unlock",
            "required-type": required_type,
            "required-subtype": required_subtype,
            "alarm-report-control": "allowed",
        },
        "port": {
            "label": description,
            "admin-state": "unlock",
            "alarm-report-control": "allowed",
        },
        "trib-ptp": {
            "label": description,
            "admin-state": "unlock",
            "service-type": service_type,
            "alarm-report-control": "allowed",
        },
        "ethernet": {
            "label": description,
            "fec-mode": "enabled",
            "loopback": "none",
            "admin-state": "unlock",
            "lldp-egress-mode": "snoop",
            "test-signal-type": "none",
            "lldp-admin-status": "rx-only",
            "lldp-ingress-mode": "snoop",
            "alarm-report-control": "allowed",
            "test-signal-direction": "egress",
            "test-signal-monitoring": False,
        },
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {optical_node.pqdn} {port_name}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


@attributedispatch("vendor_and_platform")
def validate_trx_crossconnect(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,  # noqa: ARG001
    line_port_names: list[str],  # noqa: ARG001
    xconn_description: str = "",  # noqa: ARG001
) -> None:
    """
    Validate the transponder cross-connect configuration on the specified optical device.

    Args:
        optical_node: The optical device to validate.
        client_port_name: The client port name.
        line_port_names: The line port names.
        xconn_description: The description of the cross-connect.

    Raises:
        ValueError: If the configuration is invalid.
    """
    return attribute_dispatch_base(validate_trx_crossconnect, "vendor_and_platform", optical_node.vendor_and_platform)


@validate_trx_crossconnect.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    g30 = get_optical_node_client(optical_node)
    crs_list = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    for c in crs_list:
        src_shelf_id, src_slot_id, src_port_id = _extract_shelf_slot_port_ids_from_odu_string(c.src_tp)
        dst_shelf_id, dst_slot_id, dst_port_id = _extract_shelf_slot_port_ids_from_odu_string(c.dst_tp)
        src_port_string = f"port-{src_shelf_id}/{src_slot_id}/{src_port_id}"
        dst_port_string = f"port-{dst_shelf_id}/{dst_slot_id}/{dst_port_id}"
        if (src_port_string == client_port_name and dst_port_string in line_port_names) or (
            dst_port_string == client_port_name and src_port_string in line_port_names
        ):
            if c.service_label != xconn_description:
                msg = (
                    f"Cross-connect description mismatch for {optical_node.pqdn} "
                    f"{client_port_name} to {dst_port_string}: "
                    f"Expected: {xconn_description}, Actual: {c.service_label}"
                )
                raise ValueError(msg)
            return

    msg = (
        f"Cross-connect not found for {optical_node.pqdn} {client_port_name} to {line_port_names}. "
        "Please ensure the cross-connect exists and is correctly configured then retry."
    )
    raise ValueError(msg)


@validate_trx_crossconnect.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    g42 = get_optical_node_client(optical_node)

    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"
    och_key = _derive_optical_channel_key(line_port_names)
    direction = "two-way"
    label = xconn_description
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")

    actual_config = None
    for xcon in xcons:
        if (xcon.source == client and och_key in xcon.destination) or (
            xcon.destination == client and och_key in xcon.source
        ):
            actual_config = xcon.model_dump(exclude_unset=True)
            break
        # already checked "source" and "destination" values
    """e.g. actual_config looks like this:
    {
        "name": "1-4-T1,1-4-L1-1-ODUflexi-1",
        "label": "f102c01 OCh133 pa01-ct01",
        "source": "/ioa-ne:ne/facilities/ethernet[name='1-4-T1']",
        "direction": "two-way",
        "destination": "/ioa-ne:ne/facilities/odu[name='1-4-L1-1-ODUflexi-1']",
        "payload-type": "400GBE",
        "circuit-id-suffix": "f102c01 OCh133 pa01-ct01"
    }
    """
    if actual_config is None:
        msg = (
            f"Cross-connect not found for {optical_node.pqdn} {client_port_name} to {line_port_names}. "
            "Please ensure the cross-connect exists and is correctly configured then retry."
        )
        raise ValueError(msg)

    desired_config = {
        "label": label,
        "direction": direction,
        "payload-type": payload_type,
        "circuit-id-suffix": label,
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {optical_node.pqdn} {client_port_name} to {line_port_names}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


@attributedispatch("vendor_and_platform")
def diff_btw_current_rx_power_and_target(
    optical_node: OpticalNodeBlockUnion,
    optical_spectrum_name: str,  # noqa: ARG001
) -> float:
    r"""
    Return the difference $P_{current_rx} - P_{target_rx}$ in dB for the specified optical channel.

    Args:
        optical_node: The optical device to compute for.
        optical_spectrum_name: The optical spectrum name.

    Returns:
        The delta target received power in dB.
    """
    return attribute_dispatch_base(
        diff_btw_current_rx_power_and_target, "vendor_and_platform", optical_node.vendor_and_platform
    )


@diff_btw_current_rx_power_and_target.register(VendorAndPlatform.NOKIA_FLEXILS)
def _(
    optical_node: OpticalNodeBlockUnion,
    optical_spectrum_name: str,
) -> float:
    flex = get_optical_node_client(optical_node)
    """
    procedure:
    >> RTRV-OCRS SIGTYPE=SIGNALED
    >> find by CKTIDSUFFIX
    >> save INTERMEDIATESCHCTP if card is not FSM else source AID
    >> RTRV-SCH  AID=INTERMEDIATESCHCTP
    >> save TARGETOPR
    >> RTRV-OPM-SCH AID=INTERMEDIATESCHCTP RTRV-PM-SCH::1-E1-1-T2A-1:c:::;

    RTRV-OCRS:::c:::;
    flex.bo01 25-10-27 16:45:12
    M  c COMPLD
    "1-E1-1-T2A-1,1-A-1-L1-1:2WAY:LABEL=f099c99,SIGTYPE=SIGNALED,XCT=AddDrop,CKTIDSUFFIX=OCh099_bo01-ba01,CKTID=\"1752248030.MA4621080160.0.1.28.1.3.1:OCh099_bo01-ba01\",SUPCHNUM=SCH-NONE,CHANPLANTYPE=CHPLAN-NONE,FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE,OELAID=bo01-ba01,SCHOFFSET=0,LMSCH=,BAUDRATE=NA,RXSCHOFFSET=0,SERVICESTATEFWD=ENABLED,SERVICESTATEBWD=ENABLED,AUTORETUNELMSCH=DISABLED,MODULATIONCAT=NA,FWDACTSTATUS=ACTIVATED,BWDACTSTATUS=ACTIVATED,LASTDEACTREASONFWD=NOTAPPLICABLE,LASTDEACTREASONBWD=NOTAPPLICABLE,DLTINPRGRESS=FALSE,FWDASEIDLERSTATUS=NOTAPPLICABLE,BWDASEIDLERSTATUS=NOTAPPLICABLE,PATHSTATE=ACTIVEPATH,PROFSCHNUM=,SCHPROFID=,PGAID=,ROLE=NA,PASSBANDLIST=193450000&193550000,ACTIVEPASSBANDLIST=NULL,CARRIERLIST=193500000&37500,INTERMEDIATESCHCTP=1-A-1-S3-1,INTRACARRSPECSHAPING=ENABLED,FSGALIGNMENT=12.5GHZ:IS-NR"
    ;

    RTRV-SCH::1-A-1-S3-1:c:;
    flex.bo01 25-10-27 16:45:20
    M  c COMPLD
    "1-A-1-S3-1:SCH:LABEL=,SUPCHNUM=SCH-NONE,CHANPLANTYPE=CHPLAN-NONE,FREQSLOTPLANTYPE=FREQ-SLOT-PLAN-NONE,SCHOFFSETOVERPROVISIONED=FALSE,CLIENTSCHCTP=,FWDACTSTATUS=UNKNOWN,BWDACTSTATUS=UNKNOWN,LASTDEACTREASONFWD=NOTAPPLICABLE,LASTDEACTREASONBWD=NOTAPPLICABLE,FWDASEIDLERSTATUS=UNKNOWN,BWDASEIDLERSTATUS=UNKNOWN,TPTYPE=INTERMEDIATE,ROLE=NA,TARGETOPR=-9.1721,MODULATIONCAT=NA,RXSCHPWROFFSET=0,MUXPWRCONTROLLOOP=MANUAL,DEMUXPWRCONTROLLOOP=ENABLED,DEMUXSHUTTERSTATE=CLOSED,OSNRADD=0,OSNRDROP=0,ALIENSCHTHPROFID=DFLT-SCH,PROVPBLIST=193450000&193550000:IS-NR"
    ;

    RTRV-PM-SCH::1-A-1-S3-1:c::OPR,,,,,,::;
    flex.bo01 25-10-27 17:17:37
    M  c COMPLD
    "1-A-1-S3-1,SCH:OPR,-8.81938,,NEND,RCV,,"
    ;
    """
    cktidsuffix = optical_spectrum_name.replace(" ", "_")

    ocrs = flex.rtrv_ocrs(sigtype="SIGNALED")
    ocrs = ocrs.parsed_data
    ocr = next(
        (o for o in ocrs if cktidsuffix in o["CKTIDSUFFIX"]),
        None,
    )

    if ocr is None:
        msg = (
            f"Optical channel with CKTIDSUFFIX={cktidsuffix} not found on {optical_node.pqdn}. "
            "Please ensure the optical channel exists and is correctly configured then retry."
        )
        raise ValueError(msg)

    tributary_port = ocr.get("FROMAID") if "-T" in ocr.get("FROMAID") else ocr.get("TOAID")
    card_aid = tributary_port.split("-")[:-2]
    card_aid = "-".join(card_aid)
    card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]
    sch_aid = tributary_port if card["TYPE"] == "FSM" else ocr.get("INTERMEDIATESCHCTP")

    sch = flex.rtrv_sch(aid=sch_aid)
    sch = sch.parsed_data[0]
    target_opr = float(sch["TARGETOPR"])

    pm_sch = flex.rtrv_pm_sch(aid=sch_aid, montype="OPR")
    pm_sch = pm_sch.parsed_data[0]
    current_rx_power = float(pm_sch["positional_param_1_1"])

    return round(current_rx_power - target_opr, 1)


@attributedispatch("vendor_and_platform")
def allign_tx_power_to_target(
    optical_node: OpticalNodeBlockUnion,
    line_port_name: str,  # noqa: ARG001
    db_from_target: Decimal | float | str,  # noqa: ARG001
) -> dict[str, dict[str, Decimal]]:
    r"""
    Subtract db_from_target decibels (dB) to the transmitted optical power,
      i.e. $P^{new}_{tx} = P^{old}_{tx} - \Delta P}$.

    Args:
        optical_node: The optical device to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.

    Returns:
        A dictionary indicating the old and new required transmit power.
    """
    return attribute_dispatch_base(allign_tx_power_to_target, "vendor_and_platform", optical_node.vendor_and_platform)


@allign_tx_power_to_target.register(VendorAndPlatform.NOKIA_GROOVE_G30)
def _(
    optical_node: OpticalNodeBlockUnion,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, dict[str, Decimal]]:
    if isinstance(db_from_target, float):
        db_from_target = str(db_from_target)
    if isinstance(db_from_target, str):
        db_from_target = Decimal(db_from_target)
    if not isinstance(db_from_target, Decimal):
        raise TypeError("db_from_target must be of type Decimal at this point.")

    min_tx_power = Decimal("-10.00")
    max_tx_power = Decimal("6.00")

    g30 = get_optical_node_client(optical_node)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(line_port_name)
    och_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os
    och_os = och_uri.retrieve(content="config", depth=2)
    current_tx_power = och_os.required_tx_optical_power
    new_tx_power = current_tx_power - db_from_target
    new_tx_power = min(max_tx_power, new_tx_power)
    new_tx_power = max(min_tx_power, new_tx_power)
    new_och_os = och_os.model_copy(deep=True)
    new_och_os.required_tx_optical_power = new_tx_power
    och_uri.update(new_och_os)

    return compare_pydantic_objects(och_os, new_och_os)


@allign_tx_power_to_target.register(VendorAndPlatform.NOKIA_GX_G42)
def _(
    optical_node: OpticalNodeBlockUnion,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, dict[str, Decimal]]:
    if isinstance(db_from_target, float):
        db_from_target = str(db_from_target)
    if isinstance(db_from_target, str):
        db_from_target = Decimal(db_from_target)
    if not isinstance(db_from_target, Decimal):
        raise TypeError("db_from_target must be of type Decimal at this point.")

    min_tx_power = Decimal("-6.00")
    max_tx_power = Decimal("9.00")

    g42 = get_optical_node_client(optical_node)
    uri = g42.data.ne.facilities.optical_carrier(f"{line_port_name}-1")
    conf = uri.retrieve(depth=2, content="config")
    current_tx_power = conf.tx_power
    new_tx_power = round(current_tx_power - db_from_target, 2)
    new_tx_power = min(max_tx_power, new_tx_power)
    new_tx_power = max(min_tx_power, new_tx_power)
    new_conf = conf.model_copy(deep=True)
    new_conf.tx_power = new_tx_power
    uri.update(new_conf)
    return compare_pydantic_objects(conf, new_conf)
