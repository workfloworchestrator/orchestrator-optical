"""Shared helpers for the Optical Spectrum Service workflows.

This module ports the legacy optical spectrum path engine and the optical
device selectors to the generalized Optical Node/Port model:

- the path engine works on the ``OpticalFiberSpan`` subscriptions (product
  type ``ProductType.OPTICAL_FIBER_SPAN``) whose ``optical_pipe_terminations``
  are the two ``OlsLinePortBlock`` instances connecting two Optical Nodes;
  only fiber spans are considered, fiber patches are not part of the graph;
- optical devices are the ``AbstractOpticalNodeBlock`` instances (any vendor
  block), and device types are replaced by the ``OpticalNodeRole`` of the
  hosting node (``OpticalNodeRole.ROADM``, ``OpticalNodeRole.AMPLIFIER``,
  ``OpticalNodeRole.TRANSPONDER``, ``OpticalNodeRole.TRANSPONDER_XOADM``);
- platform checks are replaced by the ``Vendor`` enum dispatched with
  ``vendor_of``;
- the old ``used_passbands`` of the optical ports is the
  ``optical_passbands`` of the ``AbstractOpticalOlsPortBlock`` instances;
- the old device-specific port selectors are ported to selectors that work on
  the Optical Node subscriptions (``optical_node_selector_of_roles``,
  ``optical_client_port_selector``, ``optical_line_port_selector``,
  ``unused_optical_client_port_selector``, ``unused_optical_line_port_selector``,
  ``transceiver_mode_selector``).
"""

from collections import deque
from typing import Annotated, cast
from uuid import UUID

from pydantic import Field
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice, choice_list
from structlog import get_logger

from orchestrator.core.db import SubscriptionTable
from orchestrator.core.db.models import SubscriptionInstanceValueTable
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.hal.optical_node import Vendor, retrieve_ports_spectral_occupations, vendor_of
from orchestrator.optical.hal.optical_port import (
    get_device_client_ports_names,
    get_device_line_ports_names,
    get_device_ports_names,
    retrieve_transceiver_modes,
)
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockInactive,
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node.abstracts import AbstractOpticalNode
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpan
from orchestrator.optical.utils.custom_types.frequencies import Passband, disjoint_intervals_overlap_search
from orchestrator.optical.workflows.shared import (
    subscription_instance_values_by_block_type_depending_on_instance_id,
    subscriptions_by_product_type,
    subscriptions_by_product_type_and_instance_value,
)

logger = get_logger(__name__)

OPTICAL_NODE_PRODUCT_TYPES = [
    ProductType.OPTICAL_NODE_NOKIA_FLEXILS.value,
    ProductType.OPTICAL_NODE_NOKIA_GROOVE_G30.value,
    ProductType.OPTICAL_NODE_NOKIA_GX_G42.value,
]

# ``AbstractOpticalNodeBlockInactive.subscription_instance_id``
Node = UUIDstr
# ``AbstractOpticalOlsPortBlockInactive.subscription_instance_id``
Port = UUIDstr
Edge = tuple[Port, Port]
NeighborConnection = tuple[Node, Edge]
Graph = dict[Node, list[NeighborConnection]]  # {node_id: [(neighbor_id, (port_a_id, port_b_id)), ...]}
Path = list[Port]  # list of ``AbstractOpticalOlsPortBlockInactive.subscription_instance_id``


class NoOpticalPathFoundError(RuntimeError):
    """Raised when no valid optical path exists between the specified devices or ports."""

    def __init__(self, src: str, dst: str):
        """Initialize the error with the source and destination of the missing path."""
        msg = f"No valid optical path exists between source node '{src}' and destination node '{dst}'."
        super().__init__(msg)


def _node_pqdn(node: AbstractOpticalNodeBlockInactive) -> str:
    """Return the pqdn of an Optical Node block, tolerating unset values."""
    return str(node.pqdn) if node.pqdn is not None else "<unknown>"


def _load_ols_port(port_id: UUIDstr) -> AbstractOpticalOlsPortBlockInactive:
    """Load an OLS Optical Port block from its subscription instance id."""
    return cast(AbstractOpticalOlsPortBlockInactive, ProductBlockModel.from_db(UUID(str(port_id))))


def _load_port(port_id: UUIDstr) -> AbstractOpticalPortBlockInactive:
    """Load an Optical Port block from its subscription instance id."""
    return cast(AbstractOpticalPortBlockInactive, ProductBlockModel.from_db(UUID(str(port_id))))


def find_constrained_shortest_path(
    src_device: AbstractOpticalNodeBlockInactive,
    dst_device: AbstractOpticalNodeBlockInactive,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> list[tuple[AbstractOpticalOlsPortBlockInactive, AbstractOpticalOlsPortBlockInactive]]:
    """Find shortest path between optical devices respecting given constraints.

    Args:
        src_device: Source optical node
        dst_device: Destination optical node
        passband: Passband to fit in the fiber spans
        exclude_node_sub_ids: Subscription ids of the nodes to exclude from the path
        exclude_span_sub_ids: Subscription ids of the fiber spans to exclude from the path

    Returns:
        List of port pairs forming the shortest path

    Raises:
        ValueError: If source or destination devices are invalid
        RuntimeError: If no valid path exists between devices
    """
    if not src_device or not dst_device:
        msg = "Source and destination devices must be specified"
        raise ValueError(msg)

    exclude_node_sub_ids = exclude_node_sub_ids or []
    exclude_span_sub_ids = exclude_span_sub_ids or []

    # retrieve all active fiber subscriptions
    fiber_subscriptions = subscriptions_by_product_type(
        ProductType.OPTICAL_FIBER_SPAN.value, [SubscriptionLifecycle.ACTIVE]
    )
    active_fibers = [
        OpticalFiberSpan.from_subscription(sub.subscription_id).optical_pipe for sub in fiber_subscriptions
    ]

    # filter out fibers that are excluded by the constraints
    exclude_node_sub_id_set = set(exclude_node_sub_ids)
    exclude_span_sub_id_set = set(exclude_span_sub_ids)

    def does_fiber_pass_exclusion(fiber):
        if str(fiber.owner_subscription_id) in exclude_span_sub_id_set:
            return False
        for port in fiber.optical_pipe_terminations:
            node = port.optical_port_host_node
            if str(node.owner_subscription_id) in exclude_node_sub_id_set:
                return False
            if vendor_of(node) == Vendor.GX_G42:
                # GX G42 ports are not supported in this path computation
                return False
            if vendor_of(node) == Vendor.GROOVE_G30 and "." not in (port.optical_port_name or ""):
                # all ports with a dot are on OLS cards
                # all ports without a dot are on transponder cards and must be excluded
                return False
            if disjoint_intervals_overlap_search(port.optical_passbands, passband):
                return False
        return True

    sifted_fibers = list(filter(does_fiber_pass_exclusion, active_fibers))

    # convert the fibers into an adjacency list
    graph: dict[Node, list[NeighborConnection]] = {}
    for fiber in sifted_fibers:
        a_port = fiber.optical_pipe_terminations[0]
        z_port = fiber.optical_pipe_terminations[1]
        a_node_sub_id = str(a_port.optical_port_host_node.owner_subscription_id)
        z_node_sub_id = str(z_port.optical_port_host_node.owner_subscription_id)
        if a_node_sub_id not in graph:
            graph[a_node_sub_id] = []
        if z_node_sub_id not in graph:
            graph[z_node_sub_id] = []
        graph[a_node_sub_id].append((z_node_sub_id, (a_port, z_port)))
        graph[z_node_sub_id].append((a_node_sub_id, (z_port, a_port)))

    # find the shortest path between the two devices with breadth-first search
    def bfs():
        src = str(src_device.owner_subscription_id)
        dst = str(dst_device.owner_subscription_id)
        visited_nodes = set()
        node_path_tuple = (src, [])
        queue = deque([node_path_tuple])
        while queue:
            current_node, current_path = queue.popleft()

            if current_node in visited_nodes:
                continue

            visited_nodes.add(current_node)

            if current_node == dst:
                return current_path

            for adjacent_node, fiber_ports in graph.get(current_node, []):
                new_path = current_path.copy()
                new_path.extend(fiber_ports)
                queue.append((adjacent_node, new_path))
        return None

    list_of_ports = bfs()
    if list_of_ports is None:
        msg = (
            f"No valid path exists between devices {src_device.owner_subscription_id} "
            f"and {dst_device.owner_subscription_id}"
        )
        raise RuntimeError(msg)

    return list_of_ports


def build_constrained_graph_from_active_fibers(
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> Graph:
    """Build a constrained graph representation of the active fiber spans.

    The graph is built from the active ``OpticalFiberSpan`` subscriptions: each
    node in the graph is an Optical Node block and each edge is a fiber span
    connecting two of its ``OlsLinePortBlock`` terminations.

    Args:
        passband: The passband used to filter fibers based on overlapping intervals.
        exclude_node_sub_ids: A list of subscription ids of nodes to exclude.
        exclude_span_sub_ids: A list of subscription ids of spans to exclude.

    Returns:
        An adjacency list representation of the graph where keys are the
        ``subscription_instance_id`` of the Optical Nodes and values are lists
        of tuples containing a connected node id and the pair of port ids of
        the fiber span, e.g. ``{node_A: [(node_B, (port_A2B, port_B2A)), ...]}``.

    Notes:
        - Spans are excluded if their owner subscription id matches any in ``exclude_span_sub_ids``.
        - Spans are excluded if any of their terminations belong to nodes with subscription ids in
          ``exclude_node_sub_ids``.
        - Spans are excluded if their terminations overlap with the provided passband.
        - Spans connected to transponder cards (ports without a dot in their name on Groove G30
          nodes) are excluded, as well as spans terminated on GX G42 nodes.
    """
    # retrieve all active fiber subscriptions
    fiber_subscriptions = subscriptions_by_product_type(
        ProductType.OPTICAL_FIBER_SPAN.value, [SubscriptionLifecycle.ACTIVE]
    )
    active_fibers = [
        OpticalFiberSpan.from_subscription(sub.subscription_id).optical_pipe for sub in fiber_subscriptions
    ]

    # filter out fibers that are excluded by the constraints
    exclude_node_sub_id_set = set(exclude_node_sub_ids or [])
    exclude_span_sub_id_set = set(exclude_span_sub_ids or [])
    logger.debug(
        "Exclusion sets for path computation",
        exclude_node_sub_ids=exclude_node_sub_id_set,
        exclude_span_sub_ids=exclude_span_sub_id_set,
    )

    def does_fiber_pass_exclusion(fiber):
        if str(fiber.owner_subscription_id) in exclude_span_sub_id_set:
            return False
        for port in fiber.optical_pipe_terminations:
            node = port.optical_port_host_node
            if str(node.owner_subscription_id) in exclude_node_sub_id_set:
                return False
            if disjoint_intervals_overlap_search(port.optical_passbands, passband):
                return False
            if vendor_of(node) == Vendor.GROOVE_G30 and "." not in (port.optical_port_name or ""):
                # all ports with a dot are on OLS cards
                # all ports without a dot are on transponder cards and must be excluded
                return False
            if vendor_of(node) == Vendor.GX_G42:
                return False
        return True

    sifted_fibers = list(filter(does_fiber_pass_exclusion, active_fibers))
    logger.debug("Graph edges for path computation", sifted_fibers=[f.optical_pipe_identifier for f in sifted_fibers])

    # convert the fibers into an adjacency list
    graph: dict[Node, list[NeighborConnection]] = {}
    for fiber in sifted_fibers:
        port_a = fiber.optical_pipe_terminations[0]
        port_b = fiber.optical_pipe_terminations[1]
        id_port_a = str(port_a.subscription_instance_id)
        id_port_b = str(port_b.subscription_instance_id)
        id_node_a = str(port_a.optical_port_host_node.subscription_instance_id)
        id_node_b = str(port_b.optical_port_host_node.subscription_instance_id)
        if id_node_a not in graph:
            graph[id_node_a] = []
        if id_node_b not in graph:
            graph[id_node_b] = []
        graph[id_node_a].append((id_node_b, (id_port_a, id_port_b)))
        graph[id_node_b].append((id_node_a, (id_port_b, id_port_a)))

    return graph


def all_valid_shortest_paths_between_oadms(
    src_optical_device_block_id: UUIDstr,
    dst_optical_device_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> list[Path]:
    """Find all shortest paths between two Optical Add-Drop Multiplexers.

    Args:
        src_optical_device_block_id: Subscription instance id of the source Optical Node block.
        dst_optical_device_block_id: Subscription instance id of the destination Optical Node block.
        passband: The passband configuration for the optical path.
        exclude_node_sub_ids: A list of node subscription ids to exclude from the path.
        exclude_span_sub_ids: A list of span subscription ids to exclude from the path.

    Returns:
        A list of all shortest paths between the two nodes.
    """
    fiber_graph = build_constrained_graph_from_active_fibers(passband, exclude_node_sub_ids, exclude_span_sub_ids)
    return compute_all_shortest_paths(fiber_graph, src_optical_device_block_id, dst_optical_device_block_id)


def all_valid_shortest_paths_between_trxs(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> list[Path]:
    """Find all shortest paths between two transponder ports, considering the specified passband and constraints."""
    src_add_drop_port, dst_add_drop_port = find_add_drop_ports(src_trx_port_block_id, dst_trx_port_block_id)
    if (
        str(src_add_drop_port.subscription_instance_id) == dst_trx_port_block_id
        and str(dst_add_drop_port.subscription_instance_id) == src_trx_port_block_id
    ):
        # transponder ports are directly connected to each other
        return [[]]

    src_ols_dev_id = str(src_add_drop_port.optical_port_host_node.subscription_instance_id)
    dst_ols_dev_id = str(dst_add_drop_port.optical_port_host_node.subscription_instance_id)
    paths = all_valid_shortest_paths_between_oadms(
        src_ols_dev_id,
        dst_ols_dev_id,
        passband,
        exclude_node_sub_ids,
        exclude_span_sub_ids,
    )

    valid_paths = []
    for path in paths:
        path.insert(0, str(src_add_drop_port.subscription_instance_id))
        path.append(str(dst_add_drop_port.subscription_instance_id))
        if are_trx_and_oadm_in_the_same_shelf_for_g30s_in_path(path):
            valid_paths.append(path)

    if not valid_paths:
        raise NoOpticalPathFoundError(
            src=src_trx_port_block_id,
            dst=dst_trx_port_block_id,
        )

    return valid_paths


def are_trx_and_oadm_in_the_same_shelf_for_g30s_in_path(path: Path) -> bool:
    """Validate whether the given path represents a valid connection between optical device ports.

    The function iterates through the path and checks if ports on the same Groove G30 are on the
    same shelf and slot. It skips every second port in the path and performs the validation
    only for ports associated with Groove G30 nodes.

    Args:
        path: A sequence of optical ports represented as Path objects.

    Returns:
        True if the path is valid and all relevant ports are connected on the same
        Groove G30 shelf and slot; False otherwise.
    """
    for i in range(len(path) - 1):
        if i % 2 == 1:
            continue

        port_i = _load_ols_port(path[i])
        if vendor_of(port_i.optical_port_host_node) != Vendor.GROOVE_G30:
            continue

        ii = i + 1
        port_ii = _load_ols_port(path[ii])

        def _(g30_port_name: str) -> tuple[int, int]:
            ids = g30_port_name.rsplit("-", maxsplit=1)[-1]  # port-1/3.3/1.1 --> 1/3.3/1.1
            shelf, slot, _ = ids.split("/")  # 1/3.3/1.1 --> 1, 3.3, 1.1
            if "." in slot:
                slot, _ = slot.split(".")  # 3.3 --> 3, 3
            return int(shelf), int(slot)

        if port_i.optical_port_name is None or port_ii.optical_port_name is None:
            return False
        shelf_i, slot_i = _(port_i.optical_port_name)
        shelf_ii, slot_ii = _(port_ii.optical_port_name)
        if shelf_i != shelf_ii or slot_i != slot_ii:
            # ports are not on the same G30 shelf and slot, so they are not connected
            return False

    return True


def find_add_drop_ports(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
) -> tuple[AbstractOpticalPortBlockInactive, AbstractOpticalPortBlockInactive]:
    """Retrieve the add/drop ports connected to the transponder/transceiver ports.

    Args:
        src_trx_port_block_id: Subscription instance id of the source transponder port block.
        dst_trx_port_block_id: Subscription instance id of the destination transponder port block.

    Returns:
        The add/drop ports terminating the fiber spans connected to the transponder ports.

    Raises:
        NoOpticalPathFoundError: If the add/drop ports cannot be found.
    """
    src_trx_port = _load_port(src_trx_port_block_id)
    dst_trx_port = _load_port(dst_trx_port_block_id)

    fiber_a = OpticalFiberSpan.from_subscription(src_trx_port.owner_subscription_id).optical_pipe
    fiber_b = OpticalFiberSpan.from_subscription(dst_trx_port.owner_subscription_id).optical_pipe

    src_add_drop_port: AbstractOpticalPortBlockInactive | None = None
    dst_add_drop_port: AbstractOpticalPortBlockInactive | None = None
    for t in fiber_a.optical_pipe_terminations:
        if t.subscription_instance_id != src_trx_port.subscription_instance_id:
            src_add_drop_port = t
            break
    for t in fiber_b.optical_pipe_terminations:
        if t.subscription_instance_id != dst_trx_port.subscription_instance_id:
            dst_add_drop_port = t
            break

    if src_add_drop_port is None or dst_add_drop_port is None:
        raise NoOpticalPathFoundError(src=src_trx_port_block_id, dst=dst_trx_port_block_id)

    return src_add_drop_port, dst_add_drop_port


def compute_all_shortest_paths(graph: Graph, src: Node, dst: Node) -> list[Path]:
    """Find all shortest paths from src to dst in a graph where path cost is the number of accumulated port pairs.

    Args:
        graph: Adjacency list representation of the graph, e.g.
            ``{node_A: [(node_B, (port_A2B, port_B2A)), (node_C, (port_A2C, port_C2A))], ...}``
        src: The starting node subscription instance id.
        dst: The destination node subscription instance id.

    Returns:
        A list of all shortest paths. Each path is a list of Optical Port subscription instance ids.

    Raises:
        NoOpticalPathFoundError: If no valid path exists between the source and destination nodes.
    """
    # Queue stores (current_node, src_to_current_node_path, current_path_length)
    # The path length is crucial for determining 'shortest' and 'equal cost'.
    queue = deque([(src, [], 0)])  # (node, src_to_node_path, hop_count)

    # Store the minimum distance found to a node so far.
    min_dist_to_node = {node: float("inf") for node in graph}
    min_dist_to_node[src] = 0

    # This will store all found shortest paths
    all_shortest_paths = []
    min_overall_path_length = float("inf")

    while queue:
        current_node, src_to_current_node_path, current_path_length = queue.popleft()

        # Pruning: If we've already found a shorter path to this node,
        # or if this path is already longer than the best path to the destination found so far,
        # then this path cannot be a shortest path.
        if current_path_length > min_dist_to_node[current_node]:
            continue
        if current_path_length > min_overall_path_length:
            continue  # This path is already longer than the shortest path we've found to destination.

        if current_node == dst:
            # If this is the first time we reach the destination, or it's an equally short path
            if current_path_length < min_overall_path_length:
                min_overall_path_length = current_path_length
                all_shortest_paths = [src_to_current_node_path]  # Start new list for shorter paths
            elif current_path_length == min_overall_path_length:
                all_shortest_paths.append(src_to_current_node_path)
            # We don't 'continue' here, as other paths might reach DST with the same length
            # from different branches.
            continue  # Important: don't process neighbors of the destination node

        for adjacent_node, fiber_ports in graph.get(current_node, []):
            # Calculate the new path length
            new_path_length = current_path_length + 1  # Every edge costs 1 hop

            # If this new path to adjacent_node is shorter than any previously found,
            # or if it's of equal length (meaning it's potentially another valid shortest path to 'adjacent_node'),
            # then we add it to the queue.
            if new_path_length < min_dist_to_node[adjacent_node]:
                min_dist_to_node[adjacent_node] = new_path_length
                src_to_adj_node_path = list(src_to_current_node_path)  # Create a true copy
                src_to_adj_node_path.extend(fiber_ports)
                queue.append((adjacent_node, src_to_adj_node_path, new_path_length))
            elif new_path_length == min_dist_to_node[adjacent_node]:
                # If we find an equally short path to 'adjacent_node', we must also explore it.
                # This is crucial for finding *all* shortest paths.
                src_to_adj_node_path = list(src_to_current_node_path)
                src_to_adj_node_path.extend(fiber_ports)
                queue.append((adjacent_node, src_to_adj_node_path, new_path_length))

    if not all_shortest_paths:
        raise NoOpticalPathFoundError(src=src, dst=dst)

    return all_shortest_paths


def human_readable_optical_spectrum_path_selector(
    paths: list[Path],
    prompt: str = "Select an optical path.",
) -> Choice:
    """Convert paths to string representations for the choice options."""
    paths_dict = {}
    for path in paths:
        human_readable_path = ""
        first_port = _load_ols_port(path[0])
        ne_name = _node_pqdn(first_port.optical_port_host_node)
        human_readable_path += f"{ne_name} ({first_port.optical_port_name}) ⇋ "

        for i in range(1, len(path) - 1):
            if i % 2 == 0:
                continue

            port_i = _load_ols_port(path[i])
            port_ii = _load_ols_port(path[i + 1])
            ne_name = _node_pqdn(port_i.optical_port_host_node)
            human_readable_path += f"{ne_name} ({port_i.optical_port_name} × {port_ii.optical_port_name}) ⇋ "  # noqa: RUF001

        last_port = _load_ols_port(path[-1])
        ne_name = _node_pqdn(last_port.optical_port_host_node)
        human_readable_path += f"{ne_name} ({last_port.optical_port_name})"

        path_subscription_ids = ";".join(str(port_id) for port_id in path)
        paths_dict[path_subscription_ids] = human_readable_path

    return Choice(prompt, zip(paths_dict.keys(), paths_dict.items(), strict=False))


def human_readable_transport_channel_path_selector(
    paths: list[Path],
    prompt: str = "Select an optical path.",
) -> Choice:
    """Convert paths to string representations for the choice options."""
    paths_dict = {}
    for path in paths:
        if path == []:
            paths_dict["direct_connection"] = "Direct connection between transceivers (no line system in between)"
            continue

        human_readable_path = ""
        for i in range(len(path) - 1):
            if i % 2 == 1:
                continue

            port_i = _load_ols_port(path[i])
            port_ii = _load_ols_port(path[i + 1])
            ne_name = _node_pqdn(port_i.optical_port_host_node)
            human_readable_path += f"{ne_name} ({port_i.optical_port_name} × {port_ii.optical_port_name}) ⇋ "  # noqa: RUF001
            # g30.na01 (port-1/3.1/1 x port-1/3.3/1.1) <-> flex.na01 (1-E1-1-T2A x 1-A-1-L1) <-> ...

        human_readable_path = human_readable_path.removesuffix(" ⇋ ")
        path_subscription_ids = ";".join(str(port_id) for port_id in path)
        paths_dict[path_subscription_ids] = human_readable_path

    return Choice(prompt, zip(paths_dict.keys(), paths_dict.items(), strict=False))


def transport_channel_path_selector(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
    prompt: str = "Select an optical path.",
) -> Choice:
    """Select an optical path between two transceiver port blocks based on the given parameters.

    The selected path MUST then be parsed using ``path.split(";")`` to obtain the sequence
    of subscription instance ids of the Optical Port blocks.

    Args:
        src_trx_port_block_id: The UUID of the source transceiver port block.
        dst_trx_port_block_id: The UUID of the destination transceiver port block.
        passband: The passband configuration for the optical path.
        exclude_node_sub_ids: A list of node subscription ids to exclude from the path. Defaults to an empty list.
        exclude_span_sub_ids: A list of span subscription ids to exclude from the path. Defaults to an empty list.
        prompt: A prompt message for the user to select an optical path. Defaults to "Select an optical path.".

    Returns:
        A Choice object containing the prompt and a list of valid optical paths represented as
        subscription ids and human-readable strings.
    """
    paths = all_valid_shortest_paths_between_trxs(
        src_trx_port_block_id,
        dst_trx_port_block_id,
        passband,
        exclude_node_sub_ids,
        exclude_span_sub_ids,
    )
    return human_readable_transport_channel_path_selector(paths, prompt)


def optical_spectrum_path_selector(
    src_optical_device_block_id: UUIDstr,
    dst_optical_device_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
    prompt: str = "Select an optical path.",
) -> Choice:
    """Select an optical path between two optical devices based on the given parameters.

    The selected path MUST then be parsed using ``path.split(";")`` to obtain the sequence
    of subscription instance ids of the Optical Port blocks.

    Args:
        src_optical_device_block_id: The UUID of the source optical device block.
        dst_optical_device_block_id: The UUID of the destination optical device block.
        passband: The passband configuration for the optical path.
        exclude_node_sub_ids: A list of node subscription ids to exclude from the path. Defaults to an empty list.
        exclude_span_sub_ids: A list of span subscription ids to exclude from the path. Defaults to an empty list.
        prompt: A prompt message for the user to select an optical path. Defaults to "Select an optical path.".

    Returns:
        A Choice object containing the prompt and a list of valid optical paths represented as
        subscription ids and human-readable strings.
    """
    paths = all_valid_shortest_paths_between_oadms(
        src_optical_device_block_id,
        dst_optical_device_block_id,
        passband,
        exclude_node_sub_ids,
        exclude_span_sub_ids,
    )
    return human_readable_optical_spectrum_path_selector(paths, prompt)


def store_list_of_ports_into_spectrum_sections(
    optical_path: list[UUIDstr],
    optical_spectrum: OpticalSpectrumBlockInactive | OpticalSpectrumBlockProvisioning,
) -> None:
    """Decompose a continuous list of optical ports into vendor-specific sections.

    The function groups the provided optical path into "sections" based on the vendor of the
    Optical Node hosting each port. Whenever the vendor changes between two adjacent ports in
    the path, a new section is started. Each section is then stored as an
    ``OpticalSpectrumSectionBlockInactive`` (or ``OpticalSpectrumSectionBlockProvisioning`` when
    the spectrum block is provisioning).

    For each section:
    - The first and last ports are designated as ``optical_spectrum_section_add_drop_ports``.
    - Any ports in between the first and last are stored in the ``optical_spectrum_section_express_ports`` field.

    Args:
        optical_path: A sequence of port UUIDs representing the full end-to-end optical route.
        optical_spectrum: The spectrum block domain model where the resulting sections will be appended.

    Returns:
        None: The function modifies the ``optical_spectrum`` object in place.
    """
    ports = [_load_ols_port(port_id) for port_id in optical_path]

    sections: list[list[AbstractOpticalOlsPortBlockInactive]] = []
    current_section = [ports[0]]
    previous_port = ports[0]
    for current_port in ports[1:]:
        if vendor_of(current_port.optical_port_host_node) != vendor_of(previous_port.optical_port_host_node):
            sections.append(current_section)
            current_section = []
        current_section.append(current_port)
        previous_port = current_port

    if current_section:
        sections.append(current_section)

    subscription = optical_spectrum.subscription
    if subscription is None:
        msg = "Optical spectrum block is not associated with a subscription"
        raise ValueError(msg)
    subscription_id = subscription.subscription_id
    if isinstance(optical_spectrum, OpticalSpectrumBlockProvisioning):
        optical_spectrum.optical_spectrum_sections = [
            OpticalSpectrumSectionBlockProvisioning.new(
                subscription_id=subscription_id,
                optical_spectrum_section_add_drop_ports=[section[0], section[-1]],
                optical_spectrum_section_express_ports=section[1:-1],
            )
            for section in sections
        ]
    else:
        optical_spectrum.optical_spectrum_sections = [
            OpticalSpectrumSectionBlockInactive.new(
                subscription_id=subscription_id,
                optical_spectrum_section_add_drop_ports=[section[0], section[-1]],
                optical_spectrum_section_express_ports=section[1:-1],
            )
            for section in sections
        ]


def update_used_passbands(optical_spectrum: OpticalSpectrumBlockProvisioning) -> None:
    """Refresh the ``optical_passbands`` of any Open Line System port in the path from the devices."""
    passbands_by_device: dict[str, dict[str, list[tuple[int, int]]]] = {}
    for section in optical_spectrum.optical_spectrum_sections:
        for port in section.optical_spectrum_section_express_ports:
            node = port.optical_port_host_node
            if node.optical_node_role not in (OpticalNodeRole.ROADM, OpticalNodeRole.TRANSPONDER_XOADM):
                continue
            if node.pqdn is None or port.optical_port_name is None:
                continue
            if node.pqdn not in passbands_by_device:
                passbands_by_device[node.pqdn] = retrieve_ports_spectral_occupations(node)
            port.optical_passbands = passbands_by_device[node.pqdn].get(port.optical_port_name, [])


def get_optical_node_subscriptions_by_roles(roles: list[OpticalNodeRole]) -> list[SubscriptionTable]:
    """Retrieve the subscriptions of the Optical Node products whose nodes have any of the given roles.

    Args:
        roles: The node roles to filter the Optical Node subscriptions by.

    Returns:
        A list of active Optical Node subscriptions for the given node roles.
    """
    subscriptions: list[SubscriptionTable] = []
    for role in roles:
        for product_type in OPTICAL_NODE_PRODUCT_TYPES:
            subscriptions.extend(
                subscriptions_by_product_type_and_instance_value(
                    product_type=product_type,
                    resource_type="optical_node_role",
                    value=role.value,
                    status=[
                        SubscriptionLifecycle.ACTIVE,
                    ],
                )
            )
    return subscriptions


def optical_node_selector_of_roles(roles: list[OpticalNodeRole], prompt: str | None = None) -> type[Choice]:
    """Select an Optical Node from a list of nodes.

    Args:
        roles: A list of node roles to filter the Optical Nodes by.
        prompt: A custom prompt message for the selection. Defaults to None.

    Returns:
        A Choice class containing the prompt and a list of tuples with subscription ids and descriptions.
    """
    subscriptions = get_optical_node_subscriptions_by_roles(roles)
    products = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(subscriptions, key=lambda x: x.description)
    }

    if not prompt:
        prompt = f"Select an Optical Node of role {', '.join(role.value for role in roles)}"

    dynamic_class = Choice(prompt, zip(products.keys(), products.items(), strict=False))
    return cast(type[Choice], dynamic_class)


def multiple_optical_node_selector(
    roles: list[OpticalNodeRole],
    prompt: str | None = None,
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
) -> type[list[Choice]]:
    """Select multiple Optical Nodes from a list of nodes.

    Args:
        roles: A list of node roles to filter the Optical Nodes by.
        prompt: A custom prompt message for the selection.
        min_items: Minimum number of selections required.
        max_items: Maximum number of selections allowed.
        unique_items: Whether duplicate selections are allowed.

    Returns:
        A Choice list type for selecting multiple nodes.
    """
    base_choice: type[Choice] = optical_node_selector_of_roles(roles, prompt)
    dynamic_class: type[list[Choice]] = choice_list(
        base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items
    )
    return Annotated[
        dynamic_class,
        Field(title=prompt),
    ]  # type: ignore[valid-type]


def optical_port_selector(optical_node_subscription_id: UUIDstr, prompt: str = "") -> type[Choice]:
    """Return a Choice object for selecting an optical port of an Optical Node."""
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    ports = get_device_ports_names(node)
    if not prompt:
        prompt = f"Select optical port on {_node_pqdn(node)}"
    dynamic_class = Choice(prompt, zip(ports, ports, strict=False))
    return cast(type[Choice], dynamic_class)


def unused_optical_port_selector(
    optical_node_subscription_id: UUIDstr,
    prompt: str = "",
    product_block_type: str = "OlsAddDropPortBlock",
) -> type[Choice]:
    """Return a Choice object for selecting an unused optical port of an Optical Node.

    Args:
        optical_node_subscription_id: Subscription id of the Optical Node.
        prompt: A custom prompt message for the selection.
        product_block_type: The product block type whose ``optical_port_name`` values mark
            ports as already in use (e.g. "OlsAddDropPortBlock", "OlsLinePortBlock").
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    ports = get_device_ports_names(node)

    ports_siv_list: list[SubscriptionInstanceValueTable] = (
        subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type=product_block_type,
            resource_type="optical_port_name",
            depending_on_instance_id=str(node.subscription_instance_id),
            states=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
        )
    )
    ports_in_db_list: list[str] = [str(p.value) for p in ports_siv_list]
    ports_in_db: set[str] = set(ports_in_db_list)

    unused_ports = [port for port in ports if port not in ports_in_db]
    if not prompt:
        prompt = f"Select optical port on {_node_pqdn(node)}"
    dynamic_class = Choice(prompt, zip(unused_ports, unused_ports, strict=False))
    return cast(type[Choice], dynamic_class)


def optical_client_port_selector(
    optical_node_subscription_id: UUIDstr,
    prompt: str = "",
) -> type[Choice]:
    """Return a Choice object for selecting a client optical port of an Optical Node.

    Args:
        optical_node_subscription_id: Subscription id of the Optical Node.
        prompt: A custom prompt message for the selection.
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    ports = get_device_client_ports_names(node)
    if not prompt:
        prompt = f"Select client optical port on {_node_pqdn(node)}"
    dynamic_class = Choice(prompt, zip(ports, ports, strict=False))
    return cast(type[Choice], dynamic_class)


def unused_optical_client_port_selector(
    optical_node_subscription_id: UUIDstr,
    prompt: str = "",
    product_block_type: str = "OlsAddDropPortBlock",
) -> type[Choice]:
    """Return a Choice object for selecting an unused client optical port of an Optical Node.

    Args:
        optical_node_subscription_id: Subscription id of the Optical Node.
        prompt: A custom prompt message for the selection.
        product_block_type: The product block type whose ``optical_port_name`` values mark
            ports as already in use (e.g. "OlsAddDropPortBlock", "OpticalTransponderClientPortBlock").
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    ports = get_device_client_ports_names(node)

    ports_siv_list: list[SubscriptionInstanceValueTable] = (
        subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type=product_block_type,
            resource_type="optical_port_name",
            depending_on_instance_id=str(node.subscription_instance_id),
            states=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
        )
    )
    ports_in_db_list: list[str] = [str(p.value) for p in ports_siv_list]
    ports_in_db: set[str] = set(ports_in_db_list)

    unused_ports = [port for port in ports if port not in ports_in_db]
    if not prompt:
        prompt = f"Select client optical port on {_node_pqdn(node)}"
    dynamic_class = Choice(prompt, zip(unused_ports, unused_ports, strict=False))
    return cast(type[Choice], dynamic_class)


def optical_line_port_selector(
    optical_node_subscription_id: UUIDstr,
    prompt: str = "",
) -> type[Choice]:
    """Return a Choice object for selecting a line optical port of an Optical Node.

    Args:
        optical_node_subscription_id: Subscription id of the Optical Node.
        prompt: A custom prompt message for the selection.
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    ports = get_device_line_ports_names(node)
    if not prompt:
        prompt = f"Select line optical port on {_node_pqdn(node)}"
    dynamic_class = Choice(prompt, zip(ports, ports, strict=False))
    return cast(type[Choice], dynamic_class)


def unused_optical_line_port_selector(
    optical_node_subscription_id: UUIDstr,
    prompt: str = "",
    product_block_type: str = "OlsLinePortBlock",
) -> type[Choice]:
    """Return a Choice object for selecting an unused line optical port of an Optical Node.

    Args:
        optical_node_subscription_id: Subscription id of the Optical Node.
        prompt: A custom prompt message for the selection.
        product_block_type: The product block type whose ``optical_port_name`` values mark
            ports as already in use (e.g. "OlsLinePortBlock", "OpticalTransponderLinePortBlock").
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    node = subscription.optical_node
    ports = get_device_line_ports_names(node)

    ports_siv_list: list[SubscriptionInstanceValueTable] = (
        subscription_instance_values_by_block_type_depending_on_instance_id(
            product_block_type=product_block_type,
            resource_type="optical_port_name",
            depending_on_instance_id=str(node.subscription_instance_id),
            states=[SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING],
        )
    )
    ports_in_db_list: list[str] = [str(p.value) for p in ports_siv_list]
    ports_in_db: set[str] = set(ports_in_db_list)

    unused_ports = [port for port in ports if port not in ports_in_db]
    if not prompt:
        prompt = f"Select line optical port on {_node_pqdn(node)}"
    dynamic_class = Choice(prompt, zip(unused_ports, unused_ports, strict=False))
    return cast(type[Choice], dynamic_class)


def transceiver_mode_selector(
    optical_node_subscription_id: UUIDstr,
    port_name: str,
    prompt: str | None = None,
) -> type[Choice]:
    """Create a Choice object for selecting a transceiver mode for a given port.

    Args:
        optical_node_subscription_id: The subscription id of the Optical Node.
        port_name: The name of the port belonging to the transceiver card.
            This can also be a client port of a CHM2T transponder.
        prompt: A custom prompt message for the selection. Defaults to None.

    Returns:
        A Choice class containing the prompt and a list of available transceiver modes.
    """
    subscription = AbstractOpticalNode.from_subscription(optical_node_subscription_id)
    modulations = retrieve_transceiver_modes(subscription.optical_node, port_name)
    if not prompt:
        prompt = "Select a modulation"
    dynamic_class = Choice(prompt, zip(modulations, modulations, strict=False))
    return cast(type[Choice], dynamic_class)
