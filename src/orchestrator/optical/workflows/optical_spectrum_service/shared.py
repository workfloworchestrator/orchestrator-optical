"""Shared helpers for the Optical Spectrum Service workflows.

This module ports the legacy optical spectrum path engine and the optical
device selectors to the generalized Optical Node/Port model:

- the path engine works on the active optical pipes (Fiber Span, Fiber Patch and
  Leased Spectrum subscriptions) whose ``optical_pipe_terminations`` are both Open
  Line System ports (``AbstractOpticalOlsPortBlockInactive``) connecting two Optical
  Nodes; pipes terminated on transponder or coherent pluggable ports are skipped;
- optical devices are the ``AbstractOpticalNodeBlock`` instances (any vendor
  block), and device types are replaced by the ``OpticalNodeRole`` of the
  hosting node (``OpticalNodeRole.ROADM``, ``OpticalNodeRole.FOADM``,
  ``OpticalNodeRole.AMPLIFIER``, ``OpticalNodeRole.TRANSPONDER``,
  ``OpticalNodeRole.TRANSPONDER_ROADM``, ``OpticalNodeRole.TRANSPONDER_FOADM``);
- platform checks are dispatched on the ``Vendor`` and ``Platform`` enums of the
  ``OpticalModuleNodeManagementBlock``;
- the old ``used_passbands`` of the optical ports is the
  ``optical_passbands`` of the ``AbstractOpticalOlsPortBlock`` instances;
- the old device-specific port selectors are replaced by the generic
  role-based ``optical_port_selector`` of ``orchestrator.optical.workflows.shared``
  and by ``optical_node_selector_of_roles`` / ``transceiver_mode_selector``.
"""

import heapq
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Annotated, Any, NamedTuple, cast
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import State, UUIDstr
from pydantic_forms.validators import Choice, choice_list
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Label
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import step
from orchestrator.optical.db import pipe_blocks_all
from orchestrator.optical.hal.connectivity import IntraNodeEdge, g30_shelf_of_port, retrieve_add_drop_connectivity
from orchestrator.optical.hal.node import retrieve_ports_spectral_occupations
from orchestrator.optical.hal.port import retrieve_transceiver_modes
from orchestrator.optical.hal.spectrum import (
    FLEXILS_SPECTRAL_GRID_MHZ,
    delete_optical_circuit,
    delete_optical_circuit_oel,
    ensure_optical_circuit,
    validate_optical_circuit,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    OADM_ROLES,
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
    OpticalSpectrumServiceBlockInactive,
    OpticalSpectrumServiceBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockInactive,
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.settings import get_settings
from orchestrator.optical.utils.custom_types.frequencies import (
    Frequency,
    Passband,
    ensure_passband_aligned_to_grid,
    free_intervals,
    merge_intervals,
    passband_within_any,
    snap_passband_to_grid,
    subtract_intervals,
)
from orchestrator.optical.utils.datadiff import DiffResult
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import rehydrate_optical_module_block
from orchestrator.optical.workflows.shared import active_instance_selector_by_block_type, used_port_names_on_node

logger = get_logger(__name__)

#: Rejecting placeholder path Choice value offered when no optical path resolves.
#: Single home for the message previously defined in the spectrum create module.
NO_OPTICAL_PATH_FOUND_MSG = (
    "No optical path found, please adjust the routing constraints in the previous step or validate fibers in the path."
)

# ``AbstractOpticalNodeBlockInactive.subscription_instance_id``
Node = UUIDstr
# A path graph vertex: the node instance id, or ``"<node instance id>#<shelf>"`` on a Groove G30
Vertex = str
# ``AbstractOpticalOlsPortBlockInactive.subscription_instance_id``
Port = UUIDstr
Edge = tuple[Port, Port]
NeighborConnection = tuple[Vertex, Edge]
Graph = dict[Vertex, list[NeighborConnection]]  # {vertex: [(neighbor_vertex, (port_a_id, port_b_id)), ...]}
Path = list[Port]  # list of ``AbstractOpticalOlsPortBlockInactive.subscription_instance_id``

_SHELF_SEPARATOR = "#"


class OwnOccupancy(NamedTuple):
    """A service's own circuits to forgive when computing the free frequencies (modify workflows).

    The stored used passbands still contain the circuit being replaced (the modify
    form runs before any device change), so an unchanged passband on the same path
    would block itself. Forgiveness is scoped to the service's current path: the
    old passbands are subtracted only on the given port instance ids, everywhere
    else the strict overlap test applies — a same-frequency interval on another
    pipe belongs to a different service (spatial frequency reuse) and still blocks.
    """

    passbands: tuple[tuple[int, int], ...]
    port_ids: frozenset[str]


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


def load_spectrum_section(section_id: UUIDstr) -> OpticalSpectrumSectionBlockProvisioning:
    """Load an Optical Spectrum Section block from its subscription instance id."""
    return cast(
        OpticalSpectrumSectionBlockProvisioning,
        ProductBlockModel.from_db(UUID(str(section_id))),
    )


def optical_spectrum_block_from_state(
    optical_module_block: OpticalSpectrumServiceBlockInactive
    | OpticalSpectrumServiceBlockProvisioning
    | dict[str, Any]
    | None,
) -> OpticalSpectrumServiceBlockProvisioning:
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
    if isinstance(optical_module_block, OpticalSpectrumServiceBlockInactive):
        return cast(OpticalSpectrumServiceBlockProvisioning, optical_module_block)
    return cast(
        OpticalSpectrumServiceBlockProvisioning,
        rehydrate_optical_module_block(optical_module_block, block_description="Optical Spectrum"),
    )


def _optical_spectrum_block_of_subscription(subscription: SubscriptionModel) -> OpticalSpectrumServiceBlockInactive:
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
    return cast(OpticalSpectrumServiceBlockInactive, spectrum)


def optical_spectrum_subscription_description(
    subscription: SubscriptionModel,
    optical_module_block: OpticalSpectrumServiceBlockInactive | None = None,
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
    optical_module_block: OpticalSpectrumServiceBlockInactive | None = None,
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


@step("Provisioning optical spectrum sections")
def provision_optical_sections(optical_module_block: OpticalSpectrumServiceBlockInactive) -> State:
    """Ensure the optical circuit of every spectrum section on the devices.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``, the same block the rest of the shipped
    block steps act on. The device push is the single idempotent
    optical-circuit primitive (the FlexILS circuits are found by identity or
    created, and drifted attributes converge in place), so the step is shared
    by the shipped create and reconcile workflows.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    passband = block.optical_spectrum_passband
    spectrum_name = block.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    snapped = snap_passband_to_grid(passband, FLEXILS_SPECTRAL_GRID_MHZ)
    snapped_changed = tuple(snapped) != tuple(passband)
    if snapped_changed:
        logger.warning(
            "Snapping off-grid spectrum passband to the 12.5 GHz grid",
            expected_passband=list(passband),
            snapped_passband=list(snapped),
        )
        block.optical_spectrum_passband = snapped
        passband = snapped
    carrier = (int(0.5 * (passband[0] + passband[1])), passband[1] - passband[0])
    circuit_identifier = str(block.subscription_instance_id)
    results = {}
    for section in block.optical_spectrum_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        results[src_node.management.optical_module_node_fqdn] = ensure_optical_circuit(
            src_node,
            section,
            spectrum_name,
            passband,
            carrier,
            label=spectrum_name,
            circuit_identifier=circuit_identifier,
        )

    state: State = {"configuration_results": results}
    if snapped_changed:
        state[OPTICAL_MODULE_BLOCK_STATE_KEY] = block
    return state


@step("Updating the available passbands of any Open Line System port in the path")
def refresh_optical_spectrum_used_passbands(
    optical_module_block: OpticalSpectrumServiceBlockInactive,
    old_section_ids: list[UUIDstr] | None = None,
) -> State:
    """Refresh the used passbands of the Open Line System ports in the path from the devices.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``. The ports owned by the spectrum
    subscription (the add/drop ports) are refreshed in the returned block, which
    the following save step persists; the foreign ports (the express line ports
    owned by the pipe subscriptions) are persisted under their own owner
    subscription by this step, because the spectrum block save skips foreign
    instances. The step is shared by the shipped create, modify, terminate and
    reconcile workflows.

    After a path change the replaced sections are also refreshed from the
    ``old_section_ids`` state key (snapshotted by the update step of the shipped
    modify workflow): their ports would otherwise keep stale "occupied"
    passbands in the database and future path computations would wrongly
    exclude them. Sections already in the current block are skipped.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
        old_section_ids: Subscription instance ids of the sections before the
            modification (only present in the modify workflow state).
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    foreign_ports = update_used_passbands(block)
    if old_section_ids:
        current_ids = {str(section.subscription_instance_id) for section in block.optical_spectrum_sections}
        replaced = [
            load_spectrum_section(section_id) for section_id in old_section_ids if str(section_id) not in current_ids
        ]
        foreign_ports += refresh_sections_used_passbands(replaced, str(block.owner_subscription_id))
    save_foreign_passband_ports(foreign_ports)

    return {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


@step("Verifying optical spectrum sections")
def verify_optical_spectrum_sections(optical_module_block: OpticalSpectrumServiceBlockInactive) -> State:
    """Verify the optical circuit of every spectrum section against the devices.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``: the block is re-hydrated from its
    serialized form (see :func:`optical_spectrum_block_from_state`) and every
    section is verified on the source Optical Node of the section. The step is
    read-only and is shared by the shipped validate and reconcile workflows.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    spectrum_name = block.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    passband = block.optical_spectrum_passband
    central_frequency = int((passband[0] + passband[1]) / 2)
    bandwidth = passband[1] - passband[0]
    carrier = (
        central_frequency,
        bandwidth,
    )
    circuit_identifier = str(block.subscription_instance_id)
    for section in block.optical_spectrum_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        validate_optical_circuit(
            src_node,
            section,
            spectrum_name,
            passband,
            carrier,
            label=spectrum_name,
            circuit_identifier=circuit_identifier,
        )

    return {}


def delete_optical_spectrum_sections(
    sections: Sequence[OpticalSpectrumSectionBlockProvisioning],
    passband: Passband,
    spectrum_name: str,
    circuit_identifier: str,
) -> dict[str, DiffResult]:
    """Delete the optical circuit of every spectrum section and any OEL it leaves unused.

    This is the shared teardown of the spectrum family: callers pass the sections to
    tear down (the current ones when terminating, the previous ones when a modify
    changes the path) and get back one diff per touched source node. It is the single
    place where the OEL teardown rule is enforced, so no caller has to remember it.

    Every section's OSNC is deleted first. Only after all of them are gone is the OEL
    of each source node deleted, and only when no other OSNC on the node still
    references it: an OEL may be shared by more than one OSNC on FlexILS, so while
    another OSNC still needs it the OEL is left in place (see
    :func:`orchestrator.optical.hal.spectrum.delete_optical_circuit_oel`, a no-op on
    platforms without OELs). The node's OEL is deleted at most once even when several
    sections share the source node.

    Args:
        sections: The optical spectrum sections to delete.
        passband: The passband the circuits were deployed with.
        spectrum_name: The user-facing name of the optical spectrum.
        circuit_identifier: The subscription instance id of the circuit; used as the
            OSNC CKTIDSUFFIX and as the OEL AID.

    Returns:
        The diff of each source node's OSNC keyed by its FQDN and the diff of the OEL
        keyed by ``"<FQDN>:OEL"``.
    """
    results: dict[str, DiffResult] = {}
    for section in sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        results[src_node.management.optical_module_node_fqdn] = delete_optical_circuit(
            src_node,
            section,
            spectrum_name,
            passband,
            circuit_identifier=circuit_identifier,
        )

    seen_oel_nodes: set[str] = set()
    for section in sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        node_id = str(src_node.subscription_instance_id)
        if node_id in seen_oel_nodes:
            continue
        seen_oel_nodes.add(node_id)
        results[f"{src_node.management.optical_module_node_fqdn}:OEL"] = delete_optical_circuit_oel(
            src_node,
            circuit_identifier,
        )

    return results


def check_optical_spectrum_add_drop_port_availability(
    node_block: AbstractOpticalNodeBlockInactive,
    port_name: str,
    exclude_subscription_id: str | None = None,
) -> None:
    """Raise if the given add/drop port is already in use by another subscription.

    This is the execution-time guard of the shipped create workflow: the form
    already excludes the ports in use, but the check is repeated when the port
    blocks are created, so a consumer bypassing the form (or a concurrent create
    between form submission and execution) is still guarded. This is an
    application-level check only: the module ships no database migrations, so no
    unique constraint enforces the uniqueness in the database (residual TOCTOU
    race between the check and the block save).

    Args:
        node_block: Optical Node block hosting the add/drop port.
        port_name: Name of the add/drop port of the node.
        exclude_subscription_id: Subscription id owning the port, so it never
            conflicts with itself.

    Raises:
        ValueError: If another subscription already uses the port on the node.
    """
    used_ports = used_port_names_on_node(node_block, exclude_subscription_id=exclude_subscription_id)
    if port_name in used_ports:
        msg = (
            f"Port {port_name} on node {node_block.management.optical_module_node_fqdn} "
            "is already in use by another subscription"
        )
        raise ValueError(msg)


def _port_blocks_passband(
    port: AbstractOpticalOlsPortBlockInactive,
    own_occupancy: OwnOccupancy | None,
) -> list[tuple[int, int]]:
    """Return the stored used passbands of a port, minus the service's own ones on its own path.

    On the ports of the service's own current path the service's old passbands are
    subtracted (in-memory equivalent of freeing the circuit being replaced); on every
    other port the stored passbands are returned unchanged.
    """
    used = [(int(start), int(end)) for start, end in port.optical_passbands]
    if own_occupancy is not None and str(port.subscription_instance_id) in own_occupancy.port_ids:
        return subtract_intervals(used, own_occupancy.passbands)
    return used


def _is_g30(node: AbstractOpticalNodeBlockInactive) -> bool:
    return (
        node.management.optical_module_node_vendor,
        node.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.GROOVE_G30)


def graph_vertex(node: AbstractOpticalNodeBlockInactive, port_name: str | None) -> Vertex:
    """Return the path graph vertex of a port of the given Optical Node.

    A Groove G30 port on shelf X only connects to ports on shelf X, so every shelf of a
    G30 node is its own vertex (``"<node instance id>#<shelf>"``). Any other node (e.g. a
    FlexILS, whose express routes are any-to-any) is a single vertex, its instance id.

    Args:
        node: The Optical Node block hosting the port.
        port_name: Device name of the port (only used for the Groove G30).

    Returns:
        The vertex of the port in the path graph.
    """
    node_id = str(node.subscription_instance_id)
    if _is_g30(node) and port_name:
        return f"{node_id}{_SHELF_SEPARATOR}{g30_shelf_of_port(port_name)}"
    return node_id


def physical_node(vertex: Vertex) -> Node:
    """Return the Optical Node instance id of a path graph vertex."""
    return vertex.split(_SHELF_SEPARATOR, 1)[0]


@dataclass
class PathGraph:
    """The topology graph of the active optical pipes, frequency-agnostic.

    Attributes:
        adjacency: ``{vertex: [(neighbor vertex, (local port id, remote port id)), ...]}``;
            parallel pipes between the same vertices are distinct entries.
        port_names: Device port name of every pipe termination port id in the graph.
        line_ports: The port ids of the terminations that are OLS line ports (degrees).
    """

    adjacency: Graph = field(default_factory=dict)
    port_names: dict[Port, str] = field(default_factory=dict)
    line_ports: set[Port] = field(default_factory=set)

    def vertices_of(self, node_id: Node) -> list[Vertex]:
        """Return the vertices of the given Optical Node (one per shelf on a Groove G30)."""
        return sorted(vertex for vertex in self.adjacency if physical_node(vertex) == str(node_id))

    def restricted_endpoint(self, vertex: Vertex, allowed_port_names: Iterable[str]) -> "PathGraph":
        """Return a copy where ``vertex`` only connects through the allowed local line ports.

        Used at the source and destination nodes: only the line ports (degrees) the
        add/drop port can reach internally may carry the path. Pipes terminated on
        another add/drop port of the node (e.g. a leased spectrum handed off on an
        add/drop port, joined by a local cross-connection) are kept: the internal
        connectivity only describes the degrees. Both the outgoing and incoming entries
        of the vertex are filtered; paths are loopless, so no other route is affected.
        """
        allowed = set(allowed_port_names)

        def blocked(port: Port) -> bool:
            return port in self.line_ports and self.port_names.get(port) not in allowed

        adjacency: Graph = {}
        for current, neighbors in self.adjacency.items():
            adjacency[current] = [
                (neighbor, (local_port, remote_port))
                for neighbor, (local_port, remote_port) in neighbors
                if not (current == vertex and blocked(local_port)) and not (neighbor == vertex and blocked(remote_port))
            ]
        return PathGraph(adjacency=adjacency, port_names=self.port_names, line_ports=self.line_ports)


def build_graph_from_pipes(
    pipes: Iterable[AbstractOpticalPipeBlockInactive],
    exclude_node_instance_ids: list[UUIDstr] | None = None,
    exclude_span_instance_ids: list[UUIDstr] | None = None,
) -> PathGraph:
    """Build the frequency-agnostic topology graph from the given optical pipes.

    A pipe is included only when both of its ``optical_pipe_terminations`` are Open
    Line System ports (``AbstractOpticalOlsPortBlockInactive``, i.e. role ``OLS_LINE``
    or ``OLS_ADD_DROP``). Any pipe terminated on a transponder line/client port or on
    a coherent pluggable is skipped entirely. The spectral occupation of the ports is
    not considered here: it is evaluated on the selected path afterwards (see
    :func:`available_passbands_for_path`).

    Args:
        pipes: The optical pipe blocks to build the graph from.
        exclude_node_instance_ids: Subscription instance ids of Optical Node blocks to exclude.
        exclude_span_instance_ids: Subscription instance ids of pipe blocks to exclude.

    Returns:
        The topology graph (see :class:`PathGraph`, vertices from :func:`graph_vertex`).

    Raises:
        ValueError: If a pipe does not have exactly two terminations.
    """
    exclude_node_sub_id_set = set(exclude_node_instance_ids or [])
    exclude_span_sub_id_set = set(exclude_span_instance_ids or [])
    logger.debug(
        "Exclusion sets for path computation",
        exclude_node_instance_ids=sorted(exclude_node_sub_id_set),
        exclude_span_instance_ids=sorted(exclude_span_sub_id_set),
    )

    graph = PathGraph()
    sifted: list[str] = []
    for pipe in pipes:
        pipe_name = pipe.optical_pipe_name
        pipe_owner = str(pipe.subscription_instance_id)
        if pipe_owner in exclude_span_sub_id_set:
            logger.debug("Skipping pipe: excluded instance", pipe_name=pipe_name, pipe_owner=pipe_owner)
            continue
        terminations = pipe.optical_pipe_terminations
        if terminations is None or len(terminations) != 2:  # noqa: PLR2004
            msg = f"Optical pipe {pipe.optical_pipe_name!r} must have exactly two terminations"
            raise ValueError(msg)
        if not all(isinstance(port, AbstractOpticalOlsPortBlockInactive) for port in terminations):
            logger.debug(
                "Skipping pipe: non-OLS termination",
                pipe_name=pipe_name,
                pipe_owner=pipe_owner,
                roles=[str(port.optical_port_role) for port in terminations],
            )
            continue
        port_a = cast(AbstractOpticalOlsPortBlockInactive, terminations[0])
        port_b = cast(AbstractOpticalOlsPortBlockInactive, terminations[1])
        if any(
            str(port.optical_port_host_node.subscription_instance_id) in exclude_node_sub_id_set
            for port in (port_a, port_b)
        ):
            logger.debug("Skipping pipe: excluded node", pipe_name=pipe_name, pipe_owner=pipe_owner)
            continue

        id_port_a = str(port_a.subscription_instance_id)
        id_port_b = str(port_b.subscription_instance_id)
        vertex_a = graph_vertex(port_a.optical_port_host_node, port_a.optical_port_name)
        vertex_b = graph_vertex(port_b.optical_port_host_node, port_b.optical_port_name)
        graph.adjacency.setdefault(vertex_a, []).append((vertex_b, (id_port_a, id_port_b)))
        graph.adjacency.setdefault(vertex_b, []).append((vertex_a, (id_port_b, id_port_a)))
        graph.port_names[id_port_a] = port_a.optical_port_name or ""
        graph.port_names[id_port_b] = port_b.optical_port_name or ""
        graph.line_ports.update(
            port_id
            for port_id, port in ((id_port_a, port_a), (id_port_b, port_b))
            if port.optical_port_role is OpticalPortRole.OLS_LINE
        )
        sifted.append(f"{pipe_name} ({port_a.optical_port_name} --- {port_b.optical_port_name})")

    logger.debug(
        "Graph edges for path computation",
        sifted_pipes=sifted,
        num_vertices=len(graph.adjacency),
        num_edges=sum(len(edges) for edges in graph.adjacency.values()) // 2,
    )
    return graph


def _load_active_pipes() -> list[AbstractOpticalPipeBlockInactive]:
    """Load the optical pipe blocks of all active pipe subscriptions.

    Block-based listing: pipe blocks are enumerated by block name and loaded via the
    product block registry, without product types or subscription models.

    Returns:
        The active Fiber Span, Fiber Patch and Leased Spectrum pipe blocks.
    """
    pipes = pipe_blocks_all([SubscriptionLifecycle.ACTIVE])
    logger.debug("Loaded active pipes for path computation", total=len(pipes))
    return pipes


def build_constrained_graph(
    exclude_node_instance_ids: list[UUIDstr] | None = None,
    exclude_span_instance_ids: list[UUIDstr] | None = None,
) -> PathGraph:
    """Build the topology graph from all active optical pipes.

    The active Fiber Span, Fiber Patch and Leased Spectrum blocks are loaded
    from the database and delegated to :func:`build_graph_from_pipes`.

    Args:
        exclude_node_instance_ids: Subscription instance ids of Optical Node blocks to exclude.
        exclude_span_instance_ids: Subscription instance ids of pipe blocks to exclude.

    Returns:
        The topology graph (see :func:`build_graph_from_pipes`).
    """
    return build_graph_from_pipes(_load_active_pipes(), exclude_node_instance_ids, exclude_span_instance_ids)


class _RoutedPath(NamedTuple):
    """A path through the graph: its vertices and the port pair of every hop."""

    vertices: tuple[Vertex, ...]
    edges: tuple[Edge, ...]

    @property
    def ports(self) -> Path:
        return [port for edge in self.edges for port in edge]

    def is_loopless(self) -> bool:
        nodes = [physical_node(vertex) for vertex in self.vertices]
        return len(nodes) == len(set(nodes))


def _bfs_shortest_path(
    graph: PathGraph,
    src: Vertex,
    dst: Vertex,
    banned_vertices: set[Vertex],
    banned_edges: set[tuple[Vertex, Edge]],
) -> _RoutedPath | None:
    """Return a minimum-hop path avoiding the banned vertices/edges, or None (BFS)."""
    previous: dict[Vertex, tuple[Vertex, Edge] | None] = {src: None}
    queue = deque([src])
    while queue:
        current = queue.popleft()
        if current == dst:
            vertices: list[Vertex] = [dst]
            edges: list[Edge] = []
            while (hop := previous[vertices[-1]]) is not None:
                vertices.append(hop[0])
                edges.append(hop[1])
            return _RoutedPath(tuple(reversed(vertices)), tuple(reversed(edges)))
        for neighbor, edge in graph.adjacency.get(current, []):
            if neighbor in previous or neighbor in banned_vertices or (current, edge) in banned_edges:
                continue
            previous[neighbor] = (current, edge)
            queue.append(neighbor)
    return None


def _path_sort_key(path: _RoutedPath) -> tuple[int, tuple[Edge, ...]]:
    return len(path.edges), path.edges


def _k_shortest_routed_paths(graph: PathGraph, src: Vertex, dst: Vertex, k: int) -> list[_RoutedPath]:
    """Yen's K loopless shortest paths by hop count; a physical node is never revisited."""
    if src == dst:
        return [_RoutedPath((src,), ())]
    first = _bfs_shortest_path(graph, src, dst, set(), set())
    if first is None:
        return []
    accepted: list[_RoutedPath] = [first]
    candidates: list[tuple[tuple[int, tuple[Edge, ...]], _RoutedPath]] = []
    seen: set[tuple[Edge, ...]] = {first.edges}
    while len(accepted) < k:
        last = accepted[-1]
        for spur_index in range(len(last.edges)):
            root_vertices = last.vertices[: spur_index + 1]
            root_edges = last.edges[:spur_index]
            spur = root_vertices[-1]
            banned_edges = {
                (spur, path.edges[spur_index])
                for path in accepted
                if path.vertices[: spur_index + 1] == root_vertices and path.edges[:spur_index] == root_edges
            }
            root_nodes = {physical_node(vertex) for vertex in root_vertices[:-1]}
            banned_vertices = {vertex for vertex in graph.adjacency if physical_node(vertex) in root_nodes}
            spur_path = _bfs_shortest_path(graph, spur, dst, banned_vertices, banned_edges)
            if spur_path is None:
                continue
            candidate = _RoutedPath(root_vertices[:-1] + spur_path.vertices, root_edges + spur_path.edges)
            if candidate.edges in seen or not candidate.is_loopless():
                continue
            seen.add(candidate.edges)
            heapq.heappush(candidates, (_path_sort_key(candidate), candidate))
        if not candidates:
            break
        accepted.append(heapq.heappop(candidates)[1])
    return [path for path in accepted if path.is_loopless()]


def k_shortest_paths(graph: PathGraph, src: Vertex, dst: Vertex, k: int) -> list[Path]:
    """Find the K loopless shortest paths from src to dst, where the cost is the hop count.

    Yen's algorithm on the topology graph; parallel pipes between the same two vertices
    are distinct paths. Paths are returned from the shortest, ties broken
    deterministically by their port ids.

    Args:
        graph: The topology graph.
        src: The source vertex.
        dst: The destination vertex.
        k: The maximum number of paths.

    Returns:
        Up to ``k`` paths, each a list of Optical Port subscription instance ids.

    Raises:
        NoOpticalPathFoundError: If no path exists between the source and destination.
    """
    paths = _k_shortest_routed_paths(graph, src, dst, k)
    if not paths:
        raise NoOpticalPathFoundError(src=src, dst=dst)
    return [path.ports for path in paths]


class PathEndpoint(NamedTuple):
    """An end of an optical path: the add/drop port of an Optical Node."""

    node: AbstractOpticalNodeBlockInactive
    add_drop_port_name: str


@dataclass(frozen=True)
class OpticalPathCandidates:
    """The K shortest paths between two add/drop ports, with the endpoint internal routes.

    Attributes:
        paths: The candidate paths, each the list of the OLS port instance ids between the
            two add/drop ports (the first and last are line ports of the endpoint nodes).
        src_edges: The internal routes of the source add/drop port, by line port name.
        dst_edges: The internal routes of the destination add/drop port, by line port name.
    """

    paths: list[Path]
    src_edges: dict[str, IntraNodeEdge]
    dst_edges: dict[str, IntraNodeEdge]


def _endpoint_edges(endpoint: PathEndpoint) -> dict[str, IntraNodeEdge]:
    edges = retrieve_add_drop_connectivity(
        cast(AnyOpticalNodeBlockProvisioningUnion, endpoint.node), endpoint.add_drop_port_name
    )
    logger.debug(
        "Internal routes of add/drop port",
        node=_node_fqdn(endpoint.node),
        add_drop_port=endpoint.add_drop_port_name,
        line_ports=[edge.line_port for edge in edges],
    )
    return {edge.line_port: edge for edge in edges}


def _waypoint_stops(
    graph: PathGraph,
    src_vertex: Vertex,
    dst_vertex: Vertex,
    waypoint_node_instance_ids: list[UUIDstr] | None,
) -> list[list[Vertex]]:
    """Return the candidate vertices of every stop, collapsing consecutive duplicate nodes."""
    stops: list[list[Vertex]] = [[src_vertex]]
    for node_id in waypoint_node_instance_ids or []:
        if physical_node(stops[-1][0]) != str(node_id):
            stops.append(graph.vertices_of(node_id) or [str(node_id)])
    if physical_node(stops[-1][0]) == physical_node(dst_vertex):
        stops[-1] = [dst_vertex]
    else:
        stops.append([dst_vertex])
    return stops


def _extend_paths(
    graph: PathGraph,
    partial: dict[Vertex, list[_RoutedPath]],
    end_vertex: Vertex,
    k: int,
) -> list[_RoutedPath]:
    """Extend the partial paths (keyed by their end vertex) to ``end_vertex``; keep the K best."""
    combined: list[_RoutedPath] = []
    for start_vertex, prefixes in partial.items():
        for segment in _k_shortest_routed_paths(graph, start_vertex, end_vertex, k):
            for prefix in prefixes:
                path = _RoutedPath(prefix.vertices + segment.vertices[1:], prefix.edges + segment.edges)
                if path.is_loopless():
                    combined.append(path)
    return sorted(combined, key=_path_sort_key)[:k]


def k_shortest_paths_through_waypoints(
    graph: PathGraph,
    src_vertex: Vertex,
    dst_vertex: Vertex,
    waypoint_node_instance_ids: list[UUIDstr] | None,
    k: int,
) -> list[Path]:
    """Find the K shortest loopless paths from source to destination through the ordered waypoints.

    The path is computed segment by segment between consecutive stops; a waypoint is a
    physical Optical Node, satisfied by any of its vertices (any shelf of a Groove G30),
    and consecutive segments meet at the same vertex. Consecutive duplicate stops are
    collapsed; combined paths revisiting a physical node are dropped.

    Args:
        graph: The topology graph (endpoint restrictions already applied).
        src_vertex: The source vertex.
        dst_vertex: The destination vertex.
        waypoint_node_instance_ids: Ordered subscription instance ids of the Optical Node
            blocks the path must traverse.
        k: The maximum number of paths.

    Returns:
        Up to ``k`` paths, shortest first.

    Raises:
        NoOpticalPathFoundError: If no path traverses all the stops.
    """
    partial: dict[Vertex, list[_RoutedPath]] = {src_vertex: [_RoutedPath((src_vertex,), ())]}
    for next_stop in _waypoint_stops(graph, src_vertex, dst_vertex, waypoint_node_instance_ids)[1:]:
        extended = {
            end_vertex: paths for end_vertex in next_stop if (paths := _extend_paths(graph, partial, end_vertex, k))
        }
        if not extended:
            raise NoOpticalPathFoundError(src=src_vertex, dst=dst_vertex)
        partial = extended

    paths = sorted((path for paths in partial.values() for path in paths), key=_path_sort_key)
    unique: dict[tuple[Edge, ...], Path] = {}
    for path in paths:
        unique.setdefault(path.edges, path.ports)
    if not unique:
        raise NoOpticalPathFoundError(src=src_vertex, dst=dst_vertex)
    return list(unique.values())[:k]


def compute_optical_path_candidates(
    src: PathEndpoint,
    dst: PathEndpoint,
    waypoint_node_instance_ids: list[UUIDstr] | None = None,
    exclude_node_instance_ids: list[UUIDstr] | None = None,
    exclude_span_instance_ids: list[UUIDstr] | None = None,
    k: int | None = None,
) -> OpticalPathCandidates:
    """Compute the K shortest paths between two add/drop ports, regardless of frequency.

    The internal connectivity of the source and destination nodes is fetched from the
    devices: the path may only leave the source node (and enter the destination node)
    through a line port the add/drop port can be connected to. The topology graph is
    built once from the active optical pipes; the frequencies are evaluated afterwards on
    the selected path (see :func:`available_passbands_for_path`).

    Args:
        src: The source add/drop port.
        dst: The destination add/drop port.
        waypoint_node_instance_ids: Ordered subscription instance ids of the intermediate
            Optical Node blocks the path must traverse.
        exclude_node_instance_ids: Subscription instance ids of Optical Node blocks to exclude.
        exclude_span_instance_ids: Subscription instance ids of pipe blocks to exclude.
        k: The maximum number of paths, defaults to ``OPTICAL_PATH_K``.

    Returns:
        The candidate paths with the internal routes of both endpoints.

    Raises:
        NoOpticalPathFoundError: If no path exists.
    """
    k = k if k is not None else get_settings().path_k
    src_edges = _endpoint_edges(src)
    dst_edges = _endpoint_edges(dst)
    src_vertex = graph_vertex(src.node, src.add_drop_port_name)
    dst_vertex = graph_vertex(dst.node, dst.add_drop_port_name)
    graph = (
        build_constrained_graph(exclude_node_instance_ids, exclude_span_instance_ids)
        .restricted_endpoint(src_vertex, src_edges)
        .restricted_endpoint(dst_vertex, dst_edges)
    )
    try:
        paths = k_shortest_paths_through_waypoints(graph, src_vertex, dst_vertex, waypoint_node_instance_ids, k)
    except NoOpticalPathFoundError as exc:
        raise NoOpticalPathFoundError(src=_node_fqdn(src.node), dst=_node_fqdn(dst.node)) from exc
    return OpticalPathCandidates(paths=paths, src_edges=src_edges, dst_edges=dst_edges)


def available_passbands_for_path(
    path: Path,
    src_edge: IntraNodeEdge | None = None,
    dst_edge: IntraNodeEdge | None = None,
    own_occupancy: OwnOccupancy | None = None,
) -> list[tuple[int, int]]:
    """Return the free frequency ranges along a path, including the endpoint internal routes.

    The used passbands are the union of the stored ``optical_passbands`` of every OLS port
    of the path and of the ``used_passbands`` of the two internal routes (add/drop port to
    line port) of the endpoints. In modify workflows the service's own passbands are
    forgiven on its own current ports and on the endpoint internal routes.

    Args:
        path: The OLS port instance ids of the path.
        src_edge: The internal route of the source add/drop port to the first line port.
        dst_edge: The internal route of the destination add/drop port to the last line port.
        own_occupancy: The service's own current circuits (modify workflows).

    Returns:
        The sorted free ``[start, end)`` ranges of the OLS band (MHz).
    """
    used: list[tuple[int, int]] = []
    for port_id in path:
        used.extend(_port_blocks_passband(_load_ols_port(port_id), own_occupancy))
    for edge in (src_edge, dst_edge):
        if edge is None:
            continue
        edge_used = list(edge.used_passbands)
        if own_occupancy is not None:
            edge_used = subtract_intervals(merge_intervals(edge_used), own_occupancy.passbands)
        used.extend(edge_used)
    return free_intervals(used)


def candidate_available_passbands(
    candidates: OpticalPathCandidates,
    path: Path,
    own_occupancy: OwnOccupancy | None = None,
) -> list[tuple[int, int]]:
    """Return the free frequency ranges of one of the candidate paths.

    The endpoint internal routes are picked from the candidates by the first and last
    line port of the path (fetched once by :func:`compute_optical_path_candidates`).

    Args:
        candidates: The candidates the path was chosen from.
        path: The chosen path (interior OLS port instance ids).
        own_occupancy: The service's own current circuits (modify workflows).

    Returns:
        The sorted free ``[start, end)`` ranges of the OLS band (MHz).
    """
    src_edge = dst_edge = None
    if path:
        src_edge = candidates.src_edges.get(_load_ols_port(path[0]).optical_port_name or "")
        dst_edge = candidates.dst_edges.get(_load_ols_port(path[-1]).optical_port_name or "")
    return available_passbands_for_path(path, src_edge, dst_edge, own_occupancy)


def ensure_passband_available(passband: tuple[int, int], available: Sequence[tuple[int, int]] | None) -> None:
    """Raise if the passband is not entirely within one of the available frequency ranges.

    Args:
        passband: The ``[start, end)`` passband (MHz) chosen by the user.
        available: The free ranges of the selected path; ``None`` skips the check
            (no path was computed, e.g. a modify that keeps the current path).

    Raises:
        ValueError: If the passband falls (even partially) outside every free range.
    """
    if available is None or passband_within_any(passband, available):
        return
    msg = (
        f"The passband {format_passbands_thz([passband])} is not available on the selected path. "
        f"Available frequency ranges: {format_passbands_thz(available)}"
    )
    raise ValueError(msg)


def optical_passband_form(
    title: str,
    available: Sequence[tuple[int, int]] | None,
    default: Passband | None = None,
) -> type[FormPage]:
    """Return the frequency FormPage shown after the optical path is selected.

    The page lists the free frequency ranges of the selected path (see
    :func:`candidate_available_passbands`) in a read-only label and collects the
    passband (``frequency_min``/``frequency_max``), rejecting values that are not in
    order, not aligned to the FlexILS grid or not within a single free range.

    Args:
        title: The page title.
        available: The free ranges of the selected path; ``None`` skips the
            availability check (and the label says so).
        default: The prefilled passband (modify workflows).

    Returns:
        The frequency FormPage.
    """
    label = (
        f"Available frequency ranges on the selected path: {format_passbands_thz(available)}"
        if available is not None
        else "The available frequency ranges were not computed: no new path was selected."
    )
    defaults = {"frequency_min": default[0], "frequency_max": default[1]} if default is not None else {}

    class OpticalPassbandForm(FormPage):
        model_config = ConfigDict(title=title)

        available_frequency_ranges: Label = label
        frequency_min: Annotated[Frequency, Field(title="Start frequency (THz)", **_default("frequency_min", defaults))]
        frequency_max: Annotated[Frequency, Field(title="End frequency (THz)", **_default("frequency_max", defaults))]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "OpticalPassbandForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            ensure_passband_aligned_to_grid((self.frequency_min, self.frequency_max), FLEXILS_SPECTRAL_GRID_MHZ)
            ensure_passband_available((self.frequency_min, self.frequency_max), available)
            return self

    return OpticalPassbandForm


def _default(key: str, defaults: dict[str, Any]) -> dict[str, Any]:
    """Return the ``Field`` kwargs setting the default of ``key`` when one is given."""
    return {"default": defaults[key]} if key in defaults else {}


def format_passbands_thz(passbands: Sequence[tuple[int, int]]) -> str:
    """Return a human-readable list of frequency ranges in THz (e.g. ``191.3250-192.1000 THz``)."""
    if not passbands:
        return "none"
    return ", ".join(f"{start / 1_000_000:.4f}-{end / 1_000_000:.4f} THz" for start, end in passbands)


def _peer_of_line_port(
    port: AbstractOpticalPortBlockInactive,
    pipes: Sequence[AbstractOpticalPipeBlockInactive],
) -> tuple[AbstractOpticalPortBlockInactive | None, AbstractOpticalPipeBlockInactive | None]:
    """Return the peer termination of a line port and the pipe connecting them.

    Two passes, so transponder line ports and coherent pluggables resolve the
    same way. A transponder line port only exists as a pipe termination, so the
    first pass matches it by ``subscription_instance_id``. A coherent pluggable
    is owned by its own subscription while the pipe stores a copy with the same
    host node and port name, so the second pass matches it by host and name.

    Args:
        port: The line port (transponder line or coherent pluggable) to resolve.
        pipes: The active pipe blocks to search (span, patch and leased spectrum).

    Returns:
        The peer termination and its pipe, or ``(None, None)`` when unresolved.
    """
    port_id = str(port.subscription_instance_id)
    for pipe in pipes:
        terminations = pipe.optical_pipe_terminations or []
        if len(terminations) != 2:  # noqa: PLR2004
            continue
        ids = [str(t.subscription_instance_id) for t in terminations]
        if port_id in ids:
            peer = terminations[1] if ids[0] == port_id else terminations[0]
            logger.debug(
                "Resolved line port by pipe termination",
                port_id=port_id,
                port_role=str(port.optical_port_role),
                pipe_name=pipe.optical_pipe_name,
                pipe_owner=str(pipe.owner_subscription_id),
                peer_id=str(peer.subscription_instance_id),
                peer_role=str(peer.optical_port_role),
            )
            return peer, pipe
    if port.optical_port_role is OpticalPortRole.COHERENT_PLUGGABLE:
        host = port.optical_port_host_node
        host_id = str(host.subscription_instance_id) if host is not None else None
        port_name = port.optical_port_name
        if host_id is not None and port_name is not None:
            candidates: list[tuple[AbstractOpticalPortBlockInactive, AbstractOpticalPipeBlockInactive]] = []
            for pipe in pipes:
                terminations = pipe.optical_pipe_terminations or []
                if len(terminations) != 2:  # noqa: PLR2004
                    continue
                for index, termination in enumerate(terminations):
                    term_host = termination.optical_port_host_node
                    if (
                        term_host is not None
                        and str(term_host.subscription_instance_id) == host_id
                        and termination.optical_port_name == port_name
                    ):
                        candidates.append((terminations[1 - index], pipe))
            if candidates:
                if len(candidates) > 1:
                    logger.warning(
                        "Multiple pipes match coherent pluggable, using the first",
                        port_id=port_id,
                        host_id=host_id,
                        port_name=port_name,
                        num_matches=len(candidates),
                    )
                peer, pipe = candidates[0]
                logger.debug(
                    "Resolved coherent pluggable by host and port name",
                    port_id=port_id,
                    host_id=host_id,
                    port_name=port_name,
                    pipe_name=pipe.optical_pipe_name,
                    pipe_owner=str(pipe.owner_subscription_id),
                    peer_id=str(peer.subscription_instance_id),
                    peer_role=str(peer.optical_port_role),
                )
                return peer, pipe
    return None, None


def find_add_drop_ports(
    src_trx_port_block_id: UUIDstr,
    dst_trx_port_block_id: UUIDstr,
) -> tuple[AbstractOpticalPortBlockInactive, AbstractOpticalPortBlockInactive]:
    """Retrieve the add/drop ports connected to the transponder/transceiver ports.

    Each line port (a transponder line port or a coherent pluggable, which is
    both client and line) is resolved to the peer termination of the optical
    pipe it is attached to, searching every active pipe type (span, patch and
    leased spectrum) by termination instance id, with a host-and-name fallback
    for coherent pluggables (whose pipe stores a copy of the pluggable block).

    Args:
        src_trx_port_block_id: Subscription instance id of the source transponder port block.
        dst_trx_port_block_id: Subscription instance id of the destination transponder port block.

    Returns:
        The add/drop ports terminating the optical pipes connected to the transponder ports.

    Raises:
        NoOpticalPathFoundError: If the add/drop ports cannot be found.
    """
    src_trx_port = _load_port(src_trx_port_block_id)
    dst_trx_port = _load_port(dst_trx_port_block_id)

    pipes = _load_active_pipes()
    src_add_drop_port, src_pipe = _peer_of_line_port(src_trx_port, pipes)
    dst_add_drop_port, dst_pipe = _peer_of_line_port(dst_trx_port, pipes)

    if src_add_drop_port is None or dst_add_drop_port is None:
        logger.warning(
            "Could not resolve add/drop ports for line ports",
            src_port_id=str(src_trx_port_block_id),
            src_role=str(src_trx_port.optical_port_role),
            src_resolved=src_add_drop_port is not None,
            src_pipe=getattr(src_pipe, "optical_pipe_name", None),
            dst_port_id=str(dst_trx_port_block_id),
            dst_role=str(dst_trx_port.optical_port_role),
            dst_resolved=dst_add_drop_port is not None,
            dst_pipe=getattr(dst_pipe, "optical_pipe_name", None),
            num_pipes=len(pipes),
        )
        raise NoOpticalPathFoundError(src=src_trx_port_block_id, dst=dst_trx_port_block_id)

    return src_add_drop_port, dst_add_drop_port


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
        paths_dict[path_subscription_ids] = f"[{len(path) // 2} hops] {human_readable_path}"

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


def optical_spectrum_path_selector(
    candidates: OpticalPathCandidates,
    prompt: str = "Select an optical path.",
) -> type[Choice]:
    """Select an optical path among the K shortest candidate paths.

    The selected path MUST then be parsed using ``path.split(";")`` to obtain the sequence
    of subscription instance ids of the Optical Port blocks.

    Args:
        candidates: The candidate paths (see :func:`compute_optical_path_candidates`).
        prompt: A prompt message for the user to select an optical path.

    Returns:
        A Choice object whose values are the ``;``-joined port instance ids of each path
        and whose labels are the human-readable paths.
    """
    return human_readable_optical_spectrum_path_selector(candidates.paths, prompt)


def store_list_of_ports_into_spectrum_sections(
    optical_path: list[UUIDstr],
    optical_spectrum: OpticalSpectrumServiceBlockInactive | OpticalSpectrumServiceBlockProvisioning,
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


def validate_optical_spectrum_path(
    interior_port_ids: list[UUIDstr],
    src_endpoint: AbstractOpticalOlsPortBlockInactive,
    dst_endpoint: AbstractOpticalOlsPortBlockInactive,
) -> None:
    """Validate that the chosen path splits into single-platform sections.

    The path chosen in the form is the sequence of interior ports between the two
    endpoint add/drop ports; this helper assembles the full path and runs the same
    :func:`split_loaded_path_into_loaded_sections` validation the construct/divide
    steps run, so an unsplittable path is rejected while the form is filled in
    rather than after the subscription has been persisted.

    Args:
        interior_port_ids: The interior port subscription instance ids of the path.
        src_endpoint: The source add/drop port block.
        dst_endpoint: The destination add/drop port block.

    Raises:
        ValueError: If the path cannot be split into valid single-platform sections.
    """
    interior = [_load_ols_port(port_id) for port_id in interior_port_ids]
    split_loaded_path_into_loaded_sections([src_endpoint, *interior, dst_endpoint])


def store_loaded_sections_into_spectrum_block(
    sections: list[list[AbstractOpticalOlsPortBlockInactive]],
    optical_spectrum: OpticalSpectrumServiceBlockInactive | OpticalSpectrumServiceBlockProvisioning,
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
    if isinstance(optical_spectrum, OpticalSpectrumServiceBlockProvisioning):
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
    optical_spectrum: OpticalSpectrumServiceBlockInactive | OpticalSpectrumServiceBlockProvisioning,
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


def refresh_sections_used_passbands(
    sections: Sequence[OpticalSpectrumSectionBlockProvisioning],
    owner_subscription_id: UUIDstr,
) -> list[AbstractOpticalOlsPortBlockInactive]:
    """Refresh the ``optical_passbands`` of the OLS ports of the given sections from the devices.

    Both the express ports and the section add/drop ports are refreshed, for every
    OLS host node role of an add/drop multiplexer (see ``OADM_ROLES``). The refresh
    reads the live spectral occupation of each device, so it also frees ports whose
    circuits were deleted: call it with the replaced
    (old) sections after a path change, otherwise their database rows keep stale
    "occupied" passbands and future path computations wrongly exclude them.
    The refreshed foreign ports (owned by another subscription than the given
    owner) are returned so the caller can persist them under their own owner
    subscription (see :func:`save_foreign_passband_ports`); the owned ports are
    persisted by the caller's block save.

    Args:
        sections: The optical spectrum sections whose ports are refreshed.
        owner_subscription_id: Subscription id owning the refreshed block; ports
            owned by another subscription are reported as foreign.

    Returns:
        The refreshed ports whose owner subscription is not the given owner
        (foreign ports), deduplicated by subscription instance id.
    """
    passbands_by_device: dict[str, dict[str, list[tuple[int, int]]]] = {}
    foreign_ports: list[AbstractOpticalOlsPortBlockInactive] = []
    seen_foreign_port_ids: set[UUID] = set()
    for section in sections:
        ports = [
            *section.optical_spectrum_section_express_ports,
            *section.optical_spectrum_section_add_drop_ports,
        ]
        for port in ports:
            node = port.optical_port_host_node
            if node.optical_node_role not in OADM_ROLES:
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
            if (
                str(port.owner_subscription_id) != str(owner_subscription_id)
                and port.subscription_instance_id not in seen_foreign_port_ids
            ):
                seen_foreign_port_ids.add(port.subscription_instance_id)
                foreign_ports.append(port)
    return foreign_ports


def update_used_passbands(
    optical_spectrum: OpticalSpectrumServiceBlockProvisioning,
) -> list[AbstractOpticalOlsPortBlockInactive]:
    """Refresh the ``optical_passbands`` of every Open Line System port in the path from the devices.

    Both the express ports and the section add/drop ports are refreshed, for every
    OLS host node role of an add/drop multiplexer (see ``OADM_ROLES``). The express
    ports are the OLS line port blocks owned by the pipe
    subscriptions (fiber span, patch, leased spectrum), so they are *foreign* to the
    spectrum subscription and ``ProductBlockModel.save`` skips them when the spectrum
    block is persisted. The refreshed foreign ports are returned so the caller can
    persist them under their own owner subscription (see
    :func:`save_foreign_passband_ports`); the owned ports (the spectrum add/drop
    ports) are persisted by the caller's block save.

    Args:
        optical_spectrum: The Optical Spectrum block whose ports are refreshed.

    Returns:
        The refreshed ports whose owner subscription is not the spectrum owner
        (foreign ports), deduplicated by subscription instance id.
    """
    return refresh_sections_used_passbands(
        list(optical_spectrum.optical_spectrum_sections), str(optical_spectrum.owner_subscription_id)
    )


def save_foreign_passband_ports(ports: list[AbstractOpticalOlsPortBlockInactive]) -> None:
    """Persist the given foreign OLS port blocks under their owner subscription.

    The express ports of a spectrum section are the OLS line port blocks owned by the
    pipe subscriptions (fiber span, patch, leased spectrum); the section add/drop
    ports at platform boundaries may belong to a leased spectrum as well. Those ports
    are foreign to the spectrum subscription, so ``ProductBlockModel.save`` skips them
    when the spectrum block is saved and the refreshed ``optical_passbands`` would be
    lost. Saving each port block directly under its own owner subscription persists
    them without reloading (and thus without overwriting) the owner's block tree.

    The ports in the spectrum block tree carry the spectrum's lifecycle variant (they
    are converted to PROVISIONING when the spectrum is transitioned), while their
    owner subscription may be in a different lifecycle. The port is therefore reloaded
    under the owner's status before saving, so the lifecycle check of
    :meth:`ProductBlockModel.save` sees the matching specialized type.

    Args:
        ports: The refreshed foreign OLS port blocks, as returned by
            :func:`update_used_passbands`.
    """
    for port in ports:
        subscription = port.subscription
        if subscription is None:
            continue
        owner_status = SubscriptionLifecycle(subscription.status)
        persisted_port = cast(
            AbstractOpticalOlsPortBlockInactive,
            ProductBlockModel.from_db(port.subscription_instance_id, status=owner_status),
        )
        persisted_port.optical_passbands = port.optical_passbands
        persisted_port.save(
            subscription_id=port.owner_subscription_id,
            status=owner_status,
        )


def optical_node_selector_of_roles(roles: Sequence[OpticalNodeRole], prompt: str | None = None) -> type[Choice]:
    """Select an Optical Node from a list of nodes.

    Block-based selector: option values are the node block subscription instance ids
    and labels are the owner subscriptions' descriptions. No block is loaded and no
    subscription is queried by product type.

    Args:
        roles: A list of node roles to filter the Optical Nodes by.
        prompt: A custom prompt message for the selection. Defaults to None.

    Returns:
        A Choice class whose values are node block subscription instance ids.
    """
    base_choice = active_instance_selector_by_block_type(
        AbstractOpticalNodeBlockInactive,
        resource_values={"optical_node_role": [role.value for role in roles]},
    )
    options = {member.value: member.label for member in base_choice}

    if not prompt:
        prompt = f"Select an Optical Node of role {', '.join(role.value for role in roles)}"

    dynamic_class = Choice(prompt, zip(options.keys(), options.items(), strict=False))
    return cast(type[Choice], dynamic_class)


def multiple_optical_node_selector(
    roles: Sequence[OpticalNodeRole],
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
    optical_node_instance_id: UUIDstr,
    port_name: str,
    prompt: str | None = None,
) -> type[Choice]:
    """Create a Choice object for selecting a transceiver mode for a given port.

    Args:
        optical_node_instance_id: Subscription instance id of the Optical Node block.
        port_name: The name of the port belonging to the transceiver card.
            This can also be a client port of a CHM2T transponder.
        prompt: A custom prompt message for the selection. Defaults to None.

    Returns:
        A Choice class containing the prompt and a list of available transceiver modes.
    """
    node_block = cast(
        AnyOpticalNodeBlockProvisioningUnion,
        ProductBlockModel.from_db(UUID(str(optical_node_instance_id))),
    )
    modulations = retrieve_transceiver_modes(node_block, port_name)
    if not prompt:
        prompt = "Select a modulation"
    dynamic_class = Choice(prompt, zip(modulations, modulations, strict=False))
    return cast(type[Choice], dynamic_class)
