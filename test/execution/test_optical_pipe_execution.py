"""Execution-level tests for the shipped optical pipe workflows.

These tests are database-backed: they run the shipped create/modify/validate/terminate
workflows of the three shipped optical pipe products (Optical Fiber Span, Optical
Fiber Patch and Optical Leased Spectrum) end to end through the real orchestrator-core
process engine, with the device-facing HAL calls stubbed (``stub_pipe_device``).

The topology is two ACTIVE Nokia FlexILS nodes seeded via ``seed_optical_node``:
fiber spans terminate on the faked line ports, while fiber patches and leased
spectrum pipes terminate on the faked client (SCG) ports. On a FlexILS node the
client ports map to OLS add/drop port blocks and the line ports to OLS line
port blocks.
"""

from typing import Any
from uuid import UUID

import pytest
from pydantic_forms.exceptions import FormValidationError

import orchestrator.core.db as core_db
from orchestrator.core.db import SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import pipe_blocks_by_types
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import OpticalPipeType
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlock
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlock
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatchSubscription
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpanSubscription
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrumSubscription
from orchestrator.optical.workflows.optical_pipe.shared import (
    multiple_optical_pipe_selector,
    optical_pipe_selector,
)
from test.support.db import CUSTOMER_ID, node_instance_id_of_subscription
from test.support.devices import FAKE_CLIENT_PORTS, FAKE_LINE_PORTS

pytestmark = pytest.mark.db

FLEXILS_NODE_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_FLEXILS.value
FIBER_SPAN_PRODUCT = ProductName.OPTICAL_FIBER_SPAN.value
FIBER_PATCH_PRODUCT = ProductName.OPTICAL_FIBER_PATCH.value
LEASED_SPECTRUM_PRODUCT = ProductName.OPTICAL_LEASED_SPECTRUM.value

#: Line port and client port offered by the faked FlexILS devices (conftest stubs).
LINE_PORT = FAKE_LINE_PORTS[0]
CLIENT_PORT = FAKE_CLIENT_PORTS[0]


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    """Return the subscription row of the given subscription id."""
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _seed_node_instance(seed_optical_node: Any, product_name: str, fqdn: str, interface_ip: str) -> str:
    """Seed an ACTIVE node and return its block instance id (the pipe forms select by instance id)."""
    return node_instance_id_of_subscription(seed_optical_node(product_name, fqdn, interface_ip))


def _create_pipe_user_inputs(
    product_id: str,
    node_a_instance_id: str,
    node_b_instance_id: str,
    port_a_name: str,
    port_b_name: str,
    pipe_name: str | None = None,
    provider_name: str | None = None,
) -> list[dict[str, Any]]:
    """Return the pipe create form inputs: product, ends, terminations, [provider], summary.

    The three shipped pipe create forms share the same page sequence
    (product, customer, nodes, terminations); ``provider_name`` adds the
    dedicated provider page of the leased spectrum form, which sits between the
    terminations page and the summary page. The node ends are block instance ids.
    """
    terminations: dict[str, Any] = {"port_a_name": port_a_name, "port_b_name": port_b_name}
    if pipe_name is not None:
        terminations["optical_pipe_name"] = pipe_name
    pages: list[dict[str, Any]] = [
        {"product": product_id},
        {"customer_id": CUSTOMER_ID},
        {"node_a_instance_id": node_a_instance_id, "node_b_instance_id": node_b_instance_id},
        terminations,
    ]
    if provider_name is not None:
        pages.append({"provider_name": provider_name})
    pages.append({})
    return pages


def _terminate_pipe_user_inputs(subscription_id: str) -> list[dict[str, Any]]:
    """Return the pipe terminate form inputs: subscription selector, TERMINATE confirmation."""
    return [{"subscription_id": subscription_id}, {"warning": "TERMINATE", "subscription_id": subscription_id}]


def _assert_pipe_terminations(pipe: Any, name_a: str, name_b: str, port_name: str, port_block_class: Any) -> None:
    """Assert the two terminations of a pipe block: port names, block types and host nodes."""
    port_a, port_b = pipe.optical_pipe_terminations
    assert isinstance(port_a, port_block_class)
    assert isinstance(port_b, port_block_class)
    assert port_a.optical_port_name == port_name
    assert port_b.optical_port_name == port_name
    assert port_a.optical_port_host_node.management.optical_module_node_fqdn == name_a
    assert port_b.optical_port_host_node.management.optical_module_node_fqdn == name_b
    assert port_a.optical_port_description == f"Physically connected to {name_b} {port_name}."
    assert port_b.optical_port_description == f"Physically connected to {name_a} {port_name}."


def test_fiber_span_full_lifecycle(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """The full create -> modify -> validate -> terminate cycle of the shipped Optical Fiber Span workflows."""
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "span-a.optical.test", "10.9.0.11")
    node_b = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "span-b.optical.test", "10.9.0.12")

    create_process_id = run_process(
        "create_fiber_span",
        _create_pipe_user_inputs(product_id_for(FIBER_SPAN_PRODUCT), node_a, node_b, LINE_PORT, LINE_PORT, "span-01"),
    )
    assert_process_completed(create_process_id)
    subscription_id = subscription_id_of_process(create_process_id)

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.customer_id == CUSTOMER_ID
    assert subscription.description == f"span-01 ({FIBER_SPAN_PRODUCT})"
    assert subscription.insync is True

    # The span terminates on OLS line ports, one per end, each hosted on its node.
    span = OpticalFiberSpanSubscription.from_subscription(subscription_id)
    assert span.optical_pipe.optical_pipe_name == "span-01"
    _assert_pipe_terminations(
        span.optical_pipe, "span-a.optical.test", "span-b.optical.test", LINE_PORT, OlsLinePortBlock
    )

    modify_process_id = run_process(
        "modify_fiber_span",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {"optical_pipe_name": "span-02"},
            {},
        ],
    )
    assert_process_completed(modify_process_id)
    assert _subscription_table(subscription_id).description == f"span-02 ({FIBER_SPAN_PRODUCT})"
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE
    assert OpticalFiberSpanSubscription.from_subscription(subscription_id).optical_pipe.optical_pipe_name == "span-02"

    validate_process_id = run_process("validate_fiber_span", [{"subscription_id": subscription_id}])
    assert_process_completed(validate_process_id)

    reconcile_process_id = run_process("reconcile_fiber_span", [{"subscription_id": subscription_id}])
    assert_process_completed(reconcile_process_id)
    assert _subscription_table(subscription_id).insync is True

    terminate_process_id = run_process("terminate_fiber_span", _terminate_pipe_user_inputs(subscription_id))
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_fiber_span_create_default_pipe_name(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """Leaving the identifier empty derives the default 'node A port A --- node B port B' name."""
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "span-dflt-a.optical.test", "10.9.0.13")
    node_b = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "span-dflt-b.optical.test", "10.9.0.14")

    create_process_id = run_process(
        "create_fiber_span",
        _create_pipe_user_inputs(product_id_for(FIBER_SPAN_PRODUCT), node_a, node_b, LINE_PORT, LINE_PORT),
    )
    assert_process_completed(create_process_id)
    subscription_id = subscription_id_of_process(create_process_id)

    expected_name = f"span-dflt-a.optical.test {LINE_PORT} --- span-dflt-b.optical.test {LINE_PORT}"
    assert (
        OpticalFiberSpanSubscription.from_subscription(subscription_id).optical_pipe.optical_pipe_name == expected_name
    )
    assert _subscription_table(subscription_id).description == f"{expected_name} ({FIBER_SPAN_PRODUCT})"


def test_fiber_span_create_rejects_same_node(
    run_process,
    product_id_for,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """A fiber span whose two ends are on the same node fails the form validation."""
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "span-same-a.optical.test", "10.9.0.15")

    with pytest.raises(FormValidationError, match="different nodes"):
        run_process(
            "create_fiber_span",
            [
                {"product": product_id_for(FIBER_SPAN_PRODUCT)},
                {"customer_id": CUSTOMER_ID},
                {"node_a_instance_id": node_a, "node_b_instance_id": node_a},
            ],
        )


def test_fiber_patch_create_validate_terminate(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """The shipped Optical Fiber Patch create/validate/terminate workflows, on FlexILS client ports."""
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "patch-a.optical.test", "10.9.0.21")
    node_b = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "patch-b.optical.test", "10.9.0.22")

    create_process_id = run_process(
        "create_fiber_patch",
        _create_pipe_user_inputs(
            product_id_for(FIBER_PATCH_PRODUCT), node_a, node_b, CLIENT_PORT, CLIENT_PORT, "patch-01"
        ),
    )
    assert_process_completed(create_process_id)
    subscription_id = subscription_id_of_process(create_process_id)

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.customer_id == CUSTOMER_ID
    assert subscription.description == f"patch-01 ({FIBER_PATCH_PRODUCT})"

    # On a FlexILS node the client (SCG) ports map to OLS add/drop port blocks.
    patch = OpticalFiberPatchSubscription.from_subscription(subscription_id)
    assert patch.optical_pipe.optical_pipe_name == "patch-01"
    _assert_pipe_terminations(
        patch.optical_pipe, "patch-a.optical.test", "patch-b.optical.test", CLIENT_PORT, OlsAddDropPortBlock
    )

    validate_process_id = run_process("validate_fiber_patch", [{"subscription_id": subscription_id}])
    assert_process_completed(validate_process_id)

    reconcile_process_id = run_process("reconcile_fiber_patch", [{"subscription_id": subscription_id}])
    assert_process_completed(reconcile_process_id)
    assert _subscription_table(subscription_id).insync is True

    terminate_process_id = run_process("terminate_fiber_patch", _terminate_pipe_user_inputs(subscription_id))
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_leased_spectrum_create_validate_terminate(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """The shipped Optical Leased Spectrum create/validate/terminate workflows, on FlexILS client ports."""
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "lease-a.optical.test", "10.9.0.31")
    node_b = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "lease-b.optical.test", "10.9.0.32")

    create_process_id = run_process(
        "create_leased_spectrum",
        _create_pipe_user_inputs(
            product_id_for(LEASED_SPECTRUM_PRODUCT),
            node_a,
            node_b,
            CLIENT_PORT,
            CLIENT_PORT,
            "circuit-77",
            provider_name="Acme Telecom",
        ),
    )
    assert_process_completed(create_process_id)
    subscription_id = subscription_id_of_process(create_process_id)

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.customer_id == CUSTOMER_ID
    # The provider name has no dedicated block field: it is persisted by prefixing the pipe name.
    assert subscription.description == f"Acme Telecom circuit-77 ({LEASED_SPECTRUM_PRODUCT})"

    leased_spectrum = OpticalLeasedSpectrumSubscription.from_subscription(subscription_id)
    assert leased_spectrum.optical_pipe.optical_pipe_name == "Acme Telecom circuit-77"
    _assert_pipe_terminations(
        leased_spectrum.optical_pipe, "lease-a.optical.test", "lease-b.optical.test", CLIENT_PORT, OlsAddDropPortBlock
    )

    validate_process_id = run_process("validate_leased_spectrum", [{"subscription_id": subscription_id}])
    assert_process_completed(validate_process_id)

    reconcile_process_id = run_process("reconcile_leased_spectrum", [{"subscription_id": subscription_id}])
    assert_process_completed(reconcile_process_id)
    assert _subscription_table(subscription_id).insync is True

    terminate_process_id = run_process("terminate_leased_spectrum", _terminate_pipe_user_inputs(subscription_id))
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_pipe_blocks_by_types_matches_stored_pipe_types(
    run_process,
    product_id_for,
    assert_process_completed,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """pipe_blocks_by_types filters on the stored optical_pipe_type resource values.

    A span and a patch are seeded through the shipped create workflows; the
    ["Span"] filter must return only the span (proving the filter matches the
    representation the database actually stores), ["Span", "Patch"] both, and a
    non-seeded type nothing.
    """
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "types-a.optical.test", "10.9.0.41")
    node_b = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "types-b.optical.test", "10.9.0.42")
    for workflow_name, product_name, port_name, pipe_name in (
        ("create_fiber_span", FIBER_SPAN_PRODUCT, LINE_PORT, "types-span-01"),
        ("create_fiber_patch", FIBER_PATCH_PRODUCT, CLIENT_PORT, "types-patch-01"),
    ):
        process_id = run_process(
            workflow_name,
            _create_pipe_user_inputs(product_id_for(product_name), node_a, node_b, port_name, port_name, pipe_name),
        )
        assert_process_completed(process_id)

    assert sorted(block.optical_pipe_name for block in pipe_blocks_by_types(["Span"])) == ["types-span-01"]
    assert sorted(block.optical_pipe_name for block in pipe_blocks_by_types(["Span", "Patch"])) == [
        "types-patch-01",
        "types-span-01",
    ]
    assert pipe_blocks_by_types(["Leased Spectrum"]) == []


def test_optical_pipe_selector_reads_options_from_stored_values(
    run_process,
    product_id_for,
    assert_process_completed,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """The pipe selector offers instance ids labelled with the stored pipe names, without loading blocks.

    A span and a patch are seeded through the shipped create workflows; the
    unfiltered selector must offer both instance ids with their names, and the
    type-filtered selector only the span.
    """
    node_a = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "sel-a.optical.test", "10.9.0.51")
    node_b = _seed_node_instance(seed_optical_node, FLEXILS_NODE_PRODUCT, "sel-b.optical.test", "10.9.0.52")
    for workflow_name, product_name, port_name, pipe_name in (
        ("create_fiber_span", FIBER_SPAN_PRODUCT, LINE_PORT, "sel-span-01"),
        ("create_fiber_patch", FIBER_PATCH_PRODUCT, CLIENT_PORT, "sel-patch-01"),
    ):
        process_id = run_process(
            workflow_name,
            _create_pipe_user_inputs(product_id_for(product_name), node_a, node_b, port_name, port_name, pipe_name),
        )
        assert_process_completed(process_id)

    span_instance_id = str(pipe_blocks_by_types(["Span"])[0].subscription_instance_id)
    patch_instance_id = str(pipe_blocks_by_types(["Patch"])[0].subscription_instance_id)

    # Choice members submit the instance id (value) and display the pipe name (label).
    assert {member.value: member.label for member in optical_pipe_selector()} == {
        span_instance_id: "sel-span-01",
        patch_instance_id: "sel-patch-01",
    }
    assert {member.value: member.label for member in optical_pipe_selector(pipe_types=[OpticalPipeType.SPAN])} == {
        span_instance_id: "sel-span-01"
    }
    # The multiple selector delegates to the single one.
    multiple_optical_pipe_selector(pipe_types=[OpticalPipeType.SPAN])
