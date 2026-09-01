"""Nokia Groove G30 transponder operations: bandwidth, client/line config, cross-connects and validation."""

from decimal import Decimal
from re import search
from typing import Any

from requests.exceptions import HTTPError

from orchestrator.optical.hal._common import OpticalNodeBlock, _as_decimal, _node_id
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (
    g30_ids_from_port_name,
    g30_port_navigator_node_from_port_name,
    get_g30_client,
)
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.utils.datadiff import compare_dicts, compare_pydantic_objects


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


def get_signal_bandwidth(optical_node_block: OpticalNodeBlock, port_name: str) -> int:
    """Return the signal bandwidth, in MHz, of the Groove G30 transport channel on the given line port.

    Args:
        optical_node_block: The Groove G30 Optical Node hosting the line port.
        port_name: The line port name.

    Returns:
        The signal bandwidth in MHz.
    """
    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
    och_os = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os.retrieve(depth=2, content="config")
    if och_os.fec_type == "SDFEC27ND":
        bw = 75_000
    elif och_os.fec_type == "SDFEC15ND2":
        bw = 68_750
    else:
        bw = 37_500
    return bw


def configure_line_transceivers(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> dict[str, Any]:
    """Configure the line transceivers on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Returns:
        A dictionary of configuration diffs, keyed by port/facility name.
    """
    g30 = get_g30_client(optical_node_block)
    configurations = {}
    for port_name, central_frequency, mode, description in zip(
        port_names,
        central_frequencies,
        modes,
        descriptions,
        strict=True,
    ):
        shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
        uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)
        before = uri.retrieve(depth=3, content="config")
        uri.update(
            port_id=port_id,
            port_mode=mode,
            service_label=description,
            admin_status="up",
        )
        modulation, rate = _get_modulation_and_rate_from_mode(mode)
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


def configure_transceiver_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> dict[str, Any]:
    """Configure the client port of a transceiver on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Returns:
        A dictionary of configuration diffs, keyed by facility name.
    """
    navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node_block, port_name)
    port_mode, eth_name, fec_type = _client_speed_config(speed)
    eth = getattr(navigator, eth_name)

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


def configure_transponder_crossconnect(  # noqa: PLR0912, PLR0915
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    """Configure a cross-connect between client and line ports on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to configure.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).
        line_port_names: List of line port names.
        xconn_description: Optional description for the cross-connect.

    Returns:
        The created cross-connect configuration.

    Raises:
        ValueError: If the cross-connect cannot be created.
    """
    g30 = get_g30_client(optical_node_block)
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
        msg = f"No eth service found on {_node_id(optical_node_block)} {client_port_name}"
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
                    if getattr(och_os, f, None) is not None
                ),
                None,
            )
            if otu_key is None:
                msg = f"No OTU service found for line port {line_port_id} on {_node_id(optical_node_block)}"
                raise ValueError(msg)
            for odu in getattr(och_os, otu_key).odu:
                key_list = [
                    "odutype_L1",
                    "oduid_L1",
                    "odutype_L2",
                    "oduid_L2",
                    "odutype_L3",
                    "oduid_L3",
                    "odutype_L4",
                    "oduid_L4",
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
            msg = f"No available ODU for crossconnect on {_node_id(optical_node_block)}"
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


def delete_transponder_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
) -> dict[str, Any]:
    """Delete a cross-connect between client and line ports on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node (transponder) to configure.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).

    Returns:
        A dictionary with a ``"message"`` and the list of deleted cross-connects.

    Raises:
        ValueError: If the client port has no ethernet service.
    """
    result = {"message": "", "deleted_xcon": []}

    g30 = get_g30_client(optical_node_block)

    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(client_port_name)

    uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card

    card = uri.retrieve(depth=2)
    if card.required_type == "CHM1":
        result["message"] = (
            f"{_node_id(optical_node_block)} {client_port_name}: no need to delete any xcon,"
            " CHM1 crossconnections are not configurable."
        )
        return result

    client_port = uri.port(port_id).retrieve(depth=3, content="config")
    eth_key = next((f for f in ("eth100g", "eth400g") if getattr(client_port, f, None) is not None), None)
    if not eth_key:
        msg = (
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " This port does not have an ethernet service, it must have been deleted manually."
        )
        raise ValueError(msg)

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
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " There was no cross-connection associated to this client port in the configuration."
        )
        return result

    result["deleted_xcon"] = deleted_crs
    return result


def factory_reset_transponder_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
) -> dict[str, Any]:
    """Factory reset the client port configuration of the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to reset.
        port_name: The client port name.

    Returns:
        The reset configuration.
    """
    navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node_block, port_name)
    before = navigator.retrieve(depth=3, content="config")
    navigator.update(
        port_id=port_id,
        admin_status="down",
        service_label="",
        port_mode="not-applicable",
    )
    after = navigator.retrieve(depth=3, content="config")
    return compare_pydantic_objects(before, after)


def factory_reset_transponder_lines(
    optical_node_block: OpticalNodeBlock,
    line_port_names: list[str],
) -> list[Any]:
    """Factory reset the transponder line configuration of the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to reset.
        line_port_names: The line port names.

    Returns:
        The reset configuration.
    """
    result = []
    for port_name in line_port_names:
        navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node_block, port_name)
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


def validate_trx_line(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    """Validate the transceiver line configuration on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Raises:
        ValueError: If the configuration is invalid.
    """
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)

    if len(set(modes)) != 1:
        msg = f"All modes must be the same but got {modes}."
        raise ValueError(msg)

    g30 = get_g30_client(optical_node_block)

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
                f"Configuration mismatch for {_node_id(optical_node_block)} {port_name}:\n"
                f"mismatch: {diff['mismatched_value']}\n"
                f"missing: {diff['missing_key']}\n"
            )
            raise ValueError(msg)


def validate_trx_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> None:
    """Validate the transceiver client configuration on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Raises:
        ValueError: If the configuration is invalid.
    """
    g30 = get_g30_client(optical_node_block)

    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)

    port_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    port_mode, eth_name, fec_type = _client_speed_config(speed)

    actual_config = port_uri.retrieve(depth=3, content="config").model_dump(exclude_unset=True)

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
            f"Configuration mismatch for {_node_id(optical_node_block)} {port_name}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def validate_trx_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    """Validate the transponder cross-connect configuration on the given Groove G30 node.

    Args:
        optical_node_block: The Optical Node to validate.
        client_port_name: The client port name.
        line_port_names: The line port names.
        xconn_description: The description of the cross-connect.

    Raises:
        ValueError: If the cross-connect is missing or its description does not match.
    """
    g30 = get_g30_client(optical_node_block)
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
                    f"Cross-connect description mismatch for {_node_id(optical_node_block)} "
                    f"{client_port_name} to {dst_port_string}: "
                    f"Expected: {xconn_description}, Actual: {c.service_label}"
                )
                raise ValueError(msg)
            return

    msg = (
        f"Cross-connect not found for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}. "
        "Please ensure the cross-connect exists and is correctly configured then retry."
    )
    raise ValueError(msg)


def align_tx_power_to_target(
    optical_node_block: OpticalNodeBlock,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, Any]:
    r"""Subtract db_from_target decibels (dB) to the transmitted optical power.

    I.e. :math:`P^{new}_{tx} = P^{old}_{tx} - \Delta P`, where :math:`P^{old}_{tx}`
    is the currently configured required transmit power (``required-tx-optical-power``
    on G30), used as the baseline for the adjustment.

    Args:
        optical_node_block: The Optical Node to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.

    Returns:
        A dictionary indicating the old and new required transmit power.

    Raises:
        ValueError: If no required transmit power is configured.
    """
    db_from_target = _as_decimal(db_from_target)

    min_tx_power = Decimal("-10.00")
    max_tx_power = Decimal("6.00")

    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(line_port_name)
    och_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os
    och_os = och_uri.retrieve(content="config", depth=2)
    current_tx_power = och_os.required_tx_optical_power
    if current_tx_power is None:
        msg = f"No required transmit power configured on {_node_id(optical_node_block)} {line_port_name}"
        raise ValueError(msg)
    new_tx_power = current_tx_power - db_from_target
    new_tx_power = min(max_tx_power, new_tx_power)
    new_tx_power = max(min_tx_power, new_tx_power)
    new_och_os = och_os.model_copy(deep=True)
    new_och_os.required_tx_optical_power = new_tx_power
    och_uri.update(new_och_os)

    return compare_pydantic_objects(och_os, new_och_os)
