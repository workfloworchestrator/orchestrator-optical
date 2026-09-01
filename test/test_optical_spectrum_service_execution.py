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

import orchestrator.core.db as core_db
from orchestrator.core.db import ProcessTable, ProcessSubscriptionTable, ProductTable, SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import ProcessStatus
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpan
from orchestrator.optical.products.product_types.optical_spectrum_service import OpticalSpectrum
from test.conftest import CUSTOMER_ID, FAKE_CLIENT_PORTS, FAKE_LINE_PORTS
from sqlalchemy import select

pytestmark = pytest.mark.db

SPECTRUM_PRODUCT_NAME = "Optical Spectrum"
FIBER_SPAN_PRODUCT_NAME = "Optical Fiber Span"
FLEXILS_NODE_PRODUCT_NAME = "Nokia FlexILS Optical Node"

NODE_A = ("spec-a.test.local", "10.9.1.11")
NODE_B = ("spec-b.test.local", "10.9.1.12")
LINE_PORT = FAKE_LINE_PORTS[0]
CLIENT_PORT = FAKE_CLIENT_PORTS[0]

SPECTRUM_NAME = "spec-svc-01"
PASSBAND = (196_000_000, 196_100_000)
MODIFIED_SPECTRUM_NAME = "spec-svc-01-renamed"
MODIFIED_PASSBAND = (196_050_000, 196_150_000)


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
            {"customer_id": CUSTOMER_ID, "node_a_id": node_a_id, "node_b_id": node_b_id},
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
    pipe = OpticalFiberSpan.from_subscription(span_subscription_id).optical_pipe
    terminations = pipe.optical_pipe_terminations
    src_port = next(
        t for t in terminations if str(t.optical_port_host_node.owner_subscription_id) == src_node_subscription_id
    )
    dst_port = next(
        t for t in terminations if str(t.subscription_instance_id) != str(src_port.subscription_instance_id)
    )
    return f"{src_port.subscription_instance_id};{dst_port.subscription_instance_id}"


def _create_user_inputs(node_a_id: str, node_b_id: str, optical_path: str) -> list[dict]:
    return [
        {"product": _product_id(SPECTRUM_PRODUCT_NAME)},
        {
            "customer_id": CUSTOMER_ID,
            "optical_spectrum_name": SPECTRUM_NAME,
            "src_optical_device_id": node_a_id,
            "dst_optical_device_id": node_b_id,
            "frequency_min": PASSBAND[0],
            "frequency_max": PASSBAND[1],
        },
        {"src_optical_port_name": CLIENT_PORT, "dst_optical_port_name": CLIENT_PORT},
        {"exclude_devices_list": [], "exclude_fibers_list": []},
        {"optical_path": optical_path},
        {},
    ]


def _run_create(run_process, node_a_id: str, node_b_id: str, span_subscription_id: str) -> tuple[str, str]:
    """Run the shipped create workflow and return the (process id, subscription id) pair."""
    process_id = run_process(
        "create_optical_spectrum",
        _create_user_inputs(node_a_id, node_b_id, _optical_path_value(span_subscription_id, node_a_id)),
    )
    _assert_process_completed(process_id)
    return process_id, _subscription_id_of_process(process_id)


def test_create_optical_spectrum_service_end_to_end(
    run_process, seed_optical_node, stub_pipe_device, stub_spectrum_device
) -> None:
    """The shipped create workflow executes end to end over a two-node fiber span topology."""
    node_a_id, node_b_id, span_id = _seed_topology(run_process, seed_optical_node)
    process_id, subscription_id = _run_create(run_process, node_a_id, node_b_id, span_id)

    table = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(table.status) == SubscriptionLifecycle.ACTIVE
    assert table.customer_id == CUSTOMER_ID
    assert table.description == f"{SPECTRUM_NAME} ({SPECTRUM_PRODUCT_NAME})"
    assert _subscription_id_of_process(process_id) == subscription_id

    spectrum = OpticalSpectrum.from_subscription(subscription_id).optical_spectrum_service
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


def test_full_lifecycle_create_modify_validate_terminate(
    run_process,
    seed_optical_node,
    stub_pipe_device,
    stub_spectrum_device,
) -> None:
    """The full create -> modify -> validate -> terminate cycle of the shipped workflows."""
    node_a_id, node_b_id, span_id = _seed_topology(run_process, seed_optical_node)
    _, subscription_id = _run_create(run_process, node_a_id, node_b_id, span_id)

    optical_path = _optical_path_value(span_id, node_a_id)
    modify_process_id = run_process(
        "modify_optical_spectrum",
        [
            {"subscription_id": subscription_id},
            {
                "customer_id": CUSTOMER_ID,
                "optical_spectrum_name": MODIFIED_SPECTRUM_NAME,
                "frequency_min": MODIFIED_PASSBAND[0],
                "frequency_max": MODIFIED_PASSBAND[1],
            },
            {"exclude_devices_list": [], "exclude_fibers_list": []},
            {"optical_path": optical_path},
            {},
        ],
    )
    _assert_process_completed(modify_process_id)
    assert _subscription_table(subscription_id).description == f"{MODIFIED_SPECTRUM_NAME} ({SPECTRUM_PRODUCT_NAME})"
    spectrum = OpticalSpectrum.from_subscription(subscription_id).optical_spectrum_service
    assert spectrum.optical_spectrum_name == MODIFIED_SPECTRUM_NAME
    assert tuple(spectrum.optical_spectrum_passband) == MODIFIED_PASSBAND
    assert len(spectrum.optical_spectrum_sections) == 1
    assert _subscription_table(subscription_id).insync is True

    validate_process_id = run_process("validate_optical_spectrum", [{"subscription_id": subscription_id}])
    _assert_process_completed(validate_process_id)

    terminate_process_id = run_process(
        "terminate_optical_spectrum",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    _assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert _subscription_id_of_process(terminate_process_id) == subscription_id
