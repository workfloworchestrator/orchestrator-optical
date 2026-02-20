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

from collections import deque
from typing import NewType

from orchestrator.types import SubscriptionLifecycle
from pydantic_forms.types import UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType, OpticalDeviceBlock, Platform
from products.product_blocks.optical_device_port import OpticalDevicePortBlock
from products.product_blocks.optical_spectrum import OpticalSpectrumBlockInactive, OpticalSpectrumBlockProvisioning
from products.product_blocks.optical_spectrum_path_constraints import (
    OpticalSpectrumPathConstraintsBlockProvisioning,
)
from products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockInactive,
    OpticalSpectrumSectionBlockProvisioning,
)
from products.product_types.optical_fiber import OpticalFiber
from products.services.optical_device import retrieve_ports_spectral_occupations
from utils.custom_types.frequencies import Passband, disjoint_intervals_overlap_search
from workflows.shared import subscriptions_by_product_type

logger = get_logger(__name__)


def find_constrained_shortest_path(
    src_device: OpticalDeviceBlock,
    dst_device: OpticalDeviceBlock,
    passband: Passband,
    constraints: OpticalSpectrumPathConstraintsBlockProvisioning,
) -> list[dict]:
    """Find shortest path between optical devices respecting given constraints.

    Args:
        src_device: Source optical device
        dst_device: Destination optical device
        constraints: Path constraints to apply

    Returns:
        List of Optical Ports forming the shortest path

    Raises:
        ValueError: If source or destination devices are invalid
        RuntimeError: If no valid path exists between devices
    """
    if not src_device or not dst_device:
        msg = "Source and destination devices must be specified"
        raise ValueError(msg)

    # retrieve all active fiber subscriptions
    fiber_subscriptions = subscriptions_by_product_type("OpticalFiber", [SubscriptionLifecycle.ACTIVE])
    active_fibers = [OpticalFiber.from_subscription(sub.subscription_id).optical_fiber for sub in fiber_subscriptions]

    # filter out fibers that are excluded by the constraints
    exclude_node_sub_id_set = {x.owner_subscription_id for x in constraints.exclude_nodes}
    exclude_span_sub_id_set = {x.owner_subscription_id for x in constraints.exclude_spans}

    def does_fiber_pass_exclusion(fiber):
        if fiber.owner_subscription_id in exclude_span_sub_id_set:
            return False
        for port in fiber.terminations:
            if port.optical_device.owner_subscription_id in exclude_node_sub_id_set:
                return False
            if port.optical_device.platform == Platform.GX_G42:
                # GX_G42 ports are not supported in this path computation
                return False
            if port.optical_device.platform == Platform.Groove_G30 and "." not in port.port_name:
                # all ports with a dot are on OLS cards
                # all ports without a dot are on transponder cards and must be excluded from path computation
                return False
            if disjoint_intervals_overlap_search(port.used_passbands, passband):
                return False
        return True

    sifted_fibers = list(filter(does_fiber_pass_exclusion, active_fibers))

    # convert the fibers into an adjacency list
    graph = {}
    for fiber in sifted_fibers:
        a_port = fiber.terminations[0]
        z_port = fiber.terminations[1]
        a_node_sub_id = a_port.optical_device.owner_subscription_id
        z_node_sub_id = z_port.optical_device.owner_subscription_id
        if a_node_sub_id not in graph:
            graph[a_node_sub_id] = []
        if z_node_sub_id not in graph:
            graph[z_node_sub_id] = []
        graph[a_node_sub_id].append((z_node_sub_id, (a_port, z_port)))
        graph[z_node_sub_id].append((a_node_sub_id, (z_port, a_port)))

    # find the shortest path between the two devices with breadth-first search
    def bfs():
        src = src_device.owner_subscription_id
        dst = dst_device.owner_subscription_id
        visited_nodes = set()
        node_path_tuple = (src, [])
        queue = deque(
            [
                node_path_tuple,
            ]
        )
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
        raise RuntimeError(
            f"No valid path exists between devices {src_device.owner_subscription_id} and {dst_device.owner_subscription_id}"
        )

    return list_of_ports


Node = NewType("Node", UUIDstr)  # OpticalDeviceBlock.subscription_instance_id
Port = NewType("Port", UUIDstr)  # OpticalDevicePortBlock.subscription_instance_id
Edge = tuple[Port, Port]  # (port_a_id, port_b_id)
NeighborConnection = tuple[Node, Edge]
Graph = dict[Node, list[NeighborConnection]]  # {node_id: [(neighbor_id, (port_a_id, port_b_id)), ...]}
Path = list[Port]  # List of OpticalDevicePortBlock.subscription_instance_id


class NoOpticalPathFoundError(RuntimeError):
    """Raised when no valid optical path exists between the specified devices or ports."""

    def __init__(self, src: str, dst: str):
        super().__init__(f"No valid optical path exists between source node '{src}' and destination node '{dst}'.")


def all_valid_shortest_paths_between_oadms(
    src_optical_device_block_id: UUIDstr,
    dst_optical_device_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] = [],
    exclude_span_sub_ids: list[UUIDstr] = [],
) -> list[Path]:
    """Find all shortest paths between two Optical Add-Drop Multiplexers, considering the specified passband and constraints."""
    fiber_graph = build_constrained_graph_from_active_fibers(passband, exclude_node_sub_ids, exclude_span_sub_ids)
    return compute_all_shortest_paths(fiber_graph, src_optical_device_block_id, dst_optical_device_block_id)


def all_valid_shortest_paths_between_trxs(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] = [],
    exclude_span_sub_ids: list[UUIDstr] = [],
) -> list[Path]:
    """Find all shortest paths between two transponder ports, considering the specified passband and constraints."""
    src_add_drop_port, dst_add_drop_port = find_add_drop_ports(src_trx_port_block_id, dst_trx_port_block_id)
    if (
        str(src_add_drop_port.subscription_instance_id) == dst_trx_port_block_id
        and str(dst_add_drop_port.subscription_instance_id) == src_trx_port_block_id
    ):
        # transponder ports are directly connected to each other
        return [[]]

    src_ols_dev_id = src_add_drop_port.optical_device.subscription_instance_id
    dst_ols_dev_id = dst_add_drop_port.optical_device.subscription_instance_id
    paths = all_valid_shortest_paths_between_oadms(
        src_ols_dev_id,
        dst_ols_dev_id,
        passband,
        exclude_node_sub_ids,
        exclude_span_sub_ids,
    )

    valid_paths = []
    for path in paths:
        path.insert(0, src_add_drop_port.subscription_instance_id)
        path.append(dst_add_drop_port.subscription_instance_id)
        if are_trx_and_oadm_in_the_same_shelf_for_g30s_in_path(path):
            valid_paths.append(path)

    if not valid_paths:
        raise NoOpticalPathFoundError(
            src=src_trx_port_block_id,
            dst=dst_trx_port_block_id,
        )

    return valid_paths


def are_trx_and_oadm_in_the_same_shelf_for_g30s_in_path(path: Path) -> bool:
    """
    Validates whether the given path represents a valid connection between optical device ports.
    The function iterates through the path and checks if ports on the same Groove G30 are on the
    same shelf and slot. It skips every second port in the path and performs the validation
    only for ports associated with the Groove G30 platform.

    Args:
        path (Path): A sequence of optical device ports represented as Path objects.

    Returns:
        bool: True if the path is valid and all relevant ports are connected on the same
              Groove G30 shelf and slot; False otherwise.
    """
    for i in range(len(path) - 1):
        if i % 2 == 1:
            continue

        port_i = OpticalDevicePortBlock.from_db(path[i])
        if port_i.optical_device.platform != Platform.Groove_G30:
            continue

        ii = i + 1
        port_ii = OpticalDevicePortBlock.from_db(path[ii])

        def _(g30_port_name: str) -> tuple[int, int]:
            ids = g30_port_name.split("-")[-1]  # port-1/3.3/1.1 --> 1/3.3/1.1
            shelf, slot, _ = ids.split("/")  # 1/3.3/1.1 --> 1, 3.3, 1.1
            if "." in slot:
                slot, _ = slot.split(".")  # 3.3 --> 3, 3
            return int(shelf), int(slot)

        shelf_i, slot_i = _(port_i.port_name)
        shelf_ii, slot_ii = _(port_ii.port_name)
        if shelf_i != shelf_ii or slot_i != slot_ii:
            # ports are not on the same G30 shelf and slot, so they are not connected
            return False

    return True


def build_constrained_graph_from_active_fibers(
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] = [],
    exclude_span_sub_ids: list[UUIDstr] = [],
) -> Graph:
    """
    Builds a constrained graph representation of active optical fibers based on the provided passband
    and exclusion constraints.

    The function retrieves all active optical fiber subscriptions, filters them based on exclusion
    criteria, and constructs an adjacency list representation of the graph. Each node in the graph
    represents an optical device, and edges represent optical fibers connecting the devices.

    Args:
        passband (Passband): The passband used to filter fibers based on overlapping intervals.
        exclude_node_sub_ids (List[UUIDstr], optional): A list of subscription IDs for nodes to exclude.
        exclude_span_sub_ids (List[UUIDstr], optional): A list of subscription IDs for spans to exclude.

    Returns:
        Graph: An adjacency list representation of the graph where keys are node IDs and values are
        lists of tuples. Each tuple contains a connected node ID and a pair of port IDs representing
        the fiber connection. For example:
        {
            node_A: [(node_B, (port_A2B, port_B2A)),
                     (node_C, (port_A2C, port_C2A))],
            node_B: [(node_A, (port_B2A, port_A2B)),
                     (node_C, (port_B2C, port_C2B))],
            ...
        }
        where `node_A`, `node_B`, etc. are subscription instance IDs of optical devices,
        and `port_A2B`, `port_B2A`, etc. are subscription instance IDs of the optical device ports.

    Notes:
        - Fibers are excluded if their owner subscription ID matches any in `exclude_span_sub_ids`.
        - Fibers are excluded if any of their terminations belong to nodes with subscription IDs in
          `exclude_node_sub_ids`.
        - Fibers are excluded if their terminations overlap with the provided passband.
        - Fibers connected to transponder cards (ports without a dot in their name on Groove G30
          platform) are excluded.
    """
    # retrieve all active fiber subscriptions
    fiber_subscriptions = subscriptions_by_product_type("OpticalFiber", [SubscriptionLifecycle.ACTIVE])
    active_fibers = [OpticalFiber.from_subscription(sub.subscription_id).optical_fiber for sub in fiber_subscriptions]

    # filter out fibers that are excluded by the constraints
    exclude_node_sub_id_set = set(exclude_node_sub_ids)
    exclude_span_sub_id_set = set(exclude_span_sub_ids)
    logger.debug(
        "Exclusion sets for path computation",
        exclude_node_sub_ids=exclude_node_sub_id_set,
        exclude_span_sub_ids=exclude_span_sub_id_set,
    )

    def does_fiber_pass_exclusion(fiber):
        if str(fiber.owner_subscription_id) in exclude_span_sub_id_set:
            return False
        for port in fiber.terminations:
            if str(port.optical_device.owner_subscription_id) in exclude_node_sub_id_set:
                return False
            if disjoint_intervals_overlap_search(port.used_passbands, passband):
                return False
            if port.optical_device.platform == Platform.Groove_G30 and "." not in port.port_name:
                # all ports with a dot are on OLS cards
                # all ports without a dot are on transponder cards and must be excluded from path computation
                return False
            if port.optical_device.platform == Platform.GX_G42:
                return False
        return True

    sifted_fibers = list(filter(does_fiber_pass_exclusion, active_fibers))
    logger.debug("Graph edges for path computation", sifted_fibers=[f.fiber_name for f in sifted_fibers])

    # convert the fibers into an adjacency list
    graph = {}
    for fiber in sifted_fibers:
        port_a = fiber.terminations[0]
        port_b = fiber.terminations[1]
        id_port_a = port_a.subscription_instance_id
        id_port_b = port_b.subscription_instance_id
        id_node_a = port_a.optical_device.subscription_instance_id
        id_node_b = port_b.optical_device.subscription_instance_id
        if id_node_a not in graph:
            graph[id_node_a] = []
        if id_node_b not in graph:
            graph[id_node_b] = []
        graph[id_node_a].append((id_node_b, (id_port_a, id_port_b)))
        graph[id_node_b].append((id_node_a, (id_port_b, id_port_a)))

    return graph


def find_add_drop_ports(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
) -> tuple[OpticalDevicePortBlock, OpticalDevicePortBlock]:
    """
    Retrieve the add/drop ports connected to the transponder/transceiver ports.
    """
    src_trx_port = OpticalDevicePortBlock.from_db(src_trx_port_block_id)
    dst_trx_port = OpticalDevicePortBlock.from_db(dst_trx_port_block_id)

    src_fiber_sub_id = src_trx_port.owner_subscription_id
    dst_fiber_sub_id = dst_trx_port.owner_subscription_id

    fiber_a_sub = OpticalFiber.from_subscription(src_fiber_sub_id)
    fiber_b_sub = OpticalFiber.from_subscription(dst_fiber_sub_id)

    fiber_a = fiber_a_sub.optical_fiber
    fiber_b = fiber_b_sub.optical_fiber

    for t in fiber_a.terminations:
        if t.subscription_instance_id != src_trx_port.subscription_instance_id:
            src_add_drop_port = t
            break
    for t in fiber_b.terminations:
        if t.subscription_instance_id != dst_trx_port.subscription_instance_id:
            dst_add_drop_port = t
            break

    return src_add_drop_port, dst_add_drop_port


def compute_all_shortest_paths(graph: Graph, src: Node, dst: Node) -> list[Path]:
    """
    Finds all shortest paths from src to dst in a graph where path cost is
    the number of accumulated fiber_ports segments.

    Args:
        graph (dict): Adjacency list representation of the graph.
                      e.g., {node_A: [(node_B, (port_A2B, port_B2A)), (node_C, [port_A2C, port_C2A])], ...}
        src: The starting node subscription instance ID.
        dst: The destination node subscription instance ID.

    Returns:
        list: A list of all shortest paths. Each path is a list of OpticalDevicePortBlock subscription instance IDs.

    Raises:
        RuntimeError: If no valid path exists between the source and destination nodes.
    """
    # Queue stores (current_node, src_to_current_node_path, current_path_length)
    # The path length is crucial for determining 'shortest' and 'equal cost'.
    # We use a tuple for path_segments to make it hashable if needed, though not strictly here.
    queue = deque([(src, [], 0)])  # (node, src_to_node_path, hop_count)

    # Store the minimum distance found to a node so far.
    # This is key for optimizing and pruning longer paths early.
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
        first_port = OpticalDevicePortBlock.from_db(path[0])
        ne_name = first_port.optical_device.fqdn
        ne_name = ne_name.removesuffix(".garr.net")
        human_readable_path += f"{ne_name} ({first_port.port_name}) ⇋ "

        for i in range(1, len(path) - 1):
            if i % 2 == 0:
                continue

            port_i = OpticalDevicePortBlock.from_db(path[i])
            port_ii = OpticalDevicePortBlock.from_db(path[i + 1])
            ne_name = port_i.optical_device.fqdn
            ne_name = ne_name.removesuffix(".garr.net")
            human_readable_path += f"{ne_name} ({port_i.port_name} × {port_ii.port_name}) ⇋ "

        last_port = OpticalDevicePortBlock.from_db(path[-1])
        ne_name = last_port.optical_device.fqdn
        ne_name = ne_name.removesuffix(".garr.net")
        human_readable_path += f"{ne_name} ({last_port.port_name})"

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

            port_i = OpticalDevicePortBlock.from_db(path[i])
            port_ii = OpticalDevicePortBlock.from_db(path[i + 1])
            ne_name = port_i.optical_device.fqdn
            ne_name = ne_name.removesuffix(".garr.net")
            human_readable_path += f"{ne_name} ({port_i.port_name} × {port_ii.port_name}) ⇋ "
            # g30.na01 (port-1/3.1/1 × port-1/3.3/1.1) ⇋ flex.na01 (1-E1-1-T2A × 1-A-1-L1) ⇋ flex.bo01 (2-A-1-L1 × ...

        human_readable_path = human_readable_path.removesuffix(" ⇋ ")
        path_subscription_ids = ";".join(str(port_id) for port_id in path)
        paths_dict[path_subscription_ids] = human_readable_path

    return Choice(prompt, zip(paths_dict.keys(), paths_dict.items(), strict=False))


def transport_channel_path_selector(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] = [],
    exclude_span_sub_ids: list[UUIDstr] = [],
    prompt: str = "Select an optical path.",
) -> Choice:
    """
    Selects an optical path between two transceiver port blocks based on the given parameters.
    The selected path MUST then be parsed using path.split(";") to obtain the sequence of subscription instance IDs of the OpticalDevicePortBlock.

    Args:
        src_trx_port_block_id (UUIDstr): The UUID of the source transceiver port block.
        dst_trx_port_block_id (UUIDstr): The UUID of the destination transceiver port block.
        passband (Passband): The passband configuration for the optical path.
        exclude_node_sub_ids (List[UUIDstr], optional): A list of node subscription IDs to exclude from the path. Defaults to an empty list.
        exclude_span_sub_ids (List[UUIDstr], optional): A list of span subscription IDs to exclude from the path. Defaults to an empty list.
        prompt (str, optional): A prompt message for the user to select an optical path. Defaults to "Select an optical path.".

    Returns:
        Choice: A Choice object containing the prompt and a list of valid optical paths represented as subscription IDs and human-readable strings.

    Notes:
        - The function finds valid equal-cost shortest paths between the source and destination transceiver port blocks.
        - Each path is converted into a human-readable string format for user selection.
        - The paths are internally represented as sequences of subscription IDs delimited by ;.
          e.g. "<subscription_instance_id>;<subscription_instance_id>;<subscription_instance_id>;".
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
    exclude_node_sub_ids: list[UUIDstr] = [],
    exclude_span_sub_ids: list[UUIDstr] = [],
    prompt: str = "Select an optical path.",
) -> Choice:
    """
    Selects an optical path between two optical devices based on the given parameters.
    The selected path MUST then be parsed using path.split(";") to obtain the sequence
    of subscription instance IDs of the OpticalDevicePortBlock.

    Args:
        src_optical_device_block_id (UUIDstr): The UUID of the source optical device block.
        dst_optical_device_block_id (UUIDstr): The UUID of the destination optical device block.
        passband (Passband): The passband configuration for the optical path.
        exclude_node_sub_ids (List[UUIDstr], optional): A list of node subscription IDs to exclude from the path.
            Defaults to an empty list.
        exclude_span_sub_ids (List[UUIDstr], optional): A list of span subscription IDs to exclude from the path.
            Defaults to an empty list.
        prompt (str, optional): A prompt message for the user to select an optical path.
            Defaults to "Select an optical path.".

    Returns:
        Choice: A Choice object containing the prompt and a list of valid optical paths represented as
        subscription IDs and human-readable strings.

    Notes:
        - The function finds valid equal-cost shortest paths between the source and destination transceiver port blocks.
        - Each path is converted into a human-readable string format for user selection.
        - The paths are internally represented as sequences of subscription IDs delimited by ;.
          e.g. "<subscription_instance_id>;<subscription_instance_id>;<subscription_instance_id>;".
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
    """
    Decomposes a continuous list of optical ports into platform-specific sections and
    saves them to the provided optical spectrum block.

    The function groups the provided optical path into "sections" based on the device platform.
    Whenever the platform changes between two adjacent ports in the path, a new section is
    started. Each section is then stored as an `OpticalSpectrumSectionBlockInactive`.

    For each section:
    - The first and last ports are designated as `add_drop_ports`.
    - Any ports in between the first and last are stored in the `optical_path` field.

    Args:
        optical_path: A sequence of port UUIDs representing the full end-to-end
            optical route.
        optical_spectrum: The spectrum block domain model where the resulting
            sections will be appended.

    Returns:
        None: The function modifies the `optical_spectrum` object in place.
    """
    ports = []
    for port_id in optical_path:
        port = OpticalDevicePortBlock.from_db(port_id)
        ports.append(port)

    sections: list[list[OpticalDevicePortBlock]] = []
    current_section = [ports[0]]
    previous_port = ports[0]
    for current_port in ports[1:]:
        if current_port.optical_device.platform != previous_port.optical_device.platform:
            sections.append(current_section)
            current_section = []
        current_section.append(current_port)
        previous_port = current_port

    if current_section:
        sections.append(current_section)

    subscription_id = optical_spectrum.subscription.subscription_id
    optical_spectrum_sections = optical_spectrum.optical_spectrum_sections
    if isinstance(optical_spectrum, OpticalSpectrumBlockProvisioning):
        optical_spectrum_sections = []
        block = OpticalSpectrumSectionBlockProvisioning
    else:
        block = OpticalSpectrumSectionBlockInactive

    for section in sections:
        s = block.new(
            subscription_id=subscription_id,
            add_drop_ports=[section[0], section[-1]],
            optical_path=section[1:-1],
        )
        optical_spectrum_sections.append(s)


def update_used_passbands(optical_spectrum: OpticalSpectrumBlockProvisioning) -> None:
    passbands_by_device = {}
    for section in optical_spectrum.optical_spectrum_sections:
        for port in section.optical_path:
            device = port.optical_device
            if device.device_type in [
                DeviceType.ROADM,
                DeviceType.TransponderAndOADM,
            ]:
                if device.fqdn not in passbands_by_device:
                    passbands_by_device[device.fqdn] = retrieve_ports_spectral_occupations(device)
                port.used_passbands = passbands_by_device[device.fqdn].get(port.port_name, [])
