"""Shared helpers for the Optical Spectrum Service workflows.

This module ports the legacy optical spectrum path engine and the optical
device selectors to the generalized Optical Node/Port model:

- the path engine works on the active optical pipes (Fiber Span, Fiber Patch and
  Leased Spectrum subscriptions) whose ``optical_pipe_terminations`` are both Open
  Line System ports (``AbstractOpticalOlsPortBlockInactive``) connecting two Optical
  Nodes; pipes terminated on transponder or coherent pluggable ports are skipped;
- optical devices are the ``AbstractOpticalNodeBlock`` instances (any vendor
  block), and device types are replaced by the ``OpticalNodeRole`` of the
  hosting node (``OpticalNodeRole.ROADM``, ``OpticalNodeRole.AMPLIFIER``,
  ``OpticalNodeRole.TRANSPONDER``, ``OpticalNodeRole.TRANSPONDER_XOADM``);
- platform checks are dispatched on the ``Vendor`` and ``Platform`` enums of the
  ``OpticalModuleNodeManagementBlock``;
- the old ``used_passbands`` of the optical ports is the
  ``optical_passbands`` of the ``AbstractOpticalOlsPortBlock`` instances;
- the old device-specific port selectors are replaced by the generic
  role-based ``optical_port_selector`` of ``orchestrator.optical.workflows.shared``
  and by ``optical_node_selector_of_roles`` / ``transceiver_mode_selector``.
"""

from collections import deque
from collections.abc import Iterable
from itertools import pairwise, product
from typing import Annotated, Any, cast
from uuid import UUID

from pydantic import Field
from pydantic_forms.types import State, UUIDstr
from pydantic_forms.validators import Choice, choice_list
from structlog import get_logger

from orchestrator.core.db import SubscriptionTable
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import step
from orchestrator.optical.db import (
    subscriptions_by_product_type,
    subscriptions_by_product_type_and_instance_value,
)
from orchestrator.optical.hal.node import retrieve_ports_spectral_occupations
from orchestrator.optical.hal.port import retrieve_transceiver_modes
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import AbstractOpticalPipeBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalPortBlockInactive,
    OpticalPortRole,
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
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatchSubscription
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpanSubscription
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrumSubscription
from orchestrator.optical.utils.custom_types.frequencies import Passband, disjoint_intervals_overlap_search
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import rehydrate_optical_module_block

logger = get_logger(__name__)

OPTICAL_NODE_PRODUCT_TYPES = [
    ProductType.OPTICAL_NODE_NOKIA_FLEXILS.value,
    ProductType.OPTICAL_NODE_NOKIA_GROOVE_G30.value,
    ProductType.OPTICAL_NODE_NOKIA_GX_G42.value,
]

OPTICAL_PIPE_PRODUCT_TYPES = [
    ProductType.OPTICAL_FIBER_SPAN.value,
    ProductType.OPTICAL_FIBER_PATCH.value,
    ProductType.OPTICAL_LEASED_SPECTRUM.value,
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


def _node_fqdn(node: AbstractOpticalNodeBlockInactive) -> str:
    """Return the fqdn of an Optical Node block, tolerating unset values."""
    return (
        str(node.management.optical_module_node_fqdn)
        if node.management.optical_module_node_fqdn is not None
        else "<unknown>"
    )


def _load_ols_port(port_id: UUIDstr) -> AbstractOpticalOlsPortBlockInactive:
    """Load an OLS Optical Port block from its subscription instance id."""
    return cast(AbstractOpticalOlsPortBlockInactive, ProductBlockModel.from_db(UUID(str(port_id))))


def load_ols_port(port_id: UUIDstr) -> AbstractOpticalOlsPortBlockInactive:
    """Load an OLS Optical Port block from its subscription instance id.

    This is the public wrapper over :func:`_load_ols_port`, shipped for
    consumers that need to resolve the port blocks of a path chosen in a form
    to their domain models (e.g. in their own construct step).

    Args:
        port_id: Subscription instance id of the OLS Optical Port block.

    Returns:
        The loaded OLS Optical Port block.
    """
    return _load_ols_port(port_id)


def _load_port(port_id: UUIDstr) -> AbstractOpticalPortBlockInactive:
    """Load an Optical Port block from its subscription instance id."""
    return cast(AbstractOpticalPortBlockInactive, ProductBlockModel.from_db(UUID(str(port_id))))


def optical_spectrum_block_from_state(
    optical_module_block: OpticalSpectrumBlockInactive | OpticalSpectrumBlockProvisioning | dict[str, Any] | None,
) -> OpticalSpectrumBlockProvisioning:
    """Return the Optical Spectrum block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the full block data) rather than as a domain
    model. This helper returns the value unchanged when it is already a domain
    model (in-process usage, e.g. in tests) and reconstructs the block from the
    serialized data otherwise. The lifecycle variant of the block is resolved
    from the status of its owner subscription, so blocks of any lifecycle are
    loaded as their matching variant (INITIAL, PROVISIONING or ACTIVE). The
    shipped block steps always operate on the PROVISIONING variant: their
    callers construct the block with the mandatory fields set and transition
    the subscription to PROVISIONING before running them.

    Args:
        optical_module_block: The block value from the workflow state, or None.

    Returns:
        The Optical Spectrum block as a domain model.

    Raises:
        ValueError: If there is no Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    if optical_module_block is None:
        msg = "No Optical Spectrum block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    if isinstance(optical_module_block, OpticalSpectrumBlockInactive):
        return cast(OpticalSpectrumBlockProvisioning, optical_module_block)
    return cast(
        OpticalSpectrumBlockProvisioning,
        rehydrate_optical_module_block(optical_module_block, block_description="Optical Spectrum"),
    )


def _optical_spectrum_block_of_subscription(subscription: SubscriptionModel) -> OpticalSpectrumBlockInactive:
    """Return the Optical Spectrum block under the ``optical_spectrum_service`` attribute.

    This is the shipped-model fallback of the family: it reads the block from
    the ``optical_spectrum_service`` attribute of the subscription, which the
    shipped subscription models always have.

    Args:
        subscription: The Optical Spectrum subscription.

    Returns:
        The Optical Spectrum block of the subscription.

    Raises:
        ValueError: If the subscription has no block under the attribute.
    """
    spectrum = getattr(subscription, "optical_spectrum_service", None)
    if spectrum is None:
        msg = (
            "Optical Spectrum subscription has no Optical Spectrum block under attribute "
            "'optical_spectrum_service': the subscription model must have-a the Optical Spectrum block, "
            "e.g. under 'optical_spectrum_service'"
        )
        raise ValueError(msg)
    return cast(OpticalSpectrumBlockInactive, spectrum)


def optical_spectrum_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalSpectrumBlockInactive | None = None,
) -> str:
    """Generate the human-readable description of an Optical Spectrum subscription.

    The description is derived from the spectrum name and the product name, so
    the same function can be reused by consumers that compose the shipped block
    under their own attribute: pass the shipped block explicitly, otherwise it
    falls back to the ``optical_spectrum_service`` attribute of the shipped
    subscription models.

    Args:
        subscription: The Optical Spectrum subscription.
        optical_module_block: The Optical Spectrum block of the subscription.
            When given, it is used instead of the ``optical_spectrum_service``
            attribute of the shipped subscription models.

    Returns:
        The subscription description, e.g. ``"spec-01 (Optical Spectrum)"`` or
        the product name when the spectrum has no name yet.

    Raises:
        ValueError: If the subscription has no Optical Spectrum block under the
            ``optical_spectrum_service`` attribute and no block was passed.
    """
    spectrum = optical_module_block or _optical_spectrum_block_of_subscription(subscription)
    if spectrum.optical_spectrum_name:
        return f"{spectrum.optical_spectrum_name} ({subscription.product.name})"
    return subscription.product.name


@step("Set Optical Spectrum subscription description")
def set_optical_spectrum_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalSpectrumBlockInactive | None = None,
) -> State:
    """Set the description of the Optical Spectrum subscription.

    The block is read from the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``
    (put there by the construct step of the shipped create workflow or by
    :func:`load_optical_spectrum_block` in the other shipped workflows); a step
    chain must always load the block into the state before this step runs.

    Args:
        subscription: The Optical Spectrum subscription.
        optical_module_block: The Optical Spectrum block of the subscription, as
            available in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    subscription.description = optical_spectrum_subscription_description(subscription, block)
    return {"subscription": subscription, "subscription_description": subscription.description}


@step("Load optical spectrum block")
def load_optical_spectrum_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Spectrum block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_spectrum_service`` attribute: it makes
    the block available to the shipped block steps under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. Consumers that compose the shipped
    block under a different attribute name write their own one-step wiring
    instead.

    Args:
        subscription: The Optical Spectrum subscription.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Spectrum block under the
            ``optical_spectrum_service`` attribute.
    """
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: _optical_spectrum_block_of_subscription(subscription)}


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
        OpticalFiberSpanSubscription.from_subscription(sub.subscription_id).optical_pipe for sub in fiber_subscriptions
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
            if (
                node.management.optical_module_node_vendor,
                node.management.optical_module_node_platform,
            ) == (Vendor.NOKIA, Platform.GROOVE_G30) and "." not in (port.optical_port_name or ""):
                # all ports with a dot are on OLS cards
                # all ports without a dot are on transponder cards and must be excluded
                return False
            if (
                node.management.optical_module_node_vendor,
                node.management.optical_module_node_platform,
            ) == (Vendor.NOKIA, Platform.GX_G42):
                return False
        return True

    sifted_fibers = list(filter(does_fiber_pass_exclusion, active_fibers))
    logger.debug("Graph edges for path computation", sifted_fibers=[f.optical_pipe_name for f in sifted_fibers])

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


def build_graph_from_pipes(
    pipes: Iterable[AbstractOpticalPipeBlockInactive],
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> Graph:
    """Build a constrained graph representation from the given optical pipes.

    A pipe is included only when both of its ``optical_pipe_terminations`` are Open
    Line System ports (``AbstractOpticalOlsPortBlockInactive``, i.e. role ``OLS_LINE``
    or ``OLS_ADD_DROP``). Any pipe terminated on a transponder line/client port or on
    a coherent pluggable is skipped entirely.

    Args:
        pipes: The optical pipe blocks to build the graph from.
        passband: The passband used to filter pipes based on overlapping intervals.
        exclude_node_sub_ids: A list of subscription ids of nodes to exclude.
        exclude_span_sub_ids: A list of subscription ids of pipes to exclude.

    Returns:
        An adjacency list representation of the graph where keys are the
        ``subscription_instance_id`` of the Optical Nodes and values are lists
        of tuples containing a connected node id and the pair of port ids of
        the pipe, e.g. ``{node_A: [(node_B, (port_A2B, port_B2A)), ...]}``.

    Raises:
        ValueError: If a pipe does not have exactly two terminations.
    """
    exclude_node_sub_id_set = set(exclude_node_sub_ids or [])
    exclude_span_sub_id_set = set(exclude_span_sub_ids or [])

    graph: dict[Node, list[NeighborConnection]] = {}
    for pipe in pipes:
        if str(pipe.owner_subscription_id) in exclude_span_sub_id_set:
            continue
        terminations = pipe.optical_pipe_terminations
        if terminations is None or len(terminations) != 2:  # noqa: PLR2004
            msg = f"Optical pipe {pipe.optical_pipe_name!r} must have exactly two terminations"
            raise ValueError(msg)
        if not all(isinstance(port, AbstractOpticalOlsPortBlockInactive) for port in terminations):
            continue
        port_a = cast(AbstractOpticalOlsPortBlockInactive, terminations[0])
        port_b = cast(AbstractOpticalOlsPortBlockInactive, terminations[1])
        if any(
            str(port.optical_port_host_node.owner_subscription_id) in exclude_node_sub_id_set
            for port in (port_a, port_b)
        ):
            continue
        if any(disjoint_intervals_overlap_search(port.optical_passbands, passband) for port in (port_a, port_b)):
            continue

        id_port_a = str(port_a.subscription_instance_id)
        id_port_b = str(port_b.subscription_instance_id)
        id_node_a = str(port_a.optical_port_host_node.subscription_instance_id)
        id_node_b = str(port_b.optical_port_host_node.subscription_instance_id)
        graph.setdefault(id_node_a, []).append((id_node_b, (id_port_a, id_port_b)))
        graph.setdefault(id_node_b, []).append((id_node_a, (id_port_b, id_port_a)))

    return graph


def build_constrained_graph(
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> Graph:
    """Build a constrained graph from all active optical pipes.

    The active Fiber Span, Fiber Patch and Leased Spectrum subscriptions are loaded
    from the database and delegated to :func:`build_graph_from_pipes`.

    Args:
        passband: The passband used to filter pipes based on overlapping intervals.
        exclude_node_sub_ids: A list of subscription ids of nodes to exclude.
        exclude_span_sub_ids: A list of subscription ids of pipes to exclude.

    Returns:
        An adjacency list representation of the constrained graph (see
        :func:`build_graph_from_pipes`).
    """
    pipes: list[AbstractOpticalPipeBlockInactive] = []
    for product_type, subscription_model in (
        (ProductType.OPTICAL_FIBER_SPAN.value, OpticalFiberSpanSubscription),
        (ProductType.OPTICAL_FIBER_PATCH.value, OpticalFiberPatchSubscription),
        (ProductType.OPTICAL_LEASED_SPECTRUM.value, OpticalLeasedSpectrumSubscription),
    ):
        pipes.extend(
            subscription_model.from_subscription(sub.subscription_id).optical_pipe
            for sub in subscriptions_by_product_type(product_type, [SubscriptionLifecycle.ACTIVE])
        )
    return build_graph_from_pipes(pipes, passband, exclude_node_sub_ids, exclude_span_sub_ids)


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
        if (
            port_i.optical_port_host_node.management.optical_module_node_vendor,
            port_i.optical_port_host_node.management.optical_module_node_platform,
        ) != (Vendor.NOKIA, Platform.GROOVE_G30):
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

    fiber_a = OpticalFiberSpanSubscription.from_subscription(src_trx_port.owner_subscription_id).optical_pipe
    fiber_b = OpticalFiberSpanSubscription.from_subscription(dst_trx_port.owner_subscription_id).optical_pipe

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


def all_shortest_paths_through_waypoints(
    src_node_sub_id: UUIDstr,
    dst_node_sub_id: UUIDstr,
    waypoint_node_sub_ids: list[UUIDstr] | None,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
) -> list[Path]:
    """Find all shortest paths from source to destination through the ordered waypoints.

    The graph is built once from the active optical pipes; the path is then computed
    segment by segment between consecutive stops (source, the ordered waypoints and
    destination). Consecutive duplicate stops are collapsed.

    Args:
        src_node_sub_id: Subscription instance id of the source Optical Node block.
        dst_node_sub_id: Subscription instance id of the destination Optical Node block.
        waypoint_node_sub_ids: Ordered subscription instance ids of the intermediate
            nodes the path must traverse.
        passband: The passband configuration for the optical path.
        exclude_node_sub_ids: A list of node subscription ids to exclude from the path.
        exclude_span_sub_ids: A list of pipe subscription ids to exclude from the path.

    Returns:
        A list of all shortest paths as lists of Optical Port subscription instance ids.

    Raises:
        NoOpticalPathFoundError: If any segment between two consecutive stops has no path.
    """
    graph = build_constrained_graph(passband, exclude_node_sub_ids, exclude_span_sub_ids)
    if not waypoint_node_sub_ids:
        return compute_all_shortest_paths(graph, src_node_sub_id, dst_node_sub_id)

    stops = [src_node_sub_id]
    for stop in [*waypoint_node_sub_ids, dst_node_sub_id]:
        if stop != stops[-1]:
            stops.append(stop)

    segments: list[list[Path]] = []
    for segment_src, segment_dst in pairwise(stops):
        try:
            segments.append(compute_all_shortest_paths(graph, segment_src, segment_dst))
        except NoOpticalPathFoundError as exc:
            raise NoOpticalPathFoundError(src=src_node_sub_id, dst=dst_node_sub_id) from exc

    unique_paths: dict[tuple[Port, ...], Path] = {}
    for segment_combination in product(*segments):
        path: Path = [port for segment in segment_combination for port in segment]
        unique_paths.setdefault(tuple(path), path)
    return list(unique_paths.values())


def human_readable_optical_spectrum_path_selector(
    paths: list[Path],
    prompt: str = "Select an optical path.",
) -> type[Choice]:
    """Convert paths to string representations for the choice options."""
    paths_dict = {}
    for path in paths:
        human_readable_path = ""
        first_port = _load_ols_port(path[0])
        ne_name = _node_fqdn(first_port.optical_port_host_node)
        human_readable_path += f"{ne_name} ({first_port.optical_port_name}) ⇋ "

        for i in range(1, len(path) - 1):
            if i % 2 == 0:
                continue

            port_i = _load_ols_port(path[i])
            port_ii = _load_ols_port(path[i + 1])
            ne_name = _node_fqdn(port_i.optical_port_host_node)
            human_readable_path += f"{ne_name} ({port_i.optical_port_name} × {port_ii.optical_port_name}) ⇋ "  # noqa: RUF001

        last_port = _load_ols_port(path[-1])
        ne_name = _node_fqdn(last_port.optical_port_host_node)
        human_readable_path += f"{ne_name} ({last_port.optical_port_name})"

        path_subscription_ids = ";".join(str(port_id) for port_id in path)
        paths_dict[path_subscription_ids] = human_readable_path

    return cast(type[Choice], Choice(prompt, zip(paths_dict.keys(), paths_dict.items(), strict=False)))


def human_readable_transport_channel_path_selector(
    paths: list[Path],
    prompt: str = "Select an optical path.",
) -> type[Choice]:
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
            ne_name = _node_fqdn(port_i.optical_port_host_node)
            human_readable_path += f"{ne_name} ({port_i.optical_port_name} × {port_ii.optical_port_name}) ⇋ "  # noqa: RUF001
            # g30.na01 (port-1/3.1/1 x port-1/3.3/1.1) <-> flex.na01 (1-E1-1-T2A x 1-A-1-L1) <-> ...

        human_readable_path = human_readable_path.removesuffix(" ⇋ ")
        path_subscription_ids = ";".join(str(port_id) for port_id in path)
        paths_dict[path_subscription_ids] = human_readable_path

    return cast(type[Choice], Choice(prompt, zip(paths_dict.keys(), paths_dict.items(), strict=False)))


def transport_channel_path_selector(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
    prompt: str = "Select an optical path.",
) -> type[Choice]:
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
    src_node_sub_id: UUIDstr,
    dst_node_sub_id: UUIDstr,
    waypoint_node_sub_ids: list[UUIDstr] | None,
    passband: Passband,
    exclude_node_sub_ids: list[UUIDstr] | None = None,
    exclude_span_sub_ids: list[UUIDstr] | None = None,
    prompt: str = "Select an optical path.",
) -> type[Choice]:
    """Select an optical path between two optical devices based on the given parameters.

    The selected path MUST then be parsed using ``path.split(";")`` to obtain the sequence
    of subscription instance ids of the Optical Port blocks.

    Args:
        src_node_sub_id: The subscription instance id of the source Optical Node block.
        dst_node_sub_id: The subscription instance id of the destination Optical Node block.
        waypoint_node_sub_ids: Ordered subscription instance ids of the nodes the path must traverse.
        passband: The passband configuration for the optical path.
        exclude_node_sub_ids: A list of node subscription ids to exclude from the path. Defaults to an empty list.
        exclude_span_sub_ids: A list of pipe subscription ids to exclude from the path. Defaults to an empty list.
        prompt: A prompt message for the user to select an optical path. Defaults to "Select an optical path.".

    Returns:
        A Choice object containing the prompt and a list of valid optical paths represented as
        subscription ids and human-readable strings.
    """
    paths = all_shortest_paths_through_waypoints(
        src_node_sub_id,
        dst_node_sub_id,
        waypoint_node_sub_ids,
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
        if (
            current_port.optical_port_host_node.management.optical_module_node_vendor,
            current_port.optical_port_host_node.management.optical_module_node_platform,
        ) != (
            previous_port.optical_port_host_node.management.optical_module_node_vendor,
            previous_port.optical_port_host_node.management.optical_module_node_platform,
        ):
            sections.append(current_section)
            current_section = []
        current_section.append(current_port)
        previous_port = current_port

    if current_section:
        sections.append(current_section)

    store_loaded_sections_into_spectrum_block(sections, optical_spectrum)


def split_loaded_path_into_loaded_sections(
    ports: list[AbstractOpticalOlsPortBlockInactive],
) -> list[list[AbstractOpticalOlsPortBlockInactive]]:
    """Split a loaded optical path into single-platform sections at the add/drop ports.

    The path is split at the OLS add/drop ports: the path must start and end with an
    add/drop port and contain an even number of them. Consecutive add/drop ports are
    paired and the ports between each pair form a section, which must contain only OLS
    line ports and share a single (vendor, platform) pair.

    Args:
        ports: The loaded OLS port blocks of the path, ordered from source to destination.

    Returns:
        The sections as lists of loaded OLS port blocks.

    Raises:
        ValueError: If the path does not start and end with add/drop ports, if the
            number of add/drop ports is not even, if a middle port is not an OLS line
            port, or if a section mixes vendors or platforms.
    """
    add_drop_indices = [
        index for index, port in enumerate(ports) if port.optical_port_role is OpticalPortRole.OLS_ADD_DROP
    ]
    if len(add_drop_indices) < 2 or len(add_drop_indices) % 2 != 0:  # noqa: PLR2004
        msg = "The optical path must contain an even number of add/drop ports"
        raise ValueError(msg)
    if add_drop_indices[0] != 0 or add_drop_indices[-1] != len(ports) - 1:
        msg = "The optical path must start and end with an add/drop port"
        raise ValueError(msg)

    sections: list[list[AbstractOpticalOlsPortBlockInactive]] = []
    for start, end in zip(add_drop_indices[::2], add_drop_indices[1::2], strict=True):
        section = ports[start : end + 1]
        if any(port.optical_port_role is not OpticalPortRole.OLS_LINE for port in section[1:-1]):
            msg = "Every middle port of a section must be an OLS line port"
            raise ValueError(msg)
        platforms = {
            (
                port.optical_port_host_node.management.optical_module_node_vendor,
                port.optical_port_host_node.management.optical_module_node_platform,
            )
            for port in section
        }
        if len(platforms) != 1:
            msg = "Every port of a section must belong to the same vendor and platform"
            raise ValueError(msg)
        sections.append(section)
    return sections


def split_loaded_path_into_platform_sections(
    ports: list[AbstractOpticalOlsPortBlockInactive],
) -> list[list[UUIDstr]]:
    """Split a loaded optical path into single-platform sections at the add/drop ports.

    Thin wrapper over :func:`split_loaded_path_into_loaded_sections` that returns the
    sections as lists of port subscription instance ids.

    Args:
        ports: The loaded OLS port blocks of the path, ordered from source to destination.

    Returns:
        The sections as lists of port subscription instance ids.

    Raises:
        ValueError: If the path cannot be split into valid single-platform sections.
    """
    return [
        [str(port.subscription_instance_id) for port in section]
        for section in split_loaded_path_into_loaded_sections(ports)
    ]


def split_path_into_platform_sections(optical_path: list[UUIDstr]) -> list[list[UUIDstr]]:
    """Split an optical path given as port subscription instance ids into platform sections.

    Args:
        optical_path: The ordered port subscription instance ids of the path.

    Returns:
        The sections as lists of port subscription instance ids.

    Raises:
        ValueError: If the path cannot be split into valid single-platform sections.
    """
    ports = [_load_ols_port(port_id) for port_id in optical_path]
    return split_loaded_path_into_platform_sections(ports)


def store_loaded_sections_into_spectrum_block(
    sections: list[list[AbstractOpticalOlsPortBlockInactive]],
    optical_spectrum: OpticalSpectrumBlockInactive | OpticalSpectrumBlockProvisioning,
) -> None:
    """Store the given single-platform sections into the spectrum block.

    For each section the first and last ports become the
    ``optical_spectrum_section_add_drop_ports`` and the ports in between become the
    ``optical_spectrum_section_express_ports``. The section blocks are created in the
    lifecycle variant matching the spectrum block (PROVISIONING sections for a
    PROVISIONING spectrum, INITIAL sections otherwise) and are owned by the spectrum's
    owner subscription (``owner_subscription_id``), so the function also works before
    the owner subscription row is persisted.

    Args:
        sections: The sections as lists of loaded OLS port blocks.
        optical_spectrum: The spectrum block where the resulting sections will be stored.

    Returns:
        None: The function modifies the ``optical_spectrum`` object in place.
    """
    subscription_id = optical_spectrum.owner_subscription_id
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


def store_sections_into_spectrum_block(
    sections: list[list[UUIDstr]],
    optical_spectrum: OpticalSpectrumBlockInactive | OpticalSpectrumBlockProvisioning,
) -> None:
    """Store the given single-platform sections into the spectrum block.

    Thin wrapper over :func:`store_loaded_sections_into_spectrum_block` that loads the
    section ports from their subscription instance ids first.

    Args:
        sections: The sections as lists of port subscription instance ids.
        optical_spectrum: The spectrum block where the resulting sections will be stored.

    Returns:
        None: The function modifies the ``optical_spectrum`` object in place.
    """
    loaded_sections = [[_load_ols_port(port_id) for port_id in section] for section in sections]
    store_loaded_sections_into_spectrum_block(loaded_sections, optical_spectrum)


def update_used_passbands(optical_spectrum: OpticalSpectrumBlockProvisioning) -> None:
    """Refresh the ``optical_passbands`` of any Open Line System port in the path from the devices."""
    passbands_by_device: dict[str, dict[str, list[tuple[int, int]]]] = {}
    for section in optical_spectrum.optical_spectrum_sections:
        for port in section.optical_spectrum_section_express_ports:
            node = port.optical_port_host_node
            if node.optical_node_role not in (OpticalNodeRole.ROADM, OpticalNodeRole.TRANSPONDER_XOADM):
                continue
            if node.management.optical_module_node_fqdn is None or port.optical_port_name is None:
                continue
            if node.management.optical_module_node_fqdn not in passbands_by_device:
                passbands_by_device[node.management.optical_module_node_fqdn] = retrieve_ports_spectral_occupations(
                    node
                )
            port.optical_passbands = passbands_by_device[node.management.optical_module_node_fqdn].get(
                port.optical_port_name, []
            )


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
    return cast(
        type[list[Choice]],
        Annotated[
            dynamic_class,
            Field(title=prompt),
        ],
    )


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
    node_block = cast(AnyOpticalNodeBlockProvisioningUnion, subscription.optical_node)
    modulations = retrieve_transceiver_modes(node_block, port_name)
    if not prompt:
        prompt = "Select a modulation"
    dynamic_class = Choice(prompt, zip(modulations, modulations, strict=False))
    return cast(type[Choice], dynamic_class)
