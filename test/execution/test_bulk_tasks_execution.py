"""Execution-level tests for the CSV bulk creation tasks.

These tests are database-backed: they run the shipped bulk tasks end to end
through the real orchestrator-core process engine, with the device-facing HAL
calls stubbed (``stub_node_device`` / ``stub_pipe_device``). Each bulk task
fans out to the shipped create sub-workflows with ``start_process``; the tests
assert the bulk process completes and the fanned-out subscriptions reach
ACTIVE with the CSV values persisted on their blocks.
"""

from typing import Any

import pytest
from sqlalchemy import select

import orchestrator.core.db as core_db
from orchestrator.core.db import SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import node_block_from_instance
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlock
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30Block
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatchSubscription
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import OpticalFiberSpanSubscription
from test.support.db import CUSTOMER_ID, node_instance_id_of_subscription
from test.support.devices import FAKE_CLIENT_PORTS, FAKE_LINE_PORTS
from test.support.topology import _flexils_gmpls_id

pytestmark = pytest.mark.db

FLEXILS_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_FLEXILS.value
GROOVE_G30_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_GROOVE_G30.value
FIBER_SPAN_PRODUCT = ProductName.OPTICAL_FIBER_SPAN.value
FIBER_PATCH_PRODUCT = ProductName.OPTICAL_FIBER_PATCH.value

LINE_PORT = FAKE_LINE_PORTS[0]
CLIENT_PORT = FAKE_CLIENT_PORTS[0]


def _bulk_user_inputs(csv_data: str) -> list[dict[str, Any]]:
    """Return the bulk task form inputs: customer page, then the CSV payload page."""
    return [
        {"customer_id": CUSTOMER_ID},
        {"achtung": "CREATE", "csv_data": csv_data, "delimiter": ","},
    ]


def _active_subscription_ids_by_description_prefix(prefix: str) -> list[str]:
    """Return the ids of the ACTIVE subscriptions whose description starts with the prefix."""
    with core_db.db.database_scope():
        rows = core_db.db.session.scalars(
            select(SubscriptionTable).where(SubscriptionTable.description.ilike(f"{prefix} (%"))
        ).all()
        return [
            str(row.subscription_id)
            for row in rows
            if SubscriptionLifecycle(row.status) == SubscriptionLifecycle.ACTIVE
        ]


def test_bulk_create_optical_nodes(
    run_process,
    assert_process_completed,
    active_location,
    stub_node_device,
) -> None:
    """The bulk nodes task fans out to the FlexILS and G30 create sub-workflows."""
    flexils_fqdn = "bulk-flexils-01.optical.test"
    g30_fqdn = "bulk-g30-01.optical.test"
    csv_data = (
        "location_code,vendor,platform,fqdn,dcn_loopback_ip,dcn_interface_ip,gmpls_id,target_id\n"
        f"loc-01,Nokia,FlexILS,{flexils_fqdn},192.0.2.1,192.0.2.2,{_flexils_gmpls_id(flexils_fqdn)},bulk-flexils-01.opti\n"
        f"loc-01,Nokia,Groove G30,{g30_fqdn},192.0.2.11,,,\n"
    )
    process_id = run_process("bulk_create_optical_nodes", _bulk_user_inputs(csv_data))
    assert_process_completed(process_id)

    flexils_ids = _active_subscription_ids_by_description_prefix(flexils_fqdn)
    assert len(flexils_ids) == 1
    flexils_block = node_block_from_instance(node_instance_id_of_subscription(flexils_ids[0]))
    assert isinstance(flexils_block, NokiaFlexIlsBlock)
    assert flexils_block.management.optical_module_node_dcn_loopback_ip == "192.0.2.1"
    assert flexils_block.optical_flexils_gmpls_id == _flexils_gmpls_id(flexils_fqdn)
    assert flexils_block.optical_flexils_target_id == "bulk-flexils-01.opti"

    g30_ids = _active_subscription_ids_by_description_prefix(g30_fqdn)
    assert len(g30_ids) == 1
    g30_block = node_block_from_instance(node_instance_id_of_subscription(g30_ids[0]))
    assert isinstance(g30_block, NokiaGrooveG30Block)
    assert g30_block.management.optical_module_node_dcn_loopback_ip == "192.0.2.11"
    assert g30_block.management.optical_module_node_dcn_interface_ip is None


def test_bulk_create_optical_pipes(
    run_process,
    assert_process_completed,
    seed_optical_node,
    stub_pipe_device,
) -> None:
    """The bulk pipes task fans out to the span and patch create sub-workflows."""
    node_a = seed_optical_node(FLEXILS_PRODUCT, "bulk-a.optical.test", "10.9.1.11")
    node_b = seed_optical_node(FLEXILS_PRODUCT, "bulk-b.optical.test", "10.9.1.12")
    node_a_block = node_block_from_instance(node_instance_id_of_subscription(node_a))
    node_b_block = node_block_from_instance(node_instance_id_of_subscription(node_b))
    fqdn_a = node_a_block.management.optical_module_node_fqdn
    fqdn_b = node_b_block.management.optical_module_node_fqdn
    csv_data = (
        "pipe_type,node_a_fqdn,port_a_name,node_b_fqdn,port_b_name,optical_pipe_name,provider_name\n"
        f"Span,{fqdn_a},{LINE_PORT},{fqdn_b},{LINE_PORT},bulk-span-01,\n"
        f"Patch,{fqdn_a},{CLIENT_PORT},{fqdn_b},{CLIENT_PORT},bulk-patch-01,\n"
    )
    process_id = run_process("bulk_create_optical_pipes", _bulk_user_inputs(csv_data))
    assert_process_completed(process_id)

    span_ids = _active_subscription_ids_by_description_prefix("bulk-span-01")
    assert len(span_ids) == 1
    with core_db.db.database_scope():
        span = OpticalFiberSpanSubscription.from_subscription(span_ids[0])
    assert [port.optical_port_name for port in span.optical_pipe.optical_pipe_terminations] == [LINE_PORT, LINE_PORT]

    patch_ids = _active_subscription_ids_by_description_prefix("bulk-patch-01")
    assert len(patch_ids) == 1
    with core_db.db.database_scope():
        patch = OpticalFiberPatchSubscription.from_subscription(patch_ids[0])
    assert [port.optical_port_name for port in patch.optical_pipe.optical_pipe_terminations] == [
        CLIENT_PORT,
        CLIENT_PORT,
    ]
