"""Unit tests for the optical spectrum path engine (database-free).

The path engine is exercised with product blocks built through
``model_construct``: no subscription is persisted and no device or database is
touched. Only the pure helpers are covered here (``build_graph_from_pipes``,
``all_shortest_paths_through_waypoints`` and
``split_loaded_path_into_platform_sections``); the database wrappers are thin
delegations.
"""

from uuid import uuid4

import pytest

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
from orchestrator.optical.workflows.optical_spectrum_service import shared
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    NoOpticalPathFoundError,
    all_shortest_paths_through_waypoints,
    build_graph_from_pipes,
    compute_all_shortest_paths,
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
            optical_module_node_fqdn=fqdn,
        ),
    )


def _ols_line(
    node: NokiaFlexIlsBlockInactive, *, passbands: list[tuple[int, int]] | None = None
) -> OlsLinePortBlockInactive:
    """Build a fake OLS line port hosted by the given node."""
    return OlsLinePortBlockInactive.model_construct(
        subscription_instance_id=uuid4(),
        owner_subscription_id=node.owner_subscription_id,
        optical_port_role=OpticalPortRole.OLS_LINE,
        optical_port_name="port-line",
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
    return {neighbor for neighbor, _ in graph.get(_nid(node), [])}


def _linear_topology() -> tuple:
    """Build a 4-node chain joined by an OLS span, patch and leased spectrum."""
    n1, n2, n3, n4 = _node(fqdn="n1"), _node(fqdn="n2"), _node(fqdn="n3"), _node(fqdn="n4")
    span = _pipe(OpticalFiberSpanBlockInactive, _ols_line(n1), _ols_line(n2), name="span")
    patch = _pipe(OpticalFiberPatchBlockInactive, _ols_add_drop(n2), _ols_add_drop(n3), name="patch")
    leased = _pipe(OpticalLeasedSpectrumBlockInactive, _ols_line(n3), _ols_line(n4), name="leased")
    return n1, n2, n3, n4, span, patch, leased


def test_build_graph_from_pipes_includes_ols_pipes_and_skips_non_ols() -> None:
    """Span, patch and leased OLS pipes are included; transponder-terminated pipes are not."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    transponder_pipe = _pipe(
        OpticalFiberSpanBlockInactive, _ols_line(n1), _transponder_line(n4), name="transponder-pipe"
    )

    graph = build_graph_from_pipes([span, patch, leased, transponder_pipe], PASSBAND)

    assert set(graph) == {_nid(node) for node in (n1, n2, n3, n4)}
    assert _neighbors(graph, n1) == {_nid(n2)}
    assert _neighbors(graph, n2) == {_nid(n1), _nid(n3)}
    assert _neighbors(graph, n3) == {_nid(n2), _nid(n4)}
    assert _neighbors(graph, n4) == {_nid(n3)}
    assert sum(len(edges) for edges in graph.values()) == 6


def test_build_graph_from_pipes_applies_exclusions() -> None:
    """Span exclusion, node exclusion and passband overlap exclusion all drop the pipe."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    pipes = [span, patch, leased]

    graph = build_graph_from_pipes(pipes, PASSBAND)
    assert _neighbors(graph, n1) == {_nid(n2)}

    excluded_by_span = build_graph_from_pipes(
        pipes, PASSBAND, exclude_span_instance_ids=[str(span.subscription_instance_id)]
    )
    assert _nid(n1) not in excluded_by_span

    excluded_by_node = build_graph_from_pipes(pipes, PASSBAND, exclude_node_instance_ids=[_nid(n2)])
    assert _nid(n1) not in excluded_by_node
    assert _nid(n2) not in excluded_by_node

    overlapping_span = _pipe(
        OpticalFiberSpanBlockInactive,
        _ols_line(n1, passbands=[PASSBAND]),
        _ols_line(n2),
        name="overlapping-span",
    )
    excluded_by_passband = build_graph_from_pipes([overlapping_span, patch, leased], PASSBAND)
    assert _nid(n1) not in excluded_by_passband


def test_all_shortest_paths_through_waypoints_concatenates_segments(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ordered waypoints split the path into segments that are concatenated in order."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    graph = build_graph_from_pipes([span, patch, leased], PASSBAND)
    monkeypatch.setattr(shared, "build_constrained_graph", lambda *_, **__: graph)

    paths = all_shortest_paths_through_waypoints(_nid(n1), _nid(n4), [_nid(n2), _nid(n3)], PASSBAND)

    expected = [
        _pid(span.optical_pipe_terminations[0]),
        _pid(span.optical_pipe_terminations[1]),
        _pid(patch.optical_pipe_terminations[0]),
        _pid(patch.optical_pipe_terminations[1]),
        _pid(leased.optical_pipe_terminations[0]),
        _pid(leased.optical_pipe_terminations[1]),
    ]
    assert paths == [expected]

    # Consecutive duplicate waypoints are collapsed.
    assert all_shortest_paths_through_waypoints(_nid(n1), _nid(n4), [_nid(n2), _nid(n2), _nid(n3)], PASSBAND) == [
        expected
    ]

    # With no waypoints the result is the plain all-shortest-paths computation.
    assert all_shortest_paths_through_waypoints(_nid(n1), _nid(n4), None, PASSBAND) == compute_all_shortest_paths(
        graph, _nid(n1), _nid(n4)
    )


def test_all_shortest_paths_through_waypoints_raises_on_unreachable_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unreachable waypoint re-raises the path error with the overall source and destination."""
    n1, n2, n3, n4, span, patch, leased = _linear_topology()
    graph = build_graph_from_pipes([span, patch, leased], PASSBAND)
    monkeypatch.setattr(shared, "build_constrained_graph", lambda *_, **__: graph)

    with pytest.raises(NoOpticalPathFoundError):
        all_shortest_paths_through_waypoints(_nid(n1), _nid(n4), [str(uuid4())], PASSBAND)


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
