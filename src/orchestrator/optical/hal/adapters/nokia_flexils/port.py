"""Port-area operations for the Nokia FlexILS device adapter."""

import json
from typing import Any, Literal, cast

from orchestrator.optical.hal._common import (
    UnsupportedPortRoleError,
    _as_flexils_block,
    _extract_remote_port_id,
    _node_id,
    _port_name,
    _ports_by_role,
)
from orchestrator.optical.hal.adapters.nokia_flexils._shared import (
    _get_remote_node_id,
    get_flex_client,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import OpticalPipeType
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning
from orchestrator.optical.services.nokia import TL1CommandDeniedError

#: Port roles a Nokia FlexILS node can enumerate: OTS line ports and SCG add/drop (tributary) ports.
_FLEXILS_SUPPORTED_ROLES = frozenset({OpticalPortRole.OLS_LINE, OpticalPortRole.OLS_ADD_DROP})


def _scg_aids(flex: Any) -> list[str]:
    """Return the SCG AIDs of a FlexILS node, tolerating nodes without SCGs."""
    try:
        return [str(x["AID"]) for x in flex.rtrv_scg().parsed_data]
    except TL1CommandDeniedError as e:
        if "INPUT, SPECIFIED OBJECT ENTITY DOES NOT EXIST" not in e.response:
            raise
        return []


def get_device_ports_names(optical_node_block: NokiaFlexIlsBlockProvisioning) -> list[str]:
    """Return the SCG and OTS AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    scg_aids = _scg_aids(flex)
    ots_aids = [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]
    return scg_aids + ots_aids


def get_device_client_ports_names(optical_node_block: NokiaFlexIlsBlockProvisioning) -> list[str]:
    """Return the SCG AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    return _scg_aids(flex)


def get_device_line_ports_names(optical_node_block: NokiaFlexIlsBlockProvisioning) -> list[str]:
    """Return the OTS AIDs of a Nokia FlexILS node."""
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically
    return [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]


def get_device_ports_by_role(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    roles: list[OpticalPortRole] | None = None,
) -> list[str]:
    """Return the device port names of a Nokia FlexILS node for the requested Optical Port roles.

    A FlexILS node exposes OLS line ports (OTS AIDs) and OLS add/drop tributary ports (SCG AIDs);
    it cannot enumerate transponder or coherent pluggable ports.
    """
    flex = cast(Any, get_flex_client(optical_node_block))  # the TL1 command methods are bound dynamically

    def port_names_for_role(role: OpticalPortRole) -> list[str]:
        if role is OpticalPortRole.OLS_LINE:
            return [str(x["AID"]) for x in flex.rtrv_ots().parsed_data]
        if role is OpticalPortRole.OLS_ADD_DROP:
            return _scg_aids(flex)
        msg = f"Nokia FlexILS does not support port role {role.value}"
        raise UnsupportedPortRoleError(msg)

    return _ports_by_role(_FLEXILS_SUPPORTED_ROLES, port_names_for_role, roles)


def set_port_description(
    port_block: AnyOpticalPortBlockProvisioning,
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
    optical_port_block: AnyOpticalPortBlockProvisioning,
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


def _ensure_manualmode2(optical_port_block: AnyOpticalPortBlockProvisioning) -> None:
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
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
    pipe_type: OpticalPipeType,
) -> dict[str, Any]:
    """Configure a Nokia FlexILS port when attaching a fiber to it.

    The OTS-vs-SCG path is decided by the local port role and the pipe type: an
    OLS line port carries a fiber span (OTS), while an OLS add/drop (tributary)
    port carries a fiber patch or a leased spectrum (SCG). Branching on the
    remote platform, as the legacy code did, misconfigured the cross-role cases
    (e.g. a FlexILS<->FlexILS client patch).
    """
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    description = optical_port_block.optical_port_description or ""

    match (optical_port_block.optical_port_role, pipe_type):
        case (OpticalPortRole.OLS_LINE, OpticalPipeType.SPAN):
            flex.ed_ots(aid=port_name, label=rf'"{description}"')
            flex.rst_maintenance(aidtype="OTS", aid=port_name)
            return flex.rtrv_ots(aid=port_name).model_dump()
        case (OpticalPortRole.OLS_ADD_DROP, OpticalPipeType.PATCH | OpticalPipeType.LEASED_SPECTRUM):
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
        case _:
            msg = (
                f"Unsupported Nokia FlexILS termination for port role "
                f"{optical_port_block.optical_port_role.value} and pipe type {pipe_type.value}"
            )
            raise ValueError(msg)


def factory_reset(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,  # noqa: ARG001
    pipe_type: OpticalPipeType,
) -> dict[str, Any]:
    """Prune the configuration of a Nokia FlexILS port.

    The OTS-vs-SCG path is decided by the local port role and the pipe type, as
    in :func:`configure_termination`; the remote port is not needed to prune a
    port (the SCG remote-tributary reference is simply cleared).
    """
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)

    match (optical_port_block.optical_port_role, pipe_type):
        case (OpticalPortRole.OLS_LINE, OpticalPipeType.SPAN):
            flex.ed_ots(aid=port_name, label=r'""')
            return flex.rtrv_ots(aid=port_name).model_dump()
        case (OpticalPortRole.OLS_ADD_DROP, OpticalPipeType.PATCH | OpticalPipeType.LEASED_SPECTRUM):
            set_port_admin_state(optical_port_block, "maintenance")
            flex.ed_scg(
                aid=port_name,
                intftyp="MANUALMODE-2",
                provowremptp=r'""',
                label=r'""',
            )
            set_port_admin_state(optical_port_block, "down")
            return flex.rtrv_scg(aid=port_name).model_dump()
        case _:
            msg = (
                f"Unsupported Nokia FlexILS factory reset for port role "
                f"{optical_port_block.optical_port_role.value} and pipe type {pipe_type.value}"
            )
            raise ValueError(msg)


def check_fiber(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
    pipe_type: OpticalPipeType,
) -> None:
    """Check if a Nokia FlexILS port attached to a fiber is correctly configured."""
    flex = cast(Any, get_flex_client(_as_flexils_block(optical_port_block.optical_port_host_node)))
    port_name = _port_name(optical_port_block)
    remote_port_name = _port_name(remote_port_block)
    description = optical_port_block.optical_port_description or ""

    match (optical_port_block.optical_port_role, pipe_type):
        case (OpticalPortRole.OLS_LINE, OpticalPipeType.SPAN):
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
        case (OpticalPortRole.OLS_ADD_DROP, OpticalPipeType.PATCH | OpticalPipeType.LEASED_SPECTRUM):
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
            return
        case _:
            msg = (
                f"Unsupported Nokia FlexILS fiber check for port role "
                f"{optical_port_block.optical_port_role.value} and pipe type {pipe_type.value}"
            )
            raise ValueError(msg)
