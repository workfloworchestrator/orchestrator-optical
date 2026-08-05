"""Shared creation utilities and steps for Optical Nodes."""

from pydantic_forms.types import UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_location.shared import location_block_from_subscription
from orchestrator.optical.workflows.shared import subscriptions_by_product_type_and_instance_value

OPTICAL_NODE_PRODUCT_TYPES = [
    ProductType.OPTICAL_NODE_NOKIA_FLEXILS.value,
    ProductType.OPTICAL_NODE_NOKIA_GROOVE_G30.value,
    ProductType.OPTICAL_NODE_NOKIA_GX_G42.value,
]


def optical_node_subscription_description(subscription: SubscriptionModel) -> str:
    """Generate human-readable subscription description for an Optical Node."""
    node = getattr(subscription, "optical_node", None)
    if node and getattr(node, "pqdn", None):
        return f"{node.pqdn} ({subscription.product.name})"
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
    optical_node_block,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_node_software_version: str | None = None,
) -> None:
    """Populate the abstract fields on an optical node product block."""
    optical_node_block.location = location_block_from_subscription(location_id)
    optical_node_block.optical_node_role = optical_node_role
    optical_node_block.pqdn = pqdn
    optical_node_block.optical_management_ip = optical_management_ip
    optical_node_block.optical_loopback_ip = optical_loopback_ip
    optical_node_block.optical_node_software_version = optical_node_software_version
