"""Node-area operations for the Nokia FlexILS device adapter."""

from typing import Any, cast

from orchestrator.optical.hal.adapters.nokia_flexils._shared import (
    _record_value,
    _retrieve_node_properties,
    discover_flexils_node,
    get_flex_client,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.utils.custom_types.frequencies import available_to_used_passbands


def role_and_version(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
) -> tuple[OpticalNodeRole, str]:
    """Retrieve the node role and software version of a Nokia FlexILS node from the device.

    Args:
        optical_node_block: The Nokia FlexILS node block.

    Returns:
        A tuple of the node role and the software version.

    Raises:
        ValueError: If the node has no Target ID or cannot be reached.
    """
    target_id = optical_node_block.optical_flexils_target_id
    if target_id is None:
        msg = "Cannot retrieve the node role and software version: the FlexILS node has no Target ID"
        raise ValueError(msg)
    return discover_flexils_node(
        optical_flexils_target_id=target_id,
        optical_management_ip=optical_node_block.management.optical_module_node_dcn_interface_ip,
        optical_loopback_ip=optical_node_block.management.optical_module_node_dcn_loopback_ip,
        optical_flexils_gmpls_id=optical_node_block.optical_flexils_gmpls_id,
        location=optical_node_block.location,
    )


def role(node: NokiaFlexIlsBlockProvisioning) -> OpticalNodeRole:
    """Retrieve the node role of a Nokia FlexILS node from the device.

    Args:
        node: The Nokia FlexILS node block.

    Returns:
        The OpticalNodeRole of the node.

    Raises:
        ValueError: If the node has no Target ID or cannot be reached.
    """
    flex = cast(Any, get_flex_client(node))
    target_id = node.optical_flexils_target_id
    if target_id is None:
        msg = "Cannot retrieve the node role: the FlexILS node has no Target ID"
        raise ValueError(msg)
    role, _ = _retrieve_node_properties(flex, target_id)
    return role


def software_version(node: NokiaFlexIlsBlockProvisioning) -> str:
    """Retrieve the software version of a Nokia FlexILS node from the device.

    Args:
        node: The Nokia FlexILS node block.

    Returns:
        The software version of the node.

    Raises:
        ValueError: If the node has no Target ID or cannot be reached.
    """
    flex = cast(Any, get_flex_client(node))
    target_id = node.optical_flexils_target_id
    if target_id is None:
        msg = "Cannot retrieve the software version: the FlexILS node has no Target ID"
        raise ValueError(msg)
    _, version = _retrieve_node_properties(flex, target_id)
    return version


def retrieve_omses(optical_node_block: NokiaFlexIlsBlockProvisioning) -> list[dict[str, Any]]:
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


def retrieve_ports_spectral_occupations(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
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
