"""Shared database query helpers for the optical module.

This module is the neutral home of the database queries that both the
Hardware Abstraction Layer (``hal/``) and the workflow layer
(``workflows/``) need: they resolve product blocks from the database and
never depend on subscription models or workflow code. Product blocks are the
shared contracts between the layers; subscription ids are input parameters
only, never model dependencies.
"""

from collections.abc import Mapping, Sequence
from typing import Any, cast
from uuid import UUID

from pydantic_forms.types import UUIDstr
from sqlalchemy import ForeignKey, Select, String, Text, delete, func, select, text
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import aliased, mapped_column
from sqlalchemy_utils import UUIDType

from orchestrator.core.db import (
    ProductBlockTable,
    ResourceTypeTable,
    SubscriptionInstanceRelationTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
    UtcTimestamp,
    db,
)
from orchestrator.core.db.database import BaseModel
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
from orchestrator.optical.utils.custom_types.frequencies import parse_if_string

__all__ = [
    "OpticalAppliedConfigTable",
    "applied_config",
    "applied_config_of_other_owners",
    "forget_applied_config",
    "golden_config_of_other_owners",
    "leased_passbands_of_ports",
    "location_block_from_instance",
    "lock_node_config",
    "node_applied_config",
    "node_block_from_instance",
    "node_instance_id_of_subscription",
    "packet_node_block_from_instance",
    "packet_node_instance_id_of_subscription",
    "pipe_blocks_all",
    "pipe_blocks_by_types",
    "pipe_instances_by_block_names",
    "replace_applied_config",
    "subscription_instance_values_by_block_type_depending_on_instance_id",
    "subscription_instance_values_by_instance_ids_and_resource_type",
    "subscription_instances_by_block_names",
    "subscription_instances_by_block_type",
    "subscription_instances_by_block_type_and_resource_value",
    "subscription_instances_by_block_types_and_resource_values",
]


def _all[T](statement: Select[T]) -> list[T]:
    """Execute a SQLAlchemy 2.x ``select()`` on the core session and return every row entity."""
    return list(db.session.scalars(statement).all())


def _one_or_none[T](statement: Select[T]) -> T | None:
    """Execute a SQLAlchemy 2.x ``select()`` on the core session and return at most one row entity."""
    return db.session.scalars(statement).one_or_none()


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
    return _all(
        select(SubscriptionInstanceTable)
        .join(SubscriptionTable)
        .join(ProductBlockTable)
        .where(SubscriptionTable.status.in_(states))
        .where(ProductBlockTable.name == product_block_type)
    )


def subscription_instances_by_block_types_and_resource_values(
    block_names: set[str],
    resource_values: dict[str, str | list[str] | set[str]],
    states: list[SubscriptionLifecycle] = [SubscriptionLifecycle.ACTIVE],  # noqa: B006
) -> list[SubscriptionInstanceTable]:
    """From the database, retrieve the subscription instances matching block names and resource values.

    This is the general form of :func:`subscription_instances_by_block_type_and_resource_value`:
    several block names can be matched at once (e.g. the ``__names__`` of an abstract block)
    and several ``(resource type, values)`` conditions can be combined. Conditions on
    different resource types are AND-ed (each gets its own join on the instance values,
    all tied to the same subscription instance); values of the same resource type are
    OR-ed (``IN``). Everything is filtered in a single SQL query: callers offering a
    subset of blocks (e.g. a selector filtered by type) never pay the load cost of
    every block in the database.

    Usage example:
        >>> sis = subscription_instances_by_block_types_and_resource_values(
        ...     {"OpticalFiberSpanBlock", "OpticalFiberPatchBlock"},
        ...     {"optical_pipe_type": ["Span"]},
        ...     [SubscriptionLifecycle.ACTIVE]
        ... )
        >>> for si in sis:
        ...     print(si.subscription_instance_id).

    This function finds subscription instances that:
    1. are instances of a product block of one of the specified names
    2. for every specified resource type, hold a value matching one of the specified values
    3. Belong to a subscription in one of the specified lifecycle states

    Args:
        block_names: The product block names to match (e.g. the ``__names__`` of an
            abstract block).
        resource_values: Mapping of resource type (e.g. ``"optical_pipe_type"``) to the
            acceptable value or values. A key mapped to no values matches nothing.
        states: List of subscription lifecycle states to include in the search

    Returns:
        List of SubscriptionInstanceTable objects (i.e. entries of the subscription_instances table in the DB)
            matching all criteria
    """
    query = (
        select(SubscriptionInstanceTable)
        .join(SubscriptionTable)
        .join(ProductBlockTable)
        .where(SubscriptionTable.status.in_(states))
        .where(ProductBlockTable.name.in_(block_names))
    )
    for resource_type, values in resource_values.items():
        wanted = [values] if isinstance(values, str) else list(values)
        if not wanted:
            return []
        values_table = aliased(SubscriptionInstanceValueTable)
        resource_table = aliased(ResourceTypeTable)
        query = (
            query.join(
                values_table,
                values_table.subscription_instance_id == SubscriptionInstanceTable.subscription_instance_id,
            )
            .join(resource_table, values_table.resource_type_id == resource_table.resource_type_id)
            .where(resource_table.resource_type == resource_type)
            .where(values_table.value.in_(wanted))
        )
    return _all(query)


def subscription_instances_by_block_type_and_resource_value(
    product_block_type: str,
    resource_type: str,
    resource_value: str,
    states: list[SubscriptionLifecycle] = [SubscriptionLifecycle.ACTIVE],  # noqa: B006
) -> list[SubscriptionInstanceTable]:
    """From the database, retrieve the subscription instances that match specific product block type and resource value.

    Single-name, single-value subcase of
    :func:`subscription_instances_by_block_types_and_resource_values`, kept for its callers.

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
    return subscription_instances_by_block_types_and_resource_values(
        {product_block_type}, {resource_type: resource_value}, states
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
    return _all(
        select(SubscriptionInstanceValueTable)
        .join(
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
        .where(SubscriptionInstanceRelationTable.depends_on_id == depending_on_instance_id)
        .where(SubscriptionTable.status.in_(states))
        .where(ProductBlockTable.name == product_block_type)
        .where(ResourceTypeTable.resource_type == resource_type)
    )


def subscription_instance_values_by_instance_ids_and_resource_type(
    instance_ids: list[str],
    resource_type: str,
) -> list[SubscriptionInstanceValueTable]:
    """Return the stored values of one resource type for the given block instances.

    Single query over the instance values table: selectors that only need a label
    (e.g. the pipe name) read it here instead of loading every block. Instances
    without a stored value simply have no row; callers fall back to a placeholder.

    Args:
        instance_ids: Subscription instance ids to read the values of.
        resource_type: The resource type in the DB (i.e. product block attribute name).

    Returns:
        The matching SubscriptionInstanceValueTable rows (at most one per instance
        for scalar block fields).
    """
    if not instance_ids:
        return []
    return _all(
        select(SubscriptionInstanceValueTable)
        .join(
            ResourceTypeTable,
            SubscriptionInstanceValueTable.resource_type_id == ResourceTypeTable.resource_type_id,
        )
        .where(SubscriptionInstanceValueTable.subscription_instance_id.in_(instance_ids))
        .where(ResourceTypeTable.resource_type == resource_type)
    )


def leased_passbands_of_ports(port_instance_ids: Sequence[str]) -> dict[str, list[tuple[int, int]]]:
    """Return the leased passbands of the Leased Spectrum blocks terminated on the given ports.

    Single query: the blocks using any of the ports are joined with their stored
    ``optical_leased_passbands`` values, so no block is loaded. A Leased Spectrum block
    without stored passbands (an unrestricted lease) has no row and is not returned.

    Args:
        port_instance_ids: Subscription instance ids of Optical Port blocks (any role).

    Returns:
        ``{leased spectrum block instance id: [(start, end), ...]}`` in MHz, sorted.
    """
    if not port_instance_ids:
        return {}
    rows = db.session.execute(
        select(SubscriptionInstanceRelationTable.in_use_by_id, SubscriptionInstanceValueTable.value)
        .join(
            SubscriptionInstanceValueTable,
            SubscriptionInstanceValueTable.subscription_instance_id == SubscriptionInstanceRelationTable.in_use_by_id,
        )
        .join(
            ResourceTypeTable,
            SubscriptionInstanceValueTable.resource_type_id == ResourceTypeTable.resource_type_id,
        )
        .where(SubscriptionInstanceRelationTable.depends_on_id.in_(port_instance_ids))
        .where(ResourceTypeTable.resource_type == "optical_leased_passbands")
        .distinct()
    ).all()
    leased: dict[str, set[tuple[int, int]]] = {}
    for pipe_instance_id, value in rows:
        start, end = parse_if_string(value)
        leased.setdefault(str(pipe_instance_id), set()).add((int(start), int(end)))
    return {pipe_instance_id: sorted(passbands) for pipe_instance_id, passbands in leased.items()}


def subscription_instances_by_block_names(
    block_names: set[str],
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Return the subscription instances whose product block is one of the given names.

    Block-based listing: no product type or subscription model is involved, so the
    lookup also covers consumers composing the shipped blocks under their own product
    types. This is the generic form of :func:`pipe_instances_by_block_names`,
    backing the block-filtered selectors.

    Args:
        block_names: The product block names to match (e.g. the ``__names__`` of an
            abstract block).
        states: Lifecycle states the owner subscription must be in.

    Returns:
        The matching subscription instances.
    """
    return _all(
        select(SubscriptionInstanceTable)
        .join(SubscriptionTable)
        .join(ProductBlockTable)
        .where(SubscriptionTable.status.in_(states))
        .where(ProductBlockTable.name.in_(block_names))
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
    instances = _all(
        select(SubscriptionInstanceTable)
        .join(ProductBlockTable)
        .where(ProductBlockTable.name.in_(block_names))
        .where(SubscriptionInstanceTable.subscription_id == subscription_id)
    )
    if not instances:
        msg = f"Subscription {subscription_id} has no {block_description}"
        raise ValueError(msg)
    if len(instances) > 1:
        msg = f"Subscription {subscription_id} has more than one {block_description}"
        raise ValueError(msg)
    return instances[0]


def pipe_instances_by_block_names(
    block_names: set[str],
    states: list[SubscriptionLifecycle],
) -> list[SubscriptionInstanceTable]:
    """Return the pipe subscription instances whose product block is one of the given names.

    Block-based listing for the optical pipe family (span, patch, leased spectrum).

    Args:
        block_names: The product block names to match.
        states: Lifecycle states the owner subscription must be in.

    Returns:
        The matching subscription instances.
    """
    return _all(
        select(SubscriptionInstanceTable)
        .join(SubscriptionTable)
        .join(ProductBlockTable)
        .where(SubscriptionTable.status.in_(states))
        .where(ProductBlockTable.name.in_(block_names))
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
    instance = _one_or_none(
        select(SubscriptionInstanceTable)
        .join(ProductBlockTable)
        .where(SubscriptionInstanceTable.subscription_instance_id == instance_id)
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

    The node name lives on the node's management block, whose instance id differs from the
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


def _load_pipe_blocks(instances: list[SubscriptionInstanceTable]) -> list:
    """Load optical pipe blocks for the given instances as the most-derived lifecycle class."""
    blocks = []
    for instance in instances:
        block_class = ProductBlockModel.registry[instance.product_block.name]
        active_class = cast(
            type[ProductBlockModel],
            lookup_specialized_type(block_class, SubscriptionLifecycle.ACTIVE),
        )
        blocks.append(active_class.from_db(subscription_instance_id=instance.subscription_instance_id))
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
    return _load_pipe_blocks(instances)


def pipe_blocks_by_types(
    pipe_types: list[str],
    states: list[SubscriptionLifecycle] | None = None,
) -> list:
    """Return the optical pipe blocks of the given pipe types in the given states.

    Block-based listing with the type filter pushed into the instance query: only
    matching instances are loaded, so callers offering a subset of pipe types never
    pay the load cost of every pipe in the database.

    Args:
        pipe_types: Stored ``optical_pipe_type`` resource values to match (i.e.
            ``OpticalPipeType.<member>.value``, e.g. ``"Span"``).
        states: Lifecycle states the owner subscription must be in (ACTIVE by default).

    Returns:
        The matching optical pipe blocks.
    """
    from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (  # noqa: PLC0415
        AbstractOpticalPipeBlockInactive,
    )

    instances = subscription_instances_by_block_types_and_resource_values(
        set(AbstractOpticalPipeBlockInactive.__names__),
        {"optical_pipe_type": pipe_types},
        states or [SubscriptionLifecycle.ACTIVE],
    )
    return _load_pipe_blocks(instances)


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
    instance = _one_or_none(
        select(SubscriptionInstanceTable)
        .join(ProductBlockTable)
        .where(SubscriptionInstanceTable.subscription_instance_id == instance_id)
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
    instance = _one_or_none(
        select(SubscriptionInstanceTable)
        .join(ProductBlockTable)
        .where(SubscriptionInstanceTable.subscription_instance_id == instance_id)
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


class OpticalAppliedConfigTable(BaseModel):
    """The device configuration applied by this module: one row per (node, path, owner).

    A row records that the product block ``owner_instance_id`` applied ``value`` at the
    device path ``path`` of the Optical Node ``node_instance_id``. Rows mean *applied*,
    not *desired*: they are written only after the device accepted the configuration
    (see :mod:`orchestrator.optical.hal.reconcile`), the desired configuration is always
    rendered again from the blocks. The rows of a node are its golden configuration,
    i.e. the part of its configuration managed by the orchestrator.

    Several owners may hold the same path with the same value (a shared object stays on
    the device until its last owner releases it). ``scope`` names the rendering unit of
    the owner that wrote the row (e.g. ``line``, ``client:<port>``), so that a unit is
    replaced or released without touching the other units of the same owner. The owner
    is deliberately not a foreign key: a block removed from its subscription must not
    silently take along the record of what it left on the device.
    """

    __tablename__ = "optical_applied_config"

    node_instance_id = mapped_column(
        UUIDType,
        ForeignKey("subscription_instances.subscription_instance_id", ondelete="CASCADE"),
        primary_key=True,
    )
    path = mapped_column(Text(), primary_key=True)
    owner_instance_id = mapped_column(UUIDType, primary_key=True, index=True)
    scope = mapped_column(String(255), nullable=False)
    #: ``{"value": <applied value>}``: orchestrator-core decodes every JSON column as an object.
    value = mapped_column(pg.JSONB(), nullable=False)
    applied_at = mapped_column(UtcTimestamp, server_default=text("current_timestamp"), nullable=False)


#: Key of the applied value inside the ``value`` JSON object of a row.
_VALUE = "value"


def _uuid(value: UUID | UUIDstr) -> UUID:
    """Return ``value`` as a :class:`~uuid.UUID`."""
    return value if isinstance(value, UUID) else UUID(str(value))


def lock_node_config(node_instance_id: UUID | UUIDstr) -> None:
    """Serialize the configuration changes of an Optical Node until the transaction ends.

    Takes a PostgreSQL transaction-level advisory lock keyed by the node, so that two
    workflows changing the same device run one after the other.
    """
    db.session.execute(select(func.pg_advisory_xact_lock(func.hashtext(str(_uuid(node_instance_id))))))


def applied_config(node_instance_id: UUID | UUIDstr, owner_instance_id: UUID | UUIDstr, scope: str) -> dict[str, Any]:
    """Return ``{path: value}`` applied by one scope of an owner block on an Optical Node."""
    rows = _all(
        select(OpticalAppliedConfigTable)
        .where(OpticalAppliedConfigTable.node_instance_id == _uuid(node_instance_id))
        .where(OpticalAppliedConfigTable.owner_instance_id == _uuid(owner_instance_id))
        .where(OpticalAppliedConfigTable.scope == scope)
    )
    return {row.path: row.value[_VALUE] for row in rows}


def applied_config_of_other_owners(
    node_instance_id: UUID | UUIDstr, owner_instance_id: UUID | UUIDstr
) -> dict[str, Any]:
    """Return ``{path: value}`` applied on an Optical Node by every owner block but the given one.

    Two owners may only hold the same path with the same value, so one value per path
    is enough.
    """
    rows = _all(
        select(OpticalAppliedConfigTable)
        .where(OpticalAppliedConfigTable.node_instance_id == _uuid(node_instance_id))
        .where(OpticalAppliedConfigTable.owner_instance_id != _uuid(owner_instance_id))
    )
    return {row.path: row.value[_VALUE] for row in rows}


def golden_config_of_other_owners(
    node_instance_id: UUID | UUIDstr, owner_instance_id: UUID | UUIDstr
) -> dict[str, Any]:
    """Return ``{path: value}`` applied on an Optical Node by the product blocks but the given one and the node.

    The rows of the node block itself are its configuration overrides, which never
    conflict with what the other product blocks apply.
    """
    rows = _all(
        select(OpticalAppliedConfigTable)
        .where(OpticalAppliedConfigTable.node_instance_id == _uuid(node_instance_id))
        .where(OpticalAppliedConfigTable.owner_instance_id.not_in([_uuid(owner_instance_id), _uuid(node_instance_id)]))
    )
    return {row.path: row.value[_VALUE] for row in rows}


def node_applied_config(node_instance_id: UUID | UUIDstr) -> dict[str, Any]:
    """Return the golden configuration of an Optical Node: ``{path: value}`` of all its owners."""
    rows = _all(
        select(OpticalAppliedConfigTable)
        .where(OpticalAppliedConfigTable.node_instance_id == _uuid(node_instance_id))
        .order_by(OpticalAppliedConfigTable.path)
    )
    return {row.path: row.value[_VALUE] for row in rows}


def replace_applied_config(
    node_instance_id: UUID | UUIDstr,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
    config: Mapping[str, Any],
) -> None:
    """Record ``config`` as what one scope of an owner block applied on an Optical Node.

    The rows of the scope that are not in ``config`` are deleted, the others are
    inserted or updated. A path the owner already holds under another scope moves to
    this scope (an owner holds a path once).
    """
    node_id, owner_id = _uuid(node_instance_id), _uuid(owner_instance_id)
    stale = delete(OpticalAppliedConfigTable).where(
        OpticalAppliedConfigTable.node_instance_id == node_id,
        OpticalAppliedConfigTable.owner_instance_id == owner_id,
        OpticalAppliedConfigTable.scope == scope,
    )
    if config:
        stale = stale.where(OpticalAppliedConfigTable.path.not_in(list(config)))
    db.session.execute(stale)
    if config:
        upsert = pg.insert(OpticalAppliedConfigTable).values(
            [
                {
                    "node_instance_id": node_id,
                    "path": path,
                    "owner_instance_id": owner_id,
                    "scope": scope,
                    "value": {_VALUE: value},
                }
                for path, value in config.items()
            ]
        )
        db.session.execute(
            upsert.on_conflict_do_update(
                index_elements=["node_instance_id", "path", "owner_instance_id"],
                set_={"scope": upsert.excluded.scope, "value": upsert.excluded.value, "applied_at": func.now()},
            )
        )
    db.session.flush()


def forget_applied_config(node_instance_id: UUID | UUIDstr, owner_instance_id: UUID | UUIDstr, scope: str) -> None:
    """Drop the record of one scope of an owner block on an Optical Node, without touching the device."""
    replace_applied_config(node_instance_id, owner_instance_id, scope, {})
