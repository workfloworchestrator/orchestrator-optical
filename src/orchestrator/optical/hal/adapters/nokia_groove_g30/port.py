"""Nokia Groove G30 port operations: discovery, description, admin state, termination and checks.

The configuration is declarative (see :mod:`orchestrator.optical.hal.reconcile`): it is
rendered, then applied, verified or released. It is owned by the Optical Port block.
"""

import re
from decimal import Decimal
from typing import Any, Literal

from orchestrator.optical.hal._common import (
    _node_id,
    _port_name,
    _ports_by_role,
    _retrieve_required,
    _same_node,
)
from orchestrator.optical.hal.adapters.nokia_groove_g30._sdk import (
    CardTypeEnum,
    GainRangeTypeEnum,
)
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (
    G30_MAX_SLOT_ID,
    G30Function,
    G30Module,
    g30_ids_from_port_name,
    g30_modules,
    g30_och_os_node,
    g30_ots_id,
    g30_port_node,
    get_g30_client,
)
from orchestrator.optical.hal.adapters.nokia_groove_g30.transponder import _get_modulation_and_rate_from_mode
from orchestrator.optical.hal.reconcile import Fragment, apply_config, fragment, release_config, verify_config
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning

#: Subslot of the OCC2 card holding the booster of an amplifier card; the
#: preamplifier lives in the amplifier port's own subslot. A Groove G30 amplifier card
#: exposes its two amplifiers in fixed subslots of the carrier.
_BOOSTER_SUBSLOT_ID = 2

#: Port roles a Groove G30 node can enumerate. The role of each physical port is
#: determined from the device, from the functions of the card or subcard hosting it (see
#: :mod:`orchestrator.optical.hal.adapters.nokia_groove_g30._shared`): every card that is
#: not a pure transponder is an Open Line System element -- an OCC2 carrier, an amplifier,
#: an add/drop, a mux/demux, a wavelength selector or a mix -- and exposes OLS line ports
#: when an OTS with the same id exists and OLS add/drop ports otherwise, while a
#: transponder exposes transponder line ports (card ports 1 and 2) or transponder client
#: ports (every other port, subports included).
_G30_SUPPORTED_ROLES = frozenset(
    {
        OpticalPortRole.OLS_LINE,
        OpticalPortRole.OLS_ADD_DROP,
        OpticalPortRole.TRANSPONDER_LINE,
        OpticalPortRole.TRANSPONDER_CLIENT,
    }
)


def _g30_port_role(
    *,
    module: G30Module,
    is_card_port: bool,
    port_id: int,
    port_name: str,
) -> OpticalPortRole:
    """Return the Optical Port role of a Groove G30 port from the functions of its module.

    A module belongs to the Open Line System unless the transponder is the only function
    it provides: an OCC2 carrier, an amplifier, an add/drop and a wavelength selector are
    all OLS elements, and a single card often mixes several of them. One card can expose
    both line and add/drop ports -- a WSS terminates the line on one port and drops on the
    others -- so the OTS, not the card, decides: a port carrying an OTS id is the line
    side, a port without one is an add/drop port. A transponder is the remaining case:
    its card ports 1 and 2 are the line side, every other port and subport is a client
    port.
    """
    is_transponder_only = module.functions <= frozenset({G30Function.TRANSPONDER})
    if module.is_occ2 or not is_transponder_only:
        return OpticalPortRole.OLS_LINE if g30_ots_id(port_name) in module.ots_ids else OpticalPortRole.OLS_ADD_DROP
    if is_card_port and port_id in (1, 2):
        return OpticalPortRole.TRANSPONDER_LINE
    return OpticalPortRole.TRANSPONDER_CLIENT


def _g30_port_roles(optical_node_block: NokiaGrooveG30BlockProvisioning) -> dict[str, OpticalPortRole]:
    """Return the role of every port of a Groove G30 node, keyed by the device port name."""
    g30 = get_g30_client(optical_node_block)
    shelves = g30.data.ne_ne.shelf.retrieve(depth=8, content="config")

    modules_by_id = {(module.slot_id, module.subslot_id): module for module in g30_modules(optical_node_block)}

    port_roles: dict[str, OpticalPortRole] = {}
    for shelf in shelves or []:
        for slot in shelf.slot or []:
            if slot.slot_id > G30_MAX_SLOT_ID or not slot.card:
                continue
            card_module = modules_by_id[(slot.slot_id, None)]

            for port in slot.card.port or []:
                if port.alias_name is not None:
                    port_roles[port.alias_name] = _g30_port_role(
                        module=card_module,
                        is_card_port=True,
                        port_id=port.port_id,
                        port_name=port.alias_name,
                    )

            for subslot in slot.card.subslot or []:
                if not subslot.subcard:
                    continue
                subcard_module = modules_by_id.get((slot.slot_id, subslot.subslot_id), card_module)
                for port in subslot.subcard.port or []:
                    if port.alias_name is not None:
                        port_roles[port.alias_name] = _g30_port_role(
                            module=subcard_module,
                            is_card_port=False,
                            port_id=port.port_id,
                            port_name=port.alias_name,
                        )
                    for subport in port.subport or []:
                        if subport.alias_name is not None:
                            port_roles[subport.alias_name] = _g30_port_role(
                                module=subcard_module,
                                is_card_port=False,
                                port_id=subport.subport_id,
                                port_name=subport.alias_name,
                            )

    return port_roles


def get_device_ports_by_role(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    roles: list[OpticalPortRole] | None = None,
) -> list[str]:
    """Return the device port names of a Groove G30 node for the requested Optical Port roles.

    Each physical port has exactly one role, determined from the device (see
    :func:`_g30_port_roles`): OCC2 card ports are OLS line ports when an OTS with the
    same id exists and OLS add/drop ports otherwise, while every other card exposes
    transponder line ports (card ports 1 and 2) or transponder client ports.
    """
    port_roles = _g30_port_roles(optical_node_block)

    def port_names_for_role(role: OpticalPortRole) -> list[str]:
        return [name for name, port_role in port_roles.items() if port_role is role]

    return _ports_by_role(_G30_SUPPORTED_ROLES, port_names_for_role, roles)


def retrieve_transceiver_modes(optical_node_block: NokiaGrooveG30BlockProvisioning, port_name: str) -> list[str]:
    """Return the supported transceiver modes of a Groove G30 line port."""
    # fmt: off
    mapping = {
        CardTypeEnum.CHM1: [
            "not-applicable",      "QPSK_100G",          "16QAM_200G",          "8QAM_300G",
        ],
        CardTypeEnum.CHM2T: [
            "16QAM_200G",           "16QAM_300G",           "16QAM_32QAM_400G",     "16QAM_32QAM_500G",
            "16QAM_400G",           "32QAM_200G",           "32QAM_300G",           "32QAM_400G",
            "32QAM_500G",           "32QAM_64QAM_500G",     "32QAM_64QAM_600G",     "64QAM_300G",
            "64QAM_400G",           "64QAM_500G",           "64QAM_600G",           "QPSK_100G",
            "QPSK_200G",            "QPSK_SP16QAM_200G",    "QPSK_SP16QAM_300G",    "SP16QAM_16QAM_200G",
            "SP16QAM_16QAM_300G",   "SP16QAM_16QAM_400G",   "SP16QAM_200G",         "SP16QAM_300G",
            "SPQPSK_100G",          "SPQPSK_QPSK_100G",     "SPQPSK_QPSK_200G",     "not-applicable",
            "SP16QAM_300G_C",       "QPSK_SP16QAM_300G_C",  "16QAM_32QAM_500G_C",   "16QAM_500G_C",
            "SP16QAM_500G_C",       "QPSK_SP16QAM_500G_C",  "32QAM_64QAM_700G_C",   "16QAM_700G_C",
            "SP16QAM_16QAM_700G_C", "32QAM_900G_C",         "16QAM_32QAM_900G_C",   "32QAM_64QAM_1100G_C",
        ],
    }
    # fmt: on

    shelf_id, slot_id, _, _, _ = g30_ids_from_port_name(port_name)

    g30 = get_g30_client(optical_node_block)

    card = _retrieve_required(g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.retrieve, depth=2)

    card_type = card.required_type

    supported_modes = mapping.get(card_type)

    if not supported_modes:
        msg = f"Card {card_type} not supported"
        raise ValueError(msg)

    return supported_modes


#: Rendering units of the port configuration owned by an Optical Port block.
DESCRIPTION_SCOPE = "description"
ADMIN_STATE_SCOPE = "admin-state"
TERMINATION_SCOPE = "termination"
CHANNEL_DESCRIPTION_SCOPE = "channel-description:{}"

_ADMIN_STATUS = {"up": "up", "down": "down", "maintenance": "up-no-alm"}


def _host_and_root(port_block: AnyOpticalPortBlockProvisioning) -> tuple[Any, Any, Any]:
    """Return the host node of a port block, the data root of its client and the port navigator."""
    host_node = port_block.optical_port_host_node
    root = get_g30_client(host_node).data
    return host_node, root, g30_port_node(root, _port_name(port_block))


def set_port_description(
    port_block: AnyOpticalPortBlockProvisioning,
    port_description: str,
) -> dict[str, Any]:
    """Make a Groove G30 optical port carry the given description; return the applied diff."""
    host_node, _, port = _host_and_root(port_block)
    fragments = [fragment(port, service_label=port_description)]
    return apply_config(host_node, port_block.subscription_instance_id, DESCRIPTION_SCOPE, fragments)


def set_channel_description(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    facility_id: str,
    description: str,
) -> dict[str, Any]:
    """Make a Groove G30 optical channel carry the given description; return the applied diff.

    Args:
        optical_node_block: Optical Node of which the optical channel is to be modified,
            which also owns the setting.
        facility_id: The id of the optical channel to set the description on (e.g. ``"1/1/1"``).
        description: The description to set on the channel.
    """
    och_os = g30_och_os_node(get_g30_client(optical_node_block).data, facility_id)
    return apply_config(
        optical_node_block,
        optical_node_block.subscription_instance_id,
        CHANNEL_DESCRIPTION_SCOPE.format(facility_id),
        [fragment(och_os, service_label=description)],
    )


def set_port_admin_state(
    port_block: AnyOpticalPortBlockProvisioning,
    admin_state: Literal["up", "down", "maintenance"],
) -> dict[str, Any]:
    """Make a Groove G30 optical port run the given administrative state; return the applied diff."""
    host_node, _, port = _host_and_root(port_block)
    fragments = [fragment(port, admin_status=_ADMIN_STATUS[admin_state])]
    return apply_config(host_node, port_block.subscription_instance_id, ADMIN_STATE_SCOPE, fragments)


def _is_amplifier_port(
    host_node: AnyOpticalNodeBlockProvisioningUnion,
    slot_id: int,
    subslot_id: int | None,
) -> bool:
    """Return whether the port at the given slot/subslot is an amplifier line port.

    Derived from the installed cards rather than from a fixed slot layout: the subcard
    in the given subslot is an amplifier when its card type provides the amplifier
    function. Falls back to the card itself when the subslot holds no subcard, so a card
    that is an amplifier in its own right is recognised too.
    """
    modules = {(module.slot_id, module.subslot_id): module for module in g30_modules(host_node)}
    if subslot_id is not None and (module := modules.get((slot_id, subslot_id))) is not None:
        return module.is_amplifier
    return modules[(slot_id, None)].is_amplifier


def _render_amplifiers(root: Any, shelf_id: int, slot_id: int, subslot_id: int | None) -> list[Fragment]:
    """Render the booster and the preamplifier of a Groove G30 amplifier port.

    Raises:
        ValueError: If no subslot id is available for the amplifier port.
    """
    if subslot_id is None:
        msg = "Amplifier port configuration requires a subslot id"
        raise ValueError(msg)
    card = root.ne_ne.shelf(shelf_id).slot(slot_id).card
    return [
        fragment(
            card.subslot(_BOOSTER_SUBSLOT_ID).subcard.amplifier("ba"),
            admin_status="up",
            amplifier_enable="enabled",
            input_los_shutdown="disabled",
            control_mode="manual",
            gain_range_control="manual",
            target_gain_range=GainRangeTypeEnum.STANDARD,
            target_gain=Decimal("22.0"),
            output_voa=Decimal("10.0"),
            tilt_control_mode="manual",
            gain_tilt=Decimal("0.0"),
        ),
        fragment(
            card.subslot(subslot_id).subcard.amplifier("pa"),
            admin_status="up",
            amplifier_enable="enabled",
            input_los_shutdown="disabled",
            control_mode="auto",
            gain_range_control="auto",
            target_gain_range=GainRangeTypeEnum.STANDARD,
            tilt_control_mode="auto",
        ),
    ]


def render_termination(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
    *,
    amplifiers: bool = True,
) -> list[Fragment]:
    """Render a Groove G30 port terminating a fiber that leads to the remote port.

    A fiber between two ports of the same device is recorded as an internal patch; any
    other one as external connectivity to the remote node and port. The amplifier port
    of a Groove G30 facing another Groove G30 also carries the settings of its booster
    and preamplifier, found by reading the installed cards.

    Args:
        optical_port_block: The local port.
        remote_port_block: The remote port the fiber leads to.
        amplifiers: Whether to render the booster and preamplifier of an amplifier port.

    Returns:
        The desired configuration of the termination.

    Raises:
        ValueError: If the remote platform is not supported.
    """
    host_node, root, port = _host_and_root(optical_port_block)
    remote_host_node = remote_port_block.optical_port_host_node
    remote_port_name = _port_name(remote_port_block)
    external = fragment(
        port,
        external_connectivity="yes",
        connected_to=f"{_node_id(remote_host_node)} {remote_port_name}",
        admin_status="up",
    )

    match (
        remote_host_node.management.optical_module_node_vendor,
        remote_host_node.management.optical_module_node_platform,
    ):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return [external]
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            if _same_node(host_node, remote_host_node):
                return [
                    fragment(
                        port,
                        external_connectivity="no",
                        connected_to=f"patched to {remote_port_name}",
                        admin_status="up",
                    )
                ]
            shelf_id, slot_id, subslot_id, _, _ = g30_ids_from_port_name(_port_name(optical_port_block))
            if not amplifiers or not _is_amplifier_port(host_node, slot_id, subslot_id):
                return [external]
            # link H4: the port is an amplifier port of a different Groove G30 device
            return [*_render_amplifiers(root, shelf_id, slot_id, subslot_id), external]
        case _:
            msg = (
                "Unsupported remote optical device platform when configuring Groove G30 remote port: "
                f"{type(remote_host_node).__name__}"
            )
            raise ValueError(msg)


def configure_termination(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> dict[str, Any]:
    """Make a Groove G30 port run the configuration of the fiber attached to it; return the applied diff."""
    return apply_config(
        optical_port_block.optical_port_host_node,
        optical_port_block.subscription_instance_id,
        TERMINATION_SCOPE,
        render_termination(optical_port_block, remote_port_block),
    )


def factory_reset(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> dict[str, Any]:
    """Release the fiber termination of a Groove G30 port; return the applied diff.

    The port leaves go back to their factory value unless another product block (e.g. a
    service using the port) still holds them.
    """
    return release_config(
        optical_port_block.optical_port_host_node,
        optical_port_block.subscription_instance_id,
        TERMINATION_SCOPE,
        render_termination(optical_port_block, remote_port_block, amplifiers=False),
    )


def check_fiber(
    optical_port_block: AnyOpticalPortBlockProvisioning,
    remote_port_block: AnyOpticalPortBlockProvisioning,
) -> None:
    """Check that a Groove G30 port attached to a fiber runs its termination configuration.

    The amplifier settings of an amplifier port are not part of the check: they are
    tuned on the device after the fiber is attached.

    Raises:
        ValueError: If the port configuration differs.
    """
    verify_config(
        optical_port_block.optical_port_host_node,
        optical_port_block.subscription_instance_id,
        TERMINATION_SCOPE,
        render_termination(optical_port_block, remote_port_block, amplifiers=False),
    )


def get_transceiver_capacity_from_mode(mode: str) -> int | None:
    """Return the carrier capacity in Gbit/s of a Groove G30 transceiver mode.

    The capacity is the effective rate class of the mode (e.g. ``8QAM_300G``
    carries 150G), not the bitrate in the mode name; modes without coherent
    properties yield None (unknown capacity).

    Args:
        mode: The operating mode string stored on the transport channel.

    Returns:
        The capacity in Gbit/s, or None when the mode carries no bitrate.
    """
    _, rate = _get_modulation_and_rate_from_mode(mode)
    match = re.fullmatch(r"(\d+)G", rate.strip())
    return int(match.group(1)) if match else None
