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
    ProductTable,
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
from orchestrator.optical.products.product_blocks.optical_packet_node import (
    OpticalModulePacketNode,
    OpticalModulePacketNodeInactive,
)

__all__ = [
    "location_block_from_subscription",
    "node_block_from_subscription",
    "packet_node_block_from_subscription",
    "subscription_instance_values_by_block_type_depending_on_instance_id",
    "subscription_instances_by_block_type",
    "subscription_instances_by_block_type_and_resource_value",
    "subscriptions_by_product_type",
    "subscriptions_by_product_type_and_instance_value",
]


def subscriptions_by_product_type(product_type: str, status: list[SubscriptionLifecycle]) -> list[SubscriptionTable]:
    """Retrieve_subscription_list_by_product.

    This function lets you retrieve a list of all subscriptions of a
    given product type. For example, you could call this like so:

    >>> subscriptions_by_product_type("Node", [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING])
        [SubscriptionTable(su...note=None), SubscriptionTable(su...note=None)]

    You now have a list of all active Node subscription instances and can then
    use them in your workflow.

    Args:
        product_type (str): The product type in the DB (i.e. Node, User, etc.)
        status (List[SubscriptionLifecycle]): The lifecycle states you want returned (i.e. SubscriptionLifecycle.ACTIVE)

    Returns:
        List[SubscriptionTable]: A list of all the subscriptions that match
            your criteria.
    """
    return (
        SubscriptionTable.query.join(ProductTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )


def subscriptions_by_product_type_and_instance_value(
    product_type: str,
    resource_type: str,
    value: str,
    status: list[SubscriptionLifecycle],
) -> list[SubscriptionTable]:
    """Retrieve a list of Subscriptions by product_type, resource_type and value.

    Args:
        product_type: type of subscriptions
        resource_type: name of the resource type
        value: value of the resource type
        status: lifecycle status of the subscriptions

    Returns:
        list[SubscriptionTable]: List of matching subscriptions.
    """
    return (
        SubscriptionTable.query.join(ProductTable)
        .join(SubscriptionInstanceTable)
        .join(SubscriptionInstanceValueTable)
        .join(ResourceTypeTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionInstanceValueTable.value == value)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )


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


def location_block_from_subscription(location_id: UUIDstr) -> OpticalModuleLocationBlock:
    """Return the Optical Module Location product block of the given location subscription.

    The resolution is block-based: the subscription instance whose product
    block is an ``OpticalModuleLocationBlock`` is looked up by the subscription
    id and loaded as the most-derived class. Because every consumer that
    composes the shipped block persists it under the shipped block name, the
    lookup also covers composed product types without hardcoding a product
    type or depending on the subscription model registry. The subscription id
    is only an input parameter, not a model dependency.

    Args:
        location_id: Subscription id of an active Optical Location subscription.

    Returns:
        The Optical Module Location product block of the subscription.

    Raises:
        ValueError: If the subscription has no Optical Module Location block.
    """
    instance = _block_instance_of_subscription(
        location_id,
        OpticalModuleLocationBlock.__names__,
        "Optical Module Location block",
    )
    # The ACTIVE class is the most-derived subclass, so it can load INITIAL,
    # PROVISIONING and ACTIVE blocks (unlike the PROVISIONING class).
    return OpticalModuleLocationBlock.from_db(subscription_instance_id=instance.subscription_instance_id)


def node_block_from_subscription(node_subscription_id: UUIDstr) -> AbstractOpticalNodeBlockInactive:
    """Return the Optical Node product block of the given node subscription.

    The resolution is block-based: the subscription instance whose product
    block is one of the concrete Optical Node block names (the ``__names__`` of
    the abstract node block) is looked up by the subscription id, resolved to
    its concrete block class through the product block registry and loaded as
    the most-derived lifecycle class. This covers all the shipped vendor
    blocks without hardcoding a vendor, a product type or the subscription
    model registry. The subscription id is only an input parameter, not a
    model dependency.

    Args:
        node_subscription_id: Subscription id of an active Optical Node subscription.

    Returns:
        The Optical Node product block of the subscription.

    Raises:
        ValueError: If the subscription has no Optical Node block.
    """
    instance = _block_instance_of_subscription(
        node_subscription_id,
        AbstractOpticalNodeBlockInactive.__names__,
        "Optical Node block",
    )
    block_class = ProductBlockModel.registry[instance.product_block.name]
    # The ACTIVE variant is the most-derived subclass, so it can load INITIAL,
    # PROVISIONING and ACTIVE blocks (unlike the PROVISIONING class).
    active_class = cast(
        type[AbstractOpticalNodeBlockInactive],
        lookup_specialized_type(block_class, SubscriptionLifecycle.ACTIVE),
    )
    return active_class.from_db(subscription_instance_id=instance.subscription_instance_id)


def packet_node_block_from_subscription(subscription_id: UUIDstr) -> OpticalModulePacketNodeInactive:
    """Return the Optical Module Packet Node product block of the given subscription.

    The resolution is block-based: the subscription instance whose product
    block is an ``OpticalModulePacketNode`` is looked up by the subscription id
    and loaded as the most-derived class. Because every consumer that composes
    the shipped block persists it under the shipped block name, the lookup
    also covers composed product types without hardcoding a product type or
    depending on the subscription model registry. The subscription id is only
    an input parameter, not a model dependency.

    Args:
        subscription_id: Subscription id of an active Optical Packet Node subscription.

    Returns:
        The Optical Module Packet Node product block of the subscription.

    Raises:
        ValueError: If the subscription has no Optical Module Packet Node block.
    """
    instance = _block_instance_of_subscription(
        subscription_id,
        OpticalModulePacketNodeInactive.__names__,
        "Optical Module Packet Node block",
    )
    # The ACTIVE class is the most-derived subclass, so it can load INITIAL,
    # PROVISIONING and ACTIVE blocks (unlike the PROVISIONING class).
    return OpticalModulePacketNode.from_db(subscription_instance_id=instance.subscription_instance_id)
