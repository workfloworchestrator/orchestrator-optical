"""Shared creation utilities and steps for Optical Nodes."""

from typing import Any, cast

from pydantic_forms.types import UUIDstr

from orchestrator.core.db import SubscriptionInstanceTable, db
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.domain.lifecycle import lookup_specialized_type
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import location_block_from_subscription, subscriptions_by_product_type_and_instance_value
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.utils.custom_types.dns import Fqdn
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

    The description is derived from the node FQDN of the composed management
    block, so the same function can be reused by consumers that compose the
    shipped block under their own attribute: pass the shipped block explicitly,
    otherwise it falls back to the ``optical_node`` attribute of the shipped
    subscription models.

    Args:
        subscription: The Optical Node subscription.
        optical_node_block: The Optical Node block of the subscription. When
            given, it is used instead of the ``optical_node`` attribute of the
            shipped subscription models, so the helper also works for consumer
            models that compose the block under a different attribute name.

    Returns:
        The subscription description, e.g. ``"node.example.com (Nokia FlexILS)"``
        or the product name when the node has no FQDN yet.

    Raises:
        ValueError: If the subscription has no Optical Node block under the
            ``optical_node`` attribute and no block was passed.
    """
    node = optical_node_block or _optical_node_block_of_subscription(subscription)
    fqdn = node.management.optical_module_node_fqdn
    if fqdn:
        return f"{fqdn} ({subscription.product.name})"
    return subscription.product.name


def validate_optical_node_fqdn_uniqueness(fqdn: str, exclude_subscription_id: UUIDstr | None = None) -> None:
    """Ensure the FQDN is not already used across any active/provisioning Optical Node subscriptions.

    Args:
        fqdn: The FQDN to check for uniqueness.
        exclude_subscription_id: Subscription ID to exclude from the check, when modifying.
    """
    for product_type_name in OPTICAL_NODE_PRODUCT_TYPES:
        existing_subs = subscriptions_by_product_type_and_instance_value(
            product_type=product_type_name,
            resource_type="optical_module_node_fqdn",
            value=fqdn,
            status=[
                SubscriptionLifecycle.INITIAL,
                SubscriptionLifecycle.PROVISIONING,
                SubscriptionLifecycle.ACTIVE,
            ],
        )
        conflicting = [sub for sub in existing_subs if str(sub.subscription_id) != exclude_subscription_id]
        if conflicting:
            msg = f"FQDN '{fqdn}' is already in use by subscription {conflicting[0].subscription_id}"
            raise ValueError(msg)


def validate_management_ips_uniqueness(ips: list[IPAddress], exclude_subscription_id: UUIDstr | None = None) -> None:
    """Ensure none of the DCN interface/loopback IPs is already in use by an Optical Node subscription.

    Args:
        ips: The DCN interface/loopback IPs to check for uniqueness.
        exclude_subscription_id: Subscription ID to exclude from the check, when modifying.
    """
    for ip in ips:
        ip_value = str(ip)
        for product_type_name in OPTICAL_NODE_PRODUCT_TYPES:
            for resource_type in ("optical_module_node_dcn_loopback_ip", "optical_module_node_dcn_interface_ip"):
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
    *,
    location_id: UUIDstr,
    optical_node_role: OpticalNodeRole,
    optical_module_node_fqdn: Fqdn,
    optical_module_node_dcn_loopback_ip: IPAddress | None = None,
    optical_module_node_dcn_interface_ip: IPAddress | None = None,
    optical_module_node_software_version: str | None = None,
    optical_module_node_vendor: Vendor | None = None,
    optical_module_node_platform: Platform | None = None,
) -> None:
    """Populate the abstract fields on an optical node product block.

    The block is intentionally untyped: the abstract Optical Node block does
    not declare the fields populated here (they are vendor-specific), and the
    helper is shared by all vendors and their consumers.

    Args:
        optical_node_block: The Optical Node block to populate (any lifecycle variant).
        location_id: Subscription id of the Optical Location hosting the node.
        optical_node_role: Role of the node.
        optical_module_node_fqdn: Fully qualified domain name of the node.
        optical_module_node_dcn_loopback_ip: Loopback IP of the node's DCN interface.
        optical_module_node_dcn_interface_ip: Interface IP of the node's DCN interface.
        optical_module_node_software_version: Software version of the node.
        optical_module_node_vendor: Vendor of the node.
        optical_module_node_platform: Platform of the node.
    """
    optical_node_block.location = location_block_from_subscription(location_id)
    optical_node_block.optical_node_role = optical_node_role
    optical_node_block.management.optical_module_node_fqdn = optical_module_node_fqdn
    optical_node_block.management.optical_module_node_dcn_loopback_ip = optical_module_node_dcn_loopback_ip
    optical_node_block.management.optical_module_node_dcn_interface_ip = optical_module_node_dcn_interface_ip
    optical_node_block.management.optical_module_node_software_version = optical_module_node_software_version
    optical_node_block.management.optical_module_node_vendor = optical_module_node_vendor
    optical_node_block.management.optical_module_node_platform = optical_module_node_platform


def optical_node_block_from_state(
    optical_node_block: AbstractOpticalNodeBlockInactive | dict[str, Any] | None,
) -> AbstractOpticalNodeBlockInactive | None:
    """Return the Optical Node block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_NODE_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the full block data) rather than as a domain
    model. This helper returns the value unchanged when it is already a domain
    model (in-process usage, e.g. in tests) and reconstructs the block from the
    serialized data otherwise. The lifecycle variant of the block is resolved
    from the status of its owner subscription, so blocks of any lifecycle are
    loaded as their matching variant (INITIAL, PROVISIONING or ACTIVE).

    Args:
        optical_node_block: The block value from the workflow state, or None.

    Returns:
        The Optical Node block as a domain model, or None when the value is None.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``.
    """
    if optical_node_block is None:
        return None
    if isinstance(optical_node_block, AbstractOpticalNodeBlockInactive):
        return optical_node_block
    return _optical_node_block_from_state(optical_node_block)


def _optical_node_block_from_state(
    optical_node_block: dict[str, Any],
) -> AbstractOpticalNodeBlockInactive:
    """Reconstruct an Optical Node block from its serialized form.

    The state dict carries the full block data (the block is serialized with
    ``model_dump``), so the block is reconstructed from it rather than reloaded
    from the database: reloading would discard the mutations made by the
    preceding step, which workflow steps only persist when they explicitly save.
    The concrete block class is resolved through the product block registry and
    its lifecycle variant from the status of its owner subscription: the ACTIVE
    class cannot construct an INITIAL block (whose required fields are unset)
    and the base class rejects non-INITIAL blocks, so the specialized variant
    must be resolved explicitly, mirroring the block-based resolution in
    ``orchestrator.optical.db``.

    Args:
        optical_node_block: The serialized block from the workflow state.

    Returns:
        The Optical Node block as a domain model.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``,
            or if no subscription instance exists with the given id.
    """
    subscription_instance_id = optical_node_block.get("subscription_instance_id")
    if subscription_instance_id is None:
        msg = "Optical Node block in the state has no subscription_instance_id"
        raise ValueError(msg)
    instance = db.session.get(SubscriptionInstanceTable, subscription_instance_id)
    if instance is None:
        msg = f"No subscription instance with id {subscription_instance_id}"
        raise ValueError(msg)
    block_class = cast(
        type[AbstractOpticalNodeBlockInactive],
        lookup_specialized_type(
            ProductBlockModel.registry[instance.product_block.name],
            SubscriptionLifecycle(instance.subscription.status),
        ),
    )
    return block_class.model_validate(optical_node_block)
