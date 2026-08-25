"""Shared creation utilities and steps for Optical Nodes."""

from typing import Any

from pydantic_forms.types import UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import location_block_from_subscription, subscriptions_by_product_type_and_instance_value
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress

OPTICAL_NODE_PRODUCT_TYPES = [
    ProductType.OPTICAL_NODE_NOKIA_FLEXILS.value,
    ProductType.OPTICAL_NODE_NOKIA_GROOVE_G30.value,
    ProductType.OPTICAL_NODE_NOKIA_GX_G42.value,
]

#: State key under which the Optical Node block of the subscription is passed
#: between the shipped block steps. Consumers put the block they compose (under
#: any attribute name of their own model) in the state under this key.
OPTICAL_NODE_BLOCK_STATE_KEY = "optical_node_block"


def _optical_node_block_of_subscription(subscription: SubscriptionModel) -> AbstractOpticalNodeBlockInactive:
    """Return the Optical Node block under the ``optical_node`` attribute.

    This is the shipped-model fallback of the family: it reads the block from
    the ``optical_node`` attribute of the subscription, which the shipped
    subscription models always have.

    Args:
        subscription: The Optical Node subscription.

    Returns:
        The Optical Node block of the subscription.

    Raises:
        ValueError: If the subscription has no block under the attribute.
    """
    node = getattr(subscription, "optical_node", None)
    if node is None:
        msg = (
            "Optical Node subscription has no Optical Node block under attribute 'optical_node': "
            "the subscription model must have-a the Optical Node block, e.g. under 'optical_node'"
        )
        raise ValueError(msg)
    return node


def optical_node_subscription_description(
    subscription: SubscriptionModel,
    optical_node_block: AbstractOpticalNodeBlockInactive | None = None,
) -> str:
    """Generate human-readable subscription description for an Optical Node.

    Args:
        subscription: The Optical Node subscription.
        optical_node_block: The Optical Node block of the subscription. When
            given, it is used instead of the ``optical_node`` attribute of the
            shipped subscription models, so the helper also works for consumer
            models that compose the block under a different attribute name.

    Returns:
        The subscription description, e.g. ``"node.example.com (Nokia FlexILS)"``
        or the product name when the node has no ``pqdn`` yet.

    Raises:
        ValueError: If the subscription has no Optical Node block under the
            ``optical_node`` attribute and no block was passed.
    """
    node = optical_node_block or _optical_node_block_of_subscription(subscription)
    pqdn = getattr(node, "pqdn", None)
    if pqdn:
        return f"{pqdn} ({subscription.product.name})"
    return subscription.product.name


def validate_pqdn_uniqueness(pqdn: str, exclude_subscription_id: UUIDstr | None = None) -> None:
    """Ensure PQDN is not already used across any active/provisioning Optical Node subscriptions.

    Args:
        pqdn: The PQDN to check for uniqueness.
        exclude_subscription_id: Subscription ID to exclude from the check, when modifying.
    """
    for product_type_name in OPTICAL_NODE_PRODUCT_TYPES:
        existing_subs = subscriptions_by_product_type_and_instance_value(
            product_type=product_type_name,
            resource_type="pqdn",
            value=pqdn,
            status=[
                SubscriptionLifecycle.INITIAL,
                SubscriptionLifecycle.PROVISIONING,
                SubscriptionLifecycle.ACTIVE,
            ],
        )
        conflicting = [sub for sub in existing_subs if str(sub.subscription_id) != exclude_subscription_id]
        if conflicting:
            msg = f"PQDN '{pqdn}' is already in use by subscription {conflicting[0].subscription_id}"
            raise ValueError(msg)


def validate_management_ips_uniqueness(ips: list[IPAddress], exclude_subscription_id: UUIDstr | None = None) -> None:
    """Ensure none of the management/loopback IPs is already in use by an Optical Node subscription.

    Args:
        ips: The management/loopback IPs to check for uniqueness.
        exclude_subscription_id: Subscription ID to exclude from the check, when modifying.
    """
    for ip in ips:
        ip_value = str(ip)
        for product_type_name in OPTICAL_NODE_PRODUCT_TYPES:
            for resource_type in ("optical_management_ip", "optical_loopback_ip"):
                existing_subs = subscriptions_by_product_type_and_instance_value(
                    product_type=product_type_name,
                    resource_type=resource_type,
                    value=ip_value,
                    status=[
                        SubscriptionLifecycle.INITIAL,
                        SubscriptionLifecycle.PROVISIONING,
                        SubscriptionLifecycle.ACTIVE,
                    ],
                )
                conflicting = [sub for sub in existing_subs if str(sub.subscription_id) != exclude_subscription_id]
                if conflicting:
                    msg = (
                        f"Management IP '{ip_value}' is already in use by subscription {conflicting[0].subscription_id}"
                    )
                    raise ValueError(msg)


def validate_gmpls_id_uniqueness(gmpls_id: IPAddress, exclude_subscription_id: UUIDstr | None = None) -> None:
    """Ensure the FlexILS GMPLS ID is not already in use by a Nokia FlexILS subscription.

    Args:
        gmpls_id: The GMPLS ID to check for uniqueness.
        exclude_subscription_id: Subscription ID to exclude from the check, when modifying.
    """
    existing_subs = subscriptions_by_product_type_and_instance_value(
        product_type=ProductType.OPTICAL_NODE_NOKIA_FLEXILS.value,
        resource_type="optical_flexils_gmpls_id",
        value=gmpls_id,
        status=[
            SubscriptionLifecycle.INITIAL,
            SubscriptionLifecycle.PROVISIONING,
            SubscriptionLifecycle.ACTIVE,
        ],
    )
    conflicting = [sub for sub in existing_subs if str(sub.subscription_id) != exclude_subscription_id]
    if conflicting:
        msg = f"GMPLS ID '{gmpls_id}' is already in use by subscription {conflicting[0].subscription_id}"
        raise ValueError(msg)


def populate_abstract_optical_node_fields(
    optical_node_block: Any,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_node_software_version: str | None = None,
) -> None:
    """Populate the abstract fields on an optical node product block.

    The block is intentionally untyped: the abstract Optical Node block does
    not declare the fields populated here (they are vendor-specific), and the
    helper is shared by all vendors and their consumers.
    """
    optical_node_block.location = location_block_from_subscription(location_id)
    optical_node_block.optical_node_role = optical_node_role
    optical_node_block.pqdn = pqdn
    optical_node_block.optical_management_ip = optical_management_ip
    optical_node_block.optical_loopback_ip = optical_loopback_ip
    optical_node_block.optical_node_software_version = optical_node_software_version
