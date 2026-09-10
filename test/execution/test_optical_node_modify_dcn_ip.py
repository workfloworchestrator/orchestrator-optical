"""Execution-level tests for deleting DCN IPs in the shipped Optical Node modify workflows.

These tests are database-backed: they seed an ACTIVE optical node of the shipped
products and run the shipped modify workflow end to end through the real
orchestrator-core process engine, asserting on the persisted DCN loopback/interface
IPs. They cover the ``delete_*`` checkboxes of the shared management modify form:
deleting a single DCN IP, deleting both IPs for FlexILS (``require_dcn_ip=False``,
mirroring its create form), and the rejection of removing the last DCN IP for the
products that require one (Groove G30, ``require_dcn_ip=True``).

They live in their own module so the deletion coverage is self-contained. The node
role/software-version retrieval step is stubbed locally (patching only that target)
because the shared ``stub_node_device``/``seed_optical_node`` fixtures also patch a
validate-workflow target that is currently stale in the committed conftest.
"""

from uuid import UUID

import pytest
from pydantic_forms.exceptions import FormValidationError

import orchestrator.core.db as core_db
from orchestrator.core.db import SubscriptionTable
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlock
from test.support.db import CUSTOMER_ID
from test.support.devices import _fake_retrieve_optical_node_role_and_software_version
from test.support.topology import _flexils_gmpls_id

pytestmark = pytest.mark.db

FLEXILS_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_FLEXILS.value
GROOVE_G30_PRODUCT = ProductName.OPTICAL_NODE_NOKIA_GROOVE_G30.value


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    """Return the subscription row of the given subscription id."""
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _stub_node_retrieve(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub only the node role/software-version retrieval step that the create/modify workflows invoke."""
    monkeypatch.setattr(
        "orchestrator.optical.workflows.optical_node.shared.retrieve._retrieve_optical_node_role_and_software_version",
        _fake_retrieve_optical_node_role_and_software_version,
    )


def _management_page(
    fqdn: str,
    interface_ip: str,
    loopback_ip: str,
    *,
    delete_loopback: bool,
    delete_interface: bool,
) -> dict:
    """Return the management page input of an optical node modify form, with the delete checkboxes set."""
    return {
        "optical_module_node_fqdn": fqdn,
        "optical_module_node_dcn_interface_ip": interface_ip,
        "optical_module_node_dcn_loopback_ip": loopback_ip,
        "delete_optical_module_node_dcn_loopback_ip": delete_loopback,
        "delete_optical_module_node_dcn_interface_ip": delete_interface,
    }


def _flexils_vendor_page(fqdn: str) -> dict:
    """Return the FlexILS vendor page input (GMPLS ID + TID), keeping the seeded values."""
    return {
        "optical_flexils_gmpls_id": _flexils_gmpls_id(fqdn),
        "optical_flexils_target_id": fqdn.split(".")[0],
    }


def _seed_node(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    *,
    workflow_name: str,
    product_name: str,
    fqdn: str,
    interface_ip: str,
    loopback_ip: str,
    vendor_page: dict | None,
) -> str:
    """Create an ACTIVE node of the shipped product via its create workflow (retrieval step stubbed)."""
    pages: list[dict] = [
        {"product": product_id_for(product_name)},
        {"customer_id": CUSTOMER_ID},
        {"location_id": active_location},
        {
            "optical_module_node_fqdn": fqdn,
            "optical_module_node_dcn_interface_ip": interface_ip,
            "optical_module_node_dcn_loopback_ip": loopback_ip,
        },
    ]
    if vendor_page is not None:
        pages.append(vendor_page)
    pages.append({})
    process_id = run_process(workflow_name, pages)
    assert_process_completed(process_id)
    return subscription_id_of_process(process_id)


def test_modify_flexils_deletes_loopback_ip(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    monkeypatch,
) -> None:
    """Checking the 'delete DCN loopback IP' box persists a None loopback IP, keeping the interface IP."""
    _stub_node_retrieve(monkeypatch)
    fqdn = "flex-mod-lo.optical.test"
    subscription_id = _seed_node(
        run_process,
        product_id_for,
        assert_process_completed,
        subscription_id_of_process,
        active_location,
        workflow_name="create_optical_node_nokia_flexils",
        product_name=FLEXILS_PRODUCT,
        fqdn=fqdn,
        interface_ip="192.0.2.71",
        loopback_ip="192.0.2.72",
        vendor_page=_flexils_vendor_page(fqdn),
    )

    process_id = run_process(
        "modify_optical_node_nokia_flexils",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            _management_page(fqdn, "192.0.2.71", "192.0.2.72", delete_loopback=True, delete_interface=False),
            _flexils_vendor_page(fqdn),
            {},
        ],
    )
    assert_process_completed(process_id)

    block = node_block_from_subscription(subscription_id)
    assert isinstance(block, NokiaFlexIlsBlock)
    assert block.management.optical_module_node_dcn_loopback_ip is None
    assert block.management.optical_module_node_dcn_interface_ip == "192.0.2.71"
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.ACTIVE


def test_modify_flexils_deletes_both_dcn_ips(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    monkeypatch,
) -> None:
    """FlexILS modify allows removing both DCN IPs (``require_dcn_ip=False``, mirroring its create form)."""
    _stub_node_retrieve(monkeypatch)
    fqdn = "flex-mod-both.optical.test"
    subscription_id = _seed_node(
        run_process,
        product_id_for,
        assert_process_completed,
        subscription_id_of_process,
        active_location,
        workflow_name="create_optical_node_nokia_flexils",
        product_name=FLEXILS_PRODUCT,
        fqdn=fqdn,
        interface_ip="192.0.2.75",
        loopback_ip="192.0.2.76",
        vendor_page=_flexils_vendor_page(fqdn),
    )

    process_id = run_process(
        "modify_optical_node_nokia_flexils",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            _management_page(fqdn, "192.0.2.75", "192.0.2.76", delete_loopback=True, delete_interface=True),
            _flexils_vendor_page(fqdn),
            {},
        ],
    )
    assert_process_completed(process_id)

    block = node_block_from_subscription(subscription_id)
    assert isinstance(block, NokiaFlexIlsBlock)
    assert block.management.optical_module_node_dcn_loopback_ip is None
    assert block.management.optical_module_node_dcn_interface_ip is None


def test_modify_g30_cannot_delete_last_dcn_ip(
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    active_location,
    monkeypatch,
) -> None:
    """Removing the last DCN IP is rejected for Groove G30 (``require_dcn_ip=True``)."""
    _stub_node_retrieve(monkeypatch)
    fqdn = "g30-mod-both.optical.test"
    subscription_id = _seed_node(
        run_process,
        product_id_for,
        assert_process_completed,
        subscription_id_of_process,
        active_location,
        workflow_name="create_optical_node_nokia_groove_g30",
        product_name=GROOVE_G30_PRODUCT,
        fqdn=fqdn,
        interface_ip="192.0.2.81",
        loopback_ip="192.0.2.82",
        vendor_page=None,
    )

    with pytest.raises(FormValidationError, match="At least one of DCN loopback IP or DCN interface IP"):
        run_process(
            "modify_optical_node_nokia_groove_g30",
            [
                {"subscription_id": subscription_id},
                {"customer_id": CUSTOMER_ID},
                _management_page(fqdn, "192.0.2.81", "192.0.2.82", delete_loopback=True, delete_interface=True),
                {},
            ],
        )
