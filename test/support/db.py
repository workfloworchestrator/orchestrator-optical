"""Database-backed execution-test harness for the shipped workflows.

This module provisions a throwaway PostgreSQL container (``pgvector/pgvector:pg16`` —
the orchestrator-core migration head requires the pgvector extension), applies the
orchestrator-core migrations (``alembic upgrade head``, the same path a consumer uses),
provisions the shipped catalog (product, product block, resource types, workflows) from
the migration generated off the shipped models and registers all the shipped workflows
of every family (discovered by walking ``orchestrator.optical.workflows``), so the
shipped workflows can be executed end to end through the real orchestrator-core process
engine (``start_process`` with the threadpool executor). The generation step doubles as
the drift gate: after applying the generated migration the catalog must be a faithful
projection of the models (``verify_no_drift``).

All database configuration lives in this harness only: the module under test keeps its
no-import-time-side-effects rule and its settings are never touched. Set
``OPTICAL_TEST_PG_URL`` to an existing PostgreSQL URL to reuse an external instance
instead of spinning up a container.

The session-scoped ``postgres_database`` fixture rewrites the global
``core_settings.app_settings`` process-wide; it captures the previous value before the
overwrite and restores it on teardown, so the session never leaves the process-global
settings pointing at the (stopped) container.
"""

import inspect
import os
import pkgutil
from collections.abc import Callable, Iterator
from importlib import import_module
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from pydantic_forms.validators import Choice
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select, text
from testcontainers.community.postgres import PostgresContainer

import orchestrator.core.db as core_db
import orchestrator.core.settings as core_settings
import orchestrator.optical.migrations.generate as migrations
import orchestrator.optical.products  # register the shipped product types in the registry
import orchestrator.optical.workflows
from orchestrator.core.db import (
    ProcessSubscriptionTable,
    ProcessTable,
    ProductTable,
    SubscriptionTable,
)
from orchestrator.core.db.database import BaseModel as CoreBaseModel
from orchestrator.core.services.processes import start_process
from orchestrator.core.targets import Target
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import ProcessStatus
from orchestrator.core.workflows import LazyWorkflowInstance
from orchestrator.optical import db as optical_db
from orchestrator.optical.workflows.customer import register_customer_choice

#: PostgreSQL image shipping the pgvector extension required by the orchestrator-core migration head.
POSTGRES_IMAGE = "pgvector/pgvector:pg16"

#: Error shown when the PostgreSQL test container cannot be started.
CONTAINER_START_ERROR_MSG = (
    "Could not start the PostgreSQL test container for the DB-backed execution tests. "
    "A running Docker daemon is required; pull the image with "
    f"'docker pull {POSTGRES_IMAGE}' and re-run, or set OPTICAL_TEST_PG_URL to an existing "
    "PostgreSQL URL to reuse an external instance."
)

#: Customer id used by the seeded subscriptions and the form inputs.
CUSTOMER_ID = "cust-1"

#: Sentinel marking "no previous ``app_settings`` value could be read" (see the
#: ``postgres_database`` fixture).
_UNSET = object()

#: Catalog tables provisioned once per session by the generated optical migration (products,
#: product blocks, resource types, workflows and their association tables). They are part of
#: the shipped catalog and must survive the per-test truncate.
CATALOG_TABLES = frozenset(
    {
        "fixed_inputs",
        "product_block_relations",
        "product_block_resource_types",
        "product_blocks",
        "product_product_blocks",
        "products",
        "products_workflows",
        "resource_types",
        "workflows",
    }
)

#: Non-catalog tables seeded by the orchestrator-core schema migration that the process engine
#: reads during step execution (``engine_settings``) plus the migration bookkeeping table; they
#: must survive the per-test truncate as well.
INFRASTRUCTURE_TABLES = frozenset({"alembic_version", "engine_settings"})

#: Tables preserved across tests: the shipped catalog plus the schema infrastructure.
KEEP_TABLES = CATALOG_TABLES | INFRASTRUCTURE_TABLES


def _materialized_view_names() -> frozenset[str]:
    """Return the orchestrator-core model tables that are materialized views, not truncatable tables."""
    return frozenset(
        name for name, table in CoreBaseModel.metadata.tables.items() if table.info.get("materialized_view")
    )


def _volatile_tables() -> tuple[str, ...]:
    """Derive the per-test tables as every live base table minus the kept catalog/infrastructure.

    Deriving the truncate set from the live schema means a table added by a new
    orchestrator-core version is truncated automatically instead of silently leaking rows
    between tests. Materialized views are excluded (they are not base tables and cannot be
    truncated). The guard fails loudly if an orchestrator-core model table is neither kept,
    truncated nor a view (e.g. a table missing from the migrated database).
    """
    live_tables = set(sa_inspect(core_db.db.engine).get_table_names())
    volatile = live_tables - KEEP_TABLES
    unclassified = set(CoreBaseModel.metadata.tables) - (KEEP_TABLES | volatile | _materialized_view_names())
    assert not unclassified, f"unclassified orchestrator-core tables: {sorted(unclassified)}"
    return tuple(sorted(volatile))


def _create_schema() -> None:
    """Apply the orchestrator-core migrations (``alembic upgrade head``)."""
    migrations_dir = Path(import_module("orchestrator.core.migrations").__file__).parent
    config = Config(str(migrations_dir / "alembic.ini"))
    command.upgrade(config, "head")


def _discover_shipped_workflows() -> list[tuple[str, str]]:
    """Discover (module path, workflow name) pairs of all shipped workflows.

    The shipped workflows are the module-level functions decorated with
    @create_workflow/@modify_workflow/@terminate_workflow/@validate_workflow;
    they carry a ``target`` attribute of type ``orchestrator.core.targets.Target``.
    """
    workflows: list[tuple[str, str]] = []
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
            workflows.append((module_info.name, attribute.name))
    return workflows


def _register_shipped_workflows() -> None:
    """Register the shipped workflows so ``create_process`` resolves them by name."""
    workflows = _discover_shipped_workflows()
    assert workflows, "no shipped workflows discovered in orchestrator.optical.workflows"
    for module, name in workflows:
        LazyWorkflowInstance(module, name)


def _register_customer_choice() -> None:
    """Register a test customer selector (the user-code-space hook of the workflows)."""
    register_customer_choice(
        lambda: cast(type[Choice], Choice.__call__("TestCustomerChoice", {"cust-1": "cust-1", "cust-2": "cust-2"}))
    )


def _provision_catalog(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Generate the shipped catalog migration from the models and apply it to the database.

    Replaces hand-seeding: the generation pipeline derives the product, product block,
    resource type and workflow rows from the shipped models, renders an Alembic revision
    into a scratch directory, applies it on top of the orchestrator-core migrations (the
    same path a consumer follows) and then verifies the applied catalog is drift-free
    against the models. This is the end-to-end validation of the shipped-migration
    machinery.
    """
    plan = migrations.generate_plan()
    assert not plan.is_empty, "the shipped models must produce a non-empty catalog migration"
    version_dir = tmp_path_factory.mktemp("optical-migrations")
    migrations.write_migration(
        plan, version_dir, down_revision=migrations.pinned_core_revision(), message="optical baseline"
    )
    migrations.apply_migrations(version_dir)
    migrations.verify_no_drift()


@pytest.fixture(scope="session")
def postgres_database(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Any]:
    """Provision the test database and configure the orchestrator-core runtime for the session.

    Starts a throwaway PostgreSQL container (or reuses ``OPTICAL_TEST_PG_URL`` when set),
    applies the migrations, provisions the shipped catalog from the generated migration and
    registers the shipped workflows. Fails loudly when Docker is unavailable, so the
    execution-level safety net cannot silently vanish from the suite.
    """
    container = None
    db_url = os.environ.get("OPTICAL_TEST_PG_URL")
    if db_url is None:
        container = PostgresContainer(POSTGRES_IMAGE, driver="psycopg")
        try:
            container.start()
        except Exception as exc:
            raise RuntimeError(CONTAINER_START_ERROR_MSG) from exc
        db_url = container.get_connection_url()

    settings = core_settings.AppSettings(DATABASE_URI=db_url)
    previous_settings: Any = _UNSET
    try:
        previous_settings = core_settings.app_settings
    except Exception:  # noqa: BLE001 - an unconfigured lazy settings proxy may raise on read
        previous_settings = _UNSET
    core_settings.app_settings = settings
    core_db.init_database(settings)
    _create_schema()
    _register_shipped_workflows()
    _register_customer_choice()
    _provision_catalog(tmp_path_factory)

    try:
        yield core_db.db
    finally:
        if previous_settings is not _UNSET:
            core_settings.app_settings = previous_settings
        if container is not None:
            container.stop()


@pytest.fixture
def run_process(postgres_database: Any) -> Callable[[str, list[dict[str, Any]]], str]:
    """Return a helper that runs a shipped workflow through the real orchestrator-core process engine.

    The helper returns the id of the created process; the process itself has completed
    (or failed) synchronously, because the threadpool executor waits for the result when
    ``TESTING`` is enabled. The caller asserts on the process status and the database rows.
    """

    def _run_process(workflow_name: str, user_inputs: list[dict[str, Any]]) -> str:
        process_id = start_process(workflow_name, user_inputs=user_inputs)
        # The worker thread committed its own session; expire the main-thread session so
        # subsequent queries observe the committed rows.
        postgres_database.session.expire_all()
        return str(process_id)

    return _run_process


def _product_id_of(product_name: str) -> str:
    """Return the database product id of the given shipped product name."""
    with core_db.db.database_scope():
        product = core_db.db.session.scalar(select(ProductTable).where(ProductTable.name == product_name))
        assert product is not None
        return str(product.product_id)


def _assert_process_completed(process_id: str) -> None:
    """Assert the process completed, failing with its failure reason otherwise."""
    with core_db.db.database_scope():
        process = core_db.db.session.get(ProcessTable, UUID(process_id))
        assert process is not None
        assert ProcessStatus(process.last_status) == ProcessStatus.COMPLETED, f"process failed: {process.failed_reason}"


def _assert_process_failed(process_id: str) -> None:
    """Assert the process failed."""
    with core_db.db.database_scope():
        process = core_db.db.session.get(ProcessTable, UUID(process_id))
        assert process is not None
        assert ProcessStatus(process.last_status) == ProcessStatus.FAILED, "process did not fail"


def _subscription_id_of_process(process_id: str) -> str:
    """Return the id of the subscription related to the given process."""
    with core_db.db.database_scope():
        relation = core_db.db.session.scalar(
            select(ProcessSubscriptionTable).where(ProcessSubscriptionTable.process_id == UUID(process_id))
        )
        assert relation is not None
        return str(relation.subscription_id)


def node_instance_id_of_subscription(subscription_id: str) -> str:
    """Return the node block instance id of a node subscription (test helper only)."""
    with core_db.db.database_scope():
        return optical_db.node_instance_id_of_subscription(subscription_id)


def _set_subscription_status(subscription_id: str, status: SubscriptionLifecycle) -> None:
    """Set the lifecycle status of a subscription row in the database."""
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        subscription.status = status.value
        core_db.db.session.commit()
    # The default-scope session may hold the row in its identity map; expire it so
    # subsequent domain-model reloads observe the new status.
    core_db.db.session.expire_all()


@pytest.fixture
def product_id_for() -> Callable[[str], str]:
    """Return a helper mapping a shipped product name to its database product id."""
    return _product_id_of


@pytest.fixture
def assert_process_completed() -> Callable[[str], None]:
    """Return a helper asserting a process completed, with its failure reason otherwise."""
    return _assert_process_completed


@pytest.fixture
def assert_process_failed() -> Callable[[str], None]:
    """Return a helper asserting a process failed."""
    return _assert_process_failed


@pytest.fixture
def subscription_id_of_process() -> Callable[[str], str]:
    """Return a helper resolving the subscription id of a process."""
    return _subscription_id_of_process


@pytest.fixture
def set_subscription_status() -> Callable[[str, SubscriptionLifecycle], None]:
    """Return a helper setting the lifecycle status of a subscription row."""
    return _set_subscription_status


@pytest.fixture(autouse=True)
def clean_database(request: pytest.FixtureRequest) -> None:
    """Truncate all per-test data before every db-marked test, keeping the seeded catalog."""
    if request.node.get_closest_marker("db") is None:
        return
    request.getfixturevalue("postgres_database")
    # Uncoped reads leave the default-scope session's pooled connection checked out;
    # roll back to release it before the TRUNCATE below.
    core_db.db.session.rollback()
    volatile_tables = _volatile_tables()
    quote = core_db.db.engine.dialect.identifier_preparer.quote
    quoted_tables = ", ".join(quote(name) for name in volatile_tables)
    with core_db.db.database_scope():
        core_db.db.session.execute(text(f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"))
        core_db.db.session.commit()
