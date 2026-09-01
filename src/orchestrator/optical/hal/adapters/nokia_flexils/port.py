"""Port-area operations for the Nokia FlexILS device adapter."""

import json
from typing import Any, Literal, cast

from orchestrator.optical.hal._common import _as_flexils_block, _extract_remote_port_id, _node_id, _port_name
from orchestrator.optical.hal.adapters.nokia_flexils._shared import (
    _get_remote_node_id,
    get_flex_client,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import AbstractOpticalPortBlockInactive
from orchestrator.optical.services.nokia import TL1CommandDeniedError


def _scg_aids(flex: Any) -> list[str]:
    """Return the SCG AIDs of a FlexILS node, tolerating nodes without SCGs."""
    try:
        return [str(x["AID"]) for x in flex.rtrv_scg().parsed_data]
    except TL1CommandDeniedError as e:
        if "INPUT, SPECIFIED OBJECT ENTITY DOES NOT EXIST" not in e.response:
            raise
        return []


def get_device_ports_names(optical_node_block: NokiaFlexIlsBlockInactive) -> list[str]:
    """Return the SCG and OTS AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    scg_aids = _scg_aids(flex)
    ots_aids = [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]
    return scg_aids + ots_aids


def get_device_client_ports_names(optical_node_block: NokiaFlexIlsBlockInactive) -> list[str]:
    """Return the SCG AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    return _scg_aids(flex)


def get_device_line_ports_names(optical_node_block: NokiaFlexIlsBlockInactive) -> list[str]:
    """Return the OTS AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    return [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]


def set_port_description(
    port_block: AbstractOpticalPortBlockInactive,
    port_description: str,
) -> dict[str, Any]:
    """Set the description of an optical port.

    Args:
        port_block: Optical Port of which the description is to be set.
        port_description: The description to set on the port.

    Returns:
        The port configuration after the update.

    Raises:
        ValueError: In case the configuration failed.
    """
    host_node = port_block.optical_port_host_node
    port_name = _port_name(port_block)
    flex = cast(Any, get_flex_client(_as_flexils_block(host_node)))  # TL1 methods are bound dynamically
    if "L" in port_name:
        flex.ed_ots(aid=port_name, label=rf'"{port_description}"')
        return flex.rtrv_ots(aid=port_name).model_dump()
    flex.ed_scg(aid=port_name, label=rf'"{port_description}"')
    return flex.rtrv_scg(aid=port_name).model_dump()


def set_port_admin_state(
    optical_port_block: AbstractOpticalPortBlockInactive,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Set the administrative state of a Nokia FlexILS port.

    FlexILS has 3 admin states for the tributary ports: IS (in service), OOS (out of
    service), and MT (maintenance). Line ports (OTS) can only be in IS or MT state.
    It works as a finite state machine with the following transitions:
    OOS <-edit---edit-> IS <-rst---put-> MT.
    """
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)

    # Line ports (OTS)
    if "L" in port_name:
        if admin_state == "down":
            msg = "Line ports (OTS) can only be in service (IS) or maintenance (MT) state"
            raise ValueError(msg)
        if admin_state == "maintenance":
            flex.put_maintenance(aidtype="OTS", aid=port_name)
        elif admin_state == "up":
            flex.rst_maintenance(aidtype="OTS", aid=port_name)
        return flex.rtrv_ots(aid=port_name).model_dump()

    # Tributary ports (SCG)
    # from any state to in-service state (we must know the current state of the
    # finite state machine to move between states)
    try:
        flex.ed_scg(aid=port_name, is_oos="IS")
    except TL1CommandDeniedError as e:
        if "use RST command" not in e.response:
            raise
        flex.rst_maintenance(aidtype="SCG", aid=port_name)
    # from in-service state to desired state
    if admin_state == "up":
        pass
    elif admin_state == "down":
        flex.ed_scg(aid=port_name, is_oos="OOS")
    elif admin_state == "maintenance":
        flex.put_maintenance(aidtype="SCG", aid=port_name)

    return flex.rtrv_scg(aid=port_name).model_dump()


def _ensure_manualmode2(optical_port_block: AbstractOpticalPortBlockInactive) -> None:
    """Ensure the given FlexILS SCG port is in MANUALMODE-2, setting it there if needed.

    Args:
        optical_port_block: Optical Port of the FlexILS SCG port to check and configure.

    Raises:
        ValueError: In case the configuration failed.
    """
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    scg = flex.rtrv_scg(aid=port_name).parsed_data[0]

    if scg["INTFTYP"] != "MANUALMODE-2":
        card_aid = port_name.split("-")[:-1]
        card_aid = "-".join(card_aid)
        card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]

        if card["TYPE"] in ["FSM", "FRM"]:
            # tributary ports of FSM and system ports of FRM cards can only be unlocked or locked
            set_port_admin_state(optical_port_block, "down")
        else:
            set_port_admin_state(optical_port_block, "maintenance")

        flex.ed_scg(aid=port_name, intftyp="MANUALMODE-2")

    set_port_admin_state(optical_port_block, "up")


def configure_termination(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Configure a Nokia FlexILS port when attaching a fiber to it."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    description = optical_port_block.optical_port_description or ""

    # Handle FlexILS-to-FlexILS connection separately (simpler case)
    if (
        remote_port_block.optical_port_host_node.management.optical_module_node_vendor,
        remote_port_block.optical_port_host_node.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS):
        flex.ed_ots(aid=port_name, label=rf'"{description}"')
        flex.rst_maintenance(aidtype="OTS", aid=port_name)
        return flex.rtrv_ots(aid=port_name).model_dump()

    # Handle FlexILS connections to other platform types
    _ensure_manualmode2(optical_port_block)

    remote_node_id = _get_remote_node_id(remote_port_block)
    remote_port_id = _extract_remote_port_id(_port_name(remote_port_block))
    provowremptp = f"{remote_node_id}/{remote_port_id}"
    flex.ed_scg(
        aid=port_name,
        provowremptp=provowremptp,
        label=rf'"{description}"',
    )

    return flex.rtrv_scg(aid=port_name).model_dump()


def factory_reset(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> dict[str, Any]:
    """Prune the configuration of a Nokia FlexILS port."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)

    if (
        remote_port_block.optical_port_host_node.management.optical_module_node_vendor,
        remote_port_block.optical_port_host_node.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS):
        flex.ed_ots(aid=port_name, label=r'""')
        return flex.rtrv_ots(aid=port_name).model_dump()

    set_port_admin_state(optical_port_block, "maintenance")
    flex.ed_scg(
        aid=port_name,
        intftyp="MANUALMODE-2",
        provowremptp=r'""',
        label=r'""',
    )
    set_port_admin_state(optical_port_block, "down")
    return flex.rtrv_scg(aid=port_name).model_dump()


def check_fiber(
    optical_port_block: AbstractOpticalPortBlockInactive,
    remote_port_block: AbstractOpticalPortBlockInactive,
) -> None:
    """Check if a Nokia FlexILS port attached to a fiber is correctly configured."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    remote_port_name = _port_name(remote_port_block)
    description = optical_port_block.optical_port_description or ""

    # Handle FlexILS-to-FlexILS connection separately (simpler case)
    if (
        remote_port_block.optical_port_host_node.management.optical_module_node_vendor,
        remote_port_block.optical_port_host_node.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS):
        ots = flex.rtrv_ots(aid=port_name).parsed_data[0]
        checks = (
            description in ots["LABEL"]
            and "IS" in ots["OPERSTATE"]
            and remote_port_name in ots["PROVNBROTS"]
            and ots["PROVNBROTS"] == ots["DISCNBROTS"]
            and ots["HISTSTATS"] == "ENABLED"
        )
        if not checks:
            raise ValueError(
                json.dumps(
                    {
                        "optical_device": _node_id(optical_port_block.optical_port_host_node),
                        "port_name": port_name,
                        "expected": {
                            "label": description,
                            "operstate": "IS",
                            "provnbrots": remote_port_name,
                            "discnbrots": remote_port_name,
                            "histstats": "ENABLED",
                        },
                        "actual": {
                            "label": ots["LABEL"],
                            "operstate": ots["OPERSTATE"],
                            "provnbrots": ots["PROVNBROTS"],
                            "discnbrots": ots["DISCNBROTS"],
                            "histstats": ots["HISTSTATS"],
                        },
                    },
                    indent=4,
                )
            )
        return

    # Handle FlexILS connections to other platform types
    remote_node_id = _get_remote_node_id(remote_port_block)
    remote_port_id = _extract_remote_port_id(remote_port_name)
    provowremptp = f"{remote_node_id}/{remote_port_id}"

    scg = flex.rtrv_scg(aid=port_name).parsed_data[0]

    checks = (
        scg["INTFTYP"] == "MANUALMODE-2"
        and scg["PROVOWREMPTP"] == provowremptp
        and description in scg["LABEL"]
        and "IS" in scg["OPERSTATE"]
        and scg["HISTSTATS"] == "ENABLED"
    )
    if not checks:
        raise ValueError(
            json.dumps(
                {
                    "optical_device": _node_id(optical_port_block.optical_port_host_node),
                    "port_name": port_name,
                    "expected": {
                        "intftyp": "MANUALMODE-2",
                        "provowremptp": provowremptp,
                        "label": description,
                        "operstate": "IS",
                        "histstats": "ENABLED",
                    },
                    "actual": {
                        "intftyp": scg["INTFTYP"],
                        "provowremptp": scg["PROVOWREMPTP"],
                        "label": scg["LABEL"],
                        "operstate": scg["OPERSTATE"],
                        "histstats": scg["HISTSTATS"],
                    },
                },
                indent=4,
            )
        )
