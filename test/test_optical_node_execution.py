"""Execution-level tests for the shipped Optical Node workflows.

These tests are database-backed: they run the shipped workflows of the three
shipped Optical Node products (Nokia FlexILS, Groove G30 and GX G42) end to
end through the real orchestrator-core process engine, with the device-facing
HAL calls stubbed (``stub_node_device`` / ``seed_optical_node``). They cover
the create workflow of every vendor (discovery step, block population and
persistence), the shared modify/validate/terminate steps of one vendor and
the FQDN uniqueness check of the create form.
"""

from typing import Any
from uuid import UUID

import pytest
from pydantic_forms.exceptions import FormValidationError

import orchestrator.core.db as core_db
from orchestrator.core.db import SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlock
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30Block
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42Block
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from test.conftest import CUSTOMER_ID, FAKE_SOFTWARE_VERSION, _flexils_gmpls_id

pytestmark = pytest.mark.db

FLEXILS_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_FLEXILS.value
GROOVE_G30_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_GROOVE_G30.value
GX_G42_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_GX_G42.value


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    """Return the subscription row of the given subscription id."""
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _flexils_create_user_inputs(
    product_id: str, location_id: str, fqdn: str, interface_ip: str, loopback_ip: str
) -> list[dict[str, Any]]:
    """Return the create form inputs of a Nokia FlexILS node (product, customer, location, management, vendor, summary)."""  # noqa: E501
    return [
        {"product": product_id},
        {"customer_id": CUSTOMER_ID},
        {"location_id": location_id},
        {
            "optical_module_node_fqdn": fqdn,
            "optical_module_node_dcn_interface_ip": interface_ip,
            "optical_module_node_dcn_loopback_ip": loopback_ip,
        },
        {
            "optical_flexils_gmpls_id": _flexils_gmpls_id(fqdn),
            "optical_flexils_target_id": fqdn,
        },
        {},
    ]


def _transponder_create_user_inputs(
    product_id: str, location_id: str, fqdn: str, interface_ip: str, loopback_ip: str
) -> list[dict[str, Any]]:
    """Return the create form inputs of a G30 / G42 transponder node (product, customer, location, management, summary)."""  # noqa: E501
    return [
        {"product": product_id},
        {"customer_id": CUSTOMER_ID},
        {"location_id": location_id},
        {
            "optical_module_node_fqdn": fqdn,
            "optical_module_node_dcn_interface_ip": interface_ip,
            "optical_module_node_dcn_loopback_ip": loopback_ip,
        },
        {},
    ]


def test_create_nokia_flexils_node(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    stub_node_device,
) -> None:
    """The shipped FlexILS create workflow discovers the node and persists the populated block."""
    fqdn = "flexils-node-01.optical.test"
    process_id = run_process(
        "create_optical_node_nokia_flexils",
        _flexils_create_user_inputs(
            product_id_for(FLEXILS_PRODUCT),
            active_location,
            fqdn,
            "192.0.2.11",
            "192.0.2.12",
        ),
    )
    assert_process_completed(process_id)
    subscription_id = subscription_id_of_process(process_id)

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.customer_id == CUSTOMER_ID
    assert subscription.description == f"{fqdn} ({FLEXILS_PRODUCT})"

    block = node_block_from_subscription(subscription_id)
    assert isinstance(block, NokiaFlexIlsBlock)
    # The role is discovered from the (stubbed) device, not taken from the form.
    assert block.optical_node_role == OpticalNodeRole.ROADM
    assert block.management.optical_module_node_fqdn == fqdn
    assert block.management.optical_module_node_dcn_interface_ip == "192.0.2.11"
    assert block.management.optical_module_node_dcn_loopback_ip == "192.0.2.12"
    assert block.management.optical_module_node_software_version == FAKE_SOFTWARE_VERSION
    assert block.management.optical_module_node_vendor == Vendor.NOKIA
    assert block.management.optical_module_node_platform == Platform.FLEXILS
    assert block.optical_flexils_gmpls_id == _flexils_gmpls_id(fqdn)
    assert block.optical_flexils_target_id == fqdn


def test_create_nokia_groove_g30_node(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    stub_node_device,
) -> None:
    """The shipped Groove G30 create workflow retrieves the software version and persists the block."""
    fqdn = "g30-node-01.optical.test"
    process_id = run_process(
        "create_optical_node_nokia_groove_g30",
        _transponder_create_user_inputs(
            product_id_for(GROOVE_G30_PRODUCT),
            active_location,
            fqdn,
            "192.0.2.21",
            "192.0.2.22",
        ),
    )
    assert_process_completed(process_id)
    subscription_id = subscription_id_of_process(process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE

    block = node_block_from_subscription(subscription_id)
    assert isinstance(block, NokiaGrooveG30Block)
    assert block.optical_node_role == OpticalNodeRole.TRANSPONDER
    assert block.management.optical_module_node_fqdn == fqdn
    assert block.management.optical_module_node_dcn_interface_ip == "192.0.2.21"
    assert block.management.optical_module_node_dcn_loopback_ip == "192.0.2.22"
    assert block.management.optical_module_node_software_version == FAKE_SOFTWARE_VERSION
    assert block.management.optical_module_node_vendor == Vendor.NOKIA
    assert block.management.optical_module_node_platform == Platform.GROOVE_G30


def test_create_nokia_gx_g42_node(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    stub_node_device,
) -> None:
    """The shipped GX G42 create workflow retrieves the software version and persists the block."""
    fqdn = "g42-node-01.optical.test"
    process_id = run_process(
        "create_optical_node_nokia_gx_g42",
        _transponder_create_user_inputs(
            product_id_for(GX_G42_PRODUCT),
            active_location,
            fqdn,
            "192.0.2.31",
            "192.0.2.32",
        ),
    )
    assert_process_completed(process_id)
    subscription_id = subscription_id_of_process(process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE

    block = node_block_from_subscription(subscription_id)
    assert isinstance(block, NokiaGxG42Block)
    assert block.optical_node_role == OpticalNodeRole.TRANSPONDER
    assert block.management.optical_module_node_fqdn == fqdn
    assert block.management.optical_module_node_dcn_interface_ip == "192.0.2.31"
    assert block.management.optical_module_node_dcn_loopback_ip == "192.0.2.32"
    assert block.management.optical_module_node_software_version == FAKE_SOFTWARE_VERSION
    assert block.management.optical_module_node_vendor == Vendor.NOKIA
    assert block.management.optical_module_node_platform == Platform.GX_G42


def test_node_full_lifecycle_g30(
    run_process,
    seed_optical_node,
    assert_process_completed,
    subscription_id_of_process,
    stub_node_device,
) -> None:
    """The full create -> modify -> validate -> terminate cycle of the shipped Groove G30 workflows."""
    subscription_id = seed_optical_node(
        GROOVE_G30_PRODUCT,
        "g30-life-01.optical.test",
        "192.0.2.41",
        dcn_loopback_ip="192.0.2.42",
    )
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE

    modify_process_id = run_process(
        "modify_optical_node_nokia_groove_g30",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {
                "optical_module_node_fqdn": "g30-life-02.optical.test",
                "optical_module_node_dcn_interface_ip": "192.0.2.41",
                "optical_module_node_dcn_loopback_ip": "192.0.2.42",
            },
            {},
        ],
    )
    assert_process_completed(modify_process_id)
    # The shipped modify workflow updates and persists the block, keeping the subscription ACTIVE.
    block = node_block_from_subscription(subscription_id)
    assert isinstance(block, NokiaGrooveG30Block)
    assert block.management.optical_module_node_fqdn == "g30-life-02.optical.test"
    assert block.management.optical_module_node_dcn_interface_ip == "192.0.2.41"
    assert block.management.optical_module_node_dcn_loopback_ip == "192.0.2.42"
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE

    validate_process_id = run_process(
        "validate_optical_node_nokia_groove_g30",
        [{"subscription_id": subscription_id}],
    )
    assert_process_completed(validate_process_id)
    # The shared validate steps refresh the software version from the (stubbed) device.
    assert (
        node_block_from_subscription(subscription_id).management.optical_module_node_software_version
        == FAKE_SOFTWARE_VERSION
    )

    terminate_process_id = run_process(
        "terminate_optical_node_nokia_groove_g30",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_create_nokia_groove_g30_duplicate_fqdn_rejected(
    run_process,
    product_id_for,
    seed_optical_node,
    active_location,
    stub_node_device,
) -> None:
    """A create with an FQDN already in use fails the form validation against the database."""
    seed_optical_node(GROOVE_G30_PRODUCT, "g30-dup-01.optical.test", "192.0.2.51")

    with pytest.raises(FormValidationError, match="already in use"):
        run_process(
            "create_optical_node_nokia_groove_g30",
            _transponder_create_user_inputs(
                product_id_for(GROOVE_G30_PRODUCT),
                active_location,
                "g30-dup-01.optical.test",
                "192.0.2.52",
                "192.0.2.53",
            ),
        )
