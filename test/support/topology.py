"""Topology seeders that build the ACTIVE subscriptions the workflows need.

The device-facing execution tests need a location (and sometimes a packet node or an
optical node) already ACTIVE in the database before they can exercise the workflows
under test. These fixtures create those subscriptions through the shipped create
workflows (or, where no shipped workflow exists, through the domain models directly),
stubbing the device calls as needed.
"""

from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

import orchestrator.core.db as core_db
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import location_block_from_instance
from orchestrator.optical.products.product_types.optical_location import OpticalModuleLocationSubscription
from orchestrator.optical.products.product_types.optical_packet_node import (
    OpticalModulePacketNodeSubscriptionInactive,
)
from test.support.db import (
    CUSTOMER_ID,
    _assert_process_completed,
    _product_id_of,
    _set_subscription_status,
    _subscription_id_of_process,
    packet_node_instance_id_of_subscription,
)
from test.support.devices import FAKE_SOFTWARE_VERSION, fake_flexils_gmpls_id, install_device_stubs


def _flexils_gmpls_id(fqdn: str) -> str:
    """Return the GMPLS ID the faked device reports for the FlexILS node seeded with the given name."""
    return fake_flexils_gmpls_id(fqdn[:20])


@pytest.fixture
def active_location(run_process: Callable[[str, list[dict[str, Any]]], str]) -> str:
    """Create an ACTIVE Optical Module Location via the shipped create workflow.

    Returns the subscription instance id of the location block.
    """
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
    subscription_id = _subscription_id_of_process(process_id)
    with core_db.db.database_scope():
        subscription = OpticalModuleLocationSubscription.from_subscription(subscription_id)
        return str(subscription.optical_location.subscription_instance_id)


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
        location: dict[str, Any] = {"location_instance_id": active_location}
        management: dict[str, Any] = {
            "optical_module_node_management_ip": dcn_interface_ip,
            "optical_module_node_management_loopback_ip": dcn_loopback_ip,
        }
        identity: dict[str, Any] = {"optical_module_node_name": fqdn}
        user_inputs: list[dict[str, Any]] = [
            {"product": _product_id_of(product_name)},
            {"customer_id": CUSTOMER_ID},
            location,
        ]
        match product_name:
            case "Nokia FlexILS Optical Node":
                workflow_name = "create_optical_node_nokia_flexils"
                # The FlexILS TID (GMPLS NENAME) is distinct from the node name and is capped at
                # 20 chars; the GMPLS ID is read from the (stubbed) device.
                user_inputs.append({"optical_flexils_target_id": fqdn[:20]})
            case "Nokia Groove G30 Optical Node":
                workflow_name = "create_optical_node_nokia_groove_g30"
            case "Nokia GX G42 Optical Node":
                workflow_name = "create_optical_node_nokia_gx_g42"
            case _:
                msg = (
                    f"Unknown optical node product {product_name!r}; supported products are "
                    "'Nokia FlexILS Optical Node', 'Nokia Groove G30 Optical Node' and 'Nokia GX G42 Optical Node'"
                )
                raise ValueError(msg)
        user_inputs += [management, identity, {}]
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

    This seeder fills the fields the ACTIVE management block requires. The coherent pluggable
    workflows resolve the host node through ``packet_node_block_from_instance`` (the
    most-derived lifecycle class), which cannot load a partially provisioned node.

    Returns the subscription instance id of the packet node block.
    """
    with core_db.db.database_scope():
        subscription = OpticalModulePacketNodeSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id_of("Optical Module Packet Node")),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        management = subscription.optical_packet_node.management
        management.optical_module_node_name = "pluggable-host-01.test.local"
        management.optical_module_node_vendor = "Nokia"
        management.optical_module_node_platform = "NCS"
        management.optical_module_node_software_version = FAKE_SOFTWARE_VERSION
        subscription.optical_packet_node.location = location_block_from_instance(active_location)
        # A fully provisioned packet node is in sync; the shipped coherent pluggable workflows
        # would otherwise not be able to modify/terminate subscriptions depending on it.
        subscription.insync = True
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    core_db.db.session.expire_all()
    _set_subscription_status(subscription_id, SubscriptionLifecycle.ACTIVE)
    return packet_node_instance_id_of_subscription(subscription_id)
