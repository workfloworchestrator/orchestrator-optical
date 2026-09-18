"""Shared database query helpers for the optical module.

This module is the neutral home of the database queries that both the
Hardware Abstraction Layer (``hal/``) and the workflow layer
(``workflows/``) need: they resolve product blocks from the database and
never depend on subscription models or workflow code. Product blocks are the
shared contracts between the layers; subscription ids are input parameters
only, never model dependencies.
"""

from typing import cast

from pydantic_forms.types import UUIDstr

from orchestrator.core.db import (
    ProductBlockTable,
    ResourceTypeTable,
    SubscriptionInstanceRelationTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
)
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.domain.lifecycle import lookup_specialized_type
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlock
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockInactive
from orchestrator.optical.products.product_blocks.optical_node.optical_packet_node import (
    OpticalModulePacketNodeBlock,
    OpticalModulePacketNodeBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockUnion

__all__ = [
    "location_block_from_instance",
    "node_block_from_instance",
    "node_blocks_by_roles",
    "node_instance_id_of_subscription",
    "node_instances_by_block_names",
    "packet_node_block_from_instance",
    "packet_node_instance_id_of_subscription",
    "pipe_blocks_all",
    "pipe_instances_by_block_names",
    "subscription_instance_values_by_block_type_depending_on_instance_id",
    "subscription_instances_by_block_names",
    "subscription_instances_by_block_type",
    "subscription_instances_by_block_type_and_resource_value",
]


def subscription_instances_by_block_type(
    product_block_type: str,
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Retrieve the subscription instances that match a specific product block type.

    Args:
        product_block_type: The name of the product block type (e.g., "NokiaFlexIlsBlock").
        states: List of subscription lifecycle states the owner subscription must be in.

    Returns:
        List of SubscriptionInstanceTable entries (i.e. rows of the subscription_instances table)
            whose product block type matches and whose owner subscription is in one of the given states.
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name == product_block_type)
        .all()
    )


def subscription_instances_by_block_type_and_resource_value(
    product_block_type: str,
    resource_type: str,
    resource_value: str,
    states: list[SubscriptionLifecycle] = [SubscriptionLifecycle.ACTIVE],  # noqa: B006
) -> list[SubscriptionInstanceTable]:
    """From the database, retrieve the subscription instances that match specific product block type and resource value.

    Usage example:
        >>> sis = subscription_instances_by_block_type_and_resource_value(
        ...     "OpticalDevicePort",
        ...     "port_name",
        ...     "ge-0/0/0",
        ...     [SubscriptionLifecycle.ACTIVE]
        ... )
        >>> for si in sis:
        ...     print(si.subscription_instance_id).

    This function finds subscription instances that:
    1. are instances of the product block of the specified type
    2. the value of the specified resource attribute matches the specified value
    3. Belong to a subscription in one of the specified lifecycle states

    Args:
        product_block_type: The name of the product block type (e.g., "OpticalDevicePort")
        resource_type: The name of the resource attribute (e.g., "port_name")
        resource_value: The specific value to match (e.g., "ge-0/0/0")
        states: List of subscription lifecycle states to include in the search

    Returns:
        List of SubscriptionInstanceTable objects (i.e. entries of the subscription_instances table in the DB)
            matching all criteria
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionInstanceValueTable)
        .join(ResourceTypeTable)
        .join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name == product_block_type)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .filter(SubscriptionInstanceValueTable.value == resource_value)
        .all()
    )


def subscription_instance_values_by_block_type_depending_on_instance_id(
    product_block_type: str,
    resource_type: str,
    depending_on_instance_id: str,
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceValueTable]:
    """Retrieve subscription instance values of a block type depending on another instance.

    This function retrieves a list of all subscription instance values (i.e. product block attributes, e.g.
    port_name) of a specific product block type (e.g. OpticalDevicePort) that depend on the given instance id
    (e.g. OpticalDeviceBlock of flex.ba01 subscription instance id) and whose owner subscription
    (e.g. OpticalFiber flex.ba01---flex.mt00 might own an optical port of flex.ba01)
    is in the specified lifecycle states.

    For example:
    >>> an_optical_device_instance_id = an_optical_device_subscription.optical_device.subscription_instance_id
    >>> subscription_instances_values = subscription_instances_of_type_that_depends_on(
            "OpticalDevicePort",
            "port_name",
            an_optical_device_instance_id,
            [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING]
        )
    [SubscriptionInstanceValueTable(su...value=xe-0/0/0), SubscriptionInstanceValueTable(su...value=et-1/0/0)]
                                               ^^^^^^^^                                             ^^^^^^^^
    You now have a list of all rows from the subscription instance values table in the DB.
    Each row corresponds to a subscription instance that depends on "an_optical_device".
    Each of these instances also belongs to a subscription whose status is in one of the specified states.
    You can use these subscription instances in your workflow like this:
    >>> subscription_instance_id = subscription_instances_values[0].subscription_instance_id
    >>> optical_port_block = OpticalDevicePortBlock.from_db(subscription_instance_id)

    Args:
        product_block_type (str): The product block type in the DB (i.e. product name, e.g. OpticalDevicePort)
        resource_type (str): The resource type in the DB (i.e. product block attribute name, e.g. port_name, etc.)
        depending_on_instance_id (str): The subscription_instance_id of theproduct block that the returned product
            blocks depend on.
        states (List[SubscriptionLifecycle]): The lifecycle states you want returned (i.e. SubscriptionLifecycle.ACTIVE)

    Returns:
        List[SubscriptionInstanceValueTable]: A list of all the subscription instance values that match your criteria.
    """
    return (
        SubscriptionInstanceValueTable.query.join(
            SubscriptionInstanceTable,
            SubscriptionInstanceTable.subscription_instance_id
            == SubscriptionInstanceValueTable.subscription_instance_id,
        )
        .join(
            SubscriptionInstanceRelationTable,
            SubscriptionInstanceTable.subscription_instance_id == SubscriptionInstanceRelationTable.in_use_by_id,
        )
        .join(
            SubscriptionTable,
            SubscriptionInstanceTable.subscription_id == SubscriptionTable.subscription_id,
        )
        .join(
            ProductBlockTable,
            SubscriptionInstanceTable.product_block_id == ProductBlockTable.product_block_id,
        )
        .join(
            ResourceTypeTable,
            SubscriptionInstanceValueTable.resource_type_id == ResourceTypeTable.resource_type_id,
        )
        .filter(SubscriptionInstanceRelationTable.depends_on_id == depending_on_instance_id)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name == product_block_type)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .all()
    )


def subscription_instances_by_block_names(
    block_names: set[str],
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Return the subscription instances whose product block is one of the given names.

    Block-based listing: no product type or subscription model is involved, so the
    lookup also covers consumers composing the shipped blocks under their own product
    types. This is the generic form of :func:`node_instances_by_block_names` and
    :func:`pipe_instances_by_block_names`, backing the block-filtered selectors.

    Args:
        block_names: The product block names to match (e.g. the ``__names__`` of an
            abstract block).
        states: Lifecycle states the owner subscription must be in.

    Returns:
        The matching subscription instances.
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name.in_(block_names))
        .all()
    )


def _block_instance_of_subscription(
    subscription_id: UUIDstr,
    block_names: set[str],
    block_description: str,
) -> SubscriptionInstanceTable:
    """Return the subscription instance of a block type owned by the given subscription.

    Args:
        subscription_id: Subscription id owning the block instance.
        block_names: The product block names to match (e.g. the ``__names__`` of an abstract block).
        block_description: Human-readable block description used in error messages.

    Returns:
        The subscription instance whose product block is one of ``block_names``.

    Raises:
        ValueError: If the subscription has no matching block instance, or more than one.
    """
    instances = (
        SubscriptionInstanceTable.query.join(ProductBlockTable)
        .filter(ProductBlockTable.name.in_(block_names))
        .filter(SubscriptionInstanceTable.subscription_id == subscription_id)
        .all()
    )
    if not instances:
        msg = f"Subscription {subscription_id} has no {block_description}"
        raise ValueError(msg)
    if len(instances) > 1:
        msg = f"Subscription {subscription_id} has more than one {block_description}"
        raise ValueError(msg)
    return instances[0]


def node_instances_by_block_names(
    block_names: set[str],
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Return the subscription instances whose product block is one of the given names.

    Block-based listing: no product type or subscription model is involved, so the
    lookup also covers consumers composing the shipped blocks under their own product
    types. Callers load the blocks via :func:`node_block_from_instance`.

    Args:
        block_names: The product block names to match (e.g. the ``__names__`` of an
            abstract block).
        states: Lifecycle states the owner subscription must be in.

    Returns:
        The matching subscription instances.
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name.in_(block_names))
        .all()
    )


def pipe_instances_by_block_names(
    block_names: set[str],
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Return the pipe subscription instances whose product block is one of the given names.

    Block-based listing, mirroring :func:`node_instances_by_block_names` for the
    optical pipe family (span, patch, leased spectrum).

    Args:
        block_names: The product block names to match.
        states: Lifecycle states the owner subscription must be in.

    Returns:
        The matching subscription instances.
    """
    return (
        SubscriptionInstanceTable.query.join(SubscriptionTable)
        .join(ProductBlockTable)
        .filter(SubscriptionTable.status.in_(states))
        .filter(ProductBlockTable.name.in_(block_names))
        .all()
    )


def node_block_from_instance(instance_id: UUIDstr) -> AnyOpticalNodeBlockUnion:
    """Return the Optical Node product block of the given block instance id.

    Block-based resolution: the instance is looked up by its
    ``subscription_instance_id`` and loaded as the most-derived lifecycle class,
    without touching subscription ids or the subscription model registry.

    Args:
        instance_id: Subscription instance id of an Optical Node block.

    Returns:
        The Optical Node product block.

    Raises:
        ValueError: If the instance does not exist or is not an Optical Node block.
    """
    instance = (
        SubscriptionInstanceTable.query.join(ProductBlockTable)
        .filter(SubscriptionInstanceTable.subscription_instance_id == instance_id)
        .one_or_none()
    )
    if instance is None:
        msg = f"Subscription instance {instance_id} does not exist"
        raise ValueError(msg)
    if instance.product_block.name not in AbstractOpticalNodeBlockInactive.__names__:
        msg = f"Subscription instance {instance_id} is not an Optical Node block"
        raise ValueError(msg)
    block_class = ProductBlockModel.registry[instance.product_block.name]
    active_class = cast(
        type[AnyOpticalNodeBlockUnion],
        lookup_specialized_type(block_class, SubscriptionLifecycle.ACTIVE),
    )
    return active_class.from_db(subscription_instance_id=instance.subscription_instance_id)


def node_instance_id_of_subscription(subscription_id: UUIDstr) -> str:
    """Return the block instance id of the Optical Node block of a node subscription.

    The FQDN lives on the node's management block, whose instance id differs from the
    node block's: callers holding a node subscription id (or one of its sub-block
    instances) resolve the node block instance through this helper before calling
    :func:`node_block_from_instance`.

    Args:
        subscription_id: Subscription id of an Optical Node subscription.

    Returns:
        The subscription instance id of the Optical Node block.

    Raises:
        ValueError: If the subscription has no Optical Node block, or more than one.
    """
    instance = _block_instance_of_subscription(
        subscription_id,
        AbstractOpticalNodeBlockInactive.__names__,
        "Optical Node block",
    )
    return str(instance.subscription_instance_id)


def node_blocks_by_roles(
    roles: list,
    states: list[SubscriptionLifecycle] | None = None,
) -> list[AnyOpticalNodeBlockUnion]:
    """Return the Optical Node blocks whose role is one of the given roles.

    Block-based listing: instances are enumerated by block name (never by product
    type or subscription), loaded via :func:`node_block_from_instance` and filtered
    on ``optical_node_role`` in Python, so consumers composing the shipped blocks
    under their own product types are covered.

    Args:
        roles: The node roles to filter by.
        states: Lifecycle states the owner subscription must be in (ACTIVE by default).

    Returns:
        The matching Optical Node blocks.
    """
    wanted = {role.value if hasattr(role, "value") else str(role) for role in roles}
    instances = node_instances_by_block_names(
        AbstractOpticalNodeBlockInactive.__names__,
        states or [SubscriptionLifecycle.ACTIVE],
    )
    blocks: list[AnyOpticalNodeBlockUnion] = []
    for instance in instances:
        block = node_block_from_instance(str(instance.subscription_instance_id))
        role = getattr(block, "optical_node_role", None)
        if role is not None and (getattr(role, "value", str(role)) in wanted):
            blocks.append(block)
    return blocks


def pipe_blocks_all(
    states: list[SubscriptionLifecycle] | None = None,
) -> list:
    """Return the optical pipe blocks (span, patch, leased spectrum) in the given states.

    Block-based listing: instances are enumerated by the abstract pipe block names
    and loaded via the product block registry, without product types or subscription
    models.

    Args:
        states: Lifecycle states the owner subscription must be in (ACTIVE by default).

    Returns:
        The matching optical pipe blocks.
    """
    from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (  # noqa: PLC0415
        AbstractOpticalPipeBlockInactive,
    )

    instances = pipe_instances_by_block_names(
        set(AbstractOpticalPipeBlockInactive.__names__),
        states or [SubscriptionLifecycle.ACTIVE],
    )
    blocks = []
    for instance in instances:
        block_class = ProductBlockModel.registry[instance.product_block.name]
        active_class = cast(
            type[ProductBlockModel],
            lookup_specialized_type(block_class, SubscriptionLifecycle.ACTIVE),
        )
        blocks.append(active_class.from_db(subscription_instance_id=instance.subscription_instance_id))
    return blocks


def location_block_from_instance(instance_id: UUIDstr) -> OpticalModuleLocationBlock:
    """Return the Optical Module Location product block of the given block instance id.

    Block-based resolution: the instance is looked up by its
    ``subscription_instance_id`` and loaded as the most-derived lifecycle class,
    without touching subscription ids or the subscription model registry.

    Args:
        instance_id: Subscription instance id of an Optical Module Location block.

    Returns:
        The Optical Module Location product block.

    Raises:
        ValueError: If the instance does not exist or is not an Optical Module Location block.
    """
    instance = (
        SubscriptionInstanceTable.query.join(ProductBlockTable)
        .filter(SubscriptionInstanceTable.subscription_instance_id == instance_id)
        .one_or_none()
    )
    if instance is None:
        msg = f"Subscription instance {instance_id} does not exist"
        raise ValueError(msg)
    if instance.product_block.name not in OpticalModuleLocationBlock.__names__:
        msg = f"Subscription instance {instance_id} is not an Optical Module Location block"
        raise ValueError(msg)
    # The ACTIVE class is the most-derived subclass, so it can load INITIAL,
    # PROVISIONING and ACTIVE blocks (unlike the PROVISIONING class).
    return OpticalModuleLocationBlock.from_db(subscription_instance_id=instance.subscription_instance_id)


def packet_node_block_from_instance(instance_id: UUIDstr) -> OpticalModulePacketNodeBlock:
    """Return the Optical Module Packet Node product block of the given block instance id.

    Block-based resolution: the instance is looked up by its
    ``subscription_instance_id`` and loaded as the most-derived lifecycle class,
    without touching subscription ids or the subscription model registry.

    Args:
        instance_id: Subscription instance id of an Optical Module Packet Node block.

    Returns:
        The Optical Module Packet Node product block.

    Raises:
        ValueError: If the instance does not exist or is not an Optical Module Packet Node block.
    """
    instance = (
        SubscriptionInstanceTable.query.join(ProductBlockTable)
        .filter(SubscriptionInstanceTable.subscription_instance_id == instance_id)
        .one_or_none()
    )
    if instance is None:
        msg = f"Subscription instance {instance_id} does not exist"
        raise ValueError(msg)
    if instance.product_block.name not in OpticalModulePacketNodeBlock.__names__:
        msg = f"Subscription instance {instance_id} is not an Optical Module Packet Node block"
        raise ValueError(msg)
    # The ACTIVE class is the most-derived subclass, so it can load INITIAL,
    # PROVISIONING and ACTIVE blocks (unlike the PROVISIONING class).
    return OpticalModulePacketNodeBlock.from_db(subscription_instance_id=instance.subscription_instance_id)


def packet_node_instance_id_of_subscription(subscription_id: UUIDstr) -> str:
    """Return the block instance id of the Optical Module Packet Node block of a packet node subscription.

    Callers holding a packet node subscription id resolve the packet node block
    instance through this helper before calling :func:`packet_node_block_from_instance`.

    Args:
        subscription_id: Subscription id of an Optical Module Packet Node subscription.

    Returns:
        The subscription instance id of the Optical Module Packet Node block.

    Raises:
        ValueError: If the subscription has no Optical Module Packet Node block, or more than one.
    """
    instance = _block_instance_of_subscription(
        subscription_id,
        OpticalModulePacketNodeBlockInactive.__names__,
        "Optical Module Packet Node block",
    )
    return str(instance.subscription_instance_id)
