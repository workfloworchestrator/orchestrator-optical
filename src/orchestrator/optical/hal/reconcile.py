"""Declarative configuration of the NETCONF devices: render, diff, apply, release.

The Nokia Groove G30 and GX G42 adapters do not push configuration imperatively: they
*render* the desired configuration of an object (a line port, a client port, a
cross-connect, a fiber termination, ...) as :class:`Fragment` s and hand them to this
module, which is the single place where a device is compared and changed:

- :func:`diff_config` compares the fragments with the running configuration (read-only);
- :func:`verify_config` is :func:`diff_config` raising :class:`ConfigDriftError` on a difference;
- :func:`apply_config` applies the difference, re-reads the device and records what was
  applied in the ``optical_applied_config`` table;
- :func:`release_config` applies "nothing": whatever the owner had applied is reset or
  deleted, unless another owner still holds it.

The comparison is done with the SDK primitives: every fragment is a partial SDK model
flattened with ``model_dump_instances()``, the running configuration is the model read
from the device flattened the same way, and the two maps are classified by the client's
``diff_instances()``; the resulting diff is sent with the client's ``reconcile()``.

Scope of a change. A call acts on one *scope* (rendering unit, e.g. ``line`` or
``client:<port>``) of one *owner* product block on one Optical Node, and never on more
than the paths rendered for it or recorded for it: the running map is restricted to
those paths before the comparison, so the SDK never infers a removal, and a release is
built explicitly from the adapter's :data:`ReleaseRule` (a reset value, the deletion of a
list entry, or nothing). Configuration nobody rendered is never touched (brownfield).

Recorded configuration. The table holds what was *applied* (not what is desired, which is
always rendered again from the blocks): the rows of a node are its golden configuration,
and they are what a later call needs to know what to release.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any
from uuid import UUID

from orchestrator.optical import db as optical_db
from orchestrator.optical.hal._common import (
    LazyAdapter,
    UnsupportedPlatformError,
    _node_id,
    _vendor_platform,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor

if TYPE_CHECKING:
    from pydantic_forms.types import UUIDstr

    from orchestrator.optical.hal.adapters.nokia_groove_g30 import config as groove_g30
    from orchestrator.optical.hal.adapters.nokia_gx_g42 import config as gx_g42
    from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
else:
    groove_g30 = LazyAdapter("orchestrator.optical.hal.adapters.nokia_groove_g30.config")
    gx_g42 = LazyAdapter("orchestrator.optical.hal.adapters.nokia_gx_g42.config")

__all__ = [
    "ConfigApplyError",
    "ConfigConflictError",
    "ConfigDiff",
    "ConfigDriftError",
    "DeleteEntry",
    "Fragment",
    "ReleaseRule",
    "Reset",
    "apply_config",
    "diff_config",
    "forget_config",
    "fragment",
    "golden_config",
    "leaf_name",
    "parent_name",
    "release_config",
    "split_instance_path",
    "verify_config",
]


class ConfigDriftError(ValueError):
    """Raised when the running configuration of a device differs from the desired one."""


class ConfigConflictError(ValueError):
    """Raised when a path is desired with a value that differs from the one another owner applied."""


class ConfigApplyError(RuntimeError):
    """Raised when a device does not accept, or does not converge to, the desired configuration."""


@dataclass(frozen=True)
class Fragment:
    """The desired leaves of one device data node.

    Attributes:
        node: The SDK navigator of the data node (a container or a list entry).
        leaves: ``{instance-identifier: value}`` of the desired leaves of the node, as
            flattened by the SDK (``model_dump_instances``), without its key leaves.
        stage: Fragments are applied in ascending stage, one edit per stage, for the
            objects the device only creates once another one is configured (e.g. the
            optical channel of a port, created when the port mode is set).
    """

    node: Any
    leaves: Mapping[str, Any]
    stage: int = 0


@dataclass(frozen=True)
class Reset:
    """Release a leaf by writing its factory value."""

    value: Any


@dataclass(frozen=True)
class DeleteEntry:
    """Release a leaf by deleting the list entry (given by its instance-identifier) that holds it."""

    path: str


#: Decides how a released path is taken off a device: a :class:`Reset`, a
#: :class:`DeleteEntry`, or ``None`` to leave the device alone (the leaf of an object the
#: device removes by itself, or one that has no factory value).
ReleaseRule = Callable[[str], Reset | DeleteEntry | None]


@dataclass(frozen=True)
class ConfigDiff:
    """The difference between the desired and the running configuration of one scope.

    Attributes:
        node: Device-side name of the Optical Node.
        added: ``{path: value}`` desired but absent from the device.
        changed: ``{path: (running, desired)}`` present with another value.
        reset: ``{path: value}`` released leaves written back to their factory value.
        deleted: Instance-identifiers of the released list entries to delete.
    """

    node: str
    added: dict[str, Any] = field(default_factory=dict)
    changed: dict[str, tuple[Any, Any]] = field(default_factory=dict)
    reset: dict[str, Any] = field(default_factory=dict)
    deleted: tuple[str, ...] = ()

    def __bool__(self) -> bool:
        """Whether there is anything to change on the device."""
        return bool(self.added or self.changed or self.reset or self.deleted)

    def as_dict(self) -> dict[str, Any]:
        """Return the diff as plain data, for the workflow state."""
        return {
            "node": self.node,
            "added": dict(self.added),
            "changed": {path: {"running": old, "desired": new} for path, (old, new) in self.changed.items()},
            "reset": dict(self.reset),
            "deleted": list(self.deleted),
        }


def split_instance_path(path: str) -> list[str]:
    """Split an instance-identifier into its segments, ignoring the ``/`` inside key predicates."""
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in path:
        if quote is not None:
            quote = None if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
        elif char == "/" and depth == 0:
            if current:
                segments.append("".join(current))
            current = []
            continue
        current.append(char)
    if current:
        segments.append("".join(current))
    return segments


def _node_name(segment: str) -> str:
    """Return the node name of a path segment, without module prefix and predicates."""
    return segment.split("[", 1)[0].rsplit(":", 1)[-1]


def leaf_name(path: str) -> str:
    """Return the name of the last node of an instance-identifier."""
    return _node_name(split_instance_path(path)[-1])


def parent_name(path: str) -> str:
    """Return the name of the node holding the last node of an instance-identifier."""
    segments = split_instance_path(path)
    return _node_name(segments[-2]) if len(segments) > 1 else ""


def _entry_path(path: str, entry_name: str) -> str | None:
    """Return the instance-identifier of the closest ancestor of ``path`` named ``entry_name``."""
    segments = split_instance_path(path)
    for index in range(len(segments) - 1, -1, -1):
        if _node_name(segments[index]) == entry_name:
            return "/" + "/".join(segments[: index + 1])
    return None


def _is_leaf_list_entry(path: str) -> bool:
    """Whether the path addresses one entry of a leaf-list (``name[.='value']``)."""
    return split_instance_path(path)[-1].partition("[")[2].startswith(".=")


def _leaf_list_base(path: str) -> str:
    """Return the instance-identifier of the leaf-list an entry path belongs to."""
    return path[: path.rindex("[")]


def fragment(node: Any, *, stage: int = 0, **leaves: Any) -> Fragment:
    """Render the desired leaves of an SDK data node.

    The leaves are validated one by one by the SDK model of the node (a partial model:
    the mandatory leaves of the node need not be given) and flattened with
    ``model_dump_instances()``, so that they compare with what is read from the device.

    Args:
        node: The SDK navigator of the data node.
        stage: The stage the fragment is applied in, see :class:`Fragment`.
        **leaves: The desired leaves, by SDK model field name.

    Returns:
        The fragment of the node.
    """
    models = importlib.import_module(type(node).__module__.replace(".data_navigators", ".data_models"))
    model = getattr(models, type(node).__name__.removesuffix("Node")).model_construct()
    for name, value in leaves.items():
        setattr(model, name, value)  # validated by the model (validate_assignment)
    instance_path = node.instance_identifier()
    # The key leaves are part of the entry address: sent again as leaves, the SDK edit
    # would carry them twice.
    keys = {f"{instance_path}/{key}" for key in _segment_keys(split_instance_path(instance_path)[-1])}
    dumped = model.model_dump_instances(instance_path, content="config")
    return Fragment(node, {path: value for path, value in dumped.items() if path not in keys}, stage)


def _segment_keys(segment: str) -> list[str]:
    """Return the key names of the predicates of a path segment."""
    keys: list[str] = []
    quote: str | None = None
    depth = 0
    start = 0
    for index, char in enumerate(segment):
        if quote is not None:
            quote = None if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == "[":
            depth += 1
            start = index + 1
        elif char == "]":
            depth -= 1
        elif char == "=" and depth == 1 and start:
            keys.append(segment[start:index])
            start = 0
    return keys


def _device(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> tuple[Any, ReleaseRule]:
    """Return the connected NETCONF client of a node and the release rule of its platform."""
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.get_g30_client(optical_node_block), groove_g30.release_rule
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.get_g42_client(optical_node_block), gx_g42.release_rule
        case _:
            msg = f"declarative configuration: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def _running(fragments: Iterable[Fragment]) -> dict[str, Any]:
    """Read the running value of every desired leaf of the fragments from the device."""
    running: dict[str, Any] = {}
    for item in fragments:
        model = item.node.retrieve(content="config", depth=2)
        if model is None:
            continue
        leaf_lists = {_leaf_list_base(path) for path in item.leaves if _is_leaf_list_entry(path)}
        dumped = model.model_dump_instances(item.node.instance_identifier(), content="config")
        running.update(
            {
                path: value
                for path, value in dumped.items()
                if path in item.leaves or (_is_leaf_list_entry(path) and _leaf_list_base(path) in leaf_lists)
            }
        )
    return running


def _same_number(running: Any, intended: Any) -> bool:
    """Whether two flattened values are the same decimal number written differently (``1.5`` and ``1.50``)."""
    if not (isinstance(running, str) and isinstance(intended, str)) or running == intended:
        return False
    try:
        return Decimal(running) == Decimal(intended)
    except InvalidOperation:
        return False


def _intended(fragments: Iterable[Fragment]) -> dict[str, Any]:
    """Merge the desired leaves of the fragments."""
    intended: dict[str, Any] = {}
    for item in fragments:
        intended.update(item.leaves)
    return intended


def _instance_diff(client: Any, fragments: Sequence[Fragment]) -> Any:
    """Classify the desired leaves of the fragments against the device with the SDK ``diff_instances``."""
    intended = _intended(fragments)
    running = _running(fragments)
    # A decimal leaf flattens to its lexical form: the device may pad it differently.
    running.update({path: intended[path] for path, value in running.items() if _same_number(value, intended.get(path))})
    instance_diff = client.diff_instances(running, intended)
    if instance_diff.removed:  # the running map is restricted to the desired paths
        msg = f"Unexpected removals in the configuration diff: {sorted(instance_diff.removed)}"
        raise ConfigApplyError(msg)
    return instance_diff


def _check_conflicts(node: str, intended: Mapping[str, Any], others: Mapping[str, Any]) -> None:
    """Raise when a desired path is held by another owner with a different value."""
    conflicts = {
        path: {"applied": others[path], "desired": value}
        for path, value in intended.items()
        if path in others and others[path] != value
    }
    if conflicts:
        msg = f"Configuration of {node} conflicts with the one applied by another product block: {conflicts}"
        raise ConfigConflictError(msg)


def _releases(
    released: Iterable[str],
    intended: Mapping[str, Any],
    others: Mapping[str, Any],
    release_rule: ReleaseRule,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Return the resets and the entry deletions that take the released paths off a device.

    A path still desired, or held by another owner, stays; so does a list entry any of
    whose leaves is still desired or held.
    """
    resets: dict[str, Any] = {}
    deletions: dict[str, None] = {}
    kept = [*intended, *others]
    for path in released:
        if path in intended or path in others:
            continue
        match release_rule(path):
            case Reset(value=value):
                resets[path] = value
            case DeleteEntry(path=entry):
                if not any(held.startswith(f"{entry}/") for held in kept):
                    deletions[entry] = None
            case _:
                pass
    return resets, tuple(deletions)


def _ids(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion, owner_instance_id: UUID | UUIDstr
) -> tuple[UUID, UUID]:
    """Return the node and owner instance ids as UUIDs."""
    owner = owner_instance_id if isinstance(owner_instance_id, UUID) else UUID(str(owner_instance_id))
    return optical_node_block.subscription_instance_id, owner


def diff_config(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
    fragments: Sequence[Fragment],
) -> ConfigDiff:
    """Compare the desired configuration of a scope with the device (read-only).

    Args:
        optical_node_block: The Optical Node hosting the configuration.
        owner_instance_id: ``subscription_instance_id`` of the product block the configuration belongs to.
        scope: The rendering unit of the owner, e.g. ``line`` or ``client:<port>``.
        fragments: The desired configuration of the scope.

    Returns:
        The difference, including what a later :func:`apply_config` would release.

    Raises:
        ConfigConflictError: If another owner applied a different value at a desired path.
    """
    client, release_rule = _device(optical_node_block)
    return _diff(client, release_rule, optical_node_block, owner_instance_id, scope, fragments, ())[0]


def _diff(
    client: Any,
    release_rule: ReleaseRule,
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
    fragments: Sequence[Fragment],
    also_released: Iterable[str],
) -> tuple[ConfigDiff, dict[str, Any]]:
    """Return the diff of a scope and its desired ``{path: value}``."""
    node_id, owner_id = _ids(optical_node_block, owner_instance_id)
    node = _node_id(optical_node_block)
    intended = _intended(fragments)
    others = optical_db.applied_config_of_other_owners(node_id, owner_id)
    _check_conflicts(node, intended, others)
    instance_diff = _instance_diff(client, fragments)
    released = [*optical_db.applied_config(node_id, owner_id, scope), *also_released]
    resets, deletions = _releases(released, intended, others, release_rule)
    return (
        ConfigDiff(node, dict(instance_diff.added), dict(instance_diff.changed), resets, deletions),
        intended,
    )


def verify_config(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
    fragments: Sequence[Fragment],
) -> None:
    """Check that the device runs the desired configuration of a scope (read-only).

    Raises:
        ConfigDriftError: If a desired leaf is missing from the device or has another value.
        ConfigConflictError: If another owner applied a different value at a desired path.
    """
    client, _ = _device(optical_node_block)
    node_id, owner_id = _ids(optical_node_block, owner_instance_id)
    node = _node_id(optical_node_block)
    _check_conflicts(node, _intended(fragments), optical_db.applied_config_of_other_owners(node_id, owner_id))
    instance_diff = _instance_diff(client, fragments)
    if instance_diff.added or instance_diff.changed:
        drift = ConfigDiff(node, dict(instance_diff.added), dict(instance_diff.changed)).as_dict()
        msg = f"Configuration mismatch for {node} ({scope}):\nmissing: {drift['added']}\nmismatch: {drift['changed']}\n"
        raise ConfigDriftError(msg)


def apply_config(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
    fragments: Sequence[Fragment],
    *,
    also_released: Iterable[str] = (),
) -> dict[str, Any]:
    """Make the device run the desired configuration of a scope, and record it.

    The list entries the scope had applied and no longer renders are deleted first, then
    only the difference is sent, one edit per fragment stage, and finally the leaves no
    longer rendered are reset. The device is read again after a change: the configuration
    is recorded as applied only once the device runs it.

    Args:
        optical_node_block: The Optical Node to configure.
        owner_instance_id: ``subscription_instance_id`` of the product block the configuration belongs to.
        scope: The rendering unit of the owner, e.g. ``line`` or ``client:<port>``.
        fragments: The desired configuration of the scope (empty to release the scope).
        also_released: Paths to release besides the recorded ones, for configuration
            applied before it was recorded.

    Returns:
        The applied difference, as plain data.

    Raises:
        ConfigConflictError: If another owner applied a different value at a desired path.
        ConfigApplyError: If the device rejects an edit or does not converge.
    """
    node_id, owner_id = _ids(optical_node_block, owner_instance_id)
    optical_db.lock_node_config(node_id)
    client, release_rule = _device(optical_node_block)
    node = _node_id(optical_node_block)
    intended = _intended(fragments)
    others = optical_db.applied_config_of_other_owners(node_id, owner_id)
    _check_conflicts(node, intended, others)
    released = [*optical_db.applied_config(node_id, owner_id, scope), *also_released]
    resets, deletions = _releases(released, intended, others, release_rule)
    sdk = importlib.import_module(type(client).__module__)

    # Entries go first: they free the resources (e.g. a tributary) a new entry may need.
    if deletions:
        removals = {path: sdk.Removal(path, "list-entry") for path in deletions}
        _send(client, sdk.InstanceDiff({}, {}, removals), node)

    added: dict[str, Any] = {}
    changed: dict[str, tuple[Any, Any]] = {}
    for stage in sorted({item.stage for item in fragments}):
        instance_diff = _instance_diff(client, [item for item in fragments if item.stage == stage])
        if instance_diff.added or instance_diff.changed:
            _send(client, instance_diff, node)
            added.update(instance_diff.added)
            changed.update(instance_diff.changed)

    if resets:
        _send(client, sdk.InstanceDiff(dict(resets), {}, {}), node)

    if added or changed:
        remaining = _instance_diff(client, fragments)
        if remaining.added or remaining.changed:
            drift = ConfigDiff(node, dict(remaining.added), dict(remaining.changed)).as_dict()
            msg = f"{node} did not converge to the desired configuration ({scope}): {drift}"
            raise ConfigApplyError(msg)

    optical_db.replace_applied_config(node_id, owner_id, scope, intended)
    return ConfigDiff(node, added, changed, resets, deletions).as_dict()


def _send(client: Any, instance_diff: Any, node: str) -> None:
    """Send a diff to the device with the SDK ``reconcile`` (validated and committed by the device)."""
    if not client.reconcile(instance_diff):
        msg = f"{node} did not accept the configuration change: {dict(instance_diff)}"
        raise ConfigApplyError(msg)


def release_config(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
    fragments: Sequence[Fragment] = (),
) -> dict[str, Any]:
    """Take the configuration of a scope off the device, unless another owner still holds it.

    Args:
        optical_node_block: The Optical Node to configure.
        owner_instance_id: ``subscription_instance_id`` of the product block the configuration belongs to.
        scope: The rendering unit of the owner to release.
        fragments: The configuration the scope renders, released as well: it covers the
            configuration applied before it was recorded.

    Returns:
        The applied difference, as plain data.
    """
    return apply_config(optical_node_block, owner_instance_id, scope, (), also_released=_intended(fragments))


def forget_config(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    owner_instance_id: UUID | UUIDstr,
    scope: str,
) -> None:
    """Drop the record of a scope without touching the device (its configuration stays, unowned)."""
    node_id, owner_id = _ids(optical_node_block, owner_instance_id)
    optical_db.forget_applied_config(node_id, owner_id, scope)


def golden_config(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> dict[str, Any]:
    """Return the golden configuration of an Optical Node: every ``{path: value}`` applied by the orchestrator."""
    return optical_db.node_applied_config(optical_node_block.subscription_instance_id)
