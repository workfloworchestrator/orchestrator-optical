"""Tests for the shipped-migration generation pipeline.

The database-free tests lock the contract of the pipeline: the shipped workflows are
discovered (with their product type and target), the catalog derived from the models is
well-formed, the plan is deterministic and the rendered migration is valid Python. The
DB-backed test runs the full generate -> apply -> drift-check path against the harness
database (the ``postgres_database`` fixture already does this once per session) and
asserts the provisioned catalog contains the shipped workflows.
"""

from pathlib import Path

import pytest

from orchestrator.core.domain import SUBSCRIPTION_MODEL_REGISTRY
from orchestrator.optical.migrations import add_optical_module_migrations, alembic_cfg, version_schema_path
from orchestrator.optical.migrations.generate import (
    build_catalog,
    discover_shipped_workflows,
    generate_plan,
    pinned_core_revision,
    render_migration,
    workflow_product_type,
)

#: Expected size of the shipped workflow set (create/modify/terminate/validate per family).
EXPECTED_SHIPPED_WORKFLOW_COUNT = 40


def test_shipped_workflow_discovery_contract() -> None:
    """Every shipped workflow is discovered, resolved to a product type and has a target."""
    workflows = discover_shipped_workflows()
    assert len(workflows) == EXPECTED_SHIPPED_WORKFLOW_COUNT
    assert len({workflow.name for workflow in workflows}) == EXPECTED_SHIPPED_WORKFLOW_COUNT

    product_types = {model.__name__ for model in SUBSCRIPTION_MODEL_REGISTRY.values()}
    for workflow in workflows:
        assert workflow.product_type in product_types, workflow.product_type
        assert workflow.target in {"CREATE", "MODIFY", "TERMINATE", "VALIDATE"}
        assert workflow.description

    by_product_type: dict[str, set[str]] = {}
    for workflow in workflows:
        by_product_type.setdefault(workflow.product_type, set()).add(workflow.target)
    for product_type, targets in by_product_type.items():
        assert targets == {"CREATE", "MODIFY", "TERMINATE", "VALIDATE"}, product_type


def test_workflow_product_type_rejects_unknown_family() -> None:
    """An unknown workflow module path fails loudly instead of silently misbinding."""
    with pytest.raises(ValueError, match="No product type registered"):
        workflow_product_type("orchestrator.optical.workflows.optical_unknown.create")
    with pytest.raises(ValueError, match="not a shipped optical workflow module"):
        workflow_product_type("mywfo.workflows.create_thing")


def test_catalog_is_well_formed() -> None:
    """The derived catalog is internally consistent: relations reference existing blocks."""
    catalog = build_catalog()
    products = catalog["products"]
    product_blocks = catalog["product_blocks"]
    assert products
    assert product_blocks

    for product_name, product in products.items():
        assert product_name in SUBSCRIPTION_MODEL_REGISTRY
        assert product["product_type"] == SUBSCRIPTION_MODEL_REGISTRY[product_name].__name__
        assert product["status"] == "active"
        assert product["product_blocks"], product_name
        for block_name in product["product_blocks"]:
            assert block_name in product_blocks, block_name

    for block in product_blocks.values():
        assert block["status"] == "active"
        assert isinstance(block["resources"], dict)
        for dependency in block.get("depends_on_block_relations", []):
            assert dependency in product_blocks, dependency


def test_plan_is_deterministic() -> None:
    """Regenerating a plan with unchanged models yields the same revision and content."""
    first = generate_plan()
    second = generate_plan()
    assert first.revision == second.revision
    assert first.catalog == second.catalog
    assert first.workflows == second.workflows
    assert not first.is_empty


def test_rendered_migration_is_valid_python() -> None:
    """The rendered revision file is valid Python and chains onto the pinned core head."""
    plan = generate_plan()
    down_revision = pinned_core_revision()
    rendered = render_migration(plan, down_revision=down_revision, message="optical baseline")

    compile(rendered, "<optical-migration>", "exec")

    assert f"revision = '{plan.revision}'" in rendered
    assert f"down_revision = '{down_revision}'" in rendered
    assert "from orchestrator.core.migrations.helpers import create" in rendered
    assert "def upgrade() -> None:" in rendered
    assert "def downgrade() -> None:" in rendered
    # The downgrade deletes the workflows and the catalog rows.
    assert "delete_workflow(conn" in rendered
    assert "delete(conn" in rendered


def test_pinned_core_revision_is_the_single_core_head() -> None:
    """The pinned revision is exactly the single orchestrator-core schema head."""
    assert pinned_core_revision()
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    import orchestrator.core.migrations

    core_dir = Path(orchestrator.core.migrations.__file__).parent
    config = Config(str(core_dir / "alembic.ini"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert pinned_core_revision() == heads[0]
    assert len(heads) == 1


def test_migration_helpers_expose_the_shipped_versions_dir() -> None:
    """The consumer-facing helpers point at the shipped versions/schema directory."""
    assert version_schema_path().name == "schema"
    assert version_schema_path().is_absolute()

    config = alembic_cfg()
    script_location = config.get_main_option("script_location")
    assert script_location is not None
    assert Path(script_location).name == "migrations"
    assert (Path(script_location) / "env.py").exists()
    locations = config.get_main_option("version_locations")
    assert locations is not None
    assert str(version_schema_path()) in locations

    augmented = add_optical_module_migrations(config)
    assert augmented is config
    augmented_locations = config.get_main_option("version_locations")
    assert augmented_locations is not None
    assert locations in augmented_locations


@pytest.mark.db
def test_provisioned_catalog_contains_the_shipped_workflows(postgres_database) -> None:
    """The generated migration provisions the workflows table with the shipped workflows."""
    from sqlalchemy import select

    from orchestrator.core.db import WorkflowTable

    discovered = discover_shipped_workflows()
    with postgres_database.database_scope():
        rows = {
            row.name: row
            for row in postgres_database.session.scalars(
                select(WorkflowTable).where(WorkflowTable.name.in_([workflow.name for workflow in discovered]))
            )
        }
    assert len(rows) == len(discovered)
    for workflow in discovered:
        row = rows[workflow.name]
        assert row.target == workflow.target
        assert row.is_task is False
