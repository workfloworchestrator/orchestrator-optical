"""Shared helpers and steps for Optical Digital Service workflows.

This module ships the parts shared by the create, modify, terminate, validate
and reconcile workflows of the family: the state key under which the shipped
Optical Digital Service block travels in the workflow state, the block
re-hydration/load/description helpers, the endpoint/line-port/channel selectors,
 the subscription assembly (the shipped construct steps build the shipped
 subscription manually around a pre-built block: port blocks require their
 host node at construction time, and speed/type are fixed inputs read from
 the product row, never asked in a form), and the block-level
device-push/verify/teardown steps.

Device access goes only through the HAL dispatchers
(:mod:`orchestrator.optical.hal.transport_channel`,
:mod:`orchestrator.optical.hal.spectrum`); the path engine, the OLS selectors,
the port-availability guard and the section teardown are reused from
:mod:`orchestrator.optical.workflows.optical_spectrum_service.shared`.
Database queries live in the neutral ``orchestrator/optical/db.py`` module.

Coherent pluggables are managed by their own dedicated subscriptions: a digital
service never creates one, it links the existing
``OpticalCoherentPluggableBlock`` instances hosted on the selected packet node
that are not already in use by another digital service. The device push for
coherent-pluggable-hosted ports is not implemented yet: every step that would
configure one raises ``NotImplementedError``.
"""

from time import sleep
from typing import Any, NamedTuple, cast
from uuid import UUID

from pydantic_forms.types import State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from orchestrator.core.db import ProductTable, SubscriptionInstanceTable, SubscriptionTable, db
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel, ProductModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.optical.db import (
    node_block_from_subscription,
    subscription_instance_values_by_block_type_depending_on_instance_id,
    subscription_instances_by_block_type,
    subscriptions_by_product_type,
)
from orchestrator.optical.hal.port import (
    get_transceiver_capacity_from_mode as hal_get_transceiver_capacity_from_mode,
)
from orchestrator.optical.hal.spectrum import (
    append_optical_circuit_label,
    deploy_optical_circuit,
    modify_optical_circuit,
    validate_optical_circuit,
)
from orchestrator.optical.hal.transport_channel import (
    align_tx_power_to_target,
    configure_line_transceivers,
    configure_transceiver_client,
    configure_transponder_crossconnect,
    delete_transponder_crossconnect,
    delta_rx_power_vs_target,
    factory_reset_transponder_client,
    factory_reset_transponder_lines,
    get_signal_bandwidth,
    validate_trx_client,
    validate_trx_crossconnect,
    validate_trx_line,
)
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlock,
    OpticalDigitalServiceBlockInactive,
    OpticalDigitalServiceBlockProvisioning,
    OpticalDigitalServiceSpeed,
    OpticalDigitalServiceType,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.optical_packet_node import (
    OpticalModulePacketNodeBlock,
)
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_spectrum import OpticalSpectrumBlockInactive
from orchestrator.optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlock,
    OpticalTransportChannelBlockInactive,
    OpticalTransportChannelBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_digital_service import (
    OpticalDigitalServiceInactive,
)
from orchestrator.optical.utils.custom_types.frequencies import Bandwidth, Frequency, Passband
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import rehydrate_optical_module_block
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    check_optical_spectrum_add_drop_port_availability,
    delete_optical_spectrum_sections,
    find_add_drop_ports,
    get_optical_node_subscriptions_by_roles,
    save_foreign_passband_ports,
    store_list_of_ports_into_spectrum_sections,
    update_used_passbands,
)

logger = get_logger(__name__)

#: Roles of the Optical Nodes that can host an endpoint of a digital service:
#: transponder nodes and packet nodes (coherent pluggables).
DIGITAL_ENDPOINT_ROLES = [
    OpticalNodeRole.TRANSPONDER,
    OpticalNodeRole.TRANSPONDER_XOADM,
    OpticalNodeRole.IPODWDM,
]

#: Placeholder path value meaning the endpoints are directly connected, with no
#: line system in between (mirrors the transport-channel path selector).
DIRECT_CONNECTION = "direct_connection"


def optical_digital_service_block_from_state(
    optical_module_block: OpticalDigitalServiceBlockInactive | dict[str, Any] | None,
) -> OpticalDigitalServiceBlockProvisioning:
    """Return the Optical Digital Service block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the full block data) rather than as a domain
    model. This helper returns the value unchanged when it is already a domain
    model (in-process usage, e.g. in tests) and reconstructs the block from the
    serialized data otherwise. The shipped block steps always operate on the
    PROVISIONING variant: their callers construct the block with the mandatory
    fields set and transition the subscription to PROVISIONING before running them.

    Args:
        optical_module_block: The block value from the workflow state, or None.

    Returns:
        The Optical Digital Service block as a domain model.

    Raises:
        ValueError: If there is no Optical Digital Service block in the state
            under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    if optical_module_block is None:
        msg = "No Optical Digital Service block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    if isinstance(optical_module_block, OpticalDigitalServiceBlockInactive):
        return cast(OpticalDigitalServiceBlockProvisioning, optical_module_block)
    return cast(
        OpticalDigitalServiceBlockProvisioning,
        rehydrate_optical_module_block(optical_module_block, block_description="Optical Digital Service"),
    )


def _optical_digital_service_block_of_subscription(
    subscription: SubscriptionModel,
) -> OpticalDigitalServiceBlockInactive:
    """Return the Optical Digital Service block under the ``optical_digital_service`` attribute.

    This is the shipped-model fallback of the family: it reads the block from
    the ``optical_digital_service`` attribute of the subscription, which the
    shipped subscription models always have.

    Args:
        subscription: The Optical Digital Service subscription.

    Returns:
        The Optical Digital Service block of the subscription.

    Raises:
        ValueError: If the subscription has no block under the attribute.
    """
    digital_service = getattr(subscription, "optical_digital_service", None)
    if digital_service is None:
        msg = (
            "Optical Digital Service subscription has no Optical Digital Service block under attribute "
            "'optical_digital_service': the subscription model must have-a the Optical Digital Service block, "
            "e.g. under 'optical_digital_service'"
        )
        raise ValueError(msg)
    return cast(OpticalDigitalServiceBlockInactive, digital_service)


def optical_digital_service_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalDigitalServiceBlockInactive | None = None,
) -> str:
    """Generate the human-readable description of an Optical Digital Service subscription.

    Args:
        subscription: The Optical Digital Service subscription.
        optical_module_block: The Optical Digital Service block of the subscription.
            When given, it is used instead of the ``optical_digital_service``
            attribute of the shipped subscription models.

    Returns:
        The subscription description, e.g. ``"my-service (Optical Digital Service)"``.

    Raises:
        ValueError: If the subscription has no Optical Digital Service block under the
            ``optical_digital_service`` attribute and no block was passed.
    """
    digital_service = optical_module_block or _optical_digital_service_block_of_subscription(subscription)
    if digital_service.optical_digital_service_name:
        return f"{digital_service.optical_digital_service_name} ({subscription.product.name})"
    return subscription.product.name


@step("Load optical digital service block")
def load_optical_digital_service_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Digital Service block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_digital_service`` attribute: it makes
    the block available to the shipped block steps under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. Consumers that compose the shipped
    block under a different attribute name write their own one-step wiring
    instead.

    Args:
        subscription: The Optical Digital Service subscription.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Digital Service block under the
            ``optical_digital_service`` attribute.
    """
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: _optical_digital_service_block_of_subscription(subscription)}


@step("Set Optical Digital Service subscription description")
def set_optical_digital_service_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalDigitalServiceBlockInactive | None = None,
) -> State:
    """Set the description of the Optical Digital Service subscription.

    The block is read from the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``
    (put there by the construct step of the shipped create workflow or by
    :func:`load_optical_digital_service_block` in the other shipped workflows); a step
    chain must always load the block into the state before this step runs.

    Args:
        subscription: The Optical Digital Service subscription.
        optical_module_block: The Optical Digital Service block of the subscription, as
            available in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    subscription.description = optical_digital_service_subscription_description(subscription, block)
    return {"subscription": subscription, "subscription_description": subscription.description}


def is_packet_node_host(host_subscription_id: UUIDstr) -> bool:
    """Return whether the given endpoint host subscription is a packet node.

    Args:
        host_subscription_id: Subscription id of the endpoint host.

    Returns:
        True when the host is an Optical Module Packet Node (``IPODWDM`` role),
        whose ports are coherent pluggables managed by their own subscriptions.
    """
    return isinstance(node_block_from_subscription(host_subscription_id), OpticalModulePacketNodeBlock)


def optical_digital_endpoint_selector(prompt: str | None = None) -> type[Choice]:
    """Create a ``Choice`` selector for the endpoint hosts of a digital service.

    The endpoints are the transponder nodes (Groove G30 / GX G42) and the
    packet nodes hosting coherent pluggables. The option values are the host
    subscription ids.

    Args:
        prompt: Prompt of the selector. When omitted, a default prompt is generated.

    Returns:
        A ``Choice`` class whose values are host subscription ids.
    """
    subscriptions = list(get_optical_node_subscriptions_by_roles(DIGITAL_ENDPOINT_ROLES))
    subscriptions.extend(
        subscriptions_by_product_type(ProductType.OPTICAL_MODULE_PACKET_NODE.value, [SubscriptionLifecycle.ACTIVE])
    )
    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }
    if not prompt:
        prompt = "Select an endpoint host (transponder node or packet node)"
    return cast(type[Choice], Choice(prompt, zip(products.keys(), products.items(), strict=False)))


def port_ids_used_by_digital_services() -> set[str]:
    """Return the subscription instance ids of the ports used by digital services.

    Every digital service in INITIAL, PROVISIONING or ACTIVE state contributes
    its two client ports and the line ports of its transport channels: those
    ports are already carrying a service and cannot be selected for a new one.
    Because every consumer that composes the shipped block persists it under the
    shipped block name, the check also covers composed product types.

    Returns:
        The subscription instance ids of the client and line ports in use.
    """
    in_use: set[str] = set()
    instances = subscription_instances_by_block_type(
        cast(str, OpticalDigitalServiceBlock.name),
        [SubscriptionLifecycle.INITIAL, SubscriptionLifecycle.PROVISIONING, SubscriptionLifecycle.ACTIVE],
    )
    for instance in instances:
        digital = OpticalDigitalServiceBlock.from_db(subscription_instance_id=instance.subscription_instance_id)
        for client_port in digital.optical_digital_service_client_ports:
            in_use.add(str(client_port.subscription_instance_id))
        for channel in digital.optical_digital_service_transport_channels:
            for line_port in channel.optical_transport_line_ports:
                in_use.add(str(line_port.subscription_instance_id))
    return in_use


def has_flexils_sections(block: OpticalDigitalServiceBlockProvisioning) -> bool:
    """Return whether any transport channel of the block has a FlexILS section.

    Args:
        block: The Optical Digital Service block to inspect.

    Returns:
        True when at least one section is hosted on a FlexILS node.
    """
    return any(
        (
            section.optical_spectrum_section_add_drop_ports[
                0
            ].optical_port_host_node.management.optical_module_node_vendor,
            section.optical_spectrum_section_add_drop_ports[
                0
            ].optical_port_host_node.management.optical_module_node_platform,
        )
        == (Vendor.NOKIA, Platform.FLEXILS)
        for channel in block.optical_digital_service_transport_channels
        for section in channel.optical_transport_spectrum.optical_spectrum_sections
    )


def _parse_port_identifiers(port_name: str, platform: Platform) -> tuple[str, str, str]:
    """Split a device port name into shelf, slot and port identifiers.

    The conventions are the device-native ones (see the HAL adapters):
    ``"port-1/2/3"`` on Groove G30, ``"1-4-L1"`` on GX G42.

    Args:
        port_name: The device-native port name.
        platform: The platform of the hosting node.

    Returns:
        The ``(shelf, slot, port)`` identifiers as strings.

    Raises:
        ValueError: If the platform is not a transponder platform or the name does not parse.
    """
    match platform:
        case Platform.GROOVE_G30:
            raw = port_name.split("-", 1)[-1]
            shelf, slot, port = raw.split("/")
        case Platform.GX_G42:
            shelf, slot, port = port_name.split("-", 2)
        case _:
            msg = f"Cannot parse port identifiers on platform {platform}"
            raise ValueError(msg)
    return shelf, slot, port


def _is_line_port_name(port: str, platform: Platform) -> bool:
    """Return whether a port identifier is a line (coherent) port of its card."""
    match platform:
        case Platform.GROOVE_G30:
            return port.isdigit() and int(port) in (1, 2)
        case Platform.GX_G42:
            return port in ("L1", "L2")
        case _:
            return False


def line_port_selector(host_subscription_id: UUIDstr, client: str, prompt: str | None = None) -> type[Choice]:
    """Create a ``Choice`` selector for the line ports of an endpoint host's card.

    On a packet node the selector holds a single option: the client pluggable
    itself (a coherent pluggable is simultaneously client and line). On a
    transponder host the candidates are the patched line port blocks on the
    same card (shelf/slot) as the client port that are not already in use by
    another digital service. The option values are the port block subscription
    instance ids. This is the convergence point for the future pipe
    termination of pluggables: the filter will apply here once, to both types.

    Args:
        host_subscription_id: Subscription id of the endpoint host.
        client: The client port name (transponder host) or the client
            pluggable instance id (packet node), as selected on the client page.
        prompt: Prompt of the selector. When omitted, a default prompt is generated.

    Returns:
        A ``Choice`` class whose values are port block subscription instance ids.
    """
    host_block = node_block_from_subscription(host_subscription_id)
    if isinstance(host_block, OpticalModulePacketNodeBlock):
        pluggable_id = str(client)
        label = pluggable_id
        for instance_value in subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type="CoherentPluggableBlock",
            resource_type="optical_port_name",
            depending_on_instance_id=str(host_block.subscription_instance_id),
            states=[SubscriptionLifecycle.ACTIVE],
        ):
            if str(instance_value.subscription_instance_id) == pluggable_id:
                label = str(instance_value.value)
        if not prompt:
            prompt = "Select a line port"
        return cast(
            type[Choice],
            Choice(prompt, [(pluggable_id, (pluggable_id, label))]),
        )
    platform = host_block.management.optical_module_node_platform
    if platform not in (Platform.GROOVE_G30, Platform.GX_G42):
        msg = f"Line port selection is not supported on platform {platform}"
        raise ValueError(msg)
    try:
        shelf_id, slot_id, _ = _parse_port_identifiers(str(client), platform)
    except ValueError as exc:
        msg = f"Cannot determine the card of client port {client!r}: {exc}"
        raise ValueError(msg) from exc
    in_use = port_ids_used_by_digital_services()
    candidates: dict[str, str] = {}
    for instance_value in subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type="OpticalTransponderLinePortBlock",
        resource_type="optical_port_name",
        depending_on_instance_id=str(host_block.subscription_instance_id),
        states=[SubscriptionLifecycle.ACTIVE],
    ):
        port_instance_id = str(instance_value.subscription_instance_id)
        if port_instance_id in in_use:
            continue
        port_name = str(instance_value.value)
        try:
            shelf, slot, port = _parse_port_identifiers(port_name, platform)
        except ValueError:
            continue
        if shelf != shelf_id or slot != slot_id or not _is_line_port_name(port, platform):
            continue
        candidates[port_instance_id] = port_name
    if not prompt:
        prompt = "Select a line port"
    options = sorted(candidates.items(), key=lambda item: item[1])
    return cast(
        type[Choice],
        Choice(prompt, [(port_id, (port_id, port_name)) for port_id, port_name in options]),
    )


def unused_coherent_pluggable_selector(host_subscription_id: UUIDstr, prompt: str | None = None) -> type[Choice]:
    """Create a ``Choice`` selector for the unused coherent pluggables of a packet node.

    Coherent pluggables are managed by their own dedicated subscriptions: the
    candidates are the existing ``CoherentPluggableBlock`` instances hosted on
    the packet node that are not already in use by a digital service. The
    option values are the pluggable block subscription instance ids.

    Args:
        host_subscription_id: Subscription id of the packet node.
        prompt: Prompt of the selector. When omitted, a default prompt is generated.

    Returns:
        A ``Choice`` class whose values are pluggable block subscription instance ids.
    """
    host_block = node_block_from_subscription(host_subscription_id)
    host_instance_id = str(host_block.subscription_instance_id)
    in_use = port_ids_used_by_digital_services()
    candidates: dict[str, str] = {}
    for instance_value in subscription_instance_values_by_block_type_depending_on_instance_id(
        product_block_type="CoherentPluggableBlock",
        resource_type="optical_port_name",
        depending_on_instance_id=host_instance_id,
        states=[SubscriptionLifecycle.ACTIVE],
    ):
        port_instance_id = str(instance_value.subscription_instance_id)
        if port_instance_id not in in_use:
            candidates[port_instance_id] = str(instance_value.value)
    if not prompt:
        prompt = "Select a coherent pluggable"
    options = sorted(candidates.items(), key=lambda item: item[1])
    return cast(
        type[Choice],
        Choice(prompt, [(port_id, (port_id, port_name)) for port_id, port_name in options]),
    )


class ChannelReuseGroup(NamedTuple):
    """A reusable unit of already provisioned transport channels.

    Channels coupled by the same owning subscription are offered (and linked)
    together: the group spare capacity is the sum over the members.
    """

    channel_ids: tuple[str, ...]
    channel_names: tuple[str, ...]
    mode: str
    total_capacity: int
    spare_capacity: int


def get_transceiver_capacity_from_mode(host_node_blocks: list[Any], mode: str) -> int | None:
    """Return the carrier capacity in Gbit/s of a transceiver mode on endpoint hosts.

    Each host resolves the mode through the HAL dispatcher
    (:func:`orchestrator.optical.hal.port.get_transceiver_capacity_from_mode`),
    which match-cases on the host vendor/platform; packet-node hosts expose no
    transceiver mode table and unknown modes resolve to None. Unresolvable
    hosts are skipped best-effort, so a transponder-coherent pair takes the
    transponder value.

    Args:
        host_node_blocks: The endpoint host node blocks of the channel.
        mode: The operating mode string stored on the transport channel.

    Returns:
        The agreed capacity in Gbit/s, or None when no host resolves one.

    Raises:
        ValueError: If the hosts resolve to different capacities.
    """
    values: set[int] = set()
    for host in host_node_blocks:
        if isinstance(host, OpticalModulePacketNodeBlock):
            continue
        try:
            value = hal_get_transceiver_capacity_from_mode(host, mode)
        except Exception:  # noqa: BLE001 - best-effort: unknown capacity, the channel is not offered for reuse
            logger.warning("Could not resolve transceiver capacity, treating it as unknown", mode=mode)
            continue
        if value is not None:
            values.add(value)
    if len(values) > 1:
        msg = f"Ambiguous transceiver capacity for mode {mode!r}: {sorted(values)}"
        raise ValueError(msg)
    return next(iter(values), None)


def _channel_line_port_hosts(channel: OpticalTransportChannelBlock) -> set[str]:
    """Return the owner subscription ids of the endpoint hosts of a channel.

    Each line port resolves to its host through ``optical_port_host_node``; for
    a coherent pluggable that is the packet node hosting the pluggable.
    """
    hosts = set()
    for line_port in channel.optical_transport_line_ports:
        host = cast(Any, line_port).optical_port_host_node
        hosts.add(str(host.owner_subscription_id))
    return hosts


def _distinct_using_service_speeds(channel: OpticalTransportChannelBlock) -> dict[str, int]:
    """Return the speeds of the non-terminated digital services using a channel.

    A reused channel may carry several digital services; the speeds are keyed
    by subscription id so a service coupled over several channels of one group
    is counted once per group (see :func:`reusable_channel_groups`).

    Args:
        channel: The transport channel block to inspect (freshly loaded).

    Returns:
        Mapping of user subscription id to service speed in Gbit/s.
    """
    speeds: dict[str, int] = {}
    for instance in channel.in_use_by:
        subscription = instance.subscription
        if subscription.status == SubscriptionLifecycle.TERMINATED:
            continue
        model = SubscriptionModel.from_subscription(subscription.subscription_id)
        speed = getattr(model, "optical_digital_service_speed", None)
        if speed is not None:
            speeds[str(subscription.subscription_id)] = int(speed)
    return speeds


def channel_spare_capacity(channel: OpticalTransportChannelBlock) -> int | None:
    """Return the spare capacity in Gbit/s of an already provisioned channel.

    Args:
        channel: The transport channel block to inspect (freshly loaded).

    Returns:
        The total capacity minus the speeds of its non-terminated digital
        service users, or None when the total capacity is unknown.
    """
    total = channel.optical_transport_total_capacity
    if total is None:
        return None
    channel = OpticalTransportChannelBlock.from_db(subscription_instance_id=channel.subscription_instance_id)
    used = sum(_distinct_using_service_speeds(channel).values())
    return total - used


def _owner_group_spare(members: list[OpticalTransportChannelBlock]) -> tuple[int, int]:
    """Return the (total, spare) capacity in Gbit/s of an owner group of channels.

    The spare is the summed total minus the speeds of the distinct
    non-terminated digital services using any member, so a service coupled
    over several members is counted once.

    Args:
        members: The transport channel blocks of one owning subscription.
    """
    totals = sum(channel.optical_transport_total_capacity or 0 for channel in members)
    used: dict[str, int] = {}
    for channel in members:
        fresh = OpticalTransportChannelBlock.from_db(subscription_instance_id=channel.subscription_instance_id)
        used.update(_distinct_using_service_speeds(fresh))
    return totals, totals - sum(used.values())


def resolve_channels_by_names(
    channel_names: list[str],
    speed: int,
    src_host_id: UUIDstr,
    dst_host_id: UUIDstr,
) -> tuple[str, ChannelReuseGroup | None]:
    """Decide whether the named transport channels are new or reused.

    This is the single source of truth for the name-driven fork, used by the
    identity form validator (early user feedback), the page sequence and the
    construct step (authoritative): ``"new"`` when no channel carries any of
    the names, otherwise ``"reuse"`` of the matched owner group. The endpoint
    match is order-insensitive: naming channels that run from dst to src is
    accepted as-is, because channels are bidirectional and every side-specific
    choice happens on later pages.

    Args:
        channel_names: User-facing names of the transport channels (one, or two
            for reverse multiplexing); blank entries are ignored.
        speed: Speed of the new digital service in Gbit/s.
        src_host_id: Subscription id of the source endpoint host.
        dst_host_id: Subscription id of the destination endpoint host.

    Returns:
        ``("new", None)``, or ``("reuse", group)`` with the owner group to link.

    Raises:
        ValueError: If the names are not distinct, if some names exist and
            others do not, if a named channel is still being created, if the
            named channels belong to several services or cover a group only
            partially (whole groups are linked, never split), if they terminate
            on a different host pair, if a member has unknown total capacity,
            or if the group spare capacity does not fit the new service speed.
    """
    names = [name.strip() for name in channel_names if name.strip()]
    if len(set(names)) != len(names):
        msg = "The transport channels must have different names"
        raise ValueError(msg)
    instances = subscription_instances_by_block_type(
        cast(str, OpticalTransportChannelBlock.name),
        [SubscriptionLifecycle.INITIAL, SubscriptionLifecycle.PROVISIONING, SubscriptionLifecycle.ACTIVE],
    )
    named: dict[str, SubscriptionInstanceTable] = {}
    for instance in instances:
        channel = OpticalTransportChannelBlock.from_db(subscription_instance_id=instance.subscription_instance_id)
        if str(channel.optical_transport_channel_name) in names:
            named[str(channel.optical_transport_channel_name)] = instance
    if not named:
        return ("new", None)
    if len(named) != len(names):
        missing = sorted(set(names) - set(named))
        msg = (
            "Transport channels must be either all new or all already provisioned: "
            f"{', '.join(missing)} match no existing channel"
        )
        raise ValueError(msg)
    in_flight = sorted(
        name for name, instance in named.items() if instance.subscription.status != SubscriptionLifecycle.ACTIVE
    )
    if in_flight:
        msg = f"Transport channels still being created, retry once they are active: {', '.join(in_flight)}"
        raise ValueError(msg)
    found = [
        OpticalTransportChannelBlock.from_db(subscription_instance_id=instance.subscription_instance_id)
        for instance in named.values()
    ]
    owners = {str(channel.owner_subscription_id) for channel in found}
    if len(owners) != 1:
        msg = "The named transport channels belong to several services; reuse one service's channels"
        raise ValueError(msg)
    members = sorted(
        (
            OpticalTransportChannelBlock.from_db(subscription_instance_id=instance.subscription_instance_id)
            for instance in subscription_instances_by_block_type(
                cast(str, OpticalTransportChannelBlock.name), [SubscriptionLifecycle.ACTIVE]
            )
        ),
        key=lambda channel: str(channel.optical_transport_channel_name),
    )
    members = [channel for channel in members if str(channel.owner_subscription_id) in owners]
    if {str(channel.subscription_instance_id) for channel in members} != {
        str(channel.subscription_instance_id) for channel in found
    }:
        msg = "Name the whole channel group of the owning service; groups are linked as a unit, never split"
        raise ValueError(msg)
    hosts = {str(src_host_id), str(dst_host_id)}
    mismatched = sorted(
        str(channel.optical_transport_channel_name) for channel in members if _channel_line_port_hosts(channel) != hosts
    )
    if mismatched:
        msg = (
            f"Termination mismatch for transport channels {', '.join(mismatched)}: "
            "reused channels must run between the selected endpoint hosts"
        )
        raise ValueError(msg)
    if any(channel.optical_transport_total_capacity is None for channel in members):
        msg = "The named channels have unknown total capacity and cannot be reused"
        raise ValueError(msg)
    totals, spare = _owner_group_spare(members)
    if spare < speed:
        msg = (
            f"The named channels only have {spare} Gbit/s of spare capacity "
            f"out of {totals} Gbit/s, but the service needs {speed} Gbit/s"
        )
        raise ValueError(msg)
    modes = {str(channel.optical_transport_mode) for channel in members}
    return (
        "reuse",
        ChannelReuseGroup(
            channel_ids=tuple(str(channel.subscription_instance_id) for channel in members),
            channel_names=tuple(str(channel.optical_transport_channel_name) for channel in members),
            mode=", ".join(sorted(modes)),
            total_capacity=totals,
            spare_capacity=spare,
        ),
    )


def reusable_channel_groups(src_host_id: UUIDstr, dst_host_id: UUIDstr, speed: int) -> list[ChannelReuseGroup]:
    """Return the reusable channel groups between two endpoint hosts.

    A group is one channel or the coupled channels of one owning subscription
    (same ``owner_subscription_id``). A group qualifies when every member
    terminates on the endpoint host pair, every member has a known total
    capacity, and the summed spare capacity fits the new service speed. The
    shipped create form resolves names instead of offering groups (see
    :func:`resolve_channels_by_names`); this stays as the query part for consumers
    composing their own forms.

    Args:
        src_host_id: Subscription id of the source endpoint host.
        dst_host_id: Subscription id of the destination endpoint host.
        speed: Speed of the new digital service in Gbit/s.

    Returns:
        The qualifying groups, sorted by group spare capacity.
    """
    hosts = {str(src_host_id), str(dst_host_id)}
    instances = subscription_instances_by_block_type(
        cast(str, OpticalTransportChannelBlock.name), [SubscriptionLifecycle.ACTIVE]
    )
    by_owner: dict[str, list[OpticalTransportChannelBlock]] = {}
    for instance in instances:
        channel = OpticalTransportChannelBlock.from_db(subscription_instance_id=instance.subscription_instance_id)
        if _channel_line_port_hosts(channel) != hosts:
            continue
        if channel.optical_transport_total_capacity is None:
            continue
        by_owner.setdefault(str(channel.owner_subscription_id), []).append(channel)
    groups: list[ChannelReuseGroup] = []
    for owner_members in by_owner.values():
        members = sorted(owner_members, key=lambda channel: str(channel.optical_transport_channel_name))
        totals, spare = _owner_group_spare(members)
        if spare < speed:
            continue
        modes = {str(channel.optical_transport_mode) for channel in members}
        groups.append(
            ChannelReuseGroup(
                channel_ids=tuple(str(channel.subscription_instance_id) for channel in members),
                channel_names=tuple(str(channel.optical_transport_channel_name) for channel in members),
                mode=", ".join(sorted(modes)),
                total_capacity=totals,
                spare_capacity=spare,
            )
        )
    return sorted(groups, key=lambda group: group.spare_capacity)


def channel_name_in_use(name: str) -> bool:
    """Return whether a transport channel name is already used by any channel."""
    instances = subscription_instances_by_block_type(
        cast(str, OpticalTransportChannelBlock.name),
        [
            SubscriptionLifecycle.INITIAL,
            SubscriptionLifecycle.PROVISIONING,
            SubscriptionLifecycle.ACTIVE,
        ],
    )
    for instance in instances:
        channel = OpticalTransportChannelBlockInactive.from_db(
            subscription_instance_id=instance.subscription_instance_id
        )
        if str(channel.optical_transport_channel_name) == name:
            return True
    return False


def _host_label(host_block: AnyOpticalNodeBlockProvisioningUnion) -> str:
    """Return the display name of an endpoint host block, tolerating unset values."""
    fqdn = host_block.management.optical_module_node_fqdn
    return str(fqdn) if fqdn is not None else "<unknown>"


def _ensure_transponder_ports(
    ports: list[Any],
) -> None:
    """Raise ``NotImplementedError`` when any of the given ports is coherent-pluggable-hosted.

    Args:
        ports: The client or line port blocks to check.

    Raises:
        NotImplementedError: If any port has the coherent pluggable role.
    """
    for port in ports:
        if port.optical_port_role is OpticalPortRole.COHERENT_PLUGGABLE:
            msg = "Coherent-pluggable-hosted ports are modelled but their device push is not implemented yet"
            raise NotImplementedError(msg)


def is_new_channel(
    channel: OpticalTransportChannelBlockProvisioning, digital_block: OpticalDigitalServiceBlockProvisioning
) -> bool:
    """Return whether a transport channel is owned by the digital service itself.

    Reused channels are owned by another subscription: their line ports, optical
    sections and passbands must not be re-provisioned, only their labels are
    extended with the new service name.

    Args:
        channel: The transport channel block to check.
        digital_block: The Optical Digital Service block owning the service.

    Returns:
        True when the channel owner is the digital service itself.
    """
    return str(channel.owner_subscription_id) == str(digital_block.owner_subscription_id)


def is_last_client_for_channels(channels: list[OpticalTransportChannelBlockProvisioning]) -> bool:
    """Return whether the digital service is the last client of its transport channels.

    A reused transport channel may carry several digital services: the line
    ports and the optical sections are torn down only when the terminating
    service is the last non-terminated client.

    Args:
        channels: The transport channel blocks of the service.

    Returns:
        True when every channel is used only by the terminating subscription.
    """
    for channel in channels:
        fresh = OpticalTransportChannelBlock.from_db(subscription_instance_id=channel.subscription_instance_id)
        remaining = [
            instance for instance in fresh.in_use_by if instance.subscription.status != SubscriptionLifecycle.TERMINATED
        ]
        if len(remaining) != 1:
            return False
    return True


def _parse_digital_service_fixed_inputs(
    fixed_inputs: dict[str, str],
) -> tuple[OpticalDigitalServiceSpeed, OpticalDigitalServiceType]:
    """Parse the speed and framing type from a digital service product's fixed inputs.

    Raises:
        ValueError: If a fixed input is missing or not a valid enum member.
    """
    try:
        speed_raw = fixed_inputs["optical_digital_service_speed"]
        type_raw = fixed_inputs["optical_digital_service_type"]
    except KeyError as exc:
        msg = f"Digital service product misses fixed input {exc}"
        raise ValueError(msg) from exc
    try:
        return OpticalDigitalServiceSpeed(int(speed_raw)), OpticalDigitalServiceType(type_raw)
    except ValueError as exc:
        msg = f"Invalid digital service fixed inputs: speed={speed_raw!r}, type={type_raw!r}"
        raise ValueError(msg) from exc


def optical_digital_service_speed_and_type(
    product_id: UUIDstr,
) -> tuple[OpticalDigitalServiceSpeed, OpticalDigitalServiceType]:
    """Return the speed and framing type fixed on a digital service product.

    Speed and type are fixed inputs: they are stored 1:1 on the product row and
    must never be asked in a form — the product chosen at workflow start already
    determines them.

    Raises:
        KeyError: If no product exists for the given product id.
        ValueError: If a fixed input is missing or not a valid enum member.
    """
    product_db = db.session.get(ProductTable, product_id)
    if product_db is None:
        msg = f"Could not find a product for the given product_id {product_id}"
        raise KeyError(msg)
    fixed_inputs = {fixed_input.name: fixed_input.value for fixed_input in product_db.fixed_inputs}
    return _parse_digital_service_fixed_inputs(fixed_inputs)


def optical_digital_service_speed_and_type_for_product(
    product_name: str,
) -> tuple[OpticalDigitalServiceSpeed, OpticalDigitalServiceType]:
    """Return the speed and framing type fixed on a digital service product by name.

    Raises:
        KeyError: If no product exists for the given product name.
        ValueError: If a fixed input is missing or not a valid enum member.
    """
    product_db = ProductTable.query.filter_by(name=product_name).one_or_none()
    if product_db is None:
        msg = f"Could not find a product for the given product_name {product_name}"
        raise KeyError(msg)
    fixed_inputs = {fixed_input.name: fixed_input.value for fixed_input in product_db.fixed_inputs}
    return _parse_digital_service_fixed_inputs(fixed_inputs)


def new_optical_digital_service_subscription(
    product_id: UUIDstr,
    customer_id: str,
    digital_block: OpticalDigitalServiceBlockInactive,
    speed: OpticalDigitalServiceSpeed,
    service_type: OpticalDigitalServiceType,
) -> OpticalDigitalServiceInactive:
    """Build a new digital service subscription model around a pre-built digital block.

    ``from_product_id`` is not used for digital services: the digital block is
    built first (see :func:`build_optical_digital_service_block`), with its
    client ports and transport channels already in place — port blocks require
    their host node at construction time and live availability checks against
    the database — and the subscription model is assembled around that block
    under the same subscription id. Speed and framing type are fixed inputs:
    they come from the product row, never from a form.

    Args:
        product_id: Id of the digital service product.
        customer_id: Customer id of the digital service.
        digital_block: The digital service block with its client ports and channels.
        speed: Speed of the digital service, kept in sync on the subscription.
        service_type: Framing protocol type, kept in sync on the subscription.

    Returns:
        The new digital service subscription model in the INITIAL state.

    Raises:
        KeyError: If no product exists for the given product id.
    """
    product_db = db.session.get(ProductTable, product_id)
    if product_db is None:
        msg = f"Could not find a product for the given product_id {product_id}"
        raise KeyError(msg)

    product = ProductModel(
        product_id=product_db.product_id,
        name=product_db.name,
        description=product_db.description,
        product_type=product_db.product_type,
        tag=product_db.tag,
        status=product_db.status,
        created_at=product_db.created_at,
        end_date=product_db.end_date,
    )
    description = f"Initial subscription of {product_db.description}"
    subscription_id = digital_block.owner_subscription_id
    subscription = SubscriptionTable(
        subscription_id=subscription_id,
        product_id=product_id,
        customer_id=customer_id,
        description=description,
        status=SubscriptionLifecycle.INITIAL.value,
        insync=False,
        version=1,
    )
    db.session.add(subscription)

    fixed_inputs = {fixed_input.name: fixed_input.value for fixed_input in product_db.fixed_inputs}
    model_data: dict[str, Any] = {
        "product": product,
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "description": description,
        "status": SubscriptionLifecycle.INITIAL,
        "insync": False,
        "start_date": None,
        "end_date": None,
        "note": None,
        "version": 1,
        **fixed_inputs,
        "optical_digital_service_speed": speed,
        "optical_digital_service_type": service_type,
        "optical_digital_service": digital_block,
    }
    model = cast(OpticalDigitalServiceInactive, OpticalDigitalServiceInactive(**model_data))
    model.db_model = subscription
    return model


def populate_optical_digital_service_block(
    optical_module_block: OpticalDigitalServiceBlockInactive,
    optical_digital_service_name: str,
    optical_digital_service_speed: OpticalDigitalServiceSpeed,
    optical_digital_service_type: OpticalDigitalServiceType,
) -> None:
    """Populate an Optical Digital Service block from the create-form state keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle.

    Args:
        optical_module_block: The Optical Digital Service block to populate (any lifecycle variant).
        optical_digital_service_name: User-facing name of the digital service.
        optical_digital_service_speed: Speed of the digital service in Gbit/s.
        optical_digital_service_type: Framing protocol type of the digital service.
    """
    optical_module_block.optical_digital_service_name = optical_digital_service_name
    optical_module_block.optical_digital_service_speed = optical_digital_service_speed
    optical_module_block.optical_digital_service_type = optical_digital_service_type


def build_optical_digital_service_block(
    subscription_id: UUID,
    optical_digital_service_name: str,
    optical_digital_service_speed: OpticalDigitalServiceSpeed,
    optical_digital_service_type: OpticalDigitalServiceType,
    src_host_id: UUIDstr,
    dst_host_id: UUIDstr,
    src_client_port: UUIDstr,
    dst_client_port: UUIDstr,
    reuse_channel_ids: list[UUIDstr],
    channel_names: list[str],
    line_port_ids_a: list[UUIDstr],
    line_port_ids_b: list[UUIDstr],
    frequencies: list[Frequency],
    bandwidths: list[Bandwidth],
    optical_transport_mode: str,
    optical_path: list[UUIDstr],
) -> OpticalDigitalServiceBlockInactive:
    """Build the Optical Digital Service block of a new subscription.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step to build the shipped block with its
    two client port blocks and its one or two transport channel blocks (each
    with its line ports, spectrum block and sections), before their
    subscription model is transitioned to the PROVISIONING lifecycle.

    Already provisioned transport channels can be reused: they are linked
    as-is (their sections already exist) and the new-channel arguments are
    ignored. Otherwise one channel block is built per name/frequency/bandwidth
    entry; the second channel of a reverse-multiplexed pair derives its
    endpoint add/drop ports from its own line ports while sharing the interior
    of the first channel path.

    Args:
        subscription_id: Subscription id of the new digital service subscription.
        optical_digital_service_name: User-facing name of the digital service.
        optical_digital_service_speed: Speed of the digital service in Gbit/s.
        optical_digital_service_type: Framing protocol type of the digital service.
        src_host_id: Subscription id of the source endpoint host.
        dst_host_id: Subscription id of the destination endpoint host.
        src_client_port: Name of the client port on a transponder source host,
            or subscription instance id of the existing coherent pluggable on a
            packet-node source host.
        dst_client_port: Name of the client port on a transponder destination host,
            or subscription instance id of the existing coherent pluggable on a
            packet-node destination host.
        reuse_channel_ids: Subscription instance ids of already provisioned
            transport channels to reuse (one, or a coupled pair with the same
            owning subscription), or an empty list to create new channels.
        channel_names: User-facing names of the new transport channels (one,
            or two for reverse multiplexing); ignored when reusing.
        line_port_ids_a: Subscription instance ids of the source line port blocks.
            On a packet-node side they must be the source client pluggable: a
            coherent pluggable is both client and line and cannot be anything else.
        line_port_ids_b: Subscription instance ids of the destination line port blocks.
            On a packet-node side they must be the destination client pluggable.
        frequencies: Central frequency of each new transport channel in MHz.
        bandwidths: Spectral width of each new transport channel in MHz.
        optical_transport_mode: Operating mode of the new transport channels.
        optical_path: Interior OLS port subscription instance ids of the first
            channel path, or ``["direct_connection"]`` when the endpoints are
            directly connected with no line system in between.

    Returns:
        The inactive Optical Digital Service block with its client ports and channels.

    Raises:
        ValueError: If a client port name is already in use, if a coherent
            pluggable is already used by another digital service, or if a
            packet-node side carries line ports other than the client pluggable.
    """
    src_host = node_block_from_subscription(src_host_id)
    dst_host = node_block_from_subscription(dst_host_id)
    src_fqdn = _host_label(cast(AnyOpticalNodeBlockProvisioningUnion, src_host))
    dst_fqdn = _host_label(cast(AnyOpticalNodeBlockProvisioningUnion, dst_host))

    for host, client_ref, line_ids, side in (
        (src_host, src_client_port, line_port_ids_a, "source"),
        (dst_host, dst_client_port, line_port_ids_b, "destination"),
    ):
        if isinstance(host, OpticalModulePacketNodeBlock) and any(
            str(line_id) != str(client_ref) for line_id in line_ids
        ):
            msg = (
                f"The {side} line ports must be the client pluggable itself: a coherent "
                "pluggable is both client and line and cannot be anything else"
            )
            raise ValueError(msg)

    def _client_port(
        host: Any,
        port_ref: UUIDstr,
        remote_fqdn: str,
        remote_ref: UUIDstr,
    ) -> Any:
        if isinstance(host, OpticalModulePacketNodeBlock):
            pluggable_id = str(port_ref)
            if pluggable_id in port_ids_used_by_digital_services():
                msg = f"Coherent pluggable {pluggable_id} is already in use by another digital service"
                raise ValueError(msg)
            return cast(Any, ProductBlockModel.from_db(UUID(pluggable_id)))
        check_optical_spectrum_add_drop_port_availability(
            host,
            str(port_ref),
            exclude_subscription_id=str(subscription_id),
        )
        return OpticalTransponderClientPortBlockInactive.new(
            subscription_id=subscription_id,
            optical_port_name=str(port_ref),
            optical_port_host_node=cast(Any, host),
            optical_port_description=f"{optical_digital_service_name} remote {remote_fqdn} {remote_ref}",
        )

    client_a = _client_port(src_host, src_client_port, dst_fqdn, dst_client_port)
    client_b = _client_port(dst_host, dst_client_port, src_fqdn, src_client_port)

    channels: list[OpticalTransportChannelBlockInactive] = []
    if reuse_channel_ids:
        for reuse_channel_id in reuse_channel_ids:
            reused = OpticalTransportChannelBlock.from_db(subscription_instance_id=UUID(str(reuse_channel_id)))
            channels.append(cast(OpticalTransportChannelBlockInactive, reused))
    else:
        for index, (channel_name, frequency, bandwidth) in enumerate(
            zip(channel_names, frequencies, bandwidths, strict=True)
        ):
            spectrum_name = f"{channel_name} spectrum"
            passband: Passband = (frequency - bandwidth // 2, frequency + bandwidth // 2)
            spectrum = OpticalSpectrumBlockInactive.new(
                subscription_id=subscription_id,
                optical_spectrum_name=spectrum_name,
                optical_spectrum_passband=passband,
            )
            if optical_path != [DIRECT_CONNECTION]:
                if index == 0:
                    store_list_of_ports_into_spectrum_sections(optical_path, spectrum)
                elif isinstance(src_host, OpticalModulePacketNodeBlock) or isinstance(
                    dst_host, OpticalModulePacketNodeBlock
                ):
                    # A packet-node side carries no add/drop ports of its own: the
                    # second carrier shares the first channel path as-is.
                    store_list_of_ports_into_spectrum_sections(optical_path, spectrum)
                else:
                    first_add_drop, last_add_drop = find_add_drop_ports(line_port_ids_a[-1], line_port_ids_b[-1])
                    derived_path = [
                        str(first_add_drop.subscription_instance_id),
                        *optical_path[1:-1],
                        str(last_add_drop.subscription_instance_id),
                    ]
                    store_list_of_ports_into_spectrum_sections(derived_path, spectrum)
            line_a: Any = ProductBlockModel.from_db(UUID(str(line_port_ids_a[index])))
            line_b: Any = ProductBlockModel.from_db(UUID(str(line_port_ids_b[index])))
            total_capacity = get_transceiver_capacity_from_mode(
                [line_a.optical_port_host_node, line_b.optical_port_host_node], optical_transport_mode
            )
            channel = OpticalTransportChannelBlockInactive.new(
                subscription_id=subscription_id,
                optical_transport_channel_name=channel_name,
                optical_transport_central_frequency=frequency,
                optical_transport_mode=optical_transport_mode,
                optical_transport_total_capacity=total_capacity,
                optical_transport_line_ports=[line_a, line_b],
                optical_transport_spectrum=spectrum,
            )
            channels.append(channel)

    digital_block = OpticalDigitalServiceBlockInactive.new(
        subscription_id=subscription_id,
        optical_digital_service_client_ports=[client_a, client_b],
        optical_digital_service_transport_channels=channels,
    )
    populate_optical_digital_service_block(
        digital_block,
        optical_digital_service_name,
        optical_digital_service_speed,
        optical_digital_service_type,
    )
    return digital_block


def has_new_channels_with_sections(block: OpticalDigitalServiceBlockProvisioning) -> bool:
    """Return whether the block holds service-owned channels with deployed sections.

    Args:
        block: The Optical Digital Service block to inspect.

    Returns:
        True when at least one new (service-owned) channel has spectrum sections.
    """
    return any(
        is_new_channel(channel, block) and channel.optical_transport_spectrum.optical_spectrum_sections
        for channel in block.optical_digital_service_transport_channels
    )


def _channel_endpoints(
    block: OpticalDigitalServiceBlockProvisioning,
) -> tuple[
    list[
        tuple[
            AnyOpticalNodeBlockProvisioningUnion,
            tuple[str, ...],
            tuple[Frequency, ...],
            tuple[str, ...],
            tuple[str, ...],
        ]
    ],
    list[tuple[AnyOpticalNodeBlockProvisioningUnion, str, str, OpticalDigitalServiceSpeed]],
    list[tuple[AnyOpticalNodeBlockProvisioningUnion, str, list[str], str]],
]:
    """Collect the per-side device parameters of a digital service block.

    Args:
        block: The Optical Digital Service block in the state.

    Returns:
        A triple of line-side tuples ``(node, port_names, frequencies, modes,
        descriptions)`` per endpoint host, client-side tuples ``(node,
        port_name, description, speed)`` per client port, and cross-connect
        tuples ``(node, client_name, line_names, description)`` per endpoint host.
    """
    service_name = block.optical_digital_service_name
    speed = block.optical_digital_service_speed
    new_channels = [ch for ch in block.optical_digital_service_transport_channels if is_new_channel(ch, block)]
    line_channels = new_channels or list(block.optical_digital_service_transport_channels)

    line_sides: dict[str, list[Any]] = {}
    for channel in line_channels:
        spectrum_name = channel.optical_transport_spectrum.optical_spectrum_name or service_name
        for line_port in channel.optical_transport_line_ports:
            host = cast(AnyOpticalNodeBlockProvisioningUnion, line_port.optical_port_host_node)
            key = str(host.subscription_instance_id)
            entry = line_sides.setdefault(key, [host, [], [], [], []])
            entry[1].append(line_port.optical_port_name)
            entry[2].append(channel.optical_transport_central_frequency)
            entry[3].append(channel.optical_transport_mode)
            entry[4].append(spectrum_name)

    clients = [
        (
            cast(AnyOpticalNodeBlockProvisioningUnion, port.optical_port_host_node),
            port.optical_port_name,
            port.optical_port_description or service_name,
            speed,
        )
        for port in block.optical_digital_service_client_ports
    ]

    xconns: dict[str, list[Any]] = {}
    for channel in block.optical_digital_service_transport_channels:
        for index, client_port in enumerate(block.optical_digital_service_client_ports):
            host = cast(AnyOpticalNodeBlockProvisioningUnion, client_port.optical_port_host_node)
            key = str(host.subscription_instance_id)
            entry = xconns.setdefault(key, [host, client_port.optical_port_name, [], service_name])
            entry[2].append(channel.optical_transport_line_ports[index].optical_port_name)
    line_side_list: list[
        tuple[
            AnyOpticalNodeBlockProvisioningUnion,
            tuple[str, ...],
            tuple[Frequency, ...],
            tuple[str, ...],
            tuple[str, ...],
        ]
    ] = [
        (
            cast(AnyOpticalNodeBlockProvisioningUnion, entry[0]),
            tuple(cast(list[str], entry[1])),
            tuple(cast(list[Frequency], entry[2])),
            tuple(cast(list[str], entry[3])),
            tuple(cast(list[str], entry[4])),
        )
        for entry in line_sides.values()
    ]
    xconn_list: list[tuple[AnyOpticalNodeBlockProvisioningUnion, str, list[str], str]] = [
        (
            cast(AnyOpticalNodeBlockProvisioningUnion, entry[0]),
            cast(str, entry[1]),
            cast(list[str], entry[2]),
            cast(str, entry[3]),
        )
        for entry in xconns.values()
    ]
    return (line_side_list, clients, xconn_list)


@step("Configuring the line ports on the transponders")
def configure_optical_digital_line_ports(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Configure the line transceivers of the new transport channels on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. Reused channels are skipped: their line
    ports already carry a service.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    line_sides, _, _ = _channel_endpoints(block)
    _ensure_transponder_ports(
        [
            port
            for channel in block.optical_digital_service_transport_channels
            for port in channel.optical_transport_line_ports
        ]
    )
    results = {}
    for host, port_names, frequencies, modes, descriptions in line_sides:
        results[_host_label(host)] = configure_line_transceivers(host, port_names, frequencies, modes, descriptions)
    return {"configuration_results": results}


@step("Configuring the client ports on the transponders")
def configure_optical_digital_client_ports(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Configure the client ports of the digital service on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    _, clients, _ = _channel_endpoints(block)
    _ensure_transponder_ports(list(block.optical_digital_service_client_ports))
    results = {}
    for host, port_name, description, speed in clients:
        results[_host_label(host)] = configure_transceiver_client(host, port_name, description, speed)
    return {"configuration_results": results}


@step("Configuring the cross-connects in the transponders")
def configure_optical_digital_crossconnects(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Configure the transponder cross-connects between client and line ports.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    _, _, xconns = _channel_endpoints(block)
    _ensure_transponder_ports(list(block.optical_digital_service_client_ports))
    results = {}
    for host, client_name, line_names, description in xconns:
        results[_host_label(host)] = configure_transponder_crossconnect(host, client_name, line_names, description)
    return {"configuration_results": results}


def _carrier_of_channel(channel: OpticalTransportChannelBlockProvisioning) -> tuple[Frequency, Bandwidth]:
    """Return the ``(central frequency, signal bandwidth)`` carrier of a transport channel.

    The signal bandwidth is read from the device hosting the first line port of
    the channel.

    Args:
        channel: The transport channel block.

    Returns:
        The carrier of the channel.
    """
    line_port = channel.optical_transport_line_ports[0]
    host = cast(AnyOpticalNodeBlockProvisioningUnion, line_port.optical_port_host_node)
    bandwidth = get_signal_bandwidth(host, line_port.optical_port_name)
    return (channel.optical_transport_central_frequency, bandwidth)


@step("Provisioning optical spectrum sections of the transport channels")
def provision_optical_digital_sections(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Deploy the optical circuit of every section of the new transport channels.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The device push is idempotent (circuits
    are found or created), so the step is shared by the shipped create and
    reconcile workflows. Reused channels are skipped: their circuits already exist.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    service_name = block.optical_digital_service_name
    results: dict[str, Any] = {}
    for channel in block.optical_digital_service_transport_channels:
        if not is_new_channel(channel, block):
            continue
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name or service_name
        carrier = _carrier_of_channel(channel)
        circuit_identifier = str(spectrum.subscription_instance_id)
        for section in spectrum.optical_spectrum_sections:
            src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            key = f"{spectrum_name} {src_node.management.optical_module_node_fqdn}"
            results[key] = deploy_optical_circuit(
                cast(AnyOpticalNodeBlockProvisioningUnion, src_node),
                section,
                spectrum_name,
                spectrum.optical_spectrum_passband,
                carrier,
                label=service_name,
                circuit_identifier=circuit_identifier,
            )
    return {"configuration_results": results}


@step("Updating the available passbands of the OLS ports in the paths")
def refresh_optical_digital_used_passbands(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Refresh the used passbands of the OLS ports of the new transport channels.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The ports owned by the digital service
    are refreshed in the returned block, which the following save step persists;
    the foreign ports (the express line ports owned by the pipe subscriptions)
    are persisted under their own owner subscription by this step. Reused
    channels are skipped: their passbands are unchanged.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    for channel in block.optical_digital_service_transport_channels:
        if not is_new_channel(channel, block):
            continue
        foreign_ports = update_used_passbands(channel.optical_transport_spectrum)
        save_foreign_passband_ports(foreign_ports)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


@step("Appending the service name to the labels of the reused channels")
def append_reused_channel_labels(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Append the service name to the circuit labels of the reused channels.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. Channels owned by the service itself are
    skipped: their labels were set at deployment time.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    service_name = block.optical_digital_service_name
    results: dict[str, Any] = {}
    for channel in block.optical_digital_service_transport_channels:
        if is_new_channel(channel, block):
            continue
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name or service_name
        circuit_identifier = str(spectrum.subscription_instance_id)
        for section in spectrum.optical_spectrum_sections:
            src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            key = f"{spectrum_name} {src_node.management.optical_module_node_fqdn}"
            results[key] = append_optical_circuit_label(
                cast(AnyOpticalNodeBlockProvisioningUnion, src_node),
                section,
                spectrum_name,
                spectrum.optical_spectrum_passband,
                service_name,
                circuit_identifier=circuit_identifier,
            )
    return {"configuration_results": results}


@step("Setting the transmitted optical power to match the line system target")
def align_optical_digital_tx_power(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Align the transponder transmit power to the FlexILS receive target.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. For every channel with a FlexILS
    section, the received power delta of the tributary port is measured; when it
    falls outside ``[0, 1.5]`` dB the transmit power of the corresponding
    transponder line port is adjusted and the delta re-measured. Channels
    without a FlexILS section are skipped.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    results: dict[str, Any] = {}
    for channel in block.optical_digital_service_transport_channels:
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name or block.optical_digital_service_name
        circuit_identifier = str(spectrum.subscription_instance_id)
        flexils_section = next(
            (
                section
                for section in spectrum.optical_spectrum_sections
                if (
                    section.optical_spectrum_section_add_drop_ports[
                        0
                    ].optical_port_host_node.management.optical_module_node_vendor,
                    section.optical_spectrum_section_add_drop_ports[
                        0
                    ].optical_port_host_node.management.optical_module_node_platform,
                )
                == (Vendor.NOKIA, Platform.FLEXILS)
            ),
            None,
        )
        if flexils_section is None:
            continue
        line_ports = channel.optical_transport_line_ports
        for index, trib_port in enumerate(flexils_section.optical_spectrum_section_add_drop_ports):
            trib_node = cast(AnyOpticalNodeBlockProvisioningUnion, trib_port.optical_port_host_node)
            db_from_target = delta_rx_power_vs_target(trib_node, spectrum_name, circuit_identifier)
            if 0.0 <= db_from_target <= 1.5:  # noqa: PLR2004
                results[f"{_host_label(trib_node)} {trib_port.optical_port_name}"] = (
                    f"P_rx_measured - P_rx_target = {db_from_target} dB"
                )
                continue
            trx_line_port = line_ports[index]
            if trx_line_port.optical_port_role is OpticalPortRole.COHERENT_PLUGGABLE:
                msg = "Coherent-pluggable-hosted ports are modelled but their device push is not implemented yet"
                raise NotImplementedError(msg)
            trx_node = cast(AnyOpticalNodeBlockProvisioningUnion, trx_line_port.optical_port_host_node)
            trx_port_name = trx_line_port.optical_port_name
            results[f"{_host_label(trx_node)} {trx_port_name}"] = align_tx_power_to_target(
                trx_node, trx_port_name, db_from_target
            )
            sleep(5)
            db_from_target = delta_rx_power_vs_target(trib_node, spectrum_name, circuit_identifier)
            results[f"{_host_label(trib_node)} {trib_port.optical_port_name}"] = (
                f"P_rx_measured - P_rx_target = {db_from_target} dB"
            )
    return {"configuration_results": results}


@step("Verifying the transponder line ports")
def verify_optical_digital_line_ports(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Verify the line transceiver configuration of the transport channels on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is read-only.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    line_sides, _, _ = _channel_endpoints(block)
    _ensure_transponder_ports(
        [
            port
            for channel in block.optical_digital_service_transport_channels
            for port in channel.optical_transport_line_ports
        ]
    )
    for host, port_names, frequencies, modes, descriptions in line_sides:
        validate_trx_line(host, port_names, frequencies, modes, descriptions)
    return {}


@step("Verifying the transponder client ports")
def verify_optical_digital_client_ports(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Verify the client port configuration of the digital service on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is read-only.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    _, clients, _ = _channel_endpoints(block)
    _ensure_transponder_ports(list(block.optical_digital_service_client_ports))
    for host, port_name, description, speed in clients:
        validate_trx_client(host, port_name, description, speed)
    return {}


@step("Verifying the transponder cross-connects")
def verify_optical_digital_crossconnects(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Verify the transponder cross-connects between client and line ports on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is read-only.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    _, _, xconns = _channel_endpoints(block)
    _ensure_transponder_ports(list(block.optical_digital_service_client_ports))
    for host, client_name, line_names, description in xconns:
        validate_trx_crossconnect(host, client_name, line_names, description)
    return {}


@step("Verifying the optical sections of the transport channels")
def verify_optical_digital_sections(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Verify the optical circuit of every section of the transport channels on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is read-only.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    service_name = block.optical_digital_service_name
    for channel in block.optical_digital_service_transport_channels:
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name or service_name
        carrier = _carrier_of_channel(channel)
        circuit_identifier = str(spectrum.subscription_instance_id)
        for section in spectrum.optical_spectrum_sections:
            src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            validate_optical_circuit(
                cast(AnyOpticalNodeBlockProvisioningUnion, src_node),
                section,
                spectrum_name,
                spectrum.optical_spectrum_passband,
                carrier,
                service_name,
                circuit_identifier=circuit_identifier,
            )
    return {}


@step("Modifying the optical sections of the transport channels")
def modify_optical_digital_sections(
    optical_module_block: OpticalDigitalServiceBlockInactive,
    old_passbands: list[Passband],
) -> State:
    """Modify the optical circuit of every section of the transport channels on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The new passbands drive the carriers;
    the old passbands locate the existing circuits on the devices.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
        old_passbands: The passbands of the channels before the modification.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    service_name = block.optical_digital_service_name
    results: dict[str, Any] = {}
    for channel, old_passband in zip(block.optical_digital_service_transport_channels, old_passbands, strict=True):
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name or service_name
        carrier = _carrier_of_channel(channel)
        circuit_identifier = str(spectrum.subscription_instance_id)
        for section in spectrum.optical_spectrum_sections:
            src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            key = f"{spectrum_name} {src_node.management.optical_module_node_fqdn}"
            results[key] = modify_optical_circuit(
                cast(AnyOpticalNodeBlockProvisioningUnion, src_node),
                section,
                optical_spectrum_name=spectrum_name,
                passband=spectrum.optical_spectrum_passband,
                carrier=carrier,
                label=service_name,
                old_passband=old_passband,
                circuit_identifier=circuit_identifier,
            )
    return {"configuration_results": results}


@step("Factory resetting the transponder cross-connects")
def factory_reset_optical_digital_crossconnects(
    optical_module_block: OpticalDigitalServiceBlockInactive,
) -> State:
    """Delete the transponder cross-connects of the digital service from the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    _ensure_transponder_ports(list(block.optical_digital_service_client_ports))
    results = {}
    for client_port in block.optical_digital_service_client_ports:
        host = cast(AnyOpticalNodeBlockProvisioningUnion, client_port.optical_port_host_node)
        results[_host_label(host)] = delete_transponder_crossconnect(host, client_port.optical_port_name)
    return {"configuration_results": results}


@step("Factory resetting the transponder client ports")
def factory_reset_optical_digital_clients(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Factory reset the client ports of the digital service on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    _ensure_transponder_ports(list(block.optical_digital_service_client_ports))
    results = {}
    for client_port in block.optical_digital_service_client_ports:
        host = cast(AnyOpticalNodeBlockProvisioningUnion, client_port.optical_port_host_node)
        results[_host_label(host)] = factory_reset_transponder_client(host, client_port.optical_port_name)
    return {"configuration_results": results}


@step("Factory resetting the transponder line ports")
def factory_reset_optical_digital_lines(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Factory reset the line ports of the transport channels on the devices.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is a no-op when the service is
    not the last client of its channels: shared line ports must stay configured
    for the remaining services.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    if not is_last_client_for_channels(list(block.optical_digital_service_transport_channels)):
        return {"configuration_results": {}}
    _ensure_transponder_ports(
        [
            port
            for channel in block.optical_digital_service_transport_channels
            for port in channel.optical_transport_line_ports
        ]
    )
    results: dict[str, Any] = {}
    by_host: dict[str, tuple[Any, list[str]]] = {}
    for channel in block.optical_digital_service_transport_channels:
        for line_port in channel.optical_transport_line_ports:
            host = cast(AnyOpticalNodeBlockProvisioningUnion, line_port.optical_port_host_node)
            key = str(host.subscription_instance_id)
            entry = by_host.setdefault(key, (host, []))
            port_name = line_port.optical_port_name
            if port_name not in entry[1]:
                entry[1].append(port_name)
    for host, port_names in by_host.values():
        results[_host_label(host)] = factory_reset_transponder_lines(host, port_names)
    return {"configuration_results": results}


@step("Deleting the optical sections of the transport channels")
def delete_optical_digital_sections(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Delete the optical circuit of every section of the transport channels.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is a no-op when the service is
    not the last client of its channels: shared circuits must stay deployed for
    the remaining services. The teardown, including the OEL of each source node,
    is delegated to the shared spectrum helper
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.delete_optical_spectrum_sections`.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    if not is_last_client_for_channels(list(block.optical_digital_service_transport_channels)):
        return {"configuration_results": {}}
    results: dict[str, Any] = {}
    for channel in block.optical_digital_service_transport_channels:
        spectrum = channel.optical_transport_spectrum
        spectrum_name = spectrum.optical_spectrum_name or block.optical_digital_service_name
        results.update(
            delete_optical_spectrum_sections(
                list(spectrum.optical_spectrum_sections),
                spectrum.optical_spectrum_passband,
                spectrum_name,
                str(spectrum.subscription_instance_id),
            )
        )
    return {"configuration_results": results}


@step("Updating the used passbands after teardown")
def refresh_optical_digital_passbands_after_teardown(
    optical_module_block: OpticalDigitalServiceBlockInactive,
) -> State:
    """Refresh the used passbands of the OLS ports after the circuits are deleted.

    Operates only on the Optical Digital Service block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The step is a no-op when the service is
    not the last client of its channels. The refreshed block is returned so the
    following save step persists it; foreign ports are persisted under their own
    owner subscription by this step.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    if not is_last_client_for_channels(list(block.optical_digital_service_transport_channels)):
        return {OPTICAL_MODULE_BLOCK_STATE_KEY: block}
    for channel in block.optical_digital_service_transport_channels:
        foreign_ports = update_used_passbands(channel.optical_transport_spectrum)
        save_foreign_passband_ports(foreign_ports)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


#: Provisioning steps shared by the create and reconcile workflows: the
#: idempotent device push of the line/client/cross-connect configuration and of
#: the optical circuits. Every step is block-level and operates on the block in
#: the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = (
    begin
    >> configure_optical_digital_line_ports
    >> configure_optical_digital_client_ports
    >> configure_optical_digital_crossconnects
    >> provision_optical_digital_sections
)

#: Verification steps shared by the validate and reconcile workflows. Every
#: step is block-level, read-only, and operates on the block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
VERIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = (
    begin
    >> verify_optical_digital_line_ports
    >> verify_optical_digital_client_ports
    >> verify_optical_digital_crossconnects
    >> verify_optical_digital_sections
)


__all__ = [
    "DIGITAL_ENDPOINT_ROLES",
    "DIRECT_CONNECTION",
    "PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS",
    "VERIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS",
    "ChannelReuseGroup",
    "align_optical_digital_tx_power",
    "append_reused_channel_labels",
    "build_optical_digital_service_block",
    "channel_name_in_use",
    "channel_spare_capacity",
    "configure_optical_digital_client_ports",
    "configure_optical_digital_crossconnects",
    "configure_optical_digital_line_ports",
    "delete_optical_digital_sections",
    "factory_reset_optical_digital_clients",
    "factory_reset_optical_digital_crossconnects",
    "factory_reset_optical_digital_lines",
    "get_transceiver_capacity_from_mode",
    "has_flexils_sections",
    "has_new_channels_with_sections",
    "is_last_client_for_channels",
    "is_new_channel",
    "is_packet_node_host",
    "line_port_selector",
    "load_optical_digital_service_block",
    "modify_optical_digital_sections",
    "new_optical_digital_service_subscription",
    "optical_digital_endpoint_selector",
    "optical_digital_service_block_from_state",
    "optical_digital_service_subscription_description",
    "populate_optical_digital_service_block",
    "port_ids_used_by_digital_services",
    "provision_optical_digital_sections",
    "refresh_optical_digital_passbands_after_teardown",
    "refresh_optical_digital_used_passbands",
    "resolve_channels_by_names",
    "reusable_channel_groups",
    "set_optical_digital_service_subscription_description",
    "unused_coherent_pluggable_selector",
    "verify_optical_digital_client_ports",
    "verify_optical_digital_crossconnects",
    "verify_optical_digital_line_ports",
    "verify_optical_digital_sections",
]
