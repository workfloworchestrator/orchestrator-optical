"""Generation pipeline for the shipped optical data migrations.

The WFO Optical module ships its catalog (products, product blocks, resource types,
workflows) as coded Alembic revisions. This module is the generator that produces those
revisions **from the shipped models**, so they never drift from the code:

* :func:`generate_plan` derives the catalog directly from ``SUBSCRIPTION_MODEL_REGISTRY``
  (the models are the single source of truth) and discovers the shipped workflows from
  the ``orchestrator.optical.workflows`` package.
* :func:`write_migration` renders one Alembic revision file for a plan.
* :func:`verify_no_drift` re-runs the orchestrator-core domain-model diff against the
  database and fails if the applied migrations are not a faithful projection of the
  models — this is the CI gate that catches model drift before a release.

The module ships **no checked-in baseline until the first stable release** (the models are
still being finalised; shipped revisions are immutable once released). Maintainers run the
pipeline in ``--commit`` mode to write the baseline, and in CI to verify no drift.
"""

# Copyright 2026 GARR, GÉANT.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import inspect
import json
import pkgutil
import re
import types
from dataclasses import dataclass
from datetime import UTC, date, datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Union, get_args, get_origin
from uuid import NAMESPACE_OID, uuid5

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

import orchestrator.core.migrations
import orchestrator.optical.products
import orchestrator.optical.workflows
from orchestrator.core.cli.migrate_domain_models import create_domain_models_migration_sql, map_product_blocks
from orchestrator.core.domain import SUBSCRIPTION_MODEL_REGISTRY
from orchestrator.core.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.core.targets import Target
from orchestrator.optical.migrations import version_schema_path

__all__ = [
    "MigrationPlan",
    "WorkflowMigration",
    "apply_migrations",
    "build_catalog",
    "discover_shipped_workflows",
    "generate_plan",
    "pinned_core_revision",
    "render_migration",
    "verify_no_drift",
    "workflow_product_type",
    "write_migration",
]


class UnknownWorkflowFamilyError(ValueError):
    """Raised when a workflow module does not belong to a shipped workflow family."""


class CatalogDriftError(RuntimeError):
    """Raised when the database catalog is not a faithful projection of the shipped models."""


#: Fields of ``ProductBlockModel`` that are not persisted as resource types.
BASE_BLOCK_FIELDS = frozenset({"name", "label", "subscription_instance_id", "owner_subscription_id"})

#: Fields of ``SubscriptionModel`` that are not product fixed inputs.
BASE_SUBSCRIPTION_FIELDS = frozenset(
    {
        "product",
        "customer_id",
        "subscription_id",
        "description",
        "status",
        "insync",
        "start_date",
        "end_date",
        "note",
        "version",
    }
)

#: Namespace for the deterministic UUIDs assigned to products and product blocks, so the
#: generated migration is reproducible across runs.
CATALOG_NAMESPACE = NAMESPACE_OID

#: Mapping of workflow package family to the product type the family's workflows bind to.
#: The keys are prefixes of the shipped workflow module paths (``orchestrator.optical.workflows.<family>``),
#: the values are ``ProductType`` values (the subscription model class names).
WORKFLOW_PRODUCT_TYPES: dict[str, str] = {
    "optical_node.nokia_flexils": "OpticalNodeNokiaFlexIls",
    "optical_node.nokia_groove_g30": "OpticalNodeNokiaGrooveG30",
    "optical_node.nokia_gx_g42": "OpticalNodeNokiaGxG42",
    "optical_coherent_pluggable": "OpticalCoherentPluggable",
    "optical_pipe.fiber_span": "OpticalFiberSpan",
    "optical_pipe.fiber_patch": "OpticalFiberPatch",
    "optical_pipe.leased_spectrum": "OpticalLeasedSpectrum",
    "optical_spectrum_service": "OpticalSpectrum",
    "optical_digital_service": "OpticalDigitalService",
    "optical_location": "OpticalModuleLocationSubscription",
}

_TRANSLATIONS_PATH = Path(orchestrator.optical.products.__file__).parent.parent / "translations" / "en-GB.json"


@dataclass(frozen=True)
class WorkflowMigration:
    """A shipped workflow as it is inserted into the ``workflows`` table by a migration."""

    name: str
    target: str
    description: str
    product_type: str

    def as_migration_dict(self) -> dict[str, str]:
        """Return the dict accepted by ``orchestrator.core.migrations.helpers.create_workflow``."""
        return {
            "name": self.name,
            "target": self.target,
            "description": self.description,
            "product_type": self.product_type,
        }


@dataclass(frozen=True)
class MigrationPlan:
    """The full content of one shipped migration: catalog rows plus workflow rows.

    A plan is derived purely from the shipped models (:func:`generate_plan`); it carries
    its own revision id so that regenerating it with unchanged models is idempotent.
    """

    catalog: dict[str, dict[str, Any]]
    workflows: tuple[WorkflowMigration, ...]
    revision: str

    @property
    def product_names(self) -> tuple[str, ...]:
        """Product names created by this plan, in insertion order."""
        return tuple(self.catalog.get("products", {}))

    @property
    def block_names(self) -> tuple[str, ...]:
        """Product block names created by this plan, in dependency-first order."""
        return tuple(self.catalog.get("product_blocks", {}))

    @property
    def is_empty(self) -> bool:
        """Whether the plan contains no catalog rows and no workflows."""
        return not self.product_names and not self.block_names and not self.workflows

    def upgrade_body(self) -> str:
        """Return the indented body of the migration's ``upgrade()``."""
        lines = ["conn = op.get_bind()"]
        if not self.is_empty:
            lines.append(f"create(conn, {_render_dict(self.catalog)})")
        lines.extend(
            f"create_workflow(conn, {_render_dict(workflow.as_migration_dict())})" for workflow in self.workflows
        )
        return _indent("\n".join(lines), 4)

    def downgrade_body(self) -> str:
        """Return the indented body of the migration's ``downgrade()``."""
        lines = ["conn = op.get_bind()"]
        lines.extend(f"delete_workflow(conn, {workflow.name!r})" for workflow in reversed(self.workflows))
        if not self.is_empty:
            deletes = {"products": list(self.product_names), "product_blocks": list(self.block_names)}
            lines.append(f"delete(conn, {_render_dict(deletes)})")
        return _indent("\n".join(lines), 4)


def pinned_core_revision() -> str:
    """Return the orchestrator-core schema head revision the optical chain attaches to.

    The optical migrations chain linearly onto this revision (``down_revision`` of the
    baseline). Every consumer database contains this revision, because it is the head of
    the orchestrator-core schema migrations at the minimum supported core version.
    Maintainers freeze this value when they set the minimum core version for a release.
    """
    core_migrations_dir = Path(orchestrator.core.migrations.__file__).parent
    config = Config(str(core_migrations_dir / "alembic.ini"))
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        message = f"Expected a single orchestrator-core schema head, found {heads}"
        raise RuntimeError(message)
    return heads[0]


def _slug(value: str) -> str:
    """Return an uppercase underscore slug usable as a product/block tag.

    The ``tag`` columns in ``products`` and ``product_blocks`` are ``varchar(20)``
    (``TAG_LENGTH`` in orchestrator-core), so the slug is truncated to 20 characters;
    tags are labels, not keys, so a deterministic truncation is safe.
    """
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    value = re.sub(r"[^0-9A-Za-z]+", "_", value)
    return value.strip("_").upper()[:20]


def _humanize(value: str) -> str:
    """Return a human-readable phrase for a ``snake_case`` field or block name."""
    words = value.replace("_", " ").split()
    if not words:
        return value
    return " ".join(word.capitalize() for word in words)


def _block_docstring(block_cls: type[ProductBlockModel]) -> str:
    """Return the first non-empty line of a block's docstring, or an empty string."""
    if not block_cls.__doc__:
        return ""
    for line in block_cls.__doc__.splitlines():
        if stripped := line.strip():
            return stripped
    return ""


def _block_scalar_fields(block_cls: type[ProductBlockModel]) -> dict[str, str]:
    """Return the block's resource types (scalar fields) with a derived description."""
    block_fields = block_cls._get_depends_on_product_block_types()  # noqa: SLF001
    return {
        field_name: _humanize(field_name)
        for field_name in block_cls.model_fields
        if field_name not in block_fields and field_name not in BASE_BLOCK_FIELDS and not field_name.startswith("_")
    }


def _block_names(block_type: type[ProductBlockModel]) -> list[str]:
    """Return the database names a block type covers, expanding abstract roots.

    ``__names__`` on a product block returns the block's own name plus, for an abstract
    root, the names of all its concrete variants — exactly the expansion orchestrator-core
    applies when it computes ``product_product_blocks`` relations.
    """
    names = getattr(block_type, "__names__", None)
    if names:
        return sorted(names)
    return [name for name in (block_type.name,) if name]


def _expand_block_type(block_type: Any) -> tuple[type[ProductBlockModel], ...]:
    """Normalize one value of ``_get_depends_on_product_block_types()`` to concrete classes.

    The core helper returns a single class (plain field), a tuple of classes (non-Optional
    union field) or a raw ``typing`` union (list field of a union, e.g. optical pipe
    terminations); all are normalized to a tuple of concrete block classes.
    """
    if isinstance(block_type, tuple):
        return block_type
    if get_origin(block_type) in (Union, types.UnionType):
        return tuple(arg for arg in get_args(block_type) if arg is not type(None))
    return (block_type,)


def _block_depends_on(block_cls: type[ProductBlockModel]) -> tuple[str, ...]:
    """Return the names of the blocks this block depends on, in stable order."""
    depends: set[str] = set()
    for block_type in block_cls._get_depends_on_product_block_types().values():  # noqa: SLF001
        for candidate in _expand_block_type(block_type):
            if getattr(candidate, "name", None):
                depends.update(_block_names(candidate))
    return tuple(sorted(depends))


def _sort_blocks_dependency_first(blocks: dict[str, type[ProductBlockModel]]) -> list[str]:
    """Topologically sort block names so dependencies are created before dependents."""

    def visit(name: str, visiting: set[str]) -> None:
        if name in visited:
            return
        if name in visiting:
            message = f"Circular product block dependency involving {name}"
            raise ValueError(message)
        visiting.add(name)
        for dependency in _block_depends_on(blocks[name]):
            if dependency in blocks:
                visit(dependency, visiting)
        visiting.remove(name)
        visited.add(name)
        ordered.append(name)

    visited: set[str] = set()
    ordered: list[str] = []
    for name in blocks:
        visit(name, set())
    return ordered


def _product_fixed_inputs(model: type[SubscriptionModel]) -> dict[str, str]:
    """Return the product's fixed inputs (its scalar fields) with a derived value.

    The value is the field's declared default when it is a scalar, otherwise a readable
    placeholder derived from the field name. Core's domain-model diff only compares fixed
    input *names*, so any value keeps the catalog in sync; maintainers review the values
    when the baseline is generated for a release.
    """
    block_fields = model._get_depends_on_product_block_types()  # noqa: SLF001
    fixed_inputs: dict[str, str] = {}
    for field_name, field_info in model.model_fields.items():
        if field_name in block_fields or field_name in BASE_SUBSCRIPTION_FIELDS or field_name.startswith("_"):
            continue
        default = field_info.default
        value = default if isinstance(default, str | int | float | bool) else _humanize(field_name)
        fixed_inputs[field_name] = str(value)
    return fixed_inputs


def _product_blocks(model: type[SubscriptionModel]) -> list[str]:
    """Return the names of the product blocks a subscription model directly contains.

    Abstract block references are expanded to all concrete variants (via ``__names__``),
    mirroring how orchestrator-core computes ``product_product_blocks`` relations.
    """
    names: list[str] = []
    for block_type in model._get_depends_on_product_block_types().values():  # noqa: SLF001
        for candidate in _expand_block_type(block_type):
            if getattr(candidate, "name", None):
                names.extend(_block_names(candidate))
    return names


def build_catalog() -> dict[str, dict[str, Any]]:
    """Derive the full shipped catalog (products, product blocks, resource types) from the models.

    Returns:
        A dict in the shape accepted by ``orchestrator.core.migrations.helpers.create``:
        ``{"products": {name: {...}}, "product_blocks": {name: {...}}}``.
    """
    blocks = map_product_blocks(list(SUBSCRIPTION_MODEL_REGISTRY.values()))
    block_order = _sort_blocks_dependency_first(blocks)

    product_blocks: dict[str, dict[str, Any]] = {}
    for block_name in block_order:
        block_cls = blocks[block_name]
        description = _block_docstring(block_cls) or _humanize(block_name)
        product_blocks[block_name] = {
            "product_block_id": str(uuid5(CATALOG_NAMESPACE, f"block:{block_name}")),
            "description": description,
            "tag": _slug(block_name),
            "status": "active",
            "resources": _block_scalar_fields(block_cls),
        }
        if dependencies := _block_depends_on(block_cls):
            product_blocks[block_name]["depends_on_block_relations"] = list(dependencies)

    products: dict[str, dict[str, Any]] = {}
    for product_name, model in SUBSCRIPTION_MODEL_REGISTRY.items():
        fixed_inputs = _product_fixed_inputs(model)
        product: dict[str, Any] = {
            "product_id": str(uuid5(CATALOG_NAMESPACE, f"product:{product_name}")),
            "product_type": model.__name__,
            "description": product_name,
            "tag": _slug(product_name),
            "status": "active",
            "product_blocks": _product_blocks(model),
        }
        if fixed_inputs:
            product["fixed_inputs"] = fixed_inputs
        products[product_name] = product

    return {"products": products, "product_blocks": product_blocks}


def _workflow_descriptions() -> dict[str, str]:
    """Return the shipped workflow display strings from the translations file."""
    try:
        translations = json.loads(_TRANSLATIONS_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return translations.get("workflow", {})


def workflow_product_type(module_name: str) -> str:
    """Return the product type a shipped workflow binds to, based on its module path.

    Raises:
        ValueError: If the workflow module does not belong to a known shipped family.
    """
    prefix = "orchestrator.optical.workflows."
    if not module_name.startswith(prefix):
        message = f"{module_name} is not a shipped optical workflow module"
        raise UnknownWorkflowFamilyError(message)
    family = module_name[len(prefix) :]
    for known_family, product_type in WORKFLOW_PRODUCT_TYPES.items():
        if family == known_family or family.startswith(known_family + "."):
            return product_type
    message = f"No product type registered for workflow family {family!r}"
    raise UnknownWorkflowFamilyError(message)


def discover_shipped_workflows() -> tuple[WorkflowMigration, ...]:
    """Discover the shipped workflows from the ``orchestrator.optical.workflows`` package.

    The shipped workflows are the module-level functions decorated with
    ``@create_workflow``/``@modify_workflow``/``@terminate_workflow``/``@validate_workflow``
    (they carry a ``target`` attribute). The descriptions come from the shipped
    translations file; the product type from :func:`workflow_product_type`.
    """
    descriptions = _workflow_descriptions()
    workflows: list[WorkflowMigration] = []
    for module_info in pkgutil.walk_packages(
        orchestrator.optical.workflows.__path__, orchestrator.optical.workflows.__name__ + "."
    ):
        if module_info.name.endswith("__init__"):
            continue
        module = import_module(module_info.name)
        for attribute_name, attribute in vars(module).items():
            # Only module-level functions can be shipped workflows; this also avoids
            # touching proxied objects (e.g. ``orchestrator.core.db``) whose ``__getattr__``
            # raises when no database is configured.
            if attribute_name.startswith("_") or not inspect.isfunction(attribute):
                continue
            if not isinstance(getattr(attribute, "target", None), Target):
                continue
            workflows.append(
                WorkflowMigration(
                    name=attribute.name,
                    target=attribute.target.value,
                    description=descriptions.get(attribute.name, attribute.name),
                    product_type=workflow_product_type(module_info.name),
                )
            )
    return tuple(sorted(workflows, key=lambda workflow: (workflow.product_type, workflow.target, workflow.name)))


def _plan_revision(catalog: dict[str, Any], workflows: tuple[WorkflowMigration, ...]) -> str:
    """Return a deterministic revision id derived from the plan content.

    Regenerating a plan with unchanged models yields the same revision id, so applying it
    to an already-migrated database is a no-op (the harness can reuse an external DB).
    """
    content = json.dumps(catalog, sort_keys=True) + json.dumps(
        [w.as_migration_dict() for w in workflows], sort_keys=True
    )
    return hashlib.sha1(content.encode()).hexdigest()[:12]  # noqa: S324  # content hash, not security


def generate_plan() -> MigrationPlan:
    """Generate the migration plan for the currently shipped models.

    This is a pure function: it derives everything from the models and needs no database.
    """
    catalog = build_catalog()
    workflows = discover_shipped_workflows()
    return MigrationPlan(catalog=catalog, workflows=workflows, revision=_plan_revision(catalog, workflows))


def _render_dict(value: dict[str, Any]) -> str:
    """Render a dict as a compact but readable Python literal."""
    return json.dumps(value, indent=4, sort_keys=False)


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" if line else line for line in text.splitlines())


def render_migration(plan: MigrationPlan, *, down_revision: str, message: str, create_date: date | None = None) -> str:
    """Render a complete Alembic revision file for a plan.

    Args:
        plan: The plan to render.
        down_revision: The revision this migration chains onto (for the baseline this is
            the pinned orchestrator-core schema head; for deltas the previous optical head).
        message: The migration message (used as the revision docstring and file slug).
        create_date: Optional creation date (defaults to today).

    Returns:
        The full migration file content.
    """
    create_date = create_date or datetime.now(UTC).date()
    header_lines = [
        f'"""{message}',
        "",
        f"Revision ID: {plan.revision}",
        f"Revises: {down_revision}",
        f"Create Date: {create_date.isoformat()}",
        "",
        '"""',
        "from alembic import op",
        "",
        "from orchestrator.core.migrations.helpers import create, create_workflow, delete, delete_workflow",
        "",
        "# revision identifiers, used by Alembic.",
        f"revision = {plan.revision!r}",
        f"down_revision = {down_revision!r}",
        "branch_labels = None",
        "depends_on = None",
        "",
        "",
        "def upgrade() -> None:",
        plan.upgrade_body(),
        "",
        "",
        "def downgrade() -> None:",
        plan.downgrade_body(),
        "",
    ]
    return "\n".join(header_lines)


def write_migration(plan: MigrationPlan, version_dir: Path, *, down_revision: str, message: str) -> Path:
    """Write a rendered migration file into ``version_dir``.

    Args:
        plan: The plan to write.
        version_dir: Target directory (e.g. the shipped ``versions/schema`` or a scratch dir).
        down_revision: The revision this migration chains onto.
        message: The migration message.

    Returns:
        The path of the written file.
    """
    version_dir.mkdir(parents=True, exist_ok=True)
    slug = "_".join(part for part in message.lower().replace("-", "_").split() if part)
    path = version_dir / f"{datetime.now(UTC).date().isoformat()}_{plan.revision}_{slug}.py"
    path.write_text(render_migration(plan, down_revision=down_revision, message=message))
    return path


def apply_migrations(version_dir: Path | None = None) -> None:
    """Apply all pending migrations (core + optical) to the configured database.

    Runs Alembic ``upgrade head`` reusing the orchestrator-core migration environment and
    the core schema migrations, plus the optical versions in ``version_dir`` (defaults to
    the shipped ``versions/schema``). The database URL is taken from
    ``orchestrator.core.settings`` at runtime by the core ``env.py``.
    """
    core_migrations_dir = Path(orchestrator.core.migrations.__file__).parent
    config = Config(str(Path(__file__).parent / "alembic.ini"))
    config.set_main_option("script_location", str(core_migrations_dir))
    optical_dir = str(version_dir) if version_dir is not None else str(version_schema_path())
    config.set_main_option("version_locations", f"{core_migrations_dir / 'versions' / 'schema'} {optical_dir}")
    command.upgrade(config, "head")


def prefill_inputs() -> dict[str, dict[str, str]]:
    """Return the inputs dict that makes the core domain-model diff fully non-interactive.

    The diff wizard prompts for product/block/resource descriptions and tags; this returns
    prefilled values derived from the models so :func:`verify_no_drift` never prompts. The
    dict is keyed by entity name (product, product block, resource type), as expected by
    ``create_domain_models_migration_sql``; entity names are disjoint in the shipped module.
    """
    inputs: dict[str, dict[str, str]] = {
        name: {"description": name, "tag": _slug(name)} for name in SUBSCRIPTION_MODEL_REGISTRY
    }
    for block_name, block_cls in map_product_blocks(list(SUBSCRIPTION_MODEL_REGISTRY.values())).items():
        description = _block_docstring(block_cls) or _humanize(block_name)
        inputs[block_name] = {"description": description, "tag": _slug(block_name)}
        for resource_type in _block_scalar_fields(block_cls):
            inputs[resource_type] = {"description": _humanize(resource_type)}
    return inputs


def verify_no_drift() -> None:
    """Fail if the database catalog is not a faithful projection of the shipped models.

    Re-runs the orchestrator-core domain-model diff (the same machinery behind
    ``orchestrator db migrate-domain-models``) against the configured database and raises
    ``RuntimeError`` if it reports any missing products, blocks, resource types or
    fixed inputs. Requires a configured database and an imported model registry.
    """
    upgrade_sql, downgrade_sql = create_domain_models_migration_sql(
        inputs=prefill_inputs(), updates=None, is_test=True, confirm_warnings=True
    )
    if upgrade_sql or downgrade_sql:
        lines = "\n".join(upgrade_sql[:10])
        message = (
            "Database catalog drifted from the shipped models; regenerate and apply the optical migration. "
            f"Pending upgrade statements ({len(upgrade_sql)}):\n{lines}"
        )
        raise CatalogDriftError(message)
