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

On top of the catalog, the harness hosts the execution scaffolding shared by the
per-family execution test modules: the process-assertion and subscription-status
helpers, the device stubs (``install_device_stubs`` and the ``stub_*_device`` fixtures)
that monkeypatch the HAL device calls, and the topology seeders (``active_location``,
``active_packet_node``, ``seed_optical_node``) that build the ACTIVE subscriptions the
device-facing workflows need.

All database configuration lives in this harness only: the module under test keeps its
no-import-time-side-effects rule and its settings are never touched. Set
``OPTICAL_TEST_PG_URL`` to an existing PostgreSQL URL to reuse an external instance
instead of spinning up a container.

The session-scoped ``postgres_database`` fixture rewrites the global
``core_settings.app_settings`` process-wide; after the session ends it keeps pointing
at the (stopped) container.
"""

import hashlib
import inspect
import os
import pkgutil
from collections.abc import Callable, Iterator, Sequence
from importlib import import_module
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from pydantic_forms.validators import Choice
from sqlalchemy import select, text
from testcontainers.community.postgres import PostgresContainer

import orchestrator.core.db as core_db
import orchestrator.core.settings as core_settings
import orchestrator.optical.migrations.generate as migrations
import orchestrator.optical.products  # register the shipped product types in the registry
import orchestrator.optical.workflows
from orchestrator.core.db import ProcessSubscriptionTable, ProcessTable, ProductTable, SubscriptionTable
from orchestrator.core.services.processes import start_process
from orchestrator.core.targets import Target
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import ProcessStatus
from orchestrator.core.workflows import LazyWorkflowInstance
from orchestrator.optical.db import location_block_from_subscription
from orchestrator.optical.products.product_types.optical_packet_node import (
    OpticalModulePacketNodeSubscriptionInactive,
)
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

#: Port names offered by the faked client ports.
FAKE_CLIENT_PORTS = ("port-1/2/1",)
#: Port names offered by the faked line ports.
FAKE_LINE_PORTS = ("port-1/3.1/1.1",)  # G30 OLS-card port: contains a dot, so the spectrum path engine keeps it
#: All port names offered by the faked devices.
FAKE_ALL_PORTS = (*FAKE_CLIENT_PORTS, *FAKE_LINE_PORTS)
#: Transceiver modes offered by the faked devices.
FAKE_TRANSCEIVER_MODES = ("DP16QAM",)
#: Software version reported by the faked devices.
FAKE_SOFTWARE_VERSION = "1.0.0"

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
    with core_db.db.database_scope():
        core_db.db.session.execute(text(f"TRUNCATE TABLE {', '.join(VOLATILE_TABLES)} RESTART IDENTITY CASCADE"))
        core_db.db.session.commit()


def _fake_get_device_line_ports_names(block: Any) -> list[str]:
    """Return the faked line port names of a device."""
    return list(FAKE_LINE_PORTS)


def _fake_get_device_client_ports_names(block: Any) -> list[str]:
    """Return the faked client port names of a device."""
    return list(FAKE_CLIENT_PORTS)


def _fake_get_device_ports_names(block: Any) -> list[str]:
    """Return the faked port names of a device."""
    return list(FAKE_ALL_PORTS)


def _fake_retrieve_transceiver_modes(block: Any, port_name: str) -> list[str]:
    """Return the faked transceiver modes of a device port."""
    return list(FAKE_TRANSCEIVER_MODES)


def _fake_retrieve_ports_spectral_occupations(block: Any) -> dict[str, Any]:
    """Return no spectral occupations for the faked device ports."""
    return {}


def _fake_configure_termination_when_attaching_new_fiber(port: Any, remote: Any) -> dict[str, Any]:
    """Configure the faked fiber terminating port, returning the configuration state."""
    return {}


def _fake_factory_reset_port_configuration(port: Any, remote: Any) -> dict[str, Any]:
    """Factory reset the faked fiber terminating port, returning the reset state."""
    return {}


def _fake_check_fiber_terminating_port(port: Any, remote: Any) -> None:
    """Accept the faked fiber terminating port as consistent."""


def _fake_set_port_description(port: Any, description: str) -> None:
    """Set the description of the faked port."""


def _fake_deploy_optical_circuit(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Deploy the faked optical circuit, returning the deployment state."""
    return {}


def _fake_modify_optical_circuit(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Modify the faked optical circuit, returning the modification state."""
    return {}


def _fake_delete_optical_circuit(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Delete the faked optical circuit, returning the deletion state."""
    return {}


def _fake_validate_optical_circuit(*args: Any, **kwargs: Any) -> None:
    """Accept the faked optical circuit as consistent."""


def _fake_get_signal_bandwidth(block: Any, port_name: str) -> int:
    """Return the faked signal bandwidth of a device port."""
    return 37500


def _fake_configure_line_transceivers(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Configure the faked line transceivers, returning the configuration state."""
    return {}


def _fake_configure_transceiver_client(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Configure the faked transceiver client, returning the configuration state."""
    return {}


def _fake_configure_transponder_crossconnect(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Configure the faked transponder crossconnect, returning the configuration state."""
    return {}


def _fake_delete_transponder_crossconnect(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Delete the faked transponder crossconnect, returning the deletion state."""
    return {}


def _fake_factory_reset_transponder_client(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Factory reset the faked transponder client, returning the reset state."""
    return {}


def _fake_factory_reset_transponder_lines(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Factory reset the faked transponder lines, returning the reset state."""
    return {}


def _fake_validate_trx_line(*args: Any, **kwargs: Any) -> None:
    """Accept the faked transponder line as consistent."""


def _fake_validate_trx_client(*args: Any, **kwargs: Any) -> None:
    """Accept the faked transponder client as consistent."""


def _fake_validate_trx_crossconnect(*args: Any, **kwargs: Any) -> None:
    """Accept the faked transponder crossconnect as consistent."""


def _fake_diff_btw_current_rx_power_and_target(*args: Any, **kwargs: Any) -> float:
    """Report the faked received power already aligned to its target."""
    return 0.0


def _fake_allign_tx_power_to_target(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Align the faked transmitted power to its target, returning the alignment state."""
    return {}


def _fake_discover_flexils_node(*args: Any, **kwargs: Any) -> tuple[str, str]:
    """Return the faked FlexILS node role and software version."""
    return ("ROADM", FAKE_SOFTWARE_VERSION)


def _fake_retrieve_g30_software_version(*args: Any, **kwargs: Any) -> str:
    """Return the faked Groove G30 software version."""
    return FAKE_SOFTWARE_VERSION


def _fake_retrieve_g42_software_version(*args: Any, **kwargs: Any) -> str:
    """Return the faked GX G42 software version."""
    return FAKE_SOFTWARE_VERSION


def _fake_retrieve_software_version(*args: Any, **kwargs: Any) -> str:
    """Return the faked node software version (vendor-dispatching HAL entry point)."""
    return FAKE_SOFTWARE_VERSION


def _fake_sleep(seconds: float) -> None:
    """Skip the faked power stabilization wait."""


def install_device_stubs(
    monkeypatch: pytest.MonkeyPatch,
    *,
    families: Sequence[str],
    client_ports: Sequence[str] = FAKE_CLIENT_PORTS,
    line_ports: Sequence[str] = FAKE_LINE_PORTS,
    all_ports: Sequence[str] = FAKE_ALL_PORTS,
    modes: Sequence[str] = FAKE_TRANSCEIVER_MODES,
) -> None:
    """Monkeypatch the HAL device functions used by the given workflow families.

    HAL functions are imported by name into each workflow module, so the patch targets
    the importing module's attribute (the module whose globals perform the lookup),
    which covers every import site of the same function.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        families: Which family tables to apply: any of ``"node"``, ``"pipe"``, ``"spectrum"``, ``"ods"``.
        client_ports/line_ports/all_ports/modes: Port and mode names offered by the faked devices.
    """

    # Port-list fakes bound to the per-test overrides.
    def _get_device_line_ports_names(block: Any) -> list[str]:
        return list(line_ports)

    def _get_device_client_ports_names(block: Any) -> list[str]:
        return list(client_ports)

    def _get_device_ports_names(block: Any) -> list[str]:
        return list(all_ports)

    def _retrieve_transceiver_modes(block: Any, port_name: str) -> list[str]:
        return list(modes)

    stubs: dict[str, dict[str, dict[str, Callable[..., Any]]]] = {
        "node": {
            "orchestrator.optical.workflows.optical_node.nokia_flexils.create": {
                "discover_flexils_node": _fake_discover_flexils_node,
            },
            "orchestrator.optical.workflows.optical_node.nokia_groove_g30.create": {
                "retrieve_g30_software_version": _fake_retrieve_g30_software_version,
            },
            "orchestrator.optical.workflows.optical_node.nokia_gx_g42.create": {
                "retrieve_g42_software_version": _fake_retrieve_g42_software_version,
            },
            # The node validate steps call the HAL dispatcher through module attribute
            # access (optical_node_hal.retrieve_software_version), so the patch target is
            # the HAL module itself.
            "orchestrator.optical.hal.optical_node": {
                "retrieve_software_version": _fake_retrieve_software_version,
            },
        },
        "pipe": {
            "orchestrator.optical.workflows.optical_pipe.fiber_span.create": {
                "get_device_line_ports_names": _get_device_line_ports_names,
                "configure_termination_when_attaching_new_fiber": _fake_configure_termination_when_attaching_new_fiber,
                "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
            },
            "orchestrator.optical.workflows.optical_pipe.fiber_span.terminate": {
                "factory_reset_port_configuration": _fake_factory_reset_port_configuration,
            },
            "orchestrator.optical.workflows.optical_pipe.fiber_span.validate": {
                "check_fiber_terminating_port": _fake_check_fiber_terminating_port,
                "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
            },
            "orchestrator.optical.workflows.optical_pipe.fiber_patch.create": {
                "get_device_client_ports_names": _get_device_client_ports_names,
                "get_device_ports_names": _get_device_ports_names,
                "configure_termination_when_attaching_new_fiber": _fake_configure_termination_when_attaching_new_fiber,
            },
            "orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate": {
                "factory_reset_port_configuration": _fake_factory_reset_port_configuration,
            },
            "orchestrator.optical.workflows.optical_pipe.fiber_patch.validate": {
                "check_fiber_terminating_port": _fake_check_fiber_terminating_port,
            },
            "orchestrator.optical.workflows.optical_pipe.leased_spectrum.create": {
                "get_device_line_ports_names": _get_device_line_ports_names,
                "get_device_client_ports_names": _get_device_client_ports_names,
                "configure_termination_when_attaching_new_fiber": _fake_configure_termination_when_attaching_new_fiber,
                "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
            },
            "orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate": {
                "factory_reset_port_configuration": _fake_factory_reset_port_configuration,
            },
            "orchestrator.optical.workflows.optical_pipe.leased_spectrum.validate": {
                "check_fiber_terminating_port": _fake_check_fiber_terminating_port,
                "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
            },
        },
        "spectrum": {
            "orchestrator.optical.workflows.optical_spectrum_service.shared": {
                "get_device_client_ports_names": _get_device_client_ports_names,
                "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
            },
            "orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum": {
                "set_port_description": _fake_set_port_description,
                "deploy_optical_circuit": _fake_deploy_optical_circuit,
            },
            "orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum": {
                "modify_optical_circuit": _fake_modify_optical_circuit,
            },
            "orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum": {
                "delete_optical_circuit": _fake_delete_optical_circuit,
            },
            "orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum": {
                "validate_optical_circuit": _fake_validate_optical_circuit,
            },
        },
        "ods": {
            "orchestrator.optical.workflows.optical_spectrum_service.shared": {
                "get_device_client_ports_names": _get_device_client_ports_names,
                "retrieve_transceiver_modes": _retrieve_transceiver_modes,
                "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
            },
            "orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service": {
                "configure_line_transceivers": _fake_configure_line_transceivers,
                "configure_transceiver_client": _fake_configure_transceiver_client,
                "configure_transponder_crossconnect": _fake_configure_transponder_crossconnect,
                "get_signal_bandwidth": _fake_get_signal_bandwidth,
                "diff_btw_current_rx_power_and_target": _fake_diff_btw_current_rx_power_and_target,
                "allign_tx_power_to_target": _fake_allign_tx_power_to_target,
                "deploy_optical_circuit": _fake_deploy_optical_circuit,
                "sleep": _fake_sleep,
            },
            "orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service": {
                "get_signal_bandwidth": _fake_get_signal_bandwidth,
                "modify_optical_circuit": _fake_modify_optical_circuit,
                "sleep": _fake_sleep,
            },
            "orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service": {
                "delete_transponder_crossconnect": _fake_delete_transponder_crossconnect,
                "factory_reset_transponder_client": _fake_factory_reset_transponder_client,
                "factory_reset_transponder_lines": _fake_factory_reset_transponder_lines,
                "delete_optical_circuit": _fake_delete_optical_circuit,
            },
            "orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service": {
                "get_signal_bandwidth": _fake_get_signal_bandwidth,
                "validate_trx_line": _fake_validate_trx_line,
                "validate_trx_client": _fake_validate_trx_client,
                "validate_trx_crossconnect": _fake_validate_trx_crossconnect,
                "validate_optical_circuit": _fake_validate_optical_circuit,
            },
        },
    }
    for family in families:
        if family not in stubs:
            msg = f"Unknown device stub family {family!r}; expected one of {sorted(stubs)}"
            raise ValueError(msg)
        for module_name, attributes in stubs[family].items():
            module = import_module(module_name)
            for attribute, fake in attributes.items():
                if not hasattr(module, attribute):
                    msg = f"Device stub target {module_name}.{attribute} does not exist"
                    raise AttributeError(msg)
                monkeypatch.setattr(module, attribute, fake)


@pytest.fixture
def stub_node_device(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the node discovery HAL calls of all three vendors."""
    install_device_stubs(monkeypatch, families=("node",))


@pytest.fixture
def stub_pipe_device(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the device calls of the optical_pipe family workflows."""
    install_device_stubs(monkeypatch, families=("pipe",))


@pytest.fixture
def stub_spectrum_device(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the device calls of the optical_spectrum_service family workflows."""
    install_device_stubs(monkeypatch, families=("spectrum",))


@pytest.fixture
def stub_ods_device(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the device calls of the optical_digital_service family workflows."""
    install_device_stubs(monkeypatch, families=("ods",))


def _flexils_gmpls_id(fqdn: str) -> str:
    """Derive a deterministic GMPLS ID from a node FQDN (the shipped FlexILS create form requires one)."""
    digest = hashlib.sha256(fqdn.encode("utf-8")).digest()
    return f"10.255.{digest[0]}.{digest[1]}"


@pytest.fixture
def active_location(run_process: Callable[[str, list[dict[str, Any]]], str]) -> str:
    """Create an ACTIVE Optical Module Location via the shipped create workflow."""
    process_id = run_process(
        "create_optical_module_location",
        [
            {"product": _product_id_of("Optical Module Location")},
            {"customer_id": CUSTOMER_ID, "location_code": "loc-01", "location_name": "Test Location"},
            {"longitude": "12.4964", "latitude": "41.9028"},
            {},
        ],
    )
    _assert_process_completed(process_id)
    return _subscription_id_of_process(process_id)


@pytest.fixture
def active_packet_node(
    run_process: Callable[[str, list[dict[str, Any]]], str],
    active_location: str,
) -> str:
    """Create an ACTIVE Optical Module Packet Node (there is no shipped workflow for it)."""
    with core_db.db.database_scope():
        subscription = OpticalModulePacketNodeSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id_of("Optical Module Packet Node")),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        subscription.optical_packet_node.management.optical_module_node_fqdn = "packet-node-01.test.local"
        subscription.optical_packet_node.location = location_block_from_subscription(active_location)
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    core_db.db.session.expire_all()
    _set_subscription_status(subscription_id, SubscriptionLifecycle.ACTIVE)
    return subscription_id


@pytest.fixture
def seed_optical_node(
    run_process: Callable[[str, list[dict[str, Any]]], str],
    active_location: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., str]:
    """Return a helper creating ACTIVE optical nodes of the shipped products (device calls stubbed)."""

    def _seed(
        product_name: str,
        fqdn: str,
        dcn_interface_ip: str,
        *,
        optical_node_role: str | None = None,
        dcn_loopback_ip: str | None = None,
    ) -> str:
        """Create an ACTIVE optical node of the given product via the shipped create workflow (device calls stubbed).

        The node role is a block constraint: FlexILS nodes are line systems (the role is discovered from
        the device, always ``ROADM`` via the stub, and is not a form field); Groove G30 nodes default to
        ``Transponder`` (``Transponder and xOADM`` is also allowed); GX G42 nodes are ``Transponder`` only.
        """
        install_device_stubs(monkeypatch, families=("node",))
        identity: dict[str, Any] = {
            "customer_id": CUSTOMER_ID,
            "location_id": active_location,
            "optical_module_node_fqdn": fqdn,
        }
        management: dict[str, Any] = {
            "optical_module_node_dcn_interface_ip": dcn_interface_ip,
            "optical_module_node_dcn_loopback_ip": dcn_loopback_ip,
        }
        match product_name:
            case "Nokia FlexILS Optical Node":
                workflow_name = "create_optical_node_nokia_flexils"
                identity["optical_flexils_target_id"] = fqdn
                management["optical_flexils_gmpls_id"] = _flexils_gmpls_id(fqdn)
            case "Nokia Groove G30 Optical Node":
                workflow_name = "create_optical_node_nokia_groove_g30"
                identity["optical_node_role"] = optical_node_role or "Transponder"
            case "Nokia GX G42 Optical Node":
                workflow_name = "create_optical_node_nokia_gx_g42"
                identity["optical_node_role"] = optical_node_role or "Transponder"
            case _:
                msg = (
                    f"Unknown optical node product {product_name!r}; supported products are "
                    "'Nokia FlexILS Optical Node', 'Nokia Groove G30 Optical Node' and 'Nokia GX G42 Optical Node'"
                )
                raise ValueError(msg)
        user_inputs: list[dict[str, Any]] = [{"product": _product_id_of(product_name)}, identity, management, {}]
        process_id = run_process(workflow_name, user_inputs)
        _assert_process_completed(process_id)
        return _subscription_id_of_process(process_id)

    return _seed


@pytest.fixture
def active_coherent_pluggable_host(
    run_process: Callable[[str, list[dict[str, Any]]], str],
    active_location: str,
) -> str:
    """Create an ACTIVE Optical Module Packet Node fully provisioned as a coherent pluggable host.

    Unlike ``active_packet_node`` (which only sets the management block FQDN), this seeder
    also fills the fields the ACTIVE management block requires. The coherent pluggable
    workflows resolve the host node through ``packet_node_block_from_subscription`` (the
    most-derived lifecycle class), which cannot load a partially provisioned node.
    """
    with core_db.db.database_scope():
        subscription = OpticalModulePacketNodeSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id_of("Optical Module Packet Node")),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        management = subscription.optical_packet_node.management
        management.optical_module_node_fqdn = "pluggable-host-01.test.local"
        management.optical_module_node_vendor = "Nokia"
        management.optical_module_node_platform = "NCS"
        management.optical_module_node_software_version = FAKE_SOFTWARE_VERSION
        subscription.optical_packet_node.location = location_block_from_subscription(active_location)
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    core_db.db.session.expire_all()
    _set_subscription_status(subscription_id, SubscriptionLifecycle.ACTIVE)
    return subscription_id
