"""Execution-level tests for the shipped Optical Spectrum Service workflows.

These tests are database-backed: they run the shipped workflows end to end through the
real orchestrator-core process engine (``start_process`` with the threadpool executor),
so the paths that break first as models drift are actually executed: the optical path
finding over the seeded fiber span topology (two FlexILS ROADM nodes joined by one
fiber span), the decomposition of the path into vendor-specific spectrum sections, the
device-facing circuit deployment/modify/delete/validate (HAL stubbed), the block
persistence, the description refresh, the process-subscription relation and the
modify/terminate/validate transitions.
"""

from uuid import UUID

import pytest
from sqlalchemy import select

import orchestrator.core.db as core_db
from orchestrator.core.db import (
    ProcessSubscriptionTable,
    ProcessTable,
    ProductBlockTable,
    ProductTable,
    SubscriptionInstanceTable,
    SubscriptionTable,
)
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import ProcessStatus
from orchestrator.optical.products.product_blocks.optical_node_management import Platform
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalPortBlockInactive,
    OpticalPortRole,
)
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpanSubscription
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumSubscription,
)
from orchestrator.optical.products.product_types.optical_spectrum_service import OpticalSpectrumServiceSubscription
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum_service import (
    construct_optical_spectrum_subscription,
)
from test.support.core_api import unwrap_step
from test.support.db import CUSTOMER_ID
from test.support.devices import FAKE_CLIENT_PORTS, FAKE_LINE_PORTS, install_device_stubs

pytestmark = pytest.mark.db

SPECTRUM_PRODUCT_NAME = "Optical Spectrum"
FIBER_SPAN_PRODUCT_NAME = "Optical Fiber Span"
LEASED_SPECTRUM_PRODUCT_NAME = "Optical Leased Spectrum"
FLEXILS_NODE_PRODUCT_NAME = "Nokia FlexILS Optical Node"
G30_NODE_PRODUCT_NAME = "Nokia Groove G30 Optical Node"

NODE_A = ("spec-a.test.local", "10.9.1.11")
NODE_B = ("spec-b.test.local", "10.9.1.12")
LINE_PORT = FAKE_LINE_PORTS[0]
CLIENT_PORT = FAKE_CLIENT_PORTS[0]

SPECTRUM_NAME = "spec-svc-01"
PASSBAND = (196_000_000, 196_100_000)
MODIFIED_SPECTRUM_NAME = "spec-svc-01-renamed"
MODIFIED_PASSBAND = (196_050_000, 196_125_000)

#: Multiple client (OLS add/drop) ports offered by the multi-vendor topology, so the
#: endpoint add/drop ports of the spectrum do not collide with the leased-spectrum ones.
MULTI_VENDOR_CLIENT_PORTS = ("port-1/2/1", "port-1/2/2", "port-1/2/3")
MULTI_VENDOR_LINE_PORTS = ("port-1/3.1/1.1", "port-1/3.2/1.1")


def _product_id(product_name: str) -> str:
    with core_db.db.database_scope():
        product = core_db.db.session.scalar(select(ProductTable).where(ProductTable.name == product_name))
        assert product is not None
        return str(product.product_id)


def _assert_process_completed(process_id: str) -> None:
    with core_db.db.database_scope():
        process = core_db.db.session.get(ProcessTable, UUID(process_id))
        assert process is not None
        assert ProcessStatus(process.last_status) == ProcessStatus.COMPLETED, f"process failed: {process.failed_reason}"


def _subscription_id_of_process(process_id: str) -> str:
    with core_db.db.database_scope():
        relation = core_db.db.session.scalar(
            select(ProcessSubscriptionTable).where(ProcessSubscriptionTable.process_id == UUID(process_id))
        )
        assert relation is not None
        return str(relation.subscription_id)


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _orphan_section_instance_count(subscription_id: str) -> int:
    """Count OpticalSpectrumSectionBlock instances not reachable from the spectrum block tree.

    A successful modify must leave no orphaned section instance behind: the replaced
    sections are pruned by the subscription save at the end of the workflow (see
    ``divide_path_into_sections``). This guards the documented orphan window.
    """
    with core_db.db.database_scope():
        instances = set(
            core_db.db.session.scalars(
                select(SubscriptionInstanceTable.subscription_instance_id)
                .join(
                    ProductBlockTable,
                    SubscriptionInstanceTable.product_block_id == ProductBlockTable.product_block_id,
                )
                .where(
                    SubscriptionInstanceTable.subscription_id == UUID(subscription_id),
                    ProductBlockTable.name == "OpticalSpectrumSectionBlock",
                )
            ).all()
        )
        spectrum = OpticalSpectrumServiceSubscription.from_subscription(subscription_id).optical_spectrum_service
        reachable = {section.subscription_instance_id for section in spectrum.optical_spectrum_sections}
    return len(instances - reachable)


def _seed_topology(run_process, seed_optical_node) -> tuple[str, str, str]:
    """Seed two FlexILS ROADM nodes joined by one fiber span.

    Returns the (node A, node B, fiber span) subscription ids. The span is created with
    the shipped ``create_fiber_span`` workflow, so the terminating line port blocks are
    persisted exactly the way the path engine expects to find them.
    """
    node_a_id = seed_optical_node(FLEXILS_NODE_PRODUCT_NAME, NODE_A[0], NODE_A[1])
    node_b_id = seed_optical_node(FLEXILS_NODE_PRODUCT_NAME, NODE_B[0], NODE_B[1])
    process_id = run_process(
        "create_fiber_span",
        [
            {"product": _product_id(FIBER_SPAN_PRODUCT_NAME)},
            {"customer_id": CUSTOMER_ID},
            {"node_a_id": node_a_id, "node_b_id": node_b_id},
            {
                "optical_pipe_name": f"{NODE_A[0]} {LINE_PORT} --- {NODE_B[0]} {LINE_PORT}",
                "port_a_name": LINE_PORT,
                "port_b_name": LINE_PORT,
            },
            {},
        ],
    )
    _assert_process_completed(process_id)
    return node_a_id, node_b_id, _subscription_id_of_process(process_id)


def _optical_path_value(span_subscription_id: str, src_node_subscription_id: str) -> str:
    """Build the optical path form value: the span's line port instance ids, ordered from the source node.

    The path selector offers the ``";"``-joined subscription instance ids of the OLS line
    port blocks of the fiber spans, in the order the shortest path traverses them.
    """
    pipe = OpticalFiberSpanSubscription.from_subscription(span_subscription_id).optical_pipe
    terminations = pipe.optical_pipe_terminations
    src_port = next(
        t for t in terminations if str(t.optical_port_host_node.owner_subscription_id) == src_node_subscription_id
    )
    dst_port = next(
        t for t in terminations if str(t.subscription_instance_id) != str(src_port.subscription_instance_id)
    )
    return f"{src_port.subscription_instance_id};{dst_port.subscription_instance_id}"


def _create_user_inputs(
    node_a_id: str,
    node_b_id: str,
    optical_path: str,
    *,
    name: str = SPECTRUM_NAME,
    passband: tuple[int, int] = PASSBAND,
    src_port: str = CLIENT_PORT,
    dst_port: str = CLIENT_PORT,
) -> list[dict]:
    """Return the create form inputs, one dict per page of the shipped page sequence.

    The core injects the product page first; the shipped generator then yields the
    customer page, the identity page, the two-nodes page, the add/drop page, the
    waypoints page, the constraints page, the path page and the summary page.
    """
    return [
        {"product": _product_id(SPECTRUM_PRODUCT_NAME)},
        {"customer_id": CUSTOMER_ID},
        {"optical_spectrum_name": name, "frequency_min": passband[0], "frequency_max": passband[1]},
        {"src_optical_device_id": node_a_id, "dst_optical_device_id": node_b_id},
        {"src_optical_port_name": src_port, "dst_optical_port_name": dst_port},
        {"intermediate_node_ids": []},
        {"exclude_devices_list": [], "exclude_fibers_list": []},
        {"optical_path": optical_path},
        {},
    ]


def _run_create(
    run_process,
    node_a_id: str,
    node_b_id: str,
    optical_path: str,
    *,
    name: str = SPECTRUM_NAME,
    passband: tuple[int, int] = PASSBAND,
    src_port: str = CLIENT_PORT,
    dst_port: str = CLIENT_PORT,
) -> tuple[str, str]:
    """Run the shipped create workflow and return the (process id, subscription id) pair."""
    process_id = run_process(
        "create_optical_spectrum",
        _create_user_inputs(
            node_a_id,
            node_b_id,
            optical_path,
            name=name,
            passband=passband,
            src_port=src_port,
            dst_port=dst_port,
        ),
    )
    _assert_process_completed(process_id)
    return process_id, _subscription_id_of_process(process_id)


def test_create_optical_spectrum_service_end_to_end(
    run_process, seed_optical_node, stub_pipe_device, stub_spectrum_device
) -> None:
    """The shipped create workflow executes end to end over a two-node fiber span topology."""
    node_a_id, node_b_id, span_id = _seed_topology(run_process, seed_optical_node)
    process_id, subscription_id = _run_create(
        run_process, node_a_id, node_b_id, _optical_path_value(span_id, node_a_id)
    )

    table = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(table.status) == SubscriptionLifecycle.ACTIVE
    assert table.customer_id == CUSTOMER_ID
    assert table.description == f"{SPECTRUM_NAME} ({SPECTRUM_PRODUCT_NAME})"
    assert _subscription_id_of_process(process_id) == subscription_id

    spectrum = OpticalSpectrumServiceSubscription.from_subscription(subscription_id).optical_spectrum_service
    assert spectrum.optical_spectrum_name == SPECTRUM_NAME
    assert tuple(spectrum.optical_spectrum_passband) == PASSBAND

    # The path (src add/drop, line port A, line port B, dst add/drop) is on FlexILS nodes
    # only, so it decomposes into a single section.
    assert len(spectrum.optical_spectrum_sections) == 1
    section = spectrum.optical_spectrum_sections[0]
    add_drop_ports = section.optical_spectrum_section_add_drop_ports
    express_ports = section.optical_spectrum_section_express_ports
    assert [port.optical_port_name for port in add_drop_ports] == [CLIENT_PORT, CLIENT_PORT]
    assert [port.optical_port_name for port in express_ports] == [LINE_PORT, LINE_PORT]
    assert str(add_drop_ports[0].optical_port_host_node.owner_subscription_id) == node_a_id
    assert str(add_drop_ports[-1].optical_port_host_node.owner_subscription_id) == node_b_id
    # The stubbed devices report no spectral occupations, so the refreshed passbands are empty.
    assert [port.optical_passbands for port in express_ports] == [[], []]


def test_create_persists_used_passbands_on_owning_pipe(
    run_process, seed_optical_node, stub_pipe_device, stub_spectrum_device, monkeypatch
) -> None:
    """The refreshed express-port passbands are persisted under the owning pipe subscription.

    The express ports of a spectrum section are owned by the fiber span (they are its
    OLS line terminations), so ``save_optical_module_block`` skips them as foreign. The
    passband step must persist them under the span subscription, otherwise the path
    engine keeps seeing stale occupations.
    """
    node_a_id, node_b_id, span_id = _seed_topology(run_process, seed_optical_node)
    occupied = [PASSBAND]
    monkeypatch.setattr(
        "orchestrator.optical.workflows.optical_spectrum_service.shared.retrieve_ports_spectral_occupations",
        lambda _block: {LINE_PORT: occupied},
    )

    _run_create(run_process, node_a_id, node_b_id, _optical_path_value(span_id, node_a_id))

    # Reload the fiber span from the database: its termination carries the passbands
    # refreshed by the spectrum workflow.
    pipe = OpticalFiberSpanSubscription.from_subscription(span_id).optical_pipe
    assert any(list(port.optical_passbands) == occupied for port in pipe.optical_pipe_terminations)


def test_construct_rejects_add_drop_port_already_in_use(
    run_process, seed_optical_node, stub_pipe_device, stub_spectrum_device
) -> None:
    """The construct step refuses an add/drop port already owned by another subscription.

    The form selector already excludes the ports in use; this calls the construct step
    directly (bypassing the form) to exercise the execution-time guard.
    """
    node_a_id, node_b_id, span_id = _seed_topology(run_process, seed_optical_node)
    optical_path = _optical_path_value(span_id, node_a_id)
    _run_create(run_process, node_a_id, node_b_id, optical_path, name="spec-1")

    product_id = _product_id(SPECTRUM_PRODUCT_NAME)
    with core_db.db.database_scope(), pytest.raises(ValueError, match="already in use"):
        unwrap_step(construct_optical_spectrum_subscription)(
            product=product_id,
            customer_id=CUSTOMER_ID,
            optical_spectrum_name="spec-2",
            frequency_min=PASSBAND[0],
            frequency_max=PASSBAND[1],
            src_optical_device_id=node_a_id,
            dst_optical_device_id=node_b_id,
            src_optical_port_name=CLIENT_PORT,
            dst_optical_port_name=CLIENT_PORT,
            optical_path=[],
        )


def test_full_lifecycle_create_modify_validate_terminate(
    run_process,
    seed_optical_node,
    stub_pipe_device,
    stub_spectrum_device,
) -> None:
    """The full create -> modify -> validate -> terminate cycle of the shipped workflows."""
    node_a_id, node_b_id, span_id = _seed_topology(run_process, seed_optical_node)
    _, subscription_id = _run_create(run_process, node_a_id, node_b_id, _optical_path_value(span_id, node_a_id))

    optical_path = _optical_path_value(span_id, node_a_id)
    modify_process_id = run_process(
        "modify_optical_spectrum",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {
                "optical_spectrum_name": MODIFIED_SPECTRUM_NAME,
                "frequency_min": MODIFIED_PASSBAND[0],
                "frequency_max": MODIFIED_PASSBAND[1],
            },
            {"intermediate_node_ids": []},
            {"exclude_devices_list": [], "exclude_fibers_list": []},
            {"optical_path": optical_path},
            {},
        ],
    )
    _assert_process_completed(modify_process_id)
    assert _subscription_table(subscription_id).description == f"{MODIFIED_SPECTRUM_NAME} ({SPECTRUM_PRODUCT_NAME})"
    spectrum = OpticalSpectrumServiceSubscription.from_subscription(subscription_id).optical_spectrum_service
    assert spectrum.optical_spectrum_name == MODIFIED_SPECTRUM_NAME
    assert tuple(spectrum.optical_spectrum_passband) == MODIFIED_PASSBAND
    assert len(spectrum.optical_spectrum_sections) == 1
    assert _subscription_table(subscription_id).insync is True
    # The replaced sections are pruned by the final subscription save: no orphan
    # OpticalSpectrumSectionBlock instance must be left behind by a successful modify.
    assert _orphan_section_instance_count(subscription_id) == 0

    validate_process_id = run_process("validate_optical_spectrum", [{"subscription_id": subscription_id}])
    _assert_process_completed(validate_process_id)

    reconcile_process_id = run_process("reconcile_optical_spectrum", [{"subscription_id": subscription_id}])
    _assert_process_completed(reconcile_process_id)

    terminate_process_id = run_process(
        "terminate_optical_spectrum",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    _assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert _subscription_id_of_process(terminate_process_id) == subscription_id


def _leased_spectrum_termination_on(
    pipe_subscription_id: str, node_subscription_id: str
) -> AbstractOpticalPortBlockInactive:
    """Return the leased-spectrum termination hosted on the given node."""
    pipe = OpticalLeasedSpectrumSubscription.from_subscription(pipe_subscription_id).optical_pipe
    return next(
        termination
        for termination in pipe.optical_pipe_terminations
        if str(termination.optical_port_host_node.owner_subscription_id) == node_subscription_id
    )


def _seed_leased_spectrum(
    run_process, node_a_id: str, node_b_id: str, port_a_name: str, port_b_name: str, name: str
) -> str:
    """Create an ACTIVE Optical Leased Spectrum pipe between two nodes via the shipped workflow."""
    process_id = run_process(
        "create_leased_spectrum",
        [
            {"product": _product_id(LEASED_SPECTRUM_PRODUCT_NAME)},
            {"customer_id": CUSTOMER_ID},
            {"node_a_id": node_a_id, "node_b_id": node_b_id},
            {"optical_pipe_name": name, "port_a_name": port_a_name, "port_b_name": port_b_name},
            {"provider_name": "Test Provider"},
            {},
        ],
    )
    _assert_process_completed(process_id)
    return _subscription_id_of_process(process_id)


def test_create_optical_spectrum_multi_vendor_sections(run_process, seed_optical_node, monkeypatch) -> None:
    """A path crossing two platforms splits into one section per add/drop port pair.

    Topology: FlexILS node A <-> Groove G30 node M <-> FlexILS node Z, joined by two
    leased spectra terminating on OLS add/drop ports. A fiber span cannot be used for
    the cross-vendor links (it requires the two ends on the same vendor/platform), so
    the leased spectra are the cross-platform edges of the graph. The spectrum path is
    ``[A add/drop, A-M add/drop, M-A add/drop, M-Z add/drop, Z-M add/drop, Z add/drop]``,
    which the construct step splits at the add/drop ports into three single-platform
    sections (FlexILS, Groove G30, FlexILS).
    """
    install_device_stubs(
        monkeypatch,
        families=("pipe", "spectrum"),
        client_ports=MULTI_VENDOR_CLIENT_PORTS,
        line_ports=MULTI_VENDOR_LINE_PORTS,
    )
    node_a = seed_optical_node(FLEXILS_NODE_PRODUCT_NAME, "mv-a.test.local", "10.9.2.11")
    node_m = seed_optical_node(G30_NODE_PRODUCT_NAME, "mv-m.test.local", "10.9.2.12")
    node_z = seed_optical_node(FLEXILS_NODE_PRODUCT_NAME, "mv-z.test.local", "10.9.2.13")

    # The "used ports" bookkeeping is per node: A and Z each use their first add/drop
    # port for the cross-vendor leased spectrum, M uses its first and second ones.
    pipe_am = _seed_leased_spectrum(
        run_process, node_a, node_m, MULTI_VENDOR_CLIENT_PORTS[0], MULTI_VENDOR_CLIENT_PORTS[0], "mv-a-m"
    )
    pipe_mz = _seed_leased_spectrum(
        run_process, node_m, node_z, MULTI_VENDOR_CLIENT_PORTS[1], MULTI_VENDOR_CLIENT_PORTS[0], "mv-m-z"
    )

    # The spectrum endpoint add/drop ports must not collide with the leased-spectrum ones.
    src_port = MULTI_VENDOR_CLIENT_PORTS[1]
    dst_port = MULTI_VENDOR_CLIENT_PORTS[1]

    a_term = _leased_spectrum_termination_on(pipe_am, node_a)
    m_term_am = _leased_spectrum_termination_on(pipe_am, node_m)
    m_term_mz = _leased_spectrum_termination_on(pipe_mz, node_m)
    z_term = _leased_spectrum_termination_on(pipe_mz, node_z)
    optical_path = ";".join(str(port.subscription_instance_id) for port in (a_term, m_term_am, m_term_mz, z_term))

    _, subscription_id = _run_create(
        run_process,
        node_a,
        node_z,
        optical_path,
        name="mv-spec-01",
        src_port=src_port,
        dst_port=dst_port,
    )

    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE
    spectrum = OpticalSpectrumServiceSubscription.from_subscription(subscription_id).optical_spectrum_service
    sections = spectrum.optical_spectrum_sections
    assert len(sections) >= 2

    section_platforms = [
        section.optical_spectrum_section_add_drop_ports[
            0
        ].optical_port_host_node.management.optical_module_node_platform
        for section in sections
    ]
    assert section_platforms == [Platform.FLEXILS, Platform.GROOVE_G30, Platform.FLEXILS]

    for section in sections:
        add_drop_ports = section.optical_spectrum_section_add_drop_ports
        express_ports = section.optical_spectrum_section_express_ports
        assert len(add_drop_ports) == 2
        assert all(port.optical_port_role is OpticalPortRole.OLS_LINE for port in express_ports)
