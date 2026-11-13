"""Unit tests for the optical spectrum path engine (database-free).

The path engine is exercised with product blocks built through
``model_construct``: no subscription is persisted and no device or database is
touched. Only the pure helpers are covered here (``build_graph_from_pipes``,
the K-shortest-paths engine, the endpoint restriction, the availability
computation and ``split_loaded_path_into_platform_sections``); the database
and device wrappers are monkeypatched.
"""

from uuid import uuid4

import pytest

from orchestrator.optical.hal.connectivity import IntraNodeEdge
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlockInactive,
    Platform,
    Vendor,
)
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import AbstractOpticalPipeBlockInactive
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_patch import OpticalFiberPatchBlockInactive
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import OpticalFiberSpanBlockInactive
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import OpticalLeasedSpectrumBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlockInactive,
    OpticalPortRole,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.transponder_line import (
    OpticalTransponderLinePortBlockInactive,
)
from orchestrator.optical.utils.custom_types.frequencies import OLS_BAND
from orchestrator.optical.workflows.optical_spectrum_service import shared
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    NoOpticalPathFoundError,
    OwnOccupancy,
    PathEndpoint,
    available_passbands_for_path,
    build_graph_from_pipes,
    compute_optical_path_candidates,
    ensure_passband_available,
    graph_vertex,
    k_shortest_paths,
    k_shortest_paths_through_waypoints,
    split_loaded_path_into_platform_sections,
)

PASSBAND = (196_000_000, 196_100_000)


def _node(
    platform: Platform = Platform.FLEXILS,
    vendor: Vendor = Vendor.NOKIA,
    *,
    fqdn: str = "node.test.local",
) -> NokiaFlexIlsBlockInactive:
    """Build a fake Optical Node block carrying the given vendor and platform."""
    return NokiaFlexIlsBlockInactive.model_construct(
        subscription_instance_id=uuid4(),
        owner_subscription_id=uuid4(),
        management=OpticalModuleNodeManagementBlockInactive.model_construct(
            optical_module_node_vendor=vendor,
            optical_module_node_platform=platform,
            optical_module_node_name=fqdn,
        ),
    )


def _ols_line(
    node: NokiaFlexIlsBlockInactive,
    *,
    passbands: list[tuple[int, int]] | None = None,
    name: str = "port-line",
) -> OlsLinePortBlockInactive:
    """Build a fake OLS line port hosted by the given node."""
    return OlsLinePortBlockInactive.model_construct(
        subscription_instance_id=uuid4(),
        owner_subscription_id=node.owner_subscription_id,
        optical_port_role=OpticalPortRole.OLS_LINE,
        optical_port_name=name,
        optical_port_host_node=node,
        optical_passbands=passbands or [],
    )


def _ols_add_drop(node: NokiaFlexIlsBlockInactive) -> OlsAddDropPortBlockInactive:
    """Build a fake OLS add/drop port hosted by the given node."""
    return OlsAddDropPortBlockInactive.model_construct(
        subscription_instance_id=uuid4(),
        owner_subscription_id=node.owner_subscription_id,
        optical_port_role=OpticalPortRole.OLS_ADD_DROP,
        optical_port_name="port-add-drop",
        optical_port_host_node=node,
        optical_passbands=[],
    )


def _transponder_line(node: NokiaFlexIlsBlockInactive) -> OpticalTransponderLinePortBlockInactive:
    """Build a fake transponder line port hosted by the given node."""
    return OpticalTransponderLinePortBlockInactive.model_construct(
        subscription_instance_id=uuid4(),
        owner_subscription_id=node.owner_subscription_id,
        optical_port_role=OpticalPortRole.TRANSPONDER_LINE,
        optical_port_name="port-trx",
        optical_port_host_node=node,
    )


def _pipe(pipe_class, port_a, port_b, *, name: str = "pipe") -> AbstractOpticalPipeBlockInactive:
    """Build a fake optical pipe block terminated on the two given ports."""
    return pipe_class.model_construct(
        subscription_instance_id=uuid4(),
        owner_subscription_id=uuid4(),
        optical_pipe_name=name,
        optical_pipe_terminations=[port_a, port_b],
    )


def _nid(node: NokiaFlexIlsBlockInactive) -> str:
    return str(node.subscription_instance_id)


def _pid(port: AbstractOpticalOlsPortBlockInactive) -> str:
    return str(port.subscription_instance_id)


def _neighbors(graph, node: NokiaFlexIlsBlockInactive) -> set[str]:
    return {neighbor for neighbor, _ in graph.adjacency.get(_nid(node), [])}


def _ports(*pipes: AbstractOpticalPipeBlockInactive) -> list[str]:
    """Return the port ids of the given pipes, in order (the path through them)."""
    return [_pid(port) for pipe in pipes for port in pipe.optical_pipe_terminations]


def _linear_topology() -> tuple:
    """Build a 4-node chain joined by an OLS span, patch and leased spectrum."""
    n1, n2, n3, n4 = _node(fqdn="n1"), _node(fqdn="n2"), _node(fqdn="n3"), _node(fqdn="n4")
    span = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1), _ols_line(n2), name="span")
    patch = _pipe(OpticalFiberPatchBlockInactive, _ols_add_drop(n2), _ols_add_drop(n3), name="patch")
    leased = _pipe(OpticalLeasedSpectrumBlockInactive, _ols_line(n3), _ols_line(n4), name="leased")
    return n1, n2, n3, n4, span, patch, leased


def _diamond() -> tuple:
    """Build a diamond n1-{n2,n3}-n4 plus a direct n1-n4 span and a parallel n1-n2 span.

    The shortest path is the direct span (1 hop), then three 2-hop paths (two via n2
    over the parallel spans, one via n3).
    """
    n1, n2, n3, n4 = _node(fqdn="n1"), _node(fqdn="n2"), _node(fqdn="n3"), _node(fqdn="n4")
    direct = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1, name="1-A-1-L1"), _ols_line(n4), name="direct")
    a12 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1, name="1-B-1-L1"), _ols_line(n2), name="a12")
    b12 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1, name="1-C-1-L1"), _ols_line(n2), name="b12")
    s24 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n2), _ols_line(n4), name="s24")
    s13 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1, name="1-D-1-L1"), _ols_line(n3), name="s13")
    s34 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n3), _ols_line(n4), name="s34")
    return (n1, n2, n3, n4), (direct, a12, b12, s24, s13, s34)


def test_build_graph_from_pipes_includes_ols_pipes_and_skips_non_ols() -> None:
    """Span, patch and leased OLS pipes are included; transponder-terminated pipes are not."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    transponder_pipe = _pipe(
        OpticalFiberSpanBlockInactive, _ols_line(n1), _transponder_line(n4), name="transponder-pipe"
    )

    graph = build_graph_from_pipes([span, patch, leased, transponder_pipe])

    assert set(graph.adjacency) == {_nid(node) for node in (n1, n2, n3, n4)}
    assert _neighbors(graph, n1) == {_nid(n2)}
    assert _neighbors(graph, n2) == {_nid(n1), _nid(n3)}
    assert _neighbors(graph, n3) == {_nid(n2), _nid(n4)}
    assert _neighbors(graph, n4) == {_nid(n3)}
    assert sum(len(edges) for edges in graph.adjacency.values()) == 6
    assert graph.port_names[_pid(span.optical_pipe_terminations[0])] == "port-line"


def test_build_graph_from_pipes_applies_exclusions_and_ignores_frequency() -> None:
    """Span and node exclusions drop the pipe; an occupied passband no longer does."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    pipes = [span, patch, leased]

    excluded_by_span = build_graph_from_pipes(pipes, exclude_span_instance_ids=[str(span.subscription_instance_id)])
    assert _nid(n1) not in excluded_by_span.adjacency

    excluded_by_node = build_graph_from_pipes(pipes, exclude_node_instance_ids=[_nid(n2)])
    assert _nid(n1) not in excluded_by_node.adjacency
    assert _nid(n2) not in excluded_by_node.adjacency

    occupied_span = _pipe(
        OpticalFiberSpanBlockInactive, _ols_line(n1, passbands=[PASSBAND]), _ols_line(n2), name="occupied"
    )
    assert _neighbors(build_graph_from_pipes([occupied_span, patch, leased]), n1) == {_nid(n2)}


def test_g30_nodes_are_split_by_shelf() -> None:
    """A Groove G30 port on shelf X only connects to ports on shelf X: one vertex per shelf."""
    n1, n3 = _node(fqdn="n1"), _node(fqdn="n3")
    g30 = _node(Platform.GROOVE_G30, fqdn="g30")
    in_shelf_1 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1), _ols_line(g30, name="port-1/3.3/1"), name="a")
    out_shelf_2 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(g30, name="port-2/3.3/1"), _ols_line(n3), name="b")

    graph = build_graph_from_pipes([in_shelf_1, out_shelf_2])

    assert graph.vertices_of(_nid(g30)) == [f"{_nid(g30)}#1", f"{_nid(g30)}#2"]
    assert graph_vertex(g30, "port-2/1/4") == f"{_nid(g30)}#2"
    assert graph_vertex(n1, "1-A-1-L1") == _nid(n1)
    with pytest.raises(NoOpticalPathFoundError):
        k_shortest_paths(graph, _nid(n1), _nid(n3), 5)

    out_shelf_1 = _pipe(OpticalFiberSpanBlockInactive, _ols_line(g30, name="port-1/4.3/1"), _ols_line(n3), name="c")
    graph = build_graph_from_pipes([in_shelf_1, out_shelf_2, out_shelf_1])
    assert k_shortest_paths(graph, _nid(n1), _nid(n3), 5) == [_ports(in_shelf_1, out_shelf_1)]


def test_k_shortest_paths_orders_by_hops_and_caps_k() -> None:
    """Yen returns loopless paths by hop count, parallel pipes as distinct paths, at most K."""
    (n1, _n2, _n3, n4), (direct, a12, b12, s24, s13, s34) = _diamond()
    graph = build_graph_from_pipes([direct, a12, b12, s24, s13, s34])

    paths = k_shortest_paths(graph, _nid(n1), _nid(n4), 10)

    assert paths[0] == _ports(direct)
    assert sorted(map(tuple, paths[1:])) == sorted(
        [tuple(_ports(a12, s24)), tuple(_ports(b12, s24)), tuple(_ports(s13, s34))]
    )
    assert len(paths) == 4
    assert k_shortest_paths(graph, _nid(n1), _nid(n4), 2)[0] == _ports(direct)
    assert len(k_shortest_paths(graph, _nid(n1), _nid(n4), 2)) == 2
    with pytest.raises(NoOpticalPathFoundError):
        k_shortest_paths(graph, _nid(n1), str(uuid4()), 3)


def test_restricted_endpoint_keeps_only_reachable_line_ports() -> None:
    """Only the line ports reachable from the add/drop port may carry the path out of the source."""
    (n1, _n2, _n3, n4), pipes = _diamond()
    direct, _a12, _b12, _s24, s13, s34 = pipes
    graph = build_graph_from_pipes(pipes).restricted_endpoint(_nid(n1), {"1-D-1-L1"})

    assert k_shortest_paths(graph, _nid(n1), _nid(n4), 10) == [_ports(s13, s34)]
    assert _ports(direct) not in k_shortest_paths(graph, _nid(n1), _nid(n4), 10)


def test_restricted_endpoint_keeps_add_drop_handoffs() -> None:
    """A pipe terminated on another add/drop port of the endpoint (local cross-connect) is kept."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    graph = build_graph_from_pipes([span, patch, leased]).restricted_endpoint(_nid(n2), set())

    # n2 cannot leave through its line port (span), but the patch on its add/drop port survives.
    assert _neighbors(graph, n2) == {_nid(n3)}
    assert k_shortest_paths(graph, _nid(n2), _nid(n4), 5) == [_ports(patch, leased)]


def test_k_shortest_paths_through_waypoints_concatenates_segments() -> None:
    """The ordered waypoints split the path into segments that are concatenated in order."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    graph = build_graph_from_pipes([span, patch, leased])
    expected = _ports(span, patch, leased)

    assert k_shortest_paths_through_waypoints(graph, _nid(n1), _nid(n4), [_nid(n2), _nid(n3)], 5) == [expected]
    # Consecutive duplicate waypoints are collapsed.
    assert k_shortest_paths_through_waypoints(graph, _nid(n1), _nid(n4), [_nid(n2), _nid(n2), _nid(n3)], 5) == [
        expected
    ]
    assert k_shortest_paths_through_waypoints(graph, _nid(n1), _nid(n4), None, 5) == [expected]
    with pytest.raises(NoOpticalPathFoundError):
        k_shortest_paths_through_waypoints(graph, _nid(n1), _nid(n4), [str(uuid4())], 5)


def test_waypoint_forces_the_longer_path() -> None:
    """A waypoint off the shortest path selects the paths through it only."""
    (n1, _n2, n3, n4), pipes = _diamond()
    _direct, _a12, _b12, _s24, s13, s34 = pipes
    graph = build_graph_from_pipes(pipes)

    assert k_shortest_paths_through_waypoints(graph, _nid(n1), _nid(n4), [_nid(n3)], 5) == [_ports(s13, s34)]


def test_available_passbands_for_path_unions_ports_and_internal_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ports and endpoint internal routes reduce the free ranges; own occupancy is forgiven."""
    node = _node()
    own = (192_000_000, 192_100_000)
    foreign = (193_000_000, 193_100_000)
    port_a = _ols_line(node, passbands=[own])
    port_b = _ols_line(node, passbands=[foreign])
    ports = {_pid(port_a): port_a, _pid(port_b): port_b}
    monkeypatch.setattr(shared, "_load_ols_port", lambda port_id: ports[port_id])
    src_edge = IntraNodeEdge("T1", "port-line", ((194_000_000, 194_050_000), own))

    available = available_passbands_for_path([_pid(port_a), _pid(port_b)], src_edge, None)
    assert available == [
        (OLS_BAND[0], own[0]),
        (own[1], foreign[0]),
        (foreign[1], 194_000_000),
        (194_050_000, OLS_BAND[1]),
    ]

    forgiven = available_passbands_for_path(
        [_pid(port_a), _pid(port_b)],
        src_edge,
        None,
        OwnOccupancy(passbands=(own,), port_ids=frozenset({_pid(port_a), _pid(port_b)})),
    )
    assert forgiven == [(OLS_BAND[0], foreign[0]), (foreign[1], 194_000_000), (194_050_000, OLS_BAND[1])]

    ensure_passband_available((191_400_000, 191_500_000), available)
    with pytest.raises(ValueError, match="not available"):
        ensure_passband_available((192_050_000, 192_150_000), available)
    ensure_passband_available((192_050_000, 192_150_000), None)


def test_compute_optical_path_candidates_restricts_both_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    """The internal connectivity read from the devices restricts the source and destination degrees."""
    (n1, _n2, _n3, n4), pipes = _diamond()
    _direct, a12, b12, s24, _s13, _s34 = pipes
    monkeypatch.setattr(shared, "build_constrained_graph", lambda *_, **__: build_graph_from_pipes(pipes))
    reachable = {_nid(n1): ["1-B-1-L1", "1-C-1-L1"], _nid(n4): ["port-line"]}
    monkeypatch.setattr(
        shared,
        "retrieve_add_drop_connectivity",
        lambda node, port: [IntraNodeEdge(port, line) for line in reachable[str(node.subscription_instance_id)]],
    )

    candidates = compute_optical_path_candidates(PathEndpoint(n1, "1-E1-1-T1"), PathEndpoint(n4, "1-E1-1-T1"), k=5)

    assert sorted(map(tuple, candidates.paths)) == sorted([tuple(_ports(a12, s24)), tuple(_ports(b12, s24))])
    assert set(candidates.src_edges) == {"1-B-1-L1", "1-C-1-L1"}


def test_split_loaded_path_into_platform_sections_splits_at_add_drop_ports() -> None:
    """A path is split into sections bounded by consecutive add/drop ports."""
    ports = [
        _ols_add_drop(_node(platform=Platform.FLEXILS)),
        _ols_line(_node(platform=Platform.FLEXILS)),
        _ols_line(_node(platform=Platform.FLEXILS)),
        _ols_add_drop(_node(platform=Platform.FLEXILS)),
        _ols_add_drop(_node(platform=Platform.GROOVE_G30)),
        _ols_line(_node(platform=Platform.GROOVE_G30)),
        _ols_line(_node(platform=Platform.GROOVE_G30)),
        _ols_add_drop(_node(platform=Platform.GROOVE_G30)),
    ]

    sections = split_loaded_path_into_platform_sections(ports)

    assert sections == [
        [str(port.subscription_instance_id) for port in ports[:4]],
        [str(port.subscription_instance_id) for port in ports[4:]],
    ]


def test_split_loaded_path_rejects_non_line_middle_port() -> None:
    """A section whose middle port is not an OLS line port is rejected."""
    ports = [
        _ols_add_drop(_node()),
        _ols_line(_node()),
        _transponder_line(_node()),
        _ols_add_drop(_node()),
    ]

    with pytest.raises(ValueError, match="middle port"):
        split_loaded_path_into_platform_sections(ports)


def test_split_loaded_path_rejects_mixed_platforms() -> None:
    """A section mixing vendors or platforms is rejected."""
    ports = [
        _ols_add_drop(_node(platform=Platform.FLEXILS)),
        _ols_line(_node(platform=Platform.FLEXILS)),
        _ols_line(_node(platform=Platform.GROOVE_G30)),
        _ols_add_drop(_node(platform=Platform.FLEXILS)),
    ]

    with pytest.raises(ValueError, match="same vendor and platform"):
        split_loaded_path_into_platform_sections(ports)


def test_split_loaded_path_rejects_missing_boundary_add_drop_ports() -> None:
    """A path that does not start and end with an add/drop port is rejected."""
    ports = [
        _ols_line(_node()),
        _ols_add_drop(_node()),
        _ols_line(_node()),
        _ols_add_drop(_node()),
    ]

    with pytest.raises(ValueError, match="start and end"):
        split_loaded_path_into_platform_sections(ports)


def test_split_loaded_path_rejects_odd_add_drop_count() -> None:
    """A path with an odd number of add/drop ports is rejected."""
    ports = [
        _ols_add_drop(_node()),
        _ols_add_drop(_node()),
        _ols_line(_node()),
        _ols_add_drop(_node()),
    ]

    with pytest.raises(ValueError, match="even number"):
        split_loaded_path_into_platform_sections(ports)


def test_validate_optical_spectrum_path_accepts_single_platform_and_rejects_mixed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The form validator accepts a single-platform path and rejects a mixed one."""
    flexils = _node(platform=Platform.FLEXILS)
    src_endpoint = _ols_add_drop(flexils)
    dst_endpoint = _ols_add_drop(flexils)
    interior = [_ols_line(flexils), _ols_line(flexils)]
    monkeypatch.setattr(shared, "_load_ols_port", lambda port_id: {"p1": interior[0], "p2": interior[1]}[port_id])

    # A FlexILS-only path is valid.
    shared.validate_optical_spectrum_path(["p1", "p2"], src_endpoint, dst_endpoint)

    # A path crossing a Groove G30 line port mixes platforms and is rejected.
    monkeypatch.setattr(shared, "_load_ols_port", lambda _port_id: _ols_line(_node(platform=Platform.GROOVE_G30)))
    with pytest.raises(ValueError, match="same vendor and platform"):
        shared.validate_optical_spectrum_path(["p1"], src_endpoint, dst_endpoint)
