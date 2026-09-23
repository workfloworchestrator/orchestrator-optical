"""Execution-level tests for the shipped Optical Digital Service workflows.

These tests are database-backed: they run the shipped create/modify/validate/
reconcile/terminate workflows of the Optical Digital Service products end to
end through the real orchestrator-core process engine, with the device-facing
HAL calls stubbed (``stub_ods_device``).

Topology: two ACTIVE Nokia Groove G30 transponder nodes joined by a shipped
``create_fiber_patch`` between their transponder line ports. The patch
terminations are the line-port inventory the digital service links
(``line_port_selector`` reads existing ``OpticalTransponderLinePortBlock``
instances); the peer resolution finds the two line ports directly connected,
so the service provisions with the ``direct_connection`` path and no OLS
sections. Transceiver modes, client/line ports and power alignment are faked.
"""

from typing import Any
from uuid import UUID

import pytest
from pydantic_forms.exceptions import FormValidationError

import orchestrator.core.db as core_db
from orchestrator.core.db import SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSubscription
from orchestrator.optical.products.product_types.optical_pipe.fiber_patch import OpticalFiberPatchSubscription
from test.support.db import CUSTOMER_ID, node_instance_id_of_subscription
from test.support.devices import install_device_stubs

pytestmark = pytest.mark.db

G30_NODE_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_GROOVE_G30.value
FIBER_PATCH_PRODUCT = ProductName.OPTICAL_FIBER_PATCH.value
DIGITAL_100G_PRODUCT = ProductName.OPTICAL_DIGITAL_SERVICE_100G_ETHERNET.value

#: G30-style ports on the same card (shelf 1, slot 2): ports 1-2 are line, the rest client.
FAKE_LINE_PORT = "port-1/2/1"
FAKE_LINE_PORT_B = "port-1/2/2"
FAKE_CLIENT_PORT = "port-1/2/5"
FAKE_MODE = "QPSK_100G"

FREQUENCY_1 = 193_450_000
BANDWIDTH_1 = 100_000
MODIFIED_FREQUENCY_1 = 193_550_000


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    """Return the subscription row of the given subscription id."""
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _seed_transponder_topology(
    run_process, product_id_for, seed_optical_node, monkeypatch, assert_process_completed, subscription_id_of_process
) -> tuple[str, str, str, str]:
    """Seed two G30 nodes joined by a fiber patch between their line ports.

    Returns the (src node block instance id, dst node block instance id,
    src line port block instance id, dst line port block instance id).
    """
    install_device_stubs(
        monkeypatch,
        families=("pipe", "ods"),
        client_ports=(FAKE_CLIENT_PORT,),
        line_ports=(FAKE_LINE_PORT, FAKE_LINE_PORT_B),
        modes=(FAKE_MODE,),
    )
    src_sub = seed_optical_node(G30_NODE_PRODUCT, "ods-a.optical.test", "10.9.3.11")
    dst_sub = seed_optical_node(G30_NODE_PRODUCT, "ods-b.optical.test", "10.9.3.12")
    src_node = node_instance_id_of_subscription(src_sub)
    dst_node = node_instance_id_of_subscription(dst_sub)

    process_id = run_process(
        "create_fiber_patch",
        [
            {"product": product_id_for(FIBER_PATCH_PRODUCT)},
            {"customer_id": CUSTOMER_ID},
            {"node_a_instance_id": src_node, "node_b_instance_id": dst_node},
            {"optical_pipe_name": "ods-line-patch", "port_a_name": FAKE_LINE_PORT, "port_b_name": FAKE_LINE_PORT},
            {},
        ],
    )
    assert_process_completed(process_id)
    patch_sub_id = subscription_id_of_process(process_id)

    patch = OpticalFiberPatchSubscription.from_subscription(patch_sub_id)
    terminations = list(patch.optical_pipe.optical_pipe_terminations)
    assert len(terminations) == 2
    src_line = next(t for t in terminations if str(t.optical_port_host_node.subscription_instance_id) == src_node)
    dst_line = next(t for t in terminations if str(t.optical_port_host_node.subscription_instance_id) == dst_node)
    return src_node, dst_node, str(src_line.subscription_instance_id), str(dst_line.subscription_instance_id)


def _create_user_inputs(
    product_id: str,
    src_node: str,
    dst_node: str,
    src_line: str,
    dst_line: str,
    *,
    service_name: str = "ods-svc-01",
    channel_name: str = "ods-ch-01",
) -> list[dict[str, Any]]:
    """Return the create form inputs for a single-channel direct-connection service."""
    return [
        {"product": product_id},
        {"customer_id": CUSTOMER_ID},
        {
            "optical_digital_service_name": service_name,
            "src_node_block_instance_id": src_node,
            "dst_node_block_instance_id": dst_node,
            "channel_name_1": channel_name,
            "channel_name_2": "",
        },
        {"unused_src_client": FAKE_CLIENT_PORT, "unused_dst_client": FAKE_CLIENT_PORT},
        {"src_lines": [src_line], "dst_lines": [dst_line]},
        {"optical_transport_mode": FAKE_MODE, "frequency_1": FREQUENCY_1, "bandwidth_1": BANDWIDTH_1},
        {"intermediate_node_instance_ids": []},
        {"exclude_node_instance_ids": [], "exclude_pipe_instance_ids": []},
        {"optical_path": "direct_connection"},
        {},
    ]


def test_create_optical_digital_service_end_to_end(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_node_device,
    monkeypatch,
) -> None:
    """The shipped create workflow provisions a direct-connection service between two transponders."""
    src_node, dst_node, src_line, dst_line = _seed_transponder_topology(
        run_process,
        product_id_for,
        seed_optical_node,
        monkeypatch,
        assert_process_completed,
        subscription_id_of_process,
    )

    process_id = run_process(
        "create_optical_digital_service",
        _create_user_inputs(product_id_for(DIGITAL_100G_PRODUCT), src_node, dst_node, src_line, dst_line),
    )
    assert_process_completed(process_id)
    subscription_id = subscription_id_of_process(process_id)

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.customer_id == CUSTOMER_ID
    assert subscription.description == f"ods-svc-01 ({DIGITAL_100G_PRODUCT})"

    digital = OpticalDigitalServiceSubscription.from_subscription(subscription_id).optical_digital_service
    assert digital.optical_digital_service_name == "ods-svc-01"
    assert int(digital.optical_digital_service_speed) == 100
    channels = list(digital.optical_digital_service_transport_channels)
    assert len(channels) == 1
    assert str(channels[0].optical_transport_channel_name) == "ods-ch-01"
    assert str(channels[0].optical_transport_mode) == FAKE_MODE
    assert int(channels[0].optical_transport_central_frequency) == FREQUENCY_1
    # Direct connection carries no OLS sections.
    assert list(channels[0].optical_transport_spectrum.optical_spectrum_sections) == []
    clients = list(digital.optical_digital_service_client_ports)
    assert sorted(port.optical_port_name for port in clients) == [FAKE_CLIENT_PORT, FAKE_CLIENT_PORT]
    lines = list(channels[0].optical_transport_line_ports)
    assert {str(port.subscription_instance_id) for port in lines} == {src_line, dst_line}


def test_full_lifecycle_create_modify_validate_reconcile_terminate(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_node_device,
    monkeypatch,
) -> None:
    """The full create -> modify -> validate -> reconcile -> terminate cycle of the shipped workflows."""
    src_node, dst_node, src_line, dst_line = _seed_transponder_topology(
        run_process,
        product_id_for,
        seed_optical_node,
        monkeypatch,
        assert_process_completed,
        subscription_id_of_process,
    )

    create_process_id = run_process(
        "create_optical_digital_service",
        _create_user_inputs(product_id_for(DIGITAL_100G_PRODUCT), src_node, dst_node, src_line, dst_line),
    )
    assert_process_completed(create_process_id)
    subscription_id = subscription_id_of_process(create_process_id)

    modify_process_id = run_process(
        "modify_optical_digital_service",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {"optical_digital_service_name": "ods-svc-02", "channel_name_1": "ods-ch-02"},
            {"optical_transport_mode": FAKE_MODE, "frequency_1": MODIFIED_FREQUENCY_1, "bandwidth_1": BANDWIDTH_1},
            {},
        ],
    )
    assert_process_completed(modify_process_id)
    assert _subscription_table(subscription_id).description == f"ods-svc-02 ({DIGITAL_100G_PRODUCT})"
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE
    digital = OpticalDigitalServiceSubscription.from_subscription(subscription_id).optical_digital_service
    assert digital.optical_digital_service_name == "ods-svc-02"
    channels = list(digital.optical_digital_service_transport_channels)
    assert str(channels[0].optical_transport_channel_name) == "ods-ch-02"
    assert int(channels[0].optical_transport_central_frequency) == MODIFIED_FREQUENCY_1

    validate_process_id = run_process("validate_optical_digital_service", [{"subscription_id": subscription_id}])
    assert_process_completed(validate_process_id)

    reconcile_process_id = run_process("reconcile_optical_digital_service", [{"subscription_id": subscription_id}])
    assert_process_completed(reconcile_process_id)
    assert _subscription_table(subscription_id).insync is True

    terminate_process_id = run_process(
        "terminate_optical_digital_service",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_create_rejects_client_port_already_in_use(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    seed_optical_node,
    stub_node_device,
    monkeypatch,
) -> None:
    """A second service reusing the same client port fails: the port already carries a service."""
    src_node, dst_node, src_line, dst_line = _seed_transponder_topology(
        run_process,
        product_id_for,
        seed_optical_node,
        monkeypatch,
        assert_process_completed,
        subscription_id_of_process,
    )

    first_id = run_process(
        "create_optical_digital_service",
        _create_user_inputs(
            product_id_for(DIGITAL_100G_PRODUCT), src_node, dst_node, src_line, dst_line, service_name="ods-first"
        ),
    )
    assert_process_completed(first_id)

    # The client-port selector already excludes ports carrying a service, so the
    # resubmitted port name is not a valid Choice anymore and the form rejects it.
    with pytest.raises(FormValidationError):
        run_process(
            "create_optical_digital_service",
            _create_user_inputs(
                product_id_for(DIGITAL_100G_PRODUCT),
                src_node,
                dst_node,
                src_line,
                dst_line,
                service_name="ods-second",
                channel_name="ods-ch-02",
            ),
        )
