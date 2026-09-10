"""Topology seeders that build the ACTIVE subscriptions the workflows need.

The device-facing execution tests need a location (and sometimes a packet node or an
optical node) already ACTIVE in the database before they can exercise the workflows
under test. These fixtures create those subscriptions through the shipped create
workflows (or, where no shipped workflow exists, through the domain models directly),
stubbing the device calls as needed.
"""

import hashlib
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

import orchestrator.core.db as core_db
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import location_block_from_subscription
from orchestrator.optical.products.product_types.optical_packet_node import (
    OpticalModulePacketNodeSubscriptionInactive,
)
from test.support.db import (
    CUSTOMER_ID,
    _assert_process_completed,
    _product_id_of,
    _set_subscription_status,
    _subscription_id_of_process,
)
from test.support.devices import FAKE_SOFTWARE_VERSION, install_device_stubs


def _flexils_gmpls_id(fqdn: str) -> str:
    """Derive a deterministic GMPLS ID from a node FQDN (the shipped FlexILS create form requires one)."""
    digest = hashlib.sha256(fqdn.encode("utf-8")).digest()
    return f"10.255.{digest[0]}.{digest[1]}"


@pytest.fixture
def active_location(run_process: Callable[[str, list[dict[str, Any]]], str]) -> str:
    """Create an ACTIVE Optical Module Location via the shipped create workflow."""
    process_id = run_process(
        "create_optical_module_location",
        [
            {"product": _product_id_of("Optical Module Location")},
            {"customer_id": CUSTOMER_ID},
            {"location_code": "loc-01", "location_name": "Test Location"},
            {"longitude": "12.4964", "latitude": "41.9028"},
            {},
        ],
    )
    _assert_process_completed(process_id)
    return _subscription_id_of_process(process_id)


@pytest.fixture
def active_packet_node(
    run_process: Callable[[str, list[dict[str, Any]]], str],
    active_location: str,
) -> str:
    """Create an ACTIVE Optical Module Packet Node (there is no shipped workflow for it)."""
    with core_db.db.database_scope():
        subscription = OpticalModulePacketNodeSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id_of("Optical Module Packet Node")),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        subscription.optical_packet_node.management.optical_module_node_fqdn = "packet-node-01.test.local"
        subscription.optical_packet_node.location = location_block_from_subscription(active_location)
        # A fully provisioned packet node is in sync; the shipped coherent pluggable workflows
        # would otherwise not be able to modify/terminate subscriptions depending on it.
        subscription.insync = True
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    core_db.db.session.expire_all()
    _set_subscription_status(subscription_id, SubscriptionLifecycle.ACTIVE)
    return subscription_id


@pytest.fixture
def seed_optical_node(
    run_process: Callable[[str, list[dict[str, Any]]], str],
    active_location: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., str]:
    """Return a helper creating ACTIVE optical nodes of the shipped products (device calls stubbed)."""

    def _seed(
        product_name: str,
        fqdn: str,
        dcn_interface_ip: str,
        *,
        dcn_loopback_ip: str | None = None,
    ) -> str:
        """Create an ACTIVE optical node of the given product via the shipped create workflow (device calls stubbed).

        The node role is discovered from the device (never a form field): FlexILS nodes are
        line systems (always ``ROADM`` via the stub); Groove G30 and GX G42 nodes are
        ``TRANSPONDER`` via the stub.
        """
        install_device_stubs(monkeypatch, families=("node",))
        location: dict[str, Any] = {"location_id": active_location}
        management: dict[str, Any] = {
            "optical_module_node_fqdn": fqdn,
            "optical_module_node_dcn_interface_ip": dcn_interface_ip,
            "optical_module_node_dcn_loopback_ip": dcn_loopback_ip,
        }
        match product_name:
            case "Nokia FlexILS Optical Node":
                workflow_name = "create_optical_node_nokia_flexils"
                # The FlexILS TID (GMPLS NENAME) is distinct from the FQDN and is capped at 20
                # chars.
                vendor: dict[str, Any] = {
                    "optical_flexils_target_id": fqdn[:20],
                    "optical_flexils_gmpls_id": _flexils_gmpls_id(fqdn),
                }
                user_inputs: list[dict[str, Any]] = [
                    {"product": _product_id_of(product_name)},
                    {"customer_id": CUSTOMER_ID},
                    location,
                    management,
                    vendor,
                    {},
                ]
            case "Nokia Groove G30 Optical Node":
                workflow_name = "create_optical_node_nokia_groove_g30"
                user_inputs = [
                    {"product": _product_id_of(product_name)},
                    {"customer_id": CUSTOMER_ID},
                    location,
                    management,
                    {},
                ]
            case "Nokia GX G42 Optical Node":
                workflow_name = "create_optical_node_nokia_gx_g42"
                user_inputs = [
                    {"product": _product_id_of(product_name)},
                    {"customer_id": CUSTOMER_ID},
                    location,
                    management,
                    {},
                ]
            case _:
                msg = (
                    f"Unknown optical node product {product_name!r}; supported products are "
                    "'Nokia FlexILS Optical Node', 'Nokia Groove G30 Optical Node' and 'Nokia GX G42 Optical Node'"
                )
                raise ValueError(msg)
        process_id = run_process(workflow_name, user_inputs)
        _assert_process_completed(process_id)
        return _subscription_id_of_process(process_id)

    return _seed


@pytest.fixture
def active_coherent_pluggable_host(
    run_process: Callable[[str, list[dict[str, Any]]], str],
    active_location: str,
) -> str:
    """Create an ACTIVE Optical Module Packet Node fully provisioned as a coherent pluggable host.

    Unlike ``active_packet_node`` (which only sets the management block FQDN), this seeder
    also fills the fields the ACTIVE management block requires. The coherent pluggable
    workflows resolve the host node through ``packet_node_block_from_subscription`` (the
    most-derived lifecycle class), which cannot load a partially provisioned node.
    """
    with core_db.db.database_scope():
        subscription = OpticalModulePacketNodeSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id_of("Optical Module Packet Node")),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        management = subscription.optical_packet_node.management
        management.optical_module_node_fqdn = "pluggable-host-01.test.local"
        management.optical_module_node_vendor = "Nokia"
        management.optical_module_node_platform = "NCS"
        management.optical_module_node_software_version = FAKE_SOFTWARE_VERSION
        subscription.optical_packet_node.location = location_block_from_subscription(active_location)
        # A fully provisioned packet node is in sync; the shipped coherent pluggable workflows
        # would otherwise not be able to modify/terminate subscriptions depending on it.
        subscription.insync = True
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    core_db.db.session.expire_all()
    _set_subscription_status(subscription_id, SubscriptionLifecycle.ACTIVE)
    return subscription_id
