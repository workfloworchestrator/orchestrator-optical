"""Execution-level tests for the shipped Optical Module Location workflows.

These tests are database-backed: they run the shipped workflows end to end through the
real orchestrator-core process engine (``start_process`` with the threadpool executor),
so the paths that break first as models drift are actually executed: ``from_product_id``
on the abstract model, lifecycle-variant resolution on reload (INITIAL, PROVISIONING,
ACTIVE), the JSON state round-trip between steps, the block persistence, the
description refresh, the process-subscription relation and the modify/terminate/validate
transitions.
"""

from typing import Any, cast
from uuid import UUID

import pytest
from pydantic_forms.exceptions import FormValidationError
from sqlalchemy import select, text

import orchestrator.core.db as core_db
from orchestrator.core.db import (
    ProcessStepTable,
    ProcessSubscriptionTable,
    ProcessTable,
    ProductTable,
    SubscriptionTable,
)
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import ProcessStatus
from orchestrator.optical.db import location_block_from_subscription
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_location import (
    OpticalModuleLocationSubscription,
    OpticalModuleLocationSubscriptionInactive,
    OpticalModuleLocationSubscriptionProvisioning,
)
from orchestrator.optical.workflows.optical_location.shared import (
    OPTICAL_LOCATION_BLOCK_STATE_KEY,
    check_location_code_uniqueness,
    optical_location_block_from_state,
)
from orchestrator.optical.workflows.optical_location.validate import validate_optical_module_location_state
from test.conftest import VOLATILE_TABLES

pytestmark = pytest.mark.db

PRODUCT_NAME = "Optical Module Location"
CUSTOMER_ID = "cust-1"


@pytest.fixture(autouse=True)
def _clean_database(postgres_database: Any) -> None:
    """Truncate all per-test data before every DB-backed test, keeping the seeded catalog."""
    # Uncoped reads (e.g. the direct check_location_code_uniqueness call in a test) leave the
    # default-scope session's pooled connection checked out; roll back to release it before
    # the TRUNCATE below.
    core_db.db.session.rollback()
    with core_db.db.database_scope():
        core_db.db.session.execute(text(f"TRUNCATE TABLE {', '.join(VOLATILE_TABLES)} RESTART IDENTITY CASCADE"))
        core_db.db.session.commit()


def _product_id() -> str:
    with core_db.db.database_scope():
        product = core_db.db.session.scalar(select(ProductTable).where(ProductTable.name == PRODUCT_NAME))
        assert product is not None
        return str(product.product_id)


def _create_user_inputs() -> list[dict]:
    return [
        {"product": _product_id()},
        {"customer_id": CUSTOMER_ID, "location_code": "rom-01", "location_name": "Rome"},
        {"longitude": "12.4964", "latitude": "41.9028"},
        {},
    ]


def _run_create(run_process) -> tuple[str, str]:
    """Run the shipped create workflow and return the (process id, subscription id) pair."""
    process_id = run_process("create_optical_module_location", _create_user_inputs())
    _assert_process_completed(process_id)
    return process_id, _subscription_id_of_process(process_id)


def _assert_process_completed(process_id: str) -> None:
    with core_db.db.database_scope():
        process = core_db.db.session.get(ProcessTable, UUID(process_id))
        assert process is not None
        assert ProcessStatus(process.last_status) == ProcessStatus.COMPLETED, f"process failed: {process.failed_reason}"


def _subscription_id_of_process(process_id: str) -> str:
    with core_db.db.database_scope():
        relation = core_db.db.session.scalar(
            select(ProcessSubscriptionTable).where(ProcessSubscriptionTable.process_id == UUID(process_id))
        )
        assert relation is not None
        return str(relation.subscription_id)


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        return subscription


def _set_subscription_status(subscription_id: str, status: SubscriptionLifecycle) -> None:
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert subscription is not None
        subscription.status = status.value
        core_db.db.session.commit()
    # The default-scope session may hold the row in its identity map; expire it so
    # subsequent domain-model reloads observe the new status.
    core_db.db.session.expire_all()


def _assert_block_state_round_tripped(process_id: str) -> None:
    """Assert a step state holds the block as a dict with the values entered in the create form."""
    expected = {
        "location_code": "rom-01",
        "location_name": "Rome",
        "longitude": "12.4964",
        "latitude": "41.9028",
    }
    with core_db.db.database_scope():
        block_states = [
            step.state[OPTICAL_LOCATION_BLOCK_STATE_KEY]
            for step in core_db.db.session.scalars(
                select(ProcessStepTable).where(ProcessStepTable.process_id == UUID(process_id))
            )
            if isinstance(step.state, dict) and isinstance(step.state.get(OPTICAL_LOCATION_BLOCK_STATE_KEY), dict)
        ]
    assert any(all(block_state.get(key) == value for key, value in expected.items()) for block_state in block_states), (
        "no step state held the round-tripped block with the create form values"
    )


def test_create_optical_module_location_end_to_end(run_process) -> None:
    """The shipped create workflow executes end to end: model construction, block save, description, relation."""
    process_id, subscription_id = _run_create(run_process)

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.description == "Rome (rom-01)"
    assert subscription.customer_id == CUSTOMER_ID

    block = location_block_from_subscription(subscription_id)
    assert isinstance(block, OpticalModuleLocationBlock)
    assert block.location_code == "rom-01"
    assert block.location_name == "Rome"
    assert block.longitude == "12.4964"
    assert block.latitude == "41.9028"

    _assert_block_state_round_tripped(process_id)


def test_full_lifecycle_create_modify_terminate_validate(run_process) -> None:
    """The full create -> modify -> terminate -> validate cycle of the shipped workflows."""
    _, subscription_id = _run_create(run_process)

    modify_process_id = run_process(
        "modify_optical_module_location",
        [
            {"subscription_id": subscription_id},
            {
                "customer_id": CUSTOMER_ID,
                "longitude": "4.9041",
                "latitude": "52.3676",
                "location_code": "ams-01",
                "location_name": "Amsterdam",
                "clear_location_name": False,
            },
            {},
        ],
    )
    _assert_process_completed(modify_process_id)
    # The shipped modify workflow updates the block and the lifecycle but does not refresh
    # the subscription description (only the create workflow does): the description is unchanged.
    assert _subscription_table(subscription_id).description == "Rome (rom-01)"
    block = location_block_from_subscription(subscription_id)
    assert isinstance(block, OpticalModuleLocationBlock)
    assert block.location_code == "ams-01"
    assert block.location_name == "Amsterdam"
    assert block.longitude == "4.9041"
    assert block.latitude == "52.3676"
    assert _subscription_table(subscription_id).insync is True

    validate_process_id = run_process("validate_optical_module_location", [{"subscription_id": subscription_id}])
    _assert_process_completed(validate_process_id)

    terminate_process_id = run_process(
        "terminate_optical_module_location",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    _assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert _subscription_id_of_process(terminate_process_id) == subscription_id


def test_subscription_and_block_lifecycle_variants_resolve_on_reload(run_process) -> None:
    """INITIAL, PROVISIONING and ACTIVE rows reload as their matching lifecycle variant."""
    _, subscription_id = _run_create(run_process)

    active_subscription = OpticalModuleLocationSubscription.from_subscription(subscription_id)
    assert isinstance(active_subscription, OpticalModuleLocationSubscription)
    assert isinstance(active_subscription.optical_location, OpticalModuleLocationBlock)

    _set_subscription_status(subscription_id, SubscriptionLifecycle.PROVISIONING)
    provisioning_subscription = OpticalModuleLocationSubscriptionProvisioning.from_subscription(subscription_id)
    assert isinstance(provisioning_subscription, OpticalModuleLocationSubscriptionProvisioning)
    assert isinstance(provisioning_subscription.optical_location, OpticalModuleLocationBlockProvisioning)

    _set_subscription_status(subscription_id, SubscriptionLifecycle.INITIAL)
    inactive_subscription = OpticalModuleLocationSubscriptionInactive.from_subscription(subscription_id)
    assert isinstance(inactive_subscription, OpticalModuleLocationSubscriptionInactive)
    assert isinstance(inactive_subscription.optical_location, OpticalModuleLocationBlockInactive)


def test_block_rehydration_resolves_the_lifecycle_variant(run_process) -> None:
    """``optical_location_block_from_state`` rehydrates the round-tripped block as its matching variant."""
    _, subscription_id = _run_create(run_process)

    block_dict = location_block_from_subscription(subscription_id).model_dump()
    assert isinstance(optical_location_block_from_state(block_dict), OpticalModuleLocationBlock)

    _set_subscription_status(subscription_id, SubscriptionLifecycle.PROVISIONING)
    block_dict = location_block_from_subscription(subscription_id).model_dump()
    assert isinstance(optical_location_block_from_state(block_dict), OpticalModuleLocationBlockProvisioning)

    _set_subscription_status(subscription_id, SubscriptionLifecycle.INITIAL)
    assert isinstance(optical_location_block_from_state(block_dict), OpticalModuleLocationBlockInactive)


def test_duplicate_location_code_rejected_by_create_workflow(run_process) -> None:
    """A second create with a location code in use fails the form validation against the database."""
    _, _ = _run_create(run_process)

    with pytest.raises(FormValidationError, match="already in use"):
        run_process("create_optical_module_location", _create_user_inputs())


def test_modify_keeps_own_location_code(run_process) -> None:
    """The modify uniqueness check excludes the subscription being modified."""
    _, subscription_id = _run_create(run_process)

    process_id = run_process(
        "modify_optical_module_location",
        [
            {"subscription_id": subscription_id},
            {
                "customer_id": CUSTOMER_ID,
                "longitude": "12.4964",
                "latitude": "41.9028",
                "location_code": "rom-01",
                "location_name": "Rome",
                "clear_location_name": False,
            },
            {},
        ],
    )
    _assert_process_completed(process_id)


def test_check_location_code_uniqueness_against_database(run_process) -> None:
    """The uniqueness check queries the database and names the conflicting subscription."""
    _, subscription_id = _run_create(run_process)

    with pytest.raises(ValueError, match="already in use") as exc_info:
        check_location_code_uniqueness("rom-01")
    assert subscription_id in str(exc_info.value)
    assert "Rome (rom-01)" in str(exc_info.value)

    check_location_code_uniqueness("rom-01", exclude_subscription_id=subscription_id)


def test_validate_fails_on_unprovisioned_block() -> None:
    """The shipped validate step fails an INITIAL subscription whose block is not fully provisioned.

    The framework only allows the validate workflow on ACTIVE subscriptions, so the shipped
    check is exercised at step level against an INITIAL subscription loaded from the database.
    """
    with core_db.db.database_scope():
        subscription = OpticalModuleLocationSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id()),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    core_db.db.session.expire_all()

    loaded = OpticalModuleLocationSubscriptionInactive.from_subscription(subscription_id)
    with pytest.raises(ValueError, match="not fully provisioned"):
        cast(Any, validate_optical_module_location_state).__wrapped__(
            subscription=loaded, optical_module_location_block=None
        )


def test_validate_on_active_unprovisioned_block_fails_with_pydantic_error(run_process) -> None:
    """Validation of an ACTIVE subscription with an empty block fails the framework's model load.

    The framework loads the ACTIVE domain model before any shipped step runs, so the process
    fails with a pydantic validation error on the required block fields, not the shipped check.
    """
    with core_db.db.database_scope():
        subscription = OpticalModuleLocationSubscriptionInactive.from_product_id(
            product_id=UUID(_product_id()),
            customer_id=CUSTOMER_ID,
            status=SubscriptionLifecycle.INITIAL,
        )
        subscription.save()
        subscription_id = str(subscription.subscription_id)
        core_db.db.session.commit()
    # A provisioned subscription would be in sync; only the block values are missing.
    with core_db.db.database_scope():
        table = core_db.db.session.get(SubscriptionTable, UUID(subscription_id))
        assert table is not None
        table.insync = True
        core_db.db.session.commit()
    core_db.db.session.expire_all()
    _set_subscription_status(subscription_id, SubscriptionLifecycle.ACTIVE)

    process_id = run_process("validate_optical_module_location", [{"subscription_id": subscription_id}])
    with core_db.db.database_scope():
        process = core_db.db.session.get(ProcessTable, UUID(process_id))
        assert process is not None
        assert ProcessStatus(process.last_status) == ProcessStatus.FAILED
        assert process.failed_reason is not None
        # The framework loads the ACTIVE domain model before any shipped step runs (the
        # "Lock subscription" step), so the failure is the pydantic field error of the
        # empty block, not the shipped "not fully provisioned" check.
        assert "validation errors for OpticalModuleLocationSubscription" in process.failed_reason
        assert "optical_location.longitude" in process.failed_reason
        assert "Input should be a valid string" in process.failed_reason
