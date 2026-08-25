"""Database-backed execution-test harness for the shipped workflows.

This module provisions a throwaway PostgreSQL container (``pgvector/pgvector:pg16`` —
the orchestrator-core migration head requires the pgvector extension), applies the
orchestrator-core migrations (``alembic upgrade head``, the same path a consumer uses),
provisions the shipped catalog (product, product block, resource types, workflows) from
the migration generated off the shipped models and registers the shipped workflows, so
the shipped workflows can be executed end to end through the real orchestrator-core
process engine (``start_process`` with the threadpool executor). The generation step
doubles as the drift gate: after applying the generated migration the catalog must be a
faithful projection of the models (``verify_no_drift``).

All database configuration lives in this harness only: the module under test keeps its
no-import-time-side-effects rule and its settings are never touched. Set
``OPTICAL_TEST_PG_URL`` to an existing PostgreSQL URL to reuse an external instance
instead of spinning up a container.
"""

import os
from collections.abc import Callable, Iterator
from importlib import import_module
from pathlib import Path
from typing import Any, cast

import pytest
from alembic import command
from alembic.config import Config
from pydantic_forms.validators import Choice
from testcontainers.community.postgres import PostgresContainer

import orchestrator.core.db as core_db
import orchestrator.core.settings as core_settings
import orchestrator.optical.migrations.generate as migrations
import orchestrator.optical.products  # noqa: F401  # register the shipped product types in the registry
from orchestrator.core.workflows import LazyWorkflowInstance
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

#: The shipped workflows registered for the execution tests, exactly as consumers register them.
SHIPPED_WORKFLOW_REGISTRATIONS = {
    "create_optical_module_location": "orchestrator.optical.workflows.optical_location.create",
    "modify_optical_module_location": "orchestrator.optical.workflows.optical_location.modify",
    "terminate_optical_module_location": "orchestrator.optical.workflows.optical_location.terminate",
    "validate_optical_module_location": "orchestrator.optical.workflows.optical_location.validate",
}

#: Tables holding per-test data. The catalog tables (products, product blocks, resource
#: types, workflows and their association tables) are provisioned once per session by the
#: generated optical migration and kept;
#: ``TRUNCATE ... CASCADE`` removes everything that references the tables below.
VOLATILE_TABLES = (
    "processes",
    "subscriptions",
    "search_queries",
    "agent_runs",
    "graph_snapshots",
    "ai_search_index",
    "ai_search_paths",
)


def _create_schema() -> None:
    """Apply the orchestrator-core migrations (``alembic upgrade head``)."""
    migrations_dir = Path(import_module("orchestrator.core.migrations").__file__).parent
    config = Config(str(migrations_dir / "alembic.ini"))
    command.upgrade(config, "head")


def _register_shipped_workflows() -> None:
    """Register the shipped workflows so ``create_process`` resolves them by name."""
    for name, module in SHIPPED_WORKFLOW_REGISTRATIONS.items():
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
    core_settings.app_settings = settings
    core_db.init_database(settings)
    _create_schema()
    _register_shipped_workflows()
    _register_customer_choice()
    _provision_catalog(tmp_path_factory)

    try:
        yield core_db.db
    finally:
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
        from orchestrator.core.services.processes import start_process

        process_id = start_process(workflow_name, user_inputs=user_inputs)
        # The worker thread committed its own session; expire the main-thread session so
        # subsequent queries observe the committed rows.
        postgres_database.session.expire_all()
        return str(process_id)

    return _run_process
