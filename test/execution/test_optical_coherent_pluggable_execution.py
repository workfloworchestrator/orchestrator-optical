"""Execution-level tests for the shipped Optical Coherent Pluggable workflows.

These tests are database-backed: they run the shipped workflows end to end through the
real orchestrator-core process engine (``start_process`` with the threadpool executor),
so the paths that break first as models drift are actually executed: the create form's
host-node resolution and the port-occupancy check against the database, the subscription
construction and description, the block persistence, and the modify/terminate/validate
lifecycle transitions.

The family makes no device calls, so no device stubs are needed; the only external
dependency is an ACTIVE Optical Module Packet Node hosting the pluggable (the
``active_coherent_pluggable_host`` seeder in ``conftest.py``).
"""

from typing import Any
from uuid import UUID

import pytest
from pydantic_forms.exceptions import FormValidationError
from sqlalchemy import update

import orchestrator.core.db as core_db
from orchestrator.core.db import FixedInputTable, SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import packet_node_block_from_subscription
from orchestrator.optical.products.product_blocks.optical_node.optical_packet_node import OpticalModulePacketNodeBlock
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
    OpticalCoherentPluggablePartNumber,
)

pytestmark = pytest.mark.db

PRODUCT_NAME = "Cisco DP04QSDD HK9 Coherent Pluggable"
PART_NUMBER = OpticalCoherentPluggablePartNumber.CISCO_DP04QSDD_HK9
CUSTOMER_ID = "cust-1"
HOST_NODE_FQDN = "pluggable-host-01.test.local"
PORT_NAME = "port-1/2/1"
PORT_DESCRIPTION = "Uplink to core"
FIRMWARE_VERSION = "2.1.3"
MODIFIED_FIRMWARE_VERSION = "2.2.0"

DESCRIPTION = f"{HOST_NODE_FQDN} {PORT_NAME} ({PART_NUMBER.value})"


@pytest.fixture(autouse=True)
def _valid_part_number_fixed_input(postgres_database: Any) -> None:
    """Work around a src bug in the shipped catalog generation.

    ``_product_fixed_inputs`` (src/orchestrator/optical/migrations/generate.py:294) fills the
    required ``optical_coherent_pluggable_part_number`` fixed input with a human-readable
    placeholder (the field's humanized name) because the model field has no default. The
    placeholder is not a valid ``OpticalCoherentPluggablePartNumber`` member, so
    ``from_product_id`` (called by the shipped construct step) fails the enum validation
    and the shipped create workflow cannot run. Set a valid value for the affected products;
    the shipped construct step overwrites the field with the user's choice anyway.
    """
    with core_db.db.database_scope():
        core_db.db.session.execute(
            update(FixedInputTable)
            .where(FixedInputTable.name == "optical_coherent_pluggable_part_number")
            .values(value=PART_NUMBER.value)
        )
        core_db.db.session.commit()


def _subscription(subscription_id: str) -> SubscriptionTable:
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _create_user_inputs(product_id_for, host_node_id: str) -> list[dict]:
    """Form pages of the shipped create workflow: product, customer, pluggable data, summary."""
    return [
        {"product": product_id_for(PRODUCT_NAME)},
        {"customer_id": CUSTOMER_ID},
        {
            "optical_packet_node_id": host_node_id,
            "optical_coherent_pluggable_part_number": PART_NUMBER.value,
            "optical_port_name": PORT_NAME,
            "optical_port_description": PORT_DESCRIPTION,
            "optical_coherent_pluggable_firmware_version": FIRMWARE_VERSION,
        },
        {},
    ]


def _run_create(run_process, product_id_for, host_node_id: str) -> str:
    """Run the shipped create workflow and return the process id."""
    return run_process("create_optical_coherent_pluggable", _create_user_inputs(product_id_for, host_node_id))


def test_create_coherent_pluggable_end_to_end(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_coherent_pluggable_host,
) -> None:
    """The shipped create workflow executes end to end: form checks against the database,
    subscription construction, block persistence, description and process relation."""
    process_id = _run_create(run_process, product_id_for, active_coherent_pluggable_host)
    assert_process_completed(process_id)
    subscription_id = subscription_id_of_process(process_id)

    subscription = _subscription(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.customer_id == CUSTOMER_ID
    assert subscription.description == DESCRIPTION

    model = OpticalCoherentPluggable.from_subscription(subscription_id)
    assert model.optical_coherent_pluggable_part_number == PART_NUMBER
    block = model.optical_coherent_pluggable
    assert block.optical_port_name == PORT_NAME
    assert block.optical_port_description == PORT_DESCRIPTION
    assert block.optical_coherent_pluggable_firmware_version == FIRMWARE_VERSION
    # The block stores the part number as a regular field, kept in sync with the
    # subscription fixed input by the construct step.
    assert block.optical_coherent_pluggable_part_number == PART_NUMBER
    host_node = block.optical_port_host_node
    assert isinstance(host_node, OpticalModulePacketNodeBlock)
    assert str(host_node.management.optical_module_node_fqdn) == HOST_NODE_FQDN
    assert (
        host_node.subscription_instance_id
        == packet_node_block_from_subscription(active_coherent_pluggable_host).subscription_instance_id
    )


def test_full_lifecycle_create_modify_validate_terminate(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_coherent_pluggable_host,
) -> None:
    """The full create -> modify -> validate -> terminate cycle of the shipped workflows."""
    process_id = _run_create(run_process, product_id_for, active_coherent_pluggable_host)
    assert_process_completed(process_id)
    subscription_id = subscription_id_of_process(process_id)

    modify_process_id = run_process(
        "modify_optical_coherent_pluggable",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {
                "instruction": "Update the firmware version",
                "optical_port_description": PORT_DESCRIPTION,
                "optical_coherent_pluggable_firmware_version": MODIFIED_FIRMWARE_VERSION,
            },
            {},
        ],
    )
    assert_process_completed(modify_process_id)
    # The shipped modify workflow refreshes the subscription description; it reads the host
    # node, port name and part number, none of which the modify form changes.
    assert _subscription(subscription_id).description == DESCRIPTION
    modified = OpticalCoherentPluggable.from_subscription(subscription_id)
    assert modified.optical_coherent_pluggable.optical_coherent_pluggable_firmware_version == MODIFIED_FIRMWARE_VERSION
    assert modified.optical_coherent_pluggable.optical_port_description == PORT_DESCRIPTION
    assert SubscriptionLifecycle(_subscription(subscription_id).status) == SubscriptionLifecycle.ACTIVE
    assert _subscription(subscription_id).insync is True

    validate_process_id = run_process("validate_optical_coherent_pluggable", [{"subscription_id": subscription_id}])
    assert_process_completed(validate_process_id)

    terminate_process_id = run_process(
        "terminate_optical_coherent_pluggable",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_create_rejects_port_already_occupied_on_host_node(
    run_process,
    product_id_for,
    assert_process_completed,
    active_coherent_pluggable_host,
) -> None:
    """A second create with a port already occupied on the same host node fails form validation."""
    process_id = _run_create(run_process, product_id_for, active_coherent_pluggable_host)
    assert_process_completed(process_id)

    with pytest.raises(FormValidationError, match="already occupied"):
        _run_create(run_process, product_id_for, active_coherent_pluggable_host)
